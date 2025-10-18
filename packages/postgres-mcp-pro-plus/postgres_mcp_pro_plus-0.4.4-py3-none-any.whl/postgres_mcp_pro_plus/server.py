"""Postgres MCP Server."""

import argparse
import asyncio
import logging
import os
import signal
import sys
from enum import Enum
from typing import Any
from typing import List
from typing import Literal
from typing import Union

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from pydantic import validate_call

from .artifacts import ErrorResult
from .artifacts import ExplainPlanArtifact
from .blocking_queries import BlockingQueriesAnalyzer
from .database_health import DatabaseHealthTool
from .database_health import HealthType
from .database_overview import DatabaseOverviewTool
from .explain import ExplainPlanTool
from .index.dta_calc import DatabaseTuningAdvisor
from .index.index_opt_base import MAX_NUM_INDEX_TUNING_QUERIES
from .index.llm_opt import LLMOptimizerTool
from .index.presentation import TextPresentation
from .schema_mapping import SchemaMappingTool
from .sql import DbConnPool
from .sql import SafeSqlDriver
from .sql import SqlDriver
from .sql import check_hypopg_installation_status
from .sql import obfuscate_password
from .top_queries import TopQueriesCalc
from .vacuum_analysis import VacuumAnalysisTool

# Initialize FastMCP with default settings
mcp = FastMCP("postgres-mcp-pro-plus")

# Constants
PG_STAT_STATEMENTS = "pg_stat_statements"
HYPOPG_EXTENSION = "hypopg"

ResponseType = List[types.TextContent | types.ImageContent | types.EmbeddedResource]

logger = logging.getLogger(__name__)


class AccessMode(str, Enum):
    """SQL access modes for the server."""

    UNRESTRICTED = "unrestricted"  # Unrestricted access
    RESTRICTED = "restricted"  # Read-only with safety features


# Global variables
db_connection = DbConnPool()
current_access_mode = AccessMode.UNRESTRICTED
shutdown_in_progress = False


async def get_sql_driver() -> Union[SqlDriver, SafeSqlDriver]:
    """Get the appropriate SQL driver based on the current access mode."""
    base_driver = SqlDriver(conn=db_connection)

    if current_access_mode == AccessMode.RESTRICTED:
        logger.debug("Using SafeSqlDriver with restrictions (RESTRICTED mode)")
        return SafeSqlDriver(sql_driver=base_driver, timeout=30)  # 30 second timeout
    else:
        logger.debug("Using unrestricted SqlDriver (UNRESTRICTED mode)")
        return base_driver


def format_text_response(text: Any) -> ResponseType:
    """Format a text response."""
    return [types.TextContent(type="text", text=str(text))]


def format_schemas_as_text(schemas: list[dict]) -> str:
    """Format schemas list compactly without emojis, preserving details."""
    if not schemas:
        return "No schemas found."

    # Group by schema type
    system = [s for s in schemas if s.get("schema_type") in ("System Schema", "System Information Schema")]
    user = [s for s in schemas if s.get("schema_type") == "User Schema"]

    out: list[str] = []
    if user:
        items = [f"{s['schema_name']}(owner={s.get('schema_owner', 'N/A')})" for s in user]
        out.append("UserSchemas: " + "; ".join(items))
    if system:
        shown = system[:10]
        items = [f"{s['schema_name']}({s.get('schema_type', 'N/A')})" for s in shown]
        line = f"SystemSchemas({len(system)}): " + "; ".join(items)
        if len(system) > 10:
            line += f"; +{len(system) - 10} more"
        out.append(line)

    return "\n".join(out)


def format_objects_as_text(objects: list[dict], object_type: str) -> str:
    """Format object lists compactly without emojis/headers, preserving details."""
    if not objects:
        return f"No {object_type}s found."

    label_map = {"table": "Tables", "view": "Views", "sequence": "Sequences", "extension": "Extensions"}
    label = label_map.get(object_type, object_type.capitalize() + "s")

    def item_str(o: dict) -> str:
        if object_type in ("table", "view"):
            return f"{o['schema']}.{o['name']}({o['type']})"
        if object_type == "sequence":
            return f"{o['schema']}.{o['name']}({o['data_type']})"
        if object_type == "extension":
            return f"{o['name']} v{o['version']} reloc={o['relocatable']}"
        return str(o)

    items = "; ".join(item_str(o) for o in objects)
    return f"{label}({len(objects)}): {items}"


def format_object_details_as_text(details: dict, object_type: str) -> str:
    """Format object details compactly without emojis, preserving content."""
    if not details:
        return f"No details found for {object_type}."

    output = []

    if object_type in ["table", "view"]:
        basic = details.get("basic", {})
        output.append(f"{object_type.capitalize()}: {basic.get('schema', 'N/A')}.{basic.get('name', 'N/A')} type={basic.get('type', 'N/A')}")

        # Columns
        columns = details.get("columns", [])
        if columns:
            parts = []
            for col in columns:
                nullable = "NULL" if col.get("is_nullable") == "YES" else "NOTNULL"
                default = col.get("default")
                piece = f"{col['column']} {col['data_type']} {nullable}"
                if default:
                    piece += f" def={default}"
                parts.append(piece)
            output.append(f"Columns({len(columns)}): " + "; ".join(parts))

        # Constraints
        constraints = details.get("constraints", [])
        if constraints:
            items = []
            for constraint in constraints:
                columns_str = ",".join(constraint.get("columns", []))
                items.append(f"{constraint['name']}({constraint['type']}) on[{columns_str}]")
            output.append(f"Constraints({len(constraints)}): " + "; ".join(items))

        # Indexes
        indexes = details.get("indexes", [])
        if indexes:
            items = [f"{idx['name']} def={idx['definition']}" for idx in indexes]
            output.append(f"Indexes({len(indexes)}): " + "; ".join(items))

    elif object_type == "sequence":
        output.append(
            "Sequence: "
            f"{details.get('schema', 'N/A')}.{details.get('name', 'N/A')} "
            f"type={details.get('data_type', 'N/A')} start={details.get('start_value', 'N/A')} inc={details.get('increment', 'N/A')}"
        )

    elif object_type == "extension":
        output.append(f"Extension: name={details.get('name', 'N/A')} v={details.get('version', 'N/A')} reloc={details.get('relocatable', 'N/A')}")

    return "\n".join(output)


def format_query_results_as_text(results: list[dict]) -> str:
    """Format SQL query results compactly without emojis, preserving content."""
    if not results:
        return "No results"

    # Column order from first row
    columns = list(results[0].keys())

    out: list[str] = []
    out.append(f"Rows={len(results)} Cols={len(columns)}")
    out.append("Columns: " + ", ".join(columns))

    # Show first few rows in compact form
    max_rows = min(10000, len(results))
    for i, row in enumerate(results[:max_rows], 1):
        parts = []
        for col in columns:
            val = row.get(col)
            s = str(val)
            if len(s) > 80:
                s = s[:77] + "..."
            parts.append(f"{col}={s}")
        out.append(f"{i}: " + "; ".join(parts))

    if len(results) > max_rows:
        out.append(f"+{len(results) - max_rows} more")

    return "\n".join(out)


def format_error_response(error: str) -> ResponseType:
    """Format an error response."""
    return format_text_response(f"Error: {error}")


@mcp.tool(description="List all schemas in the database")
async def list_schemas() -> ResponseType:
    """List all schemas in the database."""
    try:
        sql_driver = await get_sql_driver()
        rows = await sql_driver.execute_query(
            """
            SELECT
                schema_name,
                schema_owner,
                CASE
                    WHEN schema_name LIKE 'pg_%' THEN 'System Schema'
                    WHEN schema_name = 'information_schema' THEN 'System Information Schema'
                    ELSE 'User Schema'
                END as schema_type
            FROM information_schema.schemata
            ORDER BY schema_type, schema_name
            """
        )
        schemas = [row.cells for row in rows] if rows else []
        return format_text_response(format_schemas_as_text(schemas))
    except Exception as e:
        logger.error(f"Error listing schemas: {e}")
        return format_error_response(str(e))


@mcp.tool(description="List objects in a schema")
async def list_objects(
    schema_name: str = Field(description="Schema name"),
    object_type: str = Field(description="Object type: 'table', 'view', 'sequence', or 'extension'", default="table"),
) -> ResponseType:
    """List objects of a given type in a schema."""
    try:
        sql_driver = await get_sql_driver()

        if object_type in ("table", "view"):
            table_type = "BASE TABLE" if object_type == "table" else "VIEW"
            rows = await SafeSqlDriver.execute_param_query(
                sql_driver,
                """
                SELECT table_schema, table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = {} AND table_type = {}
                ORDER BY table_name
                """,
                [schema_name, table_type],
            )
            objects = (
                [
                    {
                        "schema": row.cells["table_schema"],
                        "name": row.cells["table_name"],
                        "type": row.cells["table_type"],
                    }
                    for row in rows
                ]
                if rows
                else []
            )

        elif object_type == "sequence":
            rows = await SafeSqlDriver.execute_param_query(
                sql_driver,
                """
                SELECT sequence_schema, sequence_name, data_type
                FROM information_schema.sequences
                WHERE sequence_schema = {}
                ORDER BY sequence_name
                """,
                [schema_name],
            )
            objects = (
                [
                    {
                        "schema": row.cells["sequence_schema"],
                        "name": row.cells["sequence_name"],
                        "data_type": row.cells["data_type"],
                    }
                    for row in rows
                ]
                if rows
                else []
            )

        elif object_type == "extension":
            # Extensions are not schema-specific
            rows = await sql_driver.execute_query(
                """
                SELECT extname, extversion, extrelocatable
                FROM pg_extension
                ORDER BY extname
                """
            )
            objects = (
                [
                    {
                        "name": row.cells["extname"],
                        "version": row.cells["extversion"],
                        "relocatable": row.cells["extrelocatable"],
                    }
                    for row in rows
                ]
                if rows
                else []
            )

        else:
            return format_error_response(f"Unsupported object type: {object_type}")

        return format_text_response(format_objects_as_text(objects, object_type))
    except Exception as e:
        logger.error(f"Error listing objects: {e}")
        return format_error_response(str(e))


@mcp.tool(description="Show detailed information about a database object")
async def get_object_details(
    schema_name: str = Field(description="Schema name"),
    object_name: str = Field(description="Object name"),
    object_type: str = Field(description="Object type: 'table', 'view', 'sequence', or 'extension'", default="table"),
) -> ResponseType:
    """Get detailed information about a database object."""
    try:
        sql_driver = await get_sql_driver()

        if object_type in ("table", "view"):
            # Get columns
            col_rows = await SafeSqlDriver.execute_param_query(
                sql_driver,
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = {} AND table_name = {}
                ORDER BY ordinal_position
                """,
                [schema_name, object_name],
            )
            columns = (
                [
                    {
                        "column": r.cells["column_name"],
                        "data_type": r.cells["data_type"],
                        "is_nullable": r.cells["is_nullable"],
                        "default": r.cells["column_default"],
                    }
                    for r in col_rows
                ]
                if col_rows
                else []
            )

            # Get constraints
            con_rows = await SafeSqlDriver.execute_param_query(
                sql_driver,
                """
                SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
                FROM information_schema.table_constraints AS tc
                LEFT JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_schema = kcu.table_schema
                WHERE tc.table_schema = {} AND tc.table_name = {}
                """,
                [schema_name, object_name],
            )

            constraints = {}
            if con_rows:
                for row in con_rows:
                    cname = row.cells["constraint_name"]
                    ctype = row.cells["constraint_type"]
                    col = row.cells["column_name"]

                    if cname not in constraints:
                        constraints[cname] = {"type": ctype, "columns": []}
                    if col:
                        constraints[cname]["columns"].append(col)

            constraints_list = [{"name": name, **data} for name, data in constraints.items()]

            # Get indexes
            idx_rows = await SafeSqlDriver.execute_param_query(
                sql_driver,
                """
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = {} AND tablename = {}
                """,
                [schema_name, object_name],
            )

            indexes = [{"name": r.cells["indexname"], "definition": r.cells["indexdef"]} for r in idx_rows] if idx_rows else []

            result = {
                "basic": {"schema": schema_name, "name": object_name, "type": object_type},
                "columns": columns,
                "constraints": constraints_list,
                "indexes": indexes,
            }

        elif object_type == "sequence":
            rows = await SafeSqlDriver.execute_param_query(
                sql_driver,
                """
                SELECT sequence_schema, sequence_name, data_type, start_value, increment
                FROM information_schema.sequences
                WHERE sequence_schema = {} AND sequence_name = {}
                """,
                [schema_name, object_name],
            )

            if rows and rows[0]:
                row = rows[0]
                result = {
                    "schema": row.cells["sequence_schema"],
                    "name": row.cells["sequence_name"],
                    "data_type": row.cells["data_type"],
                    "start_value": row.cells["start_value"],
                    "increment": row.cells["increment"],
                }
            else:
                result = {}

        elif object_type == "extension":
            rows = await SafeSqlDriver.execute_param_query(
                sql_driver,
                """
                SELECT extname, extversion, extrelocatable
                FROM pg_extension
                WHERE extname = {}
                """,
                [object_name],
            )

            if rows and rows[0]:
                row = rows[0]
                result = {
                    "name": row.cells["extname"],
                    "version": row.cells["extversion"],
                    "relocatable": row.cells["extrelocatable"],
                }
            else:
                result = {}

        else:
            return format_error_response(f"Unsupported object type: {object_type}")

        return format_text_response(format_object_details_as_text(result, object_type))
    except Exception as e:
        logger.error(f"Error getting object details: {e}")
        return format_error_response(str(e))


@mcp.tool(description="Explains the execution plan for a SQL query, showing how the database will execute it and provides detailed cost estimates.")
async def explain_query(
    sql: str = Field(description="SQL query to explain"),
    analyze: bool = Field(
        description="When True, actually runs the query to show real execution statistics instead of estimates. "
        "Takes longer but provides more accurate information.",
        default=False,
    ),
    hypothetical_indexes: list[dict[str, Any]] = Field(
        description="""A list of hypothetical indexes to simulate. Each index must be a dictionary with these keys:
    - 'table': The table name to add the index to (e.g., 'users')
    - 'columns': List of column names to include in the index (e.g., ['email'] or ['last_name', 'first_name'])
    - 'using': Optional index method (default: 'btree', other options include 'hash', 'gist', etc.)

Examples: [
    {"table": "users", "columns": ["email"], "using": "btree"},
    {"table": "orders", "columns": ["user_id", "created_at"]}
]
If there is no hypothetical index, you can pass an empty list.""",
        default=[],
    ),
) -> ResponseType:
    """
    Explains the execution plan for a SQL query.

    Args:
        sql: The SQL query to explain
        analyze: When True, actually runs the query for real statistics
        hypothetical_indexes: Optional list of indexes to simulate
    """
    try:
        sql_driver = await get_sql_driver()
        explain_tool = ExplainPlanTool(sql_driver=sql_driver)
        result: ExplainPlanArtifact | ErrorResult | None = None

        # If hypothetical indexes are specified, check for HypoPG extension
        if hypothetical_indexes and len(hypothetical_indexes) > 0:
            if analyze:
                return format_error_response("Cannot use analyze and hypothetical indexes together")
            try:
                # Use the common utility function to check if hypopg is installed
                (
                    is_hypopg_installed,
                    hypopg_message,
                ) = await check_hypopg_installation_status(sql_driver)

                # If hypopg is not installed, return the message
                if not is_hypopg_installed:
                    return format_text_response(hypopg_message)

                # HypoPG is installed, proceed with explaining with hypothetical indexes
                result = await explain_tool.explain_with_hypothetical_indexes(sql, hypothetical_indexes)
            except Exception:
                raise  # Re-raise the original exception
        elif analyze:
            try:
                # Use EXPLAIN ANALYZE
                result = await explain_tool.explain_analyze(sql)
            except Exception:
                raise  # Re-raise the original exception
        else:
            try:
                # Use basic EXPLAIN
                result = await explain_tool.explain(sql)
            except Exception:
                raise  # Re-raise the original exception

        if result and isinstance(result, ExplainPlanArtifact):
            return format_text_response(result.to_text())
        else:
            error_message = "Error processing explain plan"
            if isinstance(result, ErrorResult):
                error_message = result.to_text()
            return format_error_response(error_message)
    except Exception as e:
        logger.error(f"Error explaining query: {e}")
        return format_error_response(str(e))


# Query function declaration without the decorator - we'll add it dynamically based on access mode
async def execute_sql(
    sql: str = Field(description="SQL to run", default="all"),
) -> ResponseType:
    """Executes a SQL query against the database."""
    try:
        sql_driver = await get_sql_driver()
        rows = await sql_driver.execute_query(sql)  # type: ignore
        if rows is None:
            return format_text_response("No results")
        results = [r.cells for r in rows]
        return format_text_response(format_query_results_as_text(results))
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return format_error_response(str(e))


@mcp.tool(description="Analyze frequently executed queries in the database and recommend optimal indexes")
@validate_call
async def analyze_workload_indexes(
    max_index_size_mb: int = Field(description="Max index size in MB", default=10000),
    method: Literal["dta", "llm"] = Field(description="Method to use for analysis", default="dta"),
) -> ResponseType:
    """Analyze frequently executed queries in the database and recommend optimal indexes."""
    try:
        sql_driver = await get_sql_driver()
        if method == "dta":
            index_tuning = DatabaseTuningAdvisor(sql_driver)
        else:
            index_tuning = LLMOptimizerTool(sql_driver)
        dta_tool = TextPresentation(sql_driver, index_tuning)
        result = await dta_tool.analyze_workload(max_index_size_mb=max_index_size_mb)
        return format_text_response(result)
    except Exception as e:
        logger.error(f"Error analyzing workload: {e}")
        return format_error_response(str(e))


@mcp.tool(description="Analyze a list of (up to 10) SQL queries and recommend optimal indexes")
@validate_call
async def analyze_query_indexes(
    queries: list[str] = Field(description="List of Query strings to analyze"),
    max_index_size_mb: int = Field(description="Max index size in MB", default=10000),
    method: Literal["dta", "llm"] = Field(description="Method to use for analysis", default="dta"),
) -> ResponseType:
    """Analyze a list of SQL queries and recommend optimal indexes."""
    if len(queries) == 0:
        return format_error_response("Please provide a non-empty list of queries to analyze.")
    if len(queries) > MAX_NUM_INDEX_TUNING_QUERIES:
        return format_error_response(f"Please provide a list of up to {MAX_NUM_INDEX_TUNING_QUERIES} queries to analyze.")

    try:
        sql_driver = await get_sql_driver()
        if method == "dta":
            index_tuning = DatabaseTuningAdvisor(sql_driver)
        else:
            index_tuning = LLMOptimizerTool(sql_driver)
        dta_tool = TextPresentation(sql_driver, index_tuning)
        result = await dta_tool.analyze_queries(queries=queries, max_index_size_mb=max_index_size_mb)
        return format_text_response(result)
    except Exception as e:
        logger.error(f"Error analyzing queries: {e}")
        return format_error_response(str(e))


@mcp.tool(
    description="Analyzes database health. Here are the available health checks:\n"
    "- index - checks for invalid, duplicate, and bloated indexes\n"
    "- connection - checks the number of connection and their utilization\n"
    "- vacuum - checks vacuum health for transaction id wraparound\n"
    "- sequence - checks sequences at risk of exceeding their maximum value\n"
    "- replication - checks replication health including lag and slots\n"
    "- buffer - checks for buffer cache hit rates for indexes and tables\n"
    "- constraint - checks for invalid constraints\n"
    "- all - runs all checks\n"
    "You can optionally specify a single health check or a comma-separated list of health checks. The default is 'all' checks."
)
async def analyze_db_health(
    health_type: str = Field(
        description=f"Optional. Valid values are: {', '.join(sorted([t.value for t in HealthType]))}.",
        default="all",
    ),
) -> ResponseType:
    """Analyze database health for specified components.

    Args:
        health_type: Comma-separated list of health check types to perform.
                    Valid values: index, connection, vacuum, sequence, replication, buffer, constraint, all
    """
    health_tool = DatabaseHealthTool(await get_sql_driver())
    result = await health_tool.health(health_type=health_type)
    return format_text_response(result)


@mcp.tool(
    name="get_top_queries",
    description=f"Reports the slowest or most resource-intensive queries using data from the '{PG_STAT_STATEMENTS}' extension.",
)
async def get_top_queries(
    sort_by: str = Field(
        description="Ranking criteria: 'total_time' for total execution time or 'mean_time' for mean execution time per call, or 'resources' "
        "for resource-intensive queries",
        default="resources",
    ),
    limit: int = Field(description="Number of queries to return when ranking based on mean_time or total_time", default=10),
) -> ResponseType:
    try:
        sql_driver = await get_sql_driver()
        top_queries_tool = TopQueriesCalc(sql_driver=sql_driver)

        if sort_by == "resources":
            result = await top_queries_tool.get_top_resource_queries()
            return format_text_response(result)
        elif sort_by == "mean_time" or sort_by == "total_time":
            # Map the sort_by values to what get_top_queries_by_time expects
            result = await top_queries_tool.get_top_queries_by_time(limit=limit, sort_by="mean" if sort_by == "mean_time" else "total")
        else:
            return format_error_response("Invalid sort criteria. Please use 'resources' or 'mean_time' or 'total_time'.")
        return format_text_response(result)
    except Exception as e:
        logger.error(f"Error getting slow queries: {e}")
        return format_error_response(str(e))


@mcp.tool(description="Get comprehensive database overview with performance and security analysis")
async def get_database_overview(
    max_tables: int = Field(description="Maximum number of tables to analyze per schema", default=500),
    sampling_mode: bool = Field(description="Use statistical sampling for large datasets", default=True),
    timeout: int = Field(description="Maximum execution time in seconds", default=300),
) -> ResponseType:
    """Get comprehensive database overview including schemas, tables, relationships, performance metrics, and security analysis."""
    try:
        sql_driver = await get_sql_driver()
        overview_tool = DatabaseOverviewTool(sql_driver)
        result = await overview_tool.get_database_overview(max_tables, sampling_mode, timeout)
        return format_text_response(result)
    except Exception as e:
        logger.error(f"Error getting database overview: {e}")
        return format_error_response(str(e))


@mcp.tool(description="Analyze schema relationships and dependencies with visual representation")
async def analyze_schema_relationships() -> ResponseType:
    """Analyze inter-schema dependencies and relationships with visual representation data."""
    try:
        sql_driver = await get_sql_driver()
        mapping_tool = SchemaMappingTool(sql_driver)

        # Get user schemas
        user_schemas_query = """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            AND schema_name NOT LIKE 'pg_temp_%'
            AND schema_name NOT LIKE 'pg_toast_temp_%'
            ORDER BY schema_name
        """

        rows = await sql_driver.execute_query(user_schemas_query)
        user_schemas = [row.cells["schema_name"] for row in rows] if rows else []

        # Analyze schema relationships
        result = await mapping_tool.analyze_schema_relationships(user_schemas)

        return format_text_response(result)

    except Exception as e:
        logger.error(f"Error analyzing schema relationships: {e}")
        return format_error_response(str(e))


@mcp.tool(description="Get comprehensive blocking queries analysis with lock information, hierarchy, and recommendations")
async def get_blocking_queries() -> ResponseType:
    """Get comprehensive information about blocking queries and locks in the database with analysis and recommendations."""
    try:
        sql_driver = await get_sql_driver()
        analyzer = BlockingQueriesAnalyzer(sql_driver)
        result = await analyzer.get_blocking_queries()
        return format_text_response(result)
    except Exception as e:
        logger.error(f"Error getting blocking queries: {e}")
        return format_error_response(str(e))


@mcp.tool(description="Comprehensive vacuum analysis with maintenance recommendations and bloat detection")
async def analyze_vacuum_requirements() -> ResponseType:
    """Analyze database vacuum requirements with comprehensive recommendations for maintenance."""
    try:
        sql_driver = await get_sql_driver()
        vacuum_tool = VacuumAnalysisTool(sql_driver)

        # Perform comprehensive vacuum analysis
        result = await vacuum_tool.analyze_vacuum_requirements()

        return format_text_response(result)

    except Exception as e:
        logger.error(f"Error analyzing vacuum requirements: {e}")
        return format_error_response(str(e))


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PostgreSQL MCP Server")
    parser.add_argument("database_url", help="Database connection URL", nargs="?")
    parser.add_argument(
        "--access-mode",
        type=str,
        choices=[mode.value for mode in AccessMode],
        default=AccessMode.UNRESTRICTED.value,
        help="Set SQL access mode: unrestricted (unrestricted) or restricted (read-only with protections)",
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        default="stdio",
        help="Select MCP transport: stdio (default) or sse",
    )
    parser.add_argument(
        "--sse-host",
        type=str,
        default="localhost",
        help="Host to bind SSE server to (default: localhost)",
    )
    parser.add_argument(
        "--sse-port",
        type=int,
        default=8000,
        help="Port for SSE server (default: 8000)",
    )

    args = parser.parse_args()

    # Store the access mode in the global variable
    global current_access_mode
    current_access_mode = AccessMode(args.access_mode)

    # Add the query tool with a description appropriate to the access mode
    if current_access_mode == AccessMode.UNRESTRICTED:
        mcp.add_tool(execute_sql, description="Execute any SQL query")
    else:
        mcp.add_tool(execute_sql, description="Execute a read-only SQL query")

    logger.info(f"Starting PostgreSQL MCP Server in {current_access_mode.upper()} mode")

    # Get database URL from environment variable or command line
    database_url = os.environ.get("DATABASE_URI", args.database_url)

    if not database_url:
        raise ValueError(
            "Error: No database URL provided. Please specify via 'DATABASE_URI' environment variable or command-line argument.",
        )

    # Initialize database connection pool
    try:
        await db_connection.pool_connect(database_url)
        logger.info("Successfully connected to database and initialized connection pool")
    except Exception as e:
        logger.warning(
            f"Could not connect to database: {obfuscate_password(str(e))}",
        )
        logger.warning(
            "The MCP server will start but database operations will fail until a valid connection is established.",
        )

    # Set up proper shutdown handling
    try:
        loop = asyncio.get_running_loop()
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s)))
    except NotImplementedError:
        # Windows doesn't support signals properly
        logger.warning("Signal handling not supported on Windows")
        pass

    # Run the server with the selected transport (always async)
    if args.transport == "stdio":
        await mcp.run_stdio_async()
    else:
        # Update FastMCP settings based on command line arguments
        mcp.settings.host = args.sse_host
        mcp.settings.port = args.sse_port
        await mcp.run_sse_async()


async def shutdown(sig=None):
    """Clean shutdown of the server."""
    global shutdown_in_progress

    if shutdown_in_progress:
        logger.warning("Forcing immediate exit")
        # Use sys.exit instead of os._exit to allow for proper cleanup
        sys.exit(1)

    shutdown_in_progress = True

    if sig:
        logger.info(f"Received exit signal {sig.name}")

    # Close database connections
    try:
        await db_connection.close()
        logger.info("Closed database connections")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

    # Exit with appropriate status code
    sys.exit(128 + sig if sig is not None else 0)

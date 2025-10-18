import logging
from typing import Literal
from typing import LiteralString
from typing import Union
from typing import cast

from ..sql import SafeSqlDriver
from ..sql import SqlDriver
from ..sql.extension_utils import check_extension
from ..sql.extension_utils import get_postgres_version

logger = logging.getLogger(__name__)

PG_STAT_STATEMENTS = "pg_stat_statements"

install_pg_stat_statements_message = (
    "pg_stat_statements not installed. Install with: CREATE EXTENSION pg_stat_statements; "
    "It records per-query stats (time, calls, rows). Safe, standard, low overhead."
)


class TopQueriesCalc:
    """Tool for retrieving the slowest SQL queries."""

    def __init__(self, sql_driver: Union[SqlDriver, SafeSqlDriver]):
        self.sql_driver = sql_driver

    async def get_top_queries_by_time(self, limit: int = 10, sort_by: Literal["total", "mean"] = "mean") -> str:
        """Reports the slowest SQL queries based on execution time.

        Args:
            limit: Number of slow queries to return
            sort_by: Sort criteria - 'total' for total execution time or
                'mean' for mean execution time per call (default)

        Returns:
            A string with the top queries or installation instructions
        """
        try:
            logger.debug(f"Getting top queries by time. limit={limit}, sort_by={sort_by}")
            extension_status = await check_extension(
                self.sql_driver,
                PG_STAT_STATEMENTS,
                include_messages=False,
            )

            if not extension_status.is_installed:
                logger.warning(f"Extension {PG_STAT_STATEMENTS} is not installed")
                # Return installation instructions if the extension is not installed
                return install_pg_stat_statements_message

            # Check PostgreSQL version to determine column names
            pg_version = await get_postgres_version(self.sql_driver)
            logger.debug(f"PostgreSQL version: {pg_version}")

            # Column names changed in PostgreSQL 13
            if pg_version >= 13:
                # PostgreSQL 13 and newer
                total_time_col = "total_exec_time"
                mean_time_col = "mean_exec_time"
            else:
                # PostgreSQL 12 and older
                total_time_col = "total_time"
                mean_time_col = "mean_time"

            logger.debug(f"Using time columns: total={total_time_col}, mean={mean_time_col}")

            # Determine which column to sort by based on sort_by parameter and version
            order_by_column = total_time_col if sort_by == "total" else mean_time_col

            query = f"""
                SELECT
                    query,
                    calls,
                    {total_time_col},
                    {mean_time_col},
                    rows
                FROM pg_stat_statements
                ORDER BY {order_by_column} DESC
                LIMIT {{}};
            """
            logger.debug(f"Executing query: {query}")
            slow_query_rows = await SafeSqlDriver.execute_param_query(
                self.sql_driver,
                query,
                [limit],
            )
            slow_queries = [row.cells for row in slow_query_rows] if slow_query_rows else []
            logger.info(f"Found {len(slow_queries)} slow queries")

            # Create result description based on sort criteria
            if sort_by == "total":
                criteria = "total execution time"
            else:
                criteria = "mean execution time per call"

            lines = [f"Top{len(slow_queries)} by {criteria}:"]
            for i, q in enumerate(slow_queries[:limit], 1):
                query_txt = (q.get("query") or "").strip().replace("\n", " ")
                if len(query_txt) > 120:
                    query_txt = query_txt[:117] + "..."
                total = q.get(total_time_col, 0)
                mean = q.get(mean_time_col, 0)
                calls = q.get("calls", 0)
                rows = q.get("rows", 0)
                lines.append(f"{i}. calls={calls} total={float(total):.2f}ms mean={float(mean):.2f}ms rows={rows} | {query_txt}")
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error getting slow queries: {e}", exc_info=True)
            return f"Error getting slow queries: {e}"

    async def get_top_resource_queries(self, frac_threshold: float = 0.05) -> str:
        """Reports the most time consuming queries based on a resource blend.

        Args:
            frac_threshold: Fraction threshold for filtering queries (default: 0.05)

        Returns:
            A string with the resource-heavy queries or error message
        """

        try:
            logger.debug(f"Getting top resource queries with threshold {frac_threshold}")
            extension_status = await check_extension(
                self.sql_driver,
                PG_STAT_STATEMENTS,
                include_messages=False,
            )

            if not extension_status.is_installed:
                logger.warning(f"Extension {PG_STAT_STATEMENTS} is not installed")
                # Return installation instructions if the extension is not installed
                return install_pg_stat_statements_message

            # Check PostgreSQL version to determine column names
            pg_version = await get_postgres_version(self.sql_driver)
            logger.debug(f"PostgreSQL version: {pg_version}")

            # Column names changed in PostgreSQL 13
            if pg_version >= 13:
                # PostgreSQL 13 and newer
                total_time_col = "total_exec_time"
                mean_time_col = "mean_exec_time"
            else:
                # PostgreSQL 12 and older
                total_time_col = "total_time"
                mean_time_col = "mean_time"

            query = cast(
                LiteralString,
                f"""
                WITH resource_fractions AS (
                    SELECT
                        query,
                        calls,
                        rows,
                        {total_time_col} total_exec_time,
                        {mean_time_col} mean_exec_time,
                        stddev_exec_time,
                        shared_blks_hit,
                        shared_blks_read,
                        shared_blks_dirtied,
                        wal_bytes,
                        total_exec_time / SUM(total_exec_time) OVER () AS total_exec_time_frac,
                        (shared_blks_hit + shared_blks_read) / SUM(shared_blks_hit + shared_blks_read) OVER () AS shared_blks_accessed_frac,
                        shared_blks_read / SUM(shared_blks_read) OVER () AS shared_blks_read_frac,
                        shared_blks_dirtied / SUM(shared_blks_dirtied) OVER () AS shared_blks_dirtied_frac,
                        wal_bytes / SUM(wal_bytes) OVER () AS total_wal_bytes_frac
                    FROM pg_stat_statements
                )
                SELECT
                    query,
                    calls,
                    rows,
                    total_exec_time,
                    mean_exec_time,
                    stddev_exec_time,
                    total_exec_time_frac,
                    shared_blks_accessed_frac,
                    shared_blks_read_frac,
                    shared_blks_dirtied_frac,
                    total_wal_bytes_frac,
                    shared_blks_hit,
                    shared_blks_read,
                    shared_blks_dirtied,
                    wal_bytes
                FROM resource_fractions
                WHERE
                    total_exec_time_frac > {frac_threshold}
                    OR shared_blks_accessed_frac > {frac_threshold}
                    OR shared_blks_read_frac > {frac_threshold}
                    OR shared_blks_dirtied_frac > {frac_threshold}
                    OR total_wal_bytes_frac > {frac_threshold}
                ORDER BY total_exec_time DESC
            """,
            )

            logger.debug(f"Executing query: {query}")
            slow_query_rows = await SafeSqlDriver.execute_param_query(
                self.sql_driver,
                query,
            )
            resource_queries = [row.cells for row in slow_query_rows] if slow_query_rows else []
            logger.info(f"Found {len(resource_queries)} resource-intensive queries")

            lines = [f"Top{len(resource_queries)} by resource blend (thr={frac_threshold:.2f}):"]
            for i, q in enumerate(resource_queries, 1):
                query_txt = (q.get("query") or "").strip().replace("\n", " ")
                if len(query_txt) > 120:
                    query_txt = query_txt[:117] + "..."
                calls = q.get("calls", 0)
                total = q.get("total_exec_time", 0)
                mean = q.get("mean_exec_time", 0)
                frac_total = q.get("total_exec_time_frac", 0)
                frac_access = q.get("shared_blks_accessed_frac", 0)
                frac_read = q.get("shared_blks_read_frac", 0)
                frac_dirt = q.get("shared_blks_dirtied_frac", 0)
                frac_wal = q.get("total_wal_bytes_frac", 0)
                lines.append(
                    f"{i} . calls={calls} total={float(total):.2f}ms mean={float(mean):.2f}ms frac(t/access/read/dirt/wal)="
                    f"{float(frac_total):.2f}/{float(frac_access):.2f}/{float(frac_read):.2f}/{float(frac_dirt):.2f}/{float(frac_wal):.2f} | {query_txt}"
                )
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error getting resource-intensive queries: {e}", exc_info=True)
            return f"Error resource-intensive queries: {e}"

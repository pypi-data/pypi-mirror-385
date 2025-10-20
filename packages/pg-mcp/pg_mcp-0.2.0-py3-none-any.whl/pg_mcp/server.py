# ruff: noqa: B008
import argparse
import logging
import os
import signal
import sys
from enum import Enum
from typing import Any

import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from pg_mcp import ConnectionRegistry
from pg_mcp import SafeSqlDriver
from pg_mcp import SqlDriver
from pg_mcp import obfuscate_password


def setup_logging(transport: str = "stdio") -> None:
    """
    Configure logging based on transport type and LOG_LEVEL environment variable.

    For stdio transport, logs go to stderr to avoid interfering with MCP protocol on stdout.
    For SSE transport, logs can go to stdout.

    LOG_LEVEL environment variable controls verbosity:
    - DEBUG: Show all logs including debug messages
    - INFO: Show info, warning, and error messages (default)
    - WARNING: Show only warnings and errors
    - ERROR: Show only errors
    - CRITICAL: Show only critical errors
    - NONE: Disable all logging
    """
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()

    # Handle special case: disable logging
    if log_level_str == "NONE":
        logging.disable(logging.CRITICAL)
        return

    # Map string to logging level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = level_map.get(log_level_str, logging.INFO)

    # For stdio transport, ALWAYS use stderr to avoid breaking MCP protocol
    # For SSE transport, stdout is fine since MCP uses HTTP
    stream = sys.stderr if transport == "stdio" else sys.stdout

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=stream,
        force=True,  # Override any existing configuration
    )


# Initialize FastMCP with default settings
# Note: Server instructions will be updated after database connections are discovered
mcp = FastMCP("postgres-mcp")

ResponseType = list[types.TextContent | types.ImageContent | types.EmbeddedResource]

logger = logging.getLogger(__name__)


class AccessMode(str, Enum):
    """SQL access modes for the server."""

    UNRESTRICTED = "unrestricted"  # Unrestricted access
    RESTRICTED = "restricted"  # Read-only with safety features


# Global variables
connection_registry = ConnectionRegistry()
current_access_mode = AccessMode.UNRESTRICTED
shutdown_in_progress = False


def get_sql_driver(conn_name: str) -> SqlDriver | SafeSqlDriver:
    """
    Get the appropriate SQL driver based on the current access mode.

    Args:
        conn_name: Connection name (e.g., "default", "app", "etl")

    Returns:
        SqlDriver or SafeSqlDriver instance

    Raises:
        ValueError: If connection name doesn't exist
    """
    db_connection = connection_registry.get_connection(conn_name)
    base_driver = SqlDriver(conn=db_connection)

    if current_access_mode == AccessMode.RESTRICTED:
        logger.debug(f"Using SafeSqlDriver with restrictions for '{conn_name}' (RESTRICTED mode)")
        return SafeSqlDriver(sql_driver=base_driver, timeout=30)  # 30 second timeout
    else:
        logger.debug(f"Using unrestricted SqlDriver for '{conn_name}' (UNRESTRICTED mode)")
        return base_driver


def format_text_response(text: Any) -> ResponseType:
    """Format a text response."""
    return [types.TextContent(type="text", text=str(text))]


def format_error_response(error: str) -> ResponseType:
    """Format an error response."""
    return format_text_response(f"Error: {error}")


@mcp.tool(description="List all schemas in the database")
def list_schemas(
    conn_name: str = Field(description="Connection name - see server instructions for available connections"),
) -> ResponseType:
    """List all schemas in the database."""
    try:
        sql_driver = get_sql_driver(conn_name)
        rows = sql_driver.execute_query(
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
        return format_text_response(schemas)
    except Exception as e:
        logger.error(f"Error listing schemas: {e}")
        return format_error_response(str(e))


@mcp.tool(description="List objects in a schema")
def list_objects(
    conn_name: str = Field(description="Connection name - see server instructions for available connections"),
    schema_name: str = Field(description="Schema name"),
    object_type: str = Field(description="Object type: 'table', 'view', 'sequence', or 'extension'", default="table"),
) -> ResponseType:
    """List objects of a given type in a schema."""
    try:
        sql_driver = get_sql_driver(conn_name)

        if object_type in ("table", "view"):
            table_type = "BASE TABLE" if object_type == "table" else "VIEW"
            rows = SafeSqlDriver.execute_param_query(
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
                [{"schema": row.cells["table_schema"], "name": row.cells["table_name"], "type": row.cells["table_type"]} for row in rows]
                if rows
                else []
            )

        elif object_type == "sequence":
            rows = SafeSqlDriver.execute_param_query(
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
                [{"schema": row.cells["sequence_schema"], "name": row.cells["sequence_name"], "data_type": row.cells["data_type"]} for row in rows]
                if rows
                else []
            )

        elif object_type == "extension":
            # Extensions are not schema-specific
            rows = sql_driver.execute_query(
                """
                SELECT extname, extversion, extrelocatable
                FROM pg_extension
                ORDER BY extname
                """
            )
            objects = (
                [{"name": row.cells["extname"], "version": row.cells["extversion"], "relocatable": row.cells["extrelocatable"]} for row in rows]
                if rows
                else []
            )

        else:
            return format_error_response(f"Unsupported object type: {object_type}")

        return format_text_response(objects)
    except Exception as e:
        logger.error(f"Error listing objects: {e}")
        return format_error_response(str(e))


@mcp.tool(description="Show detailed information about a database object")
def get_object_details(
    conn_name: str = Field(description="Connection name - see server instructions for available connections"),
    schema_name: str = Field(description="Schema name"),
    object_name: str = Field(description="Object name"),
    object_type: str = Field(description="Object type: 'table', 'view', 'sequence', or 'extension'", default="table"),
) -> ResponseType:
    """Get detailed information about a database object."""
    try:
        sql_driver = get_sql_driver(conn_name)

        if object_type in ("table", "view"):
            # Get columns
            col_rows = SafeSqlDriver.execute_param_query(
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
            con_rows = SafeSqlDriver.execute_param_query(
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
            idx_rows = SafeSqlDriver.execute_param_query(
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
            rows = SafeSqlDriver.execute_param_query(
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
            rows = SafeSqlDriver.execute_param_query(
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
                result = {"name": row.cells["extname"], "version": row.cells["extversion"], "relocatable": row.cells["extrelocatable"]}
            else:
                result = {}

        else:
            return format_error_response(f"Unsupported object type: {object_type}")

        return format_text_response(result)
    except Exception as e:
        logger.error(f"Error getting object details: {e}")
        return format_error_response(str(e))


# Query function declaration without the decorator - we'll add it dynamically based on access mode
def execute_sql(
    conn_name: str = Field(description="Connection name - see server instructions for available connections"),
    sql: str = Field(description="SQL to run", default="all"),
) -> ResponseType:
    """Executes a SQL query against the database."""
    try:
        sql_driver = get_sql_driver(conn_name)
        rows = sql_driver.execute_query(sql)  # type: ignore
        if rows is None:
            return format_text_response("No results")
        return format_text_response(list([r.cells for r in rows]))
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return format_error_response(str(e))


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PostgreSQL MCP Server")
    parser.add_argument("database_url", help="Database connection URL", nargs="?")
    parser.add_argument(
        "--access-mode",
        type=str,
        choices=[mode.value for mode in AccessMode],
        default=AccessMode.RESTRICTED.value,
        help="Set SQL access mode: restricted (read-only, default) or unrestricted (full access)",
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

    # Setup logging BEFORE any log statements are made
    # For stdio transport, logs go to stderr to avoid interfering with MCP protocol
    setup_logging(transport=args.transport)

    # Store the access mode in the global variable
    global current_access_mode
    current_access_mode = AccessMode(args.access_mode)

    # Add the query tool with a description appropriate to the access mode
    if current_access_mode == AccessMode.UNRESTRICTED:
        mcp.add_tool(execute_sql, description="Execute any SQL query")
    else:
        mcp.add_tool(execute_sql, description="Execute a read-only SQL query")

    logger.info(f"Starting PostgreSQL MCP Server in {current_access_mode.upper()} mode")

    # Initialize database connection registry
    # For backwards compatibility, support command-line database_url argument
    if args.database_url and "DATABASE_URI" not in os.environ:
        os.environ["DATABASE_URI"] = args.database_url
        logger.info("Using command-line database URL as DATABASE_URI")

    try:
        connection_registry.discover_and_connect()
        conn_names = connection_registry.get_connection_names()
        logger.info(f"Successfully initialized {len(conn_names)} connection(s): {', '.join(conn_names)}")

        # Update server context with available connections
        conn_info = connection_registry.get_connection_info()
        if conn_info:
            instructions = ["Available database connections:"]
            for info in conn_info:
                if "description" in info:
                    instructions.append(f"- {info['name']}: {info['description']}")
                else:
                    instructions.append(f"- {info['name']}")

            # Set the server instructions to include connection information
            mcp._instructions = "\n".join(instructions)  # type: ignore
            logger.info(f"Updated server context with {len(conn_info)} connection(s)")
    except Exception as e:
        logger.warning(
            f"Could not initialize database connections: {obfuscate_password(str(e))}",
        )
        logger.warning(
            "The MCP server will start but database operations will fail until valid connections are established.",
        )

    # Set up proper shutdown handling for Unix-like systems
    try:
        signals = (signal.SIGTERM, signal.SIGINT)
        for s in signals:
            signal.signal(s, lambda sig, frame: shutdown(sig))
    except (AttributeError, ValueError):
        # Windows or signals not available
        logger.warning("Signal handling not fully supported on this platform")

    # Run the server with the selected transport
    if args.transport == "stdio":
        mcp.run()
    else:
        # Update FastMCP settings based on command line arguments
        mcp.settings.host = args.sse_host
        mcp.settings.port = args.sse_port
        mcp.run()


def shutdown(sig=None):
    """Clean shutdown of the server."""
    global shutdown_in_progress

    if shutdown_in_progress:
        logger.warning("Forcing immediate exit")
        # Use sys.exit instead of os._exit to allow for proper cleanup
        sys.exit(1)

    shutdown_in_progress = True

    if sig:
        logger.info(f"Received exit signal {sig}")

    # Close all database connections
    try:
        connection_registry.close_all()
        logger.info("Closed all database connections")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

    # Exit with appropriate status code
    sys.exit(128 + sig if sig is not None else 0)


def run():
    """Entry point for the CLI command."""
    main()

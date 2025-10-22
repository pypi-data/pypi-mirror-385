"""
Database Tools Dispatcher (Generic)

This module provides generic, engine-agnostic database tools and dispatchers for the Tessell MCP platform. 
All engine-specific logic—such as engine implementations, queries, and database operations—must be implemented in their respective engine modules (e.g., postgresql_engine.py, oracle_engine.py). 
This ensures a clean separation of concerns, maintainability, and extensibility as new database engines are added (e.g., MySQL, SQL Server).

Key Points:
- Only generic, engine-agnostic logic and tool dispatchers should reside in this file.
- The _get_engine_for_connection helper is used to select and instantiate the correct engine class based on the connection string.
- All engine-dispatching tools (such as create_database) must use this pattern.
- This pattern ensures code quality, reduces duplication, and makes it easy to add support for new engines.

"""

import logging
from typing import Dict, Any, Optional
from mcp_core.mcp_server import mcp
from .base.connection_manager import connection_manager
from .postgresql.postgresql_engine import PostgreSQLEngine
from .oracle.oracle_engine import OracleEngine

logger = logging.getLogger(__name__)

# TODO: Test the readonly-db configuration and .json configuration for connection strings (advanced configuration). See examples/mcp.examples.json for context.
# TODO: Oracle is yet to be tested; currently fails for connections requiring the Oracle thick client in the local file path.
# TODO: Connection string logic, _get_engine_for_connection and temp_engine require refactoring to be more robust and efficient. Thoughts: database name should be sufficient in most of the cases, connection should be there on that name, think about exceptions. 

def _get_engine_for_connection(connection_name: str):
    """
    Factory to get the correct engine for a connection name.
    Raises an Exception if the connection or engine type is not supported.
    """
    conn_str = connection_manager.get_connection_string(connection_name)
    if not conn_str:
        raise Exception(f"Connection not found: {connection_name}")
    if 'postgresql' in conn_str:
        return PostgreSQLEngine(conn_str)
    elif 'oracle' in conn_str:
        return OracleEngine(conn_str)
    # Add more engines here as needed
    else:
        raise Exception("Unsupported engine type.")

# ----------------------
# 1. Database Lifecycle Management
# ----------------------
@mcp.tool()
def create_database(connection_name: str, database_name: str):
    """
    Create a new database with the current user as the owner.

    - For PostgreSQL: Creates a new database with the current user as owner.
    - For Oracle: Not implemented (returns a not implemented error).

    Args:
        connection_name (str): The name of the connection to use.
        database_name (str): The name of the database to create.

    Returns:
        dict: Result of the operation or error message.
    """
    try:
        engine = _get_engine_for_connection(connection_name)
    except Exception as e:
        logger.error(str(e))
        return {"status_code": 400, "error": str(e)}
    if not engine.connect():
        return {"status_code": 500, "error": f"Failed to connect to {engine.__class__.__name__}."}
    try:
        result = engine.create_database(database_name)
        return result
    finally:
        engine.disconnect()

# ----------------------
# 2. Metadata & Discovery
# ----------------------

@mcp.tool()
def list_schemas(connection_name: str, database: str) -> Dict[str, Any]:
    """
    List all schemas in the specified database for a given connection.
    Call this tool to enumerate schemas in a database.
    
    Parameters:
        connection_name (str): The name of the connection.
        database (str): The database name.
    
    Returns:
        dict: {"success": True, "schemas": [<schema1>, <schema2>, ...]} on success.
              {"success": False, "error": <error_message>} on failure.
    """
    try:
        engine = _get_engine_for_connection(connection_name)
        if not engine.connect():
            return {"success": False, "error": "Failed to connect to database server."}
        schemas = engine.list_schemas(database)
        engine.disconnect()
        return {"success": True, "schemas": schemas}
    except Exception as e:
        logger.error(f"list_schemas error: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def list_objects(connection_name: str, database: str, schema: str) -> Dict[str, Any]:
    """
    List all objects (tables, views, sequences, extensions) in a schema.
    Use this tool to enumerate all objects in a schema. To get only tables, use the 'tables' key in the returned 'objects' dict (e.g., objects['tables']).
    
    Parameters:
        connection_name (str): The name of the connection.
        database (str): The database name.
        schema (str): The schema name.
    
    Returns:
        dict: {"success": True, "objects": {"tables": [...], "views": [...], ...}} on success.
              {"success": False, "error": <error_message>} on failure.
    """
    try:
        engine = _get_engine_for_connection(connection_name)
        if not engine.connect():
            return {"success": False, "error": "Failed to connect to database server."}
        objects = engine.list_objects_in_schema(database, schema)
        engine.disconnect()
        return {"success": True, "objects": objects}
    except Exception as e:
        logger.error(f"list_objects error: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def describe_object(connection_name: str, database: str, schema: str, object_name: str, object_type: str) -> Dict[str, Any]:
    """
    Get detailed information about a database object (table, view, sequence, extension).
    Use this tool to get metadata for any object in a schema, including tables.
    
    Parameters:
        connection_name (str): The name of the connection.
        database (str): The database name.
        schema (str): The schema name.
        object_name (str): The object name.
        object_type (str): The type of object. Options:
            - "table": For tables (returns schema, constraints, indexes, stats, etc.)
            - "view": For views
            - "sequence": For sequences
            - "extension": For extensions
    
    Returns:
        dict: {"success": True, "description": <object_description>} on success.
              {"success": False, "error": <error_message>} on failure.
    
    Note:
        Use this tool for tables as well as other object types. All details previously available via describe_table are available here when object_type is "table".
    """
    try:
        engine = _get_engine_for_connection(connection_name)
        if not engine.connect():
            return {"success": False, "error": "Failed to connect to database server."}
        desc = engine.describe_object(database, schema, object_name, object_type)
        engine.disconnect()
        return {"success": True, "description": desc}
    except Exception as e:
        logger.error(f"describe_object error: {e}")
        return {"success": False, "error": str(e)}

# ----------------------
# 3. Data Access
# ----------------------

@mcp.tool()
def get_sample_data(connection_name: str, database: str, schema: str, object_name: str, object_type: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get sample data from a table or view.
    Use this tool to preview a few rows from a table or view. Specify object_type as 'table' or 'view'.
    
    Parameters:
        connection_name (str): The name of the connection.
        database (str): The database name.
        schema (str): The schema name.
        object_name (str): The table or view name.
        object_type (str): 'table' or 'view'.
        limit (int, optional): Number of rows to return (default: 10).
    
    Returns:
        dict: {"success": True, "sample_data": [<row1>, <row2>, ...], "columns": [...], ...} on success.
              {"success": False, "error": <error_message>} on failure.
    """
    try:
        engine = _get_engine_for_connection(connection_name)
        if object_type in ("table", "view"):
            desc = engine.get_sample_data(database, f"{schema}.{object_name}", limit)
        else:
            desc = {"success": False, "error": f"Sample data not supported for object_type: {object_type}"}
        return desc
    except Exception as e:
        logger.error(f"get_sample_data error: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def execute_query(connection_name: str, database: str, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute a custom SQL query (read-only enforced if configured).
    Call this tool to run a SQL query on a database. Use for SELECT or safe queries only.
    
    Parameters:
        connection_name (str): The name of the connection.
        database (str): The database name.
        query (str): The SQL query to execute.
        params (dict, optional): Query parameters (if any).
    
    Returns:
        dict: {"success": True, ...result...} on success (result structure depends on query).
              {"success": False, "error": <error_message>} on failure.
    """
    try:
        engine = _get_engine_for_connection(connection_name)
        # Switch to the right database
        db_conn_str = engine._get_db_connection_string(database)
        if not db_conn_str:
            return {"success": False, "error": f"Cannot connect to database: {database}"}
        temp_engine = PostgreSQLEngine(db_conn_str)
        if not temp_engine.connect():
            return {"success": False, "error": f"Failed to connect to database: {database}"}
        result = temp_engine.execute_query(query, params)
        temp_engine.disconnect()
        return result
    except Exception as e:
        logger.error(f"execute_query error: {e}")
        return {"success": False, "error": str(e)}

# ----------------------
# 4. Performance/Health
# ----------------------

@mcp.tool()
def get_top_queries(connection_name: str, database: str, sort_by: str = "mean_time", limit: int = 10) -> Dict[str, Any]:
    """
    Get the top slowest or most resource-intensive queries using pg_stat_statements.
    Call this tool to analyze query performance and find slow/resource-heavy queries.
    
    Parameters:
        connection_name (str): The name of the connection.
        database (str): The database name.
        sort_by (str, optional): Field to sort by. Options:
            - "mean_time" (default): Sort by average execution time
            - "calls": Sort by number of calls
            - "rows": Sort by rows returned
            - "total_time": Sort by total execution time
        limit (int, optional): Number of queries to return (default: 10).
    
    Returns:
        dict: {"success": True, "top_queries": [<query1>, <query2>, ...]} on success.
              {"success": False, "error": <error_message>} on failure.
    """
    try:
        engine = _get_engine_for_connection(connection_name)
        if not engine.connect():
            return {"success": False, "error": "Failed to connect to database server."}
        queries = engine.get_top_queries(database, sort_by, limit)
        engine.disconnect()
        return {"success": True, "top_queries": queries}
    except Exception as e:
        logger.error(f"get_top_queries error: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def analyze_db_health(connection_name: str, database: str, check_type: str = "all") -> Dict[str, Any]:
    """
    Perform health checks (index, connection, vacuum, sequence, replication, buffer, constraint) using standard queries/extensions.
    Call this tool to assess database health for various aspects.
    
    Parameters:
        connection_name (str): The name of the connection.
        database (str): The database name.
        check_type (str, optional): What to check. Options:
            - "all" (default): Run all checks
            - "index", "connection", "vacuum", "sequence", "replication", "buffer", "constraint": Run only the specified check
    
    Returns:
        dict: {"success": True, "health": {<check_type>: <result>, ...}} on success.
              {"success": False, "error": <error_message>} on failure.
    """
    try:
        engine = _get_engine_for_connection(connection_name)
        if not engine.connect():
            return {"success": False, "error": "Failed to connect to database server."}
        health = engine.analyze_db_health(database, check_type)
        engine.disconnect()
        return {"success": True, "health": health}
    except Exception as e:
        logger.error(f"analyze_db_health error: {e}")
        return {"success": False, "error": str(e)}

@mcp.tool()
def explain_query(connection_name: str, database: str, query: str, analyze: bool = False) -> Dict[str, Any]:
    """
    Run EXPLAIN or EXPLAIN ANALYZE (FORMAT JSON) on a query and return the plan.
    Call this tool to get the execution plan for a query.
    
    Parameters:
        connection_name (str): The name of the connection.
        database (str): The database name.
        query (str): The SQL query to explain.
        analyze (bool, optional): If True, run EXPLAIN ANALYZE (default: False).
    
    Returns:
        dict: {"success": True, "plan": <plan_json>} on success.
              {"success": False, "error": <error_message>} on failure.
    """
    try:
        engine = _get_engine_for_connection(connection_name)
        if not engine.connect():
            return {"success": False, "error": "Failed to connect to database server."}
        plan = engine.explain_query(database, query, analyze)
        engine.disconnect()
        if "plan" in plan:
            return {"success": True, "plan": plan["plan"]}
        else:
            return {"success": False, "error": plan.get("error", "No plan returned")}
    except Exception as e:
        logger.error(f"explain_query error: {e}")
        return {"success": False, "error": str(e)} 
"""
Oracle database engine implementation using oracledb.

TODO: Implement all methods that are currently not implemented or are placeholders, such as:
- create_database (currently returns not implemented)
- analyze_db_health (currently returns not implemented)
- describe_object for object types other than 'table'
- Any other methods returning 'Not implemented' or partial implementations
"""

import oracledb
import logging
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from ..base.database_engine import DatabaseEngine
from ..base.connection_manager import connection_manager
from ..base.query_validator import QueryValidatorBase
from .oracle_queries import (
    get_query_template,
    format_sample_data_query
)

logger = logging.getLogger(__name__)

class OracleQueryValidator(QueryValidatorBase):
    DANGEROUS_KEYWORDS = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
        'GRANT', 'REVOKE', 'EXECUTE', 'MERGE', 'REPLACE', 'ANALYZE', 'FLASHBACK',
        'PURGE', 'RECOVER', 'RENAME', 'SHUTDOWN', 'STARTUP', 'AUDIT', 'NOAUDIT', 'COMMENT'
    ]
    DANGEROUS_STARTS = [
        'INSERT INTO', 'UPDATE ', 'DELETE FROM', 'DROP ', 'CREATE ',
        'ALTER ', 'TRUNCATE ', 'GRANT ', 'REVOKE ', 'EXECUTE ',
        'MERGE ', 'REPLACE ', 'ANALYZE ', 'FLASHBACK ', 'PURGE ', 'RECOVER ',
        'RENAME ', 'SHUTDOWN ', 'STARTUP ', 'AUDIT ', 'NOAUDIT ', 'COMMENT '
    ]
    SAFE_KEYWORDS = [
        'SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN'
    ]
    SUSPICIOUS_PATTERNS = [
        r"(--|/\*)",  # Comments
        r";\s*[^$]",  # Multiple statements
        r"UNION\s+SELECT",  # UNION attacks
        r"OR\s+1\s*=\s*1",  # Always true conditions
        r"AND\s+1\s*=\s*1", # Always true conditions
    ]

oracle_query_validator = OracleQueryValidator()

class OracleEngine(DatabaseEngine):
    """Oracle database engine implementation."""
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        self._connection_pool = None
        self._pool_size = int(kwargs.get('pool_size', 5))
        self._max_connections = int(kwargs.get('max_connections', 20))
        self._oracle_edition = None

    def connect(self) -> bool:
        try:
            parsed = connection_manager.parse_connection_string(self.connection_string)
            if not parsed:
                logger.error("Invalid Oracle connection string")
                return False
            user = parsed.get('username')
            password = parsed.get('password')
            dsn = parsed.get('host')
            port = parsed.get('port', 1521)
            service_name = parsed.get('database', '')
            logger.error(f"OracleEngine connect: parsed fields: user={user}, password={'***' if password else None}, dsn={dsn}, port={port}, service_name={service_name}")
            dsn_str = f"{dsn}:{port}/{service_name}"
            logger.error(f"OracleEngine connect: constructed dsn_str={dsn_str}")
            self._connection_pool = oracledb.create_pool(
                user=user,
                password=password,
                dsn=dsn_str,
                min=1,
                max=self._max_connections,
                increment=1
            )
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(get_query_template("GET_ORACLE_VERSION_QUERY"))
                    version_row = cursor.fetchone()
                    if version_row:
                        banner = version_row[0]
                        logger.info(f"Connected to Oracle: {banner}")
                        self._oracle_edition = 'Enterprise' if 'Enterprise' in banner else 'Standard'
            self._is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Oracle: {e}")
            self._is_connected = False
            return False

    def disconnect(self) -> bool:
        try:
            if self._connection_pool:
                self._connection_pool.close()
                self._connection_pool = None
            self._is_connected = False
            logger.info("Disconnected from Oracle")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Oracle: {e}")
            return False

    def is_connected(self) -> bool:
        return self._is_connected and self._connection_pool is not None

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = self._connection_pool.acquire()
            yield conn
        finally:
            if conn:
                self._connection_pool.release(conn)

    def _get_connection_from_pool(self):
        if not self._connection_pool:
            raise Exception("Connection pool not initialized")
        return self._connection_pool.acquire()

    def _return_connection_to_pool(self, connection):
        if self._connection_pool and connection:
            self._connection_pool.release(connection)

    def execute_query(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or {})
                    if cursor.description:
                        columns = [col[0] for col in cursor.description]
                        rows = cursor.fetchall()
                        return {"columns": columns, "rows": rows}
                    else:
                        return {"rowcount": cursor.rowcount}
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {"error": str(e)}

    def list_tables(self, database: str) -> List[Dict[str, Any]]:
        # In Oracle, database is not used, schema is used instead
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(get_query_template("LIST_TABLES_QUERY"), {"schema": database})
                    columns = [col[0] for col in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return []

    def describe_table(self, database: str, table: str) -> Dict[str, Any]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(get_query_template("DESCRIBE_TABLE_COLUMNS_QUERY"), {"schema": database, "table": table})
                    columns = [col[0] for col in cursor.description]
                    col_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    cursor.execute(get_query_template("DESCRIBE_TABLE_CONSTRAINTS_QUERY"), {"schema": database, "table": table})
                    cons_columns = [col[0] for col in cursor.description]
                    cons_data = [dict(zip(cons_columns, row)) for row in cursor.fetchall()]
                    cursor.execute(get_query_template("DESCRIBE_TABLE_INDEXES_QUERY"), {"schema": database, "table": table})
                    idx_columns = [col[0] for col in cursor.description]
                    idx_data = [dict(zip(idx_columns, row)) for row in cursor.fetchall()]
                    return {
                        "columns": col_data,
                        "constraints": cons_data,
                        "indexes": idx_data
                    }
        except Exception as e:
            logger.error(f"Error describing table: {e}")
            return {"error": str(e)}

    def get_sample_data(self, database: str, table: str, limit: int = 10) -> Dict[str, Any]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = format_sample_data_query(database, table, limit)
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    return {"columns": columns, "rows": rows}
        except Exception as e:
            logger.error(f"Error getting sample data: {e}")
            return {"error": str(e)}

    def list_schemas(self, database: str) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(get_query_template("LIST_SCHEMAS_QUERY"))
                    columns = [col[0] for col in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listing schemas: {e}")
            return []

    def list_objects_in_schema(self, database: str, schema: str) -> Dict[str, List[Dict[str, Any]]]:
        # For Oracle, list tables/views/sequences in schema
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT table_name FROM all_tables WHERE owner = :schema", {"schema": schema})
                    tables = [row[0] for row in cursor.fetchall()]
                    cursor.execute("SELECT view_name FROM all_views WHERE owner = :schema", {"schema": schema})
                    views = [row[0] for row in cursor.fetchall()]
                    cursor.execute("SELECT sequence_name FROM all_sequences WHERE sequence_owner = :schema", {"schema": schema})
                    sequences = [row[0] for row in cursor.fetchall()]
                    return {"tables": tables, "views": views, "sequences": sequences}
        except Exception as e:
            logger.error(f"Error listing objects in schema: {e}")
            return {}

    def describe_object(self, database: str, schema: str, object_name: str, object_type: str) -> Dict[str, Any]:
        # Only table supported for now
        if object_type.lower() == "table":
            return self.describe_table(schema, object_name)
        # Add more as needed
        return {"error": f"Describe for {object_type} not implemented"}

    def analyze_query_performance(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        # Use EXPLAIN PLAN FOR ...
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"EXPLAIN PLAN FOR {query}", params or {})
                    cursor.execute("SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY())")
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    return {"columns": columns, "rows": rows}
        except Exception as e:
            logger.error(f"Error analyzing query performance: {e}")
            return {"error": str(e)}

    def get_top_queries(self, database: str, sort_by: str = "elapsed_time", limit: int = 10) -> List[Dict[str, Any]]:
        # Requires Oracle Enterprise features (v$ views)
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    try:
                        cursor.execute(f"SELECT * FROM (SELECT sql_id, sql_text, elapsed_time, executions FROM v$sql ORDER BY {sort_by} DESC) WHERE ROWNUM <= :limit", {"limit": limit})
                        columns = [col[0] for col in cursor.description]
                        return [dict(zip(columns, row)) for row in cursor.fetchall()]
                    except Exception as e:
                        # Fallback for Standard Edition (no v$sql)
                        logger.warning(f"Enterprise query failed, falling back to Standard: {e}")
                        return []
        except Exception as e:
            logger.error(f"Error getting top queries: {e}")
            return []

    def analyze_db_health(self, database: str, check_type: str = "all") -> Dict[str, Any]:
        # Implement health checks as needed
        return {"status": "Not implemented"}

    def explain_query(self, database: str, query: str, analyze: bool = False) -> Dict[str, Any]:
        # Use EXPLAIN PLAN FOR ...
        return self.analyze_query_performance(query)

    def validate_connection_string(self) -> bool:
        # Basic validation for Oracle DSN
        parsed = connection_manager.parse_connection_string(self.connection_string)
        return bool(parsed and parsed.get('hostname') and parsed.get('username') and parsed.get('password'))

    def create_database(self, database_name: str) -> dict:
        """
        Not implemented for Oracle. Creating a database is a DBA operation.
        Args:
            database_name (str): The name of the database to create.
        Returns:
            dict: Not implemented error.
        """
        logger.warning("Create database is not implemented for Oracle.")
        return {"status_code": 501, "error": "Create database is not implemented for Oracle."} 
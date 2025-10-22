"""
PostgreSQL database engine implementation.
"""

import psycopg2
import psycopg2.pool
import psycopg2.extras
import logging
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from urllib.parse import urlparse, urlunparse, ParseResult

from ..base.database_engine import DatabaseEngine
from ..base.connection_manager import connection_manager
from ..base.query_validator import QueryValidatorBase
from .postgresql_queries import (
    get_query_template,
    format_sample_data_query
)

logger = logging.getLogger(__name__)


class PostgreSQLQueryValidator(QueryValidatorBase):
    DANGEROUS_KEYWORDS = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
        'GRANT', 'REVOKE', 'EXECUTE', 'EXEC', 'MERGE', 'UPSERT', 'REPLACE',
        'VACUUM', 'ANALYZE', 'CLUSTER', 'DISCARD', 'REINDEX', 'RESET', 'SET'
    ]
    DANGEROUS_STARTS = [
        'INSERT INTO', 'UPDATE ', 'DELETE FROM', 'DROP ', 'CREATE ',
        'ALTER ', 'TRUNCATE ', 'GRANT ', 'REVOKE ', 'EXECUTE ',
        'EXEC ', 'MERGE ', 'UPSERT ', 'REPLACE ', 'VACUUM ', 'ANALYZE ',
        'CLUSTER ', 'DISCARD ', 'REINDEX ', 'RESET ', 'SET '
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
        r"COPY\s+.*\s+FROM\s+PROGRAM", # Dangerous COPY FROM PROGRAM
    ]

postgresql_query_validator = PostgreSQLQueryValidator()


class PostgreSQLEngine(DatabaseEngine):
    """PostgreSQL database engine implementation."""
    
    def __init__(self, connection_string: str, **kwargs):
        super().__init__(connection_string, **kwargs)
        self._connection_pool = None
        self._pool_size = int(kwargs.get('pool_size', 5))
        self._max_connections = int(kwargs.get('max_connections', 20))
    
    def connect(self) -> bool:
        try:
            parsed = connection_manager.parse_connection_string(self.connection_string)
            if not parsed:
                logger.error("Invalid PostgreSQL connection string")
                return False
            self._connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=self._max_connections,
                dsn=self.connection_string
            )
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(get_query_template("get_postgres_version"))
                    version = cursor.fetchone()
                    logger.info(f"Connected to PostgreSQL: {version[0]}")
            self._is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self._is_connected = False
            return False
    
    def disconnect(self) -> bool:
        try:
            if self._connection_pool:
                self._connection_pool.closeall()
                self._connection_pool = None
            self._is_connected = False
            logger.info("Disconnected from PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from PostgreSQL: {e}")
            return False
    
    def is_connected(self) -> bool:
        if not self._is_connected or not self._connection_pool:
            return False
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1;")
                    return True
        except Exception:
            self._is_connected = False
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        validation = postgresql_query_validator.validate_query(query, params)
        if not validation["is_valid"]:
            return {
                "success": False,
                "error": "Query validation failed",
                "validation_errors": validation["errors"],
                "validation_warnings": validation["warnings"]
            }
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        results = [dict(row) for row in rows]
                    else:
                        columns = []
                        results = []
                    row_count = cursor.rowcount
                    return {
                        "success": True,
                        "columns": columns,
                        "rows": results,
                        "row_count": row_count,
                        "query": query,
                        "params": params
                    }
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "params": params
            }
    
    def list_tables(self, database: str) -> List[Dict[str, Any]]:
        db_connection_string = self._get_db_connection_string(database)
        if not db_connection_string:
            return []
        temp_engine = PostgreSQLEngine(db_connection_string)
        if not temp_engine.connect():
            return []
        try:
            query = get_query_template("list_tables")
            result = temp_engine.execute_query(query)
            if result["success"]:
                return result["rows"]
            else:
                logger.error(f"Failed to list tables: {result['error']}")
                return []
        finally:
            temp_engine.disconnect()
    
    def describe_table(self, database: str, table: str) -> Dict[str, Any]:
        db_connection_string = self._get_db_connection_string(database)
        if not db_connection_string:
            return {"error": f"Cannot connect to database: {database}"}
        temp_engine = PostgreSQLEngine(db_connection_string)
        if not temp_engine.connect():
            return {"error": f"Failed to connect to database: {database}"}
        try:
            if '.' in table:
                schema, table_name = table.split('.', 1)
            else:
                schema = 'public'
                table_name = table
            columns_query = get_query_template("describe_table_columns")
            columns_result = temp_engine.execute_query(columns_query, (schema, table_name))
            constraints_query = get_query_template("describe_table_constraints")
            constraints_result = temp_engine.execute_query(constraints_query, (schema, table_name))
            indexes_query = get_query_template("describe_table_indexes")
            indexes_result = temp_engine.execute_query(indexes_query, (schema, table_name))
            stats_query = get_query_template("describe_table_statistics")
            stats_result = temp_engine.execute_query(stats_query, (schema, table_name))
            return {
                "table_name": table_name,
                "schema_name": schema,
                "full_name": f"{schema}.{table_name}",
                "columns": columns_result.get("rows", []) if columns_result["success"] else [],
                "constraints": constraints_result.get("rows", []) if constraints_result["success"] else [],
                "indexes": indexes_result.get("rows", []) if indexes_result["success"] else [],
                "statistics": stats_result.get("rows", []) if stats_result["success"] else [],
                "success": True
            }
        except Exception as e:
            logger.error(f"Error describing table {table}: {e}")
            return {"error": str(e)}
        finally:
            temp_engine.disconnect()
    
    def get_sample_data(self, database: str, table: str, limit: int = 10) -> Dict[str, Any]:
        db_connection_string = self._get_db_connection_string(database)
        if not db_connection_string:
            return {"error": f"Cannot connect to database: {database}"}
        temp_engine = PostgreSQLEngine(db_connection_string)
        if not temp_engine.connect():
            return {"error": f"Failed to connect to database: {database}"}
        try:
            if '.' in table:
                schema, table_name = table.split('.', 1)
                full_table_name = f"{schema}.{table_name}"
            else:
                schema = 'public'
                table_name = table
                full_table_name = f"public.{table_name}"
            query = format_sample_data_query(full_table_name, limit=limit)
            result = temp_engine.execute_query(query, (limit,))
            if result["success"]:
                return {
                    "table_name": table_name,
                    "schema_name": schema,
                    "full_name": full_table_name,
                    "sample_data": result["rows"],
                    "columns": result["columns"],
                    "row_count": len(result["rows"]),
                    "limit": limit,
                    "success": True
                }
            else:
                return {"error": result["error"]}
        except Exception as e:
            logger.error(f"Error getting sample data from {table}: {e}")
            return {"error": str(e)}
        finally:
            temp_engine.disconnect()
    
    def analyze_query_performance(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        validation = postgresql_query_validator.validate_query(query, params)
        if not validation["is_valid"]:
            return {
                "success": False,
                "error": "Query validation failed",
                "validation_errors": validation["errors"]
            }
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                    if params:
                        cursor.execute(explain_query, params)
                    else:
                        cursor.execute(explain_query)
                    plan_result = cursor.fetchone()
                    stats_query = get_query_template("query_performance_stats")
                    cursor.execute(stats_query, (f"%{query[:50]}%",))
                    stats_result = cursor.fetchone()
                    return {
                        "success": True,
                        "execution_plan": plan_result[0] if plan_result else None,
                        "query_statistics": {
                            "calls": stats_result[1] if stats_result else 0,
                            "total_time": stats_result[2] if stats_result else 0,
                            "mean_time": stats_result[3] if stats_result else 0,
                            "rows": stats_result[4] if stats_result else 0
                        } if stats_result else None,
                        "query": query,
                        "params": params
                    }
        except Exception as e:
            logger.error(f"Query performance analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "params": params
            }
    
    def _get_connection_from_pool(self):
        if not self._connection_pool:
            raise Exception("Connection pool not initialized")
        return self._connection_pool.getconn()
    
    def _return_connection_to_pool(self, connection):
        if self._connection_pool and connection:
            self._connection_pool.putconn(connection)
    
    def validate_connection_string(self) -> bool:
        return connection_manager.validate_connection_string(self.connection_string)
    
    def _get_db_connection_string(self, database: str) -> Optional[str]:
        """
        Return a new connection string with the database name replaced by the given one,
        using urlparse/urlunparse for robustness.
        """
        parsed = urlparse(self.connection_string)
        # If the path is already the correct database, return as is
        current_db = parsed.path.lstrip("/") if parsed.path else None
        if current_db == database:
            return self.connection_string
        # Build new path
        new_path = f"/{database}"
        new_parsed = ParseResult(
            scheme=parsed.scheme,
            netloc=parsed.netloc,
            path=new_path,
            params=parsed.params,
            query=parsed.query,
            fragment=parsed.fragment
        )
        return urlunparse(new_parsed)

    def list_schemas(self, database: str) -> list[dict[str, Any]]:
        db_connection_string = self._get_db_connection_string(database)
        if not db_connection_string:
            return []
        temp_engine = PostgreSQLEngine(db_connection_string)
        if not temp_engine.connect():
            return []
        try:
            query = get_query_template("get_schemas")
            result = temp_engine.execute_query(query)
            return result["rows"] if result["success"] else []
        finally:
            temp_engine.disconnect()

    def list_objects_in_schema(self, database: str, schema: str) -> dict[str, list[dict[str, Any]]]:
        db_connection_string = self._get_db_connection_string(database)
        if not db_connection_string:
            return {}
        temp_engine = PostgreSQLEngine(db_connection_string)
        if not temp_engine.connect():
            return {}
        try:
            # Tables
            tables_query = f"""
                SELECT tablename FROM pg_tables WHERE schemaname = %s;
            """
            tables = temp_engine.execute_query(tables_query, (schema,))
            # Views
            views_query = f"""
                SELECT table_name FROM information_schema.views WHERE table_schema = %s;
            """
            views = temp_engine.execute_query(views_query, (schema,))
            # Sequences
            seq_query = f"""
                SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = %s;
            """
            sequences = temp_engine.execute_query(seq_query, (schema,))
            # Extensions
            ext_query = f"""
                SELECT extname FROM pg_extension;
            """
            extensions = temp_engine.execute_query(ext_query)
            return {
                "tables": tables["rows"] if tables["success"] else [],
                "views": views["rows"] if views["success"] else [],
                "sequences": sequences["rows"] if sequences["success"] else [],
                "extensions": extensions["rows"] if extensions["success"] else [],
            }
        finally:
            temp_engine.disconnect()

    def describe_object(self, database: str, schema: str, object_name: str, object_type: str) -> dict:
        db_connection_string = self._get_db_connection_string(database)
        if not db_connection_string:
            return {"error": f"Cannot connect to database: {database}"}
        temp_engine = PostgreSQLEngine(db_connection_string)
        if not temp_engine.connect():
            return {"error": f"Failed to connect to database: {database}"}
        try:
            if object_type == "table":
                return temp_engine.describe_table(database, f"{schema}.{object_name}")
            elif object_type == "view":
                query = f"SELECT * FROM information_schema.views WHERE table_schema = %s AND table_name = %s;"
                result = temp_engine.execute_query(query, (schema, object_name))
                return result["rows"][0] if result["success"] and result["rows"] else {"error": "View not found"}
            elif object_type == "sequence":
                query = f"SELECT * FROM information_schema.sequences WHERE sequence_schema = %s AND sequence_name = %s;"
                result = temp_engine.execute_query(query, (schema, object_name))
                return result["rows"][0] if result["success"] and result["rows"] else {"error": "Sequence not found"}
            elif object_type == "extension":
                query = f"SELECT * FROM pg_extension WHERE extname = %s;"
                result = temp_engine.execute_query(query, (object_name,))
                return result["rows"][0] if result["success"] and result["rows"] else {"error": "Extension not found"}
            else:
                return {"error": f"Unsupported object type: {object_type}"}
        finally:
            temp_engine.disconnect()

    def get_top_queries(self, database: str, sort_by: str = "mean_time", limit: int = 10) -> list[dict[str, Any]]:
        db_connection_string = self._get_db_connection_string(database)
        if not db_connection_string:
            return []
        temp_engine = PostgreSQLEngine(db_connection_string)
        if not temp_engine.connect():
            return []
        try:
            if sort_by == "total_time":
                query = f"""
                    SELECT query, calls, total_time, mean_time, rows FROM pg_stat_statements ORDER BY total_time DESC LIMIT %s;
                """
            else:
                query = f"""
                    SELECT query, calls, total_time, mean_time, rows FROM pg_stat_statements ORDER BY mean_time DESC LIMIT %s;
                """
            result = temp_engine.execute_query(query, (limit,))
            return result["rows"] if result["success"] else []
        finally:
            temp_engine.disconnect()

    def analyze_db_health(self, database: str, check_type: str = "all") -> dict:
        db_connection_string = self._get_db_connection_string(database)
        if not db_connection_string:
            return {"error": f"Cannot connect to database: {database}"}
        temp_engine = PostgreSQLEngine(db_connection_string)
        if not temp_engine.connect():
            return {"error": f"Failed to connect to database: {database}"}
        try:
            results = {}
            checks = [check_type] if check_type != "all" else [
                "index", "connection", "vacuum", "sequence", "replication", "buffer", "constraint"
            ]
            for check in checks:
                if check == "index":
                    # Bloated indexes (simple version)
                    query = '''
                        SELECT schemaname, relname AS table_name, indexrelname AS index_name, idx_scan, pg_size_pretty(pg_relation_size(pg_stat_user_indexes.indexrelid)) AS index_size
                        FROM pg_stat_user_indexes
                        JOIN pg_index ON pg_stat_user_indexes.indexrelid = pg_index.indexrelid
                        WHERE idx_scan = 0 OR pg_relation_size(pg_stat_user_indexes.indexrelid) > 100000000
                        ORDER BY pg_relation_size(pg_stat_user_indexes.indexrelid) DESC;
                    '''
                    result = temp_engine.execute_query(query)
                    results["index"] = result["rows"] if result["success"] else result.get("error")
                elif check == "connection":
                    query = get_query_template("active_connections")
                    result = temp_engine.execute_query(query)
                    results["connection"] = result["rows"] if result["success"] else result.get("error")
                elif check == "vacuum":
                    query = '''
                        SELECT relname, n_dead_tup, last_vacuum, last_autovacuum, vacuum_count, autovacuum_count
                        FROM pg_stat_user_tables
                        WHERE n_dead_tup > 1000
                        ORDER BY n_dead_tup DESC;
                    '''
                    result = temp_engine.execute_query(query)
                    results["vacuum"] = result["rows"] if result["success"] else result.get("error")
                elif check == "sequence":
                    query = '''
                        SELECT sequence_schema, sequence_name, last_value, increment_by, max_value
                        FROM information_schema.sequences
                        JOIN pg_sequences ON sequence_name = pg_sequences.schemaname || '.' || pg_sequences.sequencename
                        LIMIT 50;
                    '''
                    result = temp_engine.execute_query(query)
                    results["sequence"] = result["rows"] if result["success"] else result.get("error")
                elif check == "replication":
                    query = '''
                        SELECT * FROM pg_stat_replication;
                    '''
                    result = temp_engine.execute_query(query)
                    results["replication"] = result["rows"] if result["success"] else result.get("error")
                elif check == "buffer":
                    query = '''
                        SELECT datname, blks_hit, blks_read, round((100 * blks_hit::float / NULLIF(blks_hit + blks_read, 0))::numeric, 2) AS hit_ratio
                        FROM pg_stat_database
                        WHERE blks_hit + blks_read > 0
                        ORDER BY hit_ratio ASC;
                    '''
                    result = temp_engine.execute_query(query)
                    results["buffer"] = result["rows"] if result["success"] else result.get("error")
                elif check == "constraint":
                    query = '''
                        SELECT conname, contype, conrelid::regclass AS table, convalidated
                        FROM pg_constraint
                        WHERE NOT convalidated;
                    '''
                    result = temp_engine.execute_query(query)
                    results["constraint"] = result["rows"] if result["success"] else result.get("error")
                else:
                    results[check] = f"Unknown check type: {check}"
            return results
        finally:
            temp_engine.disconnect() 

    def explain_query(self, database: str, query: str, analyze: bool = False) -> dict:
        db_connection_string = self._get_db_connection_string(database)
        if not db_connection_string:
            return {"error": f"Cannot connect to database: {database}"}
        temp_engine = PostgreSQLEngine(db_connection_string)
        if not temp_engine.connect():
            return {"error": f"Failed to connect to database: {database}"}
        try:
            explain_prefix = "EXPLAIN (FORMAT JSON)" if not analyze else "EXPLAIN (ANALYZE, FORMAT JSON)"
            explain_sql = f"{explain_prefix} {query}"
            result = temp_engine.execute_query(explain_sql)
            if result["success"] and result["rows"]:
                # The plan is returned as a JSON string in the first column of the first row
                plan_json = result["rows"][0][list(result["rows"][0].keys())[0]]
                return {"plan": plan_json}
            else:
                return {"error": result.get("error", "No plan returned")}
        except Exception as e:
            return {"error": str(e)}
        finally:
            temp_engine.disconnect() 

    def create_database(self, database_name: str) -> dict:
        """
        Create a new PostgreSQL database with the current user as owner.
        Requires CREATEDB privilege.
        Args:
            database_name (str): The name of the database to create.
        Returns:
            dict: Result of the operation or error message.
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT current_user;")
                    owner = cursor.fetchone()[0]
                    cursor.execute(f'CREATE DATABASE "{database_name}" OWNER "{owner}";')
            return {"status_code": 201, "result": f"Database '{database_name}' created with owner '{owner}'."}
        except Exception as e:
            logger.exception("Failed to create database in PostgreSQL.")
            return {"status_code": 500, "error": str(e)} 
"""
Oracle-specific query templates for common database operations.
"""

# List all schemas
LIST_SCHEMAS_QUERY = """
    SELECT username AS schema_name
    FROM all_users
    ORDER BY username
"""

# List all tables in a schema
LIST_TABLES_QUERY = """
    SELECT owner AS schema_name, table_name, tablespace_name, status
    FROM all_tables
    WHERE owner = :schema
    ORDER BY table_name
"""

# Describe table columns
DESCRIBE_TABLE_COLUMNS_QUERY = """
    SELECT column_name, data_type, data_length, data_precision, data_scale, nullable, data_default
    FROM all_tab_columns
    WHERE owner = :schema AND table_name = :table
    ORDER BY column_id
"""

# Describe table constraints
DESCRIBE_TABLE_CONSTRAINTS_QUERY = """
    SELECT constraint_name, constraint_type, search_condition, r_owner, r_constraint_name, status
    FROM all_constraints
    WHERE owner = :schema AND table_name = :table
"""

# Describe table indexes
DESCRIBE_TABLE_INDEXES_QUERY = """
    SELECT index_name, uniqueness, status, tablespace_name
    FROM all_indexes
    WHERE table_owner = :schema AND table_name = :table
"""

# Get sample data from a table
SAMPLE_DATA_QUERY = "SELECT * FROM {schema}.{table} FETCH FIRST :limit ROWS ONLY"

# Get Oracle version and edition
GET_ORACLE_VERSION_QUERY = "SELECT BANNER FROM v$version WHERE BANNER LIKE 'Oracle%'"

# Add more queries as needed for health, performance, etc.

def get_query_template(template_name: str) -> str:
    return globals().get(template_name, "")

def format_sample_data_query(schema: str, table: str, limit: int = 10) -> str:
    return f"SELECT * FROM {schema}.{table} FETCH FIRST {limit} ROWS ONLY" 
"""
PostgreSQL-specific query templates for common database operations.
"""

# Database listing queries
LIST_DATABASES_QUERY = """
    SELECT 
        datname as database_name,
        pg_size_pretty(pg_database_size(datname)) as size,
        pg_get_userbyid(datdba) as owner,
        datcollate as collation,
        datctype as ctype,
        pg_database_size(datname) as size_bytes
    FROM pg_database 
    WHERE datistemplate = false
    ORDER BY datname;
"""

# Table listing queries
LIST_TABLES_QUERY = """
    SELECT 
        schemaname as schema_name,
        tablename as table_name,
        tableowner as owner,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
        pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
        (SELECT count(*) FROM information_schema.columns 
         WHERE table_schema = schemaname AND table_name = tablename) as column_count
    FROM pg_tables 
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
    ORDER BY schemaname, tablename;
"""

# Table description queries
DESCRIBE_TABLE_COLUMNS_QUERY = """
    SELECT 
        column_name,
        data_type,
        is_nullable,
        column_default,
        character_maximum_length,
        numeric_precision,
        numeric_scale,
        ordinal_position,
        udt_name as postgres_type
    FROM information_schema.columns 
    WHERE table_schema = %s AND table_name = %s
    ORDER BY ordinal_position;
"""

DESCRIBE_TABLE_CONSTRAINTS_QUERY = """
    SELECT 
        tc.constraint_name,
        tc.constraint_type,
        kcu.column_name,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name,
        rc.update_rule,
        rc.delete_rule
    FROM information_schema.table_constraints tc
    LEFT JOIN information_schema.key_column_usage kcu 
        ON tc.constraint_name = kcu.constraint_name
    LEFT JOIN information_schema.constraint_column_usage ccu 
        ON ccu.constraint_name = tc.constraint_name
    LEFT JOIN information_schema.referential_constraints rc
        ON tc.constraint_name = rc.constraint_name
    WHERE tc.table_schema = %s AND tc.table_name = %s;
"""

DESCRIBE_TABLE_INDEXES_QUERY = """
    SELECT 
        indexname as index_name,
        indexdef as index_definition,
        schemaname as schema_name,
        tablename as table_name
    FROM pg_indexes 
    WHERE schemaname = %s AND tablename = %s;
"""

DESCRIBE_TABLE_STATISTICS_QUERY = """
    SELECT 
        n_tup_ins as inserts,
        n_tup_upd as updates,
        n_tup_del as deletes,
        n_live_tup as live_tuples,
        n_dead_tup as dead_tuples,
        last_vacuum,
        last_autovacuum,
        last_analyze,
        last_autoanalyze,
        vacuum_count,
        autovacuum_count,
        analyze_count,
        autoanalyze_count
    FROM pg_stat_user_tables 
    WHERE schemaname = %s AND relname = %s;
"""

# Performance analysis queries
QUERY_PERFORMANCE_STATS_QUERY = """
    SELECT 
        query,
        calls,
        total_time,
        mean_time,
        stddev_time,
        min_time,
        max_time,
        rows,
        shared_blks_hit,
        shared_blks_read,
        shared_blks_written,
        shared_blks_dirtied,
        temp_blks_read,
        temp_blks_written,
        blk_read_time,
        blk_write_time
    FROM pg_stat_statements 
    WHERE query LIKE %s
    ORDER BY total_time DESC
    LIMIT 10;
"""

SLOW_QUERIES_QUERY = """
    SELECT 
        query,
        calls,
        total_time,
        mean_time,
        rows
    FROM pg_stat_statements 
    WHERE mean_time > 1000  -- Queries taking more than 1 second on average
    ORDER BY mean_time DESC
    LIMIT 20;
"""

TABLE_SIZE_QUERY = """
    SELECT 
        schemaname as schema_name,
        tablename as table_name,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
        pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size,
        pg_total_relation_size(schemaname||'.'||tablename) as total_size_bytes,
        pg_relation_size(schemaname||'.'||tablename) as table_size_bytes
    FROM pg_tables 
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"""

INDEX_USAGE_STATS_QUERY = """
    SELECT 
        schemaname as schema_name,
        tablename as table_name,
        indexname as index_name,
        idx_scan as index_scans,
        idx_tup_read as tuples_read,
        idx_tup_fetch as tuples_fetched
    FROM pg_stat_user_indexes 
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
    ORDER BY idx_scan DESC;
"""

# Connection and session queries
ACTIVE_CONNECTIONS_QUERY = """
    SELECT 
        pid,
        usename as username,
        application_name,
        client_addr,
        client_hostname,
        state,
        query_start,
        state_change,
        wait_event_type,
        wait_event,
        query
    FROM pg_stat_activity 
    WHERE state IS NOT NULL
    ORDER BY query_start DESC;
"""

DATABASE_STATS_QUERY = """
    SELECT 
        datname as database_name,
        numbackends as active_connections,
        xact_commit as commits,
        xact_rollback as rollbacks,
        blks_read as blocks_read,
        blks_hit as blocks_hit,
        tup_returned as tuples_returned,
        tup_fetched as tuples_fetched,
        tup_inserted as tuples_inserted,
        tup_updated as tuples_updated,
        tup_deleted as tuples_deleted,
        conflicts,
        temp_files,
        temp_bytes,
        deadlocks,
        blk_read_time,
        blk_write_time
    FROM pg_stat_database 
    WHERE datname = current_database();
"""

# Sample data queries
SAMPLE_DATA_QUERY = """
    SELECT * FROM {table_name} LIMIT %s;
"""

SAMPLE_DATA_WITH_ORDER_QUERY = """
    SELECT * FROM {table_name} 
    ORDER BY {order_column} 
    LIMIT %s;
"""

# Utility queries
GET_CURRENT_DATABASE_QUERY = "SELECT current_database();"

GET_CURRENT_USER_QUERY = "SELECT current_user;"

GET_POSTGRES_VERSION_QUERY = "SELECT version();"

GET_SCHEMAS_QUERY = """
    SELECT 
        schema_name,
        schema_owner
    FROM information_schema.schemata 
    WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
    ORDER BY schema_name;
"""

# Query templates for different operations
QUERY_TEMPLATES = {
    "list_databases": LIST_DATABASES_QUERY,
    "list_tables": LIST_TABLES_QUERY,
    "describe_table_columns": DESCRIBE_TABLE_COLUMNS_QUERY,
    "describe_table_constraints": DESCRIBE_TABLE_CONSTRAINTS_QUERY,
    "describe_table_indexes": DESCRIBE_TABLE_INDEXES_QUERY,
    "describe_table_statistics": DESCRIBE_TABLE_STATISTICS_QUERY,
    "query_performance_stats": QUERY_PERFORMANCE_STATS_QUERY,
    "slow_queries": SLOW_QUERIES_QUERY,
    "table_size": TABLE_SIZE_QUERY,
    "index_usage_stats": INDEX_USAGE_STATS_QUERY,
    "active_connections": ACTIVE_CONNECTIONS_QUERY,
    "database_stats": DATABASE_STATS_QUERY,
    "get_current_database": GET_CURRENT_DATABASE_QUERY,
    "get_current_user": GET_CURRENT_USER_QUERY,
    "get_postgres_version": GET_POSTGRES_VERSION_QUERY,
    "get_schemas": GET_SCHEMAS_QUERY
}


def get_query_template(template_name: str) -> str:
    """
    Get a query template by name.
    
    Args:
        template_name: Name of the template
        
    Returns:
        Query template string
    """
    return QUERY_TEMPLATES.get(template_name, "")


def format_sample_data_query(table_name: str, order_column: str = None, limit: int = 10) -> str:
    """
    Format a sample data query.
    
    Args:
        table_name: Full table name (schema.table)
        order_column: Column to order by (optional)
        limit: Number of rows to return
        
    Returns:
        Formatted query string
    """
    if order_column:
        return SAMPLE_DATA_WITH_ORDER_QUERY.format(
            table_name=table_name,
            order_column=order_column
        )
    else:
        return SAMPLE_DATA_QUERY.format(table_name=table_name) 
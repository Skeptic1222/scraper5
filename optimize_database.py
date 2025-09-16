"""
Database Optimization Script for SQL Server Express
Creates indexes and optimizes queries for better performance
"""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment"""
    return os.environ.get('DATABASE_URL',
        'mssql+pyodbc://sa:YourStrong!Password@localhost\\SQLEXPRESS/scraperdb?driver=ODBC+Driver+17+for+SQL+Server')

def create_indexes():
    """Create performance indexes for SQL Server Express"""

    engine = create_engine(get_database_url())

    # Index definitions for each table
    indexes = [
        # Users table indexes
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC)",

        # Assets table indexes
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_assets_user_id ON assets(user_id)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_assets_created_at ON assets(created_at DESC)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_assets_source_url ON assets(source_url)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_assets_file_type ON assets(file_type)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_assets_user_created ON assets(user_id, created_at DESC)",

        # ScrapeJobs table indexes
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_scrapejobs_user_id ON scrape_jobs(user_id)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_scrapejobs_status ON scrape_jobs(status)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_scrapejobs_created_at ON scrape_jobs(created_at DESC)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_scrapejobs_user_status ON scrape_jobs(user_id, status)",

        # MediaBlobs table indexes (if storing in database)
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_mediablobs_asset_id ON media_blobs(asset_id)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_mediablobs_blob_type ON media_blobs(blob_type)",

        # Composite indexes for common queries
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_assets_composite ON assets(user_id, file_type, created_at DESC)",
        "CREATE NONCLUSTERED INDEX IF NOT EXISTS idx_jobs_composite ON scrape_jobs(user_id, status, created_at DESC)"
    ]

    # SQL Server specific syntax (without IF NOT EXISTS)
    sql_server_indexes = [
        # Users table
        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_email' AND object_id = OBJECT_ID('users'))
           CREATE NONCLUSTERED INDEX idx_users_email ON users(email)""",

        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_google_id' AND object_id = OBJECT_ID('users'))
           CREATE NONCLUSTERED INDEX idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL""",

        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_created_at' AND object_id = OBJECT_ID('users'))
           CREATE NONCLUSTERED INDEX idx_users_created_at ON users(created_at DESC)""",

        # Assets table
        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_assets_user_id' AND object_id = OBJECT_ID('assets'))
           CREATE NONCLUSTERED INDEX idx_assets_user_id ON assets(user_id)""",

        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_assets_created_at' AND object_id = OBJECT_ID('assets'))
           CREATE NONCLUSTERED INDEX idx_assets_created_at ON assets(created_at DESC)""",

        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_assets_source_url' AND object_id = OBJECT_ID('assets'))
           CREATE NONCLUSTERED INDEX idx_assets_source_url ON assets(source_url)""",

        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_assets_file_type' AND object_id = OBJECT_ID('assets'))
           CREATE NONCLUSTERED INDEX idx_assets_file_type ON assets(file_type)""",

        # ScrapeJobs table
        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_scrapejobs_user_id' AND object_id = OBJECT_ID('scrape_jobs'))
           CREATE NONCLUSTERED INDEX idx_scrapejobs_user_id ON scrape_jobs(user_id)""",

        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_scrapejobs_status' AND object_id = OBJECT_ID('scrape_jobs'))
           CREATE NONCLUSTERED INDEX idx_scrapejobs_status ON scrape_jobs(status)""",

        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_scrapejobs_created_at' AND object_id = OBJECT_ID('scrape_jobs'))
           CREATE NONCLUSTERED INDEX idx_scrapejobs_created_at ON scrape_jobs(created_at DESC)""",

        # Composite indexes
        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_assets_composite' AND object_id = OBJECT_ID('assets'))
           CREATE NONCLUSTERED INDEX idx_assets_composite ON assets(user_id, file_type, created_at DESC)""",

        """IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_jobs_composite' AND object_id = OBJECT_ID('scrape_jobs'))
           CREATE NONCLUSTERED INDEX idx_jobs_composite ON scrape_jobs(user_id, status, created_at DESC)"""
    ]

    with engine.connect() as conn:
        for index_sql in sql_server_indexes:
            try:
                conn.execute(text(index_sql))
                conn.commit()
                logger.info(f"Index created/verified: {index_sql[:50]}...")
            except Exception as e:
                logger.warning(f"Index creation failed (may already exist): {str(e)[:100]}")

def update_statistics():
    """Update SQL Server statistics for query optimization"""

    engine = create_engine(get_database_url())

    statistics_commands = [
        "UPDATE STATISTICS users WITH FULLSCAN",
        "UPDATE STATISTICS assets WITH FULLSCAN",
        "UPDATE STATISTICS scrape_jobs WITH FULLSCAN",
        "UPDATE STATISTICS roles WITH FULLSCAN",
        "UPDATE STATISTICS user_roles WITH FULLSCAN",
        "UPDATE STATISTICS app_settings WITH FULLSCAN"
    ]

    with engine.connect() as conn:
        for cmd in statistics_commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
                logger.info(f"Statistics updated: {cmd}")
            except Exception as e:
                logger.warning(f"Statistics update failed: {str(e)}")

def analyze_query_performance():
    """Analyze slow queries and provide recommendations"""

    engine = create_engine(get_database_url())

    # Query to find slow queries (SQL Server specific)
    slow_queries_sql = """
    SELECT TOP 10
        qs.total_elapsed_time / qs.execution_count AS avg_elapsed_time,
        qs.total_worker_time / qs.execution_count AS avg_worker_time,
        qs.execution_count,
        SUBSTRING(st.text, (qs.statement_start_offset/2) + 1,
            ((CASE qs.statement_end_offset
                WHEN -1 THEN DATALENGTH(st.text)
                ELSE qs.statement_end_offset
            END - qs.statement_start_offset)/2) + 1) AS query_text
    FROM sys.dm_exec_query_stats AS qs
    CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) AS st
    WHERE st.text NOT LIKE '%sys.%'
    ORDER BY avg_elapsed_time DESC
    """

    try:
        with engine.connect() as conn:
            result = conn.execute(text(slow_queries_sql))
            slow_queries = result.fetchall()

            if slow_queries:
                logger.info("Top 10 slowest queries:")
                for i, query in enumerate(slow_queries, 1):
                    logger.info(f"{i}. Avg time: {query[0]}ms, Executions: {query[2]}")
                    logger.info(f"   Query: {query[3][:100]}...")
            else:
                logger.info("No slow queries found")

    except Exception as e:
        logger.error(f"Failed to analyze query performance: {str(e)}")

def optimize_connection_pool():
    """Generate optimized connection pool settings"""

    pool_config = """
# Optimized SQL Server connection pool settings for app.py

SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,           # Number of persistent connections
    'max_overflow': 20,        # Maximum overflow connections
    'pool_timeout': 30,        # Timeout for getting connection from pool
    'pool_recycle': 3600,      # Recycle connections after 1 hour
    'pool_pre_ping': True,     # Test connections before using
    'echo_pool': False,        # Set to True for debugging
    'connect_args': {
        'timeout': 30,         # Connection timeout in seconds
        'autocommit': False,   # Use transactions
        'ansi': True,          # Use ANSI SQL
        'fast_executemany': True  # Batch operations optimization
    }
}

# Add to app.py configuration:
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = SQLALCHEMY_ENGINE_OPTIONS
"""

    logger.info("Connection pool configuration:")
    print(pool_config)

    return pool_config

def main():
    """Run all database optimizations"""

    logger.info("Starting database optimization for SQL Server Express...")

    try:
        # Create indexes
        logger.info("Creating performance indexes...")
        create_indexes()

        # Update statistics
        logger.info("Updating table statistics...")
        update_statistics()

        # Analyze performance
        logger.info("Analyzing query performance...")
        analyze_query_performance()

        # Show connection pool config
        logger.info("Generating connection pool configuration...")
        optimize_connection_pool()

        logger.info("Database optimization completed successfully!")

    except Exception as e:
        logger.error(f"Database optimization failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

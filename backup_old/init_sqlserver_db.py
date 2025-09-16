import os
from app import app
from models import db, init_db, User, Role, UserRole, ScrapeJob, Asset, AppSetting, OAuth, MediaBlob
from sqlalchemy import text

print("🔄 Initializing SQL Server database...")
print(f"📍 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"📁 Current directory: {os.getcwd()}")

with app.app_context():
    try:
        print("🔍 Checking SQL Server connection...")
        # Test database connection
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION as version, DB_NAME() as database_name"))
            row = result.fetchone()
            sql_version = row[0][:50]
            database_name = row[1]
            print(f"✅ Connected to: {sql_version}...")
            print(f"🗄️  Database: {database_name}")
        
        # Check if tables exist and drop them if they do (for clean restart)
        print("🔍 Checking existing tables...")
        with db.engine.connect() as conn:
            # Check for existing tables
            result = conn.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                AND TABLE_NAME IN ('users', 'roles', 'user_roles', 'scrape_jobs', 'assets', 'app_settings', 'oauth', 'media_blobs')
            """))
            existing_tables = [row[0] for row in result.fetchall()]
            
            if existing_tables:
                print(f"🗑️ Found existing tables: {', '.join(existing_tables)}")
                print("🧹 Dropping existing tables for clean initialization...")
                
                # Disable foreign key constraints for drops
                conn.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'"))
                
                # Drop tables in any order now that constraints are disabled
                for table in existing_tables:
                    try:
                        conn.execute(text(f"DROP TABLE {table}"))
                        print(f"   🗑️ Dropped table: {table}")
                    except Exception as e:
                        print(f"   ⚠️ Could not drop table {table}: {e}")
                
                # Re-enable foreign key constraints
                conn.execute(text("EXEC sp_msforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'"))
                conn.commit()
        
        # Create all tables including new MediaBlob
        print("🏗️ Creating all tables...")
        db.create_all()
        print("✅ Created all tables")
        
        # Verify tables were created
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT TABLE_NAME, 
                       (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = T.TABLE_NAME) as COLUMN_COUNT
                FROM INFORMATION_SCHEMA.TABLES T
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            tables = result.fetchall()
            print("📋 Created tables:")
            for table_name, col_count in tables:
                print(f"   📄 {table_name} ({col_count} columns)")
        
        # Initialize with default data
        print("🔧 Initializing default data...")
        init_db()
        print("✅ Initialized default data")
        
        # Verify the initialization
        print("🔍 Verifying initialization...")
        
        roles = Role.query.all()
        print(f"👥 Roles created: {[role.name for role in roles]}")
        
        # Get database size
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    SUM(size) * 8.0 / 1024 AS size_mb
                FROM sys.master_files 
                WHERE database_id = DB_ID()
            """))
            db_size = result.scalar() or 0
        
        print(f"\n🎉 SQL Server database initialization complete!")
        print(f"📊 Database: {database_name}")
        print(f"🗄️ Server: localhost\\SQLEXPRESS")
        print(f"📈 Total Size: {db_size:.2f} MB")
        print(f"🏗️ SQL Server Version: {sql_version}")
        print(f"📱 Tables: {len(tables)} created successfully")
        print(f"🔐 Ready for OAuth authentication!")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        import traceback
        traceback.print_exc() 
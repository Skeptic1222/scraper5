
#!/usr/bin/env python3
"""
PostgreSQL database initialization script for Replit
"""
import os
from app import app
from models import db, init_db, User, Role, UserRole, ScrapeJob, Asset, AppSetting, OAuth, MediaBlob
from sqlalchemy import text

print("🔄 Initializing PostgreSQL database...")
print(f"📍 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"📁 Current directory: {os.getcwd()}")

with app.app_context():
    try:
        print("🔍 Checking PostgreSQL connection...")
        # Test database connection
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            pg_version = result.fetchone()[0]
            print(f"✅ Connected to: {pg_version[:50]}...")
            
            # Get database name
            result = conn.execute(text("SELECT current_database()"))
            database_name = result.fetchone()[0]
            print(f"🗄️  Database: {database_name}")
        
        # Check if tables exist and drop them if they do (for clean restart)
        print("🔍 Checking existing tables...")
        with db.engine.connect() as conn:
            # Check for existing tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                AND table_name IN ('users', 'roles', 'user_roles', 'scrape_jobs', 'assets', 'app_settings', 'oauth', 'media_blobs')
            """))
            existing_tables = [row[0] for row in result.fetchall()]
            
            if existing_tables:
                print(f"🗑️ Found existing tables: {', '.join(existing_tables)}")
                print("🧹 Dropping existing tables for clean initialization...")
                
                # Drop tables in reverse dependency order
                drop_order = ['media_blobs', 'assets', 'user_roles', 'scrape_jobs', 'oauth', 'users', 'roles', 'app_settings']
                for table in drop_order:
                    if table in existing_tables:
                        try:
                            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                            print(f"   🗑️ Dropped table: {table}")
                        except Exception as e:
                            print(f"   ⚠️ Could not drop table {table}: {e}")
                
                conn.commit()
        
        # Create all tables
        print("🏗️ Creating all tables...")
        db.create_all()
        print("✅ Created all tables")
        
        # Verify tables were created
        with db.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name,
                       (SELECT count(*) FROM information_schema.columns WHERE table_name = t.table_name AND table_schema = 'public') as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
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
                SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
            """))
            db_size = result.scalar() or "Unknown"
        
        print(f"\n🎉 PostgreSQL database initialization complete!")
        print(f"📊 Database: {database_name}")
        print(f"🗄️ Server: PostgreSQL on Replit")
        print(f"📈 Total Size: {db_size}")
        print(f"🏗️ PostgreSQL Version: {pg_version[:50]}...")
        print(f"📱 Tables: {len(tables)} created successfully")
        print(f"🔐 Ready for OAuth authentication!")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        import traceback
        traceback.print_exc()

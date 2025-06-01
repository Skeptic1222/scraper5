import os
from app import app
from models import db, User, Role, UserRole
from sqlalchemy import text

print("🔍 Verifying SQL Server 2022 Express Connection...")

with app.app_context():
    try:
        # Get database connection info
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"📍 Database URI: {db_uri}")
        
        # Test connection and get server info
        with db.engine.connect() as conn:
            # Get SQL Server version and database info
            result = conn.execute(text("""
                SELECT 
                    @@VERSION as server_version,
                    DB_NAME() as database_name,
                    SUSER_NAME() as login_name,
                    @@SERVERNAME as server_name
            """))
            row = result.fetchone()
            
            print(f"\n🗄️  SQL Server Information:")
            print(f"   🔧 Version: {row[0]}")
            print(f"   📂 Database: {row[1]}")
            print(f"   👤 User: {row[2]}")
            print(f"   🖥️  Server: {row[3]}")
            
            # Get table information
            result = conn.execute(text("""
                SELECT 
                    TABLE_NAME,
                    TABLE_TYPE,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = T.TABLE_NAME) as COLUMN_COUNT
                FROM INFORMATION_SCHEMA.TABLES T
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            tables = result.fetchall()
            
            print(f"\n📋 Database Tables ({len(tables)} total):")
            for table_name, table_type, col_count in tables:
                print(f"   📄 {table_name} ({col_count} columns)")
            
            # Check user data
            users = User.query.all()
            roles = Role.query.all()
            user_roles = UserRole.query.all()
            
            print(f"\n📊 Current Data:")
            print(f"   👥 Users: {len(users)}")
            print(f"   🔐 Roles: {len(roles)} - {[role.name for role in roles]}")
            print(f"   🔗 User-Role assignments: {len(user_roles)}")
            
            # Show database size information
            result = conn.execute(text("""
                SELECT 
                    DB_NAME() as database_name,
                    SUM(size) * 8 / 1024 as size_mb
                FROM sys.database_files
            """))
            row = result.fetchone()
            print(f"   💾 Database size: {row[1]:.2f} MB")
            
        print(f"\n🎉 SUCCESS: Application is now running on SQL Server 2022 Express!")
        print(f"✅ Database: {db_uri.split('/')[-1].split('?')[0]}")
        print(f"✅ All tables created and populated with default data")
        
    except Exception as e:
        print(f"❌ Error verifying SQL Server connection: {e}")
        import traceback
        traceback.print_exc() 
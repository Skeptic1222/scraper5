
#!/usr/bin/env python3
"""
PostgreSQL database status checker for Replit
"""
import os
from sqlalchemy import create_engine, text
import sys

def check_postgresql_database():
    """Check PostgreSQL database status and tables"""
    
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            print("💡 Make sure you've created a PostgreSQL database in Replit")
            return False
        
        # PostgreSQL connection
        engine = create_engine(database_url, echo=False)
        
        print("🗄️  Checking PostgreSQL database...")
        print(f"🔗 Connection: {database_url}")
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ Database connection successful")
            
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"🐘 PostgreSQL Version: {version[:50]}...")
            
            # Get database name
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"📊 Database Name: {db_name}")
            
        # Check if tables exist
        with engine.connect() as conn:
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            tables = conn.execute(tables_query).fetchall()
            
            if tables:
                print(f"📋 Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table[0]}")
                    
                    # Count records in each table
                    try:
                        count_query = text(f'SELECT COUNT(*) FROM "{table[0]}"')
                        count = conn.execute(count_query).scalar()
                        print(f"     ({count} records)")
                    except Exception as e:
                        print(f"     (Error counting: {e})")
            else:
                print("📋 No tables found - database needs initialization")
                print("💡 Run: python init_postgresql_db.py")
        
        print("✅ Database check complete")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"🔗 Attempted connection to: {os.environ.get('DATABASE_URL', 'Not set')}")
        print("💡 Make sure PostgreSQL database is created in Replit")
        return False

if __name__ == "__main__":
    success = check_postgresql_database()
    if not success:
        print("\n🚨 Database check failed!")
        print("Please ensure:")
        print("1. PostgreSQL database is created in Replit")
        print("2. DATABASE_URL environment variable is set")
        print("3. Database connection is working")
        sys.exit(1)
    else:
        print("\n🎉 Database check passed!")

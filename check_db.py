#!/usr/bin/env python3
"""
Database status checker for SQL Server Express
"""
import pyodbc
from sqlalchemy import create_engine, text
import sys

def check_sql_server_database():
    """Check SQL Server Express database status and tables"""
    
    try:
        # SQL Server Express connection with pool settings
        engine = create_engine(
            'mssql+pyodbc://localhost\\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes',
            echo=False,
            poolclass=None,  # Disable connection pooling
            pool_pre_ping=True
        )
        
        print("🗄️  Checking SQL Server Express database...")
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            print("✅ Database connection successful")
            
        # Check if tables exist in separate connection
        with engine.connect() as conn:
            tables_query = text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            
            tables = conn.execute(tables_query).fetchall()
            
            if tables:
                print(f"📋 Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table[0]}")
                    
                    # Count records in each table
                    try:
                        count_query = text(f"SELECT COUNT(*) FROM [{table[0]}]")
                        count = conn.execute(count_query).scalar()
                        print(f"     ({count} records)")
                    except Exception as e:
                        print(f"     (Error counting: {e})")
            else:
                print("⚠️  No tables found. Database may need initialization.")
                
        # Check users table in separate connection
        with engine.connect() as conn:
            users_check = text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'users'
            """)
            
            users_exists = conn.execute(users_check).scalar()
            
            if users_exists:
                user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
                print(f"👤 Users table: {user_count} users")
                
                if user_count > 0:
                    users_query = text("SELECT TOP 5 email, name, is_active, created_at FROM users")
                    users = conn.execute(users_query).fetchall()
                    for user in users:
                        print(f"   - {user[1]} ({user[0]}) - Active: {user[2]}")
            else:
                print("⚠️  Users table not found")
                
        # Check roles table in separate connection
        with engine.connect() as conn:
            roles_check = text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'roles'
            """)
            
            roles_exists = conn.execute(roles_check).scalar()
            
            if roles_exists:
                role_count = conn.execute(text("SELECT COUNT(*) FROM roles")).scalar()
                print(f"🎭 Roles table: {role_count} roles")
                
                if role_count > 0:
                    roles_query = text("SELECT name, description FROM roles")
                    roles = conn.execute(roles_query).fetchall()
                    for role in roles:
                        print(f"   - {role[0]}: {role[1]}")
            else:
                print("⚠️  Roles table not found")
                
        print("✅ Database check complete")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("💡 Make sure SQL Server Express is running and Scraped database exists")
        sys.exit(1)

if __name__ == "__main__":
    check_sql_server_database() 
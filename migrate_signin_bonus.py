"""
Migration script to add signin_bonus_claimed field to users table
"""

import os
import sys
import pyodbc
from datetime import datetime

def migrate_signin_bonus():
    """Add signin_bonus_claimed column to users table"""
    
    # Connection parameters for SQL Server Express
    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'
        'DATABASE=Scraped;'
        'Trusted_Connection=yes;'
    )
    
    try:
        # Connect to database
        print("🔌 Connecting to SQL Server Express...")
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'signin_bonus_claimed'
        """)
        
        if cursor.fetchone()[0] > 0:
            print("✅ Column 'signin_bonus_claimed' already exists in users table")
            return
        
        # Add the new column
        print("📝 Adding signin_bonus_claimed column to users table...")
        cursor.execute("""
            ALTER TABLE users 
            ADD signin_bonus_claimed BIT DEFAULT 0
        """)
        
        # Set existing users to have claimed the bonus (so they don't get it again)
        print("🔄 Setting existing users as having claimed bonus...")
        cursor.execute("""
            UPDATE users 
            SET signin_bonus_claimed = 1
            WHERE created_at < ?
        """, datetime.utcnow())
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
        # Show current user stats
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE signin_bonus_claimed = 1")
        claimed_users = cursor.fetchone()[0]
        
        print(f"\n📊 Stats:")
        print(f"   Total users: {total_users}")
        print(f"   Users who claimed bonus: {claimed_users}")
        print(f"   New users eligible for bonus: {total_users - claimed_users}")
        
    except pyodbc.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Starting signin bonus migration...")
    migrate_signin_bonus()
    print("\n✨ Migration complete!") 
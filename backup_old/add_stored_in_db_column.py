"""
Migration script to add stored_in_db column to assets table
Run this to update existing databases with the new column
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL environment variable not set")
    sys.exit(1)

def add_stored_in_db_column():
    """Add stored_in_db column to assets table if it doesn't exist"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'assets' 
                AND COLUMN_NAME = 'stored_in_db'
            """))
            
            if result.scalar() == 0:
                # Add the column
                print("🔄 Adding stored_in_db column to assets table...")
                conn.execute(text("""
                    ALTER TABLE assets 
                    ADD stored_in_db BIT DEFAULT 0
                """))
                conn.commit()
                print("✅ Column added successfully")
            else:
                print("✅ Column stored_in_db already exists")
                
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🗄️ Database Migration: Adding stored_in_db column")
    print(f"📍 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'local'}")
    
    add_stored_in_db_column()
    
    print("\n✅ Migration complete!") 
"""
Migration script to add subscription fields to the User table
Run this script to update your database schema for subscription support
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_subscription_fields():
    """Add subscription-related columns to the users table"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    print(f"🔍 Connecting to database...")
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            check_query = text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'users' 
                AND COLUMN_NAME IN ('credits', 'subscription_plan', 'subscription_status', 
                                   'is_nsfw_enabled', 'paypal_subscription_id', 
                                   'subscription_start_date', 'subscription_end_date', 
                                   'sources_enabled')
            """)
            
            existing_columns = [row[0] for row in conn.execute(check_query)]
            
            # Add missing columns
            migration_queries = []
            
            if 'credits' not in existing_columns:
                migration_queries.append(
                    "ALTER TABLE users ADD credits INT DEFAULT 50"
                )
            
            if 'subscription_plan' not in existing_columns:
                migration_queries.append(
                    "ALTER TABLE users ADD subscription_plan VARCHAR(50) DEFAULT 'trial'"
                )
            
            if 'subscription_status' not in existing_columns:
                migration_queries.append(
                    "ALTER TABLE users ADD subscription_status VARCHAR(50) DEFAULT 'active'"
                )
            
            if 'is_nsfw_enabled' not in existing_columns:
                migration_queries.append(
                    "ALTER TABLE users ADD is_nsfw_enabled BIT DEFAULT 0"
                )
            
            if 'paypal_subscription_id' not in existing_columns:
                migration_queries.append(
                    "ALTER TABLE users ADD paypal_subscription_id VARCHAR(255)"
                )
            
            if 'subscription_start_date' not in existing_columns:
                migration_queries.append(
                    "ALTER TABLE users ADD subscription_start_date DATETIME"
                )
            
            if 'subscription_end_date' not in existing_columns:
                migration_queries.append(
                    "ALTER TABLE users ADD subscription_end_date DATETIME"
                )
            
            if 'sources_enabled' not in existing_columns:
                migration_queries.append(
                    "ALTER TABLE users ADD sources_enabled TEXT"
                )
            
            # Execute migrations
            if migration_queries:
                print(f"📝 Executing {len(migration_queries)} migration queries...")
                
                for query in migration_queries:
                    print(f"   ▶️ {query}")
                    conn.execute(text(query))
                    conn.commit()
                
                print("✅ Migration completed successfully!")
                
                # Set default sources for existing users
                print("🔄 Setting default sources for existing users...")
                update_query = text("""
                    UPDATE users 
                    SET sources_enabled = '["reddit", "imgur", "wikimedia", "deviantart"]'
                    WHERE sources_enabled IS NULL
                """)
                conn.execute(update_query)
                conn.commit()
                
                print("✅ Default sources set for existing users")
            else:
                print("✅ All subscription columns already exist, no migration needed")
            
            # Display current schema
            print("\n📊 Current user table schema:")
            schema_query = text("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'users'
                AND COLUMN_NAME IN ('credits', 'subscription_plan', 'subscription_status', 
                                   'is_nsfw_enabled', 'paypal_subscription_id', 
                                   'subscription_start_date', 'subscription_end_date', 
                                   'sources_enabled')
                ORDER BY ORDINAL_POSITION
            """)
            
            for row in conn.execute(schema_query):
                print(f"   - {row[0]}: {row[1]} (Nullable: {row[2]}, Default: {row[3]})")
                
    except Exception as e:
        print(f"❌ ERROR during migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting subscription fields migration...")
    print("=" * 50)
    migrate_subscription_fields()
    print("=" * 50)
    print("✅ Migration script completed!")
    print("\n📌 Next steps:")
    print("1. Restart your Flask application")
    print("2. Test the subscription features")
    print("3. Configure PayPal webhooks to point to /subscription/webhook") 
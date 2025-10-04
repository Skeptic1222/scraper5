"""
Add thumbnail_data and thumbnail_mime_type columns to MediaBlob table
Run this script to update the database schema
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_thumbnail_columns():
    """Add thumbnail columns to MediaBlob table"""

    # Get database URL
    database_url = os.getenv('DATABASE_URL', 'sqlite:///scraper.db')
    print(f"Using database: {database_url}")

    try:
        # Create engine
        engine = create_engine(database_url)
        inspector = inspect(engine)

        # Check if media_blobs table exists
        if 'media_blobs' not in inspector.get_table_names():
            print("ERROR: media_blobs table does not exist")
            sys.exit(1)

        # Get existing columns
        existing_columns = [col['name'] for col in inspector.get_columns('media_blobs')]

        thumbnail_cols_exist = 'thumbnail_data' in existing_columns and 'thumbnail_mime_type' in existing_columns

        if thumbnail_cols_exist:
            print("Thumbnail columns already exist in media_blobs table")
            return

        # Determine if we're using SQLite or SQL Server
        is_sqlite = 'sqlite' in database_url.lower()

        with engine.begin() as conn:
            print("Adding thumbnail columns to media_blobs table...")

            if is_sqlite:
                # SQLite syntax
                if 'thumbnail_data' not in existing_columns:
                    conn.execute(text("""
                        ALTER TABLE media_blobs
                        ADD COLUMN thumbnail_data BLOB
                    """))
                    print("Added thumbnail_data column")

                if 'thumbnail_mime_type' not in existing_columns:
                    conn.execute(text("""
                        ALTER TABLE media_blobs
                        ADD COLUMN thumbnail_mime_type VARCHAR(100)
                    """))
                    print("Added thumbnail_mime_type column")
            else:
                # SQL Server syntax
                if 'thumbnail_data' not in existing_columns:
                    conn.execute(text("""
                        ALTER TABLE media_blobs
                        ADD thumbnail_data VARBINARY(MAX) NULL
                    """))
                    print("Added thumbnail_data column")

                if 'thumbnail_mime_type' not in existing_columns:
                    conn.execute(text("""
                        ALTER TABLE media_blobs
                        ADD thumbnail_mime_type VARCHAR(100) NULL
                    """))
                    print("Added thumbnail_mime_type column")

            print("Successfully added thumbnail columns!")

    except Exception as e:
        print(f"ERROR: Failed to add thumbnail columns: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    add_thumbnail_columns()
    print("Database migration completed successfully!")
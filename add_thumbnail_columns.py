#!/usr/bin/env python3
"""
Add missing thumbnail columns to media_blobs table
"""

import os
import sys
from sqlalchemy import text

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def add_thumbnail_columns():
    """Add thumbnail_data and thumbnail_mime_type columns to media_blobs table"""

    print("Adding thumbnail columns to media_blobs table...")

    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("PRAGMA table_info(media_blobs)"))
            columns = [row[1] for row in result]

            if 'thumbnail_data' not in columns:
                print("Adding thumbnail_data column...")
                db.session.execute(text(
                    "ALTER TABLE media_blobs ADD COLUMN thumbnail_data BLOB"
                ))
                print("  [OK] thumbnail_data column added")
            else:
                print("  [SKIP] thumbnail_data column already exists")

            if 'thumbnail_mime_type' not in columns:
                print("Adding thumbnail_mime_type column...")
                db.session.execute(text(
                    "ALTER TABLE media_blobs ADD COLUMN thumbnail_mime_type VARCHAR(50)"
                ))
                print("  [OK] thumbnail_mime_type column added")
            else:
                print("  [SKIP] thumbnail_mime_type column already exists")

            db.session.commit()
            print("\n[SUCCESS] Database schema updated successfully!")

        except Exception as e:
            print(f"\n[ERROR] Failed to update schema: {e}")
            db.session.rollback()

if __name__ == "__main__":
    add_thumbnail_columns()
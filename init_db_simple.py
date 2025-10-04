#!/usr/bin/env python3
"""Initialize database schema for Enhanced Media Scraper"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

def init_database():
    """Initialize database with all tables"""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables created: {', '.join(tables)}")
            
            return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    if init_database():
        print("Database initialization complete!")
        sys.exit(0)
    else:
        print("Database initialization failed!")
        sys.exit(1)
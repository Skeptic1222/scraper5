#!/usr/bin/env python3
"""Initialize PostgreSQL database tables for Enhanced Media Scraper"""

import os
import sys

# Don't override the DATABASE_URL from Replit
# It's already set correctly to PostgreSQL

print("Initializing PostgreSQL database...")
print(f"Using DATABASE_URL: {os.environ.get('DATABASE_URL')[:50]}...")  # Print partial URL for security

try:
    from app import app, db
    from models import init_db
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Initialize default data
        init_db()
        print("✅ Default data initialized")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✅ Created {len(tables)} tables: {', '.join(tables)}")
        
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    sys.exit(1)

print("✅ PostgreSQL database initialization complete!")
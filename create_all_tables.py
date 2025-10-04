#!/usr/bin/env python3
"""Create all database tables"""

from app import app, db
from sqlalchemy import inspect

with app.app_context():
    print("Creating all database tables...")
    db.create_all()

    # List created tables
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    print(f"Created {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")

    # Check for media_blobs specifically
    if 'media_blobs' in tables:
        print("\n[OK] media_blobs table created successfully")
    else:
        print("\n[WARNING] media_blobs table was not created")
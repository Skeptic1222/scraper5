"""
Check database schema to see if tables exist
"""
from app import app

with app.app_context():
    from models import db
    from sqlalchemy import inspect

    print("=" * 60)
    print("DATABASE SCHEMA CHECK")
    print("=" * 60)

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    print(f"\nDatabase file: {db.engine.url}")
    print(f"\nTables in database: {len(tables)}")
    for table in tables:
        print(f"  - {table}")

    if 'scrape_jobs' in tables:
        print("\n[OK] scrape_jobs table EXISTS")
        columns = inspector.get_columns('scrape_jobs')
        print(f"\nColumns in scrape_jobs ({len(columns)} total):")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
    else:
        print("\n[ERROR] scrape_jobs table does NOT exist!")
        print("   Fix: Run 'python init_db.py' to create tables")

    print("\n" + "=" * 60)

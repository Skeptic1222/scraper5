#!/usr/bin/env python3
"""Check database schema"""
import sqlite3

db_path = 'C:/inetpub/wwwroot/scraper/instance/scraper.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table schema
    cursor.execute("PRAGMA table_info(scrape_jobs)")
    columns = cursor.fetchall()

    print("scrape_jobs table schema:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

    # Check if there are any jobs
    cursor.execute("SELECT COUNT(*) FROM scrape_jobs")
    count = cursor.fetchone()[0]
    print(f"\nTotal jobs in database: {count}")

    if count > 0:
        # Get recent jobs
        cursor.execute("SELECT * FROM scrape_jobs ORDER BY created_at DESC LIMIT 3")
        rows = cursor.fetchall()
        print(f"\nRecent jobs:")
        for row in rows:
            print(row)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""Check for running/stuck jobs in SQLite database"""
import sqlite3
from datetime import datetime

db_path = 'C:/inetpub/wwwroot/scraper/instance/scraper.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check for running jobs
    query = """
    SELECT
        id,
        type,
        status,
        created_at,
        updated_at,
        progress,
        message,
        data
    FROM scrape_jobs
    WHERE status IN ('running', 'downloading', 'processing')
    ORDER BY created_at DESC
    LIMIT 20
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    print(f"\n{'='*80}")
    print(f"RUNNING/STUCK JOBS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: {db_path}")
    print(f"{'='*80}\n")

    if not rows:
        print("No running jobs found.")
    else:
        print(f"Found {len(rows)} running jobs:\n")
        for row in rows:
            job_id, job_type, status, created_at, updated_at, progress, message, data = row
            print(f"Job ID: {job_id}")
            print(f"Type: {job_type}")
            print(f"Status: {status}")
            print(f"Created: {created_at}")
            print(f"Updated: {updated_at}")
            print(f"Progress: {progress}%")
            print(f"Message: {message}")
            print("-" * 80)

    # Check all recent jobs
    query_all = """
    SELECT
        id,
        type,
        status,
        created_at,
        message
    FROM scrape_jobs
    ORDER BY created_at DESC
    LIMIT 10
    """

    cursor.execute(query_all)
    all_rows = cursor.fetchall()

    print(f"\n{'='*80}")
    print("RECENT JOBS (Last 10)")
    print(f"{'='*80}\n")

    for row in all_rows:
        job_id, job_type, status, created_at, message = row
        print(f"{job_id[:8]}... | {status:12} | {created_at} | {message[:50] if message else 'No message'}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

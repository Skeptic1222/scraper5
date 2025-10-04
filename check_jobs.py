#!/usr/bin/env python3
"""Check for running/stuck jobs in the database"""
import os
import sys
from datetime import datetime
import pyodbc

# Database connection
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=.\\SQLEXPRESS;DATABASE=Scraped;Trusted_Connection=yes;'

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Check for running jobs
    query = """
    SELECT
        j.id,
        j.user_id,
        j.status,
        j.created_at,
        j.updated_at,
        j.total_sources,
        j.processed_sources,
        j.successful_sources,
        j.failed_sources,
        j.progress,
        DATEDIFF(MINUTE, j.created_at, GETDATE()) as minutes_running,
        u.email
    FROM scrape_jobs j
    LEFT JOIN users u ON j.user_id = u.id
    WHERE j.status IN ('running', 'downloading', 'processing')
    ORDER BY j.created_at DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    print(f"\n{'='*80}")
    print(f"RUNNING/STUCK JOBS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    if not rows:
        print("No running jobs found.")
    else:
        for row in rows:
            print(f"Job ID: {row.id}")
            print(f"User: {row.email}")
            print(f"Status: {row.status}")
            print(f"Created: {row.created_at}")
            print(f"Updated: {row.updated_at}")
            print(f"Minutes Running: {row.minutes_running}")
            print(f"Progress: {row.progress}%")
            print(f"Sources: {row.processed_sources}/{row.total_sources}")
            print(f"Successful: {row.successful_sources} | Failed: {row.failed_sources}")
            print("-" * 80)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

#!/usr/bin/env python3
"""Fix the currently stuck job"""
import sqlite3
from datetime import datetime

db_path = 'C:/inetpub/wwwroot/scraper/instance/scraper.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update stuck job
    job_id = 'd882637a-7978-4881-ae3d-55ee43a9ae4c'

    cursor.execute("""
        UPDATE scrape_jobs
        SET status = 'error',
            message = 'Job timed out - stuck on pexels source. Fixed by timeout implementation.',
            end_time = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), job_id))

    conn.commit()
    print(f"Fixed job {job_id}")

    # Verify
    cursor.execute("SELECT id, status, message FROM scrape_jobs WHERE id = ?", (job_id,))
    result = cursor.fetchone()
    print(f"Verified: {result}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

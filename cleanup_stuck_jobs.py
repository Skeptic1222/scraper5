#!/usr/bin/env python3
"""
Cleanup Stuck Jobs - Finds and marks jobs that have been running too long as failed
Run this periodically (e.g., every 10 minutes) via Task Scheduler
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up environment
os.chdir(project_root)

def cleanup_stuck_jobs():
    """Find and cleanup jobs that have been stuck for more than 10 minutes"""
    try:
        from app import create_app
        from models import db, ScrapeJob
        from datetime import datetime, timedelta

        app = create_app()
        with app.app_context():
            # Find jobs that have been "running" for more than 10 minutes
            cutoff_time = datetime.utcnow() - timedelta(minutes=10)

            stuck_jobs = ScrapeJob.query.filter(
                ScrapeJob.status.in_(['running', 'downloading', 'processing']),
                ScrapeJob.updated_at < cutoff_time
            ).all()

            if not stuck_jobs:
                print(f"[{datetime.now()}] No stuck jobs found")
                return

            print(f"[{datetime.now()}] Found {len(stuck_jobs)} stuck jobs")

            for job in stuck_jobs:
                minutes_running = (datetime.utcnow() - job.updated_at).total_seconds() / 60
                print(f"  - Job {job.id}: status={job.status}, stuck for {minutes_running:.1f} minutes")

                # Mark as failed
                job.status = 'error'
                job.message = f'Job timed out after {minutes_running:.1f} minutes of inactivity'
                job.updated_at = datetime.utcnow()

            db.session.commit()
            print(f"[{datetime.now()}] Marked {len(stuck_jobs)} jobs as failed")

    except Exception as e:
        print(f"[{datetime.now()}] ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    cleanup_stuck_jobs()

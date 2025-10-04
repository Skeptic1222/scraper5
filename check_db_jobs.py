"""
Check what jobs are actually in the database
"""
import os
import sys

# Set up Flask app context
from app import app

with app.app_context():
    from models import ScrapeJob, db
    from sqlalchemy import select

    print("=" * 60)
    print("DATABASE JOBS CHECK")
    print("=" * 60)

    # Get all jobs
    all_jobs = db.session.execute(select(ScrapeJob)).scalars().all()
    print(f"\nTotal jobs in database: {len(all_jobs)}")

    if all_jobs:
        print("\nAll Jobs:")
        for job in all_jobs:
            print(f"  ID: {job.id}")
            print(f"  Type: {job.job_type}")
            print(f"  Status: {job.status}")
            print(f"  Progress: {job.progress}%")
            print(f"  Query: {job.query}")
            print(f"  User ID: {job.user_id}")
            print(f"  Downloaded: {job.downloaded}")
            print(f"  Created: {job.created_at}")
            print(f"  Updated: {job.updated_at}")
            print(f"  ---")

    # Get running jobs
    running_jobs = db.session.execute(select(ScrapeJob).where(ScrapeJob.status.in_(['running', 'pending', 'downloading']))).scalars().all()
    print(f"\nRunning/Pending jobs: {len(running_jobs)}")

    # Get completed jobs
    completed_jobs = db.session.execute(select(ScrapeJob).where(ScrapeJob.status == 'completed')).scalars().all()
    print(f"Completed jobs: {len(completed_jobs)}")

    # Get failed jobs
    failed_jobs = db.session.execute(select(ScrapeJob).where(ScrapeJob.status == 'error')).scalars().all()
    print(f"Failed jobs: {len(failed_jobs)}")

    # Test the get_user_jobs function
    print("\n" + "=" * 60)
    print("TESTING get_user_jobs FUNCTION")
    print("=" * 60)

    from db_job_manager import db_job_manager

    # Test with status filter
    jobs = db_job_manager.get_user_jobs(user_id=None, status_filter='running')
    print(f"\nget_user_jobs(user_id=None, status_filter='running'): {len(jobs)} jobs")
    for job in jobs:
        print(f"  - {job['id']}: {job['status']} - {job['query']}")

    # Test without status filter
    jobs_all = db_job_manager.get_user_jobs(user_id=None, limit=20)
    print(f"\nget_user_jobs(user_id=None, limit=20): {len(jobs_all)} jobs")
    for job in jobs_all[:5]:
        print(f"  - {job['id']}: {job['status']} - {job['query']}")

    print("\n" + "=" * 60)

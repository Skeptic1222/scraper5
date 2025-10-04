"""
Database-backed Job Manager - Persistent job tracking using SQLAlchemy
"""
import uuid
import json
import logging
from datetime import datetime
from flask import has_app_context

logger = logging.getLogger(__name__)

# Fallback in-memory storage for when database is unavailable
MEMORY_JOBS = {}

def create_job(job_type, data):
    """Create a new job in database"""
    job_id = str(uuid.uuid4())

    # DEBUG: Print enabled_sources
    enabled_srcs = data.get('enabled_sources', [])
    print(f"[DB_JOB_MANAGER DEBUG] create_job called with {len(enabled_srcs)} sources: {enabled_srcs}")
    logger.info(f"[DB_JOB_MANAGER] create_job called with {len(enabled_srcs)} sources: {enabled_srcs}")

    # Try database first
    if has_app_context():
        try:
            from models import ScrapeJob, db
            logger.info(f"[DB JOBS] Attempting to create job {job_id} in database")
            job = ScrapeJob(
                id=job_id,
                job_type=job_type,
                user_id=data.get('user_id'),
                query=data.get('query', ''),
                max_content=data.get('max_content', 20),
                safe_search=data.get('safe_search', True),
                status='pending',
                progress=0,
                message='Job created',
                enabled_sources=json.dumps(data.get('enabled_sources', []))
            )
            logger.info(f"[DB JOBS] ScrapeJob object created, adding to session...")
            db.session.add(job)
            logger.info(f"[DB JOBS] Added to session, committing...")
            db.session.commit()
            logger.info(f"[DB JOBS] SUCCESS! Created job {job_id} in database")
            return job_id
        except Exception as e:
            logger.error(f"[DB JOBS] FAILED to create job in database: {e}")
            import traceback
            traceback.print_exc()
            # Fall through to memory storage

    # Fallback to memory storage
    job = {
        'id': job_id,
        'type': job_type,
        'data': data,
        'status': 'pending',
        'progress': 0,
        'message': 'Job created',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'detected': 0,
        'downloaded': 0,
        'images': 0,
        'videos': 0,
        'sources': {},
        'results': {}
    }
    MEMORY_JOBS[job_id] = job
    logger.warning(f"[MEMORY JOBS] Created job {job_id} in memory (database unavailable)")
    return job_id

def update_job(job_id, **kwargs):
    """Update job status in database"""
    # Try database first
    if has_app_context():
        try:
            from models import ScrapeJob, db
            job = db.session.get(ScrapeJob, job_id)
            if job:
                for key, value in kwargs.items():
                    if hasattr(job, key):
                        setattr(job, key, value)
                db.session.commit()
                logger.debug(f"[DB JOBS] Updated job {job_id}: {kwargs}")
                return
        except Exception as e:
            logger.error(f"[DB JOBS] Failed to update job in database: {e}")
            # Fall through to memory storage

    # Fallback to memory storage
    if job_id in MEMORY_JOBS:
        job = MEMORY_JOBS[job_id]
        for key, value in kwargs.items():
            job[key] = value
        job['updated_at'] = datetime.utcnow().isoformat()
        logger.debug(f"[MEMORY JOBS] Updated job {job_id}: {kwargs}")
    else:
        logger.warning(f"[JOBS] Warning: Job {job_id} not found in memory or database")

def get_job(job_id):
    """Get job details from database or memory"""
    # Try database first
    if has_app_context():
        try:
            from models import ScrapeJob, db
            job = db.session.get(ScrapeJob, job_id)
            if job:
                return {
                    'id': job.id,
                    'type': job.job_type,
                    'status': job.status,
                    'progress': job.progress,
                    'message': job.message,
                    'query': job.query,
                    'detected': job.detected,
                    'downloaded': job.downloaded,
                    'failed': job.failed,
                    'images': job.images,
                    'videos': job.videos,
                    'current_file': job.current_file,
                    'user_id': job.user_id,
                    'created_at': job.created_at.isoformat() if job.created_at else None,
                    'updated_at': job.created_at.isoformat() if job.created_at else None,  # Use created_at as fallback
                    'enabled_sources': job.enabled_sources,
                    'sources_data': job.sources_data,
                    'live_updates': job.live_updates,
                    'data': {'query': job.query, 'user_id': job.user_id}  # Add data dict for compatibility
                }
        except Exception as e:
            logger.error(f"[DB JOBS] Failed to get job from database: {e}")

    # Fallback to memory
    return MEMORY_JOBS.get(job_id)

def get_recent_jobs(limit=10):
    """Get recent jobs from database or memory"""
    # Try database first
    if has_app_context():
        try:
            from models import ScrapeJob, db
            from sqlalchemy import select

            stmt = select(ScrapeJob).order_by(ScrapeJob.created_at.desc()).limit(limit)
            jobs = db.session.execute(stmt).scalars().all()
            return [{
                'id': job.id,
                'type': job.job_type,
                'status': job.status,
                'progress': job.progress,
                'query': job.query,
                'created_at': job.created_at.isoformat() if job.created_at else None
            } for job in jobs]
        except Exception as e:
            logger.error(f"[DB JOBS] Failed to get recent jobs from database: {e}")

    # Fallback to memory
    jobs_list = list(MEMORY_JOBS.values())
    jobs_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jobs_list[:limit]

def cleanup_old_jobs(days=30):
    """Cleanup old jobs from database or memory"""
    # Try database first
    if has_app_context():
        try:
            from models import ScrapeJob, db
            from datetime import timedelta
            from sqlalchemy import select, delete

            cutoff_date = datetime.utcnow() - timedelta(days=days)
            stmt = delete(ScrapeJob).where(
                ScrapeJob.created_at < cutoff_date,
                ScrapeJob.status.in_(['completed', 'error'])
            )
            result = db.session.execute(stmt)
            db.session.commit()
            deleted = result.rowcount
            logger.info(f"[DB JOBS] Cleaned up {deleted} old jobs from database")
            return deleted
        except Exception as e:
            logger.error(f"[DB JOBS] Failed to cleanup jobs from database: {e}")

    # Fallback to memory cleanup
    to_remove = []
    for job_id, job in MEMORY_JOBS.items():
        if job.get('status') in ['completed', 'error']:
            to_remove.append(job_id)

    for job_id in to_remove[:10]:
        del MEMORY_JOBS[job_id]

    return len(to_remove[:10])

def get_user_jobs(user_id=None, limit=20, status_filter=None):
    """Get jobs for a user or all jobs if user_id is None"""
    # Try database first
    if has_app_context():
        try:
            from models import ScrapeJob, db
            from sqlalchemy import select

            # Build query using SQLAlchemy 2.x/3.x syntax
            stmt = select(ScrapeJob)

            # Filter by user if specified
            if user_id is not None:
                stmt = stmt.where(ScrapeJob.user_id == user_id)

            # Filter by status if specified
            if status_filter:
                if status_filter in ['running', 'pending', 'downloading']:
                    # Show active jobs
                    stmt = stmt.where(ScrapeJob.status.in_(['running', 'pending', 'downloading']))
                else:
                    stmt = stmt.where(ScrapeJob.status == status_filter)

            # Order by created_at descending and limit
            stmt = stmt.order_by(ScrapeJob.created_at.desc()).limit(limit)

            # Execute query
            jobs = db.session.execute(stmt).scalars().all()

            return [{
                'id': job.id,
                'type': job.job_type,
                'status': job.status,
                'progress': job.progress,
                'message': job.message,
                'query': job.query,
                'detected': job.detected,
                'downloaded': job.downloaded,
                'failed': job.failed,
                'images': job.images,
                'videos': job.videos,
                'current_file': job.current_file,
                'user_id': job.user_id,
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'updated_at': job.created_at.isoformat() if job.created_at else None
            } for job in jobs]
        except Exception as e:
            logger.error(f"[DB JOBS] Failed to get user jobs from database: {e}")
            import traceback
            traceback.print_exc()

    # Fallback to memory
    jobs_list = []
    for job_id, job in MEMORY_JOBS.items():
        # Filter by user if specified
        if user_id is not None and job.get('user_id') != user_id:
            continue

        # Filter by status if specified
        if status_filter:
            if status_filter in ['running', 'pending', 'downloading']:
                if job.get('status') not in ['running', 'pending', 'downloading']:
                    continue
            elif job.get('status') != status_filter:
                continue

        jobs_list.append(job)

    # Sort by created_at descending
    jobs_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jobs_list[:limit]

def get_job_statistics(user_id=None):
    """Get job statistics for a user"""
    stats = {
        'total_jobs': 0,
        'completed_jobs': 0,
        'failed_jobs': 0,
        'running_jobs': 0,
        'total_downloaded': 0
    }

    # Try database first
    if has_app_context():
        try:
            from models import ScrapeJob, db
            from sqlalchemy import func, select

            # Base query
            base_stmt = select(ScrapeJob)
            if user_id:
                base_stmt = base_stmt.where(ScrapeJob.user_id == user_id)

            # Total jobs
            stats['total_jobs'] = db.session.execute(select(func.count()).select_from(base_stmt.subquery())).scalar()

            # Completed jobs
            completed_stmt = base_stmt.where(ScrapeJob.status == 'completed')
            stats['completed_jobs'] = db.session.execute(select(func.count()).select_from(completed_stmt.subquery())).scalar()

            # Failed jobs
            failed_stmt = base_stmt.where(ScrapeJob.status == 'failed')
            stats['failed_jobs'] = db.session.execute(select(func.count()).select_from(failed_stmt.subquery())).scalar()

            # Running jobs
            running_stmt = base_stmt.where(ScrapeJob.status.in_(['running', 'pending', 'downloading']))
            stats['running_jobs'] = db.session.execute(select(func.count()).select_from(running_stmt.subquery())).scalar()

            # Total downloaded
            downloaded_stmt = select(func.sum(ScrapeJob.downloaded))
            if user_id:
                downloaded_stmt = downloaded_stmt.where(ScrapeJob.user_id == user_id)
            stats['total_downloaded'] = db.session.execute(downloaded_stmt).scalar() or 0

            return stats
        except Exception as e:
            logger.error(f"[DB JOBS] Failed to get job statistics: {e}")

    # Fallback to memory statistics
    for job in MEMORY_JOBS.values():
        if user_id and job.get('user_id') != user_id:
            continue

        stats['total_jobs'] += 1
        if job.get('status') == 'completed':
            stats['completed_jobs'] += 1
        elif job.get('status') == 'failed':
            stats['failed_jobs'] += 1
        elif job.get('status') in ['running', 'pending', 'downloading']:
            stats['running_jobs'] += 1
        stats['total_downloaded'] += job.get('downloaded', 0)

    return stats

def cancel_job(job_id, user_id=None):
    """Cancel a job"""
    # Try database first
    if has_app_context():
        try:
            from models import ScrapeJob, db
            job = db.session.get(ScrapeJob, job_id)
            if job:
                # Check permission
                if user_id and job.user_id != user_id:
                    return False

                # Update status
                job.status = 'cancelled'
                job.message = 'Job cancelled by user'
                db.session.commit()
                logger.info(f"[DB JOBS] Cancelled job {job_id}")
                return True
        except Exception as e:
            logger.error(f"[DB JOBS] Failed to cancel job: {e}")

    # Fallback to memory
    if job_id in MEMORY_JOBS:
        job = MEMORY_JOBS[job_id]
        if user_id and job.get('user_id') != user_id:
            return False

        job['status'] = 'cancelled'
        job['message'] = 'Job cancelled by user'
        logger.info(f"[MEMORY JOBS] Cancelled job {job_id}")
        return True

    return False

def add_progress_update(job_id, message, progress, downloaded, images, videos, current_file):
    """Add a progress update to a job"""
    update_job(
        job_id,
        message=message,
        progress=progress,
        downloaded=downloaded,
        images=images,
        videos=videos,
        current_file=current_file
    )

# Create a class-like interface for compatibility
class DBJobManager:
    """Database-backed job manager with memory fallback"""
    create_job = staticmethod(create_job)
    update_job = staticmethod(update_job)
    get_job = staticmethod(get_job)
    get_job_status = staticmethod(get_job)  # Alias for compatibility
    get_recent_jobs = staticmethod(get_recent_jobs)
    cleanup_old_jobs = staticmethod(cleanup_old_jobs)
    add_progress_update = staticmethod(add_progress_update)
    get_user_jobs = staticmethod(get_user_jobs)
    get_job_statistics = staticmethod(get_job_statistics)
    cancel_job = staticmethod(cancel_job)

# Create instance for import
db_job_manager = DBJobManager()

"""
Memory-based Job Manager - Works without database
"""
import uuid
from datetime import datetime

# In-memory job storage
MEMORY_JOBS = {}

def create_job(job_type, data):
    """Create a new job in memory"""
    job_id = str(uuid.uuid4())
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
    print(f"[JOBS] Created job {job_id} of type {job_type}")
    return job_id

def update_job(job_id, **kwargs):
    """Update job status in memory"""
    if job_id in MEMORY_JOBS:
        job = MEMORY_JOBS[job_id]
        for key, value in kwargs.items():
            job[key] = value
        job['updated_at'] = datetime.utcnow().isoformat()
        print(f"[JOBS] Updated job {job_id}: {kwargs}")
    else:
        print(f"[JOBS] Warning: Job {job_id} not found")

def get_job(job_id):
    """Get job details from memory"""
    return MEMORY_JOBS.get(job_id)

def get_recent_jobs(limit=10):
    """Get recent jobs from memory"""
    jobs_list = list(MEMORY_JOBS.values())
    # Sort by created_at descending
    jobs_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jobs_list[:limit]

def cleanup_old_jobs(days=30):
    """Cleanup old jobs from memory"""
    # For memory storage, just clear old completed jobs
    to_remove = []
    for job_id, job in MEMORY_JOBS.items():
        if job.get('status') in ['completed', 'error']:
            to_remove.append(job_id)

    for job_id in to_remove[:10]:  # Remove max 10 at a time
        del MEMORY_JOBS[job_id]

    return len(to_remove[:10])

def add_progress_update(job_id, message, progress, downloaded, images, videos, current_file):
    """Add a progress update to a job"""
    if job_id in MEMORY_JOBS:
        job = MEMORY_JOBS[job_id]
        # Update progress info
        job['message'] = message
        job['progress'] = progress
        job['downloaded'] = downloaded
        job['images'] = images
        job['videos'] = videos
        job['current_file'] = current_file
        job['updated_at'] = datetime.utcnow().isoformat()
        print(f"[JOBS] Progress update for {job_id}: {message} ({progress}%)")

# Create a class-like interface for compatibility
class DBJobManager:
    """Memory-based job manager"""
    create_job = staticmethod(create_job)
    update_job = staticmethod(update_job)
    get_job = staticmethod(get_job)
    get_job_status = staticmethod(get_job)  # Alias for compatibility
    get_recent_jobs = staticmethod(get_recent_jobs)
    cleanup_old_jobs = staticmethod(cleanup_old_jobs)
    add_progress_update = staticmethod(add_progress_update)

# Create instance for import
db_job_manager = DBJobManager()

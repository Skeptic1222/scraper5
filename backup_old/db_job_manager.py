"""
Database-driven Job and Asset Managers
Enhanced versions of JobManager and AssetManager using SQLAlchemy models
"""

import os
import time
import threading
from datetime import datetime, timedelta
from flask_login import current_user
from models import db, ScrapeJob, Asset, AppSetting, MediaBlob, User
import json

class DatabaseJobManager:
    """Database-driven job manager using SQLAlchemy models"""
    
    def __init__(self):
        self.lock = threading.Lock()
    
    def create_job(self, job_type, params):
        """Create a new job and return job ID"""
        with self.lock:
            # Extract common parameters
            query = params.get('query', '')
            max_content = params.get('max_content', 10)
            safe_search = params.get('safe_search', True)
            enabled_sources = params.get('enabled_sources', [])
            user_id = params.get('user_id')  # May be None for guest users
            
            # Generate unique job ID
            import uuid
            job_id = str(uuid.uuid4())
            
            # Create job record
            job = ScrapeJob(
                id=job_id,
                user_id=user_id,
                job_type=job_type,
                status='starting',
                query=query,
                max_content=max_content,
                safe_search=safe_search,
                message='Job starting...'
            )
            
            # Set enabled sources
            job.set_enabled_sources(enabled_sources)
            
            db.session.add(job)
            
            try:
                db.session.commit()
                return job_id
            except Exception as e:
                db.session.rollback()
                print(f"Error creating job: {e}")
                return None
    
    def update_job(self, job_id, **updates):
        """Update job with new data"""
        with self.lock:
            job = db.session.query(ScrapeJob).filter_by(id=job_id).first()
            if not job:
                return False
            
            # Update allowed fields
            for key, value in updates.items():
                if hasattr(job, key):
                    # Special handling for 'results' field - convert dict to JSON
                    if key == 'results' and isinstance(value, dict):
                        setattr(job, key, json.dumps(value))
                    else:
                        setattr(job, key, value)
            
            # Add live update if message provided
            if 'message' in updates and updates['message']:
                job.add_live_update(updates['message'])
            
            try:
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"Error updating job {job_id}: {e}")
                return False
    
    def get_job(self, job_id):
        """Get job by ID"""
        return db.session.query(ScrapeJob).filter_by(id=job_id).first()
    
    def add_progress_update(self, job_id, message, progress, downloaded, images, videos, current_file=None):
        """Add a progress update to a job with enhanced tracking"""
        with self.lock:
            job = db.session.query(ScrapeJob).filter_by(id=job_id).first()
            if job:
                # Update core stats
                job.progress = progress
                job.downloaded = downloaded
                job.images = images
                job.videos = videos
                
                # Parse message for scan/source information
                scan_total = None
                source_name = None
                
                # Extract scan total from messages like "Scanning 1/50..."
                import re
                scan_match = re.search(r'(\d+)/(\d+)', message)
                if scan_match:
                    scan_total = int(scan_match.group(2))
                
                # Extract source name from messages containing source info
                if ':' in message:
                    parts = message.split(':', 1)
                    potential_source = parts[0].strip()
                    # Check if it looks like a source name
                    if len(potential_source) < 30 and not any(char in potential_source for char in ['/', '\\', '.', ',', ';']):
                        source_name = potential_source
                
                # Enhanced metadata tracking
                if job.results and isinstance(job.results, str):
                    metadata = json.loads(job.results)
                else:
                    metadata = {}
                
                # Track scan progress
                if 'scan_progress' not in metadata:
                    metadata['scan_progress'] = {
                        'total_scanned': 0,
                        'sources': {}
                    }
                
                # Update total scanned if we detected it
                if scan_total and scan_total > metadata['scan_progress'].get('total_scanned', 0):
                    metadata['scan_progress']['total_scanned'] = scan_total
                
                # Track per-source progress
                if source_name:
                    if source_name not in metadata['scan_progress']['sources']:
                        metadata['scan_progress']['sources'][source_name] = {
                            'scanned': 0,
                            'downloaded': 0,
                            'images': 0,
                            'videos': 0
                        }
                    
                    source_stats = metadata['scan_progress']['sources'][source_name]
                    
                    # Update source-specific stats
                    if 'Downloaded:' in message or '✅' in message:
                        source_stats['downloaded'] = source_stats.get('downloaded', 0) + 1
                        if 'video' in message.lower() or '.mp4' in message.lower() or '.webm' in message.lower():
                            source_stats['videos'] = source_stats.get('videos', 0) + 1
                        else:
                            source_stats['images'] = source_stats.get('images', 0) + 1
                    
                    if scan_match:
                        current_scan = int(scan_match.group(1))
                        source_stats['scanned'] = max(source_stats.get('scanned', 0), current_scan)
                
                # Add live update
                live_update = {
                    'timestamp': datetime.utcnow().strftime('%H:%M:%S'),
                    'message': message[:200]  # Truncate long messages
                }
                
                if 'live_updates' not in metadata:
                    metadata['live_updates'] = []
                    
                metadata['live_updates'].insert(0, live_update)
                metadata['live_updates'] = metadata['live_updates'][:10]  # Keep last 10
                
                job.results = json.dumps(metadata)
                job.created_at = datetime.utcnow()
                
                db.session.commit()
    
    def get_job_status(self, job_id):
        """Get status of a job with enhanced metadata"""
        job = db.session.query(ScrapeJob).filter_by(id=job_id).first()
        
        if not job:
            return {'status': 'not_found'}
        
        if job.results and isinstance(job.results, str):
            metadata = json.loads(job.results)
        else:
            metadata = {}
        
        # Extract enhanced progress information
        scan_progress = metadata.get('scan_progress', {})
        total_scanned = scan_progress.get('total_scanned', 0)
        sources_progress = scan_progress.get('sources', {})
        
        return {
            'id': job.id,
            'status': job.status,
            'progress': job.progress,
            'message': job.message,
            'downloaded': job.downloaded,
            'detected': job.detected,
            'images': job.images,
            'videos': job.videos,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'updated_at': job.end_time.isoformat() if job.end_time else None,
            'completed_at': job.end_time.isoformat() if job.end_time and job.status == 'completed' else None,
            'live_updates': metadata.get('live_updates', []),
            'user_id': job.user_id,
            'scan_progress': {
                'total_scanned': total_scanned,
                'total_downloaded': job.downloaded,
                'success_rate': round((job.downloaded / total_scanned * 100) if total_scanned > 0 else 0, 1),
                'sources': sources_progress
            }
        }
    
    def complete_job(self, job_id, results):
        """Complete job with final results"""
        update_data = {
            'status': 'completed',
            'progress': 100,
            'end_time': datetime.utcnow(),
            'results': results
        }
        
        return self.update_job(job_id, **update_data)
    
    def get_user_jobs(self, user_id=None, limit=50, status_filter=None):
        """Get jobs for a specific user or all jobs (admin only)"""
        query = db.session.query(ScrapeJob)
        
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        jobs = query.order_by(ScrapeJob.start_time.desc()).limit(limit).all()
        return [job.to_dict() for job in jobs]
    
    def get_active_jobs(self, user_id=None):
        """Get currently active jobs"""
        query = db.session.query(ScrapeJob).filter(
            ScrapeJob.status.in_(['starting', 'running'])
        )
        
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        
        jobs = query.order_by(ScrapeJob.start_time.desc()).all()
        return [job.to_dict() for job in jobs]
    
    def cancel_job(self, job_id, user_id=None):
        """Cancel a job (only if user owns it or is admin)"""
        job = db.session.query(ScrapeJob).filter_by(id=job_id).first()
        if not job:
            return False
        
        # Check permissions
        if user_id is not None and job.user_id != user_id and not current_user.is_admin():
            return False
        
        if job.status in ['starting', 'running']:
            job.status = 'cancelled'
            job.end_time = datetime.utcnow()
            job.message = 'Job cancelled by user'
            
            try:
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"Error cancelling job {job_id}: {e}")
                return False
        
        return False
    
    def cleanup_old_jobs(self, days_old=30):
        """Clean up old completed jobs"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_jobs = db.session.query(ScrapeJob).filter(
            ScrapeJob.end_time < cutoff_date,
            ScrapeJob.status.in_(['completed', 'error', 'cancelled'])
        ).all()
        
        for job in old_jobs:
            db.session.delete(job)
        
        try:
            db.session.commit()
            return len(old_jobs)
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up old jobs: {e}")
            return 0
    
    def get_job_statistics(self, user_id=None):
        """Get job statistics for dashboard"""
        query = db.session.query(ScrapeJob)
        
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        
        total_jobs = query.count()
        completed_jobs = query.filter_by(status='completed').count()
        running_jobs = query.filter(ScrapeJob.status.in_(['starting', 'running'])).count()
        failed_jobs = query.filter_by(status='error').count()
        
        # Get total downloads across all jobs
        total_downloaded = db.session.query(
            db.func.sum(ScrapeJob.downloaded)
        ).filter(
            ScrapeJob.user_id == user_id if user_id else True
        ).scalar() or 0
        
        total_images = db.session.query(
            db.func.sum(ScrapeJob.images)
        ).filter(
            ScrapeJob.user_id == user_id if user_id else True
        ).scalar() or 0
        
        total_videos = db.session.query(
            db.func.sum(ScrapeJob.videos)
        ).filter(
            ScrapeJob.user_id == user_id if user_id else True
        ).scalar() or 0
        
        return {
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'running_jobs': running_jobs,
            'failed_jobs': failed_jobs,
            'total_downloaded': total_downloaded,
            'total_images': total_images,
            'total_videos': total_videos,
            'success_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        }

class DatabaseAssetManager:
    """Database-driven asset manager for tracking downloaded files"""
    
    def __init__(self):
        self.lock = threading.Lock()
    
    def add_asset(self, job_id, filepath, file_type, metadata=None):
        """Add a new asset to the database"""
        with self.lock:
            filename = os.path.basename(filepath)
            file_extension = os.path.splitext(filename)[1].lower().lstrip('.')
            
            # Get file size
            file_size = None
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
            
            # Get user ID from job
            job = db.session.query(ScrapeJob).filter_by(id=job_id).first()
            user_id = job.user_id if job else None
            
            asset = Asset(
                user_id=user_id,
                job_id=job_id,
                filename=filename,
                file_path=filepath,
                file_type=file_type,
                file_size=file_size,
                file_extension=file_extension,
                source_url=metadata.get('source_url') if metadata else None,
                source_name=metadata.get('source_name') if metadata else None,
                width=metadata.get('width') if metadata else None,
                height=metadata.get('height') if metadata else None,
                duration=metadata.get('duration') if metadata else None
            )
            
            if metadata:
                asset.set_metadata(metadata)
            
            db.session.add(asset)
            
            try:
                db.session.commit()
                
                # Store the file in the database as a MediaBlob
                if user_id is not None and os.path.exists(filepath):
                    try:
                        # Determine MIME type based on file extension
                        mime_type = None
                        if file_type == 'image':
                            mime_type_map = {
                                'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                                'png': 'image/png', 'gif': 'image/gif',
                                'webp': 'image/webp', 'bmp': 'image/bmp'
                            }
                            mime_type = mime_type_map.get(file_extension, 'image/jpeg')
                        elif file_type == 'video':
                            mime_type_map = {
                                'mp4': 'video/mp4', 'webm': 'video/webm',
                                'avi': 'video/avi', 'mov': 'video/quicktime',
                                'mkv': 'video/x-matroska'
                            }
                            mime_type = mime_type_map.get(file_extension, 'video/mp4')
                        
                        # Store the file in the database
                        media_blob = MediaBlob.store_media_file(
                            asset_id=asset.id,
                            user_id=user_id,
                            file_path=filepath,
                            mime_type=mime_type
                        )
                        
                        # Only delete the file if MediaBlob was successfully created
                        if media_blob:
                            # Verify that the blob has data before deleting the file
                            if hasattr(media_blob, 'media_data') and media_blob.media_data and len(media_blob.media_data) > 0:
                                # Verify the asset was marked as stored
                                asset_check = db.session.query(Asset).filter_by(id=asset.id).first()
                                if asset_check and asset_check.stored_in_db:
                                    try:
                                        os.remove(filepath)
                                        print(f"✅ Stored file {filename} in database and removed from disk")
                                    except OSError as e:
                                        print(f"⚠️ Could not delete file after storing: {e}")
                                else:
                                    print(f"⚠️ Asset not marked as stored_in_db, keeping file on disk")
                            else:
                                print(f"⚠️ MediaBlob created but no data, keeping file on disk")
                        else:
                            print(f"⚠️ MediaBlob creation returned None, keeping file on disk")
                            
                    except Exception as e:
                        print(f"⚠️ Warning: Could not store file in database: {e}")
                        print(f"   File will remain on disk: {filepath}")
                        # Do NOT delete the file if storage failed
                else:
                    if user_id is None:
                        print(f"ℹ️ Skipping database storage for guest asset: {filename}")
                    elif not os.path.exists(filepath):
                        print(f"⚠️ File does not exist, cannot store in database: {filepath}")
                
                return asset.id
            except Exception as e:
                db.session.rollback()
                print(f"Error adding asset: {e}")
                return None
    
    def get_assets(self, user_id=None, file_type=None, limit=100, offset=0):
        """Get assets with filtering options"""
        query = db.session.query(Asset).filter_by(is_deleted=False)
        
        if user_id is not None:
            # For authenticated users, show only their assets
            query = query.filter_by(user_id=user_id)
        else:
            # For guest users, show only public assets (where user_id is NULL)
            query = query.filter(Asset.user_id.is_(None))
        
        if file_type:
            query = query.filter_by(file_type=file_type)
        
        # Order by newest first
        query = query.order_by(Asset.downloaded_at.desc())
        
        if limit:
            query = query.offset(offset).limit(limit)
        
        assets = query.all()
        return [asset.to_dict() for asset in assets]
    
    def delete_asset(self, asset_id, user_id=None):
        """Mark asset as deleted (soft delete) and optionally delete MediaBlob"""
        with self.lock:
            query = db.session.query(Asset).filter_by(id=asset_id, is_deleted=False)
            
            if user_id is not None:
                query = query.filter_by(user_id=user_id)
            
            asset = query.first()
            if not asset:
                return False
            
            # Delete associated MediaBlob if it exists
            if asset.media_blob:
                db.session.delete(asset.media_blob)
            
            # Mark asset as deleted
            asset.is_deleted = True
            
            try:
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"Error deleting asset {asset_id}: {e}")
                return False
    
    def bulk_delete_assets(self, asset_ids, user_id=None):
        """Bulk delete multiple assets"""
        with self.lock:
            deleted_count = 0
            
            for asset_id in asset_ids:
                try:
                    query = db.session.query(Asset).filter_by(id=asset_id, is_deleted=False)
                    
                    if user_id is not None:
                        query = query.filter_by(user_id=user_id)
                    
                    asset = query.first()
                    if asset:
                        # Delete associated MediaBlob if it exists
                        if asset.media_blob:
                            db.session.delete(asset.media_blob)
                        
                        # Mark asset as deleted
                        asset.is_deleted = True
                        deleted_count += 1
                        
                except Exception as e:
                    print(f"Error deleting asset {asset_id}: {e}")
                    continue
            
            try:
                db.session.commit()
                return deleted_count
            except Exception as e:
                db.session.rollback()
                print(f"Error in bulk delete: {e}")
                return 0
    
    def move_assets_to_container(self, asset_ids, container_name, user_id=None):
        """Move assets to a different container/category"""
        with self.lock:
            moved_count = 0
            
            for asset_id in asset_ids:
                try:
                    query = db.session.query(Asset).filter_by(id=asset_id, is_deleted=False)
                    
                    if user_id is not None:
                        query = query.filter_by(user_id=user_id)
                    
                    asset = query.first()
                    if asset:
                        # Update metadata to include container
                        metadata = asset.get_metadata()
                        metadata['container'] = container_name
                        asset.set_metadata(metadata)
                        moved_count += 1
                        
                except Exception as e:
                    print(f"Error moving asset {asset_id}: {e}")
                    continue
            
            try:
                db.session.commit()
                return moved_count
            except Exception as e:
                db.session.rollback()
                print(f"Error moving assets: {e}")
                return 0
    
    def get_user_containers(self, user_id):
        """Get all unique containers for a user's assets"""
        try:
            # Query all assets for the user
            assets = db.session.query(Asset).filter_by(
                user_id=user_id,
                is_deleted=False
            ).all()
            
            containers = set(['default'])  # Always include default
            
            for asset in assets:
                metadata = asset.get_metadata()
                if 'container' in metadata:
                    containers.add(metadata['container'])
            
            return sorted(list(containers))
            
        except Exception as e:
            print(f"Error getting containers: {e}")
            return ['default']
    
    def get_asset_statistics(self, user_id=None):
        """Get asset statistics for dashboard"""
        query = db.session.query(Asset).filter_by(is_deleted=False)
        
        if user_id is not None:
            # For authenticated users, show only their assets
            query = query.filter_by(user_id=user_id)
        else:
            # For guest users, show only public assets (where user_id is NULL)
            query = query.filter(Asset.user_id.is_(None))
        
        total_assets = query.count()
        total_images = query.filter_by(file_type='image').count()
        total_videos = query.filter_by(file_type='video').count()
        
        # Get total file size
        total_size = db.session.query(
            db.func.sum(Asset.file_size)
        ).filter(
            Asset.is_deleted == False,
            Asset.user_id == user_id if user_id is not None else Asset.user_id.is_(None)
        ).scalar() or 0
        
        return {
            'total_assets': total_assets,
            'total_images': total_images,
            'total_videos': total_videos,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
    
    def cleanup_missing_files(self):
        """Clean up database entries for missing files"""
        assets = db.session.query(Asset).filter_by(is_deleted=False).all()
        cleaned_count = 0
        
        for asset in assets:
            if not os.path.exists(asset.file_path):
                asset.is_deleted = True
                cleaned_count += 1
        
        try:
            db.session.commit()
            return cleaned_count
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up missing files: {e}")
            return 0

# Global instances
db_job_manager = DatabaseJobManager()
db_asset_manager = DatabaseAssetManager() 
"""
Database Asset Manager - Works with PostgreSQL database
"""
import os
import uuid
import json
import mimetypes
import hashlib
from datetime import datetime
from sqlalchemy import func
from models import Asset, MediaBlob, db
from io import BytesIO
from PIL import Image
import logging

# Setup logger
logger = logging.getLogger(__name__)

def generate_thumbnail(file_data, content_type, max_size=(200, 200)):
    """Generate thumbnail for images and videos

    Args:
        file_data: Raw bytes of the file
        content_type: MIME type of the file
        max_size: Maximum size of thumbnail (width, height)

    Returns:
        tuple: (thumbnail_bytes, thumbnail_mime_type) or (None, None) if failed
    """
    try:
        # Handle images
        if content_type and content_type.startswith('image/'):
            # Open image from bytes
            img = Image.open(BytesIO(file_data))

            # Convert RGBA to RGB if needed (for JPEG output)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # Generate thumbnail maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save to bytes
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            thumbnail_bytes = output.getvalue()

            return thumbnail_bytes, 'image/jpeg'

        # Handle videos (extract first frame)
        elif content_type and content_type.startswith('video/'):
            try:
                # Try using opencv if available
                import cv2
                import numpy as np
                import tempfile

                # Write video data to temp file (cv2 needs file path)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(file_data)
                    tmp_path = tmp_file.name

                try:
                    # Open video
                    cap = cv2.VideoCapture(tmp_path)

                    # Read first frame
                    ret, frame = cap.read()
                    cap.release()

                    if ret:
                        # Convert BGR to RGB
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        # Convert to PIL Image
                        img = Image.fromarray(frame)

                        # Generate thumbnail
                        img.thumbnail(max_size, Image.Resampling.LANCZOS)

                        # Save to bytes
                        output = BytesIO()
                        img.save(output, format='JPEG', quality=85, optimize=True)
                        thumbnail_bytes = output.getvalue()

                        return thumbnail_bytes, 'image/jpeg'
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

            except ImportError:
                logger.warning("OpenCV not available for video thumbnail generation")
            except Exception as e:
                logger.warning(f"Failed to generate video thumbnail with OpenCV: {e}")

    except Exception as e:
        logger.error(f"Error generating thumbnail: {e}")

    return None, None

def add_asset(job_id, filepath, file_type, metadata=None):
    """Add asset to database"""
    try:
        # Extract user_id from metadata or default
        user_id = 1  # Default user for testing
        if metadata and isinstance(metadata, dict):
            user_id = metadata.get('user_id', 1)
        
        filename = os.path.basename(filepath)
        
        # Read file if exists
        file_data = None
        file_size = 0
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                file_data = f.read()
            file_size = len(file_data)
        
        # Determine content type - ALWAYS detect from file, not from generic file_type parameter
        content_type = None

        # First try to guess from filename extension
        if filename:
            content_type, _ = mimetypes.guess_type(filename)

        # If that fails, detect from file signature (magic bytes)
        if not content_type and file_data and len(file_data) >= 12:
            # Check common image/video signatures
            if file_data.startswith(b'\xff\xd8\xff'):
                content_type = 'image/jpeg'
            elif file_data.startswith(b'\x89PNG\r\n\x1a\n'):
                content_type = 'image/png'
            elif file_data.startswith(b'GIF87a') or file_data.startswith(b'GIF89a'):
                content_type = 'image/gif'
            elif file_data.startswith(b'RIFF') and file_data[8:12] == b'WEBP':
                content_type = 'image/webp'
            elif file_data.startswith(b'BM'):
                content_type = 'image/bmp'
            elif file_data[4:12] == b'ftypmp42' or file_data[4:12] == b'ftypisom':
                content_type = 'video/mp4'
            elif file_data.startswith(b'\x1a\x45\xdf\xa3'):
                content_type = 'video/webm'

        # Last resort: use generic type
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Determine file type category
        file_type_category = 'other'
        if content_type:
            if content_type.startswith('image/'):
                file_type_category = 'image'
            elif content_type.startswith('video/'):
                file_type_category = 'video'
        
        # Get extension
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension.startswith('.'):
            file_extension = file_extension[1:]
        
        # Create Asset record
        asset = Asset(
            user_id=user_id,
            job_id=None,  # Don't link to jobs table for now
            filename=filename,
            file_path=filepath,
            file_type=file_type_category,
            file_size=file_size,
            file_extension=file_extension,
            source_name=metadata.get('source', 'unknown') if metadata else 'unknown',
            source_url=metadata.get('original_url', '') if metadata else '',
            downloaded_at=datetime.utcnow(),
            stored_in_db=bool(file_data),
            asset_metadata=json.dumps(metadata) if metadata else None
        )
        
        db.session.add(asset)
        db.session.flush()
        
        # Create MediaBlob if we have file data
        if file_data:
            file_hash = hashlib.sha256(file_data).hexdigest()

            # Generate thumbnail
            thumbnail_data, thumbnail_mime = generate_thumbnail(file_data, content_type)

            media_blob = MediaBlob(
                asset_id=asset.id,
                user_id=user_id,
                media_data=file_data,
                mime_type=content_type,
                file_hash=file_hash,
                thumbnail_data=thumbnail_data,
                thumbnail_mime_type=thumbnail_mime,
                created_at=datetime.utcnow()
            )
            db.session.add(media_blob)

            if thumbnail_data:
                # Mark this as a thumbnail by updating asset metadata
                metadata_dict = json.loads(asset.asset_metadata) if asset.asset_metadata else {}
                metadata_dict['has_thumbnail'] = True
                asset.asset_metadata = json.dumps(metadata_dict)
                logger.info(f"Generated thumbnail for asset {asset.id}")

        db.session.commit()
        print(f"[ASSETS] Added asset {asset.id}: {filename}")
        return str(asset.id)
        
    except Exception as e:
        print(f"[ERROR] Failed to add asset: {e}")
        db.session.rollback()
        return None

def get_assets(user_id=None, file_type=None, limit=100, offset=0):
    """Get assets from database"""
    try:
        print(f"[DEBUG] get_assets called with user_id={user_id}, file_type={file_type}, limit={limit}, offset={offset}")
        query = Asset.query.filter_by(is_deleted=False)
        
        # Only filter by user_id if specifically provided (not None)
        # This allows getting all assets when user_id is None
        if user_id is not None and user_id != "admin_all":
            print(f"[DEBUG] Filtering by user_id={user_id}")
            query = query.filter_by(user_id=user_id)
        
        if file_type:
            query = query.filter_by(file_type=file_type)
        
        query = query.order_by(Asset.downloaded_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        assets = query.all()
        print(f"[DEBUG] Found {len(assets)} assets in database")
        
        # Convert to dict format for compatibility
        result = []
        for asset in assets:
            result.append({
                'id': str(asset.id),
                'job_id': asset.job_id,
                'file_path': asset.file_path,  # Changed from 'filepath' to 'file_path'
                'filename': asset.filename,
                'file_type': f"{asset.file_type}/{asset.file_extension}" if asset.file_extension else asset.file_type,
                'file_extension': asset.file_extension or '',
                'metadata': json.loads(asset.asset_metadata) if asset.asset_metadata else {},
                'created_at': asset.downloaded_at.isoformat() if asset.downloaded_at else None,
                'file_size': asset.file_size
            })
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Failed to get assets: {e}")
        return []

def get_asset_statistics(user_id=None):
    """Get asset statistics from database"""
    try:
        query = Asset.query.filter_by(is_deleted=False)
        
        if user_id is not None and user_id != "admin_all":
            query = query.filter_by(user_id=user_id)
        
        total_count = query.count()
        
        # Count by file type
        image_count = query.filter(Asset.file_type.in_(['image', 'images'])).count()
        video_count = query.filter(Asset.file_type.in_(['video', 'videos'])).count()
        
        return {
            'total': total_count,
            'images': image_count,
            'videos': video_count,
            'all': total_count
        }
    except Exception as e:
        print(f"[ERROR] Failed to get statistics: {e}")
        return {
            'total': 0,
            'images': 0,
            'videos': 0,
            'all': 0
        }

def get_asset(asset_id):
    """Get specific asset from database"""
    try:
        asset = Asset.query.get(int(asset_id))
        if not asset or asset.is_deleted:
            return None
        
        return {
            'id': str(asset.id),
            'job_id': asset.job_id,
            'file_path': asset.file_path,  # Changed from 'filepath' to 'file_path'
            'filename': asset.filename,
            'file_type': f"{asset.file_type}/{asset.file_extension}" if asset.file_extension else asset.file_type,
            'file_extension': asset.file_extension or '',
            'metadata': json.loads(asset.asset_metadata) if asset.asset_metadata else {},
            'created_at': asset.downloaded_at.isoformat() if asset.downloaded_at else None,
            'file_size': asset.file_size
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to get asset: {e}")
        return None

def delete_asset(asset_id):
    """Delete asset from database (soft delete)"""
    try:
        asset = Asset.query.get(int(asset_id))
        if asset:
            asset.is_deleted = True
            db.session.commit()
            return True
        return False
        
    except Exception as e:
        print(f"[ERROR] Failed to delete asset: {e}")
        db.session.rollback()
        return False

def bulk_delete_assets(asset_ids, user_id=None):
    """Bulk delete assets from database and filesystem"""
    try:
        deleted_count = 0
        deleted_files = []

        for asset_id in asset_ids:
            query = Asset.query.filter_by(id=int(asset_id), is_deleted=False)
            if user_id:
                query = query.filter_by(user_id=user_id)

            asset = query.first()
            if asset:
                # Delete physical file if exists and not stored in DB
                if not asset.stored_in_db and asset.file_path and os.path.exists(asset.file_path):
                    try:
                        os.remove(asset.file_path)
                        deleted_files.append(asset.file_path)
                        logger.info(f"Deleted file: {asset.file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting file {asset.file_path}: {e}")

                # Delete MediaBlob if exists
                media_blob = MediaBlob.query.filter_by(asset_id=asset.id).first()
                if media_blob:
                    db.session.delete(media_blob)
                    logger.info(f"Deleted MediaBlob for asset {asset.id}")

                # Mark asset as deleted (soft delete)
                asset.is_deleted = True
                deleted_count += 1

        db.session.commit()
        logger.info(f"Bulk deleted {deleted_count} assets, removed {len(deleted_files)} files")
        return deleted_count

    except Exception as e:
        logger.error(f"Failed to bulk delete assets: {e}")
        db.session.rollback()
        return 0

def get_user_containers(user_id):
    """Get unique container names for a user"""
    try:
        # Get distinct folder names from file paths
        assets = Asset.query.filter_by(user_id=user_id, is_deleted=False).all()
        containers = set()
        
        for asset in assets:
            # Extract folder name from path
            if asset.file_path:
                parts = asset.file_path.split('/')
                if len(parts) > 1:
                    containers.add(parts[-2])  # Get parent folder name
        
        return sorted(list(containers))
        
    except Exception as e:
        print(f"[ERROR] Failed to get containers: {e}")
        return []

def move_assets_to_container(asset_ids, container_name, user_id=None):
    """Move assets to a different container/folder"""
    try:
        moved_count = 0
        for asset_id in asset_ids:
            query = Asset.query.filter_by(id=int(asset_id), is_deleted=False)
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            asset = query.first()
            if asset:
                # Update the path to new container
                old_path = asset.file_path
                path_parts = old_path.split('/')
                if len(path_parts) > 1:
                    path_parts[-2] = container_name
                    asset.file_path = '/'.join(path_parts)
                    moved_count += 1
        
        db.session.commit()
        return moved_count
        
    except Exception as e:
        print(f"[ERROR] Failed to move assets: {e}")
        db.session.rollback()
        return 0

def cleanup_missing_files():
    """Mark assets with missing files as deleted"""
    try:
        assets = Asset.query.filter_by(is_deleted=False).all()
        count = 0
        for asset in assets:
            if asset.file_path and not os.path.exists(asset.file_path):
                asset.is_deleted = True
                count += 1
        if count > 0:
            db.session.commit()
            print(f"[INFO] Marked {count} assets with missing files as deleted")
        
    except Exception as e:
        print(f"[ERROR] Failed to cleanup missing files: {e}")
        db.session.rollback()

def save_asset(**kwargs):
    """Save asset with flexible parameters"""
    try:
        user_id = kwargs.get('user_id', 1)
        filename = kwargs.get('filename', 'unknown')
        file_path = kwargs.get('file_path', '')
        source = kwargs.get('source', 'unknown')
        content_type = kwargs.get('content_type')
        original_url = kwargs.get('original_url', '')
        job_id = kwargs.get('job_id')
        metadata = kwargs.get('metadata', {})
        title = kwargs.get('title', '')
        
        # Read file if exists
        file_data = None
        file_size = kwargs.get('file_size', 0)
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()
            file_size = len(file_data)
        
        # Auto-detect content type - prioritize actual file detection over passed parameter
        detected_type = None

        # First try to guess from filename extension
        if filename:
            detected_type, _ = mimetypes.guess_type(filename)

        # If that fails, detect from file signature (magic bytes)
        if not detected_type and file_data and len(file_data) >= 12:
            # Check common image/video signatures
            if file_data.startswith(b'\xff\xd8\xff'):
                detected_type = 'image/jpeg'
            elif file_data.startswith(b'\x89PNG\r\n\x1a\n'):
                detected_type = 'image/png'
            elif file_data.startswith(b'GIF87a') or file_data.startswith(b'GIF89a'):
                detected_type = 'image/gif'
            elif file_data.startswith(b'RIFF') and file_data[8:12] == b'WEBP':
                detected_type = 'image/webp'
            elif file_data.startswith(b'BM'):
                detected_type = 'image/bmp'
            elif file_data[4:12] == b'ftypmp42' or file_data[4:12] == b'ftypisom':
                detected_type = 'video/mp4'
            elif file_data.startswith(b'\x1a\x45\xdf\xa3'):
                detected_type = 'video/webm'

        # Use detected type if found, otherwise use passed content_type, otherwise default
        if detected_type:
            content_type = detected_type
        elif not content_type:
            content_type = 'application/octet-stream'
        
        # Determine file type
        file_type = 'other'
        if content_type:
            if content_type.startswith('image/'):
                file_type = 'image'
            elif content_type.startswith('video/'):
                file_type = 'video'
        
        # Get extension
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension.startswith('.'):
            file_extension = file_extension[1:]
        
        # Prepare metadata
        full_metadata = metadata.copy() if metadata else {}
        if title:
            full_metadata['title'] = title
        
        # Create Asset record
        asset = Asset(
            user_id=user_id,
            job_id=None,  # Don't link to jobs table for now
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            file_extension=file_extension,
            source_url=original_url,
            source_name=source,
            downloaded_at=datetime.utcnow(),
            stored_in_db=bool(file_data),
            asset_metadata=json.dumps(full_metadata) if full_metadata else None
        )
        
        db.session.add(asset)
        db.session.flush()
        
        # Create MediaBlob if we have file data
        if file_data:
            file_hash = hashlib.sha256(file_data).hexdigest()

            # Generate thumbnail
            thumbnail_data, thumbnail_mime = generate_thumbnail(file_data, content_type)

            media_blob = MediaBlob(
                asset_id=asset.id,
                user_id=user_id,
                media_data=file_data,
                mime_type=content_type,
                file_hash=file_hash,
                thumbnail_data=thumbnail_data,
                thumbnail_mime_type=thumbnail_mime,
                created_at=datetime.utcnow()
            )
            db.session.add(media_blob)

            if thumbnail_data:
                # Mark this as a thumbnail by updating asset metadata
                metadata_dict = full_metadata.copy() if full_metadata else {}
                metadata_dict['has_thumbnail'] = True
                asset.asset_metadata = json.dumps(metadata_dict)
                logger.info(f"Generated thumbnail for asset {asset.id}")
        
        db.session.commit()
        print(f"[ASSETS] Saved asset {asset.id}: {filename} from {source}")
        return str(asset.id)
        
    except Exception as e:
        print(f"[ERROR] Failed to save asset: {e}")
        db.session.rollback()
        return None

# Create a class-like interface for compatibility
class DBAssetManager:
    """Database asset manager"""
    add_asset = staticmethod(add_asset)
    get_assets = staticmethod(get_assets)
    get_asset = staticmethod(get_asset)
    delete_asset = staticmethod(delete_asset)
    cleanup_missing_files = staticmethod(cleanup_missing_files)
    save_asset = staticmethod(save_asset)

    @staticmethod
    def get_asset_statistics(user_id=None):
        """Get statistics about assets from database"""
        try:
            query = Asset.query.filter_by(is_deleted=False)
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            # Get counts
            total_assets = query.count()
            image_count = query.filter_by(file_type='image').count()
            video_count = query.filter_by(file_type='video').count()
            other_count = total_assets - image_count - video_count
            
            # Get total size
            total_size = db.session.query(func.sum(Asset.file_size)).filter_by(is_deleted=False).scalar() or 0
            
            # Count by source
            source_counts = {}
            sources = db.session.query(Asset.source_name, func.count(Asset.id))\
                .filter_by(is_deleted=False)\
                .group_by(Asset.source_name)\
                .all()
            
            for source, count in sources:
                source_counts[source or 'unknown'] = count
            
            # Get recent assets
            recent = query.order_by(Asset.downloaded_at.desc()).limit(5).all()
            recent_assets = []
            for asset in recent:
                recent_assets.append({
                    'id': str(asset.id),
                    'filename': asset.filename,
                    'file_type': asset.file_type,
                    'source': asset.source_name,
                    'created_at': asset.downloaded_at.isoformat() if asset.downloaded_at else None,
                    'file_size': asset.file_size
                })
            
            stats = {
                'total_assets': total_assets,
                'total_images': image_count,
                'total_videos': video_count,
                'total_size': total_size,
                'by_type': {
                    'image': image_count,
                    'video': video_count,
                    'other': other_count
                },
                'by_source': source_counts,
                'recent_assets': recent_assets
            }
            
            return stats
            
        except Exception as e:
            print(f"[ERROR] Failed to get asset statistics: {e}")
            return {
                'total_assets': 0,
                'total_images': 0,
                'total_videos': 0,
                'total_size': 0,
                'by_type': {},
                'by_source': {},
                'recent_assets': []
            }

# Create instance for import
db_asset_manager = DBAssetManager()
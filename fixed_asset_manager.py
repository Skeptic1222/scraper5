"""
Fixed Database Asset Manager - Works with existing Asset model
Maps fields correctly between downloader and database models
"""

import hashlib
import json
import mimetypes
import os
from datetime import datetime

from sqlalchemy import func

from models import Asset, MediaBlob, db


class FixedAssetManager:
    """Fixed asset manager that works with existing database models"""

    @staticmethod
    def save_asset(user_id, filename, file_path, source, content_type=None,
                   original_url=None, title=None, metadata=None):
        """
        Save an asset to the database with correct field mapping
        """
        try:
            # Read file content if exists
            file_data = None
            file_size = 0

            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                file_size = len(file_data)
            else:
                print(f"[WARNING] File not found, creating reference only: {file_path}")

            # Auto-detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'

            # Determine file type category for Asset model
            file_type = 'other'
            if content_type:
                if content_type.startswith('image/'):
                    file_type = 'image'
                elif content_type.startswith('video/'):
                    file_type = 'video'
                elif content_type.startswith('audio/'):
                    file_type = 'audio'

            # Get file extension
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension.startswith('.'):
                file_extension = file_extension[1:]

            # Create Asset record with correct field names
            asset = Asset(
                user_id=user_id,
                filename=filename,
                file_path=file_path,
                file_type=file_type,
                file_size=file_size,
                file_extension=file_extension,
                source_url=original_url,  # Map original_url to source_url
                source_name=source,        # Map source to source_name
                downloaded_at=datetime.utcnow(),
                stored_in_db=bool(file_data),  # Mark if we have the actual data
                asset_metadata=json.dumps(metadata) if metadata else None
            )

            db.session.add(asset)
            db.session.flush()  # Get the asset ID

            # Create MediaBlob if we have file data
            if file_data:
                # Calculate hash
                file_hash = hashlib.sha256(file_data).hexdigest()

                media_blob = MediaBlob(
                    asset_id=asset.id,
                    user_id=user_id,
                    media_data=file_data,
                    mime_type=content_type,
                    file_hash=file_hash,
                    created_at=datetime.utcnow()
                )
                db.session.add(media_blob)

            db.session.commit()

            print(f"[SUCCESS] Asset saved: {asset.id} - {filename} ({file_size} bytes)")
            return asset

        except Exception as e:
            print(f"[ERROR] Failed to save asset: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def add_asset(job_id, filepath, file_type, metadata=None):
        """
        Add asset using job_id and filepath (compatibility wrapper for add_asset calls)
        Converts parameters to save_asset format
        """
        try:
            # Extract user_id from metadata or default
            user_id = 1  # Default user for testing
            if metadata and isinstance(metadata, dict):
                user_id = metadata.get('user_id', 1)

            filename = os.path.basename(filepath)

            # Get source and original_url from metadata
            source = metadata.get('source_name', 'unknown') if metadata else 'unknown'
            original_url = metadata.get('source_url', '') if metadata else ''
            title = metadata.get('title', '') if metadata else ''

            # Call save_asset with converted parameters
            return FixedAssetManager.save_asset(
                user_id=user_id,
                filename=filename,
                file_path=filepath,
                source=source,
                content_type=None,  # Auto-detect
                original_url=original_url,
                title=title,
                metadata=metadata
            )

        except Exception as e:
            print(f"[ERROR] Failed to add asset: {e}")
            return None

    @staticmethod
    def get_asset_content(asset_id):
        """Get the actual media content for an asset"""
        try:
            asset = Asset.query.get(asset_id)
            if not asset:
                return None, None

            # Try to get from MediaBlob first
            media_blob = MediaBlob.query.filter_by(asset_id=asset_id).first()
            if media_blob:
                return media_blob.media_data, media_blob.mime_type

            # Fallback to file system if exists
            if asset.file_path and os.path.exists(asset.file_path):
                with open(asset.file_path, 'rb') as f:
                    content_type = mimetypes.guess_type(asset.file_path)[0]
                    return f.read(), content_type

            return None, None

        except Exception as e:
            print(f"[ERROR] Failed to get asset content: {e}")
            return None, None

    @staticmethod
    def get_assets(user_id, file_type=None, limit=100, offset=0, search=None):
        """Get assets for a user with filtering"""
        try:
            query = Asset.query.filter_by(user_id=user_id, is_deleted=False)

            # Apply filters
            if file_type:
                query = query.filter_by(file_type=file_type)

            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    db.or_(
                        Asset.filename.ilike(search_term),
                        Asset.source_name.ilike(search_term)
                    )
                )

            # Order by download date (newest first)
            query = query.order_by(Asset.downloaded_at.desc())

            # Apply pagination - handle SQL Server's FETCH requirement
            if limit > 0:
                assets = query.limit(limit).offset(offset).all()
            else:
                # For limit=0, get all results without FETCH clause
                assets = query.offset(offset).all()

            # Convert to dictionaries
            result = []
            for asset in assets:
                result.append(asset.to_dict())

            return result

        except Exception as e:
            print(f"[ERROR] Failed to get assets: {e}")
            return []

    @staticmethod
    def get_asset_statistics(user_id=None):
        """Get statistics about assets"""
        try:
            query = db.session.query(Asset).filter_by(is_deleted=False)

            if user_id:
                query = query.filter_by(user_id=user_id)

            # Get counts by type
            total_assets = query.count()

            image_count = query.filter_by(file_type='image').count()
            video_count = query.filter_by(file_type='video').count()
            audio_count = query.filter_by(file_type='audio').count()
            other_count = total_assets - image_count - video_count - audio_count

            # Get total size
            total_size = db.session.query(func.sum(Asset.file_size)).filter_by(is_deleted=False).scalar() or 0
            if user_id:
                total_size = db.session.query(func.sum(Asset.file_size)).filter_by(
                    user_id=user_id, is_deleted=False
                ).scalar() or 0

            # Get counts by source
            source_counts = {}
            source_stats = db.session.query(
                Asset.source_name,
                func.count(Asset.id)
            ).filter_by(is_deleted=False)

            if user_id:
                source_stats = source_stats.filter_by(user_id=user_id)

            source_stats = source_stats.group_by(Asset.source_name).all()

            for source, count in source_stats:
                source_counts[source or 'unknown'] = count

            # Get recent assets
            recent_query = query.order_by(Asset.downloaded_at.desc()).limit(5)
            recent_assets = []
            for asset in recent_query.all():
                recent_assets.append({
                    'id': asset.id,
                    'filename': asset.filename,
                    'file_type': asset.file_type,
                    'downloaded_at': asset.downloaded_at.isoformat() if asset.downloaded_at else None
                })

            return {
                'total_assets': total_assets,
                'total_images': image_count,
                'total_videos': video_count,
                'total_audio': audio_count,
                'total_other': other_count,
                'total_size': total_size,
                'by_type': {
                    'image': image_count,
                    'video': video_count,
                    'audio': audio_count,
                    'other': other_count
                },
                'by_source': source_counts,
                'recent_assets': recent_assets,
                'storage_mode': 'database'
            }

        except Exception as e:
            print(f"[ERROR] Failed to get asset statistics: {e}")
            return {
                'total_assets': 0,
                'total_images': 0,
                'total_videos': 0,
                'total_audio': 0,
                'total_size': 0,
                'by_type': {},
                'by_source': {},
                'recent_assets': [],
                'storage_mode': 'database',
                'error': str(e)
            }

    @staticmethod
    def delete_asset(asset_id, user_id=None):
        """Soft delete an asset"""
        try:
            asset = Asset.query.get(asset_id)

            if not asset:
                return False

            # Verify ownership if user_id provided
            if user_id and asset.user_id != user_id:
                return False

            # Soft delete
            asset.is_deleted = True
            db.session.commit()

            print(f"[SUCCESS] Asset soft deleted: {asset_id}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to delete asset: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def generate_thumbnail(asset_id, max_size=(200, 200)):
        """Generate and store a thumbnail for an asset"""
        try:
            import io

            from PIL import Image

            asset = Asset.query.get(asset_id)
            if not asset or asset.file_type != 'image':
                return False

            # Get the original image data
            content, _ = FixedAssetManager.get_asset_content(asset_id)
            if not content:
                return False

            # Create thumbnail
            img = Image.open(io.BytesIO(content))
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save thumbnail to bytes
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='JPEG', quality=85, optimize=True)
            thumb_data = thumb_io.getvalue()

            # Save thumbnail path (we'll save it as a file for now)
            thumb_filename = f"thumb_{asset.id}.jpg"
            thumb_dir = os.path.join(os.path.dirname(asset.file_path), 'thumbnails')
            os.makedirs(thumb_dir, exist_ok=True)
            thumb_path = os.path.join(thumb_dir, thumb_filename)

            with open(thumb_path, 'wb') as f:
                f.write(thumb_data)

            # Update asset with thumbnail path
            asset.thumbnail_path = thumb_path
            db.session.commit()

            print(f"[SUCCESS] Generated thumbnail for asset: {asset_id}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to generate thumbnail: {e}")
            db.session.rollback()
            return False

# Create singleton instance
db_asset_manager = FixedAssetManager()

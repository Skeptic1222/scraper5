"""
Enhanced Database Asset Manager with Full Media Storage
Stores all media files directly in the database for persistence
"""

import hashlib
import json
import mimetypes
import os
from datetime import datetime

from flask import current_app
from sqlalchemy import func

from models import Asset, MediaBlob, db


class DatabaseAssetManager:
    """Manages assets with full database storage including media blobs"""

    @staticmethod
    def save_asset(user_id, filename, file_path, source, content_type=None,
                   original_url=None, title=None, metadata=None):
        """
        Save an asset to the database with its media content

        Args:
            user_id: ID of the user who owns the asset
            filename: Name of the file
            file_path: Path to the file on disk
            source: Source of the asset (e.g., 'reddit', 'youtube')
            content_type: MIME type of the file
            original_url: Original URL where the file was downloaded from
            title: Title of the asset
            metadata: Additional metadata as dict

        Returns:
            Asset object or None if failed
        """
        try:
            # Read file content
            if not os.path.exists(file_path):
                print(f"[ERROR] File not found: {file_path}")
                return None

            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Get file info
            file_size = len(file_data)

            # Auto-detect content type if not provided
            if not content_type:
                content_type, _ = mimetypes.guess_type(filename)
                if not content_type:
                    content_type = 'application/octet-stream'

            # Generate file hash for deduplication
            file_hash = hashlib.sha256(file_data).hexdigest()

            # Check if this exact file already exists for this user
            existing = Asset.query.filter_by(
                user_id=user_id,
                file_hash=file_hash
            ).first()

            if existing:
                print(f"[INFO] Asset already exists: {existing.id}")
                return existing

            # Create MediaBlob for storing file content
            media_blob = MediaBlob(
                data=file_data,
                content_type=content_type,
                file_size=file_size
            )
            db.session.add(media_blob)
            db.session.flush()  # Get the blob ID

            # Determine file type category
            file_type = 'other'
            if content_type:
                if content_type.startswith('image/'):
                    file_type = 'image'
                elif content_type.startswith('video/'):
                    file_type = 'video'
                elif content_type.startswith('audio/'):
                    file_type = 'audio'

            # Create Asset record
            asset = Asset(
                user_id=user_id,
                filename=filename,
                original_filename=filename,
                file_path=file_path,  # Keep for reference
                file_type=file_type,
                content_type=content_type,
                file_size=file_size,
                file_hash=file_hash,
                source=source,
                original_url=original_url,
                title=title or filename,
                media_blob_id=media_blob.id,
                metadata=json.dumps(metadata) if metadata else None,
                stored_in_db=True,  # Mark as stored in database
                created_at=datetime.utcnow()
            )

            db.session.add(asset)
            db.session.commit()

            print(f"[SUCCESS] Asset saved to database: {asset.id} - {filename} ({file_size} bytes)")

            # Optionally delete the file from disk after storing in DB
            if current_app.config.get('DELETE_FILES_AFTER_DB_STORAGE', True):
                try:
                    os.remove(file_path)
                    print(f"[INFO] Deleted file from disk: {file_path}")
                except:
                    pass  # File deletion is optional

            return asset

        except Exception as e:
            print(f"[ERROR] Failed to save asset: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def get_asset_content(asset_id):
        """
        Retrieve the actual media content for an asset

        Args:
            asset_id: ID of the asset

        Returns:
            Tuple of (content_bytes, content_type) or (None, None) if not found
        """
        try:
            asset = Asset.query.get(asset_id)
            if not asset:
                return None, None

            # Try to get from database blob first
            if asset.media_blob_id:
                media_blob = MediaBlob.query.get(asset.media_blob_id)
                if media_blob:
                    return media_blob.data, media_blob.content_type

            # Fallback to file system if exists
            if asset.file_path and os.path.exists(asset.file_path):
                with open(asset.file_path, 'rb') as f:
                    return f.read(), asset.content_type

            return None, None

        except Exception as e:
            print(f"[ERROR] Failed to get asset content: {e}")
            return None, None

    @staticmethod
    def get_assets(user_id, file_type=None, limit=100, offset=0, search=None):
        """
        Get assets for a user with filtering and pagination

        Args:
            user_id: User ID to get assets for
            file_type: Filter by file type ('image', 'video', 'audio', 'other')
            limit: Maximum number of assets to return
            offset: Number of assets to skip
            search: Search term for filename or title

        Returns:
            List of asset dictionaries
        """
        try:
            query = Asset.query.filter_by(user_id=user_id)

            # Apply filters
            if file_type:
                query = query.filter_by(file_type=file_type)

            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    db.or_(
                        Asset.filename.ilike(search_term),
                        Asset.title.ilike(search_term)
                    )
                )

            # Order by creation date (newest first)
            query = query.order_by(Asset.created_at.desc())

            # Apply pagination
            assets = query.limit(limit).offset(offset).all()

            # Convert to dictionaries
            result = []
            for asset in assets:
                asset_dict = {
                    'id': asset.id,
                    'filename': asset.filename,
                    'title': asset.title or asset.filename,
                    'file_type': asset.file_type,
                    'content_type': asset.content_type,
                    'file_size': asset.file_size,
                    'source': asset.source,
                    'original_url': asset.original_url,
                    'created_at': asset.created_at.isoformat() if asset.created_at else None,
                    'stored_in_db': asset.stored_in_db,
                    'has_thumbnail': bool(asset.thumbnail_blob_id),
                    'metadata': json.loads(asset.metadata) if asset.metadata else {}
                }
                result.append(asset_dict)

            return result

        except Exception as e:
            print(f"[ERROR] Failed to get assets: {e}")
            return []

    @staticmethod
    def get_asset_statistics(user_id=None):
        """
        Get statistics about assets

        Args:
            user_id: Optional user ID to filter statistics

        Returns:
            Dictionary with statistics
        """
        try:
            query = db.session.query(Asset)

            if user_id:
                query = query.filter_by(user_id=user_id)

            # Get counts by type
            total_assets = query.count()

            image_count = query.filter_by(file_type='image').count()
            video_count = query.filter_by(file_type='video').count()
            audio_count = query.filter_by(file_type='audio').count()
            other_count = query.filter_by(file_type='other').count()

            # Get total size
            total_size = db.session.query(func.sum(Asset.file_size)).scalar() or 0

            # Get counts by source
            source_counts = {}
            source_stats = db.session.query(
                Asset.source,
                func.count(Asset.id)
            ).group_by(Asset.source).all()

            for source, count in source_stats:
                source_counts[source or 'unknown'] = count

            # Get recent assets
            recent_assets = query.order_by(Asset.created_at.desc()).limit(5).all()
            recent_list = []
            for asset in recent_assets:
                recent_list.append({
                    'id': asset.id,
                    'filename': asset.filename,
                    'file_type': asset.file_type,
                    'created_at': asset.created_at.isoformat() if asset.created_at else None
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
                'recent_assets': recent_list,
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
        """
        Delete an asset and its associated media blob

        Args:
            asset_id: ID of the asset to delete
            user_id: Optional user ID for ownership verification

        Returns:
            True if deleted, False otherwise
        """
        try:
            asset = Asset.query.get(asset_id)

            if not asset:
                print(f"[WARNING] Asset not found: {asset_id}")
                return False

            # Verify ownership if user_id provided
            if user_id and asset.user_id != user_id:
                print(f"[WARNING] User {user_id} does not own asset {asset_id}")
                return False

            # Delete media blob if exists
            if asset.media_blob_id:
                media_blob = MediaBlob.query.get(asset.media_blob_id)
                if media_blob:
                    db.session.delete(media_blob)

            # Delete thumbnail blob if exists
            if asset.thumbnail_blob_id:
                thumb_blob = MediaBlob.query.get(asset.thumbnail_blob_id)
                if thumb_blob:
                    db.session.delete(thumb_blob)

            # Delete file from disk if exists
            if asset.file_path and os.path.exists(asset.file_path):
                try:
                    os.remove(asset.file_path)
                except:
                    pass

            # Delete asset record
            db.session.delete(asset)
            db.session.commit()

            print(f"[SUCCESS] Deleted asset: {asset_id}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to delete asset: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def bulk_delete_assets(asset_ids, user_id=None):
        """
        Delete multiple assets at once

        Args:
            asset_ids: List of asset IDs to delete
            user_id: Optional user ID for ownership verification

        Returns:
            Number of assets deleted
        """
        deleted_count = 0

        for asset_id in asset_ids:
            if DatabaseAssetManager.delete_asset(asset_id, user_id):
                deleted_count += 1

        return deleted_count

    @staticmethod
    def generate_thumbnail(asset_id, max_size=(200, 200)):
        """
        Generate and store a thumbnail for an asset

        Args:
            asset_id: ID of the asset
            max_size: Maximum size tuple (width, height)

        Returns:
            True if successful, False otherwise
        """
        try:
            import io

            from PIL import Image

            asset = Asset.query.get(asset_id)
            if not asset:
                return False

            # Only generate thumbnails for images
            if not asset.file_type == 'image':
                return False

            # Get the original image data
            content, _ = DatabaseAssetManager.get_asset_content(asset_id)
            if not content:
                return False

            # Create thumbnail
            img = Image.open(io.BytesIO(content))
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save thumbnail to bytes
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='JPEG', quality=85, optimize=True)
            thumb_data = thumb_io.getvalue()

            # Store thumbnail in database
            thumb_blob = MediaBlob(
                data=thumb_data,
                content_type='image/jpeg',
                file_size=len(thumb_data)
            )
            db.session.add(thumb_blob)
            db.session.flush()

            # Update asset with thumbnail reference
            asset.thumbnail_blob_id = thumb_blob.id
            db.session.commit()

            print(f"[SUCCESS] Generated thumbnail for asset: {asset_id}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to generate thumbnail: {e}")
            db.session.rollback()
            return False

# Create singleton instance
db_asset_manager = DatabaseAssetManager()

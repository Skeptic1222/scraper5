"""
Fixed Search and Download Endpoints
Simplified, working implementation that actually downloads media
"""

from flask import Blueprint, jsonify, request, session
from flask_login import current_user

from working_media_downloader import media_downloader

try:
    from fixed_asset_manager import db_asset_manager
    print("[IMPORT] Using fixed asset manager")
except ImportError:
    from database_asset_manager import db_asset_manager
    print("[IMPORT] Using original database asset manager")
import threading

from db_job_manager import db_job_manager

# Create blueprint
search_download_bp = Blueprint('search_download', __name__)

@search_download_bp.route('/api/search', methods=['POST'])
def search_media():
    """
    Search for media and download it
    Actually works and downloads real files
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        sources = data.get('sources', ['unsplash', 'pexels', 'pixabay'])
        limit = min(data.get('limit', 10), 50)  # Max 50 items
        safe_search = data.get('safe_search', True)

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Get user ID if authenticated
        user_id = None
        if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user_id = current_user.id
        elif 'user_id' in session:
            user_id = session['user_id']
        else:
            # Create a guest user ID
            user_id = 1  # Default user for testing

        # Create a job to track progress
        job_id = db_job_manager.create_job('search', {
            'query': query,
            'sources': sources,
            'limit': limit,
            'user_id': user_id
        })

        # Update job status
        db_job_manager.update_job(job_id,
            status='running',
            message=f'Searching for "{query}"...'
        )

        # Start download in background
        def download_task():
            try:
                # Progress callback
                def progress_callback(message):
                    db_job_manager.update_job(job_id, message=message)

                # Search and download
                results = media_downloader.search_and_download(
                    query=query,
                    sources=sources,
                    limit=limit,
                    safe_search=safe_search,
                    progress_callback=progress_callback,
                    user_id=user_id
                )

                # Save assets to database
                saved_count = 0
                for file_info in results.get('downloaded', []):
                    try:
                        # Save to database with blob storage
                        asset = db_asset_manager.save_asset(
                            user_id=user_id,
                            filename=file_info['filename'],
                            file_path=file_info['filepath'],
                            source=file_info['source'],
                            content_type=file_info.get('content_type', 'image/jpeg'),
                            original_url=file_info.get('original_url'),
                            title=file_info.get('title', query),
                            metadata={
                                'query': query,
                                'downloaded_at': file_info.get('downloaded_at')
                            }
                        )

                        if asset:
                            saved_count += 1
                            # Generate thumbnail for images
                            if asset.file_type == 'image':
                                db_asset_manager.generate_thumbnail(asset.id)

                    except Exception as e:
                        print(f"[ERROR] Failed to save asset: {e}")

                # Update job with results
                db_job_manager.update_job(job_id,
                    status='completed',
                    message=f'Downloaded {saved_count} items for "{query}"',
                    progress=100,
                    downloaded=saved_count,
                    detected=results.get('total', 0)
                )

            except Exception as e:
                print(f"[ERROR] Download task failed: {e}")
                db_job_manager.update_job(job_id,
                    status='failed',
                    message=f'Error: {str(e)}',
                    progress=0
                )

        # Start background task
        thread = threading.Thread(target=download_task)
        thread.daemon = True
        thread.start()

        # Return job ID immediately
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Search started for "{query}"'
        })

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return jsonify({'error': str(e)}), 500

@search_download_bp.route('/api/download-url', methods=['POST'])
def download_url():
    """
    Download media from a direct URL
    """
    try:
        data = request.get_json()
        url = data.get('url', '')
        title = data.get('title', 'Download')

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Get user ID
        user_id = None
        if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user_id = current_user.id
        elif 'user_id' in session:
            user_id = session['user_id']
        else:
            user_id = 1  # Default user

        # Download the file
        file_info = media_downloader.download_direct_url(
            url=url,
            title=title,
            source='direct',
            user_id=user_id
        )

        if file_info:
            # Save to database
            asset = db_asset_manager.save_asset(
                user_id=user_id,
                filename=file_info['filename'],
                file_path=file_info['filepath'],
                source=file_info['source'],
                content_type=file_info.get('content_type', 'application/octet-stream'),
                original_url=url,
                title=title,
                metadata={'downloaded_at': file_info.get('downloaded_at')}
            )

            if asset:
                # Generate thumbnail for images
                if asset.file_type == 'image':
                    db_asset_manager.generate_thumbnail(asset.id)

                return jsonify({
                    'success': True,
                    'asset_id': asset.id,
                    'filename': asset.filename,
                    'message': f'Downloaded {asset.filename}'
                })

        return jsonify({'error': 'Download failed'}), 500

    except Exception as e:
        print(f"[ERROR] URL download failed: {e}")
        return jsonify({'error': str(e)}), 500

@search_download_bp.route('/api/job/<job_id>/status')
def get_job_status(job_id):
    """Get the status of a download job"""
    try:
        job = db_job_manager.get_job(job_id)

        if not job:
            return jsonify({'error': 'Job not found'}), 404

        return jsonify({
            'success': True,
            'job': {
                'id': job_id,
                'status': job.get('status', 'unknown'),
                'progress': job.get('progress', 0),
                'message': job.get('message', ''),
                'downloaded': job.get('downloaded', 0),
                'detected': job.get('detected', 0)
            }
        })

    except Exception as e:
        print(f"[ERROR] Failed to get job status: {e}")
        return jsonify({'error': str(e)}), 500

@search_download_bp.route('/api/assets')
def get_assets():
    """Get user's assets from database"""
    try:
        # Get user ID
        user_id = None
        if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user_id = current_user.id
        elif 'user_id' in session:
            user_id = session['user_id']
        else:
            user_id = 1  # Default user

        # Get parameters
        file_type = request.args.get('type')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        search = request.args.get('search')

        # Get assets from database
        assets = db_asset_manager.get_assets(
            user_id=user_id,
            file_type=file_type,
            limit=limit,
            offset=offset,
            search=search
        )

        # Get statistics
        stats = db_asset_manager.get_asset_statistics(user_id=user_id)

        return jsonify({
            'success': True,
            'assets': assets,
            'statistics': stats,
            'total': stats.get('total_assets', 0)
        })

    except Exception as e:
        print(f"[ERROR] Failed to get assets: {e}")
        return jsonify({'error': str(e)}), 500

@search_download_bp.route('/api/asset/<int:asset_id>')
def get_asset(asset_id):
    """Get a specific asset's media content"""
    try:
        import io

        from flask import send_file

        # Get the asset content
        content, content_type = db_asset_manager.get_asset_content(asset_id)

        if not content:
            return jsonify({'error': 'Asset not found'}), 404

        # Send the file
        return send_file(
            io.BytesIO(content),
            mimetype=content_type or 'application/octet-stream',
            as_attachment=False
        )

    except Exception as e:
        print(f"[ERROR] Failed to get asset: {e}")
        return jsonify({'error': str(e)}), 500

@search_download_bp.route('/api/asset/<int:asset_id>/thumbnail')
def get_asset_thumbnail(asset_id):
    """Get a thumbnail for an asset"""
    try:
        import io

        from flask import send_file

        from models import Asset, MediaBlob

        # Get the asset
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({'error': 'Asset not found'}), 404

        # Get thumbnail if exists
        if asset.thumbnail_blob_id:
            thumb_blob = MediaBlob.query.get(asset.thumbnail_blob_id)
            if thumb_blob:
                return send_file(
                    io.BytesIO(thumb_blob.data),
                    mimetype=thumb_blob.content_type or 'image/jpeg',
                    as_attachment=False
                )

        # Return original if no thumbnail
        content, content_type = db_asset_manager.get_asset_content(asset_id)

        if not content:
            return jsonify({'error': 'Content not found'}), 404

        return send_file(
            io.BytesIO(content),
            mimetype=content_type or 'application/octet-stream',
            as_attachment=False
        )

    except Exception as e:
        print(f"[ERROR] Failed to get thumbnail: {e}")
        return jsonify({'error': str(e)}), 500

@search_download_bp.route('/api/asset/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    """Delete an asset"""
    try:
        # Get user ID
        user_id = None
        if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user_id = current_user.id
        elif 'user_id' in session:
            user_id = session['user_id']

        # Delete the asset
        success = db_asset_manager.delete_asset(asset_id, user_id)

        if success:
            return jsonify({'success': True, 'message': 'Asset deleted'})
        else:
            return jsonify({'error': 'Failed to delete asset'}), 400

    except Exception as e:
        print(f"[ERROR] Failed to delete asset: {e}")
        return jsonify({'error': str(e)}), 500

"""
Search API Blueprint - Handles search and download requests
"""
import asyncio
import logging
import os
import time
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import Asset, ScrapeJob

from ..models.method_config import SmartMethodSelector, db
from ..scrapers import registry
from ..services.method_fallback import MethodFallbackSystem

logger = logging.getLogger(__name__)

# DISABLED: Conflicts with blueprints/search.py - both register as 'search' blueprint
# This async implementation doesn't work in WSGI/FastCGI environment
# TODO: Merge functionality into blueprints/search.py or convert to use threading
search_bp = Blueprint('search_async_DISABLED', __name__)

# Initialize fallback system
fallback_system = MethodFallbackSystem()


@search_bp.route('/search', methods=['POST'])
@login_required
async def search():
    """
    Unified search endpoint
    
    Request JSON:
    {
        "query": "search term",
        "sources": ["reddit", "youtube", "google"],
        "max_results": 20,
        "safe_search": true,
        "media_type": "image"
    }
    """
    try:
        data = request.json
        query = data.get('query')
        sources = data.get('sources', [])
        max_results = data.get('max_results', 20)
        safe_search = data.get('safe_search', True)
        media_type = data.get('media_type')

        if not query:
            return jsonify({'success': False, 'error': 'Query required'}), 400

        # Create job record
        job = ScrapeJob(
            user_id=current_user.id,
            source='multi',
            query=query,
            status='processing',
            total_items=0,
            processed_items=0
        )
        db.session.add(job)
        db.session.commit()

        # Search across sources
        all_results = {}
        total_found = 0

        for source_id in sources:
            try:
                # Get scraper
                scraper = registry.get_scraper(source_id)

                # Check if user has access to this source
                if scraper.NSFW and not current_user.can_access_nsfw():
                    logger.info(f"User {current_user.email} denied access to NSFW source {source_id}")
                    continue

                # Progress callback
                def progress_callback(message):
                    job.progress_message = message
                    db.session.commit()

                # Search with the scraper
                logger.info(f"Searching {source_id} for: {query}")

                # Run async search
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None,
                    scraper.search,
                    query,
                    max_results,
                    safe_search,
                    media_type,
                    progress_callback
                )

                # Store results
                all_results[source_id] = [r.to_dict() for r in results]
                total_found += len(results)

                # Save assets to database
                for item in results:
                    asset = Asset(
                        user_id=current_user.id,
                        job_id=job.id,
                        source=source_id,
                        url=item.url,
                        title=item.title,
                        thumbnail=item.thumbnail,
                        media_type=item.media_type.value,
                        metadata=str(item.metadata)
                    )
                    db.session.add(asset)

            except Exception as e:
                logger.error(f"Search failed for {source_id}: {e}")
                all_results[source_id] = {'error': str(e)}

        # Update job
        job.status = 'completed'
        job.total_items = total_found
        job.processed_items = total_found
        job.completed_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'job_id': job.id,
            'results': all_results,
            'total': total_found
        })

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@search_bp.route('/download', methods=['POST'])
@login_required
async def download():
    """
    Download media from URL with smart method selection
    
    Request JSON:
    {
        "url": "https://example.com/media",
        "quality": "best",
        "source": "reddit"  // Optional, will auto-detect
    }
    """
    try:
        data = request.json
        url = data.get('url')
        quality = data.get('quality', 'best')
        source = data.get('source')

        if not url:
            return jsonify({'success': False, 'error': 'URL required'}), 400

        # Check user credits
        if current_user.credits <= 0:
            return jsonify({'success': False, 'error': 'Insufficient credits'}), 403

        # Create job
        job = ScrapeJob(
            user_id=current_user.id,
            source=source or 'unknown',
            query=url,
            status='processing'
        )
        db.session.add(job)
        db.session.commit()

        # Generate output path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{uuid.uuid4().hex[:8]}_{timestamp}"
        output_dir = os.path.join('downloads', str(current_user.id))
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

        # Progress callback
        def progress_callback(message):
            job.progress_message = message
            db.session.commit()

        start_time = time.time()

        # Try smart method selection first
        if source:
            best_method = SmartMethodSelector.get_best_method(source, url)

            if best_method:
                logger.info(f"Using known best method: {best_method} for {source}")

                try:
                    scraper = registry.get_scraper(source)

                    # Find and execute the specific method
                    for method in scraper.methods:
                        if method.name == best_method:
                            loop = asyncio.get_event_loop()
                            result = await loop.run_in_executor(
                                None,
                                method.function,
                                url,
                                output_path,
                                progress_callback
                            )

                            if result:
                                response_time = time.time() - start_time
                                SmartMethodSelector.record_attempt(
                                    source, url, best_method, True, response_time
                                )

                                # Save asset
                                _save_download_asset(job, url, output_path, source)

                                return jsonify({
                                    'success': True,
                                    'job_id': job.id,
                                    'file_path': output_path,
                                    'method_used': best_method
                                })

                except Exception as e:
                    logger.warning(f"Best method {best_method} failed: {e}")
                    SmartMethodSelector.record_attempt(source, url, best_method, False)

        # Fallback to trying all methods
        logger.info(f"Using fallback system for {url}")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            fallback_system.download,
            url,
            output_path,
            progress_callback
        )

        if result['success']:
            response_time = time.time() - start_time

            # Record successful method
            if source:
                SmartMethodSelector.record_attempt(
                    source, url, result['method'], True, response_time
                )

            # Save asset
            _save_download_asset(job, url, result['file_path'], source or 'unknown')

            # Deduct credit
            current_user.credits -= 1
            db.session.commit()

            return jsonify({
                'success': True,
                'job_id': job.id,
                'file_path': result['file_path'],
                'method_used': result['method']
            })
        else:
            job.status = 'failed'
            job.error_message = result.get('error', 'All methods failed')
            db.session.commit()

            return jsonify({
                'success': False,
                'error': result.get('error', 'Download failed')
            }), 500

    except Exception as e:
        logger.error(f"Download error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@search_bp.route('/extract', methods=['POST'])
@login_required
async def extract_info():
    """
    Extract media information without downloading
    
    Request JSON:
    {
        "url": "https://example.com/media"
    }
    """
    try:
        data = request.json
        url = data.get('url')

        if not url:
            return jsonify({'success': False, 'error': 'URL required'}), 400

        # Try to detect source
        source = None
        for scraper_info in registry.list_scrapers():
            scraper = registry.get_scraper(scraper_info['id'])
            if scraper.validate_url(url):
                source = scraper_info['id']
                break

        if not source:
            return jsonify({'success': False, 'error': 'Unsupported URL'}), 400

        # Extract info
        scraper = registry.get_scraper(source)

        loop = asyncio.get_event_loop()
        media_item = await loop.run_in_executor(
            None,
            scraper.extract_media_info,
            url
        )

        if media_item:
            return jsonify({
                'success': True,
                'media': media_item.to_dict(),
                'source': source
            })
        else:
            return jsonify({'success': False, 'error': 'Could not extract media info'}), 404

    except Exception as e:
        logger.error(f"Extract error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@search_bp.route('/jobs/<int:job_id>')
@login_required
def get_job_status(job_id):
    """Get job status and progress"""
    job = ScrapeJob.query.filter_by(id=job_id, user_id=current_user.id).first()

    if not job:
        return jsonify({'success': False, 'error': 'Job not found'}), 404

    return jsonify({
        'success': True,
        'job': {
            'id': job.id,
            'status': job.status,
            'progress': job.get_progress(),
            'message': job.progress_message,
            'total_items': job.total_items,
            'processed_items': job.processed_items,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        }
    })


def _save_download_asset(job, url, file_path, source):
    """Save downloaded asset to database"""
    try:
        # Get file info
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        asset = Asset(
            user_id=job.user_id,
            job_id=job.id,
            source=source,
            url=url,
            file_path=file_path,
            file_size=file_size,
            media_type='unknown',  # Will be detected later
            created_at=datetime.utcnow()
        )
        db.session.add(asset)

        # Update job
        job.status = 'completed'
        job.total_items = 1
        job.processed_items = 1
        job.completed_at = datetime.utcnow()

        db.session.commit()

    except Exception as e:
        logger.error(f"Failed to save asset: {e}")


# Export blueprint
__all__ = ['search_bp']

#!/usr/bin/env python3
"""
Enhanced Media Scraper Web Application - Professional Interface
Flask web application with comprehensive source management, asset organization, and real-time progress tracking
"""

import os
import json
import time
import threading
import uuid
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory
from real_content_downloader import (
    download_images_simple, 
    enhanced_social_scrape,
    enhanced_instagram_scrape,
    enhanced_twitter_scrape,
    enhanced_tiktok_scrape,
    comprehensive_multi_source_scrape,
    get_content_sources,
    test_with_known_working_content
)
from urllib.parse import unquote
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join

app = Flask(__name__)
# SECURITY FIX: Use environment variable with secure fallback
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Global variables for job management
active_jobs = {}
job_results = {}

class JobManager:
    """Manages background scraping jobs with progress tracking"""
    
    def __init__(self):
        self.jobs = {}
        self.results = {}
    
    def create_job(self, job_type, params):
        job_id = f"{job_type}_{int(time.time() * 1000)}"
        
        job_data = {
            'id': job_id,
            'type': job_type,
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing...',
            'detected': 0,
            'downloaded': 0,
            'failed': 0,
            'images': 0,
            'videos': 0,
            'current_file': '',
            'recent_files': [],
            'sources': {},
            'params': params,
            'start_time': datetime.now(),
            'end_time': None,
            'live_updates': []
        }
        
        self.jobs[job_id] = job_data
        return job_id
    
    def update_job(self, job_id, **updates):
        if job_id in self.jobs:
            self.jobs[job_id].update(updates)
            
            # Add to live updates if message provided
            if 'message' in updates:
                timestamp = datetime.now().strftime('%H:%M:%S')
                live_update = {
                    'timestamp': timestamp,
                    'message': updates['message']
                }
                self.jobs[job_id]['live_updates'].insert(0, live_update)
                
                # Keep only last 20 updates
                if len(self.jobs[job_id]['live_updates']) > 20:
                    self.jobs[job_id]['live_updates'] = self.jobs[job_id]['live_updates'][:20]
    
    def add_progress_update(self, job_id, message, progress, downloaded, images, videos, current_file=None):
        """Add detailed progress update with counters"""
        if job_id in self.jobs:
            update_data = {
                'message': message,
                'progress': progress,
                'downloaded': downloaded,
                'images': images,
                'videos': videos
            }
            
            if current_file:
                update_data['current_file'] = current_file
                # Add to recent files
                if current_file not in self.jobs[job_id]['recent_files']:
                    self.jobs[job_id]['recent_files'].insert(0, current_file)
                    # Keep only last 10 files
                    if len(self.jobs[job_id]['recent_files']) > 10:
                        self.jobs[job_id]['recent_files'] = self.jobs[job_id]['recent_files'][:10]
            
            self.update_job(job_id, **update_data)
    
    def get_job_status(self, job_id):
        return self.jobs.get(job_id, {'status': 'not_found'})
    
    def complete_job(self, job_id, results):
        if job_id in self.jobs:
            self.jobs[job_id].update({
                'status': 'completed',
                'progress': 100,
                'end_time': datetime.now(),
                'results': results
            })
            self.results[job_id] = results

job_manager = JobManager()

def create_progress_callback(job_id):
    """Create a progress callback function for a specific job"""
    def progress_callback(message, progress, downloaded, images, videos, current_file=None):
        try:
            job_manager.add_progress_update(job_id, message, progress, downloaded, images, videos, current_file)
        except Exception as e:
            # Log error but don't crash the download process
            print(f"⚠️ Progress callback error for job {job_id}: {str(e)[:100]}")
    return progress_callback

def run_comprehensive_search_job(job_id, query, search_type, max_content, enabled_sources, safe_search=True):
    """Run comprehensive search in background thread with safe search support"""
    try:
        progress_callback = create_progress_callback(job_id)
        
        job_manager.update_job(job_id, status='running', message=f'Starting comprehensive search (Safe search: {"ON" if safe_search else "OFF"})...')
        
        # Execute the comprehensive search with progress tracking and safe search
        results = comprehensive_multi_source_scrape(
            query=query,
            enabled_sources=enabled_sources,
            max_content_per_source=max_content,
            output_dir="downloads",
            progress_callback=progress_callback,
            safe_search=safe_search  # Pass safe search parameter
        )
        
        # Update job with final results
        job_manager.update_job(
            job_id,
            status='completed',
            progress=100,
            message=f'Search completed successfully! (Safe search: {"ON" if safe_search else "OFF"})',
            detected=results.get('total_detected', 0),
            downloaded=results.get('total_downloaded', 0),
            images=results.get('total_images', 0),
            videos=results.get('total_videos', 0),
            sources=results.get('sources', {}),
            results=results
        )
        
    except Exception as e:
        job_manager.update_job(
            job_id,
            status='error',
            message=f'Error: {str(e)[:200]}',
            progress=0
        )

def run_instagram_search_job(job_id, username, max_content):
    """Run Instagram-specific search in background thread"""
    try:
        progress_callback = create_progress_callback(job_id)
        
        job_manager.update_job(job_id, status='running', message=f'Scraping Instagram @{username}...')
        
        results = enhanced_instagram_scrape(
            username_or_url=username,
            max_content=max_content,
            output_dir="downloads",
            progress_callback=progress_callback
        )
        
        downloaded_count = results.get('downloaded', 0)
        images = results.get('images', 0)
        videos = results.get('videos', 0)
        
        job_manager.update_job(
            job_id,
            status='completed',
            progress=100,
            message=f'Instagram scraping completed! Downloaded {downloaded_count} files ({images} images, {videos} videos)',
            downloaded=downloaded_count,
            images=images,
            videos=videos,
            detected=downloaded_count  # For Instagram, assume all detected were attempted
        )
        
    except Exception as e:
        job_manager.update_job(
            job_id,
            status='error',
            message=f'Instagram error: {str(e)[:200]}',
            progress=0
        )

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/test-ui')
def test_ui():
    """UI functionality test page"""
    return send_from_directory('.', 'test_ui_functionality.html')

@app.route('/api/sources')
def get_sources():
    """Get available content sources with categories and safe search filtering"""
    try:
        sources = get_content_sources()
        safe_search = request.args.get('safe_search', 'true').lower() == 'true'
        
        # Organize sources by category
        categorized = {
            'social': [],
            'search': [],
            'art': [],
            'video': [],
            'gallery': [],
            'stock': [],
            'direct': [],
            'adult': []  # NEW: Adult content category
        }
        
        for source_name, source_obj in sources.items():
            # Skip adult content sources if safe search is enabled
            if safe_search and source_obj.requires_no_safe_search:
                continue
                
            category = source_obj.category
            if category == 'general':
                category = 'search'  # Default mapping
            
            source_data = {
                'name': source_name,
                'display_name': source_obj.display_name,
                'enabled': source_obj.enabled,
                'category': category,
                'requires_no_safe_search': source_obj.requires_no_safe_search
            }
            
            if category in categorized:
                categorized[category].append(source_data)
            else:
                categorized['search'].append(source_data)  # Fallback
        
        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}
        
        return jsonify({
            'success': True,
            'sources': categorized,
            'safe_search_enabled': safe_search,
            'adult_sources_available': not safe_search
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/comprehensive-search', methods=['POST'])
def start_comprehensive_search():
    """Start comprehensive search across multiple sources with safe search controls"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        search_type = data.get('search_type', 'comprehensive')
        max_content = int(data.get('max_content', 25))
        enabled_sources = data.get('enabled_sources', [])
        safe_search = data.get('safe_search', True)  # NEW: Safe search parameter
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'})
        
        # Filter out adult sources if safe search is enabled
        if safe_search:
            sources = get_content_sources()
            enabled_sources = [source for source in enabled_sources 
                             if not sources.get(source, {}).get('requires_no_safe_search', False)]
        
        # Create background job
        job_id = job_manager.create_job('comprehensive_search', {
            'query': query,
            'search_type': search_type,
            'max_content': max_content,
            'enabled_sources': enabled_sources,
            'safe_search': safe_search
        })
        
        # Start background thread
        thread = threading.Thread(
            target=run_comprehensive_search_job,
            args=(job_id, query, search_type, max_content, enabled_sources, safe_search)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Comprehensive search started (Safe search: {"ON" if safe_search else "OFF"})',
            'safe_search_enabled': safe_search
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/instagram-search', methods=['POST'])
def start_instagram_search():
    """Start Instagram-specific search"""
    try:
        data = request.json
        username = data.get('username', '').strip().replace('@', '')
        max_content = int(data.get('max_content', 25))
        
        if not username:
            return jsonify({'success': False, 'error': 'Username is required'})
        
        # Create background job
        job_id = job_manager.create_job('instagram_search', {
            'username': username,
            'max_content': max_content
        })
        
        # Start background thread
        thread = threading.Thread(
            target=run_instagram_search_job,
            args=(job_id, username, max_content)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Instagram search started for @{username}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/job-status/<job_id>')
def get_job_status(job_id):
    """Get status of a background job"""
    try:
        status = job_manager.get_job_status(job_id)
        
        # Add runtime information
        if 'start_time' in status:
            runtime = datetime.now() - status['start_time']
            status['runtime_seconds'] = int(runtime.total_seconds())
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting job status: {str(e)}'
        })

@app.route('/api/assets')
def get_assets():
    """Get all downloaded assets with metadata"""
    try:
        assets = []
        downloads_dir = "downloads"
        
        if os.path.exists(downloads_dir):
            for root, dirs, files in os.walk(downloads_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, downloads_dir)
                    
                    # Get file info
                    try:
                        stat = os.stat(file_path)
                        file_size = stat.st_size
                        modified_time = datetime.fromtimestamp(stat.st_mtime)
                        
                        # Determine file type
                        file_type = 'unknown'
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            file_type = 'image'
                        elif file.lower().endswith(('.mp4', '.avi', '.mov', '.webm', '.mkv')):
                            file_type = 'video'
                        elif file.lower().endswith(('.mp3', '.wav', '.flac', '.m4a')):
                            file_type = 'audio'
                        
                        asset_data = {
                            'name': file,
                            'path': relative_path.replace('\\', '/'),  # Normalize path separators
                            'size': file_size,
                            'type': file_type,
                            'modified': modified_time.isoformat(),
                            'source_dir': os.path.basename(root) if root != downloads_dir else 'root'
                        }
                        
                        assets.append(asset_data)
                        
                    except Exception as e:
                        continue  # Skip files that can't be accessed
        
        # Sort by modification time (newest first)
        assets.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            'success': True,
            'assets': assets,
            'total_count': len(assets),
            'total_size': sum(asset['size'] for asset in assets)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/assets/<path:asset_path>', methods=['DELETE'])
def delete_asset(asset_path):
    """Delete a specific asset"""
    try:
        full_path = os.path.join("downloads", asset_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            os.remove(full_path)
            return jsonify({
                'success': True,
                'message': f'Asset {asset_path} deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Asset not found'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/downloads/<path:filename>')
def serve_download(filename):
    """Serve downloaded files with security validation and special character handling"""
    try:
        import os.path
        
        # FIX: Decode URL-encoded filename (e.g., %23 -> #, %20 -> space)
        decoded_filename = unquote(filename)
        
        # For file existence checks, use normalized path (Windows style)
        normalized_path = os.path.normpath(decoded_filename)
        full_path = os.path.join('downloads', normalized_path)
        
        # Check for directory traversal attempts
        if normalized_path.startswith('..') or os.path.isabs(normalized_path):
            return jsonify({'error': 'Invalid file path'}), 403
            
        # Additional security: ensure path doesn't contain dangerous patterns
        dangerous_patterns = ['../', '..\\', '../', '..\\']
        if any(pattern in decoded_filename for pattern in dangerous_patterns):
            return jsonify({'error': 'Invalid file path'}), 403
        
        # Verify file exists first
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            return jsonify({'error': 'File not found'}), 404
        
        # CRITICAL FIX: Use Flask's safe_join for proper path handling
        # This handles special characters better than send_from_directory alone
        downloads_dir = os.path.abspath('downloads')
        
        # Convert to forward slashes for Flask and use safe_join
        flask_path = decoded_filename.replace('\\', '/')
        safe_path = safe_join(downloads_dir, flask_path)
        
        if safe_path is None or not os.path.exists(safe_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Use send_file with absolute path for better special character handling
        from flask import send_file
        return send_file(safe_path)
        
    except Exception as e:
        # For debugging: log the actual error
        print(f"File serving error: {str(e)}")
        print(f"Requested filename: {filename}")
        print(f"Decoded filename: {unquote(filename) if 'filename' in locals() else 'N/A'}")
        return jsonify({'error': 'File not found'}), 404

@app.route('/test-system')
def test_system():
    """Test system functionality"""
    try:
        # Run the test function
        test_results = test_with_known_working_content()
        
        system_status = {
            'system_working': test_results.get('success', False),
            'message': f"Downloaded {test_results.get('total_files', 0)} test files",
            'details': {
                'youtube_files': test_results.get('youtube', 0),
                'image_files': test_results.get('images', 0),
                'total_files': test_results.get('total_files', 0)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(system_status)
        
    except Exception as e:
        return jsonify({
            'system_working': False,
            'message': f'System test failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/download-images', methods=['POST'])
def download_images():
    """Enhanced image download endpoint with safe search controls"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        max_images = int(data.get('max_images', 10))
        safe_search = data.get('safe_search', True)  # NEW: Safe search parameter
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'})
        
        # Create background job for real-time progress
        job_id = job_manager.create_job('image_download', {
            'query': query,
            'max_images': max_images,
            'safe_search': safe_search
        })
        
        def run_image_download():
            try:
                progress_callback = create_progress_callback(job_id)
                
                # Use the enhanced download function with safe search parameter
                results = download_images_simple(
                    query=query,
                    max_images=max_images,
                    output_dir="downloads",
                    safe_search=safe_search,
                    progress_callback=progress_callback
                )
                
                downloaded_count = results.get('downloaded', 0)
                images = results.get('images', 0)
                videos = results.get('videos', 0)
                
                job_manager.update_job(
                    job_id,
                    status='completed',
                    progress=100,
                    message=f'Downloaded {downloaded_count} files for "{query}" ({images} images, {videos} videos) - Safe search: {"ON" if safe_search else "OFF"}',
                    downloaded=downloaded_count,
                    images=images,
                    videos=videos
                )
                
            except Exception as e:
                job_manager.update_job(
                    job_id,
                    status='error',
                    message=f'Image download error: {str(e)[:200]}',
                    progress=0
                )
        
        # Start background thread
        import threading
        thread = threading.Thread(target=run_image_download)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Image download started for "{query}" (Safe search: {"ON" if safe_search else "OFF"})',
            'safe_search_enabled': safe_search
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/scrape-social', methods=['POST'])
def scrape_social():
    """Enhanced social media scraping endpoint"""
    try:
        data = request.json
        url = data.get('url', '').strip()
        max_content = int(data.get('max_content', 5))
        aggressive = data.get('aggressive', False)
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        # Create background job for real-time progress
        job_id = job_manager.create_job('social_scrape', {
            'url': url,
            'max_content': max_content,
            'aggressive': aggressive
        })
        
        def run_social_scrape():
            try:
                progress_callback = create_progress_callback(job_id)
                
                # Determine platform and use appropriate scraper
                results = {'downloaded': 0, 'images': 0, 'videos': 0}
                
                if 'instagram.com' in url:
                    results = enhanced_instagram_scrape(
                        username_or_url=url,
                        max_content=max_content,
                        output_dir="downloads",
                        progress_callback=progress_callback
                    )
                elif 'twitter.com' in url or 'x.com' in url:
                    downloaded_count = enhanced_twitter_scrape(
                        username_or_url=url,
                        max_content=max_content,
                        output_dir="downloads"
                    )
                    results = {'downloaded': downloaded_count, 'images': downloaded_count, 'videos': 0}
                elif 'tiktok.com' in url:
                    downloaded_count = enhanced_tiktok_scrape(
                        username_or_url=url,
                        max_content=max_content,
                        output_dir="downloads"
                    )
                    results = {'downloaded': downloaded_count, 'images': 0, 'videos': downloaded_count}
                else:
                    # Fallback to general social scraping
                    downloaded_count = enhanced_social_scrape(
                        url=url,
                        max_content=max_content,
                        output_dir="downloads",
                        aggressive=aggressive
                    )
                    results = {'downloaded': downloaded_count, 'images': downloaded_count // 2, 'videos': downloaded_count // 2}
                
                downloaded_count = results.get('downloaded', 0)
                images = results.get('images', 0)
                videos = results.get('videos', 0)
                
                job_manager.update_job(
                    job_id,
                    status='completed',
                    progress=100,
                    message=f'Downloaded {downloaded_count} items from {url} ({images} images, {videos} videos)',
                    downloaded=downloaded_count,
                    images=images,
                    videos=videos
                )
                
            except Exception as e:
                job_manager.update_job(
                    job_id,
                    status='error',
                    message=f'Social scrape error: {str(e)[:200]}',
                    progress=0
                )
        
        # Start background thread
        import threading
        thread = threading.Thread(target=run_social_scrape)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Social media scraping started for {url}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/keyword-scrape', methods=['POST'])
def keyword_scrape():
    """Comprehensive keyword-based scraping"""
    try:
        data = request.json
        keyword = data.get('keyword', '').strip()
        platforms = data.get('platforms', ['all'])
        max_per_platform = int(data.get('max_per_platform', 10))
        
        if not keyword:
            return jsonify({'success': False, 'error': 'Keyword is required'})
        
        # Create background job for real-time progress
        job_id = job_manager.create_job('keyword_scrape', {
            'keyword': keyword,
            'platforms': platforms,
            'max_per_platform': max_per_platform
        })
        
        def run_keyword_scrape():
            try:
                progress_callback = create_progress_callback(job_id)
                
                results = {
                    'keyword': keyword,
                    'platforms_searched': [],
                    'total_downloaded': 0,
                    'total_images': 0,
                    'total_videos': 0,
                    'platform_results': {}
                }
                
                # Image search
                if 'all' in platforms or 'images' in platforms:
                    try:
                        download_results = download_images_simple(
                            query=keyword,
                            max_images=max_per_platform,
                            output_dir=f"downloads/keyword_scraping/{keyword}/images",
                            safe_search=False,
                            progress_callback=progress_callback
                        )
                        
                        img_count = download_results.get('downloaded', 0)
                        images = download_results.get('images', 0)
                        videos = download_results.get('videos', 0)
                        
                        results['platform_results']['images'] = {
                            'downloaded': img_count,
                            'images': images,
                            'videos': videos
                        }
                        results['total_downloaded'] += img_count
                        results['total_images'] += images
                        results['total_videos'] += videos
                        results['platforms_searched'].append('images')
                        
                    except Exception as e:
                        results['platform_results']['images'] = f"Error: {str(e)[:100]}"
                
                job_manager.update_job(
                    job_id,
                    status='completed',
                    progress=100,
                    message=f'Keyword scraping completed for "{keyword}": {results["total_downloaded"]} files',
                    downloaded=results['total_downloaded'],
                    images=results['total_images'],
                    videos=results['total_videos'],
                    results=results
                )
                
            except Exception as e:
                job_manager.update_job(
                    job_id,
                    status='error',
                    message=f'Keyword scrape error: {str(e)[:200]}',
                    progress=0
                )
        
        # Start background thread
        import threading
        thread = threading.Thread(target=run_keyword_scrape)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Keyword scraping started for "{keyword}"'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/collections', methods=['GET', 'POST'])
def manage_collections():
    """Manage asset collections"""
    try:
        if request.method == 'GET':
            # List collections
            collections_dir = "downloads/collections"
            collections = []
            
            if os.path.exists(collections_dir):
                for collection_name in os.listdir(collections_dir):
                    collection_path = os.path.join(collections_dir, collection_name)
                    if os.path.isdir(collection_path):
                        # Count files in collection
                        file_count = len([f for f in os.listdir(collection_path) 
                                        if os.path.isfile(os.path.join(collection_path, f))])
                        
                        collections.append({
                            'name': collection_name,
                            'file_count': file_count,
                            'path': f"collections/{collection_name}"
                        })
            
            return jsonify({
                'success': True,
                'collections': collections
            })
        
        elif request.method == 'POST':
            # Create new collection
            data = request.json
            collection_name = data.get('name', '').strip()
            
            if not collection_name:
                return jsonify({'success': False, 'error': 'Collection name is required'})
            
            # Create collection directory
            collections_dir = "downloads/collections"
            collection_path = os.path.join(collections_dir, collection_name)
            
            os.makedirs(collection_path, exist_ok=True)
            
            return jsonify({
                'success': True,
                'message': f'Collection "{collection_name}" created',
                'collection_path': f"collections/{collection_name}"
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/search', methods=['POST'])
def start_general_search():
    """General search endpoint that routes to comprehensive search"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Extract parameters with defaults
        sources = data.get('sources', [])
        safe_search = data.get('safe_search', True)
        max_per_source = data.get('max_per_source', 10)
        
        # Create background job
        job_id = job_manager.create_job('general_search', {
            'query': query,
            'sources': sources,
            'safe_search': safe_search,
            'max_per_source': max_per_source
        })
        
        # Start background thread
        thread = threading.Thread(
            target=run_comprehensive_search_job,
            args=(job_id, query, 'general', max_per_source, sources, safe_search)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'General search started for: {query} (Safe search: {"ON" if safe_search else "OFF"})'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 === STARTING ENHANCED MEDIA SCRAPER ===")
    print("📍 Server: http://localhost:5000")
    print("🔄 Mode: Enhanced (Multi-source with asset management)")
    print("💾 Real content downloads with comprehensive source support")
    print("==================================================")
    
    # Ensure downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("downloads/collections", exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
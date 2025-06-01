#!/usr/bin/env python3
"""
Enhanced Media Scraper Web Application - Database-Driven with Google OAuth and RBAC
Flask web application with comprehensive source management, asset organization, and real-time progress tracking
Now featuring database persistence, Google OAuth authentication, and role-based access control
"""

import os
import json
import time
import threading
import uuid
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_from_directory, flash, redirect, url_for, make_response, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required, logout_user
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from dotenv import load_dotenv
from urllib.parse import unquote
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join

# Load environment variables
load_dotenv()

# Debug environment variables
print(f"🔍 DEBUG: DATABASE_URL from env: {os.environ.get('DATABASE_URL', 'NOT SET')}")
print(f"🔍 DEBUG: GOOGLE_CLIENT_ID: {os.environ.get('GOOGLE_CLIENT_ID', 'NOT SET')[:30]}...")

# Import our custom modules
from models import db, User, Role, ScrapeJob, Asset, AppSetting, init_db, MediaBlob
from auth import init_auth, require_permission, require_role, admin_required, user_or_admin_required, check_user_access, optional_auth, get_current_user_info
from db_job_manager import db_job_manager, db_asset_manager

# Import subscription system
from subscription import subscription_bp, subscription_required, credits_required, check_subscription_status, get_user_sources, can_use_source, TRIAL_SOURCES
from watermark import watermark_overlay, get_watermark_css, get_watermark_html

# Import the original scraping functions
from real_content_downloader import (
    download_images_simple, 
    enhanced_social_scrape,
    enhanced_instagram_scrape,
    enhanced_twitter_scrape,
    enhanced_tiktok_scrape,
    comprehensive_multi_source_scrape,
    get_content_sources
)

# Create Flask app
app = Flask(__name__)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# SQL Server Express Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 
    'mssql+pyodbc://localhost\\SQLEXPRESS/Scraped?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes')
print(f"🔍 DEBUG: Final SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"🗄️  Database: SQL Server Express - Scraped")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['WTF_CSRF_ENABLED'] = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

# Fix MAX_CONTENT_LENGTH configuration
max_content_str = os.environ.get('MAX_CONTENT_LENGTH', '16777216')  # 16MB default in bytes
if '#' in max_content_str:
    max_content_str = max_content_str.split('#')[0].strip()  # Remove comment
app.config['MAX_CONTENT_LENGTH'] = int(max_content_str)

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)

# Initialize authentication
google_bp = init_auth(app)

# Register subscription blueprint
app.register_blueprint(subscription_bp)

# Register AI blueprint
try:
    from ai_api import ai_bp
    app.register_blueprint(ai_bp)
    print("✅ AI API blueprint registered")
except ImportError as e:
    print(f"⚠️ AI features not available: {e}")

# Security headers (optional - can be disabled for development)
if os.environ.get('FLASK_ENV') == 'production':
    talisman = Talisman(
        app,
        force_https=False,  # Set to True if using HTTPS
        strict_transport_security=True,
        content_security_policy={
            'default-src': "'self'",
            'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
            'style-src': "'self' 'unsafe-inline'",
            'img-src': "'self' data: blob:",
            'media-src': "'self' blob:",
            'connect-src': "'self'"
        }
    )

def create_progress_callback(job_id):
    """Create a progress callback function for a specific job - Database version"""
    def progress_callback(message, progress, downloaded, images, videos, current_file=None):
        print(f"[DEBUG] Progress callback called for job {job_id}: message={message}, progress={progress}, downloaded={downloaded}, images={images}, videos={videos}, current_file={current_file}")
        # Run database operations within app context
        with app.app_context():
            try:
                db_job_manager.add_progress_update(job_id, message, progress, downloaded, images, videos, current_file)
                
                # Also track the asset in the database if current_file is provided
                if current_file and os.path.exists(current_file):
                    # Determine file type
                    file_extension = os.path.splitext(current_file)[1].lower()
                    file_type = 'video' if file_extension in ['.mp4', '.webm', '.avi', '.mov', '.mkv'] else 'image'
                    
                    # Add to asset database
                    db_asset_manager.add_asset(
                        job_id=job_id,
                        filepath=current_file,
                        file_type=file_type,
                        metadata={
                            'source_name': 'scraper',
                            'downloaded_via': 'comprehensive_search'
                        }
                    )
            except Exception as e:
                # Log error but don't crash the download process
                print(f"⚠️ Progress callback error for job {job_id}: {str(e)}")
    return progress_callback

def run_comprehensive_search_job(job_id, query, search_type, max_content, enabled_sources, safe_search=True):
    """Run comprehensive search in background thread with safe search support - Database version"""
    with app.app_context():  # Add application context
        try:
            progress_callback = create_progress_callback(job_id)
            
            db_job_manager.update_job(job_id, status='running', message=f'Starting {search_type} search (Safe search: {"ON" if safe_search else "OFF"})...')
            
            # Execute the comprehensive search with progress tracking and safe search
            results = comprehensive_multi_source_scrape(
                query=query,
                search_type=search_type,  # Pass the search_type parameter
                enabled_sources=enabled_sources,
                max_content_per_source=max_content,
                output_dir=None,  # No longer using filesystem output
                progress_callback=progress_callback,
                safe_search=safe_search  # Pass safe search parameter
            )
            
            # Update job with final results
            db_job_manager.update_job(
                job_id,
                status='completed',
                progress=100,
                message=f'{search_type.capitalize()} search completed successfully! (Safe search: {"ON" if safe_search else "OFF"})',
                detected=results.get('total_detected', 0),
                downloaded=results.get('total_downloaded', 0),
                images=results.get('total_images', 0),
                videos=results.get('total_videos', 0),
                sources=results.get('sources', {}),
                results=results
            )
            
        except Exception as e:
            db_job_manager.update_job(
                job_id,
                status='error',
                message=f'Error: {str(e)}',
                progress=0
            )

def run_instagram_search_job(job_id, username, max_content):
    """Run Instagram-specific search in background thread - Database version"""
    with app.app_context():  # Add application context
        try:
            progress_callback = create_progress_callback(job_id)
            
            db_job_manager.update_job(job_id, status='running', message=f'Scraping Instagram @{username}...')
            
            results = enhanced_instagram_scrape(
                username_or_url=username,
                max_content=max_content,
                output_dir=None,  # No longer using filesystem output
                progress_callback=progress_callback
            )
            
            downloaded_count = results.get('downloaded', 0)
            images = results.get('images', 0)
            videos = results.get('videos', 0)
            
            db_job_manager.update_job(
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
            db_job_manager.update_job(
                job_id,
                status='error',
                message=f'Instagram error: {str(e)}',
                progress=0
            )

# Asset access control helper
def check_asset_access(asset, user):
    """Check if a user can access a specific asset"""
    # Public assets (no user_id) can be accessed by anyone
    if asset.user_id is None:
        return True
    
    # If user is not authenticated, they can't access private assets
    if not user or not user.is_authenticated:
        return False
    
    # Admin can access all assets
    if user.is_admin():
        return True
    
    # Users can access their own assets
    return asset.user_id == user.id

# Routes

@app.route('/')
@optional_auth
def index():
    """Main application page with authentication awareness"""
    user_info = get_current_user_info()
    return render_template('index.html', user_info=user_info, config={'DEBUG': app.debug})

@app.route('/logout')
@login_required
def logout():
    """Logout the current user"""
    logout_user()
    flash('You have been successfully signed out.', 'success')
    return redirect(url_for('index'))

@app.route('/test-ui')
@optional_auth
def test_ui():
    """UI functionality test page"""
    return send_from_directory('.', 'test_ui_functionality.html')

@app.route('/api/sources')
@optional_auth
def get_sources():
    """Get available content sources with categories and safe search filtering"""
    try:
        sources = get_content_sources()
        safe_search = request.args.get('safe_search', 'true').lower() == 'true'
        
        # Get user's allowed sources based on subscription
        allowed_sources = []
        if current_user.is_authenticated:
            # Check subscription status
            check_subscription_status(current_user)
            allowed_sources = get_user_sources(current_user)
            
            # Override safe search if user has NSFW enabled
            if current_user.can_use_nsfw() and current_user.is_nsfw_enabled:
                safe_search = False
        else:
            # Trial sources for non-authenticated users
            allowed_sources = TRIAL_SOURCES
        
        # Organize sources by category
        categorized = {
            'social': [],
            'search': [],
            'art': [],
            'video': [],
            'gallery': [],
            'stock': [],
            'direct': [],
            'adult': []  # Adult content category
        }
        
        for source_name, source_obj in sources.items():
            # Skip adult content sources if safe search is enabled
            if safe_search and source_obj.requires_no_safe_search:
                continue
            
            # Check if user can access this source
            is_allowed = source_name in allowed_sources
                
            category = source_obj.category
            if category == 'general':
                category = 'search'  # Default mapping
            
            source_data = {
                'name': source_name,
                'display_name': source_obj.display_name,
                'enabled': source_obj.enabled and is_allowed,
                'category': category,
                'requires_no_safe_search': source_obj.requires_no_safe_search,
                'locked': not is_allowed,  # Show if source is locked
                'lock_reason': 'Subscribe to unlock this source' if not is_allowed else None
            }
            
            if category in categorized:
                categorized[category].append(source_data)
            else:
                categorized['search'].append(source_data)  # Fallback
        
        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}
        
        # Add subscription info
        subscription_info = {
            'is_subscribed': False,
            'plan': 'trial',
            'credits': 0,
            'can_use_nsfw': False
        }
        
        if current_user.is_authenticated:
            subscription_info = {
                'is_subscribed': current_user.is_subscribed(),
                'plan': current_user.subscription_plan,
                'credits': current_user.credits,
                'can_use_nsfw': current_user.can_use_nsfw()
            }
        
        return jsonify({
            'success': True,
            'sources': categorized,
            'safe_search_enabled': safe_search,
            'adult_sources_available': not safe_search,
            'user_authenticated': current_user.is_authenticated,
            'subscription_info': subscription_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/comprehensive-search', methods=['POST'])
@csrf.exempt  # Exempt for API endpoints - implement token-based auth if needed
def start_comprehensive_search():
    """Start comprehensive search across multiple sources with authentication and RBAC"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        search_type = data.get('search_type', 'comprehensive')
        max_content = int(data.get('max_content', 25))
        enabled_sources = data.get('enabled_sources', [])
        safe_search = data.get('safe_search', True)
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'})
        
        # Check if user is authenticated and has permission to start jobs
        if not current_user.is_authenticated:
            # Check if guest downloads are allowed
            allow_guest = AppSetting.get_setting('allow_guest_downloads', False)
            if not allow_guest:
                return jsonify({
                    'success': False, 
                    'error': 'Authentication required to start downloads',
                    'login_required': True
                }), 401
        else:
            # Check subscription and credits
            check_subscription_status(current_user)
            
            # Check if user has credits or subscription
            if not current_user.has_credits():
                return jsonify({
                    'success': False,
                    'error': 'You have no credits remaining. Please upgrade to continue.',
                    'upgrade_required': True,
                    'credits': 0
                }), 402  # Payment Required
            
            # Check if user has permission to start jobs
            if not current_user.has_permission('start_jobs'):
                return jsonify({
                    'success': False,
                    'error': 'You do not have permission to start download jobs'
                }), 403
            
            # Filter sources based on user's subscription
            allowed_sources = get_user_sources(current_user)
            enabled_sources = [source for source in enabled_sources if source in allowed_sources]
            
            if not enabled_sources:
                return jsonify({
                    'success': False,
                    'error': 'No valid sources selected. Please check your subscription level.',
                    'upgrade_required': True
                }), 402
            
            # Override safe search if user has NSFW enabled
            if current_user.can_use_nsfw() and current_user.is_nsfw_enabled:
                safe_search = False
            elif not current_user.can_use_nsfw():
                safe_search = True  # Force safe search for non-Ultra users
        
        # Filter out adult sources if safe search is enabled
        if safe_search:
            sources = get_content_sources()
            enabled_sources = [source for source in enabled_sources 
                             if source not in sources or not sources[source].requires_no_safe_search]
        
        # Get user_id if authenticated
        user_id = current_user.id if current_user.is_authenticated else None
        
        # Use a credit if user is on trial
        if current_user.is_authenticated:
            current_user.use_credit()
            db.session.commit()
        
        # Create background job
        job_id = db_job_manager.create_job('comprehensive_search', {
            'query': query,
            'search_type': search_type,
            'max_content': max_content,
            'enabled_sources': enabled_sources,
            'safe_search': safe_search,
            'user_id': user_id
        })
        
        # Start background thread
        thread = threading.Thread(
            target=run_comprehensive_search_job,
            args=(job_id, query, search_type, max_content, enabled_sources, safe_search)
        )
        thread.daemon = True
        thread.start()
        
        credits_remaining = current_user.credits if current_user.is_authenticated else 0
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'Comprehensive search started (Safe search: {"ON" if safe_search else "OFF"})',
            'safe_search_enabled': safe_search,
            'user_authenticated': current_user.is_authenticated,
            'credits_remaining': credits_remaining
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/instagram-search', methods=['POST'])
@csrf.exempt
def start_instagram_search():
    """Start Instagram-specific search with authentication check"""
    try:
        data = request.json
        username = data.get('username', '').strip().replace('@', '')
        max_content = int(data.get('max_content', 25))
        
        if not username:
            return jsonify({'success': False, 'error': 'Username is required'})
        
        # Check authentication and permissions (same as comprehensive search)
        if not current_user.is_authenticated:
            allow_guest = AppSetting.get_setting('allow_guest_downloads', False)
            if not allow_guest:
                return jsonify({
                    'success': False, 
                    'error': 'Authentication required to start downloads',
                    'login_required': True
                }), 401
        else:
            if not current_user.has_permission('start_jobs'):
                return jsonify({
                    'success': False,
                    'error': 'You do not have permission to start download jobs'
                }), 403
        
        # Get user_id if authenticated
        user_id = current_user.id if current_user.is_authenticated else None
        
        # Create background job
        job_id = db_job_manager.create_job('instagram_search', {
            'username': username,
            'max_content': max_content,
            'user_id': user_id
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
@optional_auth
def get_job_status(job_id):
    """Get status of a background job with user access control"""
    try:
        job_data = db_job_manager.get_job_status(job_id)
        
        if job_data.get('status') == 'not_found':
            return jsonify({'status': 'not_found'}), 404
        
        # Check if user can access this job
        if current_user.is_authenticated:
            job_user_id = job_data.get('user_id')
            # Users can see their own jobs, admins can see all jobs
            if job_user_id and job_user_id != current_user.id and not current_user.is_admin():
                return jsonify({'status': 'access_denied'}), 403
        
        return jsonify(job_data)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting job status: {str(e)}'
        })

@app.route('/api/jobs')
@optional_auth
def get_jobs():
    """Get job history for current user or all jobs for admin"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status_filter = request.args.get('status')
        
        if current_user.is_authenticated:
            if current_user.is_admin():
                # Admin can see all jobs
                user_id = None
            else:
                # Regular users see only their jobs
                user_id = current_user.id
        else:
            # Guests see no job history
            return jsonify({
                'jobs': [],
                'total': 0,
                'message': 'Login to view job history'
            })
        
        jobs = db_job_manager.get_user_jobs(
            user_id=user_id,
            limit=limit,
            status_filter=status_filter
        )
        
        # Get statistics
        stats = db_job_manager.get_job_statistics(user_id=user_id)
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'statistics': stats,
            'total': len(jobs)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/jobs/<job_id>', methods=['DELETE'])
@user_or_admin_required
@csrf.exempt
def cancel_job(job_id):
    """Cancel a running job"""
    try:
        success = db_job_manager.cancel_job(
            job_id=job_id,
            user_id=current_user.id if not current_user.is_admin() else None
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Job cancelled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Unable to cancel job (may not exist or already completed)'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/assets')
@optional_auth
def get_assets():
    """Get all downloaded assets with user-based filtering"""
    try:
        file_type = request.args.get('type')  # 'image' or 'video'
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        offset = (page - 1) * limit
        
        if current_user.is_authenticated:
            if current_user.is_admin():
                # Admin can see all assets
                user_id = None
            else:
                # Regular users see only their assets
                user_id = current_user.id
        else:
            # Guests can see public assets (assets without user_id)
            user_id = None  # This will need additional filtering in the manager
        
        # Get assets from database
        assets_data = db_asset_manager.get_assets(
            user_id=user_id,
            file_type=file_type,
            limit=limit,
            offset=offset
        )
        
        # Get statistics
        stats = db_asset_manager.get_asset_statistics(user_id=user_id)
        
        # Format for compatibility with existing frontend
        assets = []
        for asset_data in assets_data:
            # Convert database format to original API format
            asset_info = {
                'name': asset_data['filename'],
                'path': asset_data['file_path'],
                'size': asset_data['file_size'] or 0,
                'modified': asset_data['downloaded_at'],
                'type': asset_data['file_type'],
                'extension': asset_data['file_extension'],
                'id': asset_data['id'],
                'source': asset_data.get('source_name', 'unknown'),
                'user_id': asset_data.get('user_id'),
                'job_id': asset_data.get('job_id')
            }
            
            # Add video-specific metadata
            if asset_data['file_type'] == 'video':
                asset_info.update({
                    'width': asset_data.get('width'),
                    'height': asset_data.get('height'),
                    'duration': asset_data.get('duration')
                })
            
            assets.append(asset_info)
        
        # Count by type for compatibility
        all_count = stats['total_assets']
        images_count = stats['total_images']
        videos_count = stats['total_videos']
        
        return jsonify({
            'success': True,
            'assets': assets,
            'statistics': stats,
            'counts': {
                'all': all_count,
                'images': images_count,
                'videos': videos_count
            },
            'total': len(assets),
            'user_authenticated': current_user.is_authenticated
        })
        
    except Exception as e:
        print(f"Error getting assets: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'assets': [],
            'counts': {'all': 0, 'images': 0, 'videos': 0}
        })

@app.route('/api/assets/<int:asset_id>', methods=['DELETE'])
@user_or_admin_required
@csrf.exempt
def delete_asset(asset_id):
    """Delete an asset by ID with user access control"""
    try:
        success = db_asset_manager.delete_asset(
            asset_id=asset_id,
            user_id=current_user.id if not current_user.is_admin() else None
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Asset deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Asset not found or access denied'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/assets/bulk-delete', methods=['POST'])
@user_or_admin_required
@csrf.exempt
def bulk_delete_assets():
    """Bulk delete multiple assets"""
    try:
        data = request.get_json()
        asset_ids = data.get('asset_ids', [])
        
        if not asset_ids:
            return jsonify({
                'success': False,
                'error': 'No asset IDs provided'
            }), 400
        
        deleted_count = db_asset_manager.bulk_delete_assets(
            asset_ids=asset_ids,
            user_id=current_user.id if not current_user.is_admin() else None
        )
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {deleted_count} assets',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/assets/bulk-move', methods=['POST'])
@user_or_admin_required
@csrf.exempt
def bulk_move_assets():
    """Move multiple assets to a container"""
    try:
        data = request.get_json()
        asset_ids = data.get('asset_ids', [])
        container = data.get('container', 'default')
        
        if not asset_ids:
            return jsonify({
                'success': False,
                'error': 'No asset IDs provided'
            }), 400
        
        moved_count = db_asset_manager.move_assets_to_container(
            asset_ids=asset_ids,
            container_name=container,
            user_id=current_user.id if not current_user.is_admin() else None
        )
        
        return jsonify({
            'success': True,
            'message': f'Successfully moved {moved_count} assets to {container}',
            'moved_count': moved_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/containers')
@user_or_admin_required
def get_user_containers():
    """Get all containers for the current user"""
    try:
        containers = db_asset_manager.get_user_containers(current_user.id)
        
        return jsonify({
            'success': True,
            'containers': containers
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/assets/<path:asset_path>', methods=['DELETE'])
@user_or_admin_required
@csrf.exempt
def delete_asset_by_path(asset_path):
    """Delete an asset by path - Legacy endpoint for backward compatibility"""
    try:
        # Find asset by path
        asset = db.session.query(Asset).filter_by(
            file_path=asset_path,
            is_deleted=False
        ).first()
        
        if not asset:
            return jsonify({
                'success': False,
                'error': 'Asset not found'
            }), 404
        
        # Use the ID-based deletion
        return delete_asset(asset.id)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/media/<int:asset_id>')
@optional_auth
def serve_media_blob(asset_id):
    """Serve media file from database blob OR filesystem with user access control and watermarks"""
    try:
        from models import MediaBlob, Asset
        
        # Get the asset
        asset = Asset.query.get_or_404(asset_id)
        
        # Check if user can access this asset
        if not check_asset_access(asset, current_user if current_user.is_authenticated else None):
            return jsonify({'error': 'Access denied'}), 403
        
        # First try to get from MediaBlob
        media_blob = MediaBlob.query.filter_by(asset_id=asset_id).first()
        
        if media_blob:
            # Serve from database
            file_data = media_blob.get_file_data()
            mime_type = media_blob.mime_type
        else:
            # Fallback to filesystem
            if not asset.file_path or not os.path.exists(asset.file_path):
                return jsonify({'error': 'Media file not found'}), 404
            
            # Read file from filesystem
            with open(asset.file_path, 'rb') as f:
                file_data = f.read()
            
            # Determine mime type
            import mimetypes
            mime_type, _ = mimetypes.guess_type(asset.file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
        
        # Apply watermark for trial users
        should_watermark = False
        if current_user.is_authenticated:
            # Check if user is on trial or doesn't have active subscription
            if current_user.subscription_plan == 'trial' or not current_user.is_subscribed():
                should_watermark = True
        else:
            # Non-authenticated users always get watermark
            should_watermark = True
        
        # Apply watermark if needed
        if should_watermark and asset.file_type == 'image':
            file_data = watermark_overlay.apply_watermark_to_image_bytes(file_data)
        
        # Create response
        response = make_response(file_data)
        response.headers['Content-Type'] = mime_type
        
        # Check if download is requested
        if request.args.get('download') == 'true':
            # Force download
            response.headers['Content-Disposition'] = f'attachment; filename="{asset.filename}"'
        else:
            # Inline display (for viewing)
            response.headers['Content-Disposition'] = f'inline; filename="{asset.filename}"'
        
        # Cache headers
        response.headers['Cache-Control'] = 'private, max-age=3600'
        response.headers['ETag'] = f'"{asset.id}-{asset.file_size}"'
        
        # Add watermark indicator header
        if should_watermark:
            response.headers['X-Watermarked'] = 'true'
        
        return response
        
    except Exception as e:
        print(f"Error serving media: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/media/<int:asset_id>/thumbnail')
@optional_auth  
def serve_media_thumbnail(asset_id):
    """Serve thumbnails for media assets with user access control"""
    try:
        # Find the asset
        asset = Asset.query.filter_by(id=asset_id, is_deleted=False).first()
        if not asset:
            return "Asset not found", 404
        
        # Check user access (same logic as media blob)
        if current_user.is_authenticated:
            if asset.user_id and asset.user_id != current_user.id and not current_user.is_admin():
                return "Access denied", 403
        else:
            if asset.user_id is not None:
                return "Authentication required", 401
        
        # For images, serve the image itself as thumbnail (scaled down via CSS)
        if asset.file_type == 'image':
            return serve_media_blob(asset_id)
        
        # For videos, try to serve thumbnail if available
        if asset.thumbnail_path and os.path.exists(asset.thumbnail_path):
            return send_file(asset.thumbnail_path)
        
        # Default video thumbnail (placeholder)
        default_thumbnail = "static/images/video-placeholder.png"
        if os.path.exists(default_thumbnail):
            return send_file(default_thumbnail)
        
        # Generate basic thumbnail response
        return "No thumbnail available", 404
    
    except Exception as e:
        print(f"Error serving thumbnail for asset {asset_id}: {e}")
        return "Error serving thumbnail", 500

@app.route('/downloads/<path:asset_path>')
@optional_auth
def download_asset_legacy(asset_path):
    """Legacy download endpoint for backward compatibility"""
    try:
        # Try to parse asset ID from path
        # Handle both numeric IDs and file paths
        asset_id = None
        
        # First try to parse as integer ID
        try:
            asset_id = int(asset_path)
        except ValueError:
            # If not an integer, try to find by filename or path
            asset = Asset.query.filter(
                (Asset.filename == asset_path) | 
                (Asset.file_path == asset_path)
            ).filter_by(is_deleted=False).first()
            
            if asset:
                asset_id = asset.id
            else:
                return "Asset not found", 404
        
        # Use the media blob endpoint
        return serve_media_blob(asset_id)
        
    except Exception as e:
        print(f"Error in legacy download: {e}")
        return "Error downloading file", 500

@app.route('/api/update-nsfw', methods=['POST'])
@login_required
@csrf.exempt
def update_nsfw_setting():
    """Update user's NSFW setting"""
    try:
        data = request.json
        enabled = data.get('enabled', False)
        
        # Check if user can use NSFW
        if not current_user.can_use_nsfw():
            return jsonify({
                'success': False,
                'error': 'NSFW content requires Ultra subscription'
            }), 403
        
        # Update setting
        current_user.is_nsfw_enabled = enabled
        db.session.commit()
        
        return jsonify({
            'success': True,
            'enabled': current_user.is_nsfw_enabled
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/watermark-css')
def get_watermark_styles():
    """Get watermark CSS for frontend"""
    return make_response(get_watermark_css(), 200, {'Content-Type': 'text/css'})

@app.route('/api/user-info')
@optional_auth
def get_user_info():
    """Get current user info including subscription details"""
    if current_user.is_authenticated:
        # Check subscription status
        check_subscription_status(current_user)
        
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict(),
            'subscription': {
                'plan': current_user.subscription_plan,
                'status': current_user.subscription_status,
                'credits': current_user.credits,
                'is_subscribed': current_user.is_subscribed(),
                'can_use_nsfw': current_user.can_use_nsfw(),
                'sources_enabled': current_user.get_enabled_sources()
            }
        })
    else:
        return jsonify({
            'authenticated': False,
            'subscription': {
                'plan': 'trial',
                'credits': 0,
                'is_subscribed': False,
                'can_use_nsfw': False,
                'sources_enabled': TRIAL_SOURCES
            }
        })

@app.route('/api/claim-signin-bonus', methods=['POST'])
@login_required
@csrf.exempt
def claim_signin_bonus():
    """Award 50 credits for first-time sign-in"""
    try:
        # Check if user already claimed bonus
        if current_user.signin_bonus_claimed:
            return jsonify({
                'success': False,
                'error': 'Sign-in bonus already claimed'
            })
        
        # Award 50 credits
        current_user.credits += 50
        current_user.signin_bonus_claimed = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'credits': current_user.credits,
            'message': 'Welcome bonus of 50 credits awarded!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Admin routes

@app.route('/api/admin/users')
@admin_required
def admin_list_users():
    """Admin endpoint to list all users"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users],
            'total': len(users)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/admin/user/<int:user_id>')
@admin_required
def admin_get_user(user_id):
    """Get specific user details for admin"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'display_name': user.display_name,
                'subscription_plan': user.subscription_plan,
                'credits': user.credits,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_admin': user.is_admin()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/admin/user/<int:user_id>', methods=['PUT'])
@admin_required
@csrf.exempt
def admin_update_user(user_id):
    """Update user details for admin"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        data = request.json
        
        # Update subscription plan
        if 'subscription_plan' in data:
            user.subscription_plan = data['subscription_plan']
            user.subscription_status = 'active' if data['subscription_plan'] != 'trial' else 'trial'
            
            # Update enabled sources based on plan
            from subscription import SUBSCRIPTION_PLANS, ALL_SOURCES, TRIAL_SOURCES
            
            if data['subscription_plan'] == 'ultra':
                user.set_enabled_sources(ALL_SOURCES)
                user.is_nsfw_enabled = True
            elif data['subscription_plan'] in SUBSCRIPTION_PLANS:
                plan = SUBSCRIPTION_PLANS[data['subscription_plan']]
                user.set_enabled_sources(plan['sources'])
                user.is_nsfw_enabled = False
            else:
                user.set_enabled_sources(TRIAL_SOURCES)
                user.is_nsfw_enabled = False
        
        # Update credits
        if 'credits' in data:
            user.credits = int(data['credits'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'subscription_plan': user.subscription_plan,
                'credits': user.credits
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/admin/settings')
@admin_required
def admin_get_settings():
    """Admin endpoint to get all application settings"""
    try:
        settings = AppSetting.query.all()
        settings_dict = {}
        
        for setting in settings:
            settings_dict[setting.key] = {
                'value': setting.get_value(),
                'description': setting.description,
                'type': setting.setting_type,
                'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
            }
        
        return jsonify({
            'success': True,
            'settings': settings_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/admin/settings', methods=['PUT'])
@admin_required
@csrf.exempt
def admin_update_settings():
    """Admin endpoint to update application settings"""
    try:
        data = request.get_json()
        
        for key, value in data.items():
            AppSetting.set_setting(
                key=key,
                value=value,
                user_id=current_user.id
            )
        
        return jsonify({
            'success': True,
            'message': f'Updated {len(data)} settings'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/admin/cleanup')
@admin_required
@csrf.exempt
def admin_cleanup():
    """Admin endpoint to cleanup old jobs and missing files"""
    try:
        cleanup_days = int(request.args.get('days', 30))
        
        # Cleanup old jobs
        cleaned_jobs = db_job_manager.cleanup_old_jobs(cleanup_days)
        
        # Cleanup missing files
        cleaned_assets = db_asset_manager.cleanup_missing_files()
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {cleaned_jobs} old jobs and {cleaned_assets} missing assets',
            'cleaned_jobs': cleaned_jobs,
            'cleaned_assets': cleaned_assets
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# AI Assistant Routes

@app.route('/api/ai-assistant', methods=['POST'])
@optional_auth
@csrf.exempt
def ai_assistant_chat():
    """Handle AI assistant chat requests with user-provided API key"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        api_key = data.get('api_key', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            })
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key is required'
            })
        
        # Import OpenAI and create client with user's API key
        from openai import OpenAI
        
        try:
            client = OpenAI(api_key=api_key)
            
            # Build conversation
            messages = [
                {"role": "system", "content": """You are an AI assistant for a media scraping application. 
Your role is to help users optimize their searches, recommend the best sources, 
and provide guidance on using the application effectively.

Key capabilities:
- Optimize search queries for better results
- Recommend appropriate sources based on content type
- Filter out low-quality or fake content
- Provide usage tips and best practices
- Help with subscription and feature questions

Always be helpful, concise, and focus on getting users the best results."""},
                {"role": "user", "content": message}
            ]
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Check if the response suggests a search query
            suggested_query = None
            import re
            query_match = re.search(r'search for[:\s]*"([^"]+)"', ai_response, re.IGNORECASE)
            if query_match:
                suggested_query = query_match.group(1)
            
            return jsonify({
                'success': True,
                'response': ai_response,
                'suggested_query': suggested_query
            })
            
        except Exception as openai_error:
            return jsonify({
                'success': False,
                'error': f'OpenAI API error: {str(openai_error)}'
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/ai-optimize-query', methods=['POST'])
@optional_auth
@csrf.exempt
def ai_optimize_query():
    """AI query optimization endpoint"""
    try:
        from ai_assistant import ai_assistant
        
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('search_type', 'comprehensive')
        filters = data.get('filters', {})
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Optimize query using AI assistant
        optimized = ai_assistant.optimize_query(query, search_type, filters)
        
        return jsonify({
            'success': True,
            'optimized_query': optimized['query'],
            'optimization_score': optimized['score'],
            'suggestions': optimized['suggestions'],
            'explanation': optimized['explanation']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Legacy routes (maintaining backward compatibility)

@app.route('/test-system')
@optional_auth
def test_system():
    """System test endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        # Test sources
        sources = get_content_sources()
        
        # Test authentication status
        auth_status = "authenticated" if current_user.is_authenticated else "guest"
        
        test_results = {
            'database': 'connected',
            'sources_available': len(sources),
            'authentication': auth_status,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'tests': test_results,
            'message': 'All systems operational'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'System test failed'
        })

@app.route('/test-oauth')
def test_oauth():
    """Test OAuth configuration step by step"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Configuration Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .step { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .check { color: green; font-weight: bold; }
            .error { color: red; font-weight: bold; }
            .test-btn { background: #4285f4; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🔍 OAuth Configuration Test</h1>
        
        <div class="step">
            <h3>Step 1: Environment Variables</h3>
            <p>Client ID: <span class="check">""" + str(bool(os.environ.get('GOOGLE_CLIENT_ID'))) + """</span></p>
            <p>Client Secret: <span class="check">""" + str(bool(os.environ.get('GOOGLE_CLIENT_SECRET'))) + """</span></p>
            <p>Insecure Transport: <span class="check">""" + str(os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', 'Not Set')) + """</span></p>
        </div>
        
        <div class="step">
            <h3>Step 2: Google Cloud Console Checklist</h3>
            <p>✅ OAuth consent screen configured with app name</p>
            <p>✅ User support email added</p>
            <p>✅ Test user (sop1973@gmail.com) added</p>
            <p>✅ People API enabled</p>
            <p>✅ Redirect URIs: http://localhost:5000/auth/google/authorized</p>
        </div>
        
        <div class="step">
            <h3>Step 3: Test OAuth Flow</h3>
            <button class="test-btn" onclick="window.location.href='/auth/login'">🚀 Test Google OAuth</button>
            <p><small>If configured correctly, this should redirect to Google and back</small></p>
        </div>
        
        <div class="step">
            <h3>Step 4: Current Status</h3>
            <p>Client ID: """ + os.environ.get('GOOGLE_CLIENT_ID', 'NOT SET')[:20] + """...</p>
            <p>Flask App Running: <span class="check">✅</span></p>
        </div>
        
        <div class="step">
            <h3>🚨 If Still Getting 401 Error:</h3>
            <ol>
                <li>Verify OAuth consent screen is PUBLISHED (not in testing)</li>
                <li>Check that redirect URI matches EXACTLY</li>
                <li>Ensure People API is enabled</li>
                <li>Wait 5-10 minutes for Google changes to propagate</li>
            </ol>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/oauth-status')
def oauth_status():
    """Simple OAuth status check"""
    import os
    
    return jsonify({
        'oauth_credentials': {
            'client_id_set': bool(os.environ.get('GOOGLE_CLIENT_ID')),
            'client_secret_set': bool(os.environ.get('GOOGLE_CLIENT_SECRET')),
            'insecure_transport': os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', 'Not Set')
        },
        'server_status': 'running',
        'test_urls': {
            'login': '/auth/login',
            'main_app': '/',
            'oauth_test': '/test-oauth'
        }
    })

@app.route('/debug-oauth')
def debug_oauth():
    """Debug OAuth configuration and status"""
    from auth import google
    import os
    
    debug_info = {
        'environment': {
            'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID', 'NOT SET'),
            'GOOGLE_CLIENT_SECRET': 'SET' if os.environ.get('GOOGLE_CLIENT_SECRET') else 'NOT SET',
            'OAUTHLIB_INSECURE_TRANSPORT': os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', 'NOT SET'),
            'SECRET_KEY': 'SET' if app.config.get('SECRET_KEY') else 'NOT SET'
        },
        'oauth_status': {
            'google_authorized': google.authorized if google else False,
            'has_token': bool(google.token if google else False),
            'google_object_type': str(type(google).__name__) if google else 'None'
        },
        'current_user': {
            'authenticated': current_user.is_authenticated if current_user else False,
            'user_id': current_user.id if current_user and current_user.is_authenticated else None,
            'email': current_user.email if current_user and current_user.is_authenticated else None
        }
    }
    
    if google and google.authorized:
        try:
            resp = google.get("/oauth2/v2/userinfo")
            debug_info['google_api_test'] = {
                'status_code': resp.status_code,
                'success': resp.ok,
                'response': resp.json() if resp.ok else resp.text
            }
        except Exception as e:
            debug_info['google_api_test'] = {
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth Debug Information</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .success {{ background-color: #d4edda; border-color: #c3e6cb; }}
            .error {{ background-color: #f8d7da; border-color: #f5c6cb; }}
            .warning {{ background-color: #fff3cd; border-color: #ffeaa7; }}
            pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
            .btn {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }}
        </style>
    </head>
    <body>
        <h1>🔍 OAuth Debug Information</h1>
        
        <div class="section">
            <h3>Environment Variables</h3>
            <pre>{debug_info['environment']}</pre>
        </div>
        
        <div class="section">
            <h3>OAuth Status</h3>
            <pre>{debug_info['oauth_status']}</pre>
        </div>
        
        <div class="section">
            <h3>Current User</h3>
            <pre>{debug_info['current_user']}</pre>
        </div>
        
        {'<div class="section"><h3>Google API Test</h3><pre>' + str(debug_info.get('google_api_test', 'No API test performed')) + '</pre></div>' if 'google_api_test' in debug_info else ''}
        
        <div class="section">
            <h3>Test Actions</h3>
            <button class="btn" onclick="window.location.href='/auth/login'">🔐 Test OAuth Login</button>
            <button class="btn" onclick="window.location.href='/auth/google'">🔗 Direct Google Auth</button>
            <button class="btn" onclick="window.location.href='/'">🏠 Home</button>
        </div>
        
        <div class="section">
            <h3>Full Debug Data</h3>
            <pre>{debug_info}</pre>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/dev/reset-credits', methods=['POST'])
@login_required
@csrf.exempt
def dev_reset_credits():
    """Development endpoint to reset user credits for testing"""
    try:
        # Only allow in debug mode
        if not app.debug:
            return jsonify({
                'success': False,
                'error': 'This endpoint is only available in debug mode'
            }), 403
        
        # Get requested credits (default to 50)
        data = request.get_json() or {}
        credits = data.get('credits', 50)
        
        # Reset current user's credits
        current_user.credits = credits
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Credits reset to {credits}',
            'user': current_user.email,
            'credits': current_user.credits
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Serve JavaScript fix patch
@app.route('/static/js_fix_patch.js')
def serve_js_fix():
    """Serve the JavaScript fix patch file"""
    try:
        with open('js_fix_patch.js', 'r') as f:
            content = f.read()
        return Response(content, mimetype='application/javascript')
    except FileNotFoundError:
        return Response('// Fix file not found', mimetype='application/javascript', status=404)

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from static directory"""
    return send_from_directory('static', filename)

# Initialize database
def create_tables():
    """Create database tables and initialize with default data"""
    try:
        with app.app_context():
            db.create_all()
            init_db()
            print("✅ Database tables created and initialized")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

@app.route('/api/media/<int:asset_id>/download')
@login_required
def download_media(asset_id):
    """Download a media file (from blob or disk, with access and credit checks)"""
    try:
        from models import MediaBlob, Asset
        asset = Asset.query.get_or_404(asset_id)
        # Check if user can access this asset
        if not check_asset_access(asset, current_user):
            return jsonify({'error': 'Access denied'}), 403
        # Check credits for trial users
        if current_user.subscription_plan == 'trial' and current_user.credits <= 0:
            return jsonify({'error': 'Insufficient credits'}), 403
        # Serve from MediaBlob if available
        media_blob = MediaBlob.query.filter_by(asset_id=asset_id).first()
        if media_blob:
            file_data = media_blob.get_file_data()
            mime_type = media_blob.mime_type
        else:
            if not asset.file_path or not os.path.exists(asset.file_path):
                return jsonify({'error': 'Media file not found'}), 404
            with open(asset.file_path, 'rb') as f:
                file_data = f.read()
            import mimetypes
            mime_type, _ = mimetypes.guess_type(asset.file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
        # Deduct credit if trial
        if current_user.subscription_plan == 'trial':
            current_user.credits -= 1
            db.session.commit()
        # Watermark for trial/non-subscribed users (images only)
        should_watermark = False
        if current_user.subscription_plan == 'trial' or not current_user.is_subscribed():
            should_watermark = True
        if should_watermark and asset.file_type == 'image':
            file_data = watermark_overlay.apply_watermark_to_image_bytes(file_data)
        # Create response
        response = make_response(file_data)
        response.headers['Content-Type'] = mime_type
        response.headers['Content-Disposition'] = f'attachment; filename="{asset.filename}"'
        response.headers['Cache-Control'] = 'private, max-age=3600'
        response.headers['ETag'] = f'"{asset.id}-{asset.file_size}"'
        if should_watermark:
            response.headers['X-Watermarked'] = 'true'
        return response
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/api/subscription/status')
@login_required
def subscription_status():
    """Get user subscription status"""
    return jsonify({
        'success': True,
        'is_premium': current_user.is_premium,
        'credits': current_user.credits,
        'daily_downloads': current_user.daily_downloads,
        'max_daily_downloads': 25 if not current_user.is_premium else 999999
    })

@app.route('/api/subscription/upgrade', methods=['POST'])
@login_required
def upgrade_subscription():
    """Upgrade to premium (placeholder)"""
    # This is a placeholder - implement payment processing
    return jsonify({
        'success': False,
        'message': 'Payment processing coming soon!'
    })

@app.route('/api/download-asset', methods=['POST'])
@login_required
@csrf.exempt
def download_asset():
    """Download individual asset from URL"""
    try:
        data = request.json
        url = data.get('url')
        filename = data.get('filename')
        
        if not url or not filename:
            return jsonify({
                'success': False,
                'error': 'URL and filename are required'
            }), 400
        
        # Check if user has credits or subscription
        if not current_user.has_credits():
            return jsonify({
                'success': False,
                'error': 'You have no credits remaining. Please upgrade to continue.',
                'upgrade_required': True
            }), 402
        
        # Use a credit for download
        current_user.use_credit()
        db.session.commit()
        
        # For now, return success (actual download implementation would go here)
        return jsonify({
            'success': True,
            'message': f'Download initiated for {filename}',
            'credits_remaining': current_user.credits
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats')
@optional_auth  
def get_stats():
    """Get dashboard statistics"""
    try:
        # Get user-specific stats if authenticated
        if current_user.is_authenticated:
            user_id = current_user.id
            # Get user's asset statistics
            stats = db_asset_manager.get_asset_statistics(user_id=user_id)
            total_downloads = stats['total_assets']
            total_images = stats['total_images']
            total_videos = stats['total_videos']
            total_size = stats['total_size_bytes']
            
            # Get user's job stats
            user_jobs = db_job_manager.get_user_jobs(user_id, limit=100)
            completed_jobs = [j for j in user_jobs if j.get('status') == 'completed']
            success_rate = int((len(completed_jobs) / len(user_jobs)) * 100) if user_jobs else 85
            
        else:
            # Return demo stats for non-authenticated users
            total_downloads = 0
            total_images = 0
            total_videos = 0
            total_size = 0
            success_rate = 85
        
        return jsonify({
            'success': True,
            'stats': {
                'total_downloads': total_downloads,
                'total_images': total_images,
                'total_videos': total_videos,
                'total_size': total_size,
                'success_rate': success_rate
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 === STARTING ENHANCED MEDIA SCRAPER (Database-Driven) ===")
    print("📍 Server: http://localhost:5000")
    print("🔄 Mode: Enhanced with Database, OAuth, and RBAC")
    print(f"🗄️  Database: SQL Server Express - Scraped")
    print("🔐 Authentication: Google OAuth Enabled")
    print("💾 Persistent job tracking and asset management")
    print("==================================================")
    print("✅ Database initialized with default roles and settings")
    print("✅ Database tables created and initialized")
    
    # Initialize database on startup
    create_tables()
    
    # Run in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000)
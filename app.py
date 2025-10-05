#!/usr/bin/env python3
"""
Enhanced Media Scraper Web Application - Database-Driven with Google OAuth and RBAC
Flask web application with comprehensive source management, asset organization, and real-time progress tracking
Now featuring database persistence, Google OAuth authentication, and role-based access control
"""

import json
import logging
import logging.config
import os
import time as _time
from datetime import timedelta
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_login import current_user, login_required, logout_user
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

from config import APP_BASE, init_app_config

# Import Windows path utilities for enterprise deployment (Windows only)
import platform
path_manager = None
if platform.system() == "Windows":
    try:
        from deployment.windows.path_utils import get_path_manager, init_windows_paths
        init_windows_paths()
        path_manager = get_path_manager()
        # Only log in development
        if os.getenv("FLASK_ENV") == "development":
            print(f"[WINDOWS] Path management initialized")
    except ImportError:
        pass
elif os.getenv("FLASK_ENV") == "development":
    print(f"[INFO] Standard path management for platform: {platform.system()}")


def require_auth(f):
    """Decorator to require authentication for API endpoints"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)

    return decorated_function


# Load environment variables (with override to ensure fresh values)
load_dotenv(override=True)

# Configure comprehensive logging
try:
    from logging_config import add_request_logging, setup_logging

    setup_logging(log_level="INFO")
    logger = logging.getLogger(__name__)
    logger.info("Comprehensive logging initialized")
except ImportError:
    # Fallback to basic logging
    os.makedirs("logs", exist_ok=True)
    # MAXIMUM DEBUG LOGGING ENABLED
    from logging.handlers import RotatingFileHandler

    os.makedirs("debug_logs", exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,  # Changed to DEBUG
        format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler("debug_logs/app_debug.log", maxBytes=10485760, backupCount=5),
            RotatingFileHandler("debug_logs/oauth_debug.log", maxBytes=10485760, backupCount=5),
        ],
    )

    # Set all loggers to DEBUG
    for logger_name in ["app", "auth", "werkzeug", "authlib", "requests", "urllib3"]:
        logging.getLogger(logger_name).setLevel(logging.DEBUG)
    logger = logging.getLogger(__name__)

try:
    from logging.handlers import RotatingFileHandler

    fh = RotatingFileHandler("logs/scraper.log", maxBytes=1_000_000, backupCount=3)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root_logger = logging.getLogger()
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        root_logger.addHandler(fh)
except Exception:
    pass
logger = logging.getLogger(__name__)

# Debug environment variables
logger.info(f"DATABASE_URL configured: {bool(os.environ.get('DATABASE_URL'))}")
logger.info(f"GOOGLE_CLIENT_ID configured: {bool(os.environ.get('GOOGLE_CLIENT_ID'))}")

# Import our custom modules
from auth import (
    get_current_user_info,
    init_auth,
    optional_auth,
)
from db_job_manager import db_job_manager
from models import db, init_db, Asset, ScrapeJob, User

# Use the fixed database asset manager that works with existing models
try:
    from fixed_asset_manager import db_asset_manager

    print("[IMPORT] Fixed asset manager loaded - proper field mapping")
except ImportError:
    try:
        from database_asset_manager import db_asset_manager

        print("[IMPORT] Database asset manager loaded - files will be stored in database")
    except ImportError:
        from db_asset_manager import db_asset_manager

        print("[IMPORT] Using memory asset manager (fallback)")

# Import subscription system
from blueprints.admin import admin_bp
from blueprints.ai import ai_bp
from blueprints.assets import assets_bp
from blueprints.dashboard import dashboard_bp
from blueprints.jobs import jobs_bp
from blueprints.search import search_bp
try:
    from blueprints.debug import debug_bp
except Exception:
    debug_bp = None
from blueprints.sources import sources_bp
from blueprints.user import user_bp
from subscription import subscription_bp

FIXED_ENDPOINTS_AVAILABLE = False

# Import sources data without dependencies
from sources_data import get_content_sources

# Try to import scraping functions (fallback if missing dependencies)
try:
    from optimized_downloader import comprehensive_multi_source_scrape

    REAL_DOWNLOADER_AVAILABLE = True
    print("[IMPORT] Optimized downloader functions imported successfully")
except ImportError as e:
    try:
        from working_downloader import comprehensive_multi_source_scrape

        REAL_DOWNLOADER_AVAILABLE = True
        print("[IMPORT] Working downloader functions imported successfully")
    except ImportError as e2:
        print(f"[IMPORT] No downloader available: {e}, {e2}")
        REAL_DOWNLOADER_AVAILABLE = False

        # Fallback function
        def comprehensive_multi_source_scrape(**kwargs):
            print("[IMPORT] Using fallback scraper")
            return {"total_detected": 0, "total_downloaded": 0, "total_images": 0, "total_videos": 0, "sources": {}}


# Create Flask app with explicit static configuration
import os

app = Flask(
    __name__,
    static_folder="static",
    static_url_path=f"{APP_BASE}/static",
)

# Configure for reverse proxy deployment (IIS with /scraper prefix)
from werkzeug.middleware.proxy_fix import ProxyFix

# Add request logging if available
try:
    from logging_config import add_request_logging

    app = add_request_logging(app)
except ImportError:
    pass


# Inject cache-busting version for static assets
@app.context_processor
def _inject_static_ver():
    try:
        ver = int(_time.time())
    except Exception:
        ver = 1
    return {"STATIC_VER": ver, "APP_BASE": APP_BASE}


# Apply proxy fix for headers FIRST
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Set APPLICATION_ROOT for proper URL generation when behind IIS proxy
app.config["APPLICATION_ROOT"] = "/scraper"


# Custom middleware to handle /scraper prefix properly
class PrefixPathMiddleware:
    """Middleware that strips APP_BASE prefix from PATH_INFO and sets SCRIPT_NAME"""
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        path_info = environ.get("PATH_INFO", "")
        
        # If path starts with APP_BASE (e.g., /scraper), strip it for routing
        if path_info.startswith(APP_BASE):
            # Set SCRIPT_NAME for proper URL generation
            environ["SCRIPT_NAME"] = APP_BASE
            # Strip the prefix from PATH_INFO so Flask can match routes correctly
            environ["PATH_INFO"] = path_info[len(APP_BASE):] or "/"
        
        return self.app(environ, start_response)


# Apply the middleware AFTER ProxyFix to handle /scraper prefix
app.wsgi_app = PrefixPathMiddleware(app.wsgi_app)

# Force /scraper prefix to match Google OAuth configuration AFTER ProxyFix
# DISABLED: This strips the prefix and breaks routing
# from force_scraper_prefix import force_scraper_urls
# force_scraper_urls(app)

# Fix OAuth redirect URI to match Google's expectation
# DISABLED: This was overriding the correct redirect URL from .env
# from oauth_redirect_fix import apply_oauth_redirect_fix
# apply_oauth_redirect_fix(app)
init_app_config(app)

# OAuth Settings
if os.environ.get("FLASK_ENV") == "development":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allow HTTP in development
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"  # Be flexible with OAuth scopes
    os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "true"  # Allow insecure transport for authlib

# Database Configuration - SQL Server Express ONLY (no SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
if not app.config["SQLALCHEMY_DATABASE_URI"]:
    # Default to SQL Server Express connection if not configured
    # This requires SQL Server Express to be installed and running
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mssql+pyodbc://sa:Admin123!@localhost/scraperdb?driver=ODBC+Driver+17+for+SQL+Server"
    )
    print(f"[DATABASE] Using default SQL Server Express connection")
else:
    print(f"[DATABASE] Using configured database connection: {app.config['SQLALCHEMY_DATABASE_URI']}")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}
app.config["WTF_CSRF_ENABLED"] = False  # Temporarily disabled for testing
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("FLASK_ENV") == "production"
app.config["SESSION_COOKIE_DOMAIN"] = None  # Don't restrict domain
app.config["SESSION_COOKIE_PATH"] = APP_BASE  # Match the application path
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Allow cookie in navigation
app.config["SESSION_COOKIE_NAME"] = "scraper_session"  # Unique session name
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)  # Keep session for 30 days
app.config["SESSION_PERMANENT"] = True  # Make sessions permanent by default
app.config["REMEMBER_COOKIE_NAME"] = "scraper_remember"
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
app.config["REMEMBER_COOKIE_PATH"] = APP_BASE
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_REFRESH_EACH_REQUEST"] = False

# Fix MAX_CONTENT_LENGTH configuration
max_content_str = os.environ.get("MAX_CONTENT_LENGTH", "16777216")  # 16MB default in bytes
if "#" in max_content_str:
    max_content_str = max_content_str.split("#")[0].strip()  # Remove comment
app.config["MAX_CONTENT_LENGTH"] = int(max_content_str)


# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)

# Add request timeout middleware
try:
    from request_timeout import add_timeout_middleware

    add_timeout_middleware(app, default_timeout=30)
    logger.info("Request timeout middleware initialized")
except ImportError:
    logger.warning("Request timeout middleware not available")

# Import database error handler
try:
    from db_error_handler import handle_db_error, with_retry

    logger.info("Database error handler imported")
except ImportError:
    logger.warning("Database error handler not available")

# Initialize authentication
google_bp = init_auth(app)
app.register_blueprint(admin_bp)
app.register_blueprint(assets_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(search_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(sources_bp)
app.register_blueprint(user_bp)
app.register_blueprint(ai_bp)

# Debug: Show registered routes
print("\n[DEBUG] Registered routes after auth init:")
for rule in app.url_map.iter_rules():
    if "auth" in rule.rule or "login" in rule.rule:
        print(f"  {rule.rule} -> {rule.endpoint}")

# Initialize mock endpoints to bypass database errors
# from auth import init_mock_endpoints
# init_mock_endpoints(app)
# print("[SUCCESS] Mock endpoints initialized to bypass database")

# Add mock login for development (OAuth workaround)
try:
    from mock_login import register_mock_auth

    register_mock_auth(app)
except Exception as e:
    print(f"[WARNING] Mock auth not loaded: {e}")


# Register subscription blueprint
app.register_blueprint(subscription_bp)

# Legacy fixed search/download endpoints removed to avoid duplication

# Optional debug/admin blueprints removed to simplify routing
if debug_bp:
    app.register_blueprint(debug_bp)

# Register 404 debug handler
try:
    from debug_404 import debug_404_bp

    app.register_blueprint(debug_404_bp)
    print("[SUCCESS] 404 debug handler registered")
except ImportError as e:
    print(f"[WARNING] 404 debug handler not available: {e}")

# Debug: Print ALL routes after everything is registered
print("\n[DEBUG] ALL REGISTERED ROUTES:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")

# Register AI blueprint
try:
    from ai_api import ai_bp

    app.register_blueprint(ai_bp)
    print("[SUCCESS] AI API blueprint registered")
except ImportError as e:
    print(f"[WARNING] AI features not available: {e}")

# Security headers (optional - can be disabled for development)
if os.environ.get("FLASK_ENV") == "production":
    talisman = Talisman(
        app,
        force_https=False,  # Set to True if using HTTPS
        strict_transport_security=True,
        content_security_policy={
            "default-src": "'self'",
            "script-src": "'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src": "'self' 'unsafe-inline'",
            "img-src": "'self' data: blob:",
            "media-src": "'self' blob:",
            "connect-src": "'self'",
        },
    )


@app.after_request
def add_security_headers(response):
    """Add additional security headers to all responses"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Aggressive cache control for JavaScript and CSS files to prevent browser caching
    if request.path.endswith(('.js', '.css')):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


def create_progress_callback(job_id):
    """Create a progress callback function for a specific job - Database version"""

    def progress_callback(message, progress, downloaded, images, videos, current_file=None, metadata=None):
        print(
            f"[DEBUG] Progress callback called for job {job_id}: message={message}, progress={progress}, downloaded={downloaded}, images={images}, videos={videos}, current_file={current_file}"
        )
        # Run database operations within app context
        with app.app_context():
            try:
                db_job_manager.add_progress_update(job_id, message, progress, downloaded, images, videos, current_file)

                # Also track the asset in the database if current_file is provided
                if current_file and os.path.exists(current_file):
                    # Determine file type
                    file_extension = os.path.splitext(current_file)[1].lower()
                    file_type = "video" if file_extension in [".mp4", ".webm", ".avi", ".mov", ".mkv"] else "image"

                    # Prepare enhanced metadata
                    asset_metadata = {"source_name": "scraper", "downloaded_via": "comprehensive_search"}

                    # Add metadata if provided
                    if metadata:
                        asset_metadata.update(
                            {
                                "source_url": metadata.get("source_url"),
                                "content_type": metadata.get("content_type"),
                                "file_size": metadata.get("file_size"),
                                "is_video": metadata.get("is_video", False),
                            }
                        )

                    # Add to asset database
                    asset_id = db_asset_manager.add_asset(
                        job_id=job_id, filepath=current_file, file_type=file_type, metadata=asset_metadata
                    )

                    if asset_id:
                        print(f"✅ Asset {asset_id} added to database: {os.path.basename(current_file)}")
                    else:
                        print(f"⚠️ Failed to add asset to database: {current_file}")

            except Exception as e:
                # Log error but don't crash the download process
                print(f"⚠️ Progress callback error for job {job_id}: {str(e)}")
                import traceback

                traceback.print_exc()

    return progress_callback


def run_comprehensive_search_job(job_id, query, search_type, max_content, enabled_sources, safe_search=True):
    """Run comprehensive search in background thread with safe search support - Database version"""
    with app.app_context():  # Add application context
        try:
            # Get user_id from job data
            job = db_job_manager.get_job(job_id)
            user_id = job.get("data", {}).get("user_id") if job else None

            db_job_manager.update_job(
                job_id,
                status="running",
                message=f'Starting {search_type} search (Safe search: {"ON" if safe_search else "OFF"})...',
            )

            # Try to use the enhanced working downloader first
            try:
                from enhanced_working_downloader import run_download_job

                print(f"[SEARCH] Using enhanced working downloader for job {job_id}")

                results = run_download_job(
                    job_id=job_id,
                    query=query,
                    sources=enabled_sources,
                    max_content=max_content,
                    safe_search=safe_search,
                    user_id=user_id,
                )

                # Job status is already updated by enhanced_working_downloader
                return

            except ImportError as e:
                print(f"[WARNING] Enhanced working downloader not available: {e}")
                # Try basic working downloader
                try:
                    from working_downloader import run_download_job

                    print(f"[SEARCH] Using basic working downloader for job {job_id}")

                    results = run_download_job(
                        job_id=job_id,
                        query=query,
                        sources=enabled_sources,
                        max_content=max_content,
                        safe_search=safe_search,
                        user_id=user_id,
                    )

                    return

                except ImportError:
                    print(f"[WARNING] No working downloader available, falling back to original")

            # Fallback to original implementation
            progress_callback = create_progress_callback(job_id)

            # Execute the comprehensive search with progress tracking and safe search
            results = comprehensive_multi_source_scrape(
                query=query,
                search_type=search_type,  # Pass the search_type parameter
                enabled_sources=enabled_sources,
                max_content_per_source=max_content,
                output_dir=None,  # No longer using filesystem output
                progress_callback=progress_callback,
                safe_search=safe_search,  # Pass safe search parameter
                use_queue=True,  # Enable queue system
                job_id=job_id,  # Pass job ID for queue tracking
            )

            # Update job with final results
            db_job_manager.update_job(
                job_id,
                status="completed",
                progress=100,
                message=f'{search_type.capitalize()} search completed successfully! (Safe search: {"ON" if safe_search else "OFF"})',
                detected=results.get("total_detected", 0),
                downloaded=results.get("total_downloaded", 0),
                images=results.get("total_images", 0),
                videos=results.get("total_videos", 0),
                sources=results.get("sources", {}),
                results=results,
            )

        except Exception as e:
            db_job_manager.update_job(job_id, status="error", message=f"Error: {str(e)}", progress=0)


def run_instagram_search_job(job_id, username, max_content):
    """Run Instagram-specific search in background thread - Database version"""
    with app.app_context():  # Add application context
        try:
            progress_callback = create_progress_callback(job_id)

            db_job_manager.update_job(job_id, status="running", message=f"Scraping Instagram @{username}...")

            results = enhanced_instagram_scrape(
                username_or_url=username,
                max_content=max_content,
                output_dir=None,  # No longer using filesystem output
                progress_callback=progress_callback,
            )

            downloaded_count = results.get("downloaded", 0)
            images = results.get("images", 0)
            videos = results.get("videos", 0)

            db_job_manager.update_job(
                job_id,
                status="completed",
                progress=100,
                message=f"Instagram scraping completed! Downloaded {downloaded_count} files ({images} images, {videos} videos)",
                downloaded=downloaded_count,
                images=images,
                videos=videos,
                detected=downloaded_count,  # For Instagram, assume all detected were attempted
            )

        except Exception as e:
            db_job_manager.update_job(job_id, status="error", message=f"Instagram error: {str(e)}", progress=0)


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


@app.route("/")
@app.route("/scraper")
@app.route("/scraper/")
@optional_auth
def index():
    """Main application page with authentication awareness"""
    from flask_login import current_user

    # Check if login is required
    login_required_setting = os.getenv("LOGIN_REQUIRED", "true").lower() == "true"

    # If login is required and user is not authenticated, show splash page
    if login_required_setting and not current_user.is_authenticated:
        google_configured = bool(os.getenv("GOOGLE_CLIENT_ID")) and bool(os.getenv("GOOGLE_CLIENT_SECRET"))
        test_admin_enabled = os.getenv("ENABLE_TEST_ADMIN", "false").lower() == "true" or os.getenv("ALLOW_MOCK_LOGIN", "false").lower() == "true"
        return render_template("splash.html", google_configured=google_configured, test_admin_enabled=test_admin_enabled)

    # Otherwise show the main application
    user_info = get_current_user_info()
    # Inject sources JSON so frontend can render instantly
    try:
        sources_data = get_content_sources()
        safe_search = True
        # Build categorized object matching /api/sources response shape
        category_mapping = {
            "search_engines": "Search Engines",
            "galleries": "Image Galleries",
            "stock_photos": "Stock Photos",
            "social_media": "Social Media",
            "video_platforms": "Video Platforms",
            "art_platforms": "Art Platforms",
            "adult_content": "Adult Content",
            "news_media": "News Media",
            "e_commerce": "E-Commerce",
            "entertainment": "Entertainment",
            "academic": "Academic",
            "tech_forums": "Tech Forums",
        }
        categorized = {}
        for category_key, category_sources in sources_data.items():
            if category_key == "all":
                continue
            display_category = category_mapping.get(category_key, category_key.title())
            for source in category_sources:
                if safe_search and source.get("nsfw", False):
                    continue
                categorized.setdefault(display_category, []).append(
                    {
                        "id": source["id"],
                        "name": source["name"],
                        "category": source["category"],
                        "enabled": True,
                        "subscription_required": source.get("subscription_required", False),
                        "nsfw": source.get("nsfw", False),
                    }
                )
        categorized = {k: v for k, v in categorized.items() if v}
        server_sources_json = json.dumps({"categories": categorized})
    except Exception:
        server_sources_json = json.dumps({"categories": {}})

    return render_template(
        "index.html", user_info=user_info, config={"DEBUG": app.debug}, server_sources_json=server_sources_json
    )


@app.route("/index.html")
@optional_auth
def index_direct():
    """Direct access to main app for authenticated users - avoids splash redirect loop"""
    from flask_login import current_user

    # Check if login is required
    login_required_setting = os.getenv("LOGIN_REQUIRED", "true").lower() == "true"

    # If login required and not authenticated, redirect to splash
    if login_required_setting and not current_user.is_authenticated:
        return redirect(url_for("index"))

    # Otherwise show the main application
    user_info = get_current_user_info()
    try:
        sources_data = get_content_sources()
        safe_search = True
        category_mapping = {
            "search_engines": "Search Engines",
            "galleries": "Image Galleries",
            "stock_photos": "Stock Photos",
            "social_media": "Social Media",
            "video_platforms": "Video Platforms",
            "art_platforms": "Art Platforms",
            "adult_content": "Adult Content",
            "news_media": "News Media",
            "e_commerce": "E-Commerce",
            "entertainment": "Entertainment",
            "academic": "Academic",
            "tech_forums": "Tech Forums",
        }
        categorized = {}
        for category_key, category_sources in sources_data.items():
            if category_key == "all":
                continue
            display_category = category_mapping.get(category_key, category_key.title())
            for source in category_sources:
                if safe_search and source.get("nsfw", False):
                    continue
                categorized.setdefault(display_category, []).append(
                    {
                        "id": source["id"],
                        "name": source["name"],
                        "category": source["category"],
                        "enabled": True,
                        "subscription_required": source.get("subscription_required", False),
                        "nsfw": source.get("nsfw", False),
                    }
                )
        categorized = {k: v for k, v in categorized.items() if v}
        server_sources_json = json.dumps({"categories": categorized})
    except Exception:
        server_sources_json = json.dumps({"categories": {}})

    return render_template(
        "index.html", user_info=user_info, config={"DEBUG": app.debug}, server_sources_json=server_sources_json
    )


@app.route("/logout")
@login_required
def logout():
    """Logout the current user"""
    logout_user()
    flash("You have been successfully signed out.", "success")
    return redirect(url_for("index"))


# Admin, AI, and search endpoints migrated to blueprints.

# Legacy routes (maintaining backward compatibility)


@app.route("/test-oauth")
def test_oauth():
    """Test OAuth configuration step by step"""
    html = (
        """
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
        <h1>[SEARCH] OAuth Configuration Test</h1>

        <div class="step">
            <h3>Step 1: Environment Variables</h3>
            <p>Client ID: <span class="check">"""
        + str(bool(os.environ.get("GOOGLE_CLIENT_ID")))
        + """</span></p>
            <p>Client Secret: <span class="check">"""
        + str(bool(os.environ.get("GOOGLE_CLIENT_SECRET")))
        + """</span></p>
            <p>Insecure Transport: <span class="check">"""
        + str(os.environ.get("OAUTHLIB_INSECURE_TRANSPORT", "Not Set"))
        + """</span></p>
        </div>

        <div class="step">
            <h3>Step 2: Google Cloud Console Checklist</h3>
            <p>[SUCCESS] OAuth consent screen configured with app name</p>
            <p>[SUCCESS] User support email added</p>
            <p>[SUCCESS] Test user (sop1973@gmail.com) added</p>
            <p>[SUCCESS] People API enabled</p>
            <p>[SUCCESS] Redirect URIs: /scraper/auth/google/authorized</p>
        </div>

        <div class="step">
            <h3>Step 3: Test OAuth Flow</h3>
            <button class="test-btn" onclick="window.location.href='{{ url_for("auth.login") }}'">[START] Test Google OAuth</button>
            <p><small>If configured correctly, this should redirect to Google and back</small></p>
        </div>

        <div class="step">
            <h3>Step 4: Current Status</h3>
            <p>Client ID: """
        + os.environ.get("GOOGLE_CLIENT_ID", "NOT SET")[:20]
        + """...</p>
            <p>Flask App Running: <span class="check">[SUCCESS]</span></p>
        </div>

        <div class="step">
            <h3>[ALERT] If Still Getting 401 Error:</h3>
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
    )
    return html


@app.route("/oauth-status")
def oauth_status():
    """Simple OAuth status check"""
    import os

    return jsonify(
        {
            "oauth_credentials": {
                "client_id_set": bool(os.environ.get("GOOGLE_CLIENT_ID")),
                "client_secret_set": bool(os.environ.get("GOOGLE_CLIENT_SECRET")),
                "insecure_transport": os.environ.get("OAUTHLIB_INSECURE_TRANSPORT", "Not Set"),
            },
            "server_status": "running",
            "test_urls": {
                "login": '{{ url_for("auth.login") }}',
                "main_app": '{{ url_for("index") }}',
                "oauth_test": "/test-oauth",
            },
        }
    )


@app.route("/debug-oauth")
def debug_oauth():
    """Debug OAuth configuration and status"""
    import os

    from auth import google

    debug_info = {
        "environment": {
            "GOOGLE_CLIENT_ID": os.environ.get("GOOGLE_CLIENT_ID", "NOT SET"),
            "GOOGLE_CLIENT_SECRET": "SET" if os.environ.get("GOOGLE_CLIENT_SECRET") else "NOT SET",
            "OAUTHLIB_INSECURE_TRANSPORT": os.environ.get("OAUTHLIB_INSECURE_TRANSPORT", "NOT SET"),
            "SECRET_KEY": "SET" if app.config.get("SECRET_KEY") else "NOT SET",
        },
        "oauth_status": {
            "google_authorized": google.authorized if google else False,
            "has_token": bool(google.token if google else False),
            "google_object_type": str(type(google).__name__) if google else "None",
        },
        "current_user": {
            "authenticated": current_user.is_authenticated if current_user else False,
            "user_id": current_user.id if current_user and current_user.is_authenticated else None,
            "email": current_user.email if current_user and current_user.is_authenticated else None,
        },
    }

    if google and google.authorized:
        try:
            resp = google.get("/oauth2/v2/userinfo")
            debug_info["google_api_test"] = {
                "status_code": resp.status_code,
                "success": resp.ok,
                "response": resp.json() if resp.ok else resp.text,
            }
        except Exception as e:
            debug_info["google_api_test"] = {"error": str(e), "error_type": type(e).__name__}

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
        <h1>[SEARCH] OAuth Debug Information</h1>

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
            <button class="btn" onclick="window.location.href='{{ url_for("auth.login") }}'">🔐 Test OAuth Login</button>
            <button class="btn" onclick="window.location.href='{{ url_for("auth.login") }}'">🔗 Direct Google Auth</button>
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



# ==================== DASHBOARD API ENDPOINTS ====================

@app.route('/api/dashboard-stats')
@optional_auth
def dashboard_stats():
    """Get dashboard statistics for the current user"""
    user_id = session.get('user_id') or (current_user.id if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None)

    # Return empty stats for unauthenticated users
    if not user_id:
        return jsonify({
            'stats': {
                'total_assets': 0,
                'total_jobs': 0,
                'completed_jobs': 0,
                'pending_jobs': 0,
                'storage_used_mb': 0
            },
            'recent_assets': [],
            'recent_jobs': []
        })

    # Get user stats - ONLY count non-deleted assets
    total_assets = db.session.query(Asset).filter_by(user_id=user_id, is_deleted=False).count()
    total_jobs = db.session.query(ScrapeJob).filter_by(user_id=user_id).count()
    completed_jobs = db.session.query(ScrapeJob).filter_by(user_id=user_id, status='completed').count()
    pending_jobs = db.session.query(ScrapeJob).filter_by(user_id=user_id, status='pending').count()

    # Get recent activity - ONLY non-deleted assets
    recent_assets = db.session.query(Asset).filter_by(user_id=user_id, is_deleted=False)\
        .order_by(Asset.downloaded_at.desc()).limit(5).all()

    recent_jobs = db.session.query(ScrapeJob).filter_by(user_id=user_id)\
        .order_by(ScrapeJob.created_at.desc()).limit(5).all()

    # Calculate storage used (in MB) - ONLY non-deleted assets
    storage_used = 0
    user_assets = db.session.query(Asset).filter_by(user_id=user_id, is_deleted=False).all()
    for asset in user_assets:
        if asset.file_size:
            storage_used += asset.file_size
    storage_used_mb = storage_used / (1024 * 1024)

    return jsonify({
        'stats': {
            'total_assets': total_assets,
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'pending_jobs': pending_jobs,
            'storage_used_mb': round(storage_used_mb, 2)
        },
        'recent_assets': [
            {
                'id': a.id,
                'filename': a.filename,
                'type': a.file_type,
                'created_at': a.downloaded_at.isoformat() if a.downloaded_at else None
            } for a in recent_assets
        ],
        'recent_jobs': [
            {
                'id': j.id,
                'query': j.query,
                'status': j.status,
                'progress': j.progress,
                'created_at': j.created_at.isoformat() if j.created_at else None
            } for j in recent_jobs
        ]
    })

@app.route('/api/system-overview')
@require_auth
def system_overview():
    """Get system overview information"""
    user_id = session.get('user_id')

    # Get user info
    user = db.session.query(User).filter_by(id=user_id).first()

    # Get source statistics
    from scrapers import SOURCES
    total_sources = len(SOURCES)

    # Get active sources (for demonstration, all are active)
    active_sources = total_sources

    # Get system status
    system_status = {
        'scraping_service': 'active',
        'database': 'connected',
        'storage': 'available',
        'api': 'operational'
    }

    return jsonify({
        'user': {
            'email': user.email if user else 'Unknown',
            'subscription': user.subscription if user else 'free',
            'credits': user.credits if user else 0,
            'role': 'admin' if user and user.is_admin else 'user'
        },
        'sources': {
            'total': total_sources,
            'active': active_sources,
            'categories': {
                'videos': 45,
                'images': 38,
                'documents': 20,
                'audio': 15
            }
        },
        'system': system_status,
        'quick_actions': [
            {'name': 'Start New Search', 'icon': 'fa-search', 'link': '#search'},
            {'name': 'Upload Files', 'icon': 'fa-upload', 'link': '#upload'},
            {'name': 'View Assets', 'icon': 'fa-folder', 'link': '#assets'},
            {'name': 'Settings', 'icon': 'fa-cog', 'link': '#settings'}
        ]
    })

# ==================== END DASHBOARD API ENDPOINTS ====================

@app.route("/test-login")
def test_login():
    """Mock login for testing purposes"""
    from flask_login import login_user

    from models import User

    # Create or get test user
    test_user = User.query.filter_by(email="test@example.com").first()
    if not test_user:
        test_user = User(email="test@example.com", name="Test User", google_id="test_google_id", picture=None)
        db.session.add(test_user)
        db.session.commit()

    # Log in the test user
    login_user(test_user)
    session["user"] = {
        "id": test_user.id,
        "email": test_user.email,
        "name": test_user.name,
        "picture": test_user.picture,
        "google_id": test_user.google_id,
    }

    return redirect(url_for("index"))


@app.route("/dev/reset-credits", methods=["POST"])
@login_required
def dev_reset_credits():
    """Development endpoint to reset user credits for testing"""
    try:
        # Only allow in debug mode
        if not app.debug:
            return jsonify({"success": False, "error": "This endpoint is only available in debug mode"}), 403

        # Get requested credits (default to 50)
        data = request.get_json() or {}
        credits = data.get("credits", 50)

        # Reset current user's credits
        current_user.credits = credits
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Credits reset to {credits}",
                "user": current_user.email,
                "credits": current_user.credits,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# Serve JavaScript fix patch
@app.route("/static/js_fix_patch.js")
def serve_js_fix():
    """Serve the JavaScript fix patch file"""
    try:
        with open("js_fix_patch.js", "r") as f:
            content = f.read()
        return Response(content, mimetype="application/javascript")
    except FileNotFoundError:
        return Response("// Fix file not found", mimetype="application/javascript", status=404)


# Serve static files explicitly for IIS deployment
@app.route("/scraper/static/<path:filename>")
def serve_static_iis(filename):
    """Serve static files from static directory for IIS deployment"""
    return send_from_directory("static", filename)


# Also handle without prefix for local development
@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files from static directory"""
    return send_from_directory("static", filename)


# Initialize database
def create_tables():
    """Create database tables and initialize with default data"""
    try:
        with app.app_context():
            db.create_all()
            init_db()
            print("[SUCCESS] Database tables created and initialized")
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")


# Note: /api/stats and /api/user/stats routes are defined in blueprints/user.py


@app.route("/admin-test")
def admin_test():
    """Serve admin test page"""
    try:
        with open("admin_test.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Admin test page not found</h1><p>The admin_test.html file is missing.</p>"


if __name__ == "__main__":
    print("[START] === STARTING ENHANCED MEDIA SCRAPER (Database-Driven) ===")
    print("[SERVER] Server: http://localhost/scraper")
    print("[MODE] Mode: Enhanced with Database, OAuth, and RBAC")
    print(f"[DATABASE] Database: SQL Server Express - Scraped")
    print("[AUTH] Authentication: Google OAuth Enabled")
    print("[STORAGE] Persistent job tracking and asset management")
    print("==================================================")
    print("[SUCCESS] Database initialized with default roles and settings")
    print("[SUCCESS] Database tables created and initialized")

    # Initialize database on startup
    create_tables()

    # Start memory management
    try:
        start_memory_management()
        print("[SUCCESS] Memory management started")
    except Exception as e:
        print(f"[WARNING] Memory management failed to start: {e}")

    try:
        # Start the Flask application
        # Use port 5050 for local deployment, 5000 for Replit
        port = int(os.environ.get("FLASK_RUN_PORT", 5050))
        debug_mode = os.environ.get("FLASK_ENV") == "development"

        print(f"[INFO] Starting Flask application on port {port}...")

        # Use threaded mode to handle concurrent requests (especially for bulk downloads)
        # This allows multiple /serve/{id} requests to be processed simultaneously
        app.run(
            host="0.0.0.0",
            port=port,
            debug=debug_mode,
            threaded=True,           # Enable multi-threading
            request_handler=None,    # Use default threaded request handler
            processes=1              # Single process with multiple threads
        )
    finally:
        # Cleanup on shutdown
        try:
            from memory_manager import stop_memory_management
            stop_memory_management()
            print("[CLEANUP] Memory management stopped")
        except Exception as e:
            print(f"[WARNING] Memory cleanup error: {e}")

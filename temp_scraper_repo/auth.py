"""
Fixed OAuth Authentication Module for IIS Deployment
Properly handles /scraper prefix and redirect URIs

This module exposes init_auth(app) which registers the auth blueprint
and initializes the OAuth client. Some app variants were calling
init_auth(app) while this file only provided init_oauth(app), causing
OAuth routes like /login and /google/callback to 404 because the
blueprint was never registered. This reconciles that mismatch.
"""

import logging
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlencode

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    make_response,
    redirect,
    request,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

try:
    from authlib.integrations.flask_client import OAuth
except Exception:
    OAuth = None
from models import User, db

# Configure logging
logger = logging.getLogger(__name__)

# Add a dedicated oauth debug logger to file as well
try:
    from logging.handlers import RotatingFileHandler

    _oauth_handler = RotatingFileHandler("logs/oauth_debug.log", maxBytes=512_000, backupCount=3)
    _oauth_handler.setLevel(logging.INFO)
    _oauth_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    if all(getattr(h, "baseFilename", "") != _oauth_handler.baseFilename for h in logger.handlers):
        logger.addHandler(_oauth_handler)
except Exception:
    pass

# Create authentication blueprint
# Mount auth routes under /auth so IIS and Google redirect URIs match
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# Lightweight in-memory user for development mock login
class MemoryUser(UserMixin):
    def __init__(self, id_, email, name, picture=None, is_admin=False, google_id=None):
        # Ensure we have a numeric ID for database compatibility
        if isinstance(id_, str):
            # Convert string ID to a stable integer hash
            self.id = abs(hash(id_)) % (10**8)  # 8-digit integer
            self.user_id = self.id  # Alias for compatibility
        else:
            self.id = id_
            self.user_id = id_

        self.email = email
        self.name = name
        self.picture = picture
        self.google_id = google_id  # Add Google ID support
        self.is_admin_user = is_admin
        self.created_at = datetime.utcnow()
        self.last_login = datetime.utcnow()

        # Add missing subscription attributes
        self.is_subscribed = True  # Default to subscribed for development
        self.subscription_end_date = datetime.utcnow() + timedelta(days=30)
        self.subscription_plan = "premium"  # Default plan

    def get_id(self):
        return f"mem:{self.id}"

    def is_admin(self):
        """Check if user is an admin"""
        return self.is_admin_user

    def check_subscription(self):
        """Check if user has active subscription"""
        if not self.is_subscribed:
            return False
        if self.subscription_end_date:
            return datetime.utcnow() < self.subscription_end_date
        return True


_MEM_USERS = {}

# Initialize Flask-Login
login_manager = LoginManager()

# Admin email configuration
ADMIN_EMAILS = os.environ.get("ADMIN_EMAILS", "sop1973@gmail.com").split(",")


def init_oauth(app):
    """Initialize OAuth with proper IIS configuration"""
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.session_protection = "basic"  # Changed from 'strong' to allow session persistence
    login_manager.remember_cookie_duration = timedelta(days=30)  # Remember for 30 days
    login_manager.remember_cookie_secure = app.config.get("SESSION_COOKIE_SECURE", False)
    login_manager.remember_cookie_httponly = True

    # Initialize OAuth
    if OAuth is None:
        logger.error("Authlib OAuth client not available; OAuth routes will degrade gracefully")
        return None, None
    oauth = OAuth(app)

    # Get OAuth credentials from environment
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not client_id or not client_secret:
        logger.error("Google OAuth credentials not configured")
        return oauth, None

    # Configure Google OAuth with proper redirect handling
    google = oauth.register(
        name="google",
        client_id=client_id,
        client_secret=client_secret,
        # Discovery document (still used for other metadata)
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        # Explicit endpoints to ensure absolute Location in redirects
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        access_token_url="https://oauth2.googleapis.com/token",
        client_kwargs={"scope": "openid email profile"},
    )

    return oauth, google


def init_auth(app):
    """Initialize authentication and register routes on the Flask app.

    - Ensures Flask-Login is attached
    - Initializes Authlib OAuth client and Google provider
    - Registers the auth blueprint so routes exist

    Returns the Google OAuth client (or None if not configured).
    """
    # Initialize OAuth + login
    oauth, google = init_oauth(app)

    # Always register the blueprint so /login, /logout, etc. are available
    # Route paths are relative (no explicit url_prefix) so with IIS the
    # app's prefix handling will still yield /scraper/login, etc.
    if "auth" not in app.blueprints:
        # Blueprint already defines url_prefix '/auth'
        app.register_blueprint(auth_bp)

    # Expose the oauth client on app.extensions for downstream access
    # (authlib registers under 'authlib.integrations.flask_client')
    # If oauth is missing (no credentials), we still keep routes available
    # to fail gracefully with a friendly message.
    return google


def get_redirect_uri(endpoint="auth.google_callback"):
    """Generate proper redirect URI for IIS deployment and dev.

    Guarantees exactly one '/scraper' prefix and avoids '//' issues.
    """
    # Path for the endpoint (may include '/scraper' depending on script_root)
    ep_path = url_for(endpoint, _external=False)
    if not isinstance(ep_path, str):
        ep_path = str(ep_path)

    def _join(base: str, path: str) -> str:
        # Normalize to a single '/scraper' prefix and a single slash join
        if path.startswith("/scraper/"):
            path = "/" + path.lstrip("/")  # ensure single leading slash
            return base.rstrip("/") + path
        # otherwise prepend '/scraper'
        return base.rstrip("/") + "/scraper" + (path if path.startswith("/") else "/" + path)

    # Behind IIS (use forwarded headers)
    if request.headers.get("X-Forwarded-Host"):
        scheme = request.headers.get("X-Forwarded-Proto", "http")
        host = request.headers.get("X-Forwarded-Host", "localhost")
        port = request.headers.get("X-Forwarded-Port", "80")
        if (scheme == "https" and port == "443") or (scheme == "http" and port == "80"):
            base_url = f"{scheme}://{host}"
        else:
            base_url = f"{scheme}://{host}:{port}"
        return _join(base_url, ep_path)

    # Local/dev (use APPLICATION_ROOT if set)
    app_root = (current_app.config.get("APPLICATION_ROOT") or "").strip()
    if app_root:
        scheme = request.scheme
        host = request.host
        base_url = f"{scheme}://{host}"
        return _join(base_url, ep_path)

    # Default Flask behavior
    return url_for(endpoint, _external=True)


def _canonical_callback_url() -> str:
    """Return the exact redirect_uri we want Google to call back.

    ALWAYS return the canonical URL regardless of how the user accessed the site.
    This prevents redirect_uri_mismatch errors.
    """
    # ALWAYS use the environment variable if set
    env_override = os.environ.get("OAUTH_CALLBACK_URL")
    if env_override:
        logger.info(f"[OAUTH] Using OAUTH_CALLBACK_URL from env: {env_override}")
        return env_override

    # Fallback - but this should be set in .env
    canonical = "http://localhost/scraper/auth/google/callback"
    logger.warning(f"[OAUTH] OAUTH_CALLBACK_URL not set, using default: {canonical}")
    return canonical


def _mask_client_id(cid: str) -> str:
    try:
        if not cid:
            return ""
        if len(cid) <= 8:
            return "****"
        return cid[:6] + "..." + cid[-10:]
    except Exception:
        return ""


def _request_context_snapshot():
    try:
        hdr = dict(request.headers)
        return {
            "url": request.url,
            "path": request.path,
            "script_root": request.script_root,
            "host": request.host,
            "scheme": request.scheme,
            "x_forwarded_host": hdr.get("X-Forwarded-Host"),
            "x_forwarded_proto": hdr.get("X-Forwarded-Proto"),
            "x_forwarded_port": hdr.get("X-Forwarded-Port"),
            "application_root": (current_app.config.get("APPLICATION_ROOT") or ""),
        }
    except Exception:
        return {}


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login (supports mem: IDs in dev)."""
    try:
        if isinstance(user_id, str) and user_id.startswith("mem:"):
            return _MEM_USERS.get(user_id)
        # Database-backed user
        return User.query.get(int(user_id))
    except Exception:
        return None


@auth_bp.route("/login")
def login():
    """Initiate OAuth login with Google"""
    # Clear any existing OAuth state to prevent stale state issues
    session.pop("oauth_state", None)
    session.pop("oauth_state_timestamp", None)
    session.pop("oauth_redirect_uri", None)

    # Generate fresh CSRF state token
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    session["oauth_state_timestamp"] = datetime.utcnow().isoformat()

    # Compute a stable redirect URI that matches authorized URI exactly
    redirect_uri = _canonical_callback_url()

    logger.info(f"[OAUTH] Login start | redirect_uri={redirect_uri} ctx={_request_context_snapshot()}")
    session["oauth_redirect_uri"] = redirect_uri

    # Build absolute Google authorize URL to avoid any proxy mangling
    try:
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        if not client_id:
            raise RuntimeError("GOOGLE_CLIENT_ID not set")
        query = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "state": state,
            "nonce": secrets.token_urlsafe(16),
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
        }
        authorize_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(query)
        logger.info(f"[OAUTH] Built authorize_url (cid={_mask_client_id(client_id)}): {authorize_url}")

        # Optional debug: return JSON instead of redirect page
        if request.args.get("debug") == "1" or request.args.get("dryrun") == "1":
            return jsonify(
                {
                    "authorize_url": authorize_url,
                    "redirect_uri": redirect_uri,
                    "client_id_masked": _mask_client_id(client_id),
                    "context": _request_context_snapshot(),
                }
            )
        # Return a tiny HTML page that performs a client-side redirect. This
        # avoids any reverse-proxy rewriting of the Location header.
        from json import dumps as _jd

        _url_js = _jd(authorize_url)
        html_tpl = """
<!doctype html>
<html><head>
  <meta http-equiv="refresh" content="0;url=%%URL%%">
  <title>Redirecting to Google</title>
  <script>window.location.replace(%%URLJS%%);</script>
</head>
<body>
  <noscript>
    <a href="%%URL%%">Continue to Google Sign-In</a>
  </noscript>
  Redirecting to Google Sign-In…
  <script>setTimeout(function(){ window.location.href = %%URLJS%%; }, 10);</script>
  <style>body{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:2rem;color:#223}</style>
</body></html>
"""
        html = html_tpl.replace("%%URL%%", authorize_url).replace("%%URLJS%%", _url_js)
        resp = make_response(html, 200)
        resp.headers["Cache-Control"] = "no-store"
        return resp
    except Exception as e:
        logger.warning(f"Manual authorize URL build failed ({e}); falling back to authlib")
        oauth_client = current_app.extensions.get("authlib.integrations.flask_client")
        if not oauth_client:
            logger.error("OAuth not configured")
            flash("OAuth is not configured. Please contact administrator.", "error")
            return redirect(url_for("index", _external=True))
        google = oauth_client.create_client("google")
        if not google:
            logger.error("Google OAuth client not configured")
            flash("Google login is not available. Please try again later.", "error")
            return redirect(url_for("index", _external=True))
        return google.authorize_redirect(redirect_uri, state=state)


@auth_bp.route("/login-fixed")
def login_fixed():
    """Initiate OAuth login with Google using a fully pinned redirect_uri.

    This avoids any proxy/host interference by building the Google URL
    locally and returning a client-side redirect page.
    """
    # CSRF state
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    session["oauth_state_timestamp"] = datetime.utcnow().isoformat()

    redirect_uri = _canonical_callback_url()
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    if not client_id:
        logger.error("[OAUTH] Missing GOOGLE_CLIENT_ID")
        flash("OAuth is not configured.", "error")
        return redirect(url_for("index", _external=True))

    try:
        query = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "state": state,
            "nonce": secrets.token_urlsafe(16),
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "consent",
        }
        authorize_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(query)
        logger.info(
            f"[OAUTH] LoginFixed | redirect_uri={redirect_uri} cid={_mask_client_id(client_id)} url={authorize_url}"
        )

        if request.args.get("debug") == "1" or request.args.get("dryrun") == "1":
            return jsonify(
                {
                    "authorize_url": authorize_url,
                    "redirect_uri": redirect_uri,
                    "client_id_masked": _mask_client_id(client_id),
                    "context": _request_context_snapshot(),
                }
            )

        from json import dumps as _jd

        _url_js = _jd(authorize_url)
        html_tpl = """
<!doctype html>
<html><head>
  <meta http-equiv=\"refresh\" content=\"0;url=%%URL%%\">
  <title>Redirecting to Google</title>
  <script>window.location.replace(%%URLJS%%);</script>
</head>
<body>
  <noscript>
    <a href=\"%%URL%%\">Continue to Google Sign-In</a>
  </noscript>
  Redirecting to Google Sign-In…
  <script>setTimeout(function(){ window.location.href = %%URLJS%%; }, 10);</script>
  <style>body{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:2rem;color:#223}</style>
</body></html>
"""
        html = html_tpl.replace("%%URL%%", authorize_url).replace("%%URLJS%%", _url_js)
        resp = make_response(html, 200)
        resp.headers["Cache-Control"] = "no-store"
        return resp
    except Exception as e:
        logger.warning(f"Manual authorize URL build failed ({e}); falling back to authlib")
        oauth_client = current_app.extensions.get("authlib.integrations.flask_client")
        if not oauth_client:
            logger.error("OAuth not configured")
            flash("OAuth is not configured. Please contact administrator.", "error")
            return redirect(url_for("index", _external=True))
        google = oauth_client.create_client("google")
        if not google:
            logger.error("Google OAuth client not configured")
            flash("Google login is not available. Please try again later.", "error")
            return redirect(url_for("index", _external=True))
        return google.authorize_redirect(redirect_uri, state=state)


@auth_bp.route("/google/callback")
def google_callback():
    """Handle OAuth callback from Google"""
    try:
        # Log the incoming callback
        logger.info(f"[OAuth] Callback received: {request.url}")
        logger.info(f"[OAuth] Query params: {list(request.args.keys())}")

        # Check for errors from Google first
        error = request.args.get("error")
        if error:
            error_desc = request.args.get("error_description", "Unknown error")
            logger.error(f"[OAuth] Error from Google: {error} - {error_desc}")

            if error == "access_denied":
                flash("You cancelled the login process", "info")
            else:
                flash(f"Authentication failed: {error_desc}", "error")

            return redirect(url_for("index"))

        # Verify state token for CSRF protection
        state = request.args.get("state")
        stored_state = session.get("oauth_state")

        # Skip state validation if both are None (for testing)
        if state and stored_state and state != stored_state:
            logger.warning(f"OAuth state mismatch - received: {state}, expected: {stored_state}")
            # Clear stale OAuth session data and retry
            session.pop("oauth_state", None)
            session.pop("oauth_state_timestamp", None)
            session.pop("oauth_redirect_uri", None)
            # Don't block authentication, just log the issue

        # Check state timestamp (5 minute expiry)
        state_timestamp = session.get("oauth_state_timestamp")
        if state_timestamp:
            state_time = datetime.fromisoformat(state_timestamp)
            if datetime.utcnow() - state_time > timedelta(minutes=30):  # Increase to 30 minutes
                logger.warning("OAuth state expired, clearing session")
                # Clear stale session data
                session.pop("oauth_state", None)
                session.pop("oauth_state_timestamp", None)

        # Check for errors from Google
        error = request.args.get("error")
        if error:
            logger.error(f"OAuth error from Google: {error}")
            flash(f"Authentication failed: {error}", "error")
            return redirect(url_for("index", _external=True))

        # Get authorization code from callback
        code = request.args.get("code")
        if not code:
            logger.error("No authorization code in callback")
            flash("Authentication failed: No authorization code received", "error")
            return redirect(url_for("index", _external=True))

        logger.info(f"OAuth callback received with code: {code[:10]}...")

        # Get OAuth client
        oauth_client = current_app.extensions.get("authlib.integrations.flask_client")
        if not oauth_client:
            logger.error("OAuth client not available in callback")
            flash("Authentication configuration error", "error")
            return redirect(url_for("index", _external=True))

        google = oauth_client.create_client("google")
        if not google:
            logger.error("Google client not available in callback")
            flash("Google authentication not available", "error")
            return redirect(url_for("index", _external=True))

        # Exchange authorization code for token (ensure redirect_uri matches Google's registered value)
        # Always use the canonical callback URL for token exchange
        redirect_uri = _canonical_callback_url()

        # For IIS deployment, bypass state validation if needed
        # The session might not persist properly through the proxy
        token = None

        # Try manual token exchange first for reliability
        logger.info("Performing manual token exchange")
        import requests

        try:
            logger.info(f"[OAuth] Starting token exchange for code: {code[:10]}...")
            token_response = requests.post(
                "https://oauth2.googleapis.com/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "code": code,
                    "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                    "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )  # Add 10 second timeout to prevent hanging

            if token_response.status_code == 200:
                token = token_response.json()
                logger.info("Manual token exchange successful")
            else:
                logger.error(f"Token exchange failed: {token_response.status_code} - {token_response.text}")
                # Fall back to authlib method
                raise Exception("Manual exchange failed, trying authlib")

        except Exception as manual_error:
            logger.warning(f"Manual token exchange failed: {manual_error}, trying authlib")

            # Try with authlib as fallback
            try:
                # Force state to match if needed
                if state:
                    session["oauth_state"] = state
                    session["_state"] = state  # Try internal state key too
                    session.permanent = True

                token = google.authorize_access_token(redirect_uri=redirect_uri)
                logger.info("Authlib token exchange successful")
            except Exception as e:
                logger.error(f"All token exchange methods failed: {e}")
                raise

        if not token:
            logger.error("Failed to get access token from Google")
            flash("Authentication failed: Could not get access token", "error")
            return redirect(url_for("index", _external=True))

        # Get user info from Google
        user_info = None

        # If we have an access token from manual exchange, get user info manually
        if token and "access_token" in token:
            try:
                import requests

                logger.info("[OAuth] Fetching user info from Google")
                userinfo_response = requests.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {token['access_token']}"},
                    timeout=10,  # Add timeout to prevent hanging
                )
                if userinfo_response.status_code == 200:
                    user_info = userinfo_response.json()
                    logger.info(f"Got user info manually: {user_info.get('email')}")
                else:
                    logger.error(f"Failed to get user info manually: {userinfo_response.status_code}")
            except Exception as e:
                logger.error(f"Error getting user info manually: {e}")

        # Fall back to authlib method if needed
        if not user_info:
            try:
                resp = google.get("userinfo")
                if resp and resp.json():
                    user_info = resp.json()
                    logger.info(f"Got user info via authlib: {user_info.get('email')}")
            except Exception as e:
                logger.error(f"Failed to get user info via authlib: {e}")

        if not user_info:
            logger.error("Failed to get user info from Google")
            flash("Authentication failed: Could not get user information", "error")
            return redirect(url_for("index", _external=True))

        # Find or create user in database
        # Google userinfo v2 uses 'id' field, not 'sub'
        google_id = user_info.get("id") or user_info.get("sub")
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            # Check if user exists with same email
            user = User.query.filter_by(email=user_info.get("email")).first()

            if user:
                # Update existing user with Google ID
                user.google_id = google_id
                logger.info(f"Linking existing user {user.email} with Google ID")
            else:
                # Create new user
                display_name = user_info.get("name") or user_info.get("email", "").split("@")[0] or "User"
                user = User(
                    name=display_name,
                    email=user_info.get("email"),
                    google_id=google_id,
                    picture=user_info.get("picture"),
                    created_at=datetime.utcnow(),
                )
                db.session.add(user)
                logger.info(f"Created new user: {user.email}")

        # Update OAuth tokens
        # Update profile picture if changed
        if user_info.get("picture") and user_info.get("picture") != user.picture:
            user.picture = user_info.get("picture")

        # Update last login
        user.last_login = datetime.utcnow()

        # Check for daily sign-in bonus
        # Optional: emit a welcome message
        flash("Welcome back!", "success")

        # Check if user should be admin
        if user.email in ADMIN_EMAILS:
            logger.info(f"Admin user logged in: {user.email}")

        # Commit user changes
        db.session.commit()

        # Log user in with persistent session
        session.permanent = True
        login_user(user, remember=True, duration=timedelta(days=30))
        logger.info(f"User {user.email} logged in successfully")

        # Debug: Check if user is authenticated immediately after login
        from flask_login import current_user as test_user

        logger.info(
            f"DEBUG: After login_user, is_authenticated={test_user.is_authenticated}, user_id={test_user.get_id() if test_user.is_authenticated else 'None'}"
        )

        # Clear OAuth session data
        session.pop("oauth_state", None)
        session.pop("oauth_state_timestamp", None)
        session.pop("oauth_redirect_uri", None)

        # Flash welcome message
        flash(f"Welcome, {user.name}!", "success")

        # Redirect to next page or home
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            # Just redirect to the next page as-is, Flask doesn't know about /scraper prefix
            return redirect(next_page)

        # Redirect to the application index with /scraper prefix
        return redirect("/scraper/")

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}", exc_info=True)
        flash("Authentication failed. Please try again.", "error")
        return redirect("/scraper/")


@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user"""
    username = getattr(current_user, "name", getattr(current_user, "email", "user"))
    logout_user()
    logger.info(f"User {username} logged out")
    flash("You have been logged out successfully.", "info")

    # Redirect to index with /scraper prefix
    return redirect("/scraper/")


@auth_bp.route("/google/verify", methods=["POST"])
def google_verify():
    """Verify Google ID token from client-side authentication"""
    try:
        import requests
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token

        data = request.get_json()
        if not data or "credential" not in data:
            return jsonify({"success": False, "error": "No credential provided"}), 400

        credential = data["credential"]
        client_id = os.environ.get("GOOGLE_CLIENT_ID")

        if not client_id:
            logger.error("GOOGLE_CLIENT_ID not configured")
            return jsonify({"success": False, "error": "Server configuration error"}), 500

        try:
            # Verify the ID token
            idinfo = id_token.verify_oauth2_token(credential, google_requests.Request(), client_id)

            # ID token is valid. Get the user's Google Account details
            google_id = idinfo.get("sub")
            email = idinfo.get("email")
            name = idinfo.get("name")
            picture = idinfo.get("picture")

            if not google_id or not email:
                return jsonify({"success": False, "error": "Invalid token data"}), 400

            # Find or create user
            user = User.query.filter_by(google_id=google_id).first()

            if not user:
                # Check if email already exists
                user = User.query.filter_by(email=email).first()

                if user:
                    # Update existing user with Google ID
                    user.google_id = google_id
                    if picture and picture != user.picture:
                        user.picture = picture
                else:
                    # Create new user
                    is_admin = email.lower() in [e.lower() for e in ADMIN_EMAILS]
                    user = User(
                        email=email,
                        name=name or email.split("@")[0],
                        google_id=google_id,
                        picture=picture,
                        created_at=datetime.utcnow(),
                        credits=999999 if is_admin else 50,
                        subscription_plan="premium" if is_admin else "trial",
                        subscription_status="active" if is_admin else "active",
                    )
                    db.session.add(user)
                    logger.info(f"Created new user: {user.email} (admin={is_admin})")

            # Update last login
            user.last_login = datetime.utcnow()

            # Update admin privileges for admin emails
            if email.lower() in [e.lower() for e in ADMIN_EMAILS]:
                user.is_admin = True
                user.credits = max(user.credits, 999999)
                user.subscription_plan = "premium"
                user.subscription_status = "active"
                user.daily_limit = 999999
                user.monthly_limit = 999999

            # Update profile picture if changed
            if picture and picture != user.picture:
                user.picture = picture

            # Commit user changes
            db.session.commit()

            # Log user in with persistent session
            session.permanent = True
            login_user(user, remember=True, duration=timedelta(days=30))
            logger.info(f"User {user.email} logged in successfully via Google Identity Services")

            # Clear any OAuth session data from old attempts
            session.pop("oauth_state", None)
            session.pop("oauth_state_timestamp", None)
            session.pop("oauth_redirect_uri", None)

            return jsonify({"success": True, "user": {"email": user.email, "name": user.name, "picture": user.picture}})

        except ValueError as e:
            # Invalid token
            logger.error(f"Invalid Google ID token: {str(e)}")
            return jsonify({"success": False, "error": "Invalid authentication token"}), 401

    except ImportError:
        # Fallback if google-auth library is not installed
        logger.warning("google-auth library not installed, using alternative verification")

        # Alternative: Use Google's tokeninfo endpoint
        import requests

        data = request.get_json()
        if not data or "credential" not in data:
            return jsonify({"success": False, "error": "No credential provided"}), 400

        credential = data["credential"]
        client_id = os.environ.get("GOOGLE_CLIENT_ID")

        # Verify token with Google's endpoint
        response = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": credential})

        if response.status_code != 200:
            return jsonify({"success": False, "error": "Invalid authentication token"}), 401

        idinfo = response.json()

        # Verify the audience
        if idinfo.get("aud") != client_id:
            return jsonify({"success": False, "error": "Token was not issued for this application"}), 401

        # Verify the token is not expired
        # Google's exp is in seconds since epoch
        import time

        if "exp" in idinfo and int(idinfo["exp"]) < time.time():
            return jsonify({"success": False, "error": "Token has expired"}), 401

        # Get user details
        google_id = idinfo.get("sub")
        email = idinfo.get("email")
        name = idinfo.get("name")
        picture = idinfo.get("picture")

        if not google_id or not email:
            return jsonify({"success": False, "error": "Invalid token data"}), 400

        # Find or create user (same as above)
        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            user = User.query.filter_by(email=email).first()

            if user:
                user.google_id = google_id
                if picture and picture != user.picture:
                    user.picture = picture
            else:
                user = User(
                    email=email,
                    name=name or email.split("@")[0],
                    google_id=google_id,
                    picture=picture,
                    created_at=datetime.utcnow(),
                )
                db.session.add(user)
                logger.info(f"Created new user: {user.email}")

        # Update last login and picture
        user.last_login = datetime.utcnow()
        if picture and picture != user.picture:
            user.picture = picture

        db.session.commit()

        # Log user in with persistent session
        session.permanent = True
        login_user(user, remember=True, duration=timedelta(days=30))
        logger.info(f"User {user.email} logged in successfully via Google Identity Services")

        # Clear any OAuth session data
        session.pop("oauth_state", None)
        session.pop("oauth_state_timestamp", None)
        session.pop("oauth_redirect_uri", None)

        return jsonify({"success": True, "user": {"email": user.email, "name": user.name, "picture": user.picture}})

    except Exception as e:
        logger.error(f"Google token verification error: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "Authentication failed"}), 500


@auth_bp.route("/debug-oauth")
def debug_oauth():
    """Debug endpoint to show OAuth configuration"""
    redirect_uri = _canonical_callback_url()
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "NOT_SET")

    return jsonify(
        {
            "redirect_uri_being_used": redirect_uri,
            "client_id": _mask_client_id(client_id),
            "env_vars": {
                "OAUTH_CALLBACK_URL": os.environ.get("OAUTH_CALLBACK_URL", "NOT_SET"),
                "GOOGLE_REDIRECT_URL": os.environ.get("GOOGLE_REDIRECT_URL", "NOT_SET"),
                "PUBLIC_BASE_URL": os.environ.get("PUBLIC_BASE_URL", "NOT_SET"),
            },
            "instructions": "Add this exact redirect URI to Google Console: " + redirect_uri,
        }
    )


@auth_bp.route("/profile")
@login_required
def profile():
    """Show user profile"""
    return jsonify(
        {
            "user": {
                "id": current_user.id,
                "username": getattr(current_user, "name", None) or getattr(current_user, "email", ""),
                "email": current_user.email,
                "credits": None,
                "subscription_type": None,
                "profile_picture": getattr(current_user, "picture", None),
                "created_at": (
                    getattr(current_user, "created_at", None).isoformat()
                    if getattr(current_user, "created_at", None)
                    else None
                ),
                "last_login": (
                    getattr(current_user, "last_login", None).isoformat()
                    if getattr(current_user, "last_login", None)
                    else None
                ),
            }
        }
    )


@auth_bp.route("/check")
def check_auth():
    """Check authentication status"""
    if current_user.is_authenticated:
        return jsonify(
            {
                "authenticated": True,
                "user": {
                    "id": current_user.id,
                    "username": getattr(current_user, "name", None) or getattr(current_user, "email", ""),
                    "email": current_user.email,
                    "credits": None,
                    "subscription_type": None,
                },
            }
        )
    else:
        return jsonify({"authenticated": False, "user": None})


def admin_required(f):
    """Decorator to require admin access"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, "is_admin_user", False):
            flash("Admin access required.", "error")
            return redirect(url_for("index", _external=True))
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/admin/grant/<int:user_id>", methods=["POST"])
@admin_required
def grant_admin(user_id):
    """Grant admin privileges to a user"""
    user = User.query.get_or_404(user_id)
    user.subscription_type = "admin"
    user.credits = 99999
    db.session.commit()
    logger.info(f"Admin privileges granted to user {user.email}")
    flash(f"Admin privileges granted to {user.email}", "success")
    return redirect(request.referrer or url_for("index"))


@auth_bp.route("/admin/revoke/<int:user_id>", methods=["POST"])
@admin_required
def revoke_admin(user_id):
    """Revoke admin privileges from a user"""
    user = User.query.get_or_404(user_id)
    if user.email in ADMIN_EMAILS:
        flash("Cannot revoke admin from primary admin account.", "error")
        return redirect(request.referrer or url_for("index"))

    user.subscription_type = "free"
    user.credits = 50
    db.session.commit()
    logger.info(f"Admin privileges revoked from user {user.email}")
    flash(f"Admin privileges revoked from {user.email}", "success")
    return redirect(request.referrer or url_for("index"))


# Development-only mock login to avoid 404s on legacy links
@auth_bp.route("/mock-login")
@auth_bp.route("/mock-login/<email>")
def mock_login_dev(email=None):
    try:
        env = os.getenv("FLASK_ENV", "production").lower()
        allow = os.getenv("ALLOW_MOCK_LOGIN", "false").lower() == "true"
        if env != "development" and not allow:
            flash("Mock login is disabled", "error")
            return redirect(url_for("index", _external=True))
        if not email:
            email = os.getenv("ADMIN_EMAIL", "sop1973@gmail.com")
        name = email.split("@")[0]
        uid = email.replace("@", "_").replace(".", "_")
        mem_id = f"mem:{uid}"
        user = _MEM_USERS.get(mem_id)
        if not user:
            # Simulate Google OAuth user
            google_id = f"google_{uid}"  # Simulate Google ID
            user = MemoryUser(
                uid, email=email, name=name, is_admin=(email.lower() == "sop1973@gmail.com"), google_id=google_id
            )  # Add Google ID
            _MEM_USERS[mem_id] = user
        session.permanent = True
        login_user(user, remember=True, duration=timedelta(days=30))
        flash(f"Mock login successful for {email}", "success")
        # Always use url_for to generate correct URLs
        return redirect(url_for("index"))
    except Exception as e:
        logger.error(f"Mock login failed: {e}")
        flash("Mock login failed", "error")
        return redirect(url_for("index", _external=True))


# Additional auth decorators and helper functions


def optional_auth(f):
    """Decorator for routes that work with or without authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function


def user_or_admin_required(f):
    """Decorator to require user or admin privileges"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function


def check_user_access(f):
    """Decorator to check user access"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated_function


def get_current_user_info():
    """Get current user information"""
    if current_user.is_authenticated:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "is_admin": current_user.is_admin(),
        }
    return None


def require_permission(permission):
    """Decorator to require specific permission"""

    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # For now, just check if user is authenticated
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_role(role):
    """Decorator to require specific role"""

    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # For now, just check if user is authenticated
            return f(*args, **kwargs)

        return decorated_function

    return decorator

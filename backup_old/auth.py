"""
Authentication and Authorization Module
Handles Google OAuth login, user management, and role-based access control
"""

import os
import logging
from datetime import datetime
from functools import wraps
from flask import Blueprint, redirect, url_for, session, flash, request, jsonify, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized, oauth_error
# Remove problematic import for now
# from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from models import db, User, Role, UserRole, OAuth
import secrets

# Set up detailed logging for OAuth
logging.basicConfig(level=logging.DEBUG)
oauth_logger = logging.getLogger('oauth_debug')
oauth_logger.setLevel(logging.DEBUG)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('🔍 OAUTH: %(asctime)s - %(message)s')
console_handler.setFormatter(formatter)
oauth_logger.addHandler(console_handler)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize Flask-Login
login_manager = LoginManager()

def init_auth(app):
    """Initialize authentication for the Flask app"""
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Enable insecure transport for development (HTTP instead of HTTPS)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    # OAuth Configuration
    oauth_logger.info("=== INITIALIZING GOOGLE OAUTH ===")
    oauth_logger.info(f"CLIENT_ID: {os.environ.get('GOOGLE_CLIENT_ID', 'NOT_SET')}")
    oauth_logger.info(f"CLIENT_SECRET: {'SET' if os.environ.get('GOOGLE_CLIENT_SECRET') else 'NOT_SET'}")
    oauth_logger.info(f"OAUTHLIB_INSECURE_TRANSPORT: {os.environ.get('OAUTHLIB_INSECURE_TRANSPORT', 'NOT_SET')}")

    google = make_google_blueprint(
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
        reprompt_consent=False,
        redirect_to='index'
    )

    oauth_logger.info(f"Google Blueprint created successfully")
    oauth_logger.info(f"Google Blueprint name: {google.name}")
    
    # Enhanced OAuth error handling - set up BEFORE registering blueprint
    @oauth_error.connect_via(google)
    def google_error(blueprint, message, response):
        oauth_logger.error("=== OAUTH ERROR OCCURRED ===")
        oauth_logger.error(f"Blueprint: {blueprint.name}")
        oauth_logger.error(f"Error message: {message}")
        oauth_logger.error(f"Response: {response}")
        oauth_logger.error(f"Response status: {getattr(response, 'status_code', 'Unknown')}")
        oauth_logger.error(f"Response text: {getattr(response, 'text', 'No text')}")
        oauth_logger.error(f"Response headers: {getattr(response, 'headers', 'No headers')}")
        
        flash(f"OAuth error: {message}", "error")
        return redirect(url_for("index"))

    # Enhanced OAuth success handling - set up BEFORE registering blueprint
    @oauth_authorized.connect_via(google)
    def google_logged_in(blueprint, token):
        """Handle successful Google OAuth login"""
        try:
            oauth_logger.info("=== OAUTH AUTHORIZED HANDLER CALLED ===")
            
            if not token:
                oauth_logger.error("No token received from Google")
                flash("Failed to log in with Google.", category="error")
                return False
            
            oauth_logger.info(f"Token received: {bool(token)}")
            
            # Get user info from Google
            resp = blueprint.session.get("/oauth2/v2/userinfo")
            if not resp.ok:
                oauth_logger.error(f"Failed to fetch user info: {resp.status_code} - {resp.text}")
                flash("Failed to fetch user information from Google.", category="error")
                return False
            
            google_user_info = resp.json()
            oauth_logger.info(f"Google user info received: {google_user_info.get('email', 'No email')}")
            
            # Find or create user in database
            user = User.query.filter_by(google_id=google_user_info["id"]).first()
            
            if not user:
                # Create new user
                oauth_logger.info(f"Creating new user: {google_user_info['email']}")
                
                # Get default user role
                user_role = Role.query.filter_by(name='user').first()
                if not user_role:
                    oauth_logger.error("Default 'user' role not found in database")
                    # Try to create default roles if they don't exist
                    try:
                        user_role = Role(
                            name='user',
                            description='Standard user role',
                            permissions='["read_own_assets", "create_jobs", "manage_own_profile"]'
                        )
                        db.session.add(user_role)
                        db.session.commit()
                        oauth_logger.info("Created default 'user' role")
                    except Exception as role_error:
                        oauth_logger.error(f"Failed to create default role: {role_error}")
                        return redirect(url_for('index'))
                
                try:
                    # Create user without role_id (it doesn't exist in the model)
                    user = User(
                        google_id=google_user_info['id'],
                        email=google_user_info['email'],
                        name=google_user_info.get('name', google_user_info['email'].split('@')[0]),
                        picture=google_user_info.get('picture'),
                        is_active=True,
                        created_at=datetime.utcnow(),
                        last_login=datetime.utcnow()
                    )
                    
                    # Add user to database first
                    db.session.add(user)
                    db.session.flush()  # Get user ID without committing
                    
                    # Now create the UserRole relationship
                    user_role_assignment = UserRole(
                        user_id=user.id,
                        role_id=user_role.id,
                        assigned_at=datetime.utcnow()
                    )
                    db.session.add(user_role_assignment)
                    
                    # Commit both user and role assignment
                    db.session.commit()
                    oauth_logger.info(f"User created successfully with role: {user.email}")
                    
                except Exception as e:
                    db.session.rollback()
                    oauth_logger.error(f"Failed to create user: {e}")
                    return redirect(url_for('index'))
            else:
                # Update existing user's last login
                try:
                    user.last_login = datetime.utcnow()
                    user.name = google_user_info.get('name', user.name)  # Update name if changed
                    user.picture = google_user_info.get('picture', user.picture)  # Update picture if changed
                    db.session.commit()
                    oauth_logger.info(f"Updated existing user: {user.email}")
                except Exception as e:
                    db.session.rollback()
                    oauth_logger.error(f"Failed to update user: {e}")
            
            # Log in the user
            login_user(user)
            oauth_logger.info(f"User logged in successfully: {user.email}")
            
            return redirect(url_for('index'))
            
        except Exception as e:
            oauth_logger.error(f"OAuth login error: {str(e)}")
            flash("An error occurred during login. Please try again.", category="error")
            return False
    
    # Register blueprints AFTER setting up decorators
    app.register_blueprint(google, url_prefix='/auth')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return google

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

@auth_bp.route('/login')
def login():
    oauth_logger.info("=== LOGIN ROUTE ACCESSED ===")
    oauth_logger.info(f"Request URL: {request.url}")
    oauth_logger.info(f"Request args: {request.args}")
    
    if current_user.is_authenticated:
        oauth_logger.info("User already authenticated, redirecting to index")
        return redirect(url_for('index'))
    
    oauth_logger.info("Redirecting to Google OAuth...")
    return redirect(url_for("google.login"))

@auth_bp.route('/logout')
@login_required
def logout():
    oauth_logger.info(f"User {current_user.name} logging out")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return jsonify(current_user.to_dict())

@auth_bp.route('/users')
@login_required
def list_users():
    """List all users (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users],
        'total': len(users)
    })

@auth_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@login_required
def update_user_role(user_id):
    """Update user role (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    role_name = data.get('role')
    
    if not role_name:
        return jsonify({'error': 'Role name is required.'}), 400
    
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({'error': 'Invalid role.'}), 400
    
    # Remove existing roles for this user
    UserRole.query.filter_by(user_id=user.id).delete()
    
    # Add new role
    user_role = UserRole(user_id=user.id, role_id=role.id)
    db.session.add(user_role)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'User {user.name} role updated to {role.name}',
        'user': user.to_dict()
    })

@auth_bp.route('/users/<int:user_id>/toggle', methods=['PUT'])
@login_required
def toggle_user_status(user_id):
    """Toggle user active status (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot deactivate your own account.'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({
        'success': True,
        'message': f'User {user.name} has been {status}',
        'user': user.to_dict()
    })

# Role-based access control decorators
def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_permission(permission):
                if request.is_json:
                    return jsonify({'error': 'Insufficient permissions'}), 403
                flash('You do not have permission to access this resource.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role_name):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_role(role_name):
                if request.is_json:
                    return jsonify({'error': f'Role {role_name} required'}), 403
                flash(f'You need {role_name} role to access this resource.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return require_role('admin')(f)

def user_or_admin_required(f):
    """Decorator to require user or admin role (excludes guests)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login', next=request.url))
        
        if current_user.has_role('guest'):
            if request.is_json:
                return jsonify({'error': 'Guest access not allowed for this action'}), 403
            flash('Please log in with a user account to perform this action.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        return f(*args, **kwargs)
    return decorated_function

def check_user_access(user_id_field='user_id'):
    """Decorator to check if user can access their own resources or is admin"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect(url_for('auth.login', next=request.url))
            
            # Admin can access everything
            if current_user.is_admin():
                return f(*args, **kwargs)
            
            # Get user_id from various sources
            resource_user_id = None
            
            # Check URL parameters
            if user_id_field in kwargs:
                resource_user_id = kwargs[user_id_field]
            
            # Check request JSON
            elif request.is_json:
                data = request.get_json()
                resource_user_id = data.get(user_id_field)
            
            # Check query parameters
            elif request.args.get(user_id_field):
                resource_user_id = int(request.args.get(user_id_field))
            
            # If no user_id specified, assume current user
            if resource_user_id is None:
                return f(*args, **kwargs)
            
            # Check if user is accessing their own resource
            if int(resource_user_id) != current_user.id:
                if request.is_json:
                    return jsonify({'error': 'Access denied to other users resources'}), 403
                flash('You can only access your own resources.', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def optional_auth(f):
    """Decorator for routes that work with or without authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This decorator doesn't enforce authentication
        # but provides information about current user if available
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_info():
    """Helper function to get current user info for templates"""
    if current_user.is_authenticated:
        # Get all permissions from all user roles
        all_permissions = []
        for user_role in current_user.user_roles:
            if user_role.role:
                all_permissions.extend(user_role.role.get_permissions())
        
        return {
            'authenticated': True,
            'user': current_user.to_dict(),
            'permissions': list(set(all_permissions))  # Remove duplicates
        }
    else:
        return {
            'authenticated': False,
            'user': None,
            'permissions': []
        }

# Context processor to make auth info available in templates
@auth_bp.app_context_processor
def inject_auth_info():
    """Inject authentication info into all templates"""
    return {
        'current_user_info': get_current_user_info(),
        'user_has_permission': lambda perm: current_user.is_authenticated and current_user.has_permission(perm),
        'user_has_role': lambda role: current_user.is_authenticated and current_user.has_role(role)
    }

# Enhanced Google OAuth route
@auth_bp.route('/google')
def google_login():
    oauth_logger.info("=== GOOGLE OAUTH ROUTE ACCESSED ===")
    oauth_logger.info(f"Request URL: {request.url}")
    oauth_logger.info(f"Google authorized: {google.authorized}")
    
    if not google.authorized:
        oauth_logger.info("Not authorized, initiating OAuth flow...")
        oauth_url = url_for("google.login")
        oauth_logger.info(f"OAuth URL: {oauth_url}")
        return redirect(oauth_url)
    
    oauth_logger.info("Already authorized, fetching user info...")
    try:
        resp = google.get("/oauth2/v2/userinfo")
        oauth_logger.info(f"User info response status: {resp.status_code}")
        
        if resp.ok:
            user_info = resp.json()
            oauth_logger.info(f"Current user: {user_info.get('email', 'Unknown')}")
        else:
            oauth_logger.error(f"Failed to get user info: {resp.text}")
            
    except Exception as e:
        oauth_logger.error(f"Error getting user info: {str(e)}")
    
    return redirect(url_for('index')) 
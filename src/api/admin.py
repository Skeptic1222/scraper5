"""
Admin API Blueprint
"""
from functools import wraps

from flask import Blueprint, jsonify
from flask_login import current_user, login_required

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator for admin-only endpoints"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/stats')
@admin_required
def get_stats():
    """Get system statistics"""
    return jsonify({
        'success': True,
        'stats': {
            'total_users': 0,
            'total_downloads': 0,
            'active_jobs': 0
        }
    })

@admin_bp.route('/users')
@admin_required
def list_users():
    """List all users"""
    return jsonify({
        'success': True,
        'users': []
    })

@admin_bp.route('/config')
@admin_required
def get_config():
    """Get system configuration"""
    return jsonify({
        'success': True,
        'config': {}
    })

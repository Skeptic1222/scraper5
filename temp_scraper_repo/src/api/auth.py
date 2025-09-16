"""
Authentication API Blueprint
"""
from flask import Blueprint, jsonify
from flask_login import current_user, login_required, logout_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login endpoint"""
    # TODO: Implement OAuth login
    return jsonify({
        'success': False,
        'message': 'Login not yet implemented'
    })

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout endpoint"""
    logout_user()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@auth_bp.route('/user')
@login_required
def get_user():
    """Get current user info"""
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id if current_user.is_authenticated else None,
            'email': getattr(current_user, 'email', None)
        }
    })

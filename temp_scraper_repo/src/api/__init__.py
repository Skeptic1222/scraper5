"""
API Blueprints initialization
"""
from .admin import admin_bp
from .assets import assets_bp
from .auth import auth_bp
from .search import search_bp

__all__ = ['search_bp', 'assets_bp', 'auth_bp', 'admin_bp']

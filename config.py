"""
Centralized application configuration and constants.
Enhanced for Windows/IIS deployment with SQL Server Express support.
"""

import os
import platform
from datetime import timedelta

# Base path for the app when reverse-proxied (IIS). Must not include trailing slash.
APP_BASE = os.getenv("APP_BASE", "/scraper").rstrip("/") or "/scraper"

# Detect Windows environment for path handling
IS_WINDOWS = platform.system() == "Windows"

class DefaultConfig:
    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(32).hex()
    PREFERRED_URL_SCHEME = "https" if os.getenv("PUBLIC_BASE_URL", "").startswith("https") else "http"

    # Database Configuration with SQL Server Express support
    # Default to environment variable, with fallbacks for different platforms
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or (
        # SQL Server Express with Windows Authentication (preferred for enterprise Windows)
        "mssql+pyodbc://./\\SQLEXPRESS/enhanced_media_scraper?driver=ODBC Driver 18 for SQL Server&trusted_connection=yes&TrustServerCertificate=yes"
        if IS_WINDOWS else
        # PostgreSQL for development/Linux
        os.getenv("POSTGRES_URL") or "postgresql://user:password@localhost:5432/scraper_db"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database engine options optimized for SQL Server Express
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "echo": False,  # Set to True for debugging SQL queries
    }

    # Sessions
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = APP_BASE
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_NAME = "scraper_session"
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Other
    WTF_CSRF_ENABLED = False  # can be toggled on when OAuth flow is stable


def apply_env_fallbacks():
    # Allow insecure transport for OAuth in dev
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")
    os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")
    os.environ.setdefault("AUTHLIB_INSECURE_TRANSPORT", "true")


def init_app_config(app):
    """Apply default config values and environment fallbacks."""
    app.config.from_object(DefaultConfig)
    apply_env_fallbacks()

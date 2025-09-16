"""
Centralized application configuration and constants.
"""

import os
from datetime import timedelta

# Base path for the app when reverse-proxied (IIS). Must not include trailing slash.
APP_BASE = os.getenv("APP_BASE", "/scraper").rstrip("/") or "/scraper"


class DefaultConfig:
    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(32).hex()
    PREFERRED_URL_SCHEME = "https" if os.getenv("PUBLIC_BASE_URL", "").startswith("https") else "http"

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
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

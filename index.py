#!/usr/bin/env python3
"""
IIS FastCGI Entry Point for Enhanced Media Scraper
Simple entry point for wfastcgi to route requests to Flask application
"""
import os
import sys

# Add application directory to Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

# Set production environment
os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("FLASK_DEBUG", "0")

# Import the Flask application
from app import app

# This is the WSGI application object that wfastcgi expects
application = app

if __name__ == "__main__":
    # Not expected to run directly in FastCGI, but safe fallback
    app.run(host="127.0.0.1", port=8000, debug=False)
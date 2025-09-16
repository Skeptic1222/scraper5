#!/usr/bin/env python3
"""
Simple startup script for Enhanced Media Scraper
"""

import os
import sys

# Set environment variables if not set
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('DATABASE_URL', 'sqlite:///instance/scraper.db')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-change-in-production')
os.environ.setdefault('OAUTHLIB_INSECURE_TRANSPORT', '1')

print("Starting Enhanced Media Scraper...")
print("=" * 50)

try:
    # Import and run the app directly
    from app import app
    
    # Configuration
    host = '0.0.0.0'
    port = 5000
    debug = True
    
    print(f"🚀 Starting server on http://{host}:{port}")
    print(f"📝 Debug mode: {debug}")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("")
    
    # Start the application
    app.run(host=host, port=port, debug=debug)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n👋 Server stopped")
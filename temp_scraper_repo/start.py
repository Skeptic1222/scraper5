#!/usr/bin/env python3
"""
Startup script for Enhanced Media Scraper
Ensures database is initialized before starting the application
"""

import os
import sys

# SQL Server is configured in .env - no need for SQLite fallback

print("Starting Enhanced Media Scraper v3.0...")
print("=" * 50)

# Import app and initialize database
from app import app, db


def init_database():
    """Initialize database if needed"""
    with app.app_context():
        try:
            # Try to query a table to check if database exists
            from models import User
            User.query.first()
            print("✅ Database already initialized")
        except:
            # Database doesn't exist, create it
            print("📦 Initializing database...")
            db.create_all()

            # Create default data
            from models import AppSetting, Role

            # Create roles
            admin_role = Role(name='admin', description='Administrator')
            user_role = Role(name='user', description='Regular user')
            db.session.add(admin_role)
            db.session.add(user_role)

            # Create default settings
            default_settings = [
                AppSetting(key='daily_credit_limit', value='10', setting_type='int'),
                AppSetting(key='signup_bonus_credits', value='5', setting_type='int'),
                AppSetting(key='watermark_enabled', value='true', setting_type='bool'),
                AppSetting(key='ai_assistant_enabled', value='true', setting_type='bool')
            ]
            for setting in default_settings:
                db.session.add(setting)

            db.session.commit()
            print("✅ Database initialized successfully!")

if __name__ == '__main__':
    try:
        # Initialize database
        init_database()

        # Get configuration
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'false').lower() == 'true'

        print(f"🚀 Starting server on http://{host}:{port}")
        print(f"📝 Debug mode: {debug}")
        print(f"🔐 Google OAuth configured: {bool(os.environ.get('GOOGLE_CLIENT_ID'))}")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("")

        # Start the application
        app.run(host=host, port=port, debug=debug)

    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

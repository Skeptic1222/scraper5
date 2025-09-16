#!/usr/bin/env python3
"""
Database initialization script for Enhanced Media Scraper
Creates all necessary tables and initial data
"""

import os
import sys

# Set SQLite as default for initialization
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/scraper.db')

# Import app and models
from app import app, db
from models import AppSetting, Role


def init_database():
    """Initialize database with all tables"""
    print("Initializing database...")

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created")

        # Create default roles if they don't exist
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            admin_role = Role(name='admin', description='Administrator role')
            db.session.add(admin_role)
            print("✅ Admin role created")

        user_role = Role.query.filter_by(name='user').first()
        if not user_role:
            user_role = Role(name='user', description='Regular user role')
            db.session.add(user_role)
            print("✅ User role created")

        # Create default app settings
        settings = AppSetting.query.first()
        if not settings:
            settings = AppSetting(
                daily_credit_limit=10,
                signup_bonus_credits=5,
                watermark_enabled=True,
                ai_assistant_enabled=True
            )
            db.session.add(settings)
            print("✅ Default app settings created")

        # Commit all changes
        db.session.commit()
        print("✅ Database initialization complete!")

        # Show database location
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'sqlite' in db_url:
            db_path = db_url.replace('sqlite:///', '')
            print(f"📁 Database location: {db_path}")
        else:
            print(f"📁 Database: {db_url.split('@')[1] if '@' in db_url else db_url}")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

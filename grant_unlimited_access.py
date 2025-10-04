#!/usr/bin/env python3
"""
Grant unlimited access to admin user (sop1973@gmail.com)
This script enables all sources and grants unlimited credits
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Role, UserRole
from sources_data import get_all_sources

def grant_unlimited_access(email="sop1973@gmail.com"):
    """Grant unlimited access to specified user"""

    with app.app_context():
        # Find or create user
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"[ERROR] User {email} not found in database")
            print("User must sign in at least once before granting access")
            return False

        print(f"[OK] Found user: {user.name} ({user.email})")

        # Get all available sources
        all_sources = get_all_sources()
        all_source_ids = [source['id'] for source in all_sources]

        print(f"[OK] Found {len(all_source_ids)} total sources")

        # Update user with unlimited access
        user.subscription_plan = "ultra"  # Highest tier
        user.subscription_status = "active"
        user.credits = 999999  # Unlimited credits
        user.is_nsfw_enabled = True  # Enable NSFW content
        user.subscription_start_date = datetime.utcnow()
        user.subscription_end_date = datetime.utcnow() + timedelta(days=36500)  # 100 years

        # Enable ALL sources
        user.set_enabled_sources(all_source_ids)

        # Ensure admin role exists
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("Creating admin role...")
            admin_role = Role(
                name='admin',
                description='Administrator with full access',
                permissions=json.dumps([
                    'view_all_jobs',
                    'start_jobs',
                    'delete_jobs',
                    'manage_users',
                    'view_logs',
                    'manage_settings',
                    'use_nsfw',
                    'unlimited_downloads',
                    'all_sources'
                ])
            )
            db.session.add(admin_role)
            db.session.flush()

        # Assign admin role if not already assigned
        existing_role = UserRole.query.filter_by(user_id=user.id, role_id=admin_role.id).first()
        if not existing_role:
            print("Assigning admin role...")
            user_role = UserRole(user_id=user.id, role_id=admin_role.id)
            db.session.add(user_role)

        # Commit all changes
        db.session.commit()

        print("\n[SUCCESS] Granted unlimited access to", email)
        print("\n[USER DETAILS]")
        print(f"   - Subscription: {user.subscription_plan} ({user.subscription_status})")
        print(f"   - Credits: {user.credits:,}")
        print(f"   - NSFW Enabled: {user.is_nsfw_enabled}")
        print(f"   - Sources Enabled: {len(user.get_enabled_sources())} sources")
        print(f"   - Is Admin: {user.is_admin()}")
        print(f"   - Roles: {user.get_roles()}")
        print(f"\n[ENABLED SOURCES] ({len(all_source_ids)} total):")

        # Group by category
        from sources_data import get_content_sources
        sources_by_category = get_content_sources()

        for category, sources in sources_by_category.items():
            if category != 'all':
                source_names = [s['name'] for s in sources]
                print(f"   {category}: {', '.join(source_names)}")

        return True

if __name__ == "__main__":
    print("=" * 60)
    print("GRANTING UNLIMITED ACCESS TO ADMIN USER")
    print("=" * 60)
    print()

    success = grant_unlimited_access("sop1973@gmail.com")

    if success:
        print("\n" + "=" * 60)
        print("[COMPLETE] USER NOW HAS UNLIMITED ACCESS TO ALL SOURCES!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("[FAILED] COULD NOT GRANT ACCESS")
        print("=" * 60)
        sys.exit(1)

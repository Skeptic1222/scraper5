"""
Script to check and reset user credits for development testing
"""

import os
import json
from app import app
from models import db, User
from sqlalchemy import text

def check_user_credits(email=None):
    """Check user credits and subscription status"""
    with app.app_context():
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"\n📊 User Details for {email}:")
                print(f"   ID: {user.id}")
                print(f"   Name: {user.name}")
                print(f"   Credits: {user.credits}")
                print(f"   Plan: {user.subscription_plan}")
                print(f"   Status: {user.subscription_status}")
                print(f"   Is Active: {user.is_active}")
                print(f"   Last Login: {user.last_login}")
                print(f"   Sources Enabled: {user.get_enabled_sources()}")
                return user
            else:
                print(f"❌ User not found: {email}")
        else:
            # Show all users
            users = User.query.all()
            print(f"\n📊 All Users ({len(users)} total):")
            for user in users:
                print(f"   - {user.email}: {user.credits} credits, {user.subscription_plan} plan")

def reset_user_credits(email, credits=50):
    """Reset user credits for testing"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            old_credits = user.credits
            user.credits = credits
            db.session.commit()
            print(f"✅ Reset credits for {email}: {old_credits} → {credits}")
        else:
            print(f"❌ User not found: {email}")

def set_user_plan(email, plan='trial'):
    """Set user subscription plan for testing"""
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            old_plan = user.subscription_plan
            user.subscription_plan = plan
            user.subscription_status = 'active'
            
            # Set default sources based on plan
            if plan == 'trial':
                user.sources_enabled = json.dumps(['reddit', 'imgur', 'wikimedia', 'deviantart'])
            elif plan == 'basic':
                user.sources_enabled = json.dumps(['reddit', 'imgur', 'wikimedia', 'deviantart', 'pixabay', 'pexels', 'unsplash'])
            elif plan == 'pro':
                user.sources_enabled = json.dumps(['reddit', 'imgur', 'wikimedia', 'deviantart', 'pixabay', 'pexels', 'unsplash', 'instagram', 'twitter', 'pinterest', 'tumblr', 'flickr', 'artstation', 'behance'])
            elif plan == 'ultra':
                # Ultra gets all sources
                from scrapers import get_content_sources
                all_sources = list(get_content_sources().keys())
                user.sources_enabled = json.dumps(all_sources)
            
            db.session.commit()
            print(f"✅ Changed plan for {email}: {old_plan} → {plan}")
            print(f"   Enabled sources: {user.get_enabled_sources()}")
        else:
            print(f"❌ User not found: {email}")

def fix_null_fields():
    """Fix all users with null subscription fields"""
    with app.app_context():
        users = User.query.all()
        fixed_count = 0
        for user in users:
            changed = False
            if user.credits is None:
                user.credits = 50
                changed = True
            if user.subscription_plan is None:
                user.subscription_plan = 'trial'
                changed = True
            if user.subscription_status is None:
                user.subscription_status = 'active'
                changed = True
            if user.sources_enabled is None:
                user.sources_enabled = json.dumps(['reddit', 'imgur', 'wikimedia', 'deviantart'])
                changed = True
            if changed:
                fixed_count += 1
                print(f"   Fixed null fields for {user.email}")
        
        if fixed_count > 0:
            db.session.commit()
            print(f"✅ Fixed {fixed_count} users with null subscription fields")
        else:
            print("✅ All users have valid subscription fields")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python check_user_credits.py check [email]")
        print("  python check_user_credits.py reset <email> [credits]")
        print("  python check_user_credits.py plan <email> <plan>")
        print("  python check_user_credits.py fix-nulls")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        email = sys.argv[2] if len(sys.argv) > 2 else None
        check_user_credits(email)
    
    elif command == "reset":
        if len(sys.argv) < 3:
            print("❌ Please provide an email address")
            sys.exit(1)
        email = sys.argv[2]
        credits = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        reset_user_credits(email, credits)
    
    elif command == "plan":
        if len(sys.argv) < 4:
            print("❌ Please provide email and plan (trial/basic/pro/ultra)")
            sys.exit(1)
        email = sys.argv[2]
        plan = sys.argv[3]
        set_user_plan(email, plan)
    
    elif command == "fix-nulls":
        fix_null_fields() 
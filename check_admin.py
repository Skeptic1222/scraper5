#!/usr/bin/env python3
"""Check admin user status"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def check_admin():
    """Check if admin user exists"""
    with app.app_context():
        admin = User.query.filter_by(email='sop1973@gmail.com').first()
        if admin:
            print(f"Admin user exists: {admin.email}")
            print(f"Credits: {admin.credits}")
            print(f"Is Admin: {admin.is_admin()}")
        else:
            print("Admin user does not exist")
            
        # List all users
        users = User.query.all()
        print(f"\nTotal users: {len(users)}")
        for user in users:
            print(f"  - {user.email} (Admin: {user.is_admin()})")

if __name__ == "__main__":
    check_admin()
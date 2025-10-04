#!/usr/bin/env python3
"""Start Flask app with OAuth properly configured"""

import os
import sys
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

# Use SQLite for testing to avoid SQL Server issues
os.environ['DATABASE_URL'] = 'sqlite:///scraped.db'
os.environ['FLASK_ENV'] = 'development'

# Verify OAuth credentials
client_id = os.environ.get('GOOGLE_CLIENT_ID')
client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

print("=== Starting Flask with OAuth ===")
print(f"Client ID: {client_id[:30]}...")
print(f"Secret: {client_secret[:15]}...")
print(f"Database: SQLite (testing mode)")
print(f"Access URL: http://localhost:5050")
print("OAuth Login: http://localhost:5050/auth/login")
print("="*50)

# Import and run the app
sys.argv = ['app.py', '--port', '5050']
exec(open('app.py').read())
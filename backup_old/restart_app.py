#!/usr/bin/env python3
"""
Restart script to ensure clean application startup with correct database
"""

import os
import signal
import psutil
import time
from dotenv import load_dotenv

def kill_existing_flask_processes():
    """Kill any existing Flask processes"""
    print("🔍 Checking for existing Flask processes...")
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any('app.py' in cmd or 'flask' in cmd for cmd in proc.info['cmdline']):
                print(f"🗑️ Killing process {proc.info['pid']}: {' '.join(proc.info['cmdline'])}")
                proc.kill()
                killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if killed_count > 0:
        print(f"✅ Killed {killed_count} existing Flask processes")
        time.sleep(2)  # Wait for processes to clean up
    else:
        print("✅ No existing Flask processes found")

def verify_environment():
    """Verify environment configuration"""
    print("🔍 Verifying environment configuration...")
    
    load_dotenv()
    
    database_url = os.environ.get('DATABASE_URL')
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    print(f"📍 DATABASE_URL: {database_url}")
    print(f"🔑 GOOGLE_CLIENT_ID: {google_client_id[:20]}...{google_client_id[-10:] if google_client_id else 'NOT SET'}")
    print(f"🔑 GOOGLE_CLIENT_SECRET: {'SET' if google_client_secret else 'NOT SET'}")
    
    if not database_url or 'SQLEXPRESS' not in database_url:
        print("❌ Warning: DATABASE_URL may not be configured for SQL Server")
    else:
        print("✅ Database URL appears to be configured for SQL Server")
    
    return all([database_url, google_client_id, google_client_secret])

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        from app import app
        with app.app_context():
            from models import db
            result = db.session.execute(db.text("SELECT @@VERSION AS version, DB_NAME() AS database_name"))
            row = result.fetchone()
            print(f"✅ Connected to: {row[0][:50]}...")
            print(f"🗄️ Database: {row[1]}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def start_application():
    """Start the Flask application"""
    print("🚀 Starting Flask application...")
    
    # Import and run
    from app import app
    
    print("=" * 60)
    print("🚀 === STARTING ENHANCED MEDIA SCRAPER (Clean Restart) ===")
    print("📍 Server: http://localhost:5000")
    print("🔄 Mode: Enhanced with Database, OAuth, and RBAC")
    print("🗄️ Database: SQL Server 2022 Express")
    print("🔐 Authentication: Google OAuth Enabled")
    print("💾 Persistent job tracking and asset management")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    print("🔄 === FLASK APPLICATION RESTART SCRIPT ===")
    
    # Step 1: Kill existing processes
    kill_existing_flask_processes()
    
    # Step 2: Verify environment
    if not verify_environment():
        print("❌ Environment configuration issues detected!")
        exit(1)
    
    # Step 3: Test database
    if not test_database_connection():
        print("❌ Database connection issues detected!")
        exit(1)
    
    # Step 4: Start application
    start_application() 
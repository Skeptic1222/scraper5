#!/usr/bin/env python3
"""
Production startup script for Enhanced Media Scraper
- Proper error handling
- Production environment settings
- IIS integration
- Memory management
"""

import os
import sys
import time
from subprocess import run

import psutil
from waitress import serve

# Add parent directory to path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'

# Import app after environment is set
from app import app, create_tables, db

def check_port_available(port):
    """Check if port is available"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return False
    return True

def initialize_database():
    """Initialize database with proper error handling"""
    try:
        with app.app_context():
            db.create_all()
            create_tables()
        print("[SUCCESS] Database initialized")
        return True
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False

def check_permissions():
    """Check file/directory permissions"""
    critical_paths = [
        'logs',
        'instance',
        'static/uploads',
    ]

    for path in critical_paths:
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            # Verify write permissions
            test_file = os.path.join(path, '.permission_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"[SUCCESS] Permission check passed for {path}")
        except Exception as e:
            print(f"[ERROR] Permission check failed for {path}: {e}")
            return False
    return True

def check_dependencies():
    """Verify critical dependencies"""
    try:
        import flask
        import sqlalchemy
        import waitress
        print("[SUCCESS] Critical dependencies verified")
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        return False

def start_server(port=5050, retries=3):
    """Start production server with retries"""
    current_retry = 0

    while current_retry < retries:
        if check_port_available(port):
            try:
                print(f"[START] Starting production server on port {port}")
                serve(app, host='0.0.0.0', port=port)
                return True
            except Exception as e:
                print(f"[ERROR] Server startup failed: {e}")
                current_retry += 1
                if current_retry < retries:
                    print(f"[RETRY] Attempting restart ({current_retry}/{retries})")
                    time.sleep(2)
        else:
            print(f"[ERROR] Port {port} is in use")
            return False

    print("[FATAL] Server startup failed after retries")
    return False

def main():
    """Main startup sequence"""
    # Initial checks
    if not all([
        check_dependencies(),
        check_permissions(),
        initialize_database()
    ]):
        print("[FATAL] Startup checks failed")
        sys.exit(1)

    # Start memory management
    try:
        from memory_manager import start_memory_management
        start_memory_management()
        print("[SUCCESS] Memory management started")
    except Exception as e:
        print(f"[WARNING] Memory management failed to start: {e}")

    # Get port from environment or use default
    port = int(os.environ.get('FLASK_RUN_PORT', 5050))

    # Start server
    if not start_server(port):
        print("[FATAL] Server failed to start")
        sys.exit(1)

if __name__ == '__main__':
    main()
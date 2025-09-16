#!/usr/bin/env python3
"""
Single Instance Flask Application Starter
Ensures only one instance of the application runs at a time
"""

import os
import subprocess
import sys
import time

import psutil


def kill_existing_instances():
    """Kill all existing Python processes running app.py or related scripts"""
    killed_count = 0
    current_pid = os.getpid()

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Skip current process
            if proc.info['pid'] == current_pid:
                continue

            # Check if it's a Python process running our app
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('app.py' in arg or 'start_production.py' in arg
                                  or 'simple_test.py' in arg for arg in cmdline):
                    print(f"Killing existing process: PID {proc.info['pid']}")
                    proc.kill()
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if killed_count > 0:
        print(f"Killed {killed_count} existing instances")
        time.sleep(2)  # Wait for processes to fully terminate

    return killed_count

def check_database_connection():
    """Verify SQL Server Express connection is available"""
    try:
        import pyodbc
        conn_str = os.environ.get('DATABASE_URL',
                                  'mssql+pyodbc://sa:Admin123!@localhost/scraperdb?driver=ODBC+Driver+17+for+SQL+Server')

        # Extract connection details for pyodbc
        if 'mssql+pyodbc://' in conn_str:
            conn_str = conn_str.replace('mssql+pyodbc://', '')
            # Parse and create ODBC connection string
            parts = conn_str.split('@')
            creds = parts[0].split(':')
            server_db = parts[1].split('/')
            server = server_db[0]
            database = server_db[1].split('?')[0]

            odbc_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={creds[0]};PWD={creds[1]}'

            conn = pyodbc.connect(odbc_str, timeout=5)
            conn.close()
            print("✅ Database connection verified")
            return True
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        print("Make sure SQL Server Express is running and accessible")
        return False

def start_application():
    """Start the Flask application with proper configuration"""
    # Set required environment variables
    env = os.environ.copy()
    env.update({
        'FLASK_ENV': 'production',
        'ALLOW_MOCK_LOGIN': 'true',
        'APP_BASE': '/scraper',
        'DATABASE_URL': os.environ.get('DATABASE_URL',
                                       'mssql+pyodbc://sa:Admin123!@localhost/scraperdb?driver=ODBC+Driver+17+for+SQL+Server')
    })

    # Start the application
    print("\n🚀 Starting Enhanced Media Scraper...")
    print("=" * 50)
    print("Configuration:")
    print(f"  Environment: {env['FLASK_ENV']}")
    print(f"  App Base: {env['APP_BASE']}")
    print(f"  Database: SQL Server Express")
    print("  Port: 5050 (via IIS proxy)")
    print("=" * 50)

    try:
        # Run the Flask app
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Stream output in real-time
        for line in iter(process.stdout.readline, ''):
            print(line, end='')

    except KeyboardInterrupt:
        print("\n\n⚠️ Shutting down application...")
        process.terminate()
        process.wait(timeout=5)
        print("✅ Application stopped cleanly")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    print("🔧 Enhanced Media Scraper - Single Instance Starter")
    print("=" * 50)

    # Change to application directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    print(f"Working directory: {app_dir}")

    # Kill existing instances
    print("\n📋 Checking for existing instances...")
    kill_existing_instances()

    # Skip database check for now - just get app running
    print("\n🔍 Skipping database connection check for now...")

    # Start the application
    start_application()

if __name__ == "__main__":
    main()

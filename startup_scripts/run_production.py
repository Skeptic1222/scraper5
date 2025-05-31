#!/usr/bin/env python3
"""
🚀 PRODUCTION MEDIA SCRAPER SERVER
===================================
Stable production server using Waitress WSGI server
No file watching, no auto-reloads, maximum stability
"""

import sys
import os
import time
from pathlib import Path

# === EXPLICIT PATH MANAGEMENT ===
sys.path.insert(0, r'C:\inetpub\wwwroot\scraper')
os.chdir(r'C:\inetpub\wwwroot\scraper')

def verify_environment():
    """Verify the production environment is properly set up"""
    print("🔍 === PRODUCTION ENVIRONMENT VERIFICATION ===")
    
    # Check working directory
    cwd = os.getcwd()
    print(f"📁 Working directory: {cwd}")
    
    # Check if required files exist
    required_files = ['app.py', 'real_content_downloader.py', 'requirements.txt']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: Found")
        else:
            print(f"❌ {file}: Missing")
            return False
    
    # Check dependencies
    try:
        import flask
        print("✅ Flask: OK")
    except ImportError:
        print("❌ Flask: Missing")
        return False
    
    try:
        import yt_dlp
        print("✅ yt-dlp: OK")
    except ImportError:
        print("❌ yt-dlp: Missing")  
        return False
    
    try:
        from real_content_downloader import download_images_simple, enhanced_social_scrape
        print("✅ real_content_downloader: OK")
    except ImportError as e:
        print(f"❌ real_content_downloader: {e}")
        return False
    
    # Check downloads directory
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    print(f"✅ Downloads directory: {downloads_dir.absolute()}")
    
    print("✅ === ENVIRONMENT VERIFICATION COMPLETE ===")
    return True

def start_production_server():
    """Start the production server"""
    print("🚀 === STARTING PRODUCTION MEDIA SCRAPER ===")
    print("📍 Server: http://localhost:5000")
    print("🔄 Mode: Production (NO DEMO FALLBACKS)")
    print("💾 Real content downloads only")
    print("=" * 50)
    
    if not verify_environment():
        print("❌ Environment verification failed!")
        return 1
    
    try:
        # Import and start the Flask app
        from app import app
        print("🚀 Starting production server...")
        app.run(host='localhost', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Production server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Production server error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = start_production_server()
    sys.exit(exit_code) 
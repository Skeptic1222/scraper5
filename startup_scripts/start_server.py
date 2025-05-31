#!/usr/bin/env python3
"""
Production Media Scraper Server Starter - NO DEMO FALLBACKS
Uses real_content_downloader.py for actual content
"""
import sys
import os
import subprocess
import time

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import flask
        print("✅ Flask: OK")
    except ImportError:
        print("❌ Missing dependency: No module named 'flask'")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    try:
        import yt_dlp
        print("✅ yt-dlp: OK")
    except ImportError:
        print("❌ Missing dependency: No module named 'yt_dlp'")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    try:
        from real_content_downloader import download_images_multi_engine
        print("✅ real_content_downloader: OK")
    except ImportError as e:
        print(f"❌ real_content_downloader import error: {e}")
        return False
    
    return True

def start_server():
    """Start the Flask server"""
    print("🚀 Starting Media Scraper Web Interface...")
    print("📍 The application will be available at:")
    print("   • http://localhost:5000")
    print("   • http://localhost:5000/scraper") 
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    if not check_dependencies():
        return
    
    try:
        # Start the Flask application
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    start_server() 
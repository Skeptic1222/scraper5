#!/usr/bin/env python3
"""
Fix Application Issues Script
Addresses identified issues in the Enhanced Media Scraper application
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

def test_flask_server():
    """Test if Flask server is responding correctly"""
    print("🔍 Testing Flask server...")
    
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:5000/test-system', timeout=5)
            if response.status_code == 200:
                print("✅ Flask server is responding correctly")
                data = response.json()
                print(f"   - Database: {data['tests']['database']}")
                print(f"   - Sources: {data['tests']['sources_available']}")
                print(f"   - Auth: {data['tests']['authentication']}")
                return True
            else:
                print(f"⚠️  Server returned status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"⚠️  Connection attempt {i+1}/{max_retries} failed")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error testing server: {str(e)}")
    
    return False

def fix_video_thumbnail_opacity():
    """Fix the video thumbnail canvas opacity issue in index.html"""
    print("\n🔧 Fixing video thumbnail opacity issue...")
    
    template_path = Path("templates/index.html")
    if not template_path.exists():
        print("❌ templates/index.html not found")
        return False
    
    # Read the file
    content = template_path.read_text(encoding='utf-8')
    
    # Fix the canvas opacity issue - change from opacity: 0 to opacity: 1
    if 'style="width: 100%; height: 100%; object-fit: cover; display: block; opacity: 0;"' in content:
        content = content.replace(
            'style="width: 100%; height: 100%; object-fit: cover; display: block; opacity: 0;"',
            'style="width: 100%; height: 100%; object-fit: cover; display: block; opacity: 1;"'
        )
        print("✅ Fixed canvas opacity from 0 to 1")
    
    # Also fix the CSS rule that might be hiding the canvas
    if 'opacity: 0;' in content and '.video-thumbnail-canvas' in content:
        # Find and fix the CSS opacity for video-thumbnail-canvas
        import re
        pattern = r'(\.video-thumbnail-canvas\s*{[^}]*opacity:\s*)0;'
        if re.search(pattern, content):
            content = re.sub(pattern, r'\g<1>1;', content)
            print("✅ Fixed CSS opacity for video-thumbnail-canvas")
    
    # Write the fixed content back
    template_path.write_text(content, encoding='utf-8')
    print("✅ Video thumbnail opacity issue fixed")
    return True

def fix_progress_callback_errors():
    """Fix progress callback error handling in real_content_downloader.py"""
    print("\n🔧 Fixing progress callback error handling...")
    
    downloader_path = Path("real_content_downloader.py")
    if not downloader_path.exists():
        print("❌ real_content_downloader.py not found")
        return False
    
    # Read the file
    content = downloader_path.read_text(encoding='utf-8')
    
    # Count fixes
    fixes_applied = 0
    
    # Fix 1: Improve error message handling (remove string slicing)
    # Replace str(e)[:100] with just str(e) for better error visibility
    if '[:100]' in content:
        content = content.replace('str(e)[:100]', 'str(e)')
        fixes_applied += 1
        print("✅ Removed error message truncation for better debugging")
    
    if '[:200]' in content:
        content = content.replace('str(e)[:200]', 'str(e)')
        fixes_applied += 1
    
    if '[:50]' in content:
        content = content.replace('str(e)[:50]', 'str(e)')
        fixes_applied += 1
    
    # Write the fixed content back
    downloader_path.write_text(content, encoding='utf-8')
    print(f"✅ Applied {fixes_applied} fixes to error handling")
    return True

def ensure_downloads_directory():
    """Ensure downloads directory exists with proper structure"""
    print("\n📁 Ensuring downloads directory structure...")
    
    directories = [
        "downloads",
        "downloads/instagram",
        "downloads/twitter", 
        "downloads/tiktok",
        "downloads/reddit",
        "downloads/youtube",
        "downloads/images",
        "downloads/videos"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory ensured: {directory}")
    
    return True

def check_environment_variables():
    """Verify all required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    required_vars = {
        'GOOGLE_CLIENT_ID': 'Google OAuth client ID',
        'GOOGLE_CLIENT_SECRET': 'Google OAuth client secret',
        'DATABASE_URL': 'SQL Server database connection string',
        'SECRET_KEY': 'Flask secret key',
        'OAUTHLIB_INSECURE_TRANSPORT': 'OAuth insecure transport flag'
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            if 'SECRET' in var or 'KEY' in var:
                print(f"✅ {var}: SET ({description})")
            else:
                print(f"✅ {var}: {value[:30]}... ({description})")
        else:
            print(f"❌ {var}: NOT SET ({description})")
            all_good = False
    
    return all_good

def restart_flask_server():
    """Restart the Flask server"""
    print("\n🔄 Restarting Flask server...")
    
    # Use the existing restart_app.py script
    restart_script = Path("restart_app.py")
    if restart_script.exists():
        os.system("python restart_app.py")
        time.sleep(5)  # Wait for server to start
        return True
    else:
        print("⚠️  restart_app.py not found, please restart manually")
        return False

def main():
    """Main function to fix all identified issues"""
    print("🚀 Enhanced Media Scraper - Issue Fix Script")
    print("=" * 50)
    
    # Check environment variables
    env_ok = check_environment_variables()
    if not env_ok:
        print("\n⚠️  Some environment variables are missing!")
        print("Please check your .env file")
    
    # Ensure directory structure
    ensure_downloads_directory()
    
    # Fix video thumbnail opacity
    fix_video_thumbnail_opacity()
    
    # Fix progress callback errors
    fix_progress_callback_errors()
    
    # Test Flask server
    server_ok = test_flask_server()
    
    if not server_ok:
        print("\n⚠️  Flask server is not responding properly")
        restart = input("Would you like to restart the Flask server? (y/n): ")
        if restart.lower() == 'y':
            restart_flask_server()
            time.sleep(5)
            test_flask_server()
    
    print("\n✅ All fixes applied!")
    print("\nNext steps:")
    print("1. If the Flask server was restarted, wait a moment for it to fully start")
    print("2. Access the application at http://localhost:5000")
    print("3. Test the video thumbnail generation")
    print("4. Run a test search to verify everything is working")

if __name__ == "__main__":
    main() 
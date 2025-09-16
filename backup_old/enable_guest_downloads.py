#!/usr/bin/env python3
"""
Enable Guest Downloads
Allows unauthenticated users to perform searches and downloads
"""

from models import db, AppSetting
from app import app

def enable_guest_downloads():
    """Enable guest downloads in app settings"""
    with app.app_context():
        try:
            # Check current setting
            current_value = AppSetting.get_setting('allow_guest_downloads', False)
            print(f"Current guest downloads setting: {current_value}")
            
            # Enable guest downloads
            AppSetting.set_setting('allow_guest_downloads', True)
            
            # Verify the change
            new_value = AppSetting.get_setting('allow_guest_downloads', False)
            print(f"New guest downloads setting: {new_value}")
            
            if new_value:
                print("✅ Guest downloads enabled successfully!")
                return True
            else:
                print("❌ Failed to enable guest downloads")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    print("🔧 Enabling Guest Downloads...")
    print("=" * 50)
    
    if enable_guest_downloads():
        print("\n✅ Success! Guest users can now:")
        print("- Start searches without logging in")
        print("- Download content from all sources")
        print("- View assets (public ones)")
        print("\nNote: For full features (job history, asset management),")
        print("users should still log in with Google OAuth.")
    else:
        print("\n❌ Failed to enable guest downloads")
        print("Please check the database connection and try again.") 
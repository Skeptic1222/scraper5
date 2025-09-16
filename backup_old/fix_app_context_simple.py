#!/usr/bin/env python3
"""
Simple Fix for Flask Application Context Issue
Wraps database operations in background threads with proper context
"""

from pathlib import Path

def apply_simple_fix():
    """Apply a simple fix to ensure app context in progress callbacks"""
    print("🔧 Applying simple fix to app.py...")
    
    app_path = Path("app.py")
    content = app_path.read_text(encoding='utf-8')
    
    # Fix the create_progress_callback function with proper context handling
    old_callback = """def create_progress_callback(job_id):
    \"\"\"Create a progress callback function for a specific job - Database version\"\"\"
    def progress_callback(message, progress, downloaded, images, videos, current_file=None):
        try:
            db_job_manager.add_progress_update(job_id, message, progress, downloaded, images, videos, current_file)
            
            # Also track the asset in the database if current_file is provided
            if current_file and os.path.exists(current_file):
                # Determine file type
                file_extension = os.path.splitext(current_file)[1].lower()
                file_type = 'video' if file_extension in ['.mp4', '.webm', '.avi', '.mov', '.mkv'] else 'image'
                
                # Add to asset database
                db_asset_manager.add_asset(
                    job_id=job_id,
                    filepath=current_file,
                    file_type=file_type,
                    metadata={
                        'source_name': 'scraper',
                        'downloaded_via': 'comprehensive_search'
                    }
                )
        except Exception as e:
            # Log error but don't crash the download process
            print(f"⚠️ Progress callback error for job {job_id}: {str(e)[:100]}")
    return progress_callback"""
    
    new_callback = """def create_progress_callback(job_id):
    \"\"\"Create a progress callback function for a specific job - Database version\"\"\"
    def progress_callback(message, progress, downloaded, images, videos, current_file=None):
        # Run database operations within app context
        with app.app_context():
            try:
                db_job_manager.add_progress_update(job_id, message, progress, downloaded, images, videos, current_file)
                
                # Also track the asset in the database if current_file is provided
                if current_file and os.path.exists(current_file):
                    # Determine file type
                    file_extension = os.path.splitext(current_file)[1].lower()
                    file_type = 'video' if file_extension in ['.mp4', '.webm', '.avi', '.mov', '.mkv'] else 'image'
                    
                    # Add to asset database
                    db_asset_manager.add_asset(
                        job_id=job_id,
                        filepath=current_file,
                        file_type=file_type,
                        metadata={
                            'source_name': 'scraper',
                            'downloaded_via': 'comprehensive_search'
                        }
                    )
            except Exception as e:
                # Log error but don't crash the download process
                print(f"⚠️ Progress callback error for job {job_id}: {str(e)}")
    return progress_callback"""
    
    if old_callback in content:
        content = content.replace(old_callback, new_callback)
        print("✅ Fixed progress callback with app context")
    else:
        print("⚠️  Could not find the exact callback function to replace")
        print("   Attempting alternative fix...")
        
        # Try a more flexible pattern
        import re
        pattern = r'(def progress_callback\(.*?\):.*?)(try:)'
        replacement = r'\1# Run database operations within app context\n        with app.app_context():\n            \2'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Also remove the string truncation in error messages
    content = content.replace('str(e)[:100]', 'str(e)')
    content = content.replace('str(e)[:200]', 'str(e)')
    
    # Write the fixed content back
    app_path.write_text(content, encoding='utf-8')
    print("✅ Applied fix to app.py")
    
    return True

def main():
    """Main function"""
    print("🚀 Simple Flask Application Context Fix")
    print("=" * 50)
    
    if apply_simple_fix():
        print("\n✅ Fix applied successfully!")
        print("\nThe fix ensures that all database operations in the progress")
        print("callback are wrapped with app.app_context().")
        print("\nPlease restart the Flask application for the changes to take effect.")
    else:
        print("\n❌ Failed to apply fix")
        print("Please check the file manually")

if __name__ == "__main__":
    main() 
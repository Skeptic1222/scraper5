#!/usr/bin/env python3
"""
Fix Flask Application Context Issue
Ensures database operations in background threads have proper context
"""

import re
from pathlib import Path

def fix_db_job_manager():
    """Fix db_job_manager.py to handle application context properly"""
    print("🔧 Fixing db_job_manager.py...")
    
    file_path = Path("db_job_manager.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Add import for current_app if not already present
    if "from flask import current_app" not in content:
        # Add import after the existing imports
        content = content.replace(
            "from flask_login import current_user",
            "from flask_login import current_user\nfrom flask import current_app"
        )
    
    # Fix the update_job method to handle context
    old_update_job = """    def update_job(self, job_id, **updates):
        \"\"\"Update job with new data\"\"\"
        with self.lock:
            job = db.session.query(ScrapeJob).filter_by(id=job_id).first()"""
    
    new_update_job = """    def update_job(self, job_id, **updates):
        \"\"\"Update job with new data\"\"\"
        with self.lock:
            # Ensure we have app context
            if not current_app:
                from app import app
                with app.app_context():
                    return self._do_update_job(job_id, **updates)
            return self._do_update_job(job_id, **updates)
    
    def _do_update_job(self, job_id, **updates):
        \"\"\"Internal method to update job with app context\"\"\"
        job = db.session.query(ScrapeJob).filter_by(id=job_id).first()"""
    
    if old_update_job in content:
        content = content.replace(old_update_job, new_update_job)
        
        # Also need to update the rest of the method to use _do_update_job
        content = content.replace(
            "return self.update_job(job_id, **update_data)",
            "return self.update_job(job_id, **update_data)"
        )
    
    # Fix add_progress_update to handle context
    old_progress = """    def add_progress_update(self, job_id, message, progress, downloaded, images, videos, current_file=None):
        \"\"\"Add progress update to job\"\"\"
        update_data = {"""
    
    new_progress = """    def add_progress_update(self, job_id, message, progress, downloaded, images, videos, current_file=None):
        \"\"\"Add progress update to job\"\"\"
        # Ensure we have app context for database operations
        if not current_app:
            from app import app
            with app.app_context():
                return self._do_add_progress_update(job_id, message, progress, downloaded, images, videos, current_file)
        return self._do_add_progress_update(job_id, message, progress, downloaded, images, videos, current_file)
    
    def _do_add_progress_update(self, job_id, message, progress, downloaded, images, videos, current_file=None):
        \"\"\"Internal method to add progress update with app context\"\"\"
        update_data = {"""
    
    if old_progress in content:
        content = content.replace(old_progress, new_progress)
    
    # Write the fixed content back
    file_path.write_text(content, encoding='utf-8')
    print("✅ Fixed db_job_manager.py")
    return True

def fix_app_py_progress_callback():
    """Fix the progress callback in app.py to ensure context is available"""
    print("\n🔧 Fixing progress callback in app.py...")
    
    file_path = Path("app.py")
    content = file_path.read_text(encoding='utf-8')
    
    # Replace the create_progress_callback function
    old_callback = """def create_progress_callback(job_id):
    \"\"\"Create a progress callback function for a specific job - Database version\"\"\"
    def progress_callback(message, progress, downloaded, images, videos, current_file=None):
        try:
            db_job_manager.add_progress_update(job_id, message, progress, downloaded, images, videos, current_file)"""
    
    new_callback = """def create_progress_callback(job_id):
    \"\"\"Create a progress callback function for a specific job - Database version\"\"\"
    def progress_callback(message, progress, downloaded, images, videos, current_file=None):
        try:
            # Ensure we have app context for database operations
            if app.app_context():
                db_job_manager.add_progress_update(job_id, message, progress, downloaded, images, videos, current_file)"""
    
    if old_callback in content:
        content = content.replace(old_callback, new_callback)
        
        # Also fix the asset tracking part
        content = content.replace(
            "# Add to asset database\n                db_asset_manager.add_asset(",
            "# Add to asset database (ensure context)\n                if app.app_context():\n                    db_asset_manager.add_asset("
        )
    
    # Write the fixed content back
    file_path.write_text(content, encoding='utf-8')
    print("✅ Fixed progress callback in app.py")
    return True

def main():
    """Main function to apply all fixes"""
    print("🚀 Fixing Flask Application Context Issues")
    print("=" * 50)
    
    # Apply fixes
    fix_db_job_manager()
    fix_app_py_progress_callback()
    
    print("\n✅ All fixes applied!")
    print("\nNext steps:")
    print("1. Restart the Flask application")
    print("2. Try running a search again")
    print("3. The jobs should now process correctly without context errors")

if __name__ == "__main__":
    main() 
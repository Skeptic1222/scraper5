#!/usr/bin/env python3
"""
Fix broken assets that have no MediaBlobs and no files
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Asset, MediaBlob

def fix_broken_assets():
    """Fix assets that have no MediaBlobs and no files"""
    with app.app_context():
        print("🔧 Fixing broken assets...")
        print("=" * 60)
        
        # Find assets without MediaBlobs
        broken_assets = []
        for asset in Asset.query.filter_by(is_deleted=False).all():
            if not asset.media_blob and not os.path.exists(asset.file_path):
                broken_assets.append(asset)
        
        print(f"Found {len(broken_assets)} broken assets (no MediaBlob, no file)")
        
        if not broken_assets:
            print("✅ No broken assets found!")
            return
        
        # Option 1: Mark them as deleted
        print("\nOption 1: Mark broken assets as deleted")
        response = input("Do you want to mark these assets as deleted? (y/n): ")
        
        if response.lower() == 'y':
            for asset in broken_assets:
                asset.is_deleted = True
                print(f"  Marked asset {asset.id} ({asset.filename}) as deleted")
            
            try:
                db.session.commit()
                print(f"✅ Marked {len(broken_assets)} assets as deleted")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error: {e}")
                return
        
        # Option 2: Try to find duplicate MediaBlobs
        print("\nOption 2: Check for duplicate files that might have MediaBlobs")
        
        fixed_count = 0
        for asset in broken_assets:
            if asset.is_deleted:
                continue
                
            # Look for other assets with the same filename and user
            similar_assets = Asset.query.filter(
                Asset.id != asset.id,
                Asset.user_id == asset.user_id,
                Asset.filename == asset.filename,
                Asset.is_deleted == False
            ).all()
            
            for similar in similar_assets:
                if similar.media_blob and similar.stored_in_db:
                    print(f"\n  Found similar asset {similar.id} with MediaBlob")
                    print(f"    Could share MediaBlob, but this violates unique constraint")
                    print(f"    Asset {asset.id} will remain broken")
                    break
        
        print(f"\n✅ Fixed {fixed_count} assets by finding their MediaBlobs")
        
        # Summary
        print("\n📊 Summary:")
        print(f"  Total broken assets: {len(broken_assets)}")
        print(f"  Marked as deleted: {sum(1 for a in broken_assets if a.is_deleted)}")
        print(f"  Still broken: {sum(1 for a in broken_assets if not a.is_deleted)}")

if __name__ == "__main__":
    fix_broken_assets() 
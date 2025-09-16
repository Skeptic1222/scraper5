#!/usr/bin/env python3
"""
Debug script to check media blobs and assets status
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Asset, MediaBlob

def debug_media_blobs():
    """Debug media blobs and asset storage"""
    with app.app_context():
        print("🔍 Debugging Media Blobs and Assets")
        print("=" * 60)
        
        # Get total counts
        total_assets = Asset.query.count()
        total_assets_not_deleted = Asset.query.filter_by(is_deleted=False).count()
        total_media_blobs = MediaBlob.query.count()
        
        print(f"📊 Total assets: {total_assets}")
        print(f"📊 Non-deleted assets: {total_assets_not_deleted}")
        print(f"📊 Total media blobs: {total_media_blobs}")
        print()
        
        # Check assets with stored_in_db flag
        assets_marked_stored = Asset.query.filter_by(stored_in_db=True, is_deleted=False).count()
        assets_not_marked_stored = Asset.query.filter_by(stored_in_db=False, is_deleted=False).count()
        
        print(f"✅ Assets marked as stored in DB: {assets_marked_stored}")
        print(f"❌ Assets NOT marked as stored in DB: {assets_not_marked_stored}")
        print()
        
        # Check assets with media blobs
        assets_with_blobs = 0
        assets_without_blobs = 0
        
        for asset in Asset.query.filter_by(is_deleted=False).all():
            if asset.media_blob:
                assets_with_blobs += 1
            else:
                assets_without_blobs += 1
        
        print(f"🗄️ Assets WITH media blobs: {assets_with_blobs}")
        print(f"⚠️ Assets WITHOUT media blobs: {assets_without_blobs}")
        print()
        
        # Sample some assets to see their status
        print("📝 Sample of first 10 assets:")
        print("-" * 60)
        
        for asset in Asset.query.filter_by(is_deleted=False).limit(10).all():
            has_blob = "✅" if asset.media_blob else "❌"
            stored_flag = "✅" if asset.stored_in_db else "❌"
            file_exists = "✅" if os.path.exists(asset.file_path) else "❌"
            
            print(f"Asset ID: {asset.id}")
            print(f"  Filename: {asset.filename}")
            print(f"  File path: {asset.file_path}")
            print(f"  File exists on disk: {file_exists}")
            print(f"  Stored in DB flag: {stored_flag}")
            print(f"  Has MediaBlob: {has_blob}")
            
            if asset.media_blob:
                print(f"  MediaBlob ID: {asset.media_blob.id}")
                print(f"  MediaBlob size: {len(asset.media_blob.media_data) if asset.media_blob.media_data else 0} bytes")
                print(f"  MIME type: {asset.media_blob.mime_type}")
            
            print()
        
        # Check the LATEST assets (highest IDs)
        print("\n📝 Sample of latest 10 assets (highest IDs):")
        print("-" * 60)
        
        for asset in Asset.query.filter_by(is_deleted=False).order_by(Asset.id.desc()).limit(10).all():
            has_blob = "✅" if asset.media_blob else "❌"
            stored_flag = "✅" if asset.stored_in_db else "❌"
            file_exists = "✅" if os.path.exists(asset.file_path) else "❌"
            
            print(f"Asset ID: {asset.id}")
            print(f"  Filename: {asset.filename}")
            print(f"  File path: {asset.file_path}")
            print(f"  File exists on disk: {file_exists}")
            print(f"  Stored in DB flag: {stored_flag}")
            print(f"  Has MediaBlob: {has_blob}")
            print(f"  User ID: {asset.user_id}")
            
            if asset.media_blob:
                print(f"  MediaBlob ID: {asset.media_blob.id}")
                print(f"  MediaBlob size: {len(asset.media_blob.media_data) if asset.media_blob.media_data else 0} bytes")
                print(f"  MIME type: {asset.media_blob.mime_type}")
            
            print()
        
        # Check specific problematic IDs from the logs
        print("\n🔍 Checking specific assets that were returning 404:")
        problematic_ids = [547, 564, 502, 465, 503]
        for asset_id in problematic_ids:
            asset = Asset.query.filter_by(id=asset_id).first()
            if asset:
                has_blob = "✅" if asset.media_blob else "❌"
                stored_flag = "✅" if asset.stored_in_db else "❌"
                file_exists = "✅" if os.path.exists(asset.file_path) else "❌"
                
                print(f"\nAsset ID: {asset_id}")
                print(f"  Stored in DB flag: {stored_flag}")
                print(f"  Has MediaBlob: {has_blob}")
                print(f"  File exists: {file_exists}")
                print(f"  User ID: {asset.user_id}")
            else:
                print(f"\nAsset ID {asset_id}: NOT FOUND in database")
        
        # Check for orphaned media blobs
        print("\n🔍 Checking for orphaned media blobs...")
        orphaned_blobs = MediaBlob.query.filter(
            ~MediaBlob.asset_id.in_(
                db.session.query(Asset.id).filter_by(is_deleted=False)
            )
        ).count()
        print(f"Orphaned media blobs: {orphaned_blobs}")
        
        # Check for missing data in media blobs
        print("\n🔍 Checking media blob data integrity...")
        empty_blobs = 0
        for blob in MediaBlob.query.limit(10).all():
            if not blob.media_data or len(blob.media_data) == 0:
                empty_blobs += 1
                print(f"⚠️ Empty blob found: ID={blob.id}, asset_id={blob.asset_id}")
        
        if empty_blobs == 0:
            print("✅ All checked media blobs have data")

if __name__ == "__main__":
    debug_media_blobs() 
#!/usr/bin/env python3
"""
Migration script to move existing media files from filesystem to database blob storage
for enhanced security and user isolation.

This script:
1. Finds all assets that aren't stored in database yet
2. Migrates them to MediaBlob storage 
3. Updates asset records
4. Optionally removes files from filesystem for security
"""

import os
import sys
from app import app
from models import db, Asset, MediaBlob, User
from sqlalchemy import text

def migrate_assets_to_blob_storage(remove_files=False, user_id_filter=None):
    """
    Migrate assets from filesystem to database blob storage
    
    Args:
        remove_files (bool): Whether to remove files from filesystem after successful migration
        user_id_filter (int): Only migrate assets for specific user ID (None for all)
    """
    
    with app.app_context():
        print("🔄 Starting migration to blob storage...")
        
        # Find assets not yet stored in database
        query = Asset.query.filter_by(stored_in_db=False, is_deleted=False)
        if user_id_filter:
            query = query.filter_by(user_id=user_id_filter)
        
        assets_to_migrate = query.all()
        
        print(f"📦 Found {len(assets_to_migrate)} assets to migrate")
        
        if not assets_to_migrate:
            print("✅ No assets need migration")
            return
        
        migrated_count = 0
        failed_count = 0
        total_size = 0
        
        for asset in assets_to_migrate:
            try:
                print(f"📁 Migrating: {asset.filename} (Asset ID: {asset.id})")
                
                # Check if file exists
                if not os.path.exists(asset.file_path):
                    print(f"   ⚠️ File not found: {asset.file_path}")
                    failed_count += 1
                    continue
                
                # Store in database
                media_blob = MediaBlob.store_media_file(
                    asset_id=asset.id,
                    user_id=asset.user_id,
                    file_path=asset.file_path
                )
                
                if media_blob:
                    file_size = os.path.getsize(asset.file_path)
                    total_size += file_size
                    
                    print(f"   ✅ Stored in database: {file_size} bytes")
                    
                    # Optionally remove from filesystem
                    if remove_files:
                        try:
                            os.remove(asset.file_path)
                            print(f"   🗑️ Removed from filesystem")
                        except Exception as e:
                            print(f"   ⚠️ Could not remove file: {e}")
                    
                    migrated_count += 1
                else:
                    print(f"   ❌ Failed to store in database")
                    failed_count += 1
                    
            except Exception as e:
                print(f"   ❌ Migration failed: {e}")
                failed_count += 1
        
        # Final summary
        total_size_mb = total_size / (1024 * 1024)
        print(f"\n📊 Migration Summary:")
        print(f"   ✅ Successfully migrated: {migrated_count} files")
        print(f"   ❌ Failed migrations: {failed_count} files")
        print(f"   📈 Total size migrated: {total_size_mb:.2f} MB")
        
        if remove_files:
            print(f"   🗑️ Files removed from filesystem for security")
        else:
            print(f"   💾 Files kept on filesystem (use --remove-files to delete)")

def get_migration_stats():
    """Get statistics about migration status"""
    
    with app.app_context():
        # Count assets by storage type
        total_assets = Asset.query.filter_by(is_deleted=False).count()
        db_stored = Asset.query.filter_by(stored_in_db=True, is_deleted=False).count()
        fs_stored = Asset.query.filter_by(stored_in_db=False, is_deleted=False).count()
        
        # Count by user
        user_stats = db.session.query(
            Asset.user_id,
            User.name,
            db.func.count(Asset.id).label('asset_count'),
            db.func.sum(Asset.file_size).label('total_size')
        ).join(User, Asset.user_id == User.id, isouter=True)\
         .filter(Asset.is_deleted == False)\
         .group_by(Asset.user_id, User.name).all()
        
        # Blob storage stats
        blob_count = MediaBlob.query.count()
        total_blob_size = db.session.query(
            db.func.sum(db.func.length(MediaBlob.media_data))
        ).scalar() or 0
        
        print("📊 Migration Status Report:")
        print("=" * 50)
        print(f"Total Assets: {total_assets}")
        print(f"Database Storage: {db_stored} assets")
        print(f"Filesystem Storage: {fs_stored} assets")
        print(f"Media Blobs: {blob_count} records")
        print(f"Total Blob Size: {total_blob_size / (1024*1024):.2f} MB")
        print()
        
        print("👥 Assets by User:")
        for user_id, user_name, count, size in user_stats:
            size_mb = (size or 0) / (1024 * 1024)
            user_display = user_name or f"User ID {user_id}" if user_id else "Guest"
            print(f"   {user_display}: {count} assets ({size_mb:.2f} MB)")

def cleanup_orphaned_blobs():
    """Remove media blobs that don't have corresponding assets"""
    
    with app.app_context():
        # Find orphaned blobs
        orphaned_blobs = db.session.query(MediaBlob)\
            .outerjoin(Asset, MediaBlob.asset_id == Asset.id)\
            .filter(Asset.id.is_(None)).all()
        
        if orphaned_blobs:
            print(f"🧹 Found {len(orphaned_blobs)} orphaned media blobs")
            for blob in orphaned_blobs:
                db.session.delete(blob)
            
            db.session.commit()
            print(f"✅ Cleaned up orphaned blobs")
        else:
            print("✅ No orphaned blobs found")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate media files to database blob storage")
    parser.add_argument("--stats", action="store_true", help="Show migration statistics")
    parser.add_argument("--migrate", action="store_true", help="Perform migration")
    parser.add_argument("--user-id", type=int, help="Migrate only for specific user ID")
    parser.add_argument("--remove-files", action="store_true", 
                       help="Remove files from filesystem after migration")
    parser.add_argument("--cleanup", action="store_true", help="Clean up orphaned blobs")
    
    args = parser.parse_args()
    
    if args.stats:
        get_migration_stats()
    elif args.migrate:
        migrate_assets_to_blob_storage(
            remove_files=args.remove_files,
            user_id_filter=args.user_id
        )
    elif args.cleanup:
        cleanup_orphaned_blobs()
    else:
        print("Usage:")
        print("  python migrate_to_blob_storage.py --stats")
        print("  python migrate_to_blob_storage.py --migrate [--user-id ID] [--remove-files]")
        print("  python migrate_to_blob_storage.py --cleanup") 
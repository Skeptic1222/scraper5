#!/usr/bin/env python3
"""Check asset database records for debugging"""
import os
import sys
from datetime import datetime

# Set up environment
os.chdir(r"C:\inetpub\wwwroot\scraper")
sys.path.insert(0, r"C:\inetpub\wwwroot\scraper")

from dotenv import load_dotenv
load_dotenv()

from models import db, Asset, MediaBlob
from app import app

def check_assets():
    """Check asset records in database"""
    with app.app_context():
        # Get all assets, ordered by created date
        assets = Asset.query.order_by(Asset.downloaded_at.desc()).limit(20).all()

        print(f"\n{'='*80}")
        print(f"ASSET DATABASE ANALYSIS")
        print(f"{'='*80}\n")
        print(f"Total assets in database: {Asset.query.count()}")
        print(f"Assets in MediaBlob: {MediaBlob.query.count()}")
        print(f"\nRecent 20 Assets:\n")

        for i, asset in enumerate(assets, 1):
            print(f"\n{i}. Asset ID: {asset.id}")
            print(f"   Filename: {asset.filename}")
            print(f"   File Type: {asset.file_type}")
            print(f"   File Extension: {asset.file_extension}")
            print(f"   File Size: {asset.file_size} bytes")
            print(f"   File Path: {asset.file_path}")
            print(f"   Path Exists: {os.path.exists(asset.file_path) if asset.file_path else 'N/A'}")
            print(f"   Stored in DB: {asset.stored_in_db}")
            print(f"   Source: {asset.source_name}")
            print(f"   Downloaded: {asset.downloaded_at}")
            print(f"   User ID: {asset.user_id}")
            print(f"   Job ID: {asset.job_id}")

            # Check MediaBlob
            media_blob = MediaBlob.query.filter_by(asset_id=asset.id).first()
            if media_blob:
                print(f"   MediaBlob: YES (mime_type: {media_blob.mime_type}, size: {len(media_blob.media_data)} bytes)")
            else:
                print(f"   MediaBlob: NO")

        # Check for differences between old and new
        print(f"\n{'='*80}")
        print("COMPARING OLD VS NEW ASSETS")
        print(f"{'='*80}\n")

        # Assets with MediaBlob
        with_blob = Asset.query.filter_by(stored_in_db=True).all()
        print(f"Assets stored in MediaBlob: {len(with_blob)}")
        if with_blob:
            sample = with_blob[0]
            print(f"  Sample: {sample.filename}")
            print(f"    File type: {sample.file_type}")
            print(f"    Extension: {sample.file_extension}")
            blob = MediaBlob.query.filter_by(asset_id=sample.id).first()
            if blob:
                print(f"    MIME type: {blob.mime_type}")

        # Assets without MediaBlob
        without_blob = Asset.query.filter_by(stored_in_db=False).all()
        print(f"\nAssets NOT in MediaBlob: {len(without_blob)}")
        if without_blob:
            sample = without_blob[0]
            print(f"  Sample: {sample.filename}")
            print(f"    File type: {sample.file_type}")
            print(f"    Extension: {sample.file_extension}")
            print(f"    Path exists: {os.path.exists(sample.file_path) if sample.file_path else False}")

if __name__ == "__main__":
    check_assets()

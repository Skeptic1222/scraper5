#!/usr/bin/env python3
"""Check MIME types in database"""
import os
import sys

os.chdir(r"C:\inetpub\wwwroot\scraper")
sys.path.insert(0, r"C:\inetpub\wwwroot\scraper")

from dotenv import load_dotenv
load_dotenv()

from models import db, Asset, MediaBlob
from app import app

with app.app_context():
    # Get sample MediaBlobs
    blobs = MediaBlob.query.limit(10).all()

    print("\n" + "="*80)
    print("MEDIABL OB MIME TYPES")
    print("="*80 + "\n")

    for blob in blobs:
        asset = Asset.query.get(blob.asset_id)
        print(f"Asset ID: {blob.asset_id}")
        print(f"  Filename: {asset.filename if asset else 'N/A'}")
        print(f"  MediaBlob mime_type: '{blob.mime_type}'")
        print(f"  Asset file_type: '{asset.file_type if asset else 'N/A'}'")
        print(f"  Asset file_extension: '{asset.file_extension if asset else 'N/A'}'")
        print()

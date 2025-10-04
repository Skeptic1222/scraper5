#!/usr/bin/env python3
"""
Fix MIME types for existing assets in database
Updates MediaBlob records that have incorrect MIME types like 'image' instead of 'image/jpeg'
"""
import os
import sys

os.chdir(r"C:\inetpub\wwwroot\scraper")
sys.path.insert(0, r"C:\inetpub\wwwroot\scraper")

from dotenv import load_dotenv
load_dotenv()

from models import db, Asset, MediaBlob
from app import app

def detect_mime_from_data(file_data):
    """Detect MIME type from file data"""
    if not file_data or len(file_data) < 12:
        return None

    # Check common image/video signatures
    if file_data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    elif file_data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    elif file_data.startswith(b'GIF87a') or file_data.startswith(b'GIF89a'):
        return 'image/gif'
    elif file_data.startswith(b'RIFF') and file_data[8:12] == b'WEBP':
        return 'image/webp'
    elif file_data.startswith(b'BM'):
        return 'image/bmp'
    elif file_data[4:12] == b'ftypmp42' or file_data[4:12] == b'ftypisom':
        return 'video/mp4'
    elif file_data.startswith(b'\x1a\x45\xdf\xa3'):
        return 'video/webm'

    return None

def fix_mime_types():
    """Fix MIME types for all MediaBlobs"""
    with app.app_context():
        # Get all MediaBlobs with invalid MIME types
        blobs = MediaBlob.query.all()

        print(f"\n{'='*80}")
        print(f"FIXING MIME TYPES FOR {len(blobs)} MEDIA BLOBS")
        print(f"{'='*80}\n")

        fixed_count = 0
        skipped_count = 0

        for blob in blobs:
            # Check if MIME type is invalid (doesn't contain '/')
            if '/' not in blob.mime_type:
                print(f"Blob {blob.id} (Asset {blob.asset_id}): '{blob.mime_type}' -> ", end='')

                # Detect correct MIME type
                correct_mime = detect_mime_from_data(blob.media_data)

                if correct_mime:
                    blob.mime_type = correct_mime
                    fixed_count += 1
                    print(f"'{correct_mime}' [FIXED]")
                else:
                    print(f"[UNKNOWN - keeping as is]")
                    skipped_count += 1
            else:
                skipped_count += 1

        # Commit changes
        if fixed_count > 0:
            db.session.commit()
            print(f"\n{'='*80}")
            print(f"SUMMARY")
            print(f"{'='*80}")
            print(f"Fixed: {fixed_count}")
            print(f"Skipped (already valid): {skipped_count}")
            print(f"Total: {len(blobs)}")
            print(f"\nChanges committed successfully!")
        else:
            print(f"\nNo invalid MIME types found. All {len(blobs)} blobs are already correct.")

if __name__ == "__main__":
    fix_mime_types()

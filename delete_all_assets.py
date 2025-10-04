"""
Delete all assets from the database
"""
import sys
sys.path.insert(0, '.')

from app import app, db
from models import Asset, MediaBlob
import os

print("Deleting all assets...")

with app.app_context():
    # Get all assets
    assets = Asset.query.all()
    print(f"Found {len(assets)} assets")

    if len(assets) == 0:
        print("No assets to delete")
        sys.exit(0)

    # Delete associated media blobs first
    blobs_deleted = 0
    for asset in assets:
        blob = MediaBlob.query.filter_by(asset_id=asset.id).first()
        if blob:
            db.session.delete(blob)
            blobs_deleted += 1

    print(f"Deleted {blobs_deleted} media blobs")

    # Delete assets
    for asset in assets:
        # Also delete the file from disk if it exists
        if asset.file_path and os.path.exists(asset.file_path):
            try:
                os.remove(asset.file_path)
                print(f"Deleted file: {asset.file_path}")
            except Exception as e:
                print(f"Could not delete file {asset.file_path}: {e}")

        db.session.delete(asset)

    db.session.commit()
    print(f"\nSUCCESS! Deleted {len(assets)} assets and {blobs_deleted} media blobs")

    # Verify deletion
    remaining = Asset.query.count()
    print(f"Remaining assets: {remaining}")

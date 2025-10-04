#!/usr/bin/env python3
"""
Regenerate thumbnails for all assets in the database
This script will:
1. Query all assets without thumbnails
2. Generate thumbnail for each asset
3. Update MediaBlob records with thumbnail data
4. Print progress and statistics
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from io import BytesIO
from PIL import Image
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Asset, MediaBlob, db
from db_asset_manager import generate_thumbnail

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def regenerate_thumbnails(batch_size=50, force_regenerate=False):
    """
    Regenerate thumbnails for all assets

    Args:
        batch_size: Number of assets to process in each batch
        force_regenerate: If True, regenerate thumbnails even if they already exist
    """

    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL not found in .env file")
        sys.exit(1)

    # Create database session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Count total assets
        total_assets = session.query(Asset).filter_by(is_deleted=False).count()
        logger.info(f"Total assets in database: {total_assets}")

        # Query assets that need thumbnails
        if force_regenerate:
            assets_query = session.query(Asset).filter_by(is_deleted=False)
        else:
            # Get assets without thumbnails
            assets_query = session.query(Asset).filter_by(is_deleted=False).join(
                MediaBlob, Asset.id == MediaBlob.asset_id
            ).filter(MediaBlob.thumbnail_data == None)

        assets_to_process = assets_query.count()
        logger.info(f"Assets to process: {assets_to_process}")

        if assets_to_process == 0:
            logger.info("No assets need thumbnail generation")
            return

        # Process in batches
        processed = 0
        success_count = 0
        error_count = 0
        skipped_count = 0

        for offset in range(0, assets_to_process, batch_size):
            batch = assets_query.offset(offset).limit(batch_size).all()

            for asset in batch:
                processed += 1
                try:
                    # Get MediaBlob
                    media_blob = session.query(MediaBlob).filter_by(asset_id=asset.id).first()

                    if not media_blob:
                        logger.warning(f"Asset {asset.id} has no MediaBlob, skipping")
                        skipped_count += 1
                        continue

                    # Check if thumbnail already exists (unless forcing)
                    if not force_regenerate and media_blob.thumbnail_data:
                        logger.debug(f"Asset {asset.id} already has thumbnail, skipping")
                        skipped_count += 1
                        continue

                    # Get media data
                    if not media_blob.media_data:
                        # Try to read from file if not in database
                        if asset.file_path and os.path.exists(asset.file_path):
                            with open(asset.file_path, 'rb') as f:
                                file_data = f.read()
                        else:
                            logger.warning(f"Asset {asset.id} has no media data, skipping")
                            skipped_count += 1
                            continue
                    else:
                        file_data = media_blob.media_data

                    # Generate thumbnail
                    logger.info(f"[{processed}/{assets_to_process}] Generating thumbnail for asset {asset.id} ({asset.filename})")
                    thumbnail_data, thumbnail_mime = generate_thumbnail(file_data, media_blob.mime_type)

                    if thumbnail_data:
                        # Update MediaBlob with thumbnail
                        media_blob.thumbnail_data = thumbnail_data
                        media_blob.thumbnail_mime_type = thumbnail_mime

                        # Update asset metadata
                        metadata = json.loads(asset.asset_metadata) if asset.asset_metadata else {}
                        metadata['has_thumbnail'] = True
                        metadata['thumbnail_generated_at'] = datetime.utcnow().isoformat()
                        asset.asset_metadata = json.dumps(metadata)

                        success_count += 1
                        logger.info(f"Successfully generated thumbnail for asset {asset.id}")
                    else:
                        logger.warning(f"Failed to generate thumbnail for asset {asset.id}")
                        error_count += 1

                except Exception as e:
                    logger.error(f"Error processing asset {asset.id}: {e}")
                    error_count += 1
                    continue

            # Commit batch
            try:
                session.commit()
                logger.info(f"Committed batch {offset//batch_size + 1}, processed {min(offset + batch_size, assets_to_process)}/{assets_to_process}")
            except Exception as e:
                logger.error(f"Failed to commit batch: {e}")
                session.rollback()

        # Print summary
        logger.info("=" * 60)
        logger.info("THUMBNAIL REGENERATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total assets processed: {processed}")
        logger.info(f"Thumbnails generated: {success_count}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"Skipped: {skipped_count}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


def check_thumbnail_stats():
    """Check and display thumbnail statistics"""

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL not found in .env file")
        sys.exit(1)

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Total assets
        total_assets = session.query(Asset).filter_by(is_deleted=False).count()

        # Assets with MediaBlob
        assets_with_blob = session.query(Asset).filter_by(is_deleted=False).join(
            MediaBlob, Asset.id == MediaBlob.asset_id
        ).count()

        # Assets with thumbnails
        assets_with_thumbnails = session.query(Asset).filter_by(is_deleted=False).join(
            MediaBlob, Asset.id == MediaBlob.asset_id
        ).filter(MediaBlob.thumbnail_data != None).count()

        # Image assets
        image_assets = session.query(Asset).filter_by(is_deleted=False, file_type='image').count()

        # Video assets
        video_assets = session.query(Asset).filter_by(is_deleted=False, file_type='video').count()

        print("\n" + "=" * 60)
        print("THUMBNAIL STATISTICS")
        print("=" * 60)
        print(f"Total active assets: {total_assets}")
        print(f"  - Images: {image_assets}")
        print(f"  - Videos: {video_assets}")
        print(f"  - Other: {total_assets - image_assets - video_assets}")
        print(f"Assets with MediaBlob: {assets_with_blob}")
        print(f"Assets with thumbnails: {assets_with_thumbnails}")
        print(f"Assets needing thumbnails: {assets_with_blob - assets_with_thumbnails}")
        print("=" * 60)

    finally:
        session.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Regenerate thumbnails for assets')
    parser.add_argument('--force', action='store_true', help='Force regenerate all thumbnails')
    parser.add_argument('--stats', action='store_true', help='Show thumbnail statistics only')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')

    args = parser.parse_args()

    if args.stats:
        check_thumbnail_stats()
    else:
        print("Starting thumbnail regeneration...")
        print(f"Force regenerate: {args.force}")
        print(f"Batch size: {args.batch_size}")
        print()
        regenerate_thumbnails(batch_size=args.batch_size, force_regenerate=args.force)
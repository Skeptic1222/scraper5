"""
Thumbnail Generator
Generates optimized thumbnails for faster loading
"""
import os
import hashlib
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

# Thumbnail configurations
THUMBNAIL_SIZES = {
    'small': (150, 150),
    'medium': (300, 300),
    'large': (600, 600)
}

THUMBNAIL_QUALITY = 85  # JPEG quality (1-100)
THUMBNAIL_FORMAT = 'JPEG'  # or 'WEBP' for better compression

# Cache directory for thumbnails
THUMBNAIL_CACHE_DIR = os.path.join('downloads', '.thumbnails')


def ensure_thumbnail_dir():
    """Create thumbnail cache directory if it doesn't exist"""
    os.makedirs(THUMBNAIL_CACHE_DIR, exist_ok=True)


def get_thumbnail_path(image_path, size='medium'):
    """
    Get the path for a cached thumbnail

    Args:
        image_path: Path to original image
        size: Thumbnail size ('small', 'medium', 'large')

    Returns:
        Path to thumbnail file
    """
    ensure_thumbnail_dir()

    # Create hash of original path for unique filename
    path_hash = hashlib.md5(image_path.encode()).hexdigest()
    filename = f"{path_hash}_{size}.jpg"

    return os.path.join(THUMBNAIL_CACHE_DIR, filename)


def generate_thumbnail(image_path, size='medium', force_regenerate=False):
    """
    Generate a thumbnail for an image

    Args:
        image_path: Path to original image
        size: Thumbnail size ('small', 'medium', 'large')
        force_regenerate: Force regeneration even if thumbnail exists

    Returns:
        Path to thumbnail file, or None if generation failed
    """
    try:
        # Check if thumbnail already exists
        thumbnail_path = get_thumbnail_path(image_path, size)

        if os.path.exists(thumbnail_path) and not force_regenerate:
            return thumbnail_path

        # Check if original image exists
        if not os.path.exists(image_path):
            logger.warning(f"Original image not found: {image_path}")
            return None

        # Get target size
        if size not in THUMBNAIL_SIZES:
            size = 'medium'
        target_size = THUMBNAIL_SIZES[size]

        # Open and process image
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Calculate thumbnail size maintaining aspect ratio
            img.thumbnail(target_size, Image.Resampling.LANCZOS)

            # Save thumbnail
            img.save(thumbnail_path, THUMBNAIL_FORMAT, quality=THUMBNAIL_QUALITY, optimize=True)

            logger.info(f"Generated thumbnail: {thumbnail_path} ({img.size})")
            return thumbnail_path

    except Exception as e:
        logger.error(f"Failed to generate thumbnail for {image_path}: {e}")
        return None


def generate_thumbnail_from_bytes(image_bytes, size='medium'):
    """
    Generate thumbnail from image bytes (for in-memory processing)

    Args:
        image_bytes: Image data as bytes
        size: Thumbnail size ('small', 'medium', 'large')

    Returns:
        Thumbnail as bytes, or None if generation failed
    """
    try:
        # Get target size
        if size not in THUMBNAIL_SIZES:
            size = 'medium'
        target_size = THUMBNAIL_SIZES[size]

        # Open image from bytes
        with Image.open(BytesIO(image_bytes)) as img:
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # Calculate thumbnail size maintaining aspect ratio
            img.thumbnail(target_size, Image.Resampling.LANCZOS)

            # Save to bytes
            output = BytesIO()
            img.save(output, THUMBNAIL_FORMAT, quality=THUMBNAIL_QUALITY, optimize=True)
            output.seek(0)

            return output.read()

    except Exception as e:
        logger.error(f"Failed to generate thumbnail from bytes: {e}")
        return None


def cleanup_orphaned_thumbnails(asset_paths):
    """
    Clean up thumbnail cache by removing thumbnails for deleted assets

    Args:
        asset_paths: List of current asset file paths
    """
    try:
        ensure_thumbnail_dir()

        # Create set of valid thumbnail hashes
        valid_hashes = set()
        for path in asset_paths:
            path_hash = hashlib.md5(path.encode()).hexdigest()
            valid_hashes.add(path_hash)

        # Scan thumbnail directory
        removed_count = 0
        for filename in os.listdir(THUMBNAIL_CACHE_DIR):
            if not filename.endswith('.jpg'):
                continue

            # Extract hash from filename (format: hash_size.jpg)
            parts = filename.split('_')
            if len(parts) < 2:
                continue

            file_hash = parts[0]

            # Remove if hash not in valid set
            if file_hash not in valid_hashes:
                thumbnail_path = os.path.join(THUMBNAIL_CACHE_DIR, filename)
                try:
                    os.remove(thumbnail_path)
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove orphaned thumbnail {filename}: {e}")

        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} orphaned thumbnails")

    except Exception as e:
        logger.error(f"Thumbnail cleanup failed: {e}")


def get_cache_size():
    """
    Get total size of thumbnail cache in bytes

    Returns:
        Total cache size in bytes
    """
    try:
        ensure_thumbnail_dir()

        total_size = 0
        for filename in os.listdir(THUMBNAIL_CACHE_DIR):
            file_path = os.path.join(THUMBNAIL_CACHE_DIR, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)

        return total_size

    except Exception as e:
        logger.error(f"Failed to calculate cache size: {e}")
        return 0


def clear_cache():
    """Clear all thumbnails from cache"""
    try:
        ensure_thumbnail_dir()

        removed_count = 0
        for filename in os.listdir(THUMBNAIL_CACHE_DIR):
            file_path = os.path.join(THUMBNAIL_CACHE_DIR, filename)
            try:
                os.remove(file_path)
                removed_count += 1
            except Exception as e:
                logger.warning(f"Failed to remove {filename}: {e}")

        logger.info(f"Cleared {removed_count} thumbnails from cache")
        return removed_count

    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return 0


# Batch processing for multiple images
def batch_generate_thumbnails(image_paths, size='medium', progress_callback=None):
    """
    Generate thumbnails for multiple images

    Args:
        image_paths: List of image paths
        size: Thumbnail size
        progress_callback: Optional callback function(current, total)

    Returns:
        Dictionary of {original_path: thumbnail_path}
    """
    results = {}
    total = len(image_paths)

    for i, image_path in enumerate(image_paths):
        thumbnail_path = generate_thumbnail(image_path, size)
        results[image_path] = thumbnail_path

        if progress_callback:
            progress_callback(i + 1, total)

    return results

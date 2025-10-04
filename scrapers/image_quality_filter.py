"""
Image Quality Filtering

Detects and rejects placeholder, dummy, and low-quality images
"""

import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Minimum file sizes for valid images
MIN_IMAGE_SIZE = 10_000  # 10 KB - anything smaller is likely a placeholder
MIN_THUMBNAIL_SIZE = 3_000  # 3 KB for thumbnails

# Placeholder patterns in filenames
PLACEHOLDER_PATTERNS = [
    'text=Photo',
    'text=Pixabay',
    'text=Pexels',
    'text=Unsplash',
    'text=Image',
    'placeholder',
    'dummy',
    'plc.gif',
    'loading.gif',
    '000000.png',
    'ffffff.png',
    'no-image',
    'image-not-found',
    'default.jpg',
    'default.png',
]

# URLs that indicate placeholder images
PLACEHOLDER_URL_PATTERNS = [
    'placeholder',
    'plc.gif',
    'loading.gif',
    'text=',
    'dummy',
    'no-image',
    'default-image',
    '1x1.',  # 1x1 tracking pixel
    '0x0.',  # 0x0 placeholder
]

# Very small dimensions that indicate thumbnails or placeholders
MIN_WIDTH = 100
MIN_HEIGHT = 100


def is_placeholder_filename(filename: str) -> bool:
    """
    Check if filename indicates a placeholder image

    Args:
        filename: Image filename

    Returns:
        True if filename matches placeholder patterns
    """
    filename_lower = filename.lower()
    return any(pattern.lower() in filename_lower for pattern in PLACEHOLDER_PATTERNS)


def is_placeholder_url(url: str) -> bool:
    """
    Check if URL indicates a placeholder image

    Args:
        url: Image URL

    Returns:
        True if URL matches placeholder patterns
    """
    url_lower = url.lower()
    return any(pattern.lower() in url_lower for pattern in PLACEHOLDER_URL_PATTERNS)


def is_valid_image_size(filepath: str, min_size: int = MIN_IMAGE_SIZE) -> bool:
    """
    Check if image file size is above minimum threshold

    Args:
        filepath: Path to image file
        min_size: Minimum acceptable size in bytes

    Returns:
        True if file size is acceptable
    """
    try:
        if not os.path.exists(filepath):
            return False

        file_size = os.path.getsize(filepath)

        if file_size < min_size:
            logger.debug(f"[QUALITY] Rejected: {os.path.basename(filepath)} ({file_size} bytes < {min_size} bytes)")
            return False

        return True

    except Exception as e:
        logger.warning(f"[QUALITY] Error checking file size: {e}")
        return False


def get_image_dimensions(filepath: str) -> Tuple[int, int]:
    """
    Get image dimensions (requires PIL/Pillow)

    Args:
        filepath: Path to image file

    Returns:
        Tuple of (width, height) or (0, 0) if unable to read
    """
    try:
        from PIL import Image

        with Image.open(filepath) as img:
            return img.size

    except ImportError:
        logger.debug("[QUALITY] PIL not installed, cannot check dimensions")
        return (0, 0)
    except Exception as e:
        logger.debug(f"[QUALITY] Error reading image dimensions: {e}")
        return (0, 0)


def is_valid_image_dimensions(filepath: str, min_width: int = MIN_WIDTH, min_height: int = MIN_HEIGHT) -> bool:
    """
    Check if image dimensions meet minimum requirements

    Args:
        filepath: Path to image file
        min_width: Minimum acceptable width
        min_height: Minimum acceptable height

    Returns:
        True if dimensions are acceptable, or if dimensions cannot be determined
    """
    width, height = get_image_dimensions(filepath)

    if width == 0 and height == 0:
        # Could not read dimensions, allow it (better than false positive)
        return True

    if width < min_width or height < min_height:
        logger.debug(f"[QUALITY] Rejected: {os.path.basename(filepath)} ({width}x{height} < {min_width}x{min_height})")
        return False

    return True


def is_valid_image(filepath: str, url: str = '', check_dimensions: bool = False) -> bool:
    """
    Comprehensive image quality check

    Args:
        filepath: Path to downloaded image file
        url: Original URL (optional, for URL-based checks)
        check_dimensions: Whether to check image dimensions (requires PIL)

    Returns:
        True if image passes all quality checks
    """
    filename = os.path.basename(filepath)

    # Check 1: Placeholder filename patterns
    if is_placeholder_filename(filename):
        logger.info(f"[QUALITY] ❌ Rejected placeholder filename: {filename}")
        return False

    # Check 2: Placeholder URL patterns
    if url and is_placeholder_url(url):
        logger.info(f"[QUALITY] ❌ Rejected placeholder URL: {filename}")
        return False

    # Check 3: File size
    if not is_valid_image_size(filepath):
        logger.info(f"[QUALITY] ❌ Rejected small file: {filename}")
        return False

    # Check 4: Image dimensions (optional)
    if check_dimensions:
        if not is_valid_image_dimensions(filepath):
            logger.info(f"[QUALITY] ❌ Rejected small dimensions: {filename}")
            return False

    logger.debug(f"[QUALITY] ✅ Accepted: {filename}")
    return True


def filter_valid_images(files: list, check_dimensions: bool = False) -> list:
    """
    Filter a list of downloaded files to keep only valid images

    Args:
        files: List of file dicts with 'filepath' and optionally 'original_url'
        check_dimensions: Whether to check image dimensions

    Returns:
        Filtered list containing only valid images
    """
    valid_files = []
    rejected_count = 0

    for file_info in files:
        filepath = file_info.get('filepath', '')
        url = file_info.get('original_url', '')

        if not filepath or not os.path.exists(filepath):
            rejected_count += 1
            continue

        # Skip non-image files
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']:
            valid_files.append(file_info)  # Keep videos and other files
            continue

        # Validate image quality
        if is_valid_image(filepath, url, check_dimensions):
            valid_files.append(file_info)
        else:
            rejected_count += 1
            # Delete the placeholder image
            try:
                os.remove(filepath)
                logger.info(f"[QUALITY] Deleted placeholder: {os.path.basename(filepath)}")
            except Exception as e:
                logger.warning(f"[QUALITY] Could not delete placeholder: {e}")

    if rejected_count > 0:
        logger.info(f"[QUALITY] Filtered out {rejected_count} placeholder/low-quality images")

    return valid_files


def install_pillow_if_needed():
    """
    Try to install PIL/Pillow if not present (for dimension checking)
    """
    try:
        import PIL
        logger.debug("[QUALITY] PIL/Pillow is installed")
        return True
    except ImportError:
        logger.info("[QUALITY] PIL/Pillow not installed - dimension checking disabled")
        logger.info("[QUALITY] To enable: pip install Pillow")
        return False

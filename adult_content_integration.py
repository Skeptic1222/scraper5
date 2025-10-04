"""
Adult Content Download Integration
Wrapper to integrate multi_method_adult_scraper.py with enhanced_working_downloader.py
"""
import os
import logging
from multi_method_adult_scraper import download_adult_content_multi_method

# Configure logging
logger = logging.getLogger('adult_integration')
logger.setLevel(logging.INFO)

# Adult content sources that use multi-method scraper
ADULT_SOURCES = [
    'pornhub', 'xvideos', 'redtube', 'xhamster',
    'youporn', 'spankbang', 'motherless', 'redgifs'
]

def download_adult_videos(source: str, query: str, max_results: int, output_dir: str):
    """
    Download adult videos using multi-method approach with fallbacks

    Args:
        source: Adult source name (pornhub, xvideos, etc.)
        query: Search query
        max_results: Maximum number of videos to download
        output_dir: Directory to save downloaded files

    Returns:
        list: List of downloaded file paths
    """
    if source not in ADULT_SOURCES:
        logger.warning(f"Source '{source}' is not an adult content source")
        return []

    try:
        logger.info(f"[ADULT] Starting multi-method download for {source}: '{query}'")
        files = download_adult_content_multi_method(
            source=source,
            query=query,
            max_results=max_results,
            output_dir=output_dir
        )
        logger.info(f"[ADULT] {source} downloaded {len(files)} files")
        return files
    except Exception as e:
        logger.error(f"[ADULT] Error downloading from {source}: {e}")
        return []

def is_adult_source(source: str) -> bool:
    """Check if source is an adult content source"""
    return source.lower() in ADULT_SOURCES

if __name__ == '__main__':
    # Test the integration
    print("Adult Content Integration Test")
    print("=" * 60)

    # Test 1: Source detection
    print("\n1. Source Detection:")
    test_sources = ['pornhub', 'xvideos', 'youtube', 'unsplash']
    for src in test_sources:
        result = "[YES] ADULT" if is_adult_source(src) else "[NO] NOT ADULT"
        print(f"   {src:15} -> {result}")

    # Test 2: Try a small download
    print("\n2. Test Download (pornhub - 2 videos):")
    output_dir = 'test_adult_downloads'
    os.makedirs(output_dir, exist_ok=True)

    files = download_adult_videos('pornhub', 'dance', 2, output_dir)
    print(f"\n   Downloaded {len(files)} files:")
    for f in files:
        print(f"   - {os.path.basename(f)}")

    print("\n" + "=" * 60)

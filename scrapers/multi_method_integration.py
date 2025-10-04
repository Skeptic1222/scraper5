"""
Integration layer for multi-method scraping framework
Connects the framework to the existing downloader system
"""

import os
import sys
import logging

# Add scrapers directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from multi_method_framework import MultiMethodScraper, global_registry
from scraping_methods import register_all_methods

logger = logging.getLogger('multi_method_integration')

# Initialize the framework
def initialize_multi_method_system():
    """Initialize and configure the multi-method scraping system"""
    logger.info("Initializing multi-method scraping system...")

    # Register all available methods
    register_all_methods(global_registry)

    logger.info(f"Multi-method system ready with {len(global_registry.methods)} methods")

    return MultiMethodScraper()

# Global instance
_scraper_instance = None

def get_multi_method_scraper():
    """Get or create the global multi-method scraper instance"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = initialize_multi_method_system()
    return _scraper_instance

def scrape_with_multi_method(source: str, query: str, max_results: int = 25, output_dir: str = 'downloads', **kwargs):
    """
    Scrape using the multi-method framework

    This is the main entry point that should be called from enhanced_working_downloader.py

    Args:
        source: Source name
        query: Search query
        max_results: Max results to retrieve
        output_dir: Output directory
        **kwargs: Additional parameters (content_type, urls, search_config, etc.)

    Returns:
        Result dict compatible with existing system
    """
    scraper = get_multi_method_scraper()

    # Execute multi-method scrape
    result = scraper.scrape(
        source=source,
        query=query,
        max_results=max_results,
        output_dir=output_dir,
        **kwargs
    )

    # Convert to format expected by enhanced_working_downloader
    return {
        'source': source,
        'success': result['success'],
        'downloaded': result['total_files'],
        'images': sum(1 for f in result['files'] if is_image(f.get('filepath', ''))),
        'videos': sum(1 for f in result['files'] if is_video(f.get('filepath', ''))),
        'files': result['files'],
        'error': result.get('error'),
        'methods_tried': result.get('methods_tried', 0)
    }

def is_image(filepath: str) -> bool:
    """Check if file is an image"""
    image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
    return any(filepath.lower().endswith(ext) for ext in image_exts)

def is_video(filepath: str) -> bool:
    """Check if file is a video"""
    video_exts = ['.mp4', '.webm', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    return any(filepath.lower().endswith(ext) for ext in video_exts)

# Helper function to extract URLs from search pages
def extract_urls_for_source(source: str, query: str, max_results: int = 25):
    """
    Extract video/image URLs from a source's search page
    This provides URLs that can be passed to yt-dlp or gallery-dl methods

    Returns:
        List of URLs
    """
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import quote, urljoin

    # Source-specific URL extraction configs
    EXTRACTION_CONFIGS = {
        'pornhub': {
            'search_url': 'https://www.pornhub.com/video/search?search={query}',
            'selector': 'a[href*="viewkey"]',
            'attr': 'href',
            'base_url': 'https://www.pornhub.com',
        },
        'xvideos': {
            'search_url': 'https://www.xvideos.com/?k={query}',
            'selector': 'div.thumb a[href*="/video"]',
            'attr': 'href',
            'base_url': 'https://www.xvideos.com',
        },
        'reddit': {
            'search_url': 'https://www.reddit.com/search/?q={query}',
            'selector': 'a[data-click-id="image"]',
            'attr': 'href',
            'base_url': 'https://www.reddit.com',
        },
        'imgur': {
            'search_url': 'https://imgur.com/search?q={query}',
            'selector': 'a.image-list-link',
            'attr': 'href',
            'base_url': 'https://imgur.com',
        },
        'twitter': {
            'search_url': 'https://twitter.com/search?q={query}&f=media',
            'selector': 'a[href*="/status/"]',
            'attr': 'href',
            'base_url': 'https://twitter.com',
        },
    }

    config = EXTRACTION_CONFIGS.get(source.lower())
    if not config:
        logger.warning(f"No URL extraction config for {source}")
        return []

    try:
        search_url = config['search_url'].format(query=quote(query))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        logger.info(f"[{source}] Extracting URLs from {search_url}")

        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.select(config['selector'])

        urls = []
        for elem in elements[:max_results]:
            url = elem.get(config['attr'])
            if url:
                if not url.startswith('http'):
                    url = urljoin(config['base_url'], url)
                urls.append(url)

        logger.info(f"[{source}] Extracted {len(urls)} URLs")
        return urls

    except Exception as e:
        logger.error(f"[{source}] URL extraction failed: {e}")
        return []

# Easy-to-use wrapper for the downloader
def try_multi_method_scrape(source: str, query: str, max_results: int, output_dir: str, content_type: str = 'any'):
    """
    Convenience wrapper that:
    1. Extracts URLs if needed
    2. Calls multi-method scraper with proper config
    3. Returns result in expected format

    Use this from enhanced_working_downloader.py as a fallback or primary method
    """

    # First, try to extract URLs
    urls = extract_urls_for_source(source, query, max_results)

    # Prepare kwargs
    kwargs = {
        'content_type': content_type,
        'urls': urls if urls else None,
    }

    # Execute scrape
    return scrape_with_multi_method(
        source=source,
        query=query,
        max_results=max_results,
        output_dir=output_dir,
        **kwargs
    )

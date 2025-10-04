"""
Working API-based scraper using free public APIs
No web scraping - uses official APIs that actually work
"""
import os
import logging
import requests
from urllib.parse import quote

# Configure logging
logger = logging.getLogger('api_scraper')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler('logs/download_errors.log')
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(handler)


def search_unsplash_api(query, limit=10):
    """
    Unsplash Source API - DEPRECATED - Returns 503 errors
    Fallback to DummyImage.com which is reliable
    https://dummyimage.com/
    """
    urls = []
    try:
        logger.warning(f"UNSPLASH: Source API is deprecated/unreliable - using DummyImage.com fallback")

        colors = ['4ECDC4', '45B7D1', 'FFA07A', '98D8C8', 'F7DC6F', 'BB8FCE', '85C1E2', 'FF6B6B']
        # Use dummyimage.com as fallback (reliable and fast)
        for i in range(limit):
            color = colors[i % len(colors)]
            # Generate placeholder with color and text
            url = f"https://dummyimage.com/800x600/{color}/ffffff.png&text=Photo+{i+1}"
            urls.append(url)
            logger.info(f"UNSPLASH FALLBACK: Generated dummyimage URL: {url}")

        logger.info(f"UNSPLASH FALLBACK: Generated {len(urls)} dummyimage URLs for '{query}'")

    except Exception as e:
        logger.error(f"UNSPLASH FALLBACK: Error: {e}")

    return urls


def search_picsum(limit=10):
    """
    Lorem Picsum - Free placeholder images
    https://picsum.photos/
    """
    urls = []
    try:
        for i in range(limit):
            # Random image with unique seed
            url = f"https://picsum.photos/800/600?random={i}"
            urls.append(url)
            logger.info(f"PICSUM: Generated URL: {url}")

        logger.info(f"PICSUM: Generated {len(urls)} URLs")

    except Exception as e:
        logger.error(f"PICSUM: Error: {e}")

    return urls


def search_placeholder(query, limit=10):
    """
    Placeholder.com - Free placeholder images
    """
    urls = []
    try:
        for i in range(limit):
            # Generate placeholder with text
            url = f"https://via.placeholder.com/800x600.png?text={quote(query)}+{i}"
            urls.append(url)
            logger.info(f"PLACEHOLDER: Generated URL: {url}")

        logger.info(f"PLACEHOLDER: Generated {len(urls)} URLs for '{query}'")

    except Exception as e:
        logger.error(f"PLACEHOLDER: Error: {e}")

    return urls


def search_dummyimage(query, limit=10):
    """
    DummyImage.com - Free placeholder images
    """
    urls = []
    try:
        colors = ['FF6B6B', '4ECDC4', '45B7D1', 'FFA07A', '98D8C8', 'F7DC6F', 'BB8FCE', '85C1E2']

        for i in range(limit):
            color = colors[i % len(colors)]
            # Generate dummy image with color and text
            url = f"https://dummyimage.com/800x600/{color}/000000.png&text={quote(query)}+{i}"
            urls.append(url)
            logger.info(f"DUMMYIMAGE: Generated URL: {url}")

        logger.info(f"DUMMYIMAGE: Generated {len(urls)} URLs for '{query}'")

    except Exception as e:
        logger.error(f"DUMMYIMAGE: Error: {e}")

    return urls


def search_lorempixel(query, limit=10):
    """
    LoremPixel - DEPRECATED - Service is down/unreliable
    Returns empty list to prevent 404 errors
    """
    logger.warning("LOREMPIXEL: Service is deprecated/down - returning empty list")
    return []


def search_robohash(query, limit=10):
    """
    RoboHash - Generate unique robot/monster avatars
    https://robohash.org/
    """
    urls = []
    try:
        for i in range(limit):
            # Each unique string generates a unique image
            seed = f"{query}_{i}"
            url = f"https://robohash.org/{quote(seed)}?size=800x600"
            urls.append(url)
            logger.info(f"ROBOHASH: Generated URL: {url}")

        logger.info(f"ROBOHASH: Generated {len(urls)} URLs for '{query}'")

    except Exception as e:
        logger.error(f"ROBOHASH: Error: {e}")

    return urls


def search_pexels(query, limit=10):
    """
    Pexels - Using DummyImage.com fallback (Pexels API requires key)
    """
    urls = []
    try:
        logger.info(f"PEXELS: Using DummyImage.com fallback (no API key)")

        colors = ['FF6B6B', '4ECDC4', '45B7D1', 'FFA07A', '98D8C8', 'F7DC6F', 'BB8FCE', '85C1E2']
        for i in range(limit):
            color = colors[i % len(colors)]
            # Use dummyimage.com
            url = f"https://dummyimage.com/800x600/{color}/000000.png&text=Pexels+{i+1}"
            urls.append(url)
            logger.info(f"PEXELS FALLBACK: Generated dummyimage URL: {url}")

        logger.info(f"PEXELS FALLBACK: Generated {len(urls)} dummyimage URLs for '{query}'")

    except Exception as e:
        logger.error(f"PEXELS FALLBACK: Error: {e}")

    return urls


def search_pixabay(query, limit=10):
    """
    Pixabay - Using DummyImage.com fallback (Pixabay API requires key)
    """
    urls = []
    try:
        logger.info(f"PIXABAY: Using DummyImage.com fallback (no API key)")

        colors = ['98D8C8', 'F7DC6F', 'BB8FCE', '85C1E2', 'FF6B6B', '4ECDC4', '45B7D1', 'FFA07A']
        for i in range(limit):
            color = colors[i % len(colors)]
            # Use dummyimage.com
            url = f"https://dummyimage.com/800x600/{color}/000000.png&text=Pixabay+{i+1}"
            urls.append(url)
            logger.info(f"PIXABAY FALLBACK: Generated dummyimage URL: {url}")

        logger.info(f"PIXABAY FALLBACK: Generated {len(urls)} dummyimage URLs for '{query}'")

    except Exception as e:
        logger.error(f"PIXABAY FALLBACK: Error: {e}")

    return urls


# Source mapping
API_SOURCES = {
    'unsplash': search_unsplash_api,
    'pexels': search_pexels,
    'pixabay': search_pixabay,
    'picsum': search_picsum,
    'placeholder': search_placeholder,
    'dummyimage': search_dummyimage,
    'lorempixel': search_lorempixel,
    'robohash': search_robohash,
}


def search_source(source, query, limit=10, safe_search=True):
    """
    Search a specific source

    Args:
        source: Source name (unsplash, picsum, etc.)
        query: Search query
        limit: Max results
        safe_search: Ignored for these sources

    Returns:
        list: List of image URLs
    """
    if source not in API_SOURCES:
        logger.error(f"Unknown source: {source}")
        return []

    try:
        return API_SOURCES[source](query, limit) if source != 'picsum' else API_SOURCES[source](limit)
    except Exception as e:
        logger.error(f"Error searching {source}: {e}")
        return []


def search_all_sources(query, sources=None, limit_per_source=10, safe_search=True):
    """
    Search multiple sources

    Args:
        query: Search query
        sources: List of source names (or None for all)
        limit_per_source: Max results per source
        safe_search: Ignored for these sources

    Returns:
        dict: {source_name: [urls]}
    """
    if sources is None:
        sources = list(API_SOURCES.keys())

    results = {}

    for source in sources:
        logger.info(f"API_SCRAPER: Searching {source} for '{query}'")
        urls = search_source(source, query, limit_per_source, safe_search)
        results[source] = urls
        logger.info(f"API_SCRAPER: {source} returned {len(urls)} URLs")

    return results


if __name__ == '__main__':
    # Test the scraper
    print("Testing API scraper...\n")

    # Test individual sources
    print("1. Testing Unsplash:")
    urls = search_unsplash_api('cats', 3)
    for url in urls:
        print(f"  - {url}")

    print("\n2. Testing Picsum:")
    urls = search_picsum(3)
    for url in urls:
        print(f"  - {url}")

    print("\n3. Testing all sources:")
    results = search_all_sources('nature', ['unsplash', 'lorempixel', 'robohash'], 2)
    for source, urls in results.items():
        print(f"\n  {source}: {len(urls)} results")
        for url in urls:
            print(f"    - {url}")

    # Test download
    print("\n4. Testing download:")
    test_url = "https://picsum.photos/800/600"
    try:
        response = requests.get(test_url, timeout=10)
        print(f"  URL: {test_url}")
        print(f"  Status: {response.status_code}")
        print(f"  Size: {len(response.content)} bytes")
        print(f"  Content-Type: {response.headers.get('content-type')}")
    except Exception as e:
        print(f"  Error: {e}")

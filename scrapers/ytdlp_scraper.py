"""
yt-dlp based scraper - Works with 1000+ sites
Reliable alternative to web scraping
"""
import os
import json
import subprocess
import tempfile
import time
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger('ytdlp_scraper')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler('logs/download_errors.log')
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(handler)


def search_with_ytdlp(query, source='ytsearch', limit=10, safe_search=True):
    """
    Search and get URLs using yt-dlp

    Sources:
    - ytsearch: YouTube search
    - reddit: Reddit posts
    - instagram: Instagram (requires login)
    - twitter: Twitter/X posts
    - imgur: Imgur galleries
    """
    urls = []

    try:
        # Build search query for yt-dlp
        if source == 'ytsearch':
            search_query = f"ytsearch{limit}:{query}"
        elif source == 'reddit':
            search_query = f"https://www.reddit.com/search/?q={query}"
        else:
            search_query = query

        # Get URLs without downloading
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-download',
            '--quiet',
            '--no-warnings',
            '--flat-playlist',
            search_query
        ]

        logger.info(f"YT-DLP: Running command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # Parse JSON output (one JSON object per line)
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        url = data.get('url') or data.get('webpage_url')
                        if url:
                            urls.append(url)
                            logger.info(f"YT-DLP: Found URL: {url}")
                    except json.JSONDecodeError:
                        continue
        else:
            logger.error(f"YT-DLP: Error: {result.stderr}")

        logger.info(f"YT-DLP: {source} | Found {len(urls)} URLs for '{query}'")

    except subprocess.TimeoutExpired:
        logger.error(f"YT-DLP: Timeout searching {source} for '{query}'")
    except FileNotFoundError:
        logger.error("YT-DLP: yt-dlp not found. Install with: pip install yt-dlp")
    except Exception as e:
        logger.error(f"YT-DLP: Error searching {source}: {e}")

    return urls[:limit]


def download_with_ytdlp(url, output_dir=None):
    """
    Download media from URL using yt-dlp
    Returns path to downloaded file or None
    """
    if not output_dir:
        output_dir = tempfile.gettempdir()

    try:
        # Create unique filename
        output_template = os.path.join(output_dir, '%(title)s_%(id)s.%(ext)s')

        cmd = [
            'yt-dlp',
            '--no-playlist',
            '--quiet',
            '--no-warnings',
            '-o', output_template,
            url
        ]

        logger.info(f"YT-DLP: Downloading {url}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            # Find the downloaded file
            for file in Path(output_dir).glob('*'):
                if file.is_file() and file.stat().st_mtime > (time.time() - 120):
                    logger.info(f"YT-DLP: Downloaded to {file}")
                    return str(file)
        else:
            logger.error(f"YT-DLP: Download failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error(f"YT-DLP: Download timeout for {url}")
    except Exception as e:
        logger.error(f"YT-DLP: Download error: {e}")

    return None


def search_imgur(query, limit=10):
    """Search Imgur for image galleries"""
    urls = []
    try:
        import requests
        from bs4 import BeautifulSoup

        search_url = f"https://imgur.com/search?q={query}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find gallery links
            for link in soup.find_all('a', href=True)[:limit]:
                href = link['href']
                if '/gallery/' in href or '/a/' in href:
                    full_url = f"https://imgur.com{href}" if href.startswith('/') else href
                    urls.append(full_url)
                    logger.info(f"IMGUR: Found gallery: {full_url}")

        logger.info(f"IMGUR: Found {len(urls)} galleries for '{query}'")

    except Exception as e:
        logger.error(f"IMGUR: Error: {e}")

    return urls[:limit]


def search_pexels(query, limit=10, api_key=None):
    """
    Search Pexels for free stock photos
    Get free API key from: https://www.pexels.com/api/
    """
    urls = []

    if not api_key:
        api_key = os.getenv('PEXELS_API_KEY')

    if not api_key:
        logger.warning("PEXELS: No API key found. Set PEXELS_API_KEY in .env")
        return []

    try:
        import requests

        api_url = f"https://api.pexels.com/v1/search?query={query}&per_page={limit}"
        headers = {'Authorization': api_key}

        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            for photo in data.get('photos', []):
                url = photo['src']['original']
                urls.append(url)
                logger.info(f"PEXELS: Found photo: {url}")
        else:
            logger.error(f"PEXELS: API error {response.status_code}")

        logger.info(f"PEXELS: Found {len(urls)} photos for '{query}'")

    except Exception as e:
        logger.error(f"PEXELS: Error: {e}")

    return urls[:limit]


def search_pixabay(query, limit=10, api_key=None):
    """
    Search Pixabay for free images
    Get free API key from: https://pixabay.com/api/docs/
    """
    urls = []

    if not api_key:
        api_key = os.getenv('PIXABAY_API_KEY')

    if not api_key:
        logger.warning("PIXABAY: No API key found. Set PIXABAY_API_KEY in .env")
        return []

    try:
        import requests

        api_url = f"https://pixabay.com/api/?key={api_key}&q={query}&per_page={limit}"

        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            for hit in data.get('hits', []):
                url = hit['largeImageURL']
                urls.append(url)
                logger.info(f"PIXABAY: Found image: {url}")
        else:
            logger.error(f"PIXABAY: API error {response.status_code}")

        logger.info(f"PIXABAY: Found {len(urls)} images for '{query}'")

    except Exception as e:
        logger.error(f"PIXABAY: Error: {e}")

    return urls[:limit]


# Source mapping
YTDLP_SOURCES = {
    'youtube': lambda q, l, s: search_with_ytdlp(q, 'ytsearch', l, s),
    'reddit': lambda q, l, s: search_with_ytdlp(q, 'reddit', l, s),
    'imgur': lambda q, l, s: search_imgur(q, l),
    'pexels': lambda q, l, s: search_pexels(q, l),
    'pixabay': lambda q, l, s: search_pixabay(q, l),
}


def search_all_sources(query, sources=None, limit_per_source=10, safe_search=True):
    """
    Search multiple sources using yt-dlp

    Args:
        query: Search query
        sources: List of source names (or None for all)
        limit_per_source: Max results per source
        safe_search: Enable safe search (ignored for APIs)

    Returns:
        dict: {source_name: [urls]}
    """
    if sources is None:
        sources = list(YTDLP_SOURCES.keys())

    results = {}

    for source in sources:
        if source in YTDLP_SOURCES:
            try:
                urls = YTDLP_SOURCES[source](query, limit_per_source, safe_search)
                results[source] = urls
                logger.info(f"YT-DLP: {source} returned {len(urls)} URLs")
            except Exception as e:
                logger.error(f"YT-DLP: Error with {source}: {e}")
                results[source] = []
        else:
            logger.warning(f"YT-DLP: Unknown source '{source}'")
            results[source] = []

    return results


if __name__ == '__main__':
    # Test the scraper
    import time

    print("Testing yt-dlp scraper...")

    # Test YouTube search
    print("\n1. Testing YouTube search:")
    urls = search_with_ytdlp('cats', 'ytsearch', 3)
    for url in urls:
        print(f"  - {url}")

    # Test Imgur
    print("\n2. Testing Imgur:")
    urls = search_imgur('cats', 3)
    for url in urls:
        print(f"  - {url}")

    # Test all sources
    print("\n3. Testing all sources:")
    results = search_all_sources('dogs', ['youtube', 'imgur'], 2)
    for source, urls in results.items():
        print(f"  {source}: {len(urls)} results")
        for url in urls:
            print(f"    - {url}")

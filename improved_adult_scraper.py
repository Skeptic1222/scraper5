"""
Improved Multi-Method Adult Content Scraper
Features: Rate limiting, retries, robust error handling, multiple file downloads
"""

import os
import time
import logging
import subprocess
import random
from urllib.parse import quote, urljoin, urlparse
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

# Try importing curl_cffi for Cloudflare bypass
try:
    from curl_cffi import requests as cf_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    logger.warning("curl_cffi not available - install with: pip install curl_cffi")

logger = logging.getLogger('adult_scraper')
logger.setLevel(logging.INFO)

class ImprovedAdultScraper:
    """Enhanced adult video scraper with rate limiting and retries"""

    SITE_CONFIGS = {
        'pornhub': {
            'search_url': 'https://www.pornhub.com/video/search?search={query}',
            'video_selector': 'a[href*="viewkey"]',
            'video_url_attr': 'href',
            'base_url': 'https://www.pornhub.com',
            'age_cookie': {'name': 'age_verified', 'value': '1', 'domain': 'pornhub.com'},
            'rate_limit': (1, 3),  # min, max seconds between requests
        },
        'xvideos': {
            'search_url': 'https://www.xvideos.com/?k={query}',
            'video_selector': 'div.thumb a[href*="/video"]',
            'video_url_attr': 'href',
            'base_url': 'https://www.xvideos.com',
            'age_cookie': None,
            'rate_limit': (0.5, 2),
        },
        'redtube': {
            'search_url': 'https://www.redtube.com/?search={query}',
            'video_selector': 'a.video_link',
            'video_url_attr': 'href',
            'base_url': 'https://www.redtube.com',
            'age_cookie': None,
            'rate_limit': (1, 2),
        },
        'xhamster': {
            'search_url': 'https://xhamster.com/search/{query}',
            'video_selector': 'a.video-thumb__image-container',
            'video_url_attr': 'href',
            'base_url': 'https://xhamster.com',
            'age_cookie': None,
            'rate_limit': (1, 3),
        },
        'youporn': {
            'search_url': 'https://www.youporn.com/search/?query={query}',
            'video_selector': 'a[href*="/watch/"]',
            'video_url_attr': 'href',
            'base_url': 'https://www.youporn.com',
            'age_cookie': None,
            'rate_limit': (1, 2),
        },
        'spankbang': {
            'search_url': 'https://spankbang.com/s/{query}/',
            'video_selector': 'a[href*="/video/"]',
            'video_url_attr': 'href',
            'base_url': 'https://spankbang.com',
            'age_cookie': None,
            'rate_limit': (0.5, 2),
        },
        'motherless': {
            'search_url': 'https://motherless.com/search/videos?term={query}',
            'video_selector': 'a.img-container',
            'video_url_attr': 'href',
            'base_url': 'https://motherless.com',
            'age_cookie': None,
            'rate_limit': (1, 3),
        },
        'redgifs': {
            'search_url': 'https://www.redgifs.com/gifs/{query}',
            'video_selector': 'a[href*="/watch/"]',
            'video_url_attr': 'href',
            'base_url': 'https://www.redgifs.com',
            'age_cookie': None,
            'rate_limit': (0.5, 2),
        },
    }

    def __init__(self, output_dir='downloads'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.last_request_time = {}

    def _rate_limit(self, source: str, config: Dict):
        """Apply rate limiting with variable delays"""
        min_delay, max_delay = config.get('rate_limit', (1, 2))
        delay = random.uniform(min_delay, max_delay)

        if source in self.last_request_time:
            elapsed = time.time() - self.last_request_time[source]
            if elapsed < delay:
                sleep_time = delay - elapsed
                logger.debug(f"[{source}] Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)

        self.last_request_time[source] = time.time()

    def _retry_request(self, url: str, source: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with exponential backoff retries"""
        # Try curl_cffi first for Cloudflare-protected sources
        if CURL_CFFI_AVAILABLE and source in ['spankbang']:
            for attempt in range(max_retries):
                try:
                    logger.info(f"[{source}] Trying curl_cffi for Cloudflare bypass")
                    response = cf_requests.get(
                        url,
                        impersonate="chrome131",
                        headers=self.headers,
                        timeout=15
                    )
                    response.raise_for_status()
                    # Convert to requests.Response-like object
                    return response
                except Exception as e:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"[{source}] curl_cffi failed (attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)

        # Fallback to regular requests
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"[{source}] Request failed (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"[{source}] Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"[{source}] All retries exhausted")
                    return None
        return None

    def scrape(self, source: str, query: str, max_results: int = 10) -> List[str]:
        """Main scraping method with fallback strategies"""
        if source not in self.SITE_CONFIGS:
            logger.error(f"Unsupported source: {source}")
            return []

        config = self.SITE_CONFIGS[source]
        logger.info(f"[{source}] Starting scrape for '{query}' (max {max_results} files)")

        # Method 1: Extract URLs + yt-dlp
        try:
            logger.info(f"[{source}] Method 1: URL extraction + yt-dlp")
            video_urls = self._extract_video_urls(source, query, max_results, config)

            if video_urls:
                logger.info(f"[{source}] Found {len(video_urls)} video URLs")
                downloaded = self._download_with_ytdlp(source, video_urls, config, max_files=max_results)
                if downloaded:
                    logger.info(f"[{source}] Method 1 SUCCESS: {len(downloaded)} files")
                    return downloaded
        except Exception as e:
            logger.warning(f"[{source}] Method 1 failed: {e}")

        # Method 2: Selenium (if available)
        try:
            logger.info(f"[{source}] Method 2: Selenium extraction")
            downloaded = self._download_with_selenium(source, query, max_results, config)
            if downloaded:
                logger.info(f"[{source}] Method 2 SUCCESS: {len(downloaded)} files")
                return downloaded
        except Exception as e:
            logger.warning(f"[{source}] Method 2 failed: {e}")

        logger.error(f"[{source}] All methods exhausted - 0 downloads")
        return []

    def _extract_video_urls(self, source: str, query: str, max_results: int, config: Dict) -> List[str]:
        """Extract video URLs with proper cookie handling"""
        search_url = config['search_url'].format(query=quote(query))

        # Set age verification cookie with correct domain
        if config.get('age_cookie'):
            cookie = config['age_cookie']
            self.session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie['domain']
            )
            logger.debug(f"[{source}] Set cookie: {cookie['name']}={cookie['value']} for {cookie['domain']}")

        logger.info(f"[{source}] Fetching search results: {search_url}")

        # Apply rate limiting
        self._rate_limit(source, config)

        # Retry logic for search page
        response = self._retry_request(search_url, source)
        if not response:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        video_elements = soup.select(config['video_selector'])
        logger.info(f"[{source}] Found {len(video_elements)} video elements")

        video_urls = []
        for elem in video_elements[:max_results]:
            url = elem.get(config['video_url_attr'])
            if url:
                if not url.startswith('http'):
                    url = urljoin(config['base_url'], url)
                video_urls.append(url)

        logger.info(f"[{source}] Extracted {len(video_urls)} video URLs")
        return video_urls

    def _download_with_ytdlp(self, source: str, video_urls: List[str], config: Dict, max_files: int = None) -> List[str]:
        """Download videos with yt-dlp and rate limiting"""
        downloaded_files = []

        for idx, url in enumerate(video_urls):
            # Stop if we've reached the file limit
            if max_files and len(downloaded_files) >= max_files:
                logger.info(f"[{source}] Reached max file limit ({max_files}), stopping downloads")
                break

            try:
                logger.info(f"[{source}] Downloading video {idx+1}/{len(video_urls)}: {url}")

                # Apply rate limiting before each download
                self._rate_limit(source, config)

                # Track files before download
                files_before = set(os.listdir(self.output_dir))

                output_template = os.path.join(self.output_dir, f'{source}_%(title)s.%(ext)s')

                # Enhanced yt-dlp options for XHamster and other problematic sources
                cmd = [
                    'yt-dlp',
                    '--no-warnings',
                    '--quiet',
                    '--no-progress',
                    '--no-playlist',  # Don't download playlists
                    '--format', 'best[ext=mp4]/best',  # Download only best single format
                    '--user-agent', self.headers['User-Agent'],
                    '--referer', url,
                    '-o', output_template,
                ]

                # Add force-generic-extractor for XHamster (broken upstream extractor)
                if source == 'xhamster':
                    cmd.extend(['--force-generic-extractor', '--verbose'])
                    logger.info(f"[{source}] Using force-generic-extractor due to broken XHamster extractor")

                cmd.append(url)

                # Execute with timeout
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)

                if result.returncode == 0:
                    time.sleep(0.5)
                    files_after = set(os.listdir(self.output_dir))
                    new_files = files_after - files_before

                    if new_files:
                        for new_file in new_files:
                            full_path = os.path.join(self.output_dir, new_file)
                            downloaded_files.append(full_path)
                            logger.info(f"[{source}] Downloaded: {new_file}")
                    else:
                        logger.warning(f"[{source}] yt-dlp succeeded but no new file found")
                else:
                    logger.warning(f"[{source}] yt-dlp failed: {result.stderr[:200]}")

            except subprocess.TimeoutExpired:
                logger.warning(f"[{source}] yt-dlp timeout for {url}")
            except Exception as e:
                logger.warning(f"[{source}] Error downloading {url}: {e}")

        return downloaded_files

    def _download_with_selenium(self, source: str, query: str, max_results: int, config: Dict) -> List[str]:
        """Selenium fallback (not implemented - requires undetected-chromedriver)"""
        logger.warning(f"[{source}] Selenium method not available")
        return []


def download_adult_content_improved(source: str, query: str, max_results: int, output_dir: str) -> List[str]:
    """Improved drop-in replacement with rate limiting and retries"""
    scraper = ImprovedAdultScraper(output_dir=output_dir)
    return scraper.scrape(source, query, max_results)


if __name__ == '__main__':
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) < 3:
        print("Usage: python improved_adult_scraper.py <source> <query> [max_results]")
        print("Example: python improved_adult_scraper.py pornhub dance 5")
        sys.exit(1)

    source = sys.argv[1]
    query = sys.argv[2]
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    scraper = ImprovedAdultScraper()
    files = scraper.scrape(source, query, max_results)

    print(f"\n{'='*60}")
    print(f"Downloaded {len(files)} files:")
    for f in files:
        print(f"  - {os.path.basename(f)}")
    print(f"{'='*60}")

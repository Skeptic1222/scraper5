"""
Multi-Method Adult Content Scraper with Fallback Strategies
Implements comprehensive fallback system for reliable adult video downloads
"""

import os
import time
import logging
import subprocess
from urllib.parse import quote, urljoin
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup

# Configure logging
logger = logging.getLogger('adult_scraper')
logger.setLevel(logging.INFO)

class AdultVideoScraper:
    """
    Multi-method video scraper with intelligent fallbacks

    Methods (in priority order):
    1. yt-dlp with individual URLs (fastest, most reliable)
    2. Selenium with undetected-chromedriver (anti-bot bypass)
    3. Direct video URL extraction + requests download
    4. API-based extraction (where available)
    """

    # Site-specific configurations
    SITE_CONFIGS = {
        'pornhub': {
            'search_url': 'https://www.pornhub.com/video/search?search={query}',
            'video_selector': 'a[href*="viewkey"]',
            'video_url_attr': 'href',
            'base_url': 'https://www.pornhub.com',
            'age_cookie': {'name': 'age_verified', 'value': '1'},
        },
        'xvideos': {
            'search_url': 'https://www.xvideos.com/?k={query}',
            'video_selector': 'div.thumb a[href*="/video"]',
            'video_url_attr': 'href',
            'base_url': 'https://www.xvideos.com',
            'age_cookie': None,
        },
        'redtube': {
            'search_url': 'https://www.redtube.com/?search={query}',
            'video_selector': 'a.video_link',
            'video_url_attr': 'href',
            'base_url': 'https://www.redtube.com',
            'age_cookie': None,
        },
        'xhamster': {
            'search_url': 'https://xhamster.com/search/{query}',
            'video_selector': 'a.video-thumb__image-container',
            'video_url_attr': 'href',
            'base_url': 'https://xhamster.com',
            'age_cookie': None,
        },
        'youporn': {
            'search_url': 'https://www.youporn.com/search/?query={query}',
            'video_selector': 'a.video-box-title',
            'video_url_attr': 'href',
            'base_url': 'https://www.youporn.com',
            'age_cookie': None,
        },
        'spankbang': {
            'search_url': 'https://spankbang.com/s/{query}/',
            'video_selector': 'a.n',
            'video_url_attr': 'href',
            'base_url': 'https://spankbang.com',
            'age_cookie': None,
        },
        'motherless': {
            'search_url': 'https://motherless.com/search/videos?term={query}',
            'video_selector': 'a.thumb',
            'video_url_attr': 'href',
            'base_url': 'https://motherless.com',
            'age_cookie': None,
        },
        'redgifs': {
            'search_url': 'https://www.redgifs.com/gifs/{query}',
            'video_selector': 'a[href*="/watch/"]',
            'video_url_attr': 'href',
            'base_url': 'https://www.redgifs.com',
            'age_cookie': None,
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

    def scrape(self, source: str, query: str, max_results: int = 5) -> List[str]:
        """
        Main scraping method with fallback strategies

        Args:
            source: Source name (pornhub, xvideos, etc.)
            query: Search query
            max_results: Maximum number of videos to download

        Returns:
            List of downloaded file paths
        """
        if source not in self.SITE_CONFIGS:
            logger.error(f"Unsupported source: {source}")
            return []

        config = self.SITE_CONFIGS[source]
        logger.info(f"[{source}] Starting scrape for query: {query}")

        # Method 1: Extract individual URLs, then use yt-dlp
        try:
            logger.info(f"[{source}] Method 1: URL extraction + yt-dlp")
            video_urls = self._extract_video_urls(source, query, max_results, config)

            if video_urls:
                logger.info(f"[{source}] Found {len(video_urls)} video URLs")
                downloaded = self._download_with_ytdlp_individual(source, video_urls)
                if downloaded:
                    logger.info(f"[{source}] ✅ Method 1 SUCCESS: {len(downloaded)} files")
                    return downloaded
        except Exception as e:
            logger.warning(f"[{source}] Method 1 failed: {e}")

        # Method 2: Try Selenium extraction (if available)
        try:
            logger.info(f"[{source}] Method 2: Selenium extraction")
            downloaded = self._download_with_selenium(source, query, max_results, config)
            if downloaded:
                logger.info(f"[{source}] ✅ Method 2 SUCCESS: {len(downloaded)} files")
                return downloaded
        except Exception as e:
            logger.warning(f"[{source}] Method 2 failed: {e}")

        # Method 3: Direct video element extraction
        try:
            logger.info(f"[{source}] Method 3: Direct video extraction")
            downloaded = self._download_direct_extraction(source, query, max_results, config)
            if downloaded:
                logger.info(f"[{source}] ✅ Method 3 SUCCESS: {len(downloaded)} files")
                return downloaded
        except Exception as e:
            logger.warning(f"[{source}] Method 3 failed: {e}")

        logger.error(f"[{source}] ❌ All methods exhausted - 0 downloads")
        return []

    def _extract_video_urls(self, source: str, query: str, max_results: int, config: Dict) -> List[str]:
        """Extract individual video URLs from search results using BeautifulSoup"""
        search_url = config['search_url'].format(query=quote(query))

        # Add age verification cookie if needed
        if config['age_cookie']:
            self.session.cookies.set(
                config['age_cookie']['name'],
                config['age_cookie']['value'],
                domain=config['base_url'].replace('https://', '').replace('www.', '')
            )

        logger.info(f"[{source}] Fetching search results: {search_url}")

        try:
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"[{source}] Failed to fetch search page: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract video links using site-specific selector
        video_elements = soup.select(config['video_selector'])
        logger.info(f"[{source}] Found {len(video_elements)} video elements")

        video_urls = []
        for elem in video_elements[:max_results]:
            url = elem.get(config['video_url_attr'])
            if url:
                # Convert relative URLs to absolute
                if not url.startswith('http'):
                    url = urljoin(config['base_url'], url)
                video_urls.append(url)

        logger.info(f"[{source}] Extracted {len(video_urls)} video URLs")
        return video_urls

    def _download_with_ytdlp_individual(self, source: str, video_urls: List[str]) -> List[str]:
        """Download individual videos using yt-dlp"""
        downloaded_files = []

        for idx, url in enumerate(video_urls):
            try:
                logger.info(f"[{source}] Downloading video {idx+1}/{len(video_urls)}: {url}")

                # Build yt-dlp command
                output_template = os.path.join(self.output_dir, f'{source}_%(title)s.%(ext)s')

                cmd = [
                    'yt-dlp',
                    '--no-warnings',
                    '--quiet',
                    '--no-progress',
                    '--cookies-from-browser', 'firefox',
                    '--user-agent', self.headers['User-Agent'],
                    '--referer', url,
                    '-o', output_template,
                    url
                ]

                # Execute yt-dlp
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    # Find the downloaded file
                    files_before = set(os.listdir(self.output_dir))
                    time.sleep(0.5)  # Small delay to ensure file is written
                    files_after = set(os.listdir(self.output_dir))
                    new_files = files_after - files_before

                    if new_files:
                        downloaded_file = list(new_files)[0]
                        full_path = os.path.join(self.output_dir, downloaded_file)
                        downloaded_files.append(full_path)
                        logger.info(f"[{source}] ✅ Downloaded: {downloaded_file}")
                    else:
                        logger.warning(f"[{source}] yt-dlp succeeded but no new file found")
                else:
                    logger.warning(f"[{source}] yt-dlp failed: {result.stderr}")

            except subprocess.TimeoutExpired:
                logger.warning(f"[{source}] yt-dlp timeout for {url}")
            except Exception as e:
                logger.warning(f"[{source}] Error downloading {url}: {e}")

        return downloaded_files

    def _download_with_selenium(self, source: str, query: str, max_results: int, config: Dict) -> List[str]:
        """Download using Selenium with undetected-chromedriver (if installed)"""
        try:
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            logger.warning(f"[{source}] Selenium not available - install undetected-chromedriver")
            return []

        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')

        driver = None
        downloaded_files = []

        try:
            driver = uc.Chrome(options=options, use_subprocess=True)
            search_url = config['search_url'].format(query=quote(query))

            driver.get(search_url)
            time.sleep(3)  # Wait for page load

            # Extract video URLs
            video_elements = driver.find_elements(By.CSS_SELECTOR, config['video_selector'])
            video_urls = []

            for elem in video_elements[:max_results]:
                url = elem.get_attribute(config['video_url_attr'])
                if url and url.startswith('http'):
                    video_urls.append(url)

            logger.info(f"[{source}] Selenium found {len(video_urls)} video URLs")

            # Download each video
            for url in video_urls:
                try:
                    driver.get(url)
                    time.sleep(2)

                    # Extract direct video URL
                    video_element = driver.find_element(By.TAG_NAME, 'video')
                    video_src = video_element.get_attribute('src') or video_element.get_property('currentSrc')

                    if video_src:
                        # Download with session cookies
                        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
                        response = self.session.get(
                            video_src,
                            headers={'Referer': url},
                            cookies=cookies,
                            stream=True,
                            timeout=30
                        )

                        if response.status_code == 200:
                            filename = f"{source}_{int(time.time())}.mp4"
                            filepath = os.path.join(self.output_dir, filename)

                            with open(filepath, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)

                            downloaded_files.append(filepath)
                            logger.info(f"[{source}] ✅ Selenium downloaded: {filename}")
                except Exception as e:
                    logger.warning(f"[{source}] Selenium error for {url}: {e}")

        finally:
            if driver:
                driver.quit()

        return downloaded_files

    def _download_direct_extraction(self, source: str, query: str, max_results: int, config: Dict) -> List[str]:
        """Direct extraction using requests + BeautifulSoup for video elements"""
        search_url = config['search_url'].format(query=quote(query))
        downloaded_files = []

        try:
            # Get search results
            response = self.session.get(search_url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract video page URLs
            video_elements = soup.select(config['video_selector'])[:max_results]

            for elem in video_elements:
                video_page_url = elem.get(config['video_url_attr'])
                if not video_page_url:
                    continue

                if not video_page_url.startswith('http'):
                    video_page_url = urljoin(config['base_url'], video_page_url)

                # Visit video page
                try:
                    video_response = self.session.get(video_page_url, timeout=15)
                    video_soup = BeautifulSoup(video_response.text, 'html.parser')

                    # Find video element
                    video_tag = video_soup.find('video')
                    if video_tag:
                        video_src = video_tag.get('src')
                        if not video_src:
                            source_tag = video_tag.find('source')
                            if source_tag:
                                video_src = source_tag.get('src')

                        if video_src:
                            if not video_src.startswith('http'):
                                video_src = urljoin(config['base_url'], video_src)

                            # Download video
                            video_data = self.session.get(
                                video_src,
                                headers={'Referer': video_page_url},
                                stream=True,
                                timeout=30
                            )

                            if video_data.status_code == 200:
                                filename = f"{source}_{int(time.time())}.mp4"
                                filepath = os.path.join(self.output_dir, filename)

                                with open(filepath, 'wb') as f:
                                    for chunk in video_data.iter_content(chunk_size=8192):
                                        if chunk:
                                            f.write(chunk)

                                downloaded_files.append(filepath)
                                logger.info(f"[{source}] ✅ Direct download: {filename}")

                except Exception as e:
                    logger.warning(f"[{source}] Direct extraction error: {e}")

        except Exception as e:
            logger.error(f"[{source}] Direct extraction failed: {e}")

        return downloaded_files


# Integration function for existing system
def download_adult_content_multi_method(source: str, query: str, max_results: int, output_dir: str) -> List[str]:
    """
    Drop-in replacement for existing adult content downloaders

    Args:
        source: Source name (pornhub, xvideos, etc.)
        query: Search query
        max_results: Maximum number of results
        output_dir: Output directory path

    Returns:
        List of downloaded file paths
    """
    scraper = AdultVideoScraper(output_dir=output_dir)
    return scraper.scrape(source, query, max_results)


if __name__ == '__main__':
    # Test the scraper
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if len(sys.argv) < 3:
        print("Usage: python multi_method_adult_scraper.py <source> <query> [max_results]")
        print("Example: python multi_method_adult_scraper.py pornhub dancing 3")
        sys.exit(1)

    source = sys.argv[1]
    query = sys.argv[2]
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    scraper = AdultVideoScraper()
    files = scraper.scrape(source, query, max_results)

    print(f"\n{'='*60}")
    print(f"Downloaded {len(files)} files:")
    for f in files:
        print(f"  - {f}")
    print(f"{'='*60}")

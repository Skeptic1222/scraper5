"""
Concrete implementations of scraping methods

Each class implements a specific scraping technique that can be
registered with the multi-method framework
"""

import os
import subprocess
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from typing import Dict, List, Any
import logging

from multi_method_framework import ScrapingMethod, MethodType, MethodResult

logger = logging.getLogger('scraping_methods')

# ==============================================
# METHOD 1: YT-DLP (Best for video platforms)
# ==============================================
class YtDlpMethod(ScrapingMethod):
    """Use yt-dlp to download videos - works for 1000+ sites"""

    def __init__(self):
        super().__init__(name="yt-dlp", method_type=MethodType.YT_DLP, priority=10)  # High priority

    def can_handle(self, source: str, content_type: str) -> bool:
        # yt-dlp is primarily for videos
        if content_type == 'images':
            return False

        # yt-dlp supports hundreds of sites
        supported_sites = [
            'youtube', 'vimeo', 'dailymotion', 'twitch', 'pornhub', 'xvideos',
            'redtube', 'youporn', 'xhamster', 'spankbang', 'redgifs', 'instagram',
            'twitter', 'reddit', 'tiktok', 'facebook', 'soundcloud', 'bandcamp'
        ]
        return any(site in source.lower() for site in supported_sites)

    def execute(self, source: str, query: str, max_results: int, **kwargs) -> MethodResult:
        output_dir = kwargs.get('output_dir', 'downloads')
        urls = kwargs.get('urls', [])  # Pre-extracted URLs if available

        if not urls:
            logger.warning(f"[{source}] yt-dlp: No URLs provided, cannot proceed")
            return MethodResult(
                success=False,
                method=self.name,
                files_downloaded=0,
                files=[],
                error="No URLs provided for yt-dlp"
            )

        downloaded_files = []
        max_retries = 3  # Retry up to 3 times

        for url in urls[:max_results]:
            downloaded = False

            for attempt in range(max_retries):
                try:
                    output_template = os.path.join(output_dir, f'{source}_%(title)s.%(ext)s')

                    cmd = [
                        'yt-dlp',
                        '--no-warnings',
                        '--quiet',
                        '--no-check-certificate',
                        '--prefer-free-formats',
                        '-f', 'best',
                        '--max-filesize', '500M',  # Skip very large files
                        '-o', output_template,
                        url
                    ]

                    if attempt > 0:
                        logger.info(f"[{source}] yt-dlp: Retry {attempt}/{max_retries-1} for {url}")
                    else:
                        logger.info(f"[{source}] yt-dlp: Downloading {url}")

                    # Increase timeout on retries
                    timeout = 120 + (60 * attempt)  # 120s, 180s, 240s

                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

                    if result.returncode == 0:
                        # Find newly created files
                        files_after = set(os.listdir(output_dir))
                        # Look for files matching our pattern
                        new_files = [f for f in files_after if f.startswith(f'{source}_')]

                        if new_files:
                            for new_file in new_files:
                                filepath = os.path.join(output_dir, new_file)
                                if os.path.getmtime(filepath) > time.time() - (timeout + 10):  # Created recently
                                    downloaded_files.append({
                                        'filepath': filepath,
                                        'source': source,
                                        'original_url': url,
                                        'method': self.name
                                    })
                            logger.info(f"[{source}] yt-dlp: ✅ Downloaded {len(new_files)} file(s)")
                            downloaded = True
                            break  # Success, exit retry loop
                        else:
                            logger.warning(f"[{source}] yt-dlp: Completed but no new file found")
                    else:
                        # Check if it's a transient error worth retrying
                        stderr_lower = result.stderr.lower()
                        retryable_errors = ['timeout', 'connection', 'network', 'temporary', 'unavailable']

                        if any(err in stderr_lower for err in retryable_errors) and attempt < max_retries - 1:
                            retry_delay = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                            logger.warning(f"[{source}] yt-dlp: Retryable error, waiting {retry_delay}s - {result.stderr[:150]}")
                            time.sleep(retry_delay)
                            continue  # Try again
                        else:
                            logger.warning(f"[{source}] yt-dlp: Failed - {result.stderr[:200]}")
                            break  # Non-retryable error

                except subprocess.TimeoutExpired:
                    if attempt < max_retries - 1:
                        retry_delay = 2 ** attempt
                        logger.warning(f"[{source}] yt-dlp: Timeout, retrying in {retry_delay}s (attempt {attempt+1}/{max_retries})")
                        time.sleep(retry_delay)
                    else:
                        logger.warning(f"[{source}] yt-dlp: Timeout downloading {url} after {max_retries} attempts")
                        break

                except Exception as e:
                    if attempt < max_retries - 1:
                        retry_delay = 2 ** attempt
                        logger.warning(f"[{source}] yt-dlp: Error (retrying in {retry_delay}s) - {e}")
                        time.sleep(retry_delay)
                    else:
                        logger.warning(f"[{source}] yt-dlp: Error after {max_retries} attempts - {e}")
                        break

        success = len(downloaded_files) > 0
        return MethodResult(
            success=success,
            method=self.name,
            files_downloaded=len(downloaded_files),
            files=downloaded_files,
            error=None if success else "No files downloaded"
        )

# ==============================================
# METHOD 2: GALLERY-DL (Best for image galleries)
# ==============================================
class GalleryDlMethod(ScrapingMethod):
    """Use gallery-dl to download image galleries"""

    def __init__(self):
        super().__init__(name="gallery-dl", method_type=MethodType.GALLERY_DL, priority=15)

    def can_handle(self, source: str, content_type: str) -> bool:
        if content_type == 'videos':
            return False

        # gallery-dl supports many image platforms
        supported = [
            'imgur', 'flickr', 'instagram', 'twitter', 'reddit', 'deviantart',
            'artstation', 'pixiv', 'danbooru', 'gelbooru', 'tumblr', 'pinterest'
        ]
        return any(site in source.lower() for site in supported)

    def execute(self, source: str, query: str, max_results: int, **kwargs) -> MethodResult:
        output_dir = kwargs.get('output_dir', 'downloads')
        urls = kwargs.get('urls', [])

        if not urls:
            return MethodResult(
                success=False,
                method=self.name,
                files_downloaded=0,
                files=[],
                error="No URLs provided"
            )

        downloaded_files = []

        for url in urls[:max_results]:
            try:
                # Create source-specific subdirectory
                source_dir = os.path.join(output_dir, source)
                os.makedirs(source_dir, exist_ok=True)

                cmd = [
                    'gallery-dl',
                    '--quiet',
                    '--no-check-certificate',
                    '--dest', source_dir,
                    url
                ]

                logger.info(f"[{source}] gallery-dl: Downloading {url}")

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)

                if result.returncode == 0:
                    # Find new files
                    for root, dirs, files in os.walk(source_dir):
                        for filename in files:
                            filepath = os.path.join(root, filename)
                            # Check if file was just created
                            if os.path.getmtime(filepath) > time.time() - 95:
                                downloaded_files.append({
                                    'filepath': filepath,
                                    'source': source,
                                    'original_url': url,
                                    'method': self.name
                                })

                    logger.info(f"[{source}] gallery-dl: ✅ Downloaded files")
                else:
                    logger.warning(f"[{source}] gallery-dl: Failed - {result.stderr[:200]}")

            except subprocess.TimeoutExpired:
                logger.warning(f"[{source}] gallery-dl: Timeout")
            except Exception as e:
                logger.warning(f"[{source}] gallery-dl: Error - {e}")

        success = len(downloaded_files) > 0
        return MethodResult(
            success=success,
            method=self.name,
            files_downloaded=len(downloaded_files),
            files=downloaded_files,
            error=None if success else "No files downloaded"
        )

# ==============================================
# METHOD 3: REQUESTS + BEAUTIFULSOUP (Universal)
# ==============================================
class RequestsBeautifulSoupMethod(ScrapingMethod):
    """Traditional web scraping with requests and BeautifulSoup"""

    def __init__(self):
        super().__init__(name="requests_bs4", method_type=MethodType.REQUESTS_BS4, priority=30)

    def can_handle(self, source: str, content_type: str) -> bool:
        # This is a universal fallback method
        return True

    def execute(self, source: str, query: str, max_results: int, **kwargs) -> MethodResult:
        output_dir = kwargs.get('output_dir', 'downloads')
        search_config = kwargs.get('search_config', {})

        if not search_config:
            return MethodResult(
                success=False,
                method=self.name,
                files_downloaded=0,
                files=[],
                error="No search configuration provided"
            )

        downloaded_files = []

        try:
            # Build search URL
            search_url = search_config.get('search_url', '').format(query=quote(query))
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            logger.info(f"[{source}] requests_bs4: Fetching {search_url}")

            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract media URLs based on config
            img_selector = search_config.get('image_selector', 'img')
            images = soup.select(img_selector)

            for img in images[:max_results]:
                img_url = img.get('src') or img.get('data-src')
                if img_url:
                    if not img_url.startswith('http'):
                        img_url = urljoin(search_url, img_url)

                    # Download image
                    try:
                        img_response = requests.get(img_url, headers=headers, timeout=10)
                        img_response.raise_for_status()

                        # Generate filename
                        ext = img_url.split('.')[-1][:4]  # Get extension
                        filename = f"{source}_{len(downloaded_files)}.{ext}"
                        filepath = os.path.join(output_dir, filename)

                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)

                        downloaded_files.append({
                            'filepath': filepath,
                            'source': source,
                            'original_url': img_url,
                            'method': self.name
                        })

                        logger.info(f"[{source}] requests_bs4: Downloaded {filename}")

                    except Exception as e:
                        logger.warning(f"[{source}] requests_bs4: Failed to download image - {e}")

        except Exception as e:
            logger.error(f"[{source}] requests_bs4: Error - {e}")
            return MethodResult(
                success=False,
                method=self.name,
                files_downloaded=0,
                files=[],
                error=str(e)
            )

        success = len(downloaded_files) > 0
        return MethodResult(
            success=success,
            method=self.name,
            files_downloaded=len(downloaded_files),
            files=downloaded_files,
            error=None if success else "No files downloaded"
        )

# ==============================================
# METHOD 4: CURL_CFFI (Cloudflare Bypass)
# ==============================================
class CurlCffiMethod(ScrapingMethod):
    """Use curl_cffi to bypass Cloudflare protection"""

    def __init__(self):
        super().__init__(name="curl_cffi", method_type=MethodType.CURL_CFFI, priority=20)

    def can_handle(self, source: str, content_type: str) -> bool:
        # Use for sites known to have Cloudflare
        cloudflare_sites = ['imgur', 'reddit', 'twitter', 'pornhub', 'xvideos']
        return any(site in source.lower() for site in cloudflare_sites)

    def execute(self, source: str, query: str, max_results: int, **kwargs) -> MethodResult:
        try:
            from curl_cffi import requests as cf_requests
        except ImportError:
            return MethodResult(
                success=False,
                method=self.name,
                files_downloaded=0,
                files=[],
                error="curl_cffi not installed"
            )

        output_dir = kwargs.get('output_dir', 'downloads')
        search_config = kwargs.get('search_config', {})

        if not search_config:
            return MethodResult(
                success=False,
                method=self.name,
                files_downloaded=0,
                files=[],
                error="No search configuration"
            )

        downloaded_files = []

        try:
            search_url = search_config.get('search_url', '').format(query=quote(query))

            logger.info(f"[{source}] curl_cffi: Fetching {search_url}")

            # Use curl_cffi to bypass Cloudflare
            response = cf_requests.get(search_url, impersonate="chrome110", timeout=15)

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract images
            img_selector = search_config.get('image_selector', 'img')
            images = soup.select(img_selector)

            for img in images[:max_results]:
                img_url = img.get('src') or img.get('data-src')
                if img_url and img_url.startswith('http'):
                    try:
                        img_response = cf_requests.get(img_url, impersonate="chrome110", timeout=10)

                        ext = img_url.split('.')[-1][:4]
                        filename = f"{source}_{len(downloaded_files)}.{ext}"
                        filepath = os.path.join(output_dir, filename)

                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)

                        downloaded_files.append({
                            'filepath': filepath,
                            'source': source,
                            'original_url': img_url,
                            'method': self.name
                        })

                        logger.info(f"[{source}] curl_cffi: Downloaded {filename}")

                    except Exception as e:
                        logger.warning(f"[{source}] curl_cffi: Failed - {e}")

        except Exception as e:
            logger.error(f"[{source}] curl_cffi: Error - {e}")
            return MethodResult(
                success=False,
                method=self.name,
                files_downloaded=0,
                files=[],
                error=str(e)
            )

        success = len(downloaded_files) > 0
        return MethodResult(
            success=success,
            method=self.name,
            files_downloaded=len(downloaded_files),
            files=downloaded_files,
            error=None if success else "No files downloaded"
        )

# ==============================================
# REGISTER ALL METHODS WITH GLOBAL REGISTRY
# ==============================================
def register_all_methods(registry):
    """Register all available scraping methods"""
    methods = [
        YtDlpMethod(),
        GalleryDlMethod(),
        RequestsBeautifulSoupMethod(),
        CurlCffiMethod(),
    ]

    for method in methods:
        registry.register(method)

    logger.info(f"Registered {len(methods)} scraping methods")

"""
Google Images Scraper - Downloads images from Google Image Search
"""
import json
import logging
import re
from typing import Callable, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from .base import BaseScraper, MediaItem, MediaType, ScraperCategory, ScraperMethod

logger = logging.getLogger(__name__)


class GoogleScraper(BaseScraper):
    """Google Images search and download scraper"""

    NAME = "Google Images"
    CATEGORY = ScraperCategory.SEARCH
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.GIF]
    BASE_URL = "https://www.google.com"
    RATE_LIMIT = 60

    def __init__(self):
        super().__init__()
        self.search_url = f"{self.BASE_URL}/search"
        self.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def _setup_methods(self):
        """Setup Google-specific scraping methods"""
        self.methods = [
            ScraperMethod(
                name="google_json_extraction",
                function=self._search_via_json,
                priority=100
            ),
            ScraperMethod(
                name="google_web_scrape",
                function=self._search_via_web_scrape,
                priority=90
            ),
            ScraperMethod(
                name="google_api_emulation",
                function=self._search_via_api_emulation,
                priority=80
            )
        ]

    async def search(self, query: str, max_results: int = 20,
                    safe_search: bool = True, media_type: Optional[MediaType] = None,
                    progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """Search Google Images for content"""
        results = []

        # Build search parameters
        params = {
            'q': query,
            'tbm': 'isch',  # Image search
            'hl': 'en',
            'gl': 'us',
            'num': max_results
        }

        # Add safe search
        if safe_search:
            params['safe'] = 'active'
        else:
            params['safe'] = 'off'

        # Add filters for specific media types
        tbs_filters = []
        if media_type == MediaType.GIF:
            tbs_filters.append('itp:animated')
        elif media_type == MediaType.IMAGE:
            tbs_filters.append('itp:photo')

        # Add quality filters
        tbs_filters.append('isz:l')  # Large images

        if tbs_filters:
            params['tbs'] = ','.join(tbs_filters)

        try:
            # Try JSON extraction first (most reliable)
            results = await self._search_via_json(query, params, max_results, progress_callback)

            # Fallback to web scraping
            if not results:
                results = await self._search_via_web_scrape(query, params, max_results, progress_callback)

        except Exception as e:
            logger.error(f"Google search error: {e}")

        return results[:max_results]

    async def download(self, url: str, output_path: str,
                      quality: str = "best",
                      progress_callback: Optional[Callable] = None) -> bool:
        """Download image from URL"""
        try:
            return await self._download_image(url, output_path, progress_callback)
        except Exception as e:
            logger.error(f"Google download error: {e}")
            return False

    def validate_url(self, url: str) -> bool:
        """Check if URL is from Google or is an image URL"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        return any(url.lower().endswith(ext) for ext in image_extensions) or 'google.com' in url

    async def _search_via_json(self, query: str, params: dict, max_results: int,
                               progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """Extract images from Google's JSON data embedded in the page"""
        results = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.search_url, params=params, headers=self.headers) as response:
                    if response.status != 200:
                        return results

                    html = await response.text()

                    # Extract JSON data from script tags
                    # Google embeds image data in various formats
                    patterns = [
                        r'AF_initDataCallback\({[^<]+key:\s*\'ds:1\'[^<]+data:([\s\S]*?), sideChannel:',
                        r'AF_initDataCallback\({[^<]+key:\s*\'ds:2\'[^<]+data:([\s\S]*?), sideChannel:',
                        r'\[\"ds.udreview\".*?\"({.*?})\"\]'
                    ]

                    for pattern in patterns:
                        matches = re.findall(pattern, html)
                        for match in matches:
                            try:
                                # Clean and parse JSON
                                json_str = match.strip()
                                if json_str.startswith('function'):
                                    continue

                                # Google's JSON often needs cleaning
                                json_str = re.sub(r',\s*}', '}', json_str)
                                json_str = re.sub(r',\s*\]', ']', json_str)

                                data = json.loads(json_str)
                                images = self._extract_images_from_json(data)

                                for idx, img in enumerate(images[:max_results]):
                                    if progress_callback:
                                        progress_callback(f"Processing Google result {idx+1}/{len(images)}")

                                    if img:
                                        results.append(img)

                            except (json.JSONDecodeError, TypeError):
                                continue

                    # Alternative: Look for base64 encoded JSON
                    b64_pattern = r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)'
                    b64_matches = re.findall(b64_pattern, html)

                    # Also extract direct image URLs from the page
                    img_pattern = r'\["(https?://[^"]+\.(?:jpg|jpeg|png|gif|webp))"'
                    img_matches = re.findall(img_pattern, html)

                    for img_url in img_matches[:max_results - len(results)]:
                        results.append(MediaItem(
                            url=img_url,
                            title="Google Image",
                            media_type=MediaType.IMAGE,
                            source=self.NAME,
                            thumbnail=img_url
                        ))

        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")

        return results

    async def _search_via_web_scrape(self, query: str, params: dict, max_results: int,
                                     progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """Search by scraping the web page"""
        results = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.search_url, params=params, headers=self.headers) as response:
                    if response.status != 200:
                        return results

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Find image containers
                    # Google uses various class names that change frequently
                    image_containers = soup.find_all('div', {'data-ved': True})

                    for idx, container in enumerate(image_containers[:max_results]):
                        if progress_callback:
                            progress_callback(f"Processing Google result {idx+1}/{len(image_containers)}")

                        # Look for image data
                        img_tag = container.find('img')
                        if img_tag:
                            # Extract image URL from various attributes
                            img_url = (img_tag.get('data-src') or
                                      img_tag.get('data-iurl') or
                                      img_tag.get('src'))

                            if img_url and not img_url.startswith('data:'):
                                results.append(MediaItem(
                                    url=img_url,
                                    title=img_tag.get('alt', 'Google Image'),
                                    media_type=MediaType.IMAGE,
                                    source=self.NAME,
                                    thumbnail=img_tag.get('src')
                                ))

                        # Look for metadata
                        meta_div = container.find('div', {'data-item-id': True})
                        if meta_div:
                            try:
                                meta_data = json.loads(meta_div.get('data-item', '{}'))
                                media_item = self._create_media_item_from_meta(meta_data)
                                if media_item:
                                    results.append(media_item)
                            except:
                                continue

        except Exception as e:
            logger.error(f"Web scrape failed: {e}")

        return results

    async def _search_via_api_emulation(self, query: str, params: dict, max_results: int,
                                        progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """Emulate Google's internal API calls"""
        results = []

        try:
            # Google's internal image API endpoint
            api_url = f"{self.BASE_URL}/async/imgrc"

            # Build API parameters
            api_params = {
                '_reqid': '123456',
                'rt': 'c',
                'q': query,
                'safe': params.get('safe', 'off'),
                'tbm': 'isch',
                'start': 0,
                'ijn': 0,
                'async': f'_id:rg_s,_pms:s,_fmt:pc'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=api_params, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()

                        # Extract images from API response
                        soup = BeautifulSoup(html, 'html.parser')

                        # Look for image data
                        scripts = soup.find_all('script')
                        for script in scripts:
                            if script.string and 'AF_initDataCallback' in script.string:
                                # Extract and parse data
                                pass

        except Exception as e:
            logger.error(f"API emulation failed: {e}")

        return results

    def _extract_images_from_json(self, data: any) -> List[MediaItem]:
        """Recursively extract image URLs from nested JSON data"""
        results = []

        if isinstance(data, dict):
            # Check for image URL keys
            if 'ou' in data or 'url' in data:
                img_url = data.get('ou') or data.get('url')
                if img_url and isinstance(img_url, str) and img_url.startswith('http'):
                    results.append(MediaItem(
                        url=img_url,
                        title=data.get('pt', '') or data.get('title', 'Google Image'),
                        media_type=MediaType.IMAGE,
                        source=self.NAME,
                        thumbnail=data.get('tu') or data.get('thumbnail'),
                        metadata={
                            'width': data.get('ow') or data.get('width'),
                            'height': data.get('oh') or data.get('height'),
                            'site': data.get('st') or data.get('site'),
                            'source_url': data.get('ru') or data.get('referrer_url')
                        }
                    ))

            # Recurse through dict values
            for value in data.values():
                results.extend(self._extract_images_from_json(value))

        elif isinstance(data, list):
            # Recurse through list items
            for item in data:
                results.extend(self._extract_images_from_json(item))

        return results

    def _create_media_item_from_meta(self, data: dict) -> Optional[MediaItem]:
        """Create MediaItem from metadata"""
        try:
            return MediaItem(
                url=data.get('url'),
                title=data.get('title', 'Google Image'),
                media_type=MediaType.IMAGE,
                source=self.NAME,
                thumbnail=data.get('thumbnail'),
                description=data.get('description'),
                metadata={
                    'width': data.get('width'),
                    'height': data.get('height'),
                    'source': data.get('source')
                }
            )
        except:
            return None

    async def _download_image(self, url: str, output_path: str,
                             progress_callback: Optional[Callable] = None) -> bool:
        """Download image from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                # Add referer header
                download_headers = {
                    **self.headers,
                    'Referer': 'https://www.google.com/'
                }

                async with session.get(url, headers=download_headers, allow_redirects=True) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded = 0

                        with open(output_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                                downloaded += len(chunk)

                                if progress_callback and total_size:
                                    percent = (downloaded / total_size) * 100
                                    progress_callback(f"Downloading: {percent:.1f}%")

                        return True
                    else:
                        logger.error(f"Download failed with status {response.status}")

        except Exception as e:
            logger.error(f"Image download failed: {e}")

        return False

    def get_filter_options(self) -> dict:
        """Get available filter options for Google Images"""
        return {
            'size': ['icon', 'medium', 'large', 'exactly'],
            'color': ['color', 'gray', 'transparent', 'red', 'orange', 'yellow', 'green', 'teal', 'blue', 'purple', 'pink', 'white', 'black', 'brown'],
            'type': ['face', 'photo', 'clipart', 'lineart', 'animated'],
            'time': ['day', 'week', 'month', 'year'],
            'usage_rights': ['labeled_for_reuse_with_modifications', 'labeled_for_reuse',
                           'labeled_for_noncommercial_reuse_with_modification',
                           'labeled_for_nocommercial_reuse'],
            'aspect_ratio': ['tall', 'square', 'wide', 'panoramic']
        }

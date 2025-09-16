"""
Bing Images Scraper - Downloads images from Bing Image Search
"""
import json
import logging
import re
from typing import Callable, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from .base import BaseScraper, MediaItem, MediaType, ScraperCategory, ScraperMethod

logger = logging.getLogger(__name__)


class BingScraper(BaseScraper):
    """Bing Images search and download scraper"""

    NAME = "Bing Images"
    CATEGORY = ScraperCategory.SEARCH
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.GIF]
    BASE_URL = "https://www.bing.com"
    RATE_LIMIT = 60

    def __init__(self):
        super().__init__()
        self.search_url = f"{self.BASE_URL}/images/search"
        self.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def _setup_methods(self):
        """Setup Bing-specific scraping methods"""
        self.methods = [
            ScraperMethod(
                name="bing_api_search",
                function=self._search_via_api,
                priority=100
            ),
            ScraperMethod(
                name="bing_web_scrape",
                function=self._search_via_web_scrape,
                priority=90
            ),
            ScraperMethod(
                name="bing_async_api",
                function=self._search_via_async_api,
                priority=80
            )
        ]

    async def search(self, query: str, max_results: int = 20,
                    safe_search: bool = True, media_type: Optional[MediaType] = None,
                    progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """Search Bing Images for content"""
        results = []

        # Build search parameters
        params = {
            'q': query,
            'first': 1,
            'count': max_results,
            'adlt': 'moderate' if safe_search else 'off',
            'qft': ''
        }

        # Add filters for specific media types
        filters = []
        if media_type == MediaType.GIF:
            filters.append('filterui:photo-animatedgif')
        elif media_type == MediaType.IMAGE:
            filters.append('filterui:photo-photo')

        # Add size and quality filters
        filters.append('filterui:imagesize-large')
        filters.append('filterui:license-L2_L3_L4_L5_L6_L7')  # Free to use licenses

        if filters:
            params['qft'] = '+' + '+'.join(filters)

        try:
            # Try API search first
            results = await self._search_via_api(query, params, max_results, progress_callback)

            # Fallback to web scraping if API fails
            if not results:
                results = await self._search_via_web_scrape(query, params, max_results, progress_callback)

        except Exception as e:
            logger.error(f"Bing search error: {e}")

        return results[:max_results]

    async def download(self, url: str, output_path: str,
                      quality: str = "best",
                      progress_callback: Optional[Callable] = None) -> bool:
        """Download image from URL"""
        try:
            return await self._download_image(url, output_path, progress_callback)
        except Exception as e:
            logger.error(f"Bing download error: {e}")
            return False

    def validate_url(self, url: str) -> bool:
        """Check if URL is from Bing or is an image URL"""
        # Accept any image URL, not just Bing
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        return any(url.lower().endswith(ext) for ext in image_extensions) or 'bing.com' in url

    async def _search_via_api(self, query: str, params: dict, max_results: int,
                             progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """Search using Bing's internal API endpoints"""
        results = []

        try:
            async with aiohttp.ClientSession() as session:
                # First, get the search page to extract API tokens
                async with session.get(self.search_url, params={'q': query}, headers=self.headers) as response:
                    if response.status != 200:
                        return results

                    html = await response.text()

                    # Extract image data from JavaScript
                    pattern = r'var m = ({.+?});'
                    matches = re.findall(pattern, html)

                    if matches:
                        try:
                            data = json.loads(matches[0])
                            images = data.get('images', [])

                            for idx, img in enumerate(images[:max_results]):
                                if progress_callback:
                                    progress_callback(f"Processing Bing result {idx+1}/{len(images)}")

                                media_item = self._create_media_item_from_api(img)
                                if media_item:
                                    results.append(media_item)

                        except json.JSONDecodeError:
                            pass

                    # Also try to extract from inline JSON
                    json_pattern = r'<a class="iusc" href="#" m=\'({.+?})\''
                    json_matches = re.findall(json_pattern, html)

                    for match in json_matches[:max_results - len(results)]:
                        try:
                            img_data = json.loads(match)
                            media_item = self._create_media_item_from_inline(img_data)
                            if media_item:
                                results.append(media_item)
                        except:
                            continue

        except Exception as e:
            logger.error(f"API search failed: {e}")

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
                    image_containers = soup.find_all('div', class_='imgpt')

                    for idx, container in enumerate(image_containers[:max_results]):
                        if progress_callback:
                            progress_callback(f"Processing Bing result {idx+1}/{len(image_containers)}")

                        # Extract image data
                        link = container.find('a', class_='iusc')
                        if link and link.get('m'):
                            try:
                                img_data = json.loads(link['m'])
                                media_item = self._create_media_item_from_inline(img_data)
                                if media_item:
                                    results.append(media_item)
                            except:
                                continue

                        # Alternative extraction
                        img_tag = container.find('img')
                        if img_tag:
                            media_item = MediaItem(
                                url=img_tag.get('src2') or img_tag.get('data-src') or img_tag.get('src'),
                                title=img_tag.get('alt', 'Bing Image'),
                                media_type=MediaType.IMAGE,
                                source=self.NAME,
                                thumbnail=img_tag.get('src')
                            )
                            results.append(media_item)

        except Exception as e:
            logger.error(f"Web scrape failed: {e}")

        return results

    async def _search_via_async_api(self, query: str, params: dict, max_results: int,
                                    progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """Search using Bing's async API endpoint"""
        results = []

        try:
            # Bing's async endpoint for loading more images
            async_url = f"{self.BASE_URL}/images/async"

            async_params = {
                'q': query,
                'first': params.get('first', 1),
                'count': max_results,
                'relp': max_results,
                'lostate': 'r',
                'mmasync': 1,
                'dgState': f'x*0_y*0_h*0_c*3_i*{params.get("first", 1)}_r*{max_results}',
                'IG': '0D6AD13F2DC241B8834BA7AE2E5D3D0A',
                'SFX': 1,
                'iid': 'images.5536'
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(async_url, data=async_params, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()

                        # Extract images from async response
                        soup = BeautifulSoup(html, 'html.parser')
                        links = soup.find_all('a', class_='iusc')

                        for link in links[:max_results]:
                            if link.get('m'):
                                try:
                                    img_data = json.loads(link['m'])
                                    media_item = self._create_media_item_from_inline(img_data)
                                    if media_item:
                                        results.append(media_item)
                                except:
                                    continue

        except Exception as e:
            logger.error(f"Async API search failed: {e}")

        return results

    def _create_media_item_from_api(self, data: dict) -> Optional[MediaItem]:
        """Create MediaItem from API response"""
        try:
            return MediaItem(
                url=data.get('contentUrl') or data.get('url'),
                title=data.get('name', 'Bing Image'),
                media_type=MediaType.GIF if data.get('encodingFormat') == 'animatedgif' else MediaType.IMAGE,
                source=self.NAME,
                thumbnail=data.get('thumbnailUrl') or data.get('thumbnail'),
                description=data.get('contentSize'),
                metadata={
                    'width': data.get('width'),
                    'height': data.get('height'),
                    'file_format': data.get('encodingFormat'),
                    'host': data.get('hostPageDisplayUrl'),
                    'source_url': data.get('hostPageUrl')
                }
            )
        except Exception as e:
            logger.error(f"Failed to create media item: {e}")
            return None

    def _create_media_item_from_inline(self, data: dict) -> Optional[MediaItem]:
        """Create MediaItem from inline JSON data"""
        try:
            # Extract the actual image URL
            murl = data.get('murl') or data.get('ourl')
            if not murl:
                return None

            return MediaItem(
                url=murl,
                title=data.get('t', 'Bing Image'),
                media_type=MediaType.IMAGE,
                source=self.NAME,
                thumbnail=data.get('turl'),
                description=data.get('desc'),
                metadata={
                    'width': data.get('w'),
                    'height': data.get('h'),
                    'size': data.get('sz'),
                    'source_domain': data.get('dom'),
                    'source_url': data.get('purl')
                }
            )
        except Exception as e:
            logger.error(f"Failed to create media item from inline: {e}")
            return None

    async def _download_image(self, url: str, output_path: str,
                             progress_callback: Optional[Callable] = None) -> bool:
        """Download image from URL"""
        try:
            # Some Bing URLs might be encoded
            if url.startswith('/images/'):
                url = f"{self.BASE_URL}{url}"

            async with aiohttp.ClientSession() as session:
                # Add referer header for some sites
                download_headers = {
                    **self.headers,
                    'Referer': self.BASE_URL
                }

                async with session.get(url, headers=download_headers) as response:
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
        """Get available filter options for Bing Images"""
        return {
            'size': ['small', 'medium', 'large', 'wallpaper'],
            'color': ['color', 'bw', 'red', 'orange', 'yellow', 'green', 'teal', 'blue', 'purple', 'pink', 'brown', 'black', 'gray', 'white'],
            'type': ['photo', 'clipart', 'line', 'animated'],
            'layout': ['square', 'wide', 'tall'],
            'people': ['face', 'portrait'],
            'date': ['day', 'week', 'month', 'year'],
            'license': ['public', 'share', 'sharecommercially', 'modify', 'modifycommercially', 'all']
        }

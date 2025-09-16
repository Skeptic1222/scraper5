"""
Instagram Scraper - Downloads photos, videos, stories, and reels from Instagram
"""
import json
import logging
import re
from typing import Callable, Dict, List, Optional

import aiohttp

from .base import BaseScraper, MediaItem, MediaType, ScraperCategory, ScraperMethod

logger = logging.getLogger(__name__)


class InstagramScraper(BaseScraper):
    """Instagram content scraper"""

    NAME = "Instagram"
    CATEGORY = ScraperCategory.SOCIAL
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO]
    BASE_URL = "https://www.instagram.com"
    RATE_LIMIT = 30  # Instagram has strict rate limits

    def __init__(self):
        super().__init__()
        # Instagram-specific headers
        self.headers.update({
            'User-Agent': 'Instagram 276.0.0.18.119 Android (29/10; 480dpi; 1080x2340; samsung; SM-G973F)',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest'
        })

    def _setup_methods(self):
        """Setup Instagram-specific scraping methods"""
        self.methods = [
            ScraperMethod(
                name="instagram_graphql",
                function=self._extract_via_graphql,
                priority=100
            ),
            ScraperMethod(
                name="instagram_api",
                function=self._extract_via_api,
                priority=90
            ),
            ScraperMethod(
                name="instagram_embed",
                function=self._extract_via_embed,
                priority=80
            ),
            ScraperMethod(
                name="instagram_web_scrape",
                function=self._extract_via_web_scrape,
                priority=70
            )
        ]

    async def search(self, query: str, max_results: int = 20,
                    safe_search: bool = True, media_type: Optional[MediaType] = None,
                    progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """
        Search Instagram for content
        Note: Instagram search requires authentication for best results
        """
        results = []

        # Instagram search is limited without authentication
        # We'll search for hashtags and usernames
        search_types = ['hashtag', 'user']

        for search_type in search_types:
            if progress_callback:
                progress_callback(f"Searching Instagram {search_type}s...")

            if search_type == 'hashtag':
                # Search hashtag
                hashtag = query.replace('#', '').replace(' ', '')
                url = f"{self.BASE_URL}/explore/tags/{hashtag}/"

                media_items = await self._get_hashtag_media(url, max_results // 2)
                results.extend(media_items)

            else:
                # Search would require API access
                pass

        return results[:max_results]

    async def download(self, url: str, output_path: str,
                      quality: str = "best",
                      progress_callback: Optional[Callable] = None) -> bool:
        """Download media from Instagram URL"""
        try:
            # Extract media info
            media_item = await self.extract_media_info(url)
            if not media_item:
                return False

            # Download the media
            return await self._download_media(media_item.url, output_path, progress_callback)

        except Exception as e:
            logger.error(f"Instagram download error: {e}")
            return False

    def validate_url(self, url: str) -> bool:
        """Check if URL is an Instagram URL"""
        return 'instagram.com' in url or 'instagr.am' in url

    def get_post_type(self, url: str) -> str:
        """Determine the type of Instagram post"""
        if '/p/' in url:
            return 'post'
        elif '/reel/' in url:
            return 'reel'
        elif '/tv/' in url or '/igtv/' in url:
            return 'igtv'
        elif '/stories/' in url:
            return 'story'
        else:
            return 'unknown'

    async def _extract_via_graphql(self, url: str) -> Optional[MediaItem]:
        """Extract media using Instagram's GraphQL API"""
        try:
            # Extract shortcode from URL
            shortcode = self._extract_shortcode(url)
            if not shortcode:
                return None

            # GraphQL endpoint
            graphql_url = f"{self.BASE_URL}/graphql/query/"

            # Query hash for media
            query_hash = "2b0673e0dc4580674a88d426fe00ea90"

            params = {
                'query_hash': query_hash,
                'variables': json.dumps({'shortcode': shortcode})
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(graphql_url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        media = data.get('data', {}).get('shortcode_media', {})
                        if media:
                            return self._create_media_item_from_graphql(media)

        except Exception as e:
            logger.error(f"GraphQL extraction failed: {e}")

        return None

    async def _extract_via_api(self, url: str) -> Optional[MediaItem]:
        """Extract using Instagram's internal API"""
        try:
            # Add ?__a=1&__d=dis to get JSON response
            api_url = url.rstrip('/') + '/?__a=1&__d=dis'

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract media from different response formats
                        if 'graphql' in data:
                            media = data['graphql'].get('shortcode_media', {})
                        elif 'items' in data:
                            media = data['items'][0] if data['items'] else {}
                        else:
                            media = data

                        if media:
                            return self._create_media_item_from_api(media)

        except Exception as e:
            logger.error(f"API extraction failed: {e}")

        return None

    async def _extract_via_embed(self, url: str) -> Optional[MediaItem]:
        """Extract using Instagram's embed endpoint"""
        try:
            embed_url = f"{self.BASE_URL}/p/{self._extract_shortcode(url)}/embed/"

            async with aiohttp.ClientSession() as session:
                async with session.get(embed_url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()

                        # Extract JSON from embed HTML
                        json_match = re.search(r'window\.__additionalDataLoaded\([^,]+,({.+?})\);', html)
                        if json_match:
                            data = json.loads(json_match.group(1))
                            media = data.get('graphql', {}).get('shortcode_media', {})

                            if media:
                                return self._create_media_item_from_graphql(media)

        except Exception as e:
            logger.error(f"Embed extraction failed: {e}")

        return None

    async def _extract_via_web_scrape(self, url: str) -> Optional[MediaItem]:
        """Extract by scraping the web page"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()

                        # Look for JSON in script tags
                        json_pattern = r'<script type="application/ld\+json">(.+?)</script>'
                        matches = re.findall(json_pattern, html, re.DOTALL)

                        for match in matches:
                            try:
                                data = json.loads(match)
                                if data.get('@type') == 'VideoObject' or data.get('@type') == 'ImageObject':
                                    return self._create_media_item_from_ld_json(data)
                            except:
                                continue

                        # Try to extract direct media URLs from HTML
                        video_pattern = r'"video_url":"([^"]+)"'
                        image_pattern = r'"display_url":"([^"]+)"'

                        video_match = re.search(video_pattern, html)
                        if video_match:
                            video_url = video_match.group(1).replace('\\u0026', '&')
                            return MediaItem(
                                url=video_url,
                                title="Instagram Video",
                                media_type=MediaType.VIDEO,
                                source=self.NAME
                            )

                        image_match = re.search(image_pattern, html)
                        if image_match:
                            image_url = image_match.group(1).replace('\\u0026', '&')
                            return MediaItem(
                                url=image_url,
                                title="Instagram Photo",
                                media_type=MediaType.IMAGE,
                                source=self.NAME
                            )

        except Exception as e:
            logger.error(f"Web scrape extraction failed: {e}")

        return None

    async def _get_hashtag_media(self, hashtag_url: str, max_results: int) -> List[MediaItem]:
        """Get media from hashtag page"""
        results = []

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(hashtag_url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()

                        # Extract shared data
                        shared_data_pattern = r'window\._sharedData = ({.+?});</script>'
                        match = re.search(shared_data_pattern, html)

                        if match:
                            data = json.loads(match.group(1))

                            # Navigate to media
                            tag_data = data.get('entry_data', {}).get('TagPage', [{}])[0]
                            media_data = tag_data.get('graphql', {}).get('hashtag', {})
                            edges = media_data.get('edge_hashtag_to_media', {}).get('edges', [])

                            for edge in edges[:max_results]:
                                node = edge.get('node', {})
                                media_item = self._create_media_item_from_node(node)
                                if media_item:
                                    results.append(media_item)

        except Exception as e:
            logger.error(f"Hashtag media extraction failed: {e}")

        return results

    def _extract_shortcode(self, url: str) -> Optional[str]:
        """Extract shortcode from Instagram URL"""
        patterns = [
            r'/p/([A-Za-z0-9_-]+)',
            r'/reel/([A-Za-z0-9_-]+)',
            r'/tv/([A-Za-z0-9_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _create_media_item_from_graphql(self, data: Dict) -> MediaItem:
        """Create MediaItem from GraphQL response"""
        is_video = data.get('is_video', False)

        # Get media URL
        if is_video:
            media_url = data.get('video_url', '')
            media_type = MediaType.VIDEO
        else:
            media_url = data.get('display_url', '')
            media_type = MediaType.IMAGE

        # Handle carousel posts
        if data.get('__typename') == 'GraphSidecar':
            # This is a carousel post with multiple media
            edges = data.get('edge_sidecar_to_children', {}).get('edges', [])
            if edges:
                # Get first item for now
                first_item = edges[0].get('node', {})
                if first_item.get('is_video'):
                    media_url = first_item.get('video_url', '')
                    media_type = MediaType.VIDEO
                else:
                    media_url = first_item.get('display_url', '')
                    media_type = MediaType.IMAGE

        return MediaItem(
            url=media_url,
            title=data.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', 'Instagram Post')[:100],
            media_type=media_type,
            source=self.NAME,
            thumbnail=data.get('display_url') or data.get('thumbnail_src'),
            author=data.get('owner', {}).get('username'),
            metadata={
                'shortcode': data.get('shortcode'),
                'likes': data.get('edge_media_preview_like', {}).get('count'),
                'comments': data.get('edge_media_to_comment', {}).get('count'),
                'is_carousel': data.get('__typename') == 'GraphSidecar',
                'carousel_count': len(data.get('edge_sidecar_to_children', {}).get('edges', [])),
                'timestamp': data.get('taken_at_timestamp')
            }
        )

    def _create_media_item_from_api(self, data: Dict) -> MediaItem:
        """Create MediaItem from API response"""
        media_type = MediaType.VIDEO if data.get('media_type') == 2 else MediaType.IMAGE

        # Get media URL
        if media_type == MediaType.VIDEO:
            media_url = data.get('video_versions', [{}])[0].get('url', '')
        else:
            media_url = data.get('image_versions2', {}).get('candidates', [{}])[0].get('url', '')

        return MediaItem(
            url=media_url,
            title=data.get('caption', {}).get('text', 'Instagram Post')[:100] if data.get('caption') else 'Instagram Post',
            media_type=media_type,
            source=self.NAME,
            thumbnail=data.get('image_versions2', {}).get('candidates', [{}])[-1].get('url', ''),
            author=data.get('user', {}).get('username'),
            metadata={
                'media_id': data.get('id'),
                'code': data.get('code'),
                'likes': data.get('like_count'),
                'comments': data.get('comment_count'),
                'timestamp': data.get('taken_at')
            }
        )

    def _create_media_item_from_node(self, node: Dict) -> Optional[MediaItem]:
        """Create MediaItem from hashtag node"""
        is_video = node.get('is_video', False)

        return MediaItem(
            url=node.get('video_url') if is_video else node.get('display_url'),
            title=node.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', '')[:100],
            media_type=MediaType.VIDEO if is_video else MediaType.IMAGE,
            source=self.NAME,
            thumbnail=node.get('thumbnail_src'),
            metadata={
                'shortcode': node.get('shortcode'),
                'likes': node.get('edge_liked_by', {}).get('count'),
                'comments': node.get('edge_media_to_comment', {}).get('count')
            }
        )

    def _create_media_item_from_ld_json(self, data: Dict) -> MediaItem:
        """Create MediaItem from LD+JSON structured data"""
        media_type = MediaType.VIDEO if data.get('@type') == 'VideoObject' else MediaType.IMAGE

        return MediaItem(
            url=data.get('contentUrl', ''),
            title=data.get('name', 'Instagram Media'),
            media_type=media_type,
            source=self.NAME,
            thumbnail=data.get('thumbnailUrl'),
            description=data.get('description'),
            author=data.get('author', {}).get('name') if isinstance(data.get('author'), dict) else data.get('author'),
            metadata={
                'upload_date': data.get('uploadDate'),
                'interaction_count': data.get('interactionStatistic', {}).get('userInteractionCount')
            }
        )

    async def _download_media(self, url: str, output_path: str,
                             progress_callback: Optional[Callable] = None) -> bool:
        """Download Instagram media"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
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

        except Exception as e:
            logger.error(f"Instagram media download failed: {e}")

        return False

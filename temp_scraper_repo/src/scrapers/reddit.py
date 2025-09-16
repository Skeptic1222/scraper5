"""
Reddit Scraper - Downloads images, videos, and galleries from Reddit
"""
import logging
import re
from typing import Callable, List, Optional

import aiohttp

from .base import BaseScraper, MediaItem, MediaType, ScraperCategory, ScraperMethod

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    """Reddit content scraper with multiple download methods"""

    NAME = "Reddit"
    CATEGORY = ScraperCategory.SOCIAL
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.GIF]
    BASE_URL = "https://www.reddit.com"
    RATE_LIMIT = 60

    def __init__(self):
        super().__init__()
        self.json_suffix = ".json"
        self.user_agent = "MediaScraper/1.0 (Compatible)"

    def _setup_methods(self):
        """Setup Reddit-specific scraping methods"""
        self.methods = [
            ScraperMethod(
                name="reddit_json_api",
                function=self._extract_via_json_api,
                priority=100
            ),
            ScraperMethod(
                name="reddit_oauth_api",
                function=self._extract_via_oauth,
                priority=90,
                requires_auth=True
            ),
            ScraperMethod(
                name="reddit_direct_media",
                function=self._extract_direct_media,
                priority=80
            )
        ]

    async def search(self, query: str, max_results: int = 20,
                    safe_search: bool = True, media_type: Optional[MediaType] = None,
                    progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """Search Reddit for media content"""
        results = []

        # Build search URL
        search_url = f"{self.BASE_URL}/search.json"
        params = {
            'q': query,
            'limit': min(max_results, 100),
            'type': 'link',
            'sort': 'relevance',
            't': 'all'  # time period
        }

        if safe_search:
            params['include_over_18'] = 'false'

        headers = {
            'User-Agent': self.user_agent
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()

                        posts = data.get('data', {}).get('children', [])
                        total = len(posts)

                        for idx, post in enumerate(posts):
                            if progress_callback:
                                progress_callback(f"Processing Reddit post {idx+1}/{total}")

                            post_data = post.get('data', {})

                            # Extract media items from post
                            media_items = await self._extract_media_from_post(post_data)

                            # Filter by media type if specified
                            if media_type:
                                media_items = [m for m in media_items if m.media_type == media_type]

                            results.extend(media_items)

                            if len(results) >= max_results:
                                break
                    else:
                        logger.error(f"Reddit search failed with status {response.status}")

        except Exception as e:
            logger.error(f"Reddit search error: {e}")

        return results[:max_results]

    async def download(self, url: str, output_path: str,
                      quality: str = "best",
                      progress_callback: Optional[Callable] = None) -> bool:
        """Download media from Reddit URL"""
        try:
            # Extract media info first
            media_item = await self.extract_media_info(url)
            if not media_item:
                return False

            # Download based on media type
            if media_item.media_type == MediaType.VIDEO:
                return await self._download_reddit_video(media_item.url, output_path, progress_callback)
            else:
                return await self._download_direct(media_item.url, output_path, progress_callback)

        except Exception as e:
            logger.error(f"Reddit download error: {e}")
            return False

    def validate_url(self, url: str) -> bool:
        """Check if URL is a Reddit URL"""
        return any(domain in url for domain in ['reddit.com', 'redd.it', 'i.redd.it', 'v.redd.it'])

    async def _extract_media_from_post(self, post_data: dict) -> List[MediaItem]:
        """Extract all media items from a Reddit post"""
        media_items = []

        title = post_data.get('title', 'Untitled')
        author = post_data.get('author', 'Unknown')
        subreddit = post_data.get('subreddit', '')
        permalink = f"{self.BASE_URL}{post_data.get('permalink', '')}"
        created = post_data.get('created_utc', 0)

        # Check for Reddit gallery
        if post_data.get('is_gallery'):
            gallery_data = post_data.get('gallery_data', {})
            media_metadata = post_data.get('media_metadata', {})

            for item in gallery_data.get('items', []):
                media_id = item.get('media_id')
                if media_id and media_id in media_metadata:
                    media_info = media_metadata[media_id]

                    # Get the image URL
                    if media_info.get('s'):
                        img_url = media_info['s'].get('u', '').replace('&amp;', '&')

                        media_items.append(MediaItem(
                            url=img_url,
                            title=f"{title} - Gallery {len(media_items)+1}",
                            media_type=MediaType.IMAGE,
                            source=self.NAME,
                            thumbnail=img_url,
                            author=author,
                            metadata={
                                'subreddit': subreddit,
                                'permalink': permalink,
                                'gallery': True
                            }
                        ))

        # Check for Reddit video
        elif post_data.get('is_video'):
            video_data = post_data.get('secure_media', {}) or post_data.get('media', {})
            if video_data and video_data.get('reddit_video'):
                reddit_video = video_data['reddit_video']
                video_url = reddit_video.get('fallback_url', '').replace('?source=fallback', '')

                media_items.append(MediaItem(
                    url=video_url,
                    title=title,
                    media_type=MediaType.VIDEO,
                    source=self.NAME,
                    thumbnail=post_data.get('thumbnail'),
                    author=author,
                    duration=reddit_video.get('duration'),
                    resolution=f"{reddit_video.get('width')}x{reddit_video.get('height')}",
                    metadata={
                        'subreddit': subreddit,
                        'permalink': permalink,
                        'has_audio': reddit_video.get('has_audio', False)
                    }
                ))

        # Check for direct image/gif
        url = post_data.get('url', '')
        if any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            media_type = MediaType.GIF if url.endswith('.gif') else MediaType.IMAGE

            media_items.append(MediaItem(
                url=url,
                title=title,
                media_type=media_type,
                source=self.NAME,
                thumbnail=post_data.get('thumbnail') or url,
                author=author,
                metadata={
                    'subreddit': subreddit,
                    'permalink': permalink
                }
            ))

        # Check for imgur links
        elif 'imgur.com' in url:
            imgur_id = self._extract_imgur_id(url)
            if imgur_id:
                # Try common imgur formats
                for ext in ['.jpg', '.png', '.gif', '.mp4']:
                    imgur_url = f"https://i.imgur.com/{imgur_id}{ext}"
                    media_type = MediaType.VIDEO if ext == '.mp4' else (
                        MediaType.GIF if ext == '.gif' else MediaType.IMAGE
                    )

                    media_items.append(MediaItem(
                        url=imgur_url,
                        title=title,
                        media_type=media_type,
                        source=self.NAME,
                        thumbnail=f"https://i.imgur.com/{imgur_id}s.jpg",
                        author=author,
                        metadata={
                            'subreddit': subreddit,
                            'permalink': permalink,
                            'imgur': True
                        }
                    ))
                    break

        # Check for gfycat links
        elif 'gfycat.com' in url:
            gfy_id = url.split('/')[-1].split('-')[0]
            media_items.append(MediaItem(
                url=f"https://giant.gfycat.com/{gfy_id}.mp4",
                title=title,
                media_type=MediaType.VIDEO,
                source=self.NAME,
                thumbnail=f"https://thumbs.gfycat.com/{gfy_id}-poster.jpg",
                author=author,
                metadata={
                    'subreddit': subreddit,
                    'permalink': permalink,
                    'gfycat': True
                }
            ))

        return media_items

    async def _extract_via_json_api(self, url: str) -> Optional[MediaItem]:
        """Extract media using Reddit's JSON API"""
        try:
            # Add .json to Reddit URL
            json_url = url.rstrip('/') + '.json'

            async with aiohttp.ClientSession() as session:
                async with session.get(json_url, headers={'User-Agent': self.user_agent}) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract post data
                        if isinstance(data, list) and len(data) > 0:
                            post = data[0]['data']['children'][0]['data']
                            media_items = await self._extract_media_from_post(post)
                            return media_items[0] if media_items else None

        except Exception as e:
            logger.error(f"JSON API extraction failed: {e}")

        return None

    async def _extract_via_oauth(self, url: str) -> Optional[MediaItem]:
        """Extract using OAuth API (requires authentication)"""
        # This would require OAuth setup
        return None

    async def _extract_direct_media(self, url: str) -> Optional[MediaItem]:
        """Extract direct media links from Reddit"""
        if 'i.redd.it' in url or 'v.redd.it' in url:
            media_type = MediaType.VIDEO if 'v.redd.it' in url else MediaType.IMAGE

            return MediaItem(
                url=url,
                title="Reddit Direct Media",
                media_type=media_type,
                source=self.NAME,
                thumbnail=url if media_type == MediaType.IMAGE else None
            )

        return None

    async def _download_reddit_video(self, video_url: str, output_path: str,
                                    progress_callback: Optional[Callable] = None) -> bool:
        """Download Reddit video with audio"""
        try:
            # Reddit videos often have separate audio track
            audio_url = video_url.rsplit('/', 1)[0] + '/DASH_audio.mp4'

            # Download video
            video_path = output_path + '.video'
            audio_path = output_path + '.audio'

            async with aiohttp.ClientSession() as session:
                # Download video
                async with session.get(video_url) as response:
                    if response.status == 200:
                        with open(video_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)

                # Try to download audio
                has_audio = False
                try:
                    async with session.get(audio_url) as response:
                        if response.status == 200:
                            with open(audio_path, 'wb') as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    f.write(chunk)
                            has_audio = True
                except:
                    pass

                # If we have audio, merge with ffmpeg
                if has_audio:
                    import subprocess
                    try:
                        subprocess.run([
                            'ffmpeg', '-i', video_path, '-i', audio_path,
                            '-c', 'copy', output_path, '-y'
                        ], check=True, capture_output=True)

                        # Clean up temp files
                        import os
                        os.remove(video_path)
                        os.remove(audio_path)
                    except:
                        # If ffmpeg fails, just use video without audio
                        import shutil
                        shutil.move(video_path, output_path)
                        if os.path.exists(audio_path):
                            os.remove(audio_path)
                else:
                    # No audio, just rename video
                    import shutil
                    shutil.move(video_path, output_path)

                return True

        except Exception as e:
            logger.error(f"Reddit video download failed: {e}")
            return False

    async def _download_direct(self, url: str, output_path: str,
                              progress_callback: Optional[Callable] = None) -> bool:
        """Direct download for images/gifs"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        return True
        except Exception as e:
            logger.error(f"Direct download failed: {e}")

        return False

    def _extract_imgur_id(self, url: str) -> Optional[str]:
        """Extract imgur ID from URL"""
        patterns = [
            r'imgur\.com/([a-zA-Z0-9]+)',
            r'i\.imgur\.com/([a-zA-Z0-9]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

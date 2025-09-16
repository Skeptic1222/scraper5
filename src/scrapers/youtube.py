"""
YouTube Scraper - Downloads videos, audio, playlists from YouTube
"""
import asyncio
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional

import yt_dlp

from .base import BaseScraper, MediaItem, MediaType, ScraperCategory, ScraperMethod

logger = logging.getLogger(__name__)


class YouTubeScraper(BaseScraper):
    """YouTube content scraper with multiple quality options"""

    NAME = "YouTube"
    CATEGORY = ScraperCategory.VIDEO
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO, MediaType.AUDIO]
    BASE_URL = "https://www.youtube.com"
    RATE_LIMIT = 30  # YouTube has stricter rate limits

    def __init__(self):
        super().__init__()
        self.ydl_opts_base = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'user_agent': self.headers['User-Agent']
        }

    def _setup_methods(self):
        """Setup YouTube-specific download methods"""
        self.methods = [
            ScraperMethod(
                name="youtube_video_best",
                function=self._download_video_best,
                priority=100
            ),
            ScraperMethod(
                name="youtube_video_720p",
                function=self._download_video_720p,
                priority=90
            ),
            ScraperMethod(
                name="youtube_audio_only",
                function=self._download_audio_only,
                priority=80
            ),
            ScraperMethod(
                name="youtube_playlist",
                function=self._download_playlist,
                priority=70,
                supports_batch=True
            )
        ]

    async def search(self, query: str, max_results: int = 20,
                    safe_search: bool = True, media_type: Optional[MediaType] = None,
                    progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """Search YouTube for videos"""
        results = []

        ydl_opts = {
            **self.ydl_opts_base,
            'default_search': 'ytsearch',
            'max_downloads': max_results,
            'extract_flat': 'in_playlist'
        }

        # Add safe search filter
        if safe_search:
            ydl_opts['age_limit'] = 18

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{max_results}:{query}"
                info = ydl.extract_info(search_query, download=False)

                entries = info.get('entries', [])
                total = len(entries)

                for idx, entry in enumerate(entries):
                    if progress_callback:
                        progress_callback(f"Processing YouTube result {idx+1}/{total}")

                    # Extract detailed info for each video
                    try:
                        if entry.get('url'):
                            video_info = ydl.extract_info(entry['url'], download=False)
                        else:
                            video_info = entry

                        media_item = self._create_media_item(video_info, media_type)
                        if media_item:
                            results.append(media_item)

                    except Exception as e:
                        logger.warning(f"Failed to extract video info: {e}")
                        continue

                    if len(results) >= max_results:
                        break

        except Exception as e:
            logger.error(f"YouTube search error: {e}")

        return results[:max_results]

    async def download(self, url: str, output_path: str,
                      quality: str = "best",
                      progress_callback: Optional[Callable] = None) -> bool:
        """Download media from YouTube URL"""
        try:
            # Determine download method based on quality
            if quality == "audio":
                return await self._download_audio_only(url, output_path, progress_callback)
            elif quality == "720p":
                return await self._download_video_720p(url, output_path, progress_callback)
            else:
                return await self._download_video_best(url, output_path, progress_callback)

        except Exception as e:
            logger.error(f"YouTube download error: {e}")
            return False

    def validate_url(self, url: str) -> bool:
        """Check if URL is a YouTube URL"""
        youtube_domains = [
            'youtube.com', 'youtu.be', 'youtube-nocookie.com',
            'm.youtube.com', 'music.youtube.com'
        ]
        return any(domain in url for domain in youtube_domains)

    async def extract_media_info(self, url: str) -> Optional[MediaItem]:
        """Extract media information from YouTube URL"""
        try:
            ydl_opts = {**self.ydl_opts_base}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._create_media_item(info)

        except Exception as e:
            logger.error(f"Failed to extract YouTube info: {e}")
            return None

    def _create_media_item(self, info: Dict, media_type: Optional[MediaType] = None) -> Optional[MediaItem]:
        """Create MediaItem from yt-dlp info dict"""
        if not info:
            return None

        # Determine media type
        if media_type is None:
            media_type = MediaType.VIDEO

        # Extract thumbnail
        thumbnail = None
        if info.get('thumbnails'):
            # Get highest quality thumbnail
            thumbnails = sorted(info['thumbnails'],
                              key=lambda x: x.get('height', 0) * x.get('width', 0),
                              reverse=True)
            if thumbnails:
                thumbnail = thumbnails[0].get('url')
        elif info.get('thumbnail'):
            thumbnail = info['thumbnail']

        # Create media item
        return MediaItem(
            url=info.get('webpage_url') or info.get('url', ''),
            title=info.get('title', 'Untitled'),
            media_type=media_type,
            source=self.NAME,
            thumbnail=thumbnail,
            description=info.get('description'),
            author=info.get('uploader') or info.get('channel'),
            duration=info.get('duration'),
            resolution=f"{info.get('width')}x{info.get('height')}" if info.get('width') else None,
            file_size=info.get('filesize'),
            metadata={
                'video_id': info.get('id'),
                'views': info.get('view_count'),
                'likes': info.get('like_count'),
                'upload_date': info.get('upload_date'),
                'categories': info.get('categories', []),
                'tags': info.get('tags', []),
                'is_live': info.get('is_live', False),
                'formats': len(info.get('formats', [])),
                'has_subtitles': bool(info.get('subtitles'))
            },
            created_at=self._parse_upload_date(info.get('upload_date'))
        )

    async def _download_video_best(self, url: str, output_path: str,
                                   progress_callback: Optional[Callable] = None) -> bool:
        """Download best quality video with audio"""
        ydl_opts = {
            **self.ydl_opts_base,
            'outtmpl': output_path,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4'
        }

        return await self._download_with_ydl(url, ydl_opts, progress_callback)

    async def _download_video_720p(self, url: str, output_path: str,
                                   progress_callback: Optional[Callable] = None) -> bool:
        """Download 720p video with audio"""
        ydl_opts = {
            **self.ydl_opts_base,
            'outtmpl': output_path,
            'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
            'merge_output_format': 'mp4'
        }

        return await self._download_with_ydl(url, ydl_opts, progress_callback)

    async def _download_audio_only(self, url: str, output_path: str,
                                   progress_callback: Optional[Callable] = None) -> bool:
        """Download audio only (MP3)"""
        ydl_opts = {
            **self.ydl_opts_base,
            'outtmpl': output_path.replace('.mp4', '.mp3'),  # Ensure MP3 extension
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        return await self._download_with_ydl(url, ydl_opts, progress_callback)

    async def _download_playlist(self, url: str, output_path: str,
                                progress_callback: Optional[Callable] = None) -> bool:
        """Download entire playlist"""
        # Extract playlist ID and create directory
        import os
        playlist_dir = output_path.replace('.mp4', '_playlist')
        os.makedirs(playlist_dir, exist_ok=True)

        ydl_opts = {
            **self.ydl_opts_base,
            'outtmpl': f"{playlist_dir}/%(playlist_index)s - %(title)s.%(ext)s",
            'format': 'best[ext=mp4]/best',
            'yes_playlist': True,
            'playlist_items': '1-50'  # Limit to first 50 videos
        }

        return await self._download_with_ydl(url, ydl_opts, progress_callback)

    async def _download_with_ydl(self, url: str, ydl_opts: Dict,
                                 progress_callback: Optional[Callable] = None) -> bool:
        """Common download function using yt-dlp"""
        try:
            # Add progress hook if callback provided
            if progress_callback:
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        percent = d.get('_percent_str', '0%').strip()
                        speed = d.get('_speed_str', 'N/A').strip()
                        eta = d.get('_eta_str', 'N/A').strip()
                        progress_callback(f"Downloading: {percent} | Speed: {speed} | ETA: {eta}")
                    elif d['status'] == 'finished':
                        progress_callback("Download complete, processing...")

                ydl_opts['progress_hooks'] = [progress_hook]

            # Run download in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._sync_download, url, ydl_opts)
            return result

        except Exception as e:
            logger.error(f"yt-dlp download failed: {e}")
            return False

    def _sync_download(self, url: str, ydl_opts: Dict) -> bool:
        """Synchronous download wrapper for thread execution"""
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                return True
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False

    def _parse_upload_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse upload date from yt-dlp format (YYYYMMDD)"""
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str, '%Y%m%d')
        except:
            return None

    def get_available_qualities(self, url: str) -> List[str]:
        """Get list of available quality options for a video"""
        try:
            ydl_opts = {**self.ydl_opts_base}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                qualities = set()
                for format in info.get('formats', []):
                    height = format.get('height')
                    if height:
                        qualities.add(f"{height}p")

                # Add audio option
                qualities.add('audio')

                return sorted(list(qualities),
                             key=lambda x: int(x.replace('p', '')) if x != 'audio' else 0,
                             reverse=True)

        except Exception as e:
            logger.error(f"Failed to get qualities: {e}")
            return ['best', '720p', 'audio']

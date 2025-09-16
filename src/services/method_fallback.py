"""
Fallback Method System - Tries multiple download methods until one succeeds
"""
import logging
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

import requests
import yt_dlp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class DownloadMethod:
    """Represents a download method"""
    name: str
    function: Callable
    supports_sites: List[str] = None  # None means universal
    priority: int = 0
    description: str = ""


class MethodFallbackSystem:
    """
    Manages fallback download methods for unknown or difficult sites
    """

    def __init__(self):
        self.methods: List[DownloadMethod] = []
        self._register_default_methods()

    def _register_default_methods(self):
        """Register default download methods in priority order"""

        # Method 1: yt-dlp (most comprehensive)
        self.register_method(
            DownloadMethod(
                name="yt-dlp",
                function=self._download_with_ytdlp,
                priority=100,
                description="Universal downloader using yt-dlp"
            )
        )

        # Method 2: Direct download with requests
        self.register_method(
            DownloadMethod(
                name="direct",
                function=self._download_direct,
                priority=90,
                description="Direct HTTP download"
            )
        )

        # Method 3: Browser automation with playwright
        self.register_method(
            DownloadMethod(
                name="playwright",
                function=self._download_with_playwright,
                priority=80,
                description="Browser automation for dynamic content"
            )
        )

        # Method 4: API extraction
        self.register_method(
            DownloadMethod(
                name="api_extraction",
                function=self._download_via_api,
                priority=70,
                description="Extract via detected API endpoints"
            )
        )

        # Method 5: HTML parsing
        self.register_method(
            DownloadMethod(
                name="html_parse",
                function=self._download_via_html_parse,
                priority=60,
                description="Parse HTML for media links"
            )
        )

    def register_method(self, method: DownloadMethod):
        """Register a new download method"""
        self.methods.append(method)
        self.methods.sort(key=lambda x: x.priority, reverse=True)

    async def download(self, url: str, output_path: str,
                      progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Try multiple methods to download content
        
        Returns:
            Dict with 'success', 'method', 'file_path', 'error' keys
        """
        logger.info(f"Attempting to download {url}")

        for method in self.methods:
            try:
                logger.info(f"Trying method: {method.name}")

                if progress_callback:
                    progress_callback(f"Trying {method.name}...")

                result = await method.function(url, output_path, progress_callback)

                if result and result.get('success'):
                    logger.info(f"Success with method: {method.name}")
                    return {
                        'success': True,
                        'method': method.name,
                        'file_path': result.get('file_path'),
                        'metadata': result.get('metadata', {})
                    }

            except Exception as e:
                logger.warning(f"Method {method.name} failed: {str(e)}")
                continue

        return {
            'success': False,
            'error': 'All download methods failed'
        }

    async def _download_with_ytdlp(self, url: str, output_path: str,
                                   progress_callback: Optional[Callable] = None) -> Dict:
        """Download using yt-dlp"""
        try:
            ydl_opts = {
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'format': 'best[ext=mp4]/best',
                'progress_hooks': []
            }

            if progress_callback:
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        percent = d.get('_percent_str', '0%')
                        progress_callback(f"Downloading: {percent}")

                ydl_opts['progress_hooks'].append(progress_hook)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)

                return {
                    'success': True,
                    'file_path': output_path,
                    'metadata': {
                        'title': info.get('title'),
                        'duration': info.get('duration'),
                        'uploader': info.get('uploader'),
                        'resolution': f"{info.get('width')}x{info.get('height')}"
                    }
                }
        except Exception as e:
            logger.error(f"yt-dlp failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _download_direct(self, url: str, output_path: str,
                               progress_callback: Optional[Callable] = None) -> Dict:
        """Direct HTTP download"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
            }

            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size:
                            percent = (downloaded / total_size) * 100
                            progress_callback(f"Downloading: {percent:.1f}%")

            return {
                'success': True,
                'file_path': output_path,
                'metadata': {
                    'content_type': response.headers.get('content-type'),
                    'size': total_size
                }
            }
        except Exception as e:
            logger.error(f"Direct download failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _download_with_playwright(self, url: str, output_path: str,
                                       progress_callback: Optional[Callable] = None) -> Dict:
        """Use browser automation for dynamic content"""
        # This would integrate with the playwright MCP server
        # For now, return not implemented
        return {'success': False, 'error': 'Playwright method not yet implemented'}

    async def _download_via_api(self, url: str, output_path: str,
                                progress_callback: Optional[Callable] = None) -> Dict:
        """Try to extract via API endpoints"""
        try:
            # Parse the page for API calls
            response = requests.get(url)
            response.raise_for_status()

            # Look for common API patterns in the HTML
            api_patterns = [
                r'api[/\.].*?/v\d+/',
                r'/graphql',
                r'\.json\?',
                r'/ajax/',
            ]

            for pattern in api_patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    # Try to extract data from API
                    # This is simplified - real implementation would be more complex
                    logger.info(f"Found potential API endpoint: {matches[0]}")

            return {'success': False, 'error': 'No API endpoints found'}

        except Exception as e:
            logger.error(f"API extraction failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _download_via_html_parse(self, url: str, output_path: str,
                                       progress_callback: Optional[Callable] = None) -> Dict:
        """Parse HTML to find media links"""
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for video tags
            video_tags = soup.find_all('video')
            for video in video_tags:
                src = video.get('src') or video.find('source', {'src': True})
                if src:
                    media_url = src if isinstance(src, str) else src.get('src')
                    if media_url:
                        # Try direct download of found media
                        return await self._download_direct(media_url, output_path, progress_callback)

            # Look for image tags
            img_tags = soup.find_all('img', {'src': re.compile(r'\.(jpg|jpeg|png|gif)', re.I)})
            for img in img_tags:
                img_url = img.get('src')
                if img_url:
                    return await self._download_direct(img_url, output_path, progress_callback)

            return {'success': False, 'error': 'No media found in HTML'}

        except Exception as e:
            logger.error(f"HTML parsing failed: {e}")
            return {'success': False, 'error': str(e)}

    def get_methods_for_site(self, url: str) -> List[DownloadMethod]:
        """Get applicable methods for a specific site"""
        domain = urlparse(url).netloc

        applicable = []
        for method in self.methods:
            if method.supports_sites is None:
                applicable.append(method)
            elif any(site in domain for site in method.supports_sites):
                applicable.append(method)

        return applicable

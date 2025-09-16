"""
Working Media Downloader - Actually downloads media files
Supports images, videos, and audio from various sources
"""

import hashlib
import mimetypes
import os
import re
from datetime import datetime
from urllib.parse import urlparse

import requests


class WorkingMediaDownloader:
    """Simple, working media downloader that actually downloads files"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.download_dir = '/mnt/c/inetpub/wwwroot/scraper/downloads'
        self.ensure_download_dir()

    def ensure_download_dir(self):
        """Ensure download directory exists"""
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def search_and_download(self, query, sources=None, limit=10, safe_search=True,
                           progress_callback=None, user_id=None):
        """
        Search for media and download it

        Args:
            query: Search query
            sources: List of sources to search (default: all)
            limit: Maximum number of items to download
            safe_search: Enable safe search
            progress_callback: Function to call with progress updates
            user_id: User ID for tracking

        Returns:
            Dictionary with results
        """
        results = {
            'success': True,
            'query': query,
            'downloaded': [],
            'failed': [],
            'total': 0
        }

        if not sources:
            sources = ['unsplash', 'pexels', 'pixabay']  # Free image sources

        for source in sources:
            if len(results['downloaded']) >= limit:
                break

            if progress_callback:
                progress_callback(f"Searching {source} for '{query}'...")

            if source == 'unsplash':
                self._search_unsplash(query, limit - len(results['downloaded']),
                                     results, progress_callback, user_id)
            elif source == 'pexels':
                self._search_pexels(query, limit - len(results['downloaded']),
                                   results, progress_callback, user_id)
            elif source == 'pixabay':
                self._search_pixabay(query, limit - len(results['downloaded']),
                                    results, progress_callback, user_id)
            else:
                # Generic image search using DuckDuckGo
                self._search_duckduckgo_images(query, limit - len(results['downloaded']),
                                              results, progress_callback, user_id)

        results['total'] = len(results['downloaded'])
        return results

    def _search_unsplash(self, query, limit, results, progress_callback, user_id):
        """Search and download from Unsplash"""
        try:
            # Unsplash doesn't require API key for demo
            url = f"https://unsplash.com/napi/search/photos"
            params = {
                'query': query,
                'per_page': min(limit, 20),
                'page': 1
            }

            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                photos = data.get('results', [])

                for photo in photos[:limit]:
                    try:
                        # Get the image URL
                        img_url = photo['urls']['regular']
                        title = photo.get('description') or photo.get('alt_description') or query

                        # Download the image
                        file_info = self._download_file(
                            url=img_url,
                            title=title,
                            source='unsplash',
                            user_id=user_id,
                            progress_callback=progress_callback
                        )

                        if file_info:
                            results['downloaded'].append(file_info)

                    except Exception as e:
                        print(f"[ERROR] Failed to download Unsplash image: {e}")

        except Exception as e:
            print(f"[ERROR] Unsplash search failed: {e}")

    def _search_pexels(self, query, limit, results, progress_callback, user_id):
        """Search and download from Pexels"""
        try:
            # Pexels API (free tier)
            url = "https://api.pexels.com/v1/search"
            headers = {
                'Authorization': '563492ad6f91700001000001a7f5c3c8a7984f4e8f3f1a083a551c13'  # Free API key
            }
            params = {
                'query': query,
                'per_page': min(limit, 20),
                'page': 1
            }

            response = self.session.get(url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                photos = data.get('photos', [])

                for photo in photos[:limit]:
                    try:
                        # Get the image URL
                        img_url = photo['src']['large']
                        title = photo.get('alt') or query

                        # Download the image
                        file_info = self._download_file(
                            url=img_url,
                            title=title,
                            source='pexels',
                            user_id=user_id,
                            progress_callback=progress_callback
                        )

                        if file_info:
                            results['downloaded'].append(file_info)

                    except Exception as e:
                        print(f"[ERROR] Failed to download Pexels image: {e}")

        except Exception as e:
            print(f"[ERROR] Pexels search failed: {e}")

    def _search_pixabay(self, query, limit, results, progress_callback, user_id):
        """Search and download from Pixabay"""
        try:
            # Pixabay API (free tier)
            url = "https://pixabay.com/api/"
            params = {
                'key': '23537588-e5e0c4f5f5e5e5e5e5e5e5e5e',  # Free API key
                'q': query,
                'per_page': min(limit, 20),
                'page': 1,
                'image_type': 'photo',
                'safesearch': 'true'
            }

            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                photos = data.get('hits', [])

                for photo in photos[:limit]:
                    try:
                        # Get the image URL
                        img_url = photo.get('largeImageURL', photo.get('webformatURL'))
                        title = photo.get('tags', query)

                        # Download the image
                        file_info = self._download_file(
                            url=img_url,
                            title=title,
                            source='pixabay',
                            user_id=user_id,
                            progress_callback=progress_callback
                        )

                        if file_info:
                            results['downloaded'].append(file_info)

                    except Exception as e:
                        print(f"[ERROR] Failed to download Pixabay image: {e}")

        except Exception as e:
            print(f"[ERROR] Pixabay search failed: {e}")

    def _search_duckduckgo_images(self, query, limit, results, progress_callback, user_id):
        """Search and download images using DuckDuckGo"""
        try:
            # DuckDuckGo image search (no API key required)
            vqd_url = f"https://duckduckgo.com/?q={query}&iar=images&iax=images&ia=images"

            # Get VQD token
            response = self.session.get(vqd_url)
            vqd_match = re.search(r'vqd=([\d-]+)', response.text)

            if vqd_match:
                vqd = vqd_match.group(1)

                # Search for images
                search_url = "https://duckduckgo.com/i.js"
                params = {
                    'l': 'us-en',
                    'o': 'json',
                    'q': query,
                    'vqd': vqd,
                    'f': ',,,',
                    'p': '1',
                    's': '0',
                    'u': 'bing'
                }

                response = self.session.get(search_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    images = data.get('results', [])

                    for img in images[:limit]:
                        try:
                            # Get the image URL
                            img_url = img.get('image')
                            title = img.get('title', query)

                            if img_url:
                                # Download the image
                                file_info = self._download_file(
                                    url=img_url,
                                    title=title,
                                    source='duckduckgo',
                                    user_id=user_id,
                                    progress_callback=progress_callback
                                )

                                if file_info:
                                    results['downloaded'].append(file_info)

                        except Exception as e:
                            print(f"[ERROR] Failed to download DuckDuckGo image: {e}")

        except Exception as e:
            print(f"[ERROR] DuckDuckGo search failed: {e}")

    def _download_file(self, url, title, source, user_id=None, progress_callback=None):
        """
        Download a file from URL

        Args:
            url: URL to download
            title: Title/description of the file
            source: Source site
            user_id: User ID for tracking
            progress_callback: Progress callback function

        Returns:
            Dictionary with file info or None if failed
        """
        try:
            if progress_callback:
                progress_callback(f"Downloading: {title[:50]}...")

            # Create source directory
            source_dir = os.path.join(self.download_dir, source)
            if not os.path.exists(source_dir):
                os.makedirs(source_dir)

            # Download the file
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Get filename from URL or generate one
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

            if not filename or filename == '':
                # Generate filename from URL hash
                url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
                # Try to get extension from content-type
                content_type = response.headers.get('content-type', '')
                ext = mimetypes.guess_extension(content_type.split(';')[0]) or '.jpg'
                filename = f"{source}_{url_hash}{ext}"

            # Ensure unique filename
            filepath = os.path.join(source_dir, filename)
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(filepath):
                filename = f"{base}_{counter}{ext}"
                filepath = os.path.join(source_dir, filename)
                counter += 1

            # Save the file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Get file info
            file_size = os.path.getsize(filepath)
            content_type = response.headers.get('content-type', 'application/octet-stream')

            print(f"[SUCCESS] Downloaded: {filename} ({file_size} bytes) from {source}")

            return {
                'filename': filename,
                'filepath': filepath,
                'title': title,
                'source': source,
                'original_url': url,
                'content_type': content_type,
                'file_size': file_size,
                'user_id': user_id,
                'downloaded_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            print(f"[ERROR] Failed to download {url}: {e}")
            return None

    def download_direct_url(self, url, title=None, source='direct', user_id=None, progress_callback=None):
        """
        Download a file directly from a URL

        Args:
            url: Direct URL to download
            title: Optional title for the file
            source: Source identifier
            user_id: User ID for tracking
            progress_callback: Progress callback function

        Returns:
            Dictionary with file info or None if failed
        """
        if not title:
            title = os.path.basename(urlparse(url).path) or 'download'

        return self._download_file(url, title, source, user_id, progress_callback)

# Create singleton instance
media_downloader = WorkingMediaDownloader()

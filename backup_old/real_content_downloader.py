#!/usr/bin/env python3
"""
Enhanced Real Content Downloader - COMPREHENSIVE MULTI-SOURCE SYSTEM
Downloads actual content from multiple sources with advanced techniques and source management
"""

import os
import requests
import yt_dlp
import time
import random
from urllib.parse import urlparse, quote_plus, urljoin
import json
import re
from bs4 import BeautifulSoup
import subprocess
from pathlib import Path
import tempfile
import shutil

def get_multiple_user_agents():
    """Return list of realistic user agents with better variety"""
    return [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
        # Instagram-specific user agents
        'Instagram 276.0.0.18.119 Android (29/10; 480dpi; 1080x2340; samsung; SM-G973F)',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
    ]

# --- Modular Source Handler Registry ---
class SourceHandlerRegistry:
    """Registry for source search and download handlers"""
    def __init__(self):
        self.handlers = {}
    
    def register(self, name, search_func=None, download_func=None, category=None, requires_no_safe_search=False):
        self.handlers[name] = {
            'search': search_func,
            'download': download_func,
            'category': category,
            'requires_no_safe_search': requires_no_safe_search
        }
    
    def get(self, name):
        return self.handlers.get(name)

# Global registry instance
source_handler_registry = SourceHandlerRegistry()

# Register all available search handlers
print("🔧 Registering content source handlers...")

# Search Engines
source_handler_registry.register(
    'bing_images',
    search_func=lambda query, max_results, safe_search: enhanced_bing_search(query, max_results, safe_search),
    download_func=None,
    category='search',
    requires_no_safe_search=False
)

source_handler_registry.register(
    'yandex_images',
    search_func=lambda query, max_results, safe_search: enhanced_yandex_search(query, max_results, safe_search),
    download_func=None,
    category='search',
    requires_no_safe_search=False
)

# Image Galleries & Sharing
source_handler_registry.register(
    'imgur',
    search_func=lambda query, max_results, safe_search: enhanced_imgur_search(query, max_results, safe_search),
    download_func=None,
    category='gallery',
    requires_no_safe_search=False
)

source_handler_registry.register(
    'pinterest',
    search_func=lambda query, max_results, safe_search: enhanced_pinterest_search(query, max_results, safe_search),
    download_func=None,
    category='gallery',
    requires_no_safe_search=False
)

source_handler_registry.register(
    'flickr',
    search_func=lambda query, max_results, safe_search: enhanced_flickr_search(query, max_results, safe_search),
    download_func=None,
    category='gallery',
    requires_no_safe_search=False
)

# Stock Photo Sites
source_handler_registry.register(
    'unsplash',
    search_func=lambda query, max_results, safe_search: enhanced_unsplash_search(query, max_results, safe_search),
    download_func=None,
    category='stock',
    requires_no_safe_search=False
)

source_handler_registry.register(
    'pexels',
    search_func=lambda query, max_results, safe_search: enhanced_pexels_search(query, max_results, safe_search),
    download_func=None,
    category='stock',
    requires_no_safe_search=False
)

# Social Media - Basic Reddit Search
source_handler_registry.register(
    'reddit',
    search_func=lambda query, max_results, safe_search: enhanced_reddit_search(query, max_results, safe_search) if safe_search else enhanced_reddit_nsfw_search(query, max_results),
    download_func=None,
    category='social',
    requires_no_safe_search=False
)

source_handler_registry.register(
    'tumblr',
    search_func=lambda query, max_results, safe_search: enhanced_tumblr_search(query, max_results, safe_search),
    download_func=None,
    category='social',
    requires_no_safe_search=False
)

# Video Platforms
source_handler_registry.register(
    'youtube',
    search_func=lambda query, max_results, safe_search: enhanced_youtube_search(query, max_results),
    download_func=None,
    category='video',
    requires_no_safe_search=False
)

source_handler_registry.register(
    'videos',
    search_func=lambda query, max_results, safe_search: enhanced_video_search(query, max_results, safe_search),
    download_func=None,
    category='video',
    requires_no_safe_search=False
)

# Art Platforms (DeviantArt placeholder)
source_handler_registry.register(
    'deviantart',
    search_func=lambda query, max_results, safe_search: enhanced_deviantart_search(query, max_results, safe_search),
    download_func=None,
    category='art',
    requires_no_safe_search=False
)

# Adult Content (NSFW) - only when safe search is disabled
source_handler_registry.register(
    'reddit_nsfw',
    search_func=lambda query, max_results, safe_search: enhanced_reddit_nsfw_search(query, max_results),
    download_func=None,
    category='adult',
    requires_no_safe_search=True
)

source_handler_registry.register(
    'pornhub',
    search_func=lambda query, max_results, safe_search: enhanced_pornhub_search(query, max_results),
    download_func=None,
    category='adult',
    requires_no_safe_search=True
)

source_handler_registry.register(
    'xhamster',
    search_func=lambda query, max_results, safe_search: enhanced_xhamster_search(query, max_results),
    download_func=None,
    category='adult',
    requires_no_safe_search=True
)

source_handler_registry.register(
    'gelbooru',
    search_func=lambda query, max_results, safe_search: enhanced_gelbooru_search(query, max_results),
    download_func=None,
    category='adult',
    requires_no_safe_search=True
)

source_handler_registry.register(
    'rule34',
    search_func=lambda query, max_results, safe_search: enhanced_rule34_search(query, max_results),
    download_func=None,
    category='adult',
    requires_no_safe_search=True
)

source_handler_registry.register(
    'e621',
    search_func=lambda query, max_results, safe_search: enhanced_e621_search(query, max_results),
    download_func=None,
    category='adult',
    requires_no_safe_search=True
)

print(f"✅ Registered {len(source_handler_registry.handlers)} search handlers")

# Add missing search functions for sources that don't have implementations yet
def enhanced_reddit_search(query, max_results=50, safe_search=True):
    """Safe Reddit search (no NSFW content)"""
    print(f"🔍 Enhanced Reddit search for: {query} (Safe mode)")
    found_urls = set()
    
    try:
        import requests
        from urllib.parse import quote_plus
        import time
        import random
        
        headers = {
            'User-Agent': random.choice(get_multiple_user_agents()),
            'Accept': 'application/json'
        }
        
        # Safe subreddits for general search
        safe_subreddits = ['pics', 'funny', 'mildlyinteresting', 'earthporn', 'cityporn', 'spaceporn']
        
        session = requests.Session()
        session.headers.update(headers)
        
        # Search specific subreddits
        for subreddit in safe_subreddits[:3]:
            try:
                search_url = f"https://www.reddit.com/r/{subreddit}/search.json?q={quote_plus(query)}&restrict_sr=1&limit=25&sort=hot"
                time.sleep(random.uniform(1, 3))
                
                response = session.get(search_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'data' in data and 'children' in data['data']:
                        for post in data['data']['children']:
                            try:
                                post_data = post['data']
                                
                                # Skip NSFW content
                                if post_data.get('over_18', False):
                                    continue
                                
                                if 'url' in post_data:
                                    url = post_data['url']
                                    
                                    # Reddit-hosted images
                                    if 'i.redd.it' in url:
                                        found_urls.add(url)
                                    # Imgur links
                                    elif 'imgur.com' in url and any(ext in url.lower() for ext in ['.jpg', '.png', '.gif', '.webp']):
                                        found_urls.add(url)
                                    
                                    if len(found_urls) >= max_results:
                                        break
                            except Exception:
                                continue
                                
                if len(found_urls) >= max_results:
                    break
                    
            except Exception as e:
                print(f"❌ Reddit subreddit {subreddit} error: {str(e)}")
                continue
    
    except Exception as e:
        print(f"❌ Reddit search error: {str(e)}")
    
    print(f"✅ Reddit safe search found: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_deviantart_search(query, max_results=50, safe_search=True):
    """DeviantArt search placeholder"""
    print(f"🎨 DeviantArt search for: {query}")
    print("⚠️ DeviantArt search not fully implemented yet")
    return []

class ContentSource:
    """Represents a content source with detection and download capabilities (modular)"""
    def __init__(self, name, display_name, enabled=True, category="general", requires_no_safe_search=False):
        self.name = name
        self.display_name = display_name
        self.enabled = enabled
        self.category = category
        self.requires_no_safe_search = requires_no_safe_search
        self.detected_count = 0
        self.downloaded_count = 0
        self.failed_count = 0
        self.urls = []
        self.handler = source_handler_registry.get(name)
    
    def add_url(self, url):
        self.urls.append(url)
        self.detected_count += 1
    
    def record_download(self, success=True):
        if success:
            self.downloaded_count += 1
        else:
            self.failed_count += 1
    
    def get_stats(self):
        return {
            'name': self.name,
            'display_name': self.display_name,
            'enabled': self.enabled,
            'category': self.category,
            'requires_no_safe_search': self.requires_no_safe_search,
            'detected': self.detected_count,
            'downloaded': self.downloaded_count,
            'failed': self.failed_count,
            'success_rate': (self.downloaded_count / max(1, self.downloaded_count + self.failed_count)) * 100
        }
    
    def search(self, query, max_results=50, safe_search=True):
        if self.handler and self.handler['search']:
            try:
                urls = self.handler['search'](query, max_results, safe_search)
                for url in urls:
                    self.add_url(url)
                return urls
            except Exception as e:
                print(f"❌ Error in {self.name} search: {str(e)}")
                return []
        else:
            print(f"⚠️ No search handler registered for source: {self.name}")
            return []

def get_content_sources():
    """
    Get all available content sources with their configurations
    """
    return {
        # Social Media Platforms
        'instagram': ContentSource('instagram', 'Instagram', True, 'social'),
        'twitter': ContentSource('twitter', 'Twitter/X', True, 'social'),
        'tiktok': ContentSource('tiktok', 'TikTok', True, 'social'),
        'facebook': ContentSource('facebook', 'Facebook', True, 'social'),
        'snapchat': ContentSource('snapchat', 'Snapchat', True, 'social'),
        'telegram': ContentSource('telegram', 'Telegram', True, 'social'),
        'discord': ContentSource('discord', 'Discord', True, 'social'),
        'reddit': ContentSource('reddit', 'Reddit', True, 'social'),
        'tumblr': ContentSource('tumblr', 'Tumblr', True, 'social'),
        'linkedin': ContentSource('linkedin', 'LinkedIn', True, 'social'),
        'mastodon': ContentSource('mastodon', 'Mastodon', True, 'social'),
        'threads': ContentSource('threads', 'Threads', True, 'social'),
        
        # Video Platforms
        'videos': ContentSource('videos', 'Video Search (All Platforms)', True, 'video'),  # Generic video search
        'youtube': ContentSource('youtube', 'YouTube', True, 'video'),
        'vimeo': ContentSource('vimeo', 'Vimeo', True, 'video'),
        'dailymotion': ContentSource('dailymotion', 'Dailymotion', True, 'video'),
        'twitch': ContentSource('twitch', 'Twitch', True, 'video'),
        'kick': ContentSource('kick', 'Kick', True, 'video'),
        'rumble': ContentSource('rumble', 'Rumble', True, 'video'),
        'bitchute': ContentSource('bitchute', 'BitChute', True, 'video'),
        'odysee': ContentSource('odysee', 'Odysee', True, 'video'),
        'peertube': ContentSource('peertube', 'PeerTube', True, 'video'),
        'streamable': ContentSource('streamable', 'Streamable', True, 'video'),
        'gfycat': ContentSource('gfycat', 'Gfycat', True, 'video'),
        'redgifs': ContentSource('redgifs', 'RedGIFs', True, 'video'),
        
        # Search Engines & Image Sources
        'bing_images': ContentSource('bing_images', 'Bing Images', True, 'search'),
        'google_images': ContentSource('google_images', 'Google Images', True, 'search'),
        'yandex_images': ContentSource('yandex_images', 'Yandex Images', True, 'search'),
        'baidu_images': ContentSource('baidu_images', 'Baidu Images', True, 'search'),
        'duckduckgo': ContentSource('duckduckgo', 'DuckDuckGo Images', True, 'search'),
        
        # Art & Creative Platforms
        'deviantart': ContentSource('deviantart', 'DeviantArt', True, 'art'),
        'artstation': ContentSource('artstation', 'ArtStation', True, 'art'),
        'behance': ContentSource('behance', 'Behance', True, 'art'),
        'dribbble': ContentSource('dribbble', 'Dribbble', True, 'art'),
        'pixiv': ContentSource('pixiv', 'Pixiv', True, 'art'),
        'newgrounds': ContentSource('newgrounds', 'Newgrounds', True, 'art'),
        'furaffinity': ContentSource('furaffinity', 'FurAffinity', True, 'art'),
        
        # Image Galleries & Sharing
        'imgur': ContentSource('imgur', 'Imgur', True, 'gallery'),
        'pinterest': ContentSource('pinterest', 'Pinterest', True, 'gallery'),
        'flickr': ContentSource('flickr', 'Flickr', True, 'gallery'),
        '500px': ContentSource('500px', '500px', True, 'gallery'),
        'photobucket': ContentSource('photobucket', 'Photobucket', True, 'gallery'),
        'imageshack': ContentSource('imageshack', 'ImageShack', True, 'gallery'),
        'postimage': ContentSource('postimage', 'PostImage', True, 'gallery'),
        
        # Stock Photo Sites
        'unsplash': ContentSource('unsplash', 'Unsplash', True, 'stock'),
        'pexels': ContentSource('pexels', 'Pexels', True, 'stock'),
        'pixabay': ContentSource('pixabay', 'Pixabay', True, 'stock'),
        'shutterstock': ContentSource('shutterstock', 'Shutterstock', True, 'stock'),
        'getty_images': ContentSource('getty_images', 'Getty Images', True, 'stock'),
        'adobe_stock': ContentSource('adobe_stock', 'Adobe Stock', True, 'stock'),
        
        # News & Media
        'cnn': ContentSource('cnn', 'CNN', True, 'news'),
        'bbc': ContentSource('bbc', 'BBC', True, 'news'),
        'reuters': ContentSource('reuters', 'Reuters', True, 'news'),
        'associated_press': ContentSource('associated_press', 'Associated Press', True, 'news'),
        
        # Direct Sources
        'direct_links': ContentSource('direct_links', 'Direct Image Links', True, 'direct'),
        'file_sharing': ContentSource('file_sharing', 'File Sharing Sites', True, 'direct'),
        
        # Adult content sources (requires safe search disabled)
        'reddit_nsfw': ContentSource('reddit_nsfw', 'Reddit NSFW', True, 'adult', True),
        'reddit_gonewild': ContentSource('reddit_gonewild', 'Reddit GoneWild', True, 'adult', True),
        'deviantart_mature': ContentSource('deviantart_mature', 'DeviantArt Mature', True, 'adult', True),
        'tumblr_nsfw': ContentSource('tumblr_nsfw', 'Tumblr NSFW', True, 'adult', True),
        'xhamster': ContentSource('xhamster', 'xHamster', True, 'adult', True),
        'pornhub': ContentSource('pornhub', 'PornHub', True, 'adult', True),
        'xvideos': ContentSource('xvideos', 'XVideos', True, 'adult', True),
        'motherless': ContentSource('motherless', 'Motherless', True, 'adult', True),
        'imagefap': ContentSource('imagefap', 'ImageFap', True, 'adult', True),
        'gelbooru': ContentSource('gelbooru', 'Gelbooru', True, 'adult', True),
        'rule34': ContentSource('rule34', 'Rule34', True, 'adult', True),
        'e621': ContentSource('e621', 'e621', True, 'adult', True),
        'danbooru': ContentSource('danbooru', 'Danbooru', True, 'adult', True),
        'sankaku': ContentSource('sankaku', 'Sankaku Complex', True, 'adult', True),
        'nhentai': ContentSource('nhentai', 'nhentai', True, 'adult', True),
        'hentai_foundry': ContentSource('hentai_foundry', 'Hentai Foundry', True, 'adult', True),
        'redtube': ContentSource('redtube', 'RedTube', True, 'adult', True),
        'youporn': ContentSource('youporn', 'YouPorn', True, 'adult', True),
        'spankbang': ContentSource('spankbang', 'SpankBang', True, 'adult', True),
        'tube8': ContentSource('tube8', 'Tube8', True, 'adult', True),
        'beeg': ContentSource('beeg', 'Beeg', True, 'adult', True),
        'chaturbate': ContentSource('chaturbate', 'Chaturbate', True, 'adult', True),
        'onlyfans': ContentSource('onlyfans', 'OnlyFans', True, 'adult', True),
    }

def comprehensive_multi_source_scrape(query, search_type='comprehensive', enabled_sources=None, max_content_per_source=10, output_dir=None, progress_callback=None, safe_search=True):
    """
    Scrape content from multiple sources with detailed progress tracking
    
    Args:
        query: Search query
        search_type: Type of search ('comprehensive', 'images', 'videos')
        enabled_sources: List of enabled source names
        max_content_per_source: Max content per source
        output_dir: Output directory (None for database-only storage)
        progress_callback: Progress callback function
        safe_search: Filter adult content
    """
    print(f"\n🔍 Starting {search_type} search for: '{query}'")
    print(f"📊 Max content per source: {max_content_per_source}")
    print(f"🔒 Safe search: {'ON' if safe_search else 'OFF'}")
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Get all available sources
    all_sources = get_content_sources()
    
    # Filter sources based on safe search
    if safe_search:
        all_sources = {name: source for name, source in all_sources.items() 
                      if not source.requires_no_safe_search}
    
    # Filter enabled sources
    if enabled_sources:
        sources_to_use = {name: source for name, source in all_sources.items() 
                         if name in enabled_sources and source.enabled}
    else:
        sources_to_use = {name: source for name, source in all_sources.items() 
                         if source.enabled}
    
    print(f"📦 Using {len(sources_to_use)} sources")
    
    # Results tracking
    results = {
        'total_detected': 0,
        'total_downloaded': 0,
        'total_images': 0,
        'total_videos': 0,
        'sources': {}
    }
    
    # If search type is "videos", always prioritize video sources
    if search_type == 'videos':
        if progress_callback:
            progress_callback("🎬 Searching for videos only...", 5, 0, 0, 0)
        
        try:
            # Search for videos using enhanced video search
            video_urls = enhanced_video_search(query, max_results=max_content_per_source * 3, safe_search=safe_search)
            if video_urls:
                # Create temporary directory if output_dir is None
                temp_video_dir = None
                video_output_dir = output_dir
                
                if video_output_dir is None:
                    temp_video_dir = tempfile.mkdtemp(prefix="videos_")
                    video_output_dir = temp_video_dir
                
                video_results = download_videos_with_ytdlp(
                    video_urls[:max_content_per_source * 2],  # Download more videos
                    video_output_dir,
                    progress_callback
                )
                results['total_downloaded'] += video_results.get('downloaded', 0)
                results['total_videos'] += video_results.get('videos', 0)
                results['total_detected'] += len(video_urls)
                results['sources']['video_search'] = {
                    'detected': len(video_urls),
                    'downloaded': video_results.get('downloaded', 0),
                    'failed': video_results.get('failed', 0),
                    'images': 0,
                    'videos': video_results.get('videos', 0)
                }
                
                # Clean up temporary directory if created
                if temp_video_dir and os.path.exists(temp_video_dir):
                    try:
                        shutil.rmtree(temp_video_dir)
                    except Exception as e:
                        print(f"⚠️ Failed to clean up video temp directory: {e}")
                
                if progress_callback:
                    progress_callback(
                        f"✅ Downloaded {video_results['videos']} videos",
                        30,
                        results['total_downloaded'], 
                        results['total_images'], 
                        results['total_videos']
                    )
        except Exception as e:
            print(f"❌ Video search error: {str(e)}")
        
        # For videos only, skip regular source searching
        if results['total_downloaded'] > 0:
            if progress_callback:
                progress_callback(
                    f"✅ Video search complete: {results['total_videos']} videos downloaded", 
                    100, 
                    results['total_downloaded'], 
                    results['total_images'], 
                    results['total_videos']
                )
            return results
        else:
            # If no videos found, continue with regular sources but filter for video content
            if progress_callback:
                progress_callback("⚠️ No direct videos found, searching other sources...", 35, 0, 0, 0)
    
    # Check if this is primarily a video search (either by type or query)
    is_video_search = search_type == 'videos' or any(word in query.lower() for word in ['video', 'movie', 'clip', 'footage', 'tutorial'])
    
    # If it's a video search but not "videos only", still add video sources
    if is_video_search and search_type != 'images':
        if progress_callback:
            progress_callback("🎬 Searching for videos...", 5, 0, 0, 0)
        
        try:
            video_urls = enhanced_video_search(query, max_results=max_content_per_source * 2, safe_search=safe_search)
            if video_urls:
                # Create temporary directory if output_dir is None
                temp_video_dir = None
                video_output_dir = output_dir
                
                if video_output_dir is None:
                    temp_video_dir = tempfile.mkdtemp(prefix="videos_")
                    video_output_dir = temp_video_dir
                
                video_results = download_videos_with_ytdlp(
                    video_urls[:max_content_per_source], 
                    video_output_dir,
                    progress_callback
                )
                results['total_downloaded'] += video_results.get('downloaded', 0)
                results['total_videos'] += video_results.get('videos', 0)
                
                # Clean up temporary directory if created
                if temp_video_dir and os.path.exists(temp_video_dir):
                    try:
                        shutil.rmtree(temp_video_dir)
                    except Exception as e:
                        print(f"⚠️ Failed to clean up video temp directory: {e}")
                
                if progress_callback:
                    progress_callback(
                        f"✅ Downloaded {video_results['videos']} videos",
                        20,
                        results['total_downloaded'], 
                        results['total_images'], 
                        results['total_videos']
                    )
        except Exception as e:
            print(f"❌ Video search error: {str(e)}")
    
    # Continue with regular source searching
    sources_processed = 0
    
    for source_name, source_obj in sources_to_use.items():
        # Skip non-video sources if search type is "videos"
        if search_type == 'videos' and source_name in ['imgur', 'flickr', 'unsplash', 'pexels', 'pinterest']:
            continue
            
        # Skip video sources if search type is "images"
        if search_type == 'images' and source_name in ['youtube']:
            continue
        
        sources_processed += 1
        progress_percent = 20 + int((sources_processed / len(sources_to_use)) * 70)
        
        if progress_callback:
            progress_callback(f"🔍 Searching {source_obj.display_name}...", 
                            progress_percent - 5, 
                            results['total_downloaded'], 
                            results['total_images'], 
                            results['total_videos'])
        
        try:
            # Search for content URLs
            urls = source_obj.search(query, max_results=max_content_per_source * 2, safe_search=safe_search)
            
            if urls:
                source_obj.urls = urls
                results['total_detected'] += len(urls)
                
                # Create temporary directory if output_dir is None
                temp_source_dir = None
                source_output_dir = output_dir
                
                if source_output_dir is None:
                    temp_source_dir = tempfile.mkdtemp(prefix=f"{source_name}_")
                    source_output_dir = temp_source_dir
                
                # Download content from URLs
                download_results = download_urls_from_source(
                    urls, 
                    source_output_dir, 
                    source_obj, 
                    progress_callback,
                    max_downloads=max_content_per_source,
                    filter_type=search_type  # Pass filter type to download function
                )
                
                results['total_downloaded'] += download_results['downloaded']
                results['total_images'] += download_results['images']
                results['total_videos'] += download_results['videos']
                results['sources'][source_name] = {
                    'detected': len(urls),
                    'downloaded': download_results['downloaded'],
                    'failed': download_results['failed'],
                    'images': download_results['images'],
                    'videos': download_results['videos']
                }
                
                # Clean up temporary directory if created
                if temp_source_dir and os.path.exists(temp_source_dir):
                    try:
                        shutil.rmtree(temp_source_dir)
                    except Exception as e:
                        print(f"⚠️ Failed to clean up temp directory for {source_name}: {e}")
                
                print(f"✅ {source_obj.display_name}: {len(urls)} URLs found")
            else:
                print(f"⚠️ {source_obj.display_name}: No results")
                
        except Exception as e:
            print(f"❌ Error with {source_obj.display_name}: {str(e)}")
            continue
        
        if progress_callback:
            progress_callback(f"✅ Processed {source_obj.display_name}", 
                            progress_percent, 
                            results['total_downloaded'], 
                            results['total_images'], 
                            results['total_videos'])
    
    # Final report
    if progress_callback:
        progress_callback(
            f"✅ {search_type.capitalize()} search complete: {results['total_downloaded']} files downloaded", 
            100, 
            results['total_downloaded'], 
            results['total_images'], 
            results['total_videos']
        )
    
    print(f"\n📊 === FINAL RESULTS ===")
    print(f"🔍 Total URLs detected: {results['total_detected']}")
    print(f"✅ Total downloaded: {results['total_downloaded']}")
    print(f"🖼️ Images: {results['total_images']}")
    print(f"🎬 Videos: {results['total_videos']}")
    print(f"📦 Sources used: {len(sources_to_use)}")
    
    return results

def enhanced_instagram_scrape(username_or_url, max_content=10, output_dir=None, progress_callback=None):
    """
    Enhanced Instagram scraping with database storage support
    """
    # Create temporary directory if output_dir is None
    temp_dir = None
    if output_dir is None:
        temp_dir = tempfile.mkdtemp(prefix="instagram_")
        output_dir = temp_dir
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📸 === ENHANCED INSTAGRAM SCRAPING (FIXED) ===")
    print(f"🎯 Target: {username_or_url}")
    print(f"📊 Max content: {max_content}")
    
    # Parse username from URL if needed
    if 'instagram.com' in username_or_url:
        username = username_or_url.split('/')[-2] if username_or_url.endswith('/') else username_or_url.split('/')[-1]
    else:
        username = username_or_url.replace('@', '')
    
    print(f"📁 Output: {output_dir}")
    
    downloaded_count = 0
    image_count = 0
    video_count = 0
    methods_tried = []
    
    # Method 1: FIXED gallery-dl with improved configuration
    try:
        if progress_callback:
            progress_callback("🔄 Instagram Method 1: Enhanced gallery-dl...", 10, downloaded_count, image_count, video_count)
            
        print(f"🔄 Method 1: Enhanced gallery-dl with better authentication...")
        methods_tried.append("gallery-dl-enhanced")
        
        cmd = [
            'python', '-m', 'gallery_dl',
            '--cookies-from-browser', 'chrome',
            '--sleep', '15',  # Increased sleep to avoid rate limits
            '--sleep-request', '8',  # More conservative delays
            '--retries', '5',  # More retries for reliability
            '--write-metadata',
            '--write-info-json',
            '--dest', output_dir,
            '--config', '-',  # Use stdin config for better control
            f'https://www.instagram.com/{username}/'
        ]
        
        # Create enhanced config for gallery-dl
        gallery_config = {
            "extractor": {
                "instagram": {
                    "sleep": 15,
                    "sleep-request": 8,
                    "include": "posts",
                    "videos": True,
                    "metadata": True
                }
            }
        }
        
        result = subprocess.run(cmd, input=json.dumps(gallery_config), 
                               capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            # Count and categorize files
            if os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, file)
                    if os.path.isfile(file_path) and os.path.getsize(file_path) > 5000:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            image_count += 1
                        elif file.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                            video_count += 1
                        downloaded_count += 1
                        
                        if progress_callback:
                            try:
                                progress_callback(f"✅ Downloaded: {file}", 50, downloaded_count, image_count, video_count, file_path)
                            except Exception as e:
                                print(f"⚠️ Progress callback error: {str(e)}")
            
            if downloaded_count > 0:
                if progress_callback:
                    try:
                        progress_callback(f"✅ Gallery-dl success: {downloaded_count} files", 100, downloaded_count, image_count, video_count)
                    except Exception as e:
                        print(f"⚠️ Progress callback error: {str(e)}")
                print(f"✅ Gallery-dl success: {downloaded_count} files")
                return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}
        
        print(f"❌ Gallery-dl failed: {result.stderr[:200]}...")
        
    except Exception as e:
        print(f"❌ Gallery-dl error: {str(e)}")
    
    # Method 2: IMPROVED yt-dlp with better configuration
    try:
        if progress_callback:
            progress_callback("🔄 Instagram Method 2: Improved yt-dlp...", 30, downloaded_count, image_count, video_count)
            
        print(f"🔄 Method 2: Improved yt-dlp with enhanced settings...")
        methods_tried.append("yt-dlp-improved")
        
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(uploader)s_%(id)s.%(ext)s'),
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writedescription': True,
            'writeinfojson': True,
            'writethumbnail': True,
            'max_downloads': max_content,
            'ignoreerrors': True,
            'sleep_interval': 15,  # Increased delays
            'max_sleep_interval': 30,
            'cookiesfrombrowser': 'chrome',  # Try Chrome browser cookies
            'extractor_args': {
                'instagram': {
                    'comment_count': 0,  # Skip comments for faster extraction
                    'max_comments': 0
                }
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([f'https://www.instagram.com/{username}/'])
                
                # Count new files
                new_image_count = 0
                new_video_count = 0
                new_downloaded = 0
                
                if os.path.exists(output_dir):
                    for file in os.listdir(output_dir):
                        file_path = os.path.join(output_dir, file)
                        if os.path.isfile(file_path) and os.path.getsize(file_path) > 5000:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                                new_image_count += 1
                            elif file.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                                new_video_count += 1
                            new_downloaded += 1
                            
                            if progress_callback:
                                progress_callback(f"✅ Downloaded: {file}", 70, new_downloaded, new_image_count, new_video_count, file_path)
                
                if new_downloaded > downloaded_count:
                    downloaded_count = new_downloaded
                    image_count = new_image_count
                    video_count = new_video_count
                    
                    if progress_callback:
                        progress_callback(f"✅ yt-dlp success: {downloaded_count} files", 100, downloaded_count, image_count, video_count)
                    print(f"✅ yt-dlp success: {downloaded_count} files")
                    return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}
                    
            except Exception as e:
                print(f"❌ yt-dlp download error: {str(e)}")
        
    except Exception as e:
        print(f"❌ yt-dlp setup error: {str(e)}")
    
    # Method 3: NEW - Direct Instagram API simulation
    try:
        if progress_callback:
            progress_callback("🔄 Instagram Method 3: API simulation...", 50, downloaded_count, image_count, video_count)
            
        print(f"🔄 Method 3: Direct Instagram API simulation...")
        methods_tried.append("api-simulation")
        
        headers = {
            'User-Agent': 'Instagram 276.0.0.18.119 Android (29/10; 480dpi; 1080x2340; samsung; SM-G973F)',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'X-IG-Capabilities': '3brTvwE=',
            'X-IG-Connection-Type': 'WIFI',
            'X-IG-Bandwidth-Speed-KBPS': '-1.000',
            'X-IG-Bandwidth-TotalBytes-B': '0',
            'X-IG-Bandwidth-TotalTime-MS': '0',
            'X-Bloks-Version-Id': 'f1e4a8b2a4a8b2a4a8b2a4a8b2a4a8b2a4a8b2a4',
            'X-IG-Connection-Speed': '-1kbps',
            'X-IG-App-ID': '567067343352427',
        }
        
        # Try to get user info via web interface
        profile_url = f'https://www.instagram.com/{username}/?__a=1&__d=dis'
        
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(profile_url, timeout=30)
        
        if response.status_code == 200:
            # Parse response for image URLs
            try:
                data = response.json()
                # Extract media URLs from response
                # This is a simplified example - real implementation would be more complex
                media_found = 0
                print(f"✅ API simulation partially successful")
                
            except json.JSONDecodeError:
                # Try HTML parsing instead
                soup = BeautifulSoup(response.text, 'html.parser')
                script_tags = soup.find_all('script', {'type': 'text/javascript'})
                
                for script in script_tags:
                    if script.string and 'window._sharedData' in script.string:
                        # Extract JSON data from script
                        json_start = script.string.find('{')
                        json_end = script.string.rfind('}') + 1
                        if json_start != -1 and json_end != -1:
                            try:
                                shared_data = json.loads(script.string[json_start:json_end])
                                print(f"✅ Found shared data structure")
                                break
                            except:
                                continue
        
    except Exception as e:
        print(f"❌ API simulation error: {str(e)}")
    
    if progress_callback:
        progress_callback(f"⚠️ Instagram scraping completed with limited success", 100, downloaded_count, image_count, video_count)
    
    print(f"📊 Instagram scraping complete")
    print(f"🔧 Methods tried: {', '.join(methods_tried)}")
    print(f"📁 Files downloaded: {downloaded_count} (Images: {image_count}, Videos: {video_count})")
    
    # Clean up temporary directory if used
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"⚠️ Failed to clean up temp directory: {e}")
    
    return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}

def enhanced_twitter_scrape(username_or_url, max_content=10, output_dir=None, progress_callback=None):
    """
    Enhanced Twitter/X scraping with database storage support
    """
    # Create temporary directory if output_dir is None
    temp_dir = None
    if output_dir is None:
        temp_dir = tempfile.mkdtemp(prefix="twitter_")
        output_dir = temp_dir
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🐦 === ENHANCED TWITTER SCRAPING (FIXED) ===")
    
    # Parse username
    if 'twitter.com' in username_or_url or 'x.com' in username_or_url:
        username = username_or_url.split('/')[-1]
    else:
        username = username_or_url.replace('@', '')
    
    print(f"📁 Output: {output_dir}")
    
    downloaded_count = 0
    image_count = 0
    video_count = 0
    
    # Method 1: FIXED gallery-dl with enhanced Twitter support
    try:
        if progress_callback:
            progress_callback("🔄 Twitter Method 1: Enhanced gallery-dl...", 20, downloaded_count, image_count, video_count)
            
        print(f"🔄 Twitter Method 1: Enhanced gallery-dl...")
        
        cmd = [
            'python', '-m', 'gallery_dl',
            '--cookies-from-browser', 'chrome',
            '--sleep', '20',  # Longer delays for Twitter
            '--sleep-request', '10',
            '--retries', '5',
            '--write-metadata',
            '--dest', output_dir,
            f'https://twitter.com/{username}/media'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        if result.returncode == 0:
            if os.path.exists(output_dir):
                for file in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, file)
                    if os.path.isfile(file_path) and os.path.getsize(file_path) > 5000:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            image_count += 1
                        elif file.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                            video_count += 1
                        downloaded_count += 1
                        
                        if progress_callback:
                            progress_callback(f"✅ Downloaded: {file}", 60, downloaded_count, image_count, video_count, file_path)
            
            if downloaded_count > 0:
                if progress_callback:
                    progress_callback(f"✅ Twitter gallery-dl success: {downloaded_count} files", 100, downloaded_count, image_count, video_count)
                print(f"✅ Gallery-dl success: {downloaded_count} files")
                return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}
        
        print(f"❌ Gallery-dl failed: {result.stderr[:200]}...")
        
    except Exception as e:
        print(f"❌ Gallery-dl error: {str(e)}")
    
    # Method 2: IMPROVED yt-dlp for Twitter
    try:
        if progress_callback:
            progress_callback("🔄 Twitter Method 2: Improved yt-dlp...", 40, downloaded_count, image_count, video_count)
            
        print(f"🔄 Twitter Method 2: Improved yt-dlp...")
        
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(uploader)s_%(id)s.%(ext)s'),
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writedescription': True,
            'writeinfojson': True,
            'writethumbnail': True,
            'max_downloads': max_content,
            'ignoreerrors': True,
            'sleep_interval': 20,
            'max_sleep_interval': 40,
            'cookiesfrombrowser': 'chrome',  # Try Chrome browser cookies
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([f'https://twitter.com/{username}/media'])
                
                new_downloaded = 0
                new_image_count = 0
                new_video_count = 0
                
                if os.path.exists(output_dir):
                    for file in os.listdir(output_dir):
                        file_path = os.path.join(output_dir, file)
                        if os.path.isfile(file_path) and os.path.getsize(file_path) > 5000:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                                new_image_count += 1
                            elif file.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                                new_video_count += 1
                            new_downloaded += 1
                            
                            if progress_callback:
                                progress_callback(f"✅ Downloaded: {file}", 80, new_downloaded, new_image_count, new_video_count, file_path)
                
                if new_downloaded > downloaded_count:
                    downloaded_count = new_downloaded
                    image_count = new_image_count
                    video_count = new_video_count
                    
                    if progress_callback:
                        progress_callback(f"✅ Twitter yt-dlp success: {downloaded_count} files", 100, downloaded_count, image_count, video_count)
                    print(f"✅ yt-dlp success: {downloaded_count} files")
                    return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}
                    
            except Exception as e:
                print(f"❌ yt-dlp download error: {str(e)}")
        
    except Exception as e:
        print(f"❌ yt-dlp setup error: {str(e)}")
    
    if progress_callback:
        progress_callback(f"⚠️ Twitter scraping completed with limited success", 100, downloaded_count, image_count, video_count)
    
    print(f"📊 Twitter scraping complete")
    print(f"📁 Files downloaded: {downloaded_count} (Images: {image_count}, Videos: {video_count})")
    
    # Clean up temporary directory if used
    if temp_dir and os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"⚠️ Failed to clean up temp directory: {e}")
    
    return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}

def enhanced_tiktok_scrape(username_or_url, max_content=10, output_dir="downloads"):
    """Enhanced TikTok scraping"""
    print(f"🎵 === ENHANCED TIKTOK SCRAPING ===")
    
    # Parse username
    if 'tiktok.com' in username_or_url:
        username = username_or_url.split('@')[-1].split('/')[0]
    else:
        username = username_or_url.replace('@', '')
    
    output_path = os.path.join(output_dir, 'tiktok', username)
    os.makedirs(output_path, exist_ok=True)
    
    downloaded_count = 0
    
    # Method 1: yt-dlp for TikTok
    try:
        print(f"🔄 TikTok Method 1: yt-dlp...")
        
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(uploader)s_%(id)s.%(ext)s'),
            'max_downloads': max_content,
            'ignoreerrors': True,
            'sleep_interval': 5,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([f'https://www.tiktok.com/@{username}'])
                
                files = [f for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f))]
                downloaded_count = len([f for f in files if os.path.getsize(os.path.join(output_path, f)) > 10000])
                
                if downloaded_count > 0:
                    print(f"✅ TikTok yt-dlp success: {downloaded_count} files")
                    return downloaded_count
                    
            except Exception as e:
                print(f"❌ TikTok yt-dlp download error: {str(e)}")
        
    except Exception as e:
        print(f"❌ TikTok yt-dlp setup error: {str(e)}")
    
    # Method 2: gallery-dl for TikTok
    try:
        print(f"🔄 TikTok Method 2: Gallery-dl...")
        
        cmd = [
            'python', '-m', 'gallery_dl',
            '--sleep', '10',
            '--retries', '3',
            '--dest', output_path,
            f'https://www.tiktok.com/@{username}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            files = [f for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f))]
            new_count = len([f for f in files if os.path.getsize(os.path.join(output_path, f)) > 10000])
            
            if new_count > downloaded_count:
                downloaded_count = new_count
                print(f"✅ TikTok gallery-dl success: {downloaded_count} files")
                return downloaded_count
        
    except Exception as e:
        print(f"❌ TikTok gallery-dl error: {str(e)}")
    
    return downloaded_count

def enhanced_reddit_nsfw_search(query, max_results=50, progress_callback=None):
    """ENHANCED: Reddit NSFW search with comprehensive adult subreddit coverage"""
    if progress_callback:
        progress_callback(f"🔴 Starting comprehensive Reddit NSFW search for: {query}", 0, 0, 0, 0)
    
    print(f"🔴 Enhanced Reddit NSFW search for: {query}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    # EXPANDED NSFW subreddit list - comprehensive adult content
    nsfw_subreddits = [
        # General NSFW
        'gonewild', 'nsfw', 'RealGirls', 'Amateur', 'collegesluts', 
        'Nude_Selfie', 'Nudes', 'pussy', 'boobs', 'ass', 'BustyPetite',
        'petite', 'adorableporn', 'LegalTeens', 'homemadexxx', 'slutwife',
        'nsfw_gifs', 'porn', 'sex', 'milf', 'pawg', 'thick', 'curvy',
        
        # Specific fetishes and categories
        'BBWGW', 'BBW', 'gonewildcurvy', 'chubby', 'voluptuous',
        'BigBoobsGW', 'hugeboobs', 'Stacked', 'burstingout',
        'AssholeBehindThong', 'thongs', 'UnderwearGW', 'lingerie',
        'AmateurPorn', 'DirtySnapchat', 'snapchat_sluts', 'Slut',
        'cumsluts', 'GirlsFinishingTheJob', 'facials', 'amateurcumsluts',
        
        # Lesbian content
        'dykesgonewild', 'gonewildlesbian', 'LesbianPOV', 'girlsway',
        
        # Interactive/Chat
        'dirtykikpals', 'dirtyr4r', 'RandomActsOfBlowJob', 'RandomActsOfMuffDive',
        
        # International
        'AsiansGoneWild', 'indiansgonewild', 'LatinasGW', 'EuroGirls',
        
        # Age categories (18+ only)
        'LegalCollegeGirls', 'YoungAdultPorn', 'CollegeAmateurs'
    ]
    
    # Multiple search approaches
    search_urls = []
    
    # 1. Direct subreddit search with query
    for subreddit in nsfw_subreddits[:15]:  # Top 15 subreddits
        search_urls.append(f"https://www.reddit.com/r/{subreddit}/search.json?q={quote_plus(query)}&restrict_sr=1&limit=25&sort=hot&include_over_18=on")
    
    # 2. General NSFW search across all of Reddit
    search_urls.append(f"https://www.reddit.com/search.json?q={quote_plus(query)}+nsfw%3A1&limit=50&sort=hot&include_over_18=on")
    
    # 3. Hot posts from top NSFW subreddits (recent content)
    for subreddit in ['gonewild', 'RealGirls', 'Amateur', 'nsfw', 'collegesluts']:
        search_urls.append(f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25&include_over_18=on")
    
    # 4. New posts for fresh content
    for subreddit in ['gonewild', 'Amateur', 'RealGirls']:
        search_urls.append(f"https://www.reddit.com/r/{subreddit}/new.json?limit=25&include_over_18=on")
    
    session = requests.Session()
    session.cookies.set("over18", "1", domain="reddit.com")  # Bypass age gate
    session.cookies.set("over18", "1", domain=".reddit.com")  # Wildcard domain
    
    progress_step = 100 / len(search_urls)
    current_progress = 0
    
    for i, search_url in enumerate(search_urls):
        try:
            current_progress = i * progress_step
            if progress_callback:
                progress_callback(f"🔍 Searching Reddit NSFW source {i+1}/{len(search_urls)}", int(current_progress), len(found_urls), 0, 0)
            
            time.sleep(random.uniform(2, 4))  # Conservative delay
            
            response = session.get(search_url, headers=headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and 'children' in data['data']:
                    for post in data['data']['children']:
                        try:
                            post_data = post['data']
                            
                            # Skip non-NSFW content
                            if not post_data.get('over_18', False):
                                continue
                            
                            # Get direct image URLs
                            if 'url' in post_data:
                                url = post_data['url']
                                
                                # Reddit-hosted images (i.redd.it)
                                if 'i.redd.it' in url:
                                    found_urls.add(url)
                                
                                # Reddit galleries
                                elif 'reddit.com/gallery/' in url:
                                    # Try to extract individual images from gallery
                                    if 'media_metadata' in post_data:
                                        for media_id, media_info in post_data['media_metadata'].items():
                                            if 's' in media_info and 'u' in media_info['s']:
                                                img_url = media_info['s']['u'].replace('&amp;', '&')
                                                found_urls.add(img_url)
                                
                                # Imgur links
                                elif 'imgur.com' in url:
                                    if not url.endswith(('.jpg', '.png', '.gif', '.webp')):
                                        # Convert imgur gallery to direct image
                                        img_id = url.split('/')[-1]
                                        # Try both extensions
                                        found_urls.add(f"https://i.imgur.com/{img_id}.jpg")
                                        found_urls.add(f"https://i.imgur.com/{img_id}.png")
                                    else:
                                        found_urls.add(url)
                                
                                # Redgifs (adult GIFs)
                                elif 'redgifs.com' in url:
                                    found_urls.add(url)
                                
                                # Other direct image URLs
                                elif any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                                    found_urls.add(url)
                                
                            # Check for preview images
                            if 'preview' in post_data and 'images' in post_data['preview']:
                                for preview in post_data['preview']['images']:
                                    if 'source' in preview and 'url' in preview['source']:
                                        preview_url = preview['source']['url'].replace('&amp;', '&')
                                        found_urls.add(preview_url)
                                        
                        except Exception as e:
                            continue
                            
            elif response.status_code == 429:
                print(f"⚠️ Rate limited on {search_url}, waiting...")
                time.sleep(10)
                continue
                
        except Exception as e:
            print(f"❌ Error searching {search_url}: {str(e)}")
            continue
    
    if progress_callback:
        progress_callback(f"✅ Reddit NSFW search complete: {len(found_urls)} URLs found", 100, len(found_urls), 0, 0)
    
    print(f"✅ Reddit NSFW found: {len(found_urls)} image URLs")
    return list(found_urls)

def enhanced_pornhub_search(query, max_results=50, progress_callback=None):
    """
    Enhanced PornHub search with better URL handling
    """
    if progress_callback:
        progress_callback(f"🔞 Searching PornHub for: {query}", 0, 0, 0, 0)
    
    print(f"🔞 Enhanced PornHub search for: {query}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://www.pornhub.com/',
        'Cookie': 'age_verified=1; platform=pc'  # Age verification
    }
    
    try:
        # Multiple search strategies for PornHub
        search_strategies = [
            f"https://www.pornhub.com/video/search?search={requests.utils.quote(query)}",
            f"https://www.pornhub.com/photos/search?search={requests.utils.quote(query)}",
            f"https://www.pornhub.com/albums/search?search={requests.utils.quote(query)}"
        ]
        
        for search_url in search_strategies:
            try:
                response = requests.get(search_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find video thumbnails and preview images
                    content_selectors = [
                        'img.thumb',               # Video thumbnails
                        'img[data-thumb_url]',     # Thumbnail data
                        'img[data-src]',           # Lazy loaded images
                        'div.phimage img',         # Photo images
                        'div.videoPreviewBg img',  # Preview backgrounds
                        'a.linkVideoThumb img'     # Linked video thumbnails
                    ]
                    
                    for selector in content_selectors:
                        imgs = soup.select(selector)
                        for img in imgs:
                            img_url = (img.get('data-thumb_url') or 
                                     img.get('data-src') or 
                                     img.get('src') or
                                     img.get('data-original'))
                            
                            if img_url:
                                # Ensure full URL
                                if img_url.startswith('//'):
                                    img_url = 'https:' + img_url
                                elif img_url.startswith('/'):
                                    img_url = 'https://www.pornhub.com' + img_url
                                
                                # Filter for content images
                                if img_url.startswith('http') and any(
                                    indicator in img_url.lower() for indicator in [
                                        'thumb', 'preview', 'image', 'photo', 'pic'
                                    ]
                                ):
                                    # Skip UI elements
                                    if not any(skip in img_url.lower() for skip in [
                                        'logo', 'icon', 'button', 'sprite', 'avatar', 'default'
                                    ]):
                                        found_urls.add(img_url)
                    
                    print(f"🔍 PornHub strategy found: {len(found_urls)} URLs so far")
                    
                    if len(found_urls) >= max_results:
                        break
                        
            except Exception as e:
                print(f"❌ PornHub strategy error: {str(e)}")
                continue
                
    except Exception as e:
        print(f"❌ PornHub search failed: {str(e)}")
    
    if progress_callback:
        progress_callback(f"✅ PornHub found: {len(found_urls)} URLs", 100, 0, 0, 0)
    
    print(f"✅ PornHub found: {len(found_urls)} image URLs")
    return list(found_urls)[:max_results]

def enhanced_xhamster_search(query, max_results=50, progress_callback=None):
    """Search xHamster for adult content"""
    if progress_callback:
        progress_callback(f"🔞 Starting xHamster search for: {query}", 0, 0, 0, 0)
    
    print(f"🔞 Enhanced xHamster search for: {query}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://xhamster.com/',
        'Cookie': 'lang=en; fingerprint_hash=1658566353; timezone_offset=0'
    }
    
    try:
        search_url = f"https://xhamster.com/search/{quote_plus(query)}"
        
        if progress_callback:
            progress_callback("🔍 Searching xHamster content...", 20, 0, 0, 0)
        
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(search_url, timeout=30)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract video thumbnails
            video_blocks = soup.find_all('div', class_=['thumb-image-container', 'video-thumb'])
            
            for block in video_blocks[:max_results]:
                try:
                    img_tags = block.find_all('img')
                    for img in img_tags:
                        if img.get('src'):
                            img_url = img['src']
                            if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                found_urls.add(img_url)
                        
                        if img.get('data-src'):
                            img_url = img['data-src']
                            if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                                found_urls.add(img_url)
                
                except Exception as e:
                    continue
            
            if progress_callback:
                progress_callback(f"✅ xHamster search complete: {len(found_urls)} images found", 100, len(found_urls), 0, 0)
            
            print(f"✅ xHamster found: {len(found_urls)} image URLs")
            
        else:
            print(f"❌ xHamster search failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ xHamster search error: {str(e)}")
    
    return list(found_urls)

def enhanced_gelbooru_search(query, max_results=50, progress_callback=None):
    """Search Gelbooru anime/hentai image board"""
    if progress_callback:
        progress_callback(f"🎨 Starting Gelbooru search for: {query}", 0, 0, 0, 0)
    
    print(f"🎨 Enhanced Gelbooru search for: {query}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://gelbooru.com/'
    }
    
    try:
        # Gelbooru API endpoint
        api_url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags={quote_plus(query)}&limit={min(max_results, 100)}&json=1"
        
        if progress_callback:
            progress_callback("🔍 Searching Gelbooru API...", 20, 0, 0, 0)
        
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if isinstance(data, list):
                    for post in data:
                        if 'file_url' in post:
                            found_urls.add(post['file_url'])
                        if 'sample_url' in post:
                            found_urls.add(post['sample_url'])
                        if 'preview_url' in post:
                            found_urls.add(post['preview_url'])
                
                if progress_callback:
                    progress_callback(f"✅ Gelbooru search complete: {len(found_urls)} images found", 100, len(found_urls), 0, 0)
                
                print(f"✅ Gelbooru found: {len(found_urls)} image URLs")
                
            except json.JSONDecodeError:
                print(f"❌ Gelbooru API returned invalid JSON")
                
        else:
            print(f"❌ Gelbooru search failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Gelbooru search error: {str(e)}")
    
    return list(found_urls)

def enhanced_rule34_search(query, max_results=50, progress_callback=None):
    """Search Rule34 image board"""
    if progress_callback:
        progress_callback(f"🔞 Starting Rule34 search for: {query}", 0, 0, 0, 0)
    
    print(f"🔞 Enhanced Rule34 search for: {query}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://rule34.xxx/'
    }
    
    try:
        # Rule34 API endpoint
        api_url = f"https://rule34.xxx/index.php?page=dapi&s=post&q=index&tags={quote_plus(query)}&limit={min(max_results, 100)}&json=1"
        
        if progress_callback:
            progress_callback("🔍 Searching Rule34 API...", 20, 0, 0, 0)
        
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if isinstance(data, list):
                    for post in data:
                        if 'file_url' in post:
                            found_urls.add(post['file_url'])
                        if 'sample_url' in post:
                            found_urls.add(post['sample_url'])
                        if 'preview_url' in post:
                            found_urls.add(post['preview_url'])
                
                if progress_callback:
                    progress_callback(f"✅ Rule34 search complete: {len(found_urls)} images found", 100, len(found_urls), 0, 0)
                
                print(f"✅ Rule34 found: {len(found_urls)} image URLs")
                
            except json.JSONDecodeError:
                print(f"❌ Rule34 API returned invalid JSON")
                
        else:
            print(f"❌ Rule34 search failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Rule34 search error: {str(e)}")
    
    return list(found_urls)

def enhanced_e621_search(query, max_results=50, progress_callback=None):
    """Search e621 furry art image board"""
    if progress_callback:
        progress_callback(f"🐾 Starting e621 search for: {query}", 0, 0, 0, 0)
    
    print(f"🐾 Enhanced e621 search for: {query}")
    
    found_urls = set()
    headers = {
        'User-Agent': f'MediaScraper/1.0 (contact@example.com)',  # e621 requires proper User-Agent
        'Accept': 'application/json'
    }
    
    try:
        # e621 API endpoint (requires proper API format)
        api_url = f"https://e621.net/posts.json?tags={quote_plus(query)}&limit={min(max_results, 100)}"
        
        if progress_callback:
            progress_callback("🔍 Searching e621 API...", 20, 0, 0, 0)
        
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                if 'posts' in data:
                    for post in data['posts']:
                        if 'file' in post and 'url' in post['file']:
                            found_urls.add(post['file']['url'])
                        if 'sample' in post and 'url' in post['sample']:
                            found_urls.add(post['sample']['url'])
                        if 'preview' in post and 'url' in post['preview']:
                            found_urls.add(post['preview']['url'])
                
                if progress_callback:
                    progress_callback(f"✅ e621 search complete: {len(found_urls)} images found", 100, len(found_urls), 0, 0)
                
                print(f"✅ e621 found: {len(found_urls)} image URLs")
                
            except json.JSONDecodeError:
                print(f"❌ e621 API returned invalid JSON")
                
        else:
            print(f"❌ e621 search failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ e621 search error: {str(e)}")
    
    return list(found_urls)

def enhanced_bing_search(query, max_results=50, safe_search=True):
    """Enhanced Bing Images search with safe search controls"""
    print(f"🌐 === ENHANCED BING SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    print(f"🔒 Safe search: {'ON' if safe_search else 'OFF'}")
    
    found_urls = set()
    user_agents = get_multiple_user_agents()
    
    try:
        # Bing Images search with advanced parameters
        for page in range(1, 4):  # Search first 3 pages
            offset = (page - 1) * 35
            search_url = "https://www.bing.com/images/search"
            
            params = {
                'q': query,
                'first': offset,
                'count': 35,
                'adlt': 'strict' if safe_search else 'off',  # FIXED: strict for safe, off for adult
                'qft': '+filterui:imagesize-large',  # Large images
            }
            
            headers = {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.bing.com/',
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find image URLs in Bing's response
                for img in soup.find_all('img', class_=['mimg']):
                    if img.get('src'):
                        found_urls.add(img['src'])
                    elif img.get('data-src'):
                        found_urls.add(img['data-src'])
                
                # Also look for high-res image data
                for a in soup.find_all('a', class_=['iusc']):
                    m_attr = a.get('m')
                    if m_attr:
                        try:
                            import json
                            m_data = json.loads(m_attr)
                            if 'murl' in m_data:
                                found_urls.add(m_data['murl'])
                        except:
                            pass
                
                print(f"📄 Bing page {page}: Found {len(found_urls)} URLs so far")
                
                if len(found_urls) >= max_results:
                    break
                    
                time.sleep(random.uniform(2, 4))  # Rate limiting
        
        print(f"✅ Bing search complete: {len(found_urls)} URLs")
    
    except Exception as e:
        print(f"❌ Bing search error: {str(e)}")
    
    return list(found_urls)[:max_results]

def enhanced_youtube_search(query, max_results=20, progress_callback=None):
    """Enhanced YouTube search using yt-dlp"""
    if progress_callback:
        progress_callback(f"📺 Searching YouTube for: {query}", 0, 0, 0, 0)
    
    print(f"📺 === ENHANCED YOUTUBE SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = []
    
    try:
        # Use yt-dlp to search YouTube
        search_url = f"ytsearch{max_results}:{query}"
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download, just get URLs
            'default_search': 'ytsearch',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(search_url, download=False)
            
            if 'entries' in search_results:
                for entry in search_results['entries']:
                    if entry and entry.get('webpage_url'):
                        found_urls.append(entry['webpage_url'])
                    elif entry and entry.get('url'):
                        found_urls.append(f"https://www.youtube.com/watch?v={entry['url']}")
                    elif entry and entry.get('id'):
                        found_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
        
        print(f"✅ YouTube search complete: {len(found_urls)} URLs")
        
        if progress_callback:
            progress_callback(f"📺 YouTube search complete: {len(found_urls)} videos", 90, 0, 0, 0)
    
    except Exception as e:
        print(f"❌ YouTube search error: {str(e)}")
    
    return found_urls[:max_results]

def enhanced_social_scrape(url, max_content=5, output_dir="downloads", aggressive=False):
    """
    Enhanced social media scraping with better error handling and more platforms
    """
    print(f"🎬 === ENHANCED SOCIAL SCRAPING ===")
    print(f"🔗 URL: {url}")
    print(f"📊 Max content: {max_content}")
    print(f"⚡ Aggressive mode: {aggressive}")
    
    # Parse URL for output directory
    parsed = urlparse(url)
    platform = parsed.netloc.replace('www.', '').split('.')[0]
    path_parts = [p for p in parsed.path.split('/') if p]
    safe_path = path_parts[-1] if path_parts else 'unknown'
    
    # Create output directory
    output_path = os.path.join(output_dir, platform, safe_path)
    os.makedirs(output_path, exist_ok=True)
    
    print(f"📁 Output: {output_path}")
    
    # Enhanced yt-dlp configuration
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'format': 'best[height<=1080]/best[height<=720]/best',
        'noplaylist': True,
        'extract_flat': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'writedescription': False,
        'writeinfojson': False,
        'writethumbnail': True,  # Get thumbnails as backup
        'no_warnings': False,
        'quiet': False,
        'max_downloads': max_content,
        'socket_timeout': 30,
        'retries': 3,
        'fragment_retries': 3,
        'ignoreerrors': True,  # Continue on errors
    }
    
    # Add aggressive options if requested
    if aggressive:
        ydl_opts.update({
            'writesubtitles': True,
            'writeautomaticsub': True,
            'writedescription': True,
            'writeinfojson': True,
            'format': 'best',
            'max_downloads': max_content * 2,
        })
    
    downloaded_count = 0
    
    try:
        print(f"🔍 Starting content discovery and download...")
        print(f"🔧 Running optimized yt-dlp...")
        
        # Use yt-dlp to download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as download_error:
                print(f"❌ Scraping error: {download_error}")
        
        print(f"✅ Enhanced scraping complete!")
        
        # Count downloaded files
        if os.path.exists(output_path):
            files = [f for f in os.listdir(output_path) 
                    if os.path.isfile(os.path.join(output_path, f)) and os.path.getsize(os.path.join(output_path, f)) > 1000]
            downloaded_count = len(files)
            
            print(f"📁 Files downloaded: {downloaded_count}")
            if downloaded_count == 0:
                # Try to get any errors
                all_files = [f for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f))]
                if all_files:
                    print(f"⚠️ Found {len(all_files)} files but they may be too small or corrupted")
        else:
            print(f"❌ Output directory not created: {output_path}")
    
    except Exception as e:
        print(f"❌ Critical error in social scraping: {e}")
        return 0
    
    return downloaded_count

def download_images_simple(query, max_images=10, output_dir="downloads", safe_search=True, progress_callback=None):
    """
    Simple image download function that combines multiple sources for images only
    """
    if progress_callback:
        progress_callback(f"🔍 Starting simple image search for: {query} (Safe search: {'ON' if safe_search else 'OFF'})", 0, 0, 0, 0)
    
    print(f"🔍 SIMPLE IMAGE SEARCH: '{query}'")
    print(f"🔓 Safe search: {'ENABLED' if safe_search else 'DISABLED (explicit content allowed)'}")
    print(f"📊 Max images: {max_images}")
    
    # Clean query for directory name
    safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_query = safe_query.replace(' ', '_')
    
    output_path = os.path.join(output_dir, safe_query)
    os.makedirs(output_path, exist_ok=True)
    
    found_urls = set()
    
    # 1. Bing Images search
    if progress_callback:
        progress_callback("🌐 Searching Bing Images...", 20, 0, 0, 0)
    try:
        bing_urls = enhanced_bing_search(query, max_results=max_images * 2, safe_search=safe_search)
        found_urls.update(bing_urls)
        print(f"✅ Bing Images: {len(bing_urls)} URLs")
    except Exception as e:
        print(f"❌ Bing search error: {str(e)}")
    
    # 2. Yandex Images search
    if progress_callback:
        progress_callback("🔍 Searching Yandex Images...", 40, len(found_urls), 0, 0)
    try:
        yandex_urls = enhanced_yandex_search(query, max_results=max_images * 2, safe_search=safe_search)
        found_urls.update(yandex_urls)
        print(f"✅ Yandex Images: {len(yandex_urls)} URLs")
    except Exception as e:
        print(f"❌ Yandex search error: {str(e)}")
    
    # 3. Adult content sources (only if safe search is disabled)
    if not safe_search:
        # Add Gelbooru (anime/hentai)
        if progress_callback:
            progress_callback("🎨 Searching Gelbooru...", 60, len(found_urls), 0, 0)
        try:
            gelbooru_urls = enhanced_gelbooru_search(query, max_results=max_images, progress_callback=progress_callback)
            found_urls.update(gelbooru_urls)
            print(f"✅ Gelbooru: {len(gelbooru_urls)} URLs")
        except Exception as e:
            print(f"❌ Gelbooru error: {str(e)}")
        
        # Add Rule34
        if progress_callback:
            progress_callback("🔞 Searching Rule34...", 70, len(found_urls), 0, 0)
        try:
            rule34_urls = enhanced_rule34_search(query, max_results=max_images, progress_callback=progress_callback)
            found_urls.update(rule34_urls)
            print(f"✅ Rule34: {len(rule34_urls)} URLs")
        except Exception as e:
            print(f"❌ Rule34 error: {str(e)}")
    
    # 4. Stock photo sites
    if progress_callback:
        progress_callback("🎨 Searching Stock Photos...", 80, len(found_urls), 0, 0)
    try:
        # Try Unsplash
        unsplash_urls = enhanced_unsplash_search(query, max_results=max_images, safe_search=safe_search)
        found_urls.update(unsplash_urls)
        print(f"✅ Unsplash: {len(unsplash_urls)} URLs")
    except Exception as e:
        print(f"❌ Unsplash error: {str(e)}")
    
    if progress_callback:
        progress_callback(f"📋 Found {len(found_urls)} image URLs", 85, 0, 0, 0)
    
    print(f"📋 Total image URLs found: {len(found_urls)}")
    
    if not found_urls:
        if progress_callback:
            progress_callback("❌ No image URLs found", 100, 0, 0, 0)
        print("❌ No image URLs found from any source")
        return 0
    
    downloaded_count = 0
    attempts = 0
    max_attempts = max_images * 3  # Try more URLs for better success rate
    
    # Randomize order to get variety
    found_urls_list = list(found_urls)
    random.shuffle(found_urls_list)
    
    for img_url in found_urls_list:
        if downloaded_count >= max_images or attempts >= max_attempts:
            break
            
        attempts += 1
        progress_percent = 85 + (attempts / max_attempts) * 15  # 85% to 100%
        
        try:
            if progress_callback:
                progress_callback(f"⬇️ Downloading {downloaded_count + 1}/{max_images}: {os.path.basename(img_url)[:50]}...", int(progress_percent), downloaded_count, downloaded_count, 0)
            
            print(f"⬇️ Downloading image {downloaded_count + 1}/{max_images} (attempt {attempts}): {img_url[:80]}...")
            
            # Enhanced headers with rotation
            headers = {
                'User-Agent': random.choice(get_multiple_user_agents()),
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f"https://{urlparse(img_url).netloc}/",
                'DNT': '1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Retry logic for failed downloads
            max_retries = 2
            for retry in range(max_retries):
                try:
                    img_response = requests.get(img_url, headers=headers, timeout=15, allow_redirects=True)
                    
                    if img_response.status_code == 200 and img_response.content:
                        # Validate content
                        content_length = len(img_response.content)
                        content_type = img_response.headers.get('content-type', '').lower()
                        
                        # Check if it's actually an image
                        is_image = (
                            any(img_type in content_type for img_type in ['image/', 'jpeg', 'png', 'gif', 'webp']) or
                            img_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) or
                            content_length > 5000  # Assume larger files are likely images
                        )
                        
                        if not is_image:
                            print(f"❌ Not an image (retry {retry + 1}): {content_type}")
                            if retry < max_retries - 1:
                                time.sleep(random.uniform(1, 2))
                                continue
                            else:
                                break
                        
                        # Determine file extension
                        ext = '.jpg'  # Default
                        if 'png' in content_type:
                            ext = '.png'
                        elif 'gif' in content_type:
                            ext = '.gif'
                        elif 'webp' in content_type:
                            ext = '.webp'
                        elif img_url.lower().endswith('.png'):
                            ext = '.png'
                        elif img_url.lower().endswith('.gif'):
                            ext = '.gif'
                        elif img_url.lower().endswith('.webp'):
                            ext = '.webp'
                        
                        filename = f"{safe_query}_{downloaded_count + 1}{ext}"
                        filepath = os.path.join(output_path, filename)
                        
                        # Write file
                        with open(filepath, 'wb') as f:
                            f.write(img_response.content)
                        
                        # Validate file size
                        file_size = len(img_response.content)
                        if file_size > 5000:  # At least 5KB for decent quality
                            downloaded_count += 1
                            print(f"✅ Downloaded: {filename} ({file_size} bytes)")
                            
                            # Report the downloaded file through progress callback for database tracking
                            if progress_callback:
                                progress_callback(
                                    f"✅ Downloaded: {filename}", 
                                    int(progress_percent), 
                                    downloaded_count, 
                                    downloaded_count,  # All images 
                                    0,  # No videos
                                    filepath  # Pass the full file path as current_file
                                )
                            
                            break  # Success, exit retry loop
                        else:
                            print(f"❌ File too small: {file_size} bytes")
                            os.remove(filepath)  # Remove small file
                            
                    else:
                        print(f"❌ HTTP {img_response.status_code}: {img_url[:50]}")
                        
                except Exception as download_error:
                    print(f"❌ Download error (retry {retry + 1}): {str(download_error)[:50]}")
                    if retry < max_retries - 1:
                        time.sleep(random.uniform(1, 2))
                        continue
            
            time.sleep(random.uniform(0.5, 1.5))  # Rate limiting
            
        except Exception as e:
            print(f"❌ Error processing {img_url[:50]}: {str(e)}")
            continue
    
    if progress_callback:
        progress_callback(f"✅ Download complete: {downloaded_count}/{max_images} images", 100, downloaded_count, downloaded_count, 0)
    
    print(f"✅ Simple image download complete: {downloaded_count}/{max_images} images")
    return downloaded_count

def test_with_known_working_content():
    """
    Test with content that is known to work for verification
    """
    print("🧪 === TESTING WITH KNOWN WORKING CONTENT ===")
    
    # Test YouTube download
    print("📹 Testing YouTube download...")
    youtube_count = enhanced_social_scrape(
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # First YouTube video
        max_content=1,
        output_dir="test_downloads/youtube"
    )
    print(f"YouTube test result: {youtube_count} files")
    
    # Test image search
    print("🖼️ Testing image search...")
    image_count = download_images_simple(
        query="test",
        max_images=3,
        output_dir="test_downloads/images",
        safe_search=False
    )
    print(f"Image search test result: {image_count} files")
    
    total_files = youtube_count + image_count
    print(f"📊 TOTAL TEST RESULT: {total_files} files downloaded")
    
    if total_files > 0:
        print("✅ SUCCESS: System can download real content")
        return {'success': True, 'total_files': total_files, 'youtube': youtube_count, 'images': image_count}
    else:
        print("❌ FAILURE: System could not download any content")
        return {'success': False, 'total_files': 0, 'youtube': 0, 'images': 0}

def download_urls_from_source(urls, output_dir, source_obj, progress_callback=None, max_downloads=None, filter_type='comprehensive'):
    """
    Download content from URLs with proper type detection
    
    Args:
        urls: List of URLs to download
        output_dir: Output directory
        source_obj: Source object
        progress_callback: Progress callback function
        max_downloads: Maximum number of downloads
        filter_type: Type of content to download ('comprehensive', 'images', 'videos')
    """
    if not urls:
        return {'downloaded': 0, 'failed': 0, 'images': 0, 'videos': 0}
    
    # Use handler's download_func if available
    handler = getattr(source_obj, 'handler', None)
    if handler and handler.get('download'):
        return handler['download'](urls[:max_downloads] if max_downloads else urls, output_dir, progress_callback)
    
    # Check if this is a video source
    if source_obj.category == 'video' or source_obj.name in ['videos', 'youtube', 'vimeo', 'dailymotion']:
        # Use yt-dlp for video sources
        return download_videos_with_ytdlp(urls[:max_downloads] if max_downloads else urls, output_dir, progress_callback)
    
    # Continue with regular download for non-video sources
    if max_downloads:
        urls = urls[:max_downloads]
    
    print(f"\n⬇️ Downloading from {source_obj.display_name}...")
    print(f"📊 URLs to process: {len(urls)}")
    print(f"🔍 Filter type: {filter_type}")
    
    # Create source-specific directory
    source_dir = os.path.join(output_dir, source_obj.name)
    os.makedirs(source_dir, exist_ok=True)
    
    downloaded_count = 0
    failed_count = 0
    image_count = 0
    video_count = 0
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'image/webp,image/apng,image/*,video/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    for i, url in enumerate(urls):
        if downloaded_count >= (max_downloads or len(urls)):
            break
            
        progress_percent = int((i / len(urls)) * 100)
        
        if progress_callback:
            progress_callback(f"⬇️ Downloading from {source_obj.display_name}...", progress_percent, downloaded_count, image_count, video_count)
        
        try:
            # Skip if not a valid URL
            if not url or not url.startswith(('http://', 'https://')):
                failed_count += 1
                continue
            
            response = session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            content_length = int(response.headers.get('Content-Length', 0))
            
            # Skip if too small (likely an error page)
            if content_length < 5000 and content_length > 0:
                failed_count += 1
                source_obj.record_download(False)
                continue
            
            # Check if it's a video URL that needs yt-dlp
            if any(domain in url for domain in ['youtube.com', 'youtu.be', 'vimeo.com', 'twitter.com', 'x.com']):
                # Handle video with yt-dlp
                if filter_type == 'images':
                    # Skip videos if we're only looking for images
                    failed_count += 1
                    continue
                    
                video_result = download_videos_with_ytdlp([url], source_dir, progress_callback)
                if video_result['downloaded'] > 0:
                    downloaded_count += 1
                    video_count += 1
                    source_obj.record_download(True)
                else:
                    failed_count += 1
                    source_obj.record_download(False)
                continue
            
            # Determine if content is valid image/video
            if any(content_type.startswith(t) for t in ['image/', 'video/']):
                # Determine file extension and type
                ext = '.jpg'  # default
                is_video = False
                
                if 'image/png' in content_type:
                    ext = '.png'
                elif 'image/gif' in content_type:
                    ext = '.gif'
                elif 'image/webp' in content_type:
                    ext = '.webp'
                elif 'video/mp4' in content_type:
                    ext = '.mp4'
                    is_video = True
                elif 'video/webm' in content_type:
                    ext = '.webm'
                    is_video = True
                else:
                    # Try to guess from URL
                    url_lower = url.lower()
                    if url_lower.endswith('.png'):
                        ext = '.png'
                    elif url_lower.endswith('.gif'):
                        ext = '.gif'
                    elif url_lower.endswith('.webp'):
                        ext = '.webp'
                    elif url_lower.endswith(('.mp4', '.webm', '.avi', '.mov')):
                        is_video = True
                        ext = '.' + url_lower.split('.')[-1]
                
                # Apply filter
                if filter_type == 'images' and is_video:
                    # Skip videos if we're only looking for images
                    failed_count += 1
                    continue
                elif filter_type == 'videos' and not is_video:
                    # Skip images if we're only looking for videos
                    failed_count += 1
                    continue
                
                # Update counters
                if is_video:
                    video_count += 1
                else:
                    image_count += 1
                
                # Create filename
                filename = f"{source_obj.name}_{downloaded_count + 1}{ext}"
                filepath = os.path.join(source_dir, filename)
                
                # Write file
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                downloaded_count += 1
                source_obj.record_download(True)
                print(f"✅ Downloaded: {filename} ({content_length} bytes)")
                
                # Report the downloaded file through progress callback for database tracking
                if progress_callback:
                    progress_callback(
                        f"✅ Downloaded: {filename}", 
                        progress_percent, 
                        downloaded_count, 
                        image_count, 
                        video_count,
                        filepath  # Pass the full file path as current_file
                    )
                
            else:
                failed_count += 1
                source_obj.record_download(False)
                print(f"❌ Invalid content: {content_type} ({content_length} bytes)")
                
        except Exception as e:
            failed_count += 1
            source_obj.record_download(False)
            print(f"❌ Download error: {str(e)}")
            
        # Rate limiting
        time.sleep(random.uniform(0.5, 1.5))
    
    if progress_callback:
        progress_callback(f"✅ {source_obj.display_name} complete: {downloaded_count} downloaded", 100, downloaded_count, image_count, video_count)
    
    print(f"✅ {source_obj.display_name} download complete: {downloaded_count} downloaded, {failed_count} failed")
    
    return {
        'downloaded': downloaded_count,
        'failed': failed_count,
        'images': image_count,
        'videos': video_count
    }

def enhanced_yandex_search(query, max_results=50, safe_search=True):
    """
    Enhanced Yandex Images search
    """
    print(f"🔍 === ENHANCED YANDEX SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    print(f"🔒 Safe search: {'ON' if safe_search else 'OFF'}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        # Yandex Images search
        search_url = f"https://yandex.com/images/search?text={requests.utils.quote(query)}"
        
        if safe_search:
            search_url += "&family=yes"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image URLs in Yandex's response
            img_tags = soup.find_all('img', src=True)
            
            for img in img_tags:
                src = img.get('src')
                if src and src.startswith(('http', '//')):
                    if src.startswith('//'):
                        src = 'https:' + src
                    
                    # Filter out small images and icons
                    if not any(skip in src.lower() for skip in ['avatar', 'icon', '16x16', '32x32']):
                        found_urls.add(src)
                        
    except Exception as e:
        print(f"❌ Yandex search error: {str(e)}")
    
    print(f"✅ Yandex search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_imgur_search(query, max_results=50, safe_search=True):
    """
    Enhanced Imgur search
    """
    print(f"🖼️ === ENHANCED IMGUR SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        # Imgur search - note: Imgur's search requires API for reliable results
        search_url = f"https://imgur.com/search?q={requests.utils.quote(query)}"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image URLs
            img_tags = soup.find_all('img', src=True)
            
            for img in img_tags:
                src = img.get('src')
                if src and 'imgur.com' in src and src.startswith(('http', '//')):
                    if src.startswith('//'):
                        src = 'https:' + src
                    found_urls.add(src)
                        
    except Exception as e:
        print(f"❌ Imgur search error: {str(e)}")
    
    print(f"✅ Imgur search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_tumblr_search(query, max_results=50, safe_search=True):
    """Enhanced Tumblr search"""
    print(f"📝 === ENHANCED TUMBLR SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    print(f"🔒 Safe search: {'ON' if safe_search else 'OFF'}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        # Tumblr search URL
        search_url = f"https://www.tumblr.com/search/{requests.utils.quote(query)}"
        
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Look for image URLs in the response
            img_patterns = [
                r'"(https://[^"]*\.media\.tumblr\.com/[^"]*\.(jpg|jpeg|png|gif|webp))"',
                r'"(https://[^"]*64\.media\.tumblr\.com/[^"]*\.(jpg|jpeg|png|gif|webp))"',
                r'"(https://[^"]*static\.tumblr\.com/[^"]*\.(jpg|jpeg|png|gif|webp))"',
                r'src="(https://[^"]*\.tumblr\.com/[^"]*\.(jpg|jpeg|png|gif|webp))"'
            ]
            
            for pattern in img_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                for match in matches:
                    # Handle tuple results from group matching
                    url = match[0] if isinstance(match, tuple) else match
                    if url and url.startswith('https://'):
                        # Filter out small thumbnails
                        if not any(size in url for size in ['_75sq', '_100sq', '_128']):
                            found_urls.add(url)
            
            # Also try to extract from script tags with JSON data
            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'tumblr.com' in script.string:
                    # Look for image URLs in JSON data
                    img_urls = re.findall(r'"(https://[^"]*\.tumblr\.com/[^"]*\.(jpg|jpeg|png|gif|webp))"', script.string, re.IGNORECASE)
                    for url_match in img_urls:
                        url = url_match[0] if isinstance(url_match, tuple) else url_match
                        if url and not any(size in url for size in ['_75sq', '_100sq', '_128']):
                            found_urls.add(url)
    
    except Exception as e:
        print(f"❌ Tumblr search error: {str(e)}")
    
    print(f"✅ Tumblr search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_pinterest_search(query, max_results=50, safe_search=True):
    """
    Enhanced Pinterest search
    """
    print(f"📌 === ENHANCED PINTEREST SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        # Pinterest search
        search_url = f"https://www.pinterest.com/search/pins/?q={requests.utils.quote(query)}"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image URLs
            img_tags = soup.find_all('img', src=True)
            
            for img in img_tags:
                src = img.get('src')
                if src and ('pinimg.com' in src or 'pinterest' in src):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif not src.startswith('http'):
                        src = 'https:' + src
                    found_urls.add(src)
                        
    except Exception as e:
        print(f"❌ Pinterest search error: {str(e)}")
    
    print(f"✅ Pinterest search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_flickr_search(query, max_results=50, safe_search=True):
    """
    Enhanced Flickr search
    """
    print(f"📷 === ENHANCED FLICKR SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        # Flickr search
        search_url = f"https://www.flickr.com/search/?text={requests.utils.quote(query)}"
        
        if safe_search:
            search_url += "&safe_search=3"  # Strict
        else:
            search_url += "&safe_search=1"  # Moderate
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image URLs
            img_tags = soup.find_all('img', src=True)
            
            for img in img_tags:
                src = img.get('src')
                if src and ('flickr.com' in src or 'staticflickr.com' in src):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif not src.startswith('http'):
                        src = 'https:' + src
                    found_urls.add(src)
                        
    except Exception as e:
        print(f"❌ Flickr search error: {str(e)}")
    
    print(f"✅ Flickr search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_unsplash_search(query, max_results=50, safe_search=True):
    """
    Enhanced Unsplash search for high-quality stock photos
    """
    print(f"🌅 === ENHANCED UNSPLASH SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        # Unsplash search
        search_url = f"https://unsplash.com/s/photos/{requests.utils.quote(query)}"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image URLs
            img_tags = soup.find_all('img', src=True)
            
            for img in img_tags:
                src = img.get('src')
                if src and ('unsplash.com' in src or 'images.unsplash.com' in src):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif not src.startswith('http'):
                        src = 'https:' + src
                    found_urls.add(src)
                        
    except Exception as e:
        print(f"❌ Unsplash search error: {str(e)}")
    
    print(f"✅ Unsplash search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_pexels_search(query, max_results=50, safe_search=True):
    """
    Enhanced Pexels search for high-quality stock photos
    """
    print(f"📸 === ENHANCED PEXELS SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        # Pexels search
        search_url = f"https://www.pexels.com/search/{requests.utils.quote(query)}/"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find image URLs
            img_tags = soup.find_all('img', src=True)
            
            for img in img_tags:
                src = img.get('src')
                if src and ('pexels.com' in src or 'images.pexels.com' in src):
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif not src.startswith('http'):
                        src = 'https:' + src
                    found_urls.add(src)
                        
    except Exception as e:
        print(f"❌ Pexels search error: {str(e)}")
    
    print(f"✅ Pexels search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_video_search(query, max_results=50, safe_search=True):
    """
    Enhanced video search across multiple video platforms
    """
    print(f"🎬 === ENHANCED VIDEO SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    print(f"🔒 Safe search: {'ON' if safe_search else 'OFF'}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    # Search YouTube
    try:
        youtube_search_url = f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}"
        response = requests.get(youtube_search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Extract video IDs from search results
            video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', response.text)
            for video_id in video_ids[:max_results//3]:  # Get 1/3 from YouTube
                found_urls.add(f"https://www.youtube.com/watch?v={video_id}")
                
    except Exception as e:
        print(f"❌ YouTube search error: {str(e)}")
    
    # Search Vimeo
    try:
        vimeo_search_url = f"https://vimeo.com/search?q={requests.utils.quote(query)}"
        response = requests.get(vimeo_search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Extract Vimeo video URLs
            vimeo_urls = re.findall(r'href="(/\d+)"', response.text)
            for url in vimeo_urls[:max_results//3]:  # Get 1/3 from Vimeo
                found_urls.add(f"https://vimeo.com{url}")
                
    except Exception as e:
        print(f"❌ Vimeo search error: {str(e)}")
    
    # Search Internet Archive videos
    try:
        archive_search_url = f"https://archive.org/search.php?query={requests.utils.quote(query)}&mediatype=movies"
        response = requests.get(archive_search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find video links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/details/' in href and not href.endswith('/'):
                    found_urls.add(f"https://archive.org{href}")
                    if len(found_urls) >= max_results:
                        break
                        
    except Exception as e:
        print(f"❌ Archive.org search error: {str(e)}")
    
    print(f"✅ Video search complete: {len(found_urls)} video URLs found")
    return list(found_urls)[:max_results]

def download_videos_with_ytdlp(urls, output_dir, progress_callback=None):
    """
    Enhanced video download using yt-dlp with multiple fallback methods
    """
    if not urls:
        return {'downloaded': 0, 'failed': 0, 'videos': 0, 'images': 0}
    
    downloaded_count = 0
    failed_count = 0
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    for i, url in enumerate(urls):
        try:
            if progress_callback:
                progress_percent = int((i / len(urls)) * 100)
                progress_callback(f"📹 Downloading video {i+1}/{len(urls)}...", progress_percent, downloaded_count, 0, downloaded_count)
            
            # Try multiple quality options with fallbacks
            quality_options = [
                {
                    'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
                    'description': '720p with audio'
                },
                {
                    'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]/best',
                    'description': '480p with audio'
                },
                {
                    'format': 'best',
                    'description': 'best available'
                }
            ]
            
            download_successful = False
            
            for quality_opt in quality_options:
                try:
                    # yt-dlp options with enhanced compatibility
                    ydl_opts = {
                        'outtmpl': os.path.join(output_dir, f'video_{downloaded_count + 1}_%(title)s.%(ext)s'),
                        'quiet': False,  # Show output for debugging
                        'no_warnings': False,
                        'format': quality_opt['format'],
                        'max_filesize': 200 * 1024 * 1024,  # 200MB max
                        'ignoreerrors': False,
                        'no_color': True,
                        'extract_flat': False,
                        'prefer_free_formats': True,
                        'socket_timeout': 30,
                        'retries': 3,
                        'fragment_retries': 3,
                        'concurrent_fragment_downloads': 1,
                        # Remove problematic cookiesfrombrowser option
                        # 'cookiesfrombrowser': 'chrome',  # This was causing the error
                        'user_agent': random.choice(get_multiple_user_agents()),
                        # Post-processing options
                        'postprocessors': [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp4',  # Convert to mp4 for compatibility
                        }],
                        # Extract metadata for better filenames
                        'writeinfojson': False,
                        'writethumbnail': True,  # Download thumbnail too
                        # Subtitle options
                        'writesubtitles': False,
                        'writeautomaticsub': False,
                        # Progress hooks
                        'progress_hooks': [],
                        # Additional options for better compatibility
                        'age_limit': None,  # Allow all content
                        'geo_bypass': True,  # Bypass geo restrictions
                    }
                    
                    # Special handling for different platforms
                    if 'twitter.com' in url or 'x.com' in url:
                        ydl_opts['format'] = 'best'
                    elif 'instagram.com' in url:
                        ydl_opts['format'] = 'best'
                    elif 'tiktok.com' in url:
                        ydl_opts['format'] = 'best'
                        ydl_opts['http_headers'] = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Referer': 'https://www.tiktok.com/'
                        }
                    
                    print(f"🔄 Attempting to download: {url} with {quality_opt['description']}")
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        # First extract info without downloading
                        info = ydl.extract_info(url, download=False)
                        
                        if info:
                            # Check if it's a playlist
                            if info.get('_type') == 'playlist':
                                # Download only the first video from playlist
                                entries = info.get('entries', [])
                                if entries:
                                    url = entries[0].get('webpage_url', url)
                                    info = ydl.extract_info(url, download=True)
                            else:
                                # Download the video
                                info = ydl.extract_info(url, download=True)
                            
                            if info:
                                downloaded_count += 1
                                download_successful = True
                                
                                # Get the downloaded file path
                                if 'requested_downloads' in info:
                                    for download in info['requested_downloads']:
                                        filepath = download.get('filepath', '')
                                        if filepath and progress_callback:
                                            # Report downloaded file
                                            progress_callback(
                                                f"✅ Downloaded: {os.path.basename(filepath)}", 
                                                progress_percent, 
                                                downloaded_count, 
                                                0, 
                                                downloaded_count,
                                                filepath
                                            )
                                
                                print(f"✅ Downloaded video {downloaded_count}: {info.get('title', 'Unknown')} [{quality_opt['description']}]")
                                break
                                
                except yt_dlp.utils.DownloadError as e:
                    error_msg = str(e)
                    print(f"⚠️ yt-dlp error: {error_msg[:200]}")
                    if "Private video" in error_msg or "unavailable" in error_msg:
                        print(f"⚠️ Video unavailable: {url}")
                        break  # Don't try other qualities for unavailable videos
                    continue
                except Exception as e:
                    print(f"❌ Download attempt failed: {str(e)[:200]}")
                    continue
            
            if not download_successful:
                # Try alternative download method using requests for direct video URLs
                if any(ext in url.lower() for ext in ['.mp4', '.webm', '.avi', '.mov', '.mkv']):
                    try:
                        print(f"🔄 Attempting direct download: {url}")
                        response = requests.get(url, stream=True, timeout=30, headers={
                            'User-Agent': random.choice(get_multiple_user_agents())
                        })
                        if response.status_code == 200:
                            # Extract filename from URL or use generic name
                            filename = url.split('/')[-1].split('?')[0]
                            if not filename or '.' not in filename:
                                filename = f'video_{downloaded_count + 1}.mp4'
                            
                            filepath = os.path.join(output_dir, filename)
                            
                            # Download the file
                            with open(filepath, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            downloaded_count += 1
                            download_successful = True
                            
                            if progress_callback:
                                progress_callback(
                                    f"✅ Direct download: {filename}", 
                                    progress_percent, 
                                    downloaded_count, 
                                    0, 
                                    downloaded_count,
                                    filepath
                                )
                            
                            print(f"✅ Direct download successful: {filename}")
                    except Exception as e:
                        print(f"❌ Direct download failed: {str(e)}")
                
                if not download_successful:
                    failed_count += 1
                    print(f"❌ Failed to download video: {url}")
                    
        except Exception as e:
            failed_count += 1
            print(f"❌ Video download error: {str(e)[:100]}")
    
    if progress_callback:
        progress_callback(f"✅ Video download complete: {downloaded_count} videos", 100, downloaded_count, 0, downloaded_count)
    
    return {
        'downloaded': downloaded_count,
        'failed': failed_count,
        'videos': downloaded_count,
        'images': 0
    }

if __name__ == "__main__":
    # Run verification test
    test_with_known_working_content()
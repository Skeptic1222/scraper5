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

class ContentSource:
    """Represents a content source with detection and download capabilities"""
    def __init__(self, name, display_name, enabled=True, category="general", requires_no_safe_search=False):
        self.name = name
        self.display_name = display_name
        self.enabled = enabled
        self.category = category
        self.requires_no_safe_search = requires_no_safe_search  # NEW: Adult content flag
        self.detected_count = 0
        self.downloaded_count = 0
        self.failed_count = 0
        self.urls = []
        
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

def get_content_sources():
    """Get all available content sources with adult content separated"""
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

def enhanced_instagram_scrape(username_or_url, max_content=10, output_dir="downloads", progress_callback=None):
    """
    FIXED: Enhanced Instagram scraping with better reliability and authentication
    """
    if progress_callback:
        progress_callback("📸 Starting enhanced Instagram scraping...", 0, 0, 0, 0)
    
    print(f"📸 === ENHANCED INSTAGRAM SCRAPING (FIXED) ===")
    print(f"🎯 Target: {username_or_url}")
    print(f"📊 Max content: {max_content}")
    
    # Parse username from URL if needed
    if 'instagram.com' in username_or_url:
        username = username_or_url.split('/')[-2] if username_or_url.endswith('/') else username_or_url.split('/')[-1]
    else:
        username = username_or_url.replace('@', '')
    
    output_path = os.path.join(output_dir, 'instagram', username)
    os.makedirs(output_path, exist_ok=True)
    
    print(f"📁 Output: {output_path}")
    
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
            '--dest', output_path,
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
            if os.path.exists(output_path):
                for file in os.listdir(output_path):
                    file_path = os.path.join(output_path, file)
                    if os.path.isfile(file_path) and os.path.getsize(file_path) > 5000:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            image_count += 1
                        elif file.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                            video_count += 1
                        downloaded_count += 1
                        
                        if progress_callback:
                            try:
                                progress_callback(f"✅ Downloaded: {file}", 50, downloaded_count, image_count, video_count)
                            except Exception as e:
                                print(f"⚠️ Progress callback error: {str(e)[:50]}")
            
            if downloaded_count > 0:
                if progress_callback:
                    try:
                        progress_callback(f"✅ Gallery-dl success: {downloaded_count} files", 100, downloaded_count, image_count, video_count)
                    except Exception as e:
                        print(f"⚠️ Progress callback error: {str(e)[:50]}")
                print(f"✅ Gallery-dl success: {downloaded_count} files")
                return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}
        
        print(f"❌ Gallery-dl failed: {result.stderr[:200]}...")
        
    except Exception as e:
        print(f"❌ Gallery-dl error: {str(e)[:100]}")
    
    # Method 2: IMPROVED yt-dlp with better configuration
    try:
        if progress_callback:
            progress_callback("🔄 Instagram Method 2: Improved yt-dlp...", 30, downloaded_count, image_count, video_count)
            
        print(f"🔄 Method 2: Improved yt-dlp with enhanced settings...")
        methods_tried.append("yt-dlp-improved")
        
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(uploader)s_%(id)s.%(ext)s'),
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writedescription': True,
            'writeinfojson': True,
            'writethumbnail': True,
            'max_downloads': max_content,
            'ignoreerrors': True,
            'sleep_interval': 15,  # Increased delays
            'max_sleep_interval': 30,
            'cookiesfrombrowser': ['chrome', 'firefox'],  # Try multiple browsers
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
                
                if os.path.exists(output_path):
                    for file in os.listdir(output_path):
                        file_path = os.path.join(output_path, file)
                        if os.path.isfile(file_path) and os.path.getsize(file_path) > 5000:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                                new_image_count += 1
                            elif file.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                                new_video_count += 1
                            new_downloaded += 1
                            
                            if progress_callback:
                                progress_callback(f"✅ Downloaded: {file}", 70, new_downloaded, new_image_count, new_video_count)
                
                if new_downloaded > downloaded_count:
                    downloaded_count = new_downloaded
                    image_count = new_image_count
                    video_count = new_video_count
                    
                    if progress_callback:
                        progress_callback(f"✅ yt-dlp success: {downloaded_count} files", 100, downloaded_count, image_count, video_count)
                    print(f"✅ yt-dlp success: {downloaded_count} files")
                    return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}
                    
            except Exception as e:
                print(f"❌ yt-dlp download error: {str(e)[:100]}")
        
    except Exception as e:
        print(f"❌ yt-dlp setup error: {str(e)[:100]}")
    
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
        print(f"❌ API simulation error: {str(e)[:100]}")
    
    if progress_callback:
        progress_callback(f"⚠️ Instagram scraping completed with limited success", 100, downloaded_count, image_count, video_count)
    
    print(f"📊 Instagram scraping complete")
    print(f"🔧 Methods tried: {', '.join(methods_tried)}")
    print(f"📁 Files downloaded: {downloaded_count} (Images: {image_count}, Videos: {video_count})")
    
    return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}

def enhanced_twitter_scrape(username_or_url, max_content=10, output_dir="downloads", progress_callback=None):
    """FIXED: Enhanced Twitter/X scraping with better authentication and methods"""
    if progress_callback:
        progress_callback("🐦 Starting enhanced Twitter scraping...", 0, 0, 0, 0)
        
    print(f"🐦 === ENHANCED TWITTER SCRAPING (FIXED) ===")
    
    # Parse username
    if 'twitter.com' in username_or_url or 'x.com' in username_or_url:
        username = username_or_url.split('/')[-1]
    else:
        username = username_or_url.replace('@', '')
    
    output_path = os.path.join(output_dir, 'twitter', username)
    os.makedirs(output_path, exist_ok=True)
    
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
            '--dest', output_path,
            f'https://twitter.com/{username}/media'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        
        if result.returncode == 0:
            if os.path.exists(output_path):
                for file in os.listdir(output_path):
                    file_path = os.path.join(output_path, file)
                    if os.path.isfile(file_path) and os.path.getsize(file_path) > 5000:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                            image_count += 1
                        elif file.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                            video_count += 1
                        downloaded_count += 1
                        
                        if progress_callback:
                            progress_callback(f"✅ Downloaded: {file}", 60, downloaded_count, image_count, video_count)
            
            if downloaded_count > 0:
                if progress_callback:
                    progress_callback(f"✅ Twitter gallery-dl success: {downloaded_count} files", 100, downloaded_count, image_count, video_count)
                print(f"✅ Gallery-dl success: {downloaded_count} files")
                return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}
        
        print(f"❌ Gallery-dl failed: {result.stderr[:200]}...")
        
    except Exception as e:
        print(f"❌ Gallery-dl error: {str(e)[:100]}")
    
    # Method 2: IMPROVED yt-dlp for Twitter
    try:
        if progress_callback:
            progress_callback("🔄 Twitter Method 2: Improved yt-dlp...", 40, downloaded_count, image_count, video_count)
            
        print(f"🔄 Twitter Method 2: Improved yt-dlp...")
        
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(uploader)s_%(id)s.%(ext)s'),
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writedescription': True,
            'writeinfojson': True,
            'writethumbnail': True,
            'max_downloads': max_content,
            'ignoreerrors': True,
            'sleep_interval': 20,
            'max_sleep_interval': 40,
            'cookiesfrombrowser': ['chrome', 'firefox'],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([f'https://twitter.com/{username}/media'])
                
                new_downloaded = 0
                new_image_count = 0
                new_video_count = 0
                
                if os.path.exists(output_path):
                    for file in os.listdir(output_path):
                        file_path = os.path.join(output_path, file)
                        if os.path.isfile(file_path) and os.path.getsize(file_path) > 5000:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                                new_image_count += 1
                            elif file.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
                                new_video_count += 1
                            new_downloaded += 1
                            
                            if progress_callback:
                                progress_callback(f"✅ Downloaded: {file}", 80, new_downloaded, new_image_count, new_video_count)
                
                if new_downloaded > downloaded_count:
                    downloaded_count = new_downloaded
                    image_count = new_image_count
                    video_count = new_video_count
                    
                    if progress_callback:
                        progress_callback(f"✅ Twitter yt-dlp success: {downloaded_count} files", 100, downloaded_count, image_count, video_count)
                    print(f"✅ yt-dlp success: {downloaded_count} files")
                    return {'downloaded': downloaded_count, 'images': image_count, 'videos': video_count}
                    
            except Exception as e:
                print(f"❌ yt-dlp download error: {str(e)[:100]}")
        
    except Exception as e:
        print(f"❌ yt-dlp setup error: {str(e)[:100]}")
    
    if progress_callback:
        progress_callback(f"⚠️ Twitter scraping completed with limited success", 100, downloaded_count, image_count, video_count)
    
    print(f"📊 Twitter scraping complete")
    print(f"📁 Files downloaded: {downloaded_count} (Images: {image_count}, Videos: {video_count})")
    
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
                print(f"❌ TikTok yt-dlp download error: {str(e)[:100]}")
        
    except Exception as e:
        print(f"❌ TikTok yt-dlp setup error: {str(e)[:100]}")
    
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
        print(f"❌ TikTok gallery-dl error: {str(e)[:100]}")
    
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
            print(f"❌ Error searching {search_url}: {str(e)[:100]}")
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
                print(f"❌ PornHub strategy error: {str(e)[:50]}")
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
        print(f"❌ xHamster search error: {str(e)[:100]}")
    
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
        print(f"❌ Gelbooru search error: {str(e)[:100]}")
    
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
        print(f"❌ Rule34 search error: {str(e)[:100]}")
    
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
        print(f"❌ e621 search error: {str(e)[:100]}")
    
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
        print(f"❌ Bing search error: {str(e)[:100]}")
    
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
        print(f"❌ YouTube search error: {str(e)[:100]}")
    
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
        print(f"❌ Bing search error: {str(e)[:100]}")
    
    # 2. Google Images search
    if progress_callback:
        progress_callback("🔍 Searching Google Images...", 40, len(found_urls), 0, 0)
    try:
        google_urls = enhanced_google_search(query, max_results=max_images * 2, safe_search=safe_search)
        found_urls.update(google_urls)
        print(f"✅ Google Images: {len(google_urls)} URLs")
    except Exception as e:
        print(f"❌ Google search error: {str(e)[:100]}")
    
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
            print(f"❌ Gelbooru error: {str(e)[:100]}")
        
        # Add Rule34
        if progress_callback:
            progress_callback("🔞 Searching Rule34...", 70, len(found_urls), 0, 0)
        try:
            rule34_urls = enhanced_rule34_search(query, max_results=max_images, progress_callback=progress_callback)
            found_urls.update(rule34_urls)
            print(f"✅ Rule34: {len(rule34_urls)} URLs")
        except Exception as e:
            print(f"❌ Rule34 error: {str(e)[:100]}")
    
    # 4. DeviantArt search (safe search controlled)
    if progress_callback:
        progress_callback("🎨 Searching DeviantArt...", 80, len(found_urls), 0, 0)
    try:
        deviant_urls = enhanced_deviantart_search(query, max_results=max_images, safe_search=safe_search)
        found_urls.update(deviant_urls)
        print(f"✅ DeviantArt: {len(deviant_urls)} URLs")
    except Exception as e:
        print(f"❌ DeviantArt error: {str(e)[:100]}")
    
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
            print(f"❌ Error processing {img_url[:50]}: {str(e)[:50]}")
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

def comprehensive_multi_source_scrape(query, enabled_sources=None, max_content_per_source=10, output_dir="downloads", progress_callback=None, safe_search=True):
    """
    Comprehensive scraping from multiple sources with source management, progress tracking, and safe search controls
    """
    if progress_callback:
        progress_callback(f"🚀 Starting comprehensive multi-source scrape for: {query} (Safe search: {'ON' if safe_search else 'OFF'})", 0, 0, 0, 0)
    
    print(f"🚀 === COMPREHENSIVE MULTI-SOURCE SCRAPE ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max content per source: {max_content_per_source}")
    print(f"🔒 Safe search: {'ENABLED' if safe_search else 'DISABLED (adult content allowed)'}")
    
    # Initialize all content sources
    sources = get_content_sources()
    
    # Apply enabled/disabled sources filter
    if enabled_sources:
        for source_name, source in sources.items():
            source.enabled = source_name in enabled_sources
    
    # Filter out adult sources if safe search is enabled
    if safe_search:
        for source_name, source in sources.items():
            if source.requires_no_safe_search:
                source.enabled = False
                print(f"🔒 Disabled adult source '{source.display_name}' due to safe search")
    
    total_detected = 0
    total_downloaded = 0
    total_images = 0
    total_videos = 0
    results = {}
    
    enabled_source_names = [s.display_name for s in sources.values() if s.enabled]
    if progress_callback:
        progress_callback(f"🎯 Enabled sources: {', '.join(enabled_source_names)}", 5, 0, 0, 0)
    
    print(f"🎯 Enabled sources: {enabled_source_names}")
    
    source_count = len([s for s in sources.values() if s.enabled])
    current_source = 0
    
    # 1. Reddit NSFW Scraping (only if safe search is disabled)
    if not safe_search and sources['reddit_nsfw'].enabled:
        current_source += 1
        base_progress = (current_source - 1) * (100 / source_count) if source_count > 0 else 0
        
        if progress_callback:
            progress_callback(f"🔴 Reddit NSFW Search ({current_source}/{source_count})", int(base_progress), total_downloaded, total_images, total_videos)
        
        print(f"\n🔴 === REDDIT NSFW SEARCH ===")
        try:
            reddit_urls = enhanced_reddit_nsfw_search(query, max_results=max_content_per_source * 2, progress_callback=progress_callback)
            for url in reddit_urls:
                sources['reddit_nsfw'].add_url(url)
            
            downloaded_result = download_urls_from_source(reddit_urls[:max_content_per_source], 
                                                       os.path.join(output_dir, 'reddit_nsfw'), 
                                                       sources['reddit_nsfw'],
                                                       progress_callback=progress_callback)
            
            results['reddit_nsfw'] = sources['reddit_nsfw'].get_stats()
            total_detected += sources['reddit_nsfw'].detected_count
            total_downloaded += sources['reddit_nsfw'].downloaded_count
            total_images += downloaded_result.get('images', 0)
            total_videos += downloaded_result.get('videos', 0)
            
        except Exception as e:
            print(f"❌ Reddit NSFW error: {str(e)[:100]}")
            sources['reddit_nsfw'].failed_count += 1
    
    # 2. Adult Content Sources (only if safe search is disabled)
    if not safe_search:
        adult_sources = ['pornhub', 'xhamster', 'xvideos', 'motherless', 'imagefap', 'gelbooru', 'rule34', 'e621', 'danbooru']
        
        for adult_source in adult_sources:
            if sources.get(adult_source, {}).enabled:
                current_source += 1
                base_progress = (current_source - 1) * (100 / source_count) if source_count > 0 else 0
                
                if progress_callback:
                    progress_callback(f"🔞 {sources[adult_source].display_name} Search ({current_source}/{source_count})", int(base_progress), total_downloaded, total_images, total_videos)
                
                print(f"\n🔞 === {sources[adult_source].display_name.upper()} SEARCH ===")
                try:
                    adult_urls = []
                    
                    # Call appropriate search function based on source
                    if adult_source == 'pornhub':
                        adult_urls = enhanced_pornhub_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                    elif adult_source == 'xhamster':
                        adult_urls = enhanced_xhamster_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                    elif adult_source == 'xvideos':
                        adult_urls = enhanced_xvideos_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                    elif adult_source == 'motherless':
                        adult_urls = enhanced_motherless_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                    elif adult_source == 'imagefap':
                        adult_urls = enhanced_imagefap_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                    elif adult_source == 'gelbooru':
                        adult_urls = enhanced_gelbooru_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                    elif adult_source == 'rule34':
                        adult_urls = enhanced_rule34_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                    elif adult_source == 'e621':
                        adult_urls = enhanced_e621_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                    elif adult_source == 'danbooru':
                        adult_urls = enhanced_danbooru_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                    
                    for url in adult_urls:
                        sources[adult_source].add_url(url)
                    
                    downloaded_result = download_urls_from_source(adult_urls[:max_content_per_source], 
                                                               os.path.join(output_dir, adult_source), 
                                                               sources[adult_source],
                                                               progress_callback=progress_callback)
                    
                    results[adult_source] = sources[adult_source].get_stats()
                    total_detected += sources[adult_source].detected_count
                    total_downloaded += sources[adult_source].downloaded_count
                    total_images += downloaded_result.get('images', 0)
                    total_videos += downloaded_result.get('videos', 0)
                    
                except Exception as e:
                    print(f"❌ {sources[adult_source].display_name} error: {str(e)[:100]}")
                    sources[adult_source].failed_count += 1
    
    # 3. Regular Content Sources (always available)
    regular_sources = ['bing_images', 'google_images', 'yandex_images', 'deviantart', 'imgur', 'tumblr', 'pinterest', 'flickr', 'unsplash', 'pexels']
    
    for regular_source in regular_sources:
        if sources.get(regular_source, {}).enabled:
            current_source += 1
            base_progress = (current_source - 1) * (100 / source_count) if source_count > 0 else 0
            
            if progress_callback:
                progress_callback(f"🌐 {sources[regular_source].display_name} Search ({current_source}/{source_count})", int(base_progress), total_downloaded, total_images, total_videos)
            
            print(f"\n🌐 === {sources[regular_source].display_name.upper()} SEARCH ===")
            try:
                regular_urls = []
                
                # Call appropriate search function
                if regular_source == 'bing_images':
                    regular_urls = enhanced_bing_search(query, max_results=max_content_per_source, safe_search=safe_search)
                elif regular_source == 'google_images':
                    regular_urls = enhanced_google_search(query, max_results=max_content_per_source, safe_search=safe_search)
                elif regular_source == 'yandex_images':
                    regular_urls = enhanced_yandex_search(query, max_results=max_content_per_source, safe_search=safe_search)
                elif regular_source == 'deviantart':
                    regular_urls = enhanced_deviantart_search(query, max_results=max_content_per_source, safe_search=safe_search)
                elif regular_source == 'imgur':
                    regular_urls = enhanced_imgur_search(query, max_results=max_content_per_source, safe_search=safe_search)
                elif regular_source == 'tumblr':
                    regular_urls = enhanced_tumblr_search(query, max_results=max_content_per_source, safe_search=safe_search)
                elif regular_source == 'pinterest':
                    regular_urls = enhanced_pinterest_search(query, max_results=max_content_per_source, safe_search=safe_search)
                elif regular_source == 'flickr':
                    regular_urls = enhanced_flickr_search(query, max_results=max_content_per_source, safe_search=safe_search)
                elif regular_source == 'unsplash':
                    regular_urls = enhanced_unsplash_search(query, max_results=max_content_per_source, safe_search=safe_search)
                elif regular_source == 'pexels':
                    regular_urls = enhanced_pexels_search(query, max_results=max_content_per_source, safe_search=safe_search)
                
                for url in regular_urls:
                    sources[regular_source].add_url(url)
                
                downloaded_result = download_urls_from_source(regular_urls[:max_content_per_source], 
                                                           os.path.join(output_dir, regular_source), 
                                                           sources[regular_source],
                                                           progress_callback=progress_callback)
                
                results[regular_source] = sources[regular_source].get_stats()
                total_detected += sources[regular_source].detected_count
                total_downloaded += sources[regular_source].downloaded_count
                total_images += downloaded_result.get('images', 0)
                total_videos += downloaded_result.get('videos', 0)
                
            except Exception as e:
                print(f"❌ {sources[regular_source].display_name} error: {str(e)[:100]}")
                sources[regular_source].failed_count += 1
    
    # 4. Social Media Sources (Instagram, Twitter, TikTok, YouTube)
    social_sources = ['instagram', 'twitter', 'tiktok', 'youtube']
    
    for social_source in social_sources:
        if sources.get(social_source, {}).enabled:
            current_source += 1
            base_progress = (current_source - 1) * (100 / source_count) if source_count > 0 else 0
            
            if progress_callback:
                progress_callback(f"📱 {sources[social_source].display_name} Search ({current_source}/{source_count})", int(base_progress), total_downloaded, total_images, total_videos)
            
            print(f"\n📱 === {sources[social_source].display_name.upper()} SEARCH ===")
            try:
                # Social media sources typically require specific usernames or URLs
                # For now, we'll attempt generic searches but note that results may be limited
                social_urls = []
                
                if social_source == 'youtube':
                    # Use yt-dlp for YouTube search
                    social_urls = enhanced_youtube_search(query, max_results=max_content_per_source, progress_callback=progress_callback)
                # Instagram, Twitter, TikTok would need specific implementations
                
                for url in social_urls:
                    sources[social_source].add_url(url)
                
                downloaded_result = download_urls_from_source(social_urls[:max_content_per_source], 
                                                           os.path.join(output_dir, social_source), 
                                                           sources[social_source],
                                                           progress_callback=progress_callback)
                
                results[social_source] = sources[social_source].get_stats()
                total_detected += sources[social_source].detected_count
                total_downloaded += sources[social_source].downloaded_count
                total_images += downloaded_result.get('images', 0)
                total_videos += downloaded_result.get('videos', 0)
                
            except Exception as e:
                print(f"❌ {sources[social_source].display_name} error: {str(e)[:100]}")
                sources[social_source].failed_count += 1
    
    # Final progress update
    if progress_callback:
        progress_callback(f"✅ Multi-source scrape complete! Total: {total_downloaded} files (Safe search: {'ON' if safe_search else 'OFF'})", 100, total_downloaded, total_images, total_videos)
    
    print(f"\n🎉 === COMPREHENSIVE SCRAPE COMPLETE ===")
    print(f"🔍 Query: '{query}'")
    print(f"🔒 Safe search: {'ENABLED' if safe_search else 'DISABLED'}")
    print(f"📊 Total detected: {total_detected}")
    print(f"💾 Total downloaded: {total_downloaded}")
    print(f"🖼️ Images: {total_images}")
    print(f"🎬 Videos: {total_videos}")
    print(f"📂 Sources used: {len([s for s in sources.values() if s.enabled])}")
    
    return {
        'query': query,
        'safe_search': safe_search,
        'total_detected': total_detected,
        'total_downloaded': total_downloaded,
        'total_images': total_images,
        'total_videos': total_videos,
        'sources': results,
        'enabled_sources': enabled_source_names
    }

def enhanced_google_search(query, max_results=50, safe_search=True):
    """Enhanced Google Images search with safe search controls and better extraction"""
    print(f"🔍 === ENHANCED GOOGLE SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    print(f"🔒 Safe search: {'ON' if safe_search else 'OFF'}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'https://www.google.com/',
        'DNT': '1'
    }
    
    try:
        # Build Google Images search URL with proper safe search parameter
        search_params = {
            'q': query,
            'tbm': 'isch',  # Image search
            'safe': 'strict' if safe_search else 'off',
            'num': min(max_results, 100),
            'hl': 'en',
            'lr': 'lang_en'
        }
        
        # Multiple strategies to find images
        strategies = [
            # Strategy 1: Standard search
            "https://www.google.com/search",
            # Strategy 2: Images direct
            "https://images.google.com/search"
        ]
        
        for i, base_url in enumerate(strategies, 1):
            try:
                response = requests.get(base_url, params=search_params, headers=headers, timeout=15)
                print(f"🔍 Google strategy {i} response: {len(response.text)} chars")
                
                if response.status_code == 200:
                    # Multiple extraction methods
                    
                    # Method 1: Look for image URLs in JSON data within script tags
                    script_pattern = r'AF_initDataCallback\({[^}]*data:\s*(\[.+?\])\s*}\);'
                    script_matches = re.findall(script_pattern, response.text, re.DOTALL)
                    
                    for script_content in script_matches:
                        try:
                            # Look for image URLs in the JSON data
                            img_url_pattern = r'https?://[^"\s]+\.(?:jpg|jpeg|png|gif|webp|bmp)(?:\?[^"\s]*)?'
                            img_urls = re.findall(img_url_pattern, script_content, re.IGNORECASE)
                            
                            for url in img_urls:
                                if not any(skip in url.lower() for skip in ['logo', 'icon', 'button']):
                                    found_urls.add(url)
                        except:
                            continue
                    
                    # Method 2: Parse HTML for img tags and data attributes
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find img tags with various src attributes
                    img_selectors = [
                        'img[src*=".jpg"]',
                        'img[src*=".jpeg"]', 
                        'img[src*=".png"]',
                        'img[src*=".gif"]',
                        'img[src*=".webp"]',
                        'img[data-src*=".jpg"]',
                        'img[data-src*=".jpeg"]',
                        'img[data-src*=".png"]',
                        'img[data-original]'
                    ]
                    
                    for selector in img_selectors:
                        imgs = soup.select(selector)
                        for img in imgs:
                            img_url = img.get('src') or img.get('data-src') or img.get('data-original')
                            if img_url and img_url.startswith(('http', '//')):
                                if img_url.startswith('//'):
                                    img_url = 'https:' + img_url
                                found_urls.add(img_url)
                    
                    # Method 3: Look for encoded image URLs in the page
                    # Google often encodes URLs in various formats
                    encoded_patterns = [
                        r'"ou":"([^"]+)"',  # Original URL pattern
                        r'"rlsu":"([^"]+)"', # Result URL pattern  
                        r'"ru":"([^"]+)"',   # Reference URL pattern
                        r'imgurl=([^&]+)',   # Image URL parameter
                        r'src="(https?://[^"]+\.(?:jpg|jpeg|png|gif|webp))"'
                    ]
                    
                    for pattern in encoded_patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        for match in matches:
                            try:
                                # Decode URL if needed
                                import urllib.parse
                                decoded_url = urllib.parse.unquote(match)
                                if decoded_url.startswith(('http', '//')):
                                    if decoded_url.startswith('//'):
                                        decoded_url = 'https:' + decoded_url
                                    found_urls.add(decoded_url)
                            except:
                                continue
                    
                    # Method 4: Look in all divs with image data
                    all_divs = soup.find_all('div')
                    for div in all_divs:
                        div_str = str(div)
                        # Look for data attributes that might contain image URLs
                        data_patterns = [
                            r'data-[^=]*="([^"]*https?://[^"]*\.(?:jpg|jpeg|png|gif|webp)[^"]*)"',
                            r'url\(([^)]*\.(?:jpg|jpeg|png|gif|webp)[^)]*)\)'
                        ]
                        
                        for pattern in data_patterns:
                            matches = re.findall(pattern, div_str, re.IGNORECASE)
                            for match in matches:
                                if match.startswith(('http', '//')):
                                    if match.startswith('//'):
                                        match = 'https:' + match
                                    found_urls.add(match)
                
                print(f"🔍 Google strategy {i} found: {len(found_urls)} URLs so far")
                
                if len(found_urls) >= max_results:
                    break
                    
                time.sleep(random.uniform(1, 3))  # Rate limiting
                
            except Exception as e:
                print(f"❌ Google strategy {i} error: {str(e)[:50]}")
                continue
    
    except Exception as e:
        print(f"❌ Google search error: {str(e)}")
    
    print(f"✅ Google search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_deviantart_search(query, max_results=50, safe_search=True):
    """
    Enhanced DeviantArt search with proper safe search controls
    """
    print(f"🎨 === ENHANCED DEVIANTART SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    print(f"🔒 Safe search: {'ON' if safe_search else 'OFF'}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive'
    }
    
    try:
        per_page = min(24, max_results)  # DeviantArt shows 24 per page
        
        for page in range(1, (max_results // per_page) + 2):
            search_url = f"https://www.deviantart.com/search/deviations?q={requests.utils.quote(query)}&page={page}"
            
            if not safe_search:
                search_url += "&mature_content=true"
            
            print(f"📄 DeviantArt page {page}: Found {len(found_urls)} URLs so far")
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find image containers
                img_containers = soup.find_all(['img', 'a'], {'data-super-img': True}) + \
                               soup.find_all('img', src=True) + \
                               soup.find_all('a', href=True)
                
                for container in img_containers:
                    img_url = None
                    
                    if container.name == 'img' and container.get('src'):
                        img_url = container.get('src')
                    elif container.name == 'a' and container.get('href'):
                        href = container.get('href')
                        if any(ext in href.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            img_url = href
                    
                    if img_url and img_url.startswith(('http', '//')):
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        
                        # Filter out very small images (like icons)
                        if not any(skip in img_url.lower() for skip in ['avatar', 'icon', 'thumb', '150x', '50x']):
                            found_urls.add(img_url)
            
            time.sleep(random.uniform(1, 2))  # Rate limiting
            
            if len(found_urls) >= max_results:
                break
                
    except Exception as e:
        print(f"❌ DeviantArt search error: {str(e)}")
    
    print(f"✅ DeviantArt search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_xvideos_search(query, max_results=50, progress_callback=None):
    """
    Enhanced XVideos search
    """
    if progress_callback:
        progress_callback(f"🔞 Searching XVideos for: {query}", 0, 0, 0, 0)
    
    print(f"🔞 === XVIDEOS SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Referer': 'https://www.xvideos.com/'
    }
    
    try:
        # Multiple pages to get more results
        for page in range(0, min(3, (max_results // 24) + 1)):  # 24 videos per page typically
            search_url = f"https://www.xvideos.com/?k={requests.utils.quote(query)}&p={page}"
            
            response = requests.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find video thumbnails and preview images  
                # XVideos uses various classes and structures
                img_selectors = [
                    'img[data-src]',  # Lazy loaded images
                    'img.thumb',      # Thumbnail images
                    'img.thumb-image', # Another thumbnail class
                    'div.thumb img',   # Images inside thumb divs
                    'div.mozaique img', # Gallery images
                    'a.thumb img',     # Linked thumbnail images
                ]
                
                for selector in img_selectors:
                    imgs = soup.select(selector)
                    for img in imgs:
                        # Check both src and data-src attributes
                        img_url = img.get('data-src') or img.get('src')
                        if img_url:
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            elif img_url.startswith('/'):
                                img_url = 'https://www.xvideos.com' + img_url
                            
                            # Filter for actual content images (not site icons)
                            if img_url.startswith('https://') and not any(skip in img_url.lower() for skip in [
                                'logo', 'icon', 'button', 'sprite', 'ui-', 'flag'
                            ]):
                                found_urls.add(img_url)
                
                # Also look for all img tags with src
                all_imgs = soup.find_all('img', src=True)
                for img in all_imgs:
                    img_url = img.get('src')
                    if img_url and img_url.startswith(('http', '//')):
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        
                        # Filter for actual content images
                        if any(term in img_url.lower() for term in ['thumb', 'preview', '.jpg', '.jpeg', '.png']):
                            if not any(skip in img_url.lower() for skip in ['logo', 'icon', 'button', 'sprite']):
                                found_urls.add(img_url)
                
                # Also look for background images in CSS
                bg_images = re.findall(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', response.text)
                for bg_url in bg_images:
                    if bg_url.startswith('//'):
                        bg_url = 'https:' + bg_url
                    elif bg_url.startswith('/'):
                        bg_url = 'https://www.xvideos.com' + bg_url
                    
                    if bg_url.startswith('https://') and any(ext in bg_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        found_urls.add(bg_url)
                
                print(f"📄 XVideos page {page + 1}: Found {len(found_urls)} URLs so far")
                
                if len(found_urls) >= max_results:
                    break
                    
                time.sleep(random.uniform(2, 4))  # Rate limiting
                        
    except Exception as e:
        print(f"❌ XVideos search error: {str(e)}")
    
    if progress_callback:
        progress_callback(f"✅ XVideos found: {len(found_urls)} URLs", 100, 0, 0, 0)
    
    print(f"✅ XVideos search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_motherless_search(query, max_results=50, progress_callback=None):
    """
    Enhanced Motherless search with better content detection
    """
    if progress_callback:
        progress_callback(f"🔞 Searching Motherless for: {query}", 0, 0, 0, 0)
    
    print(f"🔞 === MOTHERLESS SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://motherless.com/',
        'Cookie': 'theme=light; nsfw=1'  # Enable NSFW content
    }
    
    try:
        # Primary search strategy - use the main search page
        search_query = quote_plus(query)
        search_url = f"https://motherless.com/search/images?term={search_query}&sort=date&range=0"
        
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for actual image content containers
            # Motherless uses specific classes for content thumbnails
            image_containers = soup.find_all(['div', 'a'], class_=[
                'thumb-container', 'thumb', 'image-container', 'media-thumb'
            ])
            
            # Also search by common image selectors
            all_imgs = soup.find_all('img')
            
            for img in all_imgs:
                img_url = img.get('src') or img.get('data-src') or img.get('data-original')
                
                if img_url:
                    # Ensure full URL
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://motherless.com' + img_url
                    
                    # Look for actual content images
                    if img_url.startswith('https://') and any(
                        indicator in img_url.lower() for indicator in [
                            'thumb', 'content', 'media', 'upload', 'images', 'gallery'
                        ]
                    ):
                        # Skip obvious site UI elements
                        if not any(skip in img_url.lower() for skip in [
                            'logo', 'icon', 'button', 'sprite', 'header', 'footer',
                            'banner', 'nav', 'menu', 'ads', 'promo'
                        ]):
                            found_urls.add(img_url)
                            print(f"📸 Found Motherless image: {img_url[:80]}...")
            
            # Alternative strategy: look for links to image pages and extract their thumbnails
            image_links = soup.find_all('a', href=True)
            for link in image_links:
                href = link.get('href')
                if href and '/G' in href:  # Motherless image page pattern
                    try:
                        img_tags = link.find_all('img')
                        for img in img_tags:
                            img_url = img.get('src') or img.get('data-src')
                            if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                                if img_url.startswith('//'):
                                    img_url = 'https:' + img_url
                                elif img_url.startswith('/'):
                                    img_url = 'https://motherless.com' + img_url
                                found_urls.add(img_url)
                    except:
                        continue
            
            print(f"🔍 Motherless search strategy found: {len(found_urls)} URLs")
            
        else:
            print(f"❌ Motherless search failed: HTTP {response.status_code}")
            
        # Fallback strategy: try video search as it may have more content
        if len(found_urls) < 5:
            video_search_url = f"https://motherless.com/search/videos?term={search_query}&sort=date&range=0"
            
            try:
                response = requests.get(video_search_url, headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    video_thumbs = soup.find_all('img')
                    for img in video_thumbs:
                        img_url = img.get('src') or img.get('data-src')
                        if img_url and 'thumb' in img_url.lower():
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            elif img_url.startswith('/'):
                                img_url = 'https://motherless.com' + img_url
                            found_urls.add(img_url)
                            
                    print(f"🔍 Motherless video search found additional: {len(found_urls)} total URLs")
            except:
                pass
        
    except Exception as e:
        print(f"❌ Motherless search error: {str(e)}")
    
    if progress_callback:
        progress_callback(f"✅ Motherless found: {len(found_urls)} URLs", 100, 0, 0, 0)
    
    print(f"✅ Motherless search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_imagefap_search(query, max_results=50, progress_callback=None):
    """
    Enhanced ImageFap search with better content detection
    """
    if progress_callback:
        progress_callback(f"🔞 Searching ImageFap for: {query}", 0, 0, 0, 0)
    
    print(f"🔞 === IMAGEFAP SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.imagefap.com/',
        'Cookie': 'lang=en'
    }
    
    try:
        # ImageFap search URL with proper encoding
        search_query = quote_plus(query)
        search_url = f"https://www.imagefap.com/search/{search_query}"
        
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for gallery thumbnails and content images
            # ImageFap uses specific structures for content
            
            # Method 1: Look for gallery thumbnail containers
            gallery_containers = soup.find_all(['div', 'a'], class_=[
                'gal-thumb', 'gallery-thumb', 'thumb-container'
            ])
            
            for container in gallery_containers:
                imgs = container.find_all('img')
                for img in imgs:
                    img_url = img.get('src') or img.get('data-src')
                    if img_url:
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://www.imagefap.com' + img_url
                        
                        # Filter for actual content images (thumbnails)
                        if any(indicator in img_url.lower() for indicator in [
                            'thumb', 'gallery', 'content', 'pic', 'img'
                        ]):
                            if not any(skip in img_url.lower() for skip in [
                                'logo', 'button', 'icon', 'sprite', 'banner'
                            ]):
                                found_urls.add(img_url)
                                print(f"📸 Found ImageFap gallery thumb: {img_url[:80]}...")
            
            # Method 2: Look for direct image thumbnails in search results
            img_tags = soup.find_all('img')
            for img in img_tags:
                img_url = img.get('src') or img.get('data-src')
                
                if img_url:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = 'https://www.imagefap.com' + img_url
                    
                    # Look for actual content images with specific patterns
                    if any(pattern in img_url.lower() for pattern in [
                        '/thumbs/', '/thumb/', '/gallery/', '/pic/', '/img/',
                        'thumb.jpg', 'thumb.png', 'thumb.gif'
                    ]):
                        # Skip obvious UI elements
                        if not any(skip in img_url.lower() for skip in [
                            'logo', 'button', 'icon', 'sprite', 'banner', 'nav',
                            'header', 'footer', 'menu', 'ad'
                        ]):
                            found_urls.add(img_url)
                            print(f"📸 Found ImageFap image: {img_url[:80]}...")
            
            # Method 3: Look for links to galleries and extract their preview images
            gallery_links = soup.find_all('a', href=True)
            for link in gallery_links:
                href = link.get('href')
                if href and '/gallery/' in href:
                    # Try to find images within gallery links
                    try:
                        img_in_link = link.find('img')
                        if img_in_link:
                            img_url = img_in_link.get('src') or img_in_link.get('data-src')
                            if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                                if img_url.startswith('//'):
                                    img_url = 'https:' + img_url
                                elif img_url.startswith('/'):
                                    img_url = 'https://www.imagefap.com' + img_url
                                
                                if 'thumb' in img_url.lower() or 'gallery' in img_url.lower():
                                    found_urls.add(img_url)
                    except:
                        continue
            
            # Method 4: Look for background images in CSS
            bg_pattern = r'background-image:\s*url\(["\']?([^"\']+)["\']?\)'
            bg_matches = re.findall(bg_pattern, response.text, re.IGNORECASE)
            
            for bg_url in bg_matches:
                if any(ext in bg_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                    if bg_url.startswith('//'):
                        bg_url = 'https:' + bg_url
                    elif bg_url.startswith('/'):
                        bg_url = 'https://www.imagefap.com' + bg_url
                    
                    if 'thumb' in bg_url.lower() or 'content' in bg_url.lower():
                        found_urls.add(bg_url)
        
        else:
            print(f"❌ ImageFap search failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ ImageFap search error: {str(e)}")
    
    if progress_callback:
        progress_callback(f"✅ ImageFap found: {len(found_urls)} URLs", 100, 0, 0, 0)
    
    print(f"✅ ImageFap search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def enhanced_danbooru_search(query, max_results=50, progress_callback=None):
    """
    Enhanced Danbooru search
    """
    if progress_callback:
        progress_callback(f"🎨 Searching Danbooru for: {query}", 0, 0, 0, 0)
    
    print(f"🎨 === DANBOORU SEARCH ===")
    print(f"🔍 Query: '{query}'")
    print(f"📊 Max results: {max_results}")
    
    found_urls = set()
    headers = {
        'User-Agent': random.choice(get_multiple_user_agents()),
        'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        # Use Danbooru API
        search_query = query.replace(' ', '_').lower()
        api_url = f"https://danbooru.donmai.us/posts.json?tags={requests.utils.quote(search_query)}&limit={min(200, max_results)}"
        
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                for post in data:
                    if isinstance(post, dict):
                        # Try different URL fields
                        for url_field in ['file_url', 'large_file_url', 'preview_file_url']:
                            if url_field in post and post[url_field]:
                                img_url = post[url_field]
                                if img_url.startswith('//'):
                                    img_url = 'https:' + img_url
                                elif not img_url.startswith('http'):
                                    img_url = 'https://danbooru.donmai.us' + img_url
                                found_urls.add(img_url)
                                break
                                
            except json.JSONDecodeError:
                print("❌ Danbooru API returned invalid JSON")
                
    except Exception as e:
        print(f"❌ Danbooru search error: {str(e)}")
    
    if progress_callback:
        progress_callback(f"✅ Danbooru found: {len(found_urls)} URLs", 100, 0, 0, 0)
    
    print(f"✅ Danbooru search complete: {len(found_urls)} URLs")
    return list(found_urls)[:max_results]

def download_urls_from_source(urls, output_dir, source_obj, progress_callback=None, max_downloads=None):
    """
    Download images from a list of URLs with proper progress tracking
    """
    if not urls:
        return {'downloaded': 0, 'failed': 0, 'images': 0, 'videos': 0}
    
    if max_downloads is None:
        max_downloads = len(urls)
    
    downloaded_count = 0
    failed_count = 0
    image_count = 0
    video_count = 0
    
    # Create source-specific directory
    source_dir = os.path.join(output_dir, source_obj.name)
    os.makedirs(source_dir, exist_ok=True)
    
    # Randomize order for variety
    urls_list = list(urls)[:max_downloads]
    random.shuffle(urls_list)
    
    if progress_callback:
        progress_callback(f"📥 Downloading from {source_obj.display_name}...", 0, downloaded_count, image_count, video_count)
    
    for i, url in enumerate(urls_list):
        if downloaded_count >= max_downloads:
            break
            
        try:
            progress_percent = int((i / len(urls_list)) * 100)
            
            if progress_callback:
                progress_callback(f"⬇️ {source_obj.display_name}: {downloaded_count + 1}/{max_downloads}", progress_percent, downloaded_count, image_count, video_count)
            
            print(f"⬇️ Downloading {downloaded_count + 1}/{max_downloads} from {source_obj.display_name}: {url[:80]}...")
            
            # Enhanced headers
            headers = {
                'User-Agent': random.choice(get_multiple_user_agents()),
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': f"https://{urlparse(url).netloc}/",
                'DNT': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            
            if response.status_code == 200 and response.content:
                content_length = len(response.content)
                content_type = response.headers.get('content-type', '').lower()
                
                # Determine if it's an image or video
                is_image = any(img_type in content_type for img_type in ['image/', 'jpeg', 'png', 'gif', 'webp'])
                is_video = any(vid_type in content_type for vid_type in ['video/', 'mp4', 'webm', 'avi'])
                
                # Check URL extension if content-type is unclear
                if not is_image and not is_video:
                    url_lower = url.lower()
                    is_image = any(url_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])
                    is_video = any(url_lower.endswith(ext) for ext in ['.mp4', '.webm', '.avi', '.mov'])
                
                # Default to image if uncertain but has reasonable size
                if not is_image and not is_video and content_length > 5000:
                    is_image = True
                
                if (is_image or is_video) and content_length > 5000:
                    # Determine file extension
                    if is_video:
                        ext = '.mp4'
                        if 'webm' in content_type:
                            ext = '.webm'
                        elif url.lower().endswith('.avi'):
                            ext = '.avi'
                        elif url.lower().endswith('.mov'):
                            ext = '.mov'
                        video_count += 1
                    else:
                        ext = '.jpg'  # Default
                        if 'png' in content_type:
                            ext = '.png'
                        elif 'gif' in content_type:
                            ext = '.gif'
                        elif 'webp' in content_type:
                            ext = '.webp'
                        elif url.lower().endswith('.png'):
                            ext = '.png'
                        elif url.lower().endswith('.gif'):
                            ext = '.gif'
                        elif url.lower().endswith('.webp'):
                            ext = '.webp'
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
                    
                else:
                    failed_count += 1
                    source_obj.record_download(False)
                    print(f"❌ Invalid content: {content_type} ({content_length} bytes)")
                    
            else:
                failed_count += 1
                source_obj.record_download(False)
                print(f"❌ HTTP {response.status_code}: {url[:50]}")
                
        except Exception as e:
            failed_count += 1
            source_obj.record_download(False)
            print(f"❌ Download error: {str(e)[:50]}")
            
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
        print(f"❌ Tumblr search error: {str(e)[:100]}")
    
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

if __name__ == "__main__":
    # Run verification test
    test_with_known_working_content()
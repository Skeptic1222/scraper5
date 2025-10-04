# Implementation Priority Roadmap
**Generated**: October 3, 2025
**Based on**: Comprehensive log analysis, online research, and performance metrics
**Current System Status**: Enhanced with multi-method framework, source filtering, image quality filtering

---

## 🎯 Quick Wins (Immediate - This Week)

### 1. Test Current Improvements ⏱️ 30 minutes
**Status**: READY TO TEST
**Why**: Validate recent installations and integrations
**Action**:
```bash
cd C:\inetpub\wwwroot\scraper
python test_complete_integration.py
```

**Then run a live test job**:
- Query: "twerking" or "test"
- Sources: pornhub, xvideos, youtube, unsplash, pexels (5 sources)
- Limit: 25 files
- Monitor: `logs/download_errors.log`

**Expected Results**:
- yt-dlp downloads working for video sources
- Source filtering removes blacklisted sources
- Image quality filtering removes placeholders
- Multi-method framework showing fallback attempts

---

### 2. Configure gallery-dl ⏱️ 1-2 hours
**Status**: Tool installed, needs configuration
**Impact**: Unlock 10+ image gallery sources (Imgur, Flickr, DeviantArt, etc.)
**Effort**: LOW

**Implementation**:
```bash
# 1. Create config directory
mkdir -p ~/.config/gallery-dl

# 2. Create config file
cat > ~/.config/gallery-dl/config.json << 'EOF'
{
  "extractor": {
    "base-directory": "C:/inetpub/wwwroot/scraper/downloads",

    "imgur": {
      "client-id": "YOUR_IMGUR_CLIENT_ID"
    },

    "flickr": {
      "api-key": "YOUR_FLICKR_API_KEY",
      "api-secret": "YOUR_FLICKR_API_SECRET"
    },

    "deviantart": {
      "client-id": "YOUR_DEVIANTART_CLIENT_ID",
      "client-secret": "YOUR_DEVIANTART_CLIENT_SECRET"
    },

    "twitter": {
      "username": "YOUR_TWITTER_USERNAME",
      "password": "YOUR_TWITTER_PASSWORD"
    },

    "reddit": {
      "client-id": "YOUR_REDDIT_CLIENT_ID",
      "client-secret": "YOUR_REDDIT_CLIENT_SECRET"
    }
  }
}
EOF

# 3. Register for API keys:
# - Imgur: https://api.imgur.com/oauth2/addclient
# - Flickr: https://www.flickr.com/services/apps/create/
# - DeviantArt: https://www.deviantart.com/developers/
# - Reddit: https://www.reddit.com/prefs/apps

# 4. Test gallery-dl
gallery-dl --version
gallery-dl "https://imgur.com/gallery/example"
```

**Expected Impact**: +30-50 files across 10 sources

---

### 3. Add Retry Logic to yt-dlp Method ⏱️ 30 minutes
**Status**: Tool working but no retry on transient failures
**Impact**: Improve video download success rate by 15-20%
**Effort**: LOW

**Edit**: `scrapers/scraping_methods.py`

**Add to YtDlpMethod.execute()**:
```python
def execute(self, source: str, query: str, max_results: int, **kwargs) -> MethodResult:
    # ... existing code ...

    # Add retry wrapper around subprocess.run
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                break  # Success
            elif attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"yt-dlp retry {attempt + 1}/{max_retries} for {url}")
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                logger.warning(f"yt-dlp timeout, retrying {attempt + 1}/{max_retries}")
                time.sleep(2 ** attempt)
            else:
                raise
```

**Expected Impact**: Handle network glitches, improve reliability

---

## 🔥 High Priority (This Month)

### 4. Implement Reddit PRAW Scraper ⏱️ 4-6 hours
**Status**: NOT IMPLEMENTED
**Current Success Rate**: 5% (near-zero)
**Target Success Rate**: 60-80%
**Impact**: HIGH (Reddit is major visual content source)
**Effort**: MEDIUM

**Implementation**:

**Step 1**: Install PRAW
```bash
pip install praw
```

**Step 2**: Register Reddit app
- Go to https://www.reddit.com/prefs/apps
- Create "script" type app
- Note client_id, client_secret

**Step 3**: Create `scrapers/reddit_praw_scraper.py`
```python
"""
Reddit PRAW Scraper
High-quality scraping using official Reddit API
"""

import praw
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RedditPRAWMethod:
    """Reddit scraper using PRAW (Python Reddit API Wrapper)"""

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent='EnhancedMediaScraper/3.0'
        )

    def scrape(self, query: str, max_results: int = 100, output_dir: str = 'downloads') -> Dict[str, Any]:
        """
        Scrape Reddit for images and videos

        Args:
            query: Search query or subreddit name
            max_results: Maximum posts to process
            output_dir: Download directory

        Returns:
            Dict with download results
        """
        results = {
            'success': False,
            'downloaded': 0,
            'images': 0,
            'videos': 0,
            'files': [],
            'error': None
        }

        try:
            # Determine if query is subreddit or search
            if query.startswith('r/'):
                subreddit = self.reddit.subreddit(query[2:])
                submissions = subreddit.hot(limit=max_results)
            else:
                # Search all of Reddit
                submissions = self.reddit.subreddit('all').search(query, limit=max_results)

            for submission in submissions:
                # Skip text-only posts
                if submission.is_self:
                    continue

                # Process image/video post
                if hasattr(submission, 'url'):
                    url = submission.url

                    # Direct image links
                    if url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                        filepath = self._download_file(url, output_dir)
                        if filepath:
                            results['files'].append({
                                'filepath': filepath,
                                'original_url': url,
                                'title': submission.title,
                                'subreddit': submission.subreddit.display_name
                            })
                            results['images'] += 1

                    # Reddit galleries
                    if hasattr(submission, 'is_gallery') and submission.is_gallery:
                        for item in submission.gallery_data['items']:
                            media_id = item['media_id']
                            media_url = f"https://i.redd.it/{media_id}.jpg"
                            filepath = self._download_file(media_url, output_dir)
                            if filepath:
                                results['files'].append({
                                    'filepath': filepath,
                                    'original_url': media_url,
                                    'title': submission.title
                                })
                                results['images'] += 1

                    # Videos (v.redd.it)
                    if hasattr(submission, 'is_video') and submission.is_video:
                        video_url = submission.media['reddit_video']['fallback_url']
                        filepath = self._download_file(video_url, output_dir)
                        if filepath:
                            results['files'].append({
                                'filepath': filepath,
                                'original_url': video_url,
                                'title': submission.title
                            })
                            results['videos'] += 1

            results['downloaded'] = len(results['files'])
            results['success'] = results['downloaded'] > 0

            logger.info(f"Reddit PRAW: Downloaded {results['downloaded']} files from query '{query}'")

        except Exception as e:
            logger.error(f"Reddit PRAW error: {e}")
            results['error'] = str(e)

        return results

    def _download_file(self, url: str, output_dir: str) -> str:
        """Download a file from URL"""
        import requests
        import hashlib
        from urllib.parse import urlparse

        try:
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Generate filename from URL
            parsed = urlparse(url)
            ext = os.path.splitext(parsed.path)[1] or '.jpg'
            filename = hashlib.md5(url.encode()).hexdigest()[:16] + ext
            filepath = os.path.join(output_dir, 'reddit', filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return filepath

        except Exception as e:
            logger.warning(f"Failed to download {url}: {e}")
            return None
```

**Step 4**: Register as scraping method
Add to `scrapers/scraping_methods.py`:
```python
from scrapers.reddit_praw_scraper import RedditPRAWMethod

# In register_all_methods():
reddit_method = RedditPRAWMethod()
registry.register(ScrapingMethod(
    name="reddit_praw",
    method_type=MethodType.API_DIRECT,
    priority=5,  # Higher priority than generic methods
    enabled=True,
    execute_func=reddit_method.scrape
))
```

**Step 5**: Add environment variables to `.env`
```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

**Expected Impact**: 5% → 60-80% success rate for Reddit

---

### 5. Implement Instaloader for Instagram ⏱️ 4-6 hours
**Status**: NOT IMPLEMENTED
**Current Success Rate**: 0%
**Target Success Rate**: 40-60%
**Impact**: HIGH (major visual content source)
**Effort**: MEDIUM

**Implementation**:

**Step 1**: Install Instaloader
```bash
pip install instaloader
```

**Step 2**: Create `scrapers/instagram_instaloader.py`
```python
"""
Instagram Instaloader Scraper
Official Instagram scraping with session persistence
"""

import instaloader
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class InstagramMethod:
    """Instagram scraper using Instaloader"""

    def __init__(self):
        self.loader = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )

        # Try to load session
        username = os.getenv('INSTAGRAM_USERNAME')
        if username:
            try:
                self.loader.load_session_from_file(username)
                logger.info(f"Loaded Instagram session for {username}")
            except FileNotFoundError:
                logger.warning(f"No saved session for {username}, will need to login")

    def login(self, username: str, password: str):
        """Login to Instagram and save session"""
        try:
            self.loader.login(username, password)
            self.loader.save_session_to_file()
            logger.info(f"Instagram login successful for {username}")
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            raise

    def scrape(self, query: str, max_results: int = 50, output_dir: str = 'downloads') -> Dict[str, Any]:
        """
        Scrape Instagram for images and videos

        Args:
            query: Username or hashtag
            max_results: Maximum posts to download
            output_dir: Download directory

        Returns:
            Dict with download results
        """
        results = {
            'success': False,
            'downloaded': 0,
            'images': 0,
            'videos': 0,
            'files': [],
            'error': None
        }

        try:
            target_dir = os.path.join(output_dir, 'instagram')
            os.makedirs(target_dir, exist_ok=True)

            # Change to target directory for Instaloader
            original_dir = os.getcwd()
            os.chdir(target_dir)

            try:
                if query.startswith('#'):
                    # Hashtag search
                    hashtag = query[1:]
                    logger.info(f"Downloading Instagram hashtag: {hashtag}")

                    for post in instaloader.Hashtag.from_name(self.loader.context, hashtag).get_posts():
                        if len(results['files']) >= max_results:
                            break

                        self.loader.download_post(post, target='#{hashtag}')

                        # Count downloaded files
                        if post.is_video:
                            results['videos'] += 1
                        else:
                            results['images'] += 1

                        results['files'].append({
                            'filepath': f"{target_dir}/#{hashtag}/{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_UTC.jpg",
                            'original_url': f"https://www.instagram.com/p/{post.shortcode}/",
                            'title': post.caption[:100] if post.caption else ''
                        })

                else:
                    # Profile download
                    logger.info(f"Downloading Instagram profile: {query}")

                    profile = instaloader.Profile.from_username(self.loader.context, query)

                    for post in profile.get_posts():
                        if len(results['files']) >= max_results:
                            break

                        self.loader.download_post(post, target=query)

                        if post.is_video:
                            results['videos'] += 1
                        else:
                            results['images'] += 1

                        results['files'].append({
                            'filepath': f"{target_dir}/{query}/{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S')}_UTC.jpg",
                            'original_url': f"https://www.instagram.com/p/{post.shortcode}/",
                            'title': post.caption[:100] if post.caption else ''
                        })

                results['downloaded'] = len(results['files'])
                results['success'] = results['downloaded'] > 0

                logger.info(f"Instagram: Downloaded {results['downloaded']} files from '{query}'")

            finally:
                os.chdir(original_dir)

        except Exception as e:
            logger.error(f"Instagram scraper error: {e}")
            results['error'] = str(e)

        return results
```

**Step 3**: Add to `.env`
```
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
```

**Step 4**: Initial login (one-time)
```python
from scrapers.instagram_instaloader import InstagramMethod

method = InstagramMethod()
method.login(os.getenv('INSTAGRAM_USERNAME'), os.getenv('INSTAGRAM_PASSWORD'))
```

**Step 5**: Register method in `scraping_methods.py`

**Expected Impact**: 0% → 40-60% success rate for Instagram

---

### 6. Implement Twitter/X Scraper (twscrape) ⏱️ 3-4 hours
**Status**: NOT IMPLEMENTED
**Current Success Rate**: 0%
**Target Success Rate**: 30-50%
**Impact**: MEDIUM (important for trending content)
**Effort**: MEDIUM

**Implementation**:

**Step 1**: Install twscrape
```bash
pip install twscrape
```

**Step 2**: Create `scrapers/twitter_scraper.py`
```python
"""
Twitter/X Scraper using twscrape
Modern async Twitter scraping
"""

import asyncio
import os
import logging
from typing import List, Dict, Any
from twscrape import API

logger = logging.getLogger(__name__)

class TwitterMethod:
    """Twitter scraper using twscrape"""

    def __init__(self):
        self.api = API()

    async def add_account(self, username: str, password: str, email: str, email_password: str):
        """Add Twitter account to pool"""
        await self.api.pool.add_account(username, password, email, email_password)
        logger.info(f"Added Twitter account: {username}")

    async def scrape_async(self, query: str, max_results: int = 100, output_dir: str = 'downloads') -> Dict[str, Any]:
        """Async scrape Twitter for images and videos"""
        results = {
            'success': False,
            'downloaded': 0,
            'images': 0,
            'videos': 0,
            'files': [],
            'error': None
        }

        try:
            target_dir = os.path.join(output_dir, 'twitter')
            os.makedirs(target_dir, exist_ok=True)

            # Search tweets
            async for tweet in self.api.search(query, limit=max_results):
                # Process media
                if hasattr(tweet, 'media') and tweet.media:
                    for media in tweet.media:
                        if hasattr(media, 'url'):
                            url = media.url

                            # Download file
                            filepath = await self._download_file_async(url, target_dir)
                            if filepath:
                                results['files'].append({
                                    'filepath': filepath,
                                    'original_url': url,
                                    'title': tweet.rawContent[:100] if tweet.rawContent else ''
                                })

                                if url.endswith('.mp4'):
                                    results['videos'] += 1
                                else:
                                    results['images'] += 1

            results['downloaded'] = len(results['files'])
            results['success'] = results['downloaded'] > 0

            logger.info(f"Twitter: Downloaded {results['downloaded']} files from query '{query}'")

        except Exception as e:
            logger.error(f"Twitter scraper error: {e}")
            results['error'] = str(e)

        return results

    def scrape(self, query: str, max_results: int = 100, output_dir: str = 'downloads') -> Dict[str, Any]:
        """Sync wrapper for async scrape"""
        return asyncio.run(self.scrape_async(query, max_results, output_dir))

    async def _download_file_async(self, url: str, output_dir: str) -> str:
        """Async download file"""
        import aiohttp
        import hashlib
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            ext = os.path.splitext(parsed.path)[1] or '.jpg'
            filename = hashlib.md5(url.encode()).hexdigest()[:16] + ext
            filepath = os.path.join(output_dir, filename)

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    response.raise_for_status()

                    with open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)

            return filepath

        except Exception as e:
            logger.warning(f"Failed to download {url}: {e}")
            return None
```

**Step 3**: Initial account setup (one-time)
```bash
# Add Twitter account to pool
python -c "
from scrapers.twitter_scraper import TwitterMethod
import asyncio

method = TwitterMethod()
asyncio.run(method.add_account(
    username='your_twitter_username',
    password='your_twitter_password',
    email='your_email',
    email_password='your_email_password'
))
"
```

**Expected Impact**: 0% → 30-50% success rate for Twitter/X

---

## 📊 Medium Priority (Next 2 Months)

### 7. Add Proxy Rotation System ⏱️ 6-8 hours
**Impact**: +20-30% success rate for protected sites
**Effort**: MEDIUM

**Options**:
1. **Free proxy lists** (unreliable, good for testing)
2. **Paid services**: BrightData, Oxylabs, SmartProxy ($100-500/month)
3. **Residential proxies**: For Instagram, Twitter, harder targets

**Implementation outline**:
- Create proxy pool manager
- Add proxy testing/validation
- Implement automatic rotation on failure
- Add proxy-specific timeout handling

---

### 8. Implement Cookie/Session Management ⏱️ 2-3 hours
**Impact**: +10-15 files per authenticated source
**Effort**: LOW

**Use cases**:
- Instagram (better quality, more content with login)
- DeviantArt (mature content filter bypass)
- Twitter (higher rate limits with account)

---

### 9. Add Video Quality Selection ⏱️ 3-4 hours
**Impact**: User control over file sizes and quality
**Effort**: MEDIUM

**Features**:
- Quality presets: 480p, 720p, 1080p, 4K
- Automatic fallback if preferred quality unavailable
- Size limits per file

---

### 10. Implement Live Dashboard with WebSockets ⏱️ 8-12 hours
**Impact**: Better user experience
**Effort**: HIGH

**User requested features**:
- Real-time thread count
- Download speed
- File count and types
- Size downloaded
- Filenames with Excel-like progress bars

**Tech stack**:
- Flask-SocketIO for real-time updates
- Progress events from downloader
- React or Vue.js for frontend (optional)

---

## 📈 Performance Targets

### Current Performance (Before Improvements)
- **Success Rate**: 15-20% overall
- **Files per Job**: 10-30 files average
- **Job Duration**: 5-15 minutes (often stalled)
- **Working Sources**: 8-10 out of 118

### Target Performance (After All Improvements)
- **Success Rate**: 50-70% overall
- **Files per Job**: 100-500 files average
- **Job Duration**: 20-60 minutes (full scrape)
- **Working Sources**: 40-60 out of 118

### Immediate Targets (After Quick Wins + High Priority)
- **Success Rate**: 35-45% overall
- **Files per Job**: 50-150 files average
- **Working Sources**: 25-35 out of 118

---

## ✅ Completed Improvements (Reference)

### Already Implemented ✅
1. **Multi-method scraping framework** (4 methods: yt-dlp, gallery-dl, curl_cffi, requests+bs4)
2. **Source filtering** (73 blacklisted sources removed automatically)
3. **Image quality filtering** (15 placeholder patterns detected)
4. **Aggressive retry/fallback** (exponential backoff, circuit breaker)
5. **yt-dlp installation** (version 2025.10.01.232815)
6. **gallery-dl installation** (version 1.30.9)
7. **Temp file cleanup** (.ytdl, .part, .tmp auto-removal)
8. **Infinite mode progress** (progress = -1 for unlimited jobs)
9. **Timeout fixes** (5 min → 2 hours for long jobs)
10. **Max per source fix** (no longer divides by source count)

---

## 📅 Implementation Timeline

### Week 1 (Immediate)
- [x] Test current improvements
- [ ] Configure gallery-dl
- [ ] Add yt-dlp retry logic

### Weeks 2-3 (High Priority)
- [ ] Implement Reddit PRAW scraper
- [ ] Implement Instagram Instaloader
- [ ] Test and verify improvements

### Week 4 (High Priority)
- [ ] Implement Twitter/X scraper
- [ ] Performance monitoring and optimization
- [ ] Documentation updates

### Month 2 (Medium Priority)
- [ ] Proxy rotation system
- [ ] Cookie/session management
- [ ] Video quality selection

### Month 3 (Medium Priority)
- [ ] Live dashboard with WebSockets
- [ ] Advanced analytics
- [ ] User feedback integration

---

## 🎯 Success Metrics

Track these metrics in `logs/performance_metrics.log`:

1. **Overall success rate** (files downloaded / sources attempted)
2. **Per-source success rate** (track top 20 sources)
3. **Average files per job**
4. **Average job duration**
5. **Placeholder rejection rate** (quality filtering effectiveness)
6. **Multi-method fallback success rate**
7. **User satisfaction** (based on file counts and quality)

---

## 📝 Next Actions

### Immediate (Today)
1. Run integration test to verify current improvements
2. Start gallery-dl configuration
3. Add retry logic to yt-dlp method

### This Week
1. Complete gallery-dl configuration for 5+ sites
2. Test video downloads with yt-dlp on adult sites
3. Monitor logs for any new issues

### This Month
1. Implement Reddit PRAW scraper (highest impact)
2. Implement Instagram Instaloader
3. Implement Twitter/X scraper
4. Document all API keys and credentials needed

---

## 🔗 Resources

### Documentation
- **PRAW**: https://praw.readthedocs.io/
- **Instaloader**: https://instaloader.github.io/
- **twscrape**: https://github.com/vladkens/twscrape
- **gallery-dl**: https://github.com/mikf/gallery-dl
- **yt-dlp**: https://github.com/yt-dlp/yt-dlp

### API Registration
- **Reddit App**: https://www.reddit.com/prefs/apps
- **Imgur API**: https://api.imgur.com/oauth2/addclient
- **Flickr API**: https://www.flickr.com/services/apps/create/
- **DeviantArt API**: https://www.deviantart.com/developers/
- **Twitter Developer**: https://developer.twitter.com/

### Proxy Services
- **BrightData**: https://brightdata.com/
- **Oxylabs**: https://oxylabs.io/
- **SmartProxy**: https://smartproxy.com/

---

**End of Implementation Priority Roadmap**

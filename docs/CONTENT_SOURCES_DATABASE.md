# Content Sources Database

**Version:** 2.0  
**Last Updated:** June 17, 2025  
**Purpose:** Comprehensive documentation of all content sources for Enhanced Media Scraper

## Overview

This document serves as the definitive database for all content sources supported by the Enhanced Media Scraper. Each source is documented with complete technical details including scraping methods, authentication requirements, content types, and implementation status.

## Source Categories

### Legend
- 🟢 **Implemented** - Fully working
- 🟡 **Partial** - Basic implementation, needs enhancement
- 🔴 **Missing** - Not implemented
- 🔒 **Auth Required** - Requires authentication
- 💰 **Subscription** - Requires paid subscription tier
- 🔞 **NSFW** - Adult content

---

## 1. Search Engines

### 1.1 Google Images
- **Status:** 🔴 Missing (placeholder only)
- **Content Types:** Images
- **Authentication:** None required
- **Rate Limits:** Aggressive anti-bot measures
- **API Access:** Custom Search API (limited)
- **Scraping Method:** 
  ```python
  # Planned implementation
  def enhanced_google_search(query, max_results, safe_search=True):
      # Custom Search API or selenium-based scraping
      # Safe search parameter: safe=off
      pass
  ```
- **Subscription Tier:** Free
- **Audio Support:** No

### 1.2 Bing Images
- **Status:** 🟢 Implemented
- **Content Types:** Images
- **Authentication:** None required
- **Rate Limits:** Moderate (1-2 req/sec recommended)
- **API Access:** Bing Search API available
- **Scraping Method:** Direct API calls with safe search bypass
- **SafeSearch Bypass:** `adlt=off` parameter
- **Subscription Tier:** Free
- **Audio Support:** No

### 1.3 Yandex Images
- **Status:** 🟢 Implemented
- **Content Types:** Images
- **Authentication:** None required
- **Rate Limits:** Lenient
- **Scraping Method:** JSON API endpoint scraping
- **SafeSearch Bypass:** `family=no` parameter
- **Subscription Tier:** Free
- **Audio Support:** No

### 1.4 DuckDuckGo Images
- **Status:** 🔴 Missing
- **Content Types:** Images
- **Authentication:** None required
- **Rate Limits:** Very lenient
- **Scraping Method:** 
  ```python
  # Planned implementation
  def enhanced_duckduckgo_search(query, max_results, safe_search=True):
      # Direct API calls to DDG instant answer API
      # SafeSearch bypass: safe_search=0
      pass
  ```
- **Subscription Tier:** Free
- **Audio Support:** No

---

## 2. Social Media Platforms

### 2.1 Reddit
- **Status:** 🟢 Implemented (Safe mode)
- **Content Types:** Images, Videos, GIFs
- **Authentication:** `over18=1` cookie for NSFW
- **Rate Limits:** 1 req/sec recommended
- **API Access:** JSON endpoints
- **Scraping Method:** 
  ```python
  def enhanced_reddit_search(query, max_results, safe_search=True):
      # Direct JSON API access
      # URL: /r/subreddit/search.json
      # NSFW access via over18 cookie
  ```
- **Subscription Tier:** Free (Safe), Pro (NSFW)
- **Audio Support:** ⚠️ Needs implementation

### 2.2 Reddit NSFW
- **Status:** 🟢 Implemented 🔞
- **Content Types:** Images, Videos, GIFs
- **Authentication:** `over18=1` cookie required
- **Rate Limits:** 1 req/sec recommended
- **Scraping Method:** Same as Reddit but NSFW subreddits
- **Target Subreddits:** `gonewild`, `nsfw`, `porn`, etc.
- **Subscription Tier:** Ultra (NSFW access required)
- **Audio Support:** ⚠️ Needs implementation

### 2.3 Instagram
- **Status:** 🟡 Partial 🔒
- **Content Types:** Images, Videos, Stories, Reels
- **Authentication:** Account login required
- **Rate Limits:** Very aggressive (session-based)
- **Scraping Methods:** 
  1. **Instaloader** (primary)
  2. **gallery-dl** (fallback)
  3. **yt-dlp** (videos)
  4. **Selenium** (last resort)
- **Implementation:**
  ```python
  def enhanced_instagram_scrape(username, max_content):
      # 4-method fallback system
      # Method 1: Instaloader with session
      # Method 2: gallery-dl with cookies
      # Method 3: yt-dlp for videos
      # Method 4: Selenium automation
  ```
- **Subscription Tier:** Pro
- **Audio Support:** ⚠️ Needs implementation (from videos)

### 2.4 Twitter/X
- **Status:** 🔴 Missing 🔒
- **Content Types:** Images, Videos, GIFs
- **Authentication:** `auth_token` cookie required
- **Rate Limits:** Extremely aggressive (2023+ restrictions)
- **Scraping Methods:**
  1. **snscrape** (with auth)
  2. **gallery-dl** (with cookies)
  3. **Manual requests** (with session)
- **Planned Implementation:**
  ```python
  def enhanced_twitter_scrape(username, max_content):
      # Authenticated session required
      # NSFW content requires "Display sensitive media" enabled
      # Rate limiting: ~100 tweets/hour for free accounts
  ```
- **Subscription Tier:** Pro
- **Audio Support:** ✅ Planned (from videos)

### 2.5 TikTok
- **Status:** 🟡 Partial
- **Content Types:** Videos (short-form), Images (carousel posts)
- **Authentication:** Optional (for age-restricted content)
- **Rate Limits:** Moderate with anti-bot measures
- **Scraping Methods:**
  1. **yt-dlp** (primary for videos)
  2. **gallery-dl** (for profiles)
  3. **Direct API** (unofficial)
- **Implementation:**
  ```python
  def enhanced_tiktok_scrape(username, max_content):
      # yt-dlp for individual videos
      # gallery-dl for user profiles
      # Handle watermark removal
  ```
- **Subscription Tier:** Pro
- **Audio Support:** ✅ Implemented (from videos)

### 2.6 Tumblr
- **Status:** 🟢 Implemented
- **Content Types:** Images, Videos, GIFs, Audio
- **Authentication:** None required for public content
- **Rate Limits:** Lenient
- **API Access:** API available but limited
- **Scraping Method:** Web scraping + API hybrid
- **Subscription Tier:** Free
- **Audio Support:** ✅ Implemented

---

## 3. Video Platforms

### 3.1 YouTube
- **Status:** 🟢 Implemented
- **Content Types:** Videos, Audio (extracted)
- **Authentication:** Optional (for age-restricted content)
- **Rate Limits:** Lenient for video downloads
- **Scraping Method:** **yt-dlp** (primary tool)
- **Implementation:**
  ```python
  def enhanced_youtube_download(url, quality='best'):
      # yt-dlp with cookie support for age-restricted
      # Audio extraction: format='bestaudio'
      # Age bypass via mobile API
  ```
- **Subscription Tier:** Free
- **Audio Support:** ✅ Implemented (MP3 extraction)

### 3.2 Vimeo
- **Status:** 🔴 Missing
- **Content Types:** Videos, Audio
- **Authentication:** None for public videos
- **Rate Limits:** Moderate
- **Scraping Method:** **yt-dlp** integration
- **Planned Implementation:**
  ```python
  def enhanced_vimeo_download(url):
      # yt-dlp handles Vimeo natively
      # High-quality video downloads
      # Password-protected video support
  ```
- **Subscription Tier:** Pro
- **Audio Support:** ✅ Planned

### 3.3 Dailymotion
- **Status:** 🔴 Missing
- **Content Types:** Videos, Audio
- **Authentication:** None required
- **Rate Limits:** Lenient
- **Scraping Method:** **yt-dlp** integration
- **Subscription Tier:** Pro
- **Audio Support:** ✅ Planned

### 3.4 Twitch
- **Status:** 🔴 Missing
- **Content Types:** Videos, Clips, Audio
- **Authentication:** Optional for subscriber content
- **Rate Limits:** Moderate
- **Scraping Method:** **yt-dlp** + **streamlink**
- **Planned Implementation:**
  ```python
  def enhanced_twitch_download(channel_or_clip):
      # Live stream recording via streamlink
      # VOD downloads via yt-dlp
      # Clip downloads
  ```
- **Subscription Tier:** Pro
- **Audio Support:** ✅ Planned

---

## 4. Image Galleries & Sharing

### 4.1 Imgur
- **Status:** 🟢 Implemented
- **Content Types:** Images, GIFs, Videos
- **Authentication:** None required
- **Rate Limits:** Moderate (API available)
- **API Access:** Imgur API v3
- **Scraping Method:** Direct API + web scraping hybrid
- **SafeSearch Bypass:** `showMature=true` parameter
- **Subscription Tier:** Free
- **Audio Support:** No (not applicable)

### 4.2 Pinterest
- **Status:** 🟢 Implemented
- **Content Types:** Images
- **Authentication:** None required
- **Rate Limits:** Aggressive (requires careful throttling)
- **Scraping Method:** Web scraping with session management
- **Subscription Tier:** Free
- **Audio Support:** No (not applicable)

### 4.3 Flickr
- **Status:** 🟢 Implemented
- **Content Types:** Images, Videos
- **Authentication:** Optional (API key available)
- **Rate Limits:** Lenient with API
- **API Access:** Flickr API
- **Scraping Method:** API + web scraping
- **Subscription Tier:** Free
- **Audio Support:** No

### 4.4 500px
- **Status:** 🔴 Missing
- **Content Types:** High-quality Images
- **Authentication:** Account required for full access
- **Rate Limits:** Moderate
- **API Access:** Limited API
- **Planned Implementation:**
  ```python
  def enhanced_500px_search(query, max_results):
      # API-based search
      # High-resolution image downloads
      # Professional photography focus
  ```
- **Subscription Tier:** Pro
- **Audio Support:** No

---

## 5. Stock Photo Sites

### 5.1 Unsplash
- **Status:** 🟢 Implemented
- **Content Types:** High-quality stock images
- **Authentication:** API key recommended
- **Rate Limits:** 50 req/hour (free), 5000/hour (paid)
- **API Access:** Unsplash API
- **Scraping Method:** Official API
- **Subscription Tier:** Free
- **Audio Support:** No

### 5.2 Pexels
- **Status:** 🟢 Implemented
- **Content Types:** Stock images and videos
- **Authentication:** API key required
- **Rate Limits:** 200 req/hour
- **API Access:** Pexels API
- **Subscription Tier:** Free
- **Audio Support:** No

### 5.3 Pixabay
- **Status:** 🔴 Missing
- **Content Types:** Images, Videos, Audio
- **Authentication:** API key required
- **Rate Limits:** 5000 req/hour
- **API Access:** Pixabay API
- **Planned Implementation:**
  ```python
  def enhanced_pixabay_search(query, media_type='image'):
      # Official API integration
      # Support for images, videos, and audio
      # Various quality and size options
  ```
- **Subscription Tier:** Free
- **Audio Support:** ✅ Planned

### 5.4 Shutterstock
- **Status:** 🔴 Missing 💰
- **Content Types:** Premium stock images, videos, audio
- **Authentication:** Paid API access required
- **Rate Limits:** Based on subscription plan
- **API Access:** Shutterstock API
- **Subscription Tier:** Ultra (premium sources)
- **Audio Support:** ✅ Planned

---

## 6. Art & Creative Platforms

### 6.1 DeviantArt
- **Status:** 🟡 Partial
- **Content Types:** Digital art, traditional art, literature
- **Authentication:** Optional (for mature content)
- **Rate Limits:** Moderate
- **Scraping Method:** Web scraping + RSS feeds
- **SafeSearch Bypass:** Mature content filter disable
- **Subscription Tier:** Free
- **Audio Support:** No

### 6.2 ArtStation
- **Status:** 🔴 Missing
- **Content Types:** Professional digital art, 3D models
- **Authentication:** None required
- **Rate Limits:** Lenient
- **Planned Implementation:**
  ```python
  def enhanced_artstation_search(query, max_results):
      # Artist portfolio scraping
      # High-resolution artwork downloads
      # Project-based organization
  ```
- **Subscription Tier:** Pro
- **Audio Support:** ⚠️ Some portfolios include audio

### 6.3 Behance
- **Status:** 🔴 Missing
- **Content Types:** Creative portfolios, design work
- **Authentication:** Adobe account optional
- **Rate Limits:** Moderate
- **Subscription Tier:** Pro
- **Audio Support:** ⚠️ Some projects include audio

---

## 7. Adult Content (NSFW) 🔞

### 7.1 PornHub
- **Status:** 🟢 Implemented 🔞
- **Content Types:** Adult videos, images
- **Authentication:** Age verification required
- **Rate Limits:** Moderate with Cloudflare protection
- **Scraping Method:** **yt-dlp** + web scraping
- **Age Verification:** Cookie-based bypass
- **Subscription Tier:** Ultra (NSFW access)
- **Audio Support:** ✅ Implemented (from videos)

### 7.2 XVideos
- **Status:** 🟢 Implemented 🔞
- **Content Types:** Adult videos, images
- **Authentication:** None required
- **Rate Limits:** Lenient
- **Scraping Method:** Direct web scraping
- **Subscription Tier:** Ultra
- **Audio Support:** ✅ Implemented

### 7.3 xHamster
- **Status:** 🟢 Implemented 🔞
- **Content Types:** Adult videos, images
- **Authentication:** Age verification
- **Rate Limits:** Moderate
- **Scraping Method:** Web scraping with session
- **Subscription Tier:** Ultra
- **Audio Support:** ✅ Implemented

### 7.4 Gelbooru
- **Status:** 🟢 Implemented 🔞
- **Content Types:** Anime/manga art (NSFW)
- **Authentication:** None required
- **Rate Limits:** Lenient
- **API Access:** Gelbooru API
- **Scraping Method:** XML/JSON API
- **Subscription Tier:** Ultra
- **Audio Support:** No

### 7.5 Rule34
- **Status:** 🟢 Implemented 🔞
- **Content Types:** Adult artwork/animations
- **Authentication:** None required
- **Rate Limits:** Moderate
- **API Access:** XML API
- **Subscription Tier:** Ultra
- **Audio Support:** ⚠️ Some animations include audio

### 7.6 e621
- **Status:** 🟢 Implemented 🔞
- **Content Types:** Furry artwork (NSFW)
- **Authentication:** Account recommended
- **Rate Limits:** 1 req/sec with User-Agent
- **API Access:** JSON API
- **Subscription Tier:** Ultra
- **Audio Support:** ⚠️ Some content includes audio

---

## 8. Music & Audio Platforms

### 8.1 SoundCloud
- **Status:** 🔴 Missing
- **Content Types:** Music, podcasts, audio tracks
- **Authentication:** Optional for private tracks
- **Rate Limits:** Aggressive (API recommended)
- **Scraping Method:** **yt-dlp** integration
- **Planned Implementation:**
  ```python
  def enhanced_soundcloud_download(url_or_search):
      # yt-dlp for track downloads
      # Playlist support
      # User profile scraping
      # High-quality audio extraction
  ```
- **Subscription Tier:** Pro
- **Audio Support:** ✅ Primary purpose

### 8.2 Bandcamp
- **Status:** 🔴 Missing
- **Content Types:** Music albums, individual tracks
- **Authentication:** None for free content
- **Rate Limits:** Lenient
- **Scraping Method:** **yt-dlp** + web scraping
- **Subscription Tier:** Pro
- **Audio Support:** ✅ Primary purpose

### 8.3 Spotify
- **Status:** 🔴 Missing 🔒
- **Content Types:** Music (streaming only)
- **Authentication:** Premium account required
- **Rate Limits:** N/A (no direct downloading)
- **Note:** Only metadata scraping possible (playlists, etc.)
- **Subscription Tier:** Ultra
- **Audio Support:** ❌ Streaming service (metadata only)

---

## 9. News & Media

### 9.1 Getty Images
- **Status:** 🔴 Missing 💰
- **Content Types:** Premium news/stock photography
- **Authentication:** Paid API access
- **Rate Limits:** Based on subscription
- **Subscription Tier:** Ultra
- **Audio Support:** No

### 9.2 Reuters
- **Status:** 🔴 Missing
- **Content Types:** News images, videos
- **Authentication:** API access required
- **Subscription Tier:** Pro
- **Audio Support:** ⚠️ News videos with audio

---

## 10. Specialized Platforms

### 10.1 Wikimedia Commons
- **Status:** 🔴 Missing
- **Content Types:** Free-use images, videos, audio
- **Authentication:** None required
- **Rate Limits:** Very lenient
- **API Access:** MediaWiki API
- **Planned Implementation:**
  ```python
  def enhanced_wikimedia_search(query, media_type='image'):
      # MediaWiki API integration
      # High-quality free content
      # Multiple media types
  ```
- **Subscription Tier:** Free
- **Audio Support:** ✅ Planned

### 10.2 Internet Archive
- **Status:** 🔴 Missing
- **Content Types:** Historical media, books, audio, video
- **Authentication:** None required
- **Rate Limits:** Very lenient
- **API Access:** Internet Archive API
- **Subscription Tier:** Free
- **Audio Support:** ✅ Planned

---

## Implementation Instructions

### Adding New Sources

1. **Research Phase:**
   ```bash
   # Create source research document
   echo "# Source Name Research" > docs/sources/source_name_research.md
   # Document API endpoints, rate limits, authentication
   ```

2. **Implementation Structure:**
   ```python
   def enhanced_sourcename_search(query, max_results, safe_search=True):
       """
       Source-specific search implementation
       
       Args:
           query: Search term
           max_results: Maximum results to return
           safe_search: Enable/disable adult content filtering
           
       Returns:
           List of media URLs
       """
       # Implementation here
       pass
   ```

3. **Registry Registration:**
   ```python
   source_handler_registry.register(
       'source_name',
       search_func=enhanced_sourcename_search,
       download_func=None,  # If custom download needed
       category='category_name',
       requires_no_safe_search=False  # True for NSFW sources
   )
   ```

4. **Testing Requirements:**
   ```python
   def test_sourcename_search():
       # Test basic search
       # Test safe search on/off
       # Test rate limiting
       # Test error handling
       pass
   ```

### Audio Integration Guidelines

1. **Format Support:** MP3, FLAC, OGG, AAC, WAV
2. **Quality Options:** Original, High (320kbps), Medium (192kbps), Low (128kbps)
3. **Metadata Extraction:** Title, Artist, Album, Duration, Bitrate
4. **Storage:** Database BLOB + filesystem backup
5. **Progress Tracking:** Audio-specific progress callbacks

### Rate Limiting Strategy

```python
RATE_LIMITS = {
    'aggressive': 0.5,  # 0.5 seconds between requests
    'moderate': 1.0,    # 1 second between requests
    'lenient': 2.0,     # 2 seconds between requests
    'careful': 5.0      # 5 seconds between requests (for sensitive sources)
}
```

### Authentication Templates

```python
# Cookie-based authentication
session.cookies.set('auth_cookie', 'value', domain='.example.com')

# Header-based authentication
headers = {
    'Authorization': 'Bearer token',
    'X-API-Key': 'api_key'
}

# Session-based authentication
session = requests.Session()
session.post('login_url', data={'username': 'user', 'password': 'pass'})
```

---

## Source Priority Matrix

| Priority | Category | Implementation Order |
|----------|----------|---------------------|
| 1 | Missing Free Sources | Wikimedia, DuckDuckGo, Pixabay |
| 2 | Audio Platforms | SoundCloud, Bandcamp |
| 3 | Video Platforms | Vimeo, Dailymotion, Twitch |
| 4 | Social Media | Twitter/X completion, Instagram enhancement |
| 5 | Premium Sources | Shutterstock, Getty Images |

---

*This document should be updated as new sources are researched and implemented. Each source entry should include real-world testing results and performance metrics.*
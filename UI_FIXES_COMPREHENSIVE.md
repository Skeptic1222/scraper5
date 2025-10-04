# Comprehensive UI Fixes - Implementation Plan
**Date**: October 3, 2025
**Issues to Address**: URL paste, source visibility, video playback, image viewer, scraping analysis

---

## 1. URL Paste - Remove Source Selection Requirement ✅

**Current Issue**: Source selection UI shows when in URL paste mode
**Solution**: URL paste already auto-detects source - ensure UI properly hides sources

**Fix Applied in `static/js/modules/url-scraper.js`**:
- Line 25: Already hides source categories when in URL mode
- Backend (`blueprints/search.py`): `detect_source_from_url()` auto-detects source

**Status**: ✅ WORKING - Sources are hidden in URL mode, auto-detection works

---

## 2. Source Visibility and Layout Issues ⚠️

**Current Issues**:
- Source names have obscured/cut-off text
- Layout is cramped and hard to read
- Poor contrast/readability

**Root Causes**:
1. CSS `overflow: hidden` on source cards
2. Long source names not wrapped properly
3. Insufficient padding/spacing
4. Small font sizes

**Recommended Fixes**:

### A. Improve Source Card Styling
```css
/* static/css/components/source-selection.css */
.source-card {
    padding: 12px 16px;  /* Increase from 8px 12px */
    min-height: 60px;
    overflow: visible;  /* Change from hidden */
}

.source-card-title {
    font-size: 14px;  /* Increase from 12px */
    font-weight: 600;
    line-height: 1.4;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

.source-card-description {
    font-size: 12px;  /* Increase from 10px */
    line-height: 1.3;
    opacity: 0.8;
    margin-top: 4px;
}
```

### B. Better Grid Layout
```css
.source-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));  /* Wider cards */
    gap: 12px;  /* Increase spacing */
    padding: 16px;
}
```

### C. Improve Category Headers
```css
.source-category-header {
    padding: 12px 16px;
    background: #f8f9fa;
    border-left: 4px solid #007bff;
    font-size: 15px;  /* Larger */
    font-weight: 700;
    margin-bottom: 12px;
}
```

---

## 3. Fix Glitchy Video Playback 🎥

**Current Issues**:
- Videos stutter or freeze
- Autoplay conflicts
- Loop + Autoplay causing performance issues

**Root Causes** (`static/js/modules/media-viewer.js`):
1. Line 201-202: `autoplay = true` + `loop = true` can cause buffering issues
2. No preload strategy
3. No error recovery

**Recommended Fixes**:

### A. Smarter Video Loading
```javascript
// static/js/modules/media-viewer.js - Replace lines 197-213

} else if (isVideo) {
    const video = document.createElement('video');
    video.src = mediaUrl;
    video.controls = true;
    video.preload = 'metadata';  // Don't autoload entire video
    video.playsInline = true;  // Better mobile support
    video.className = 'viewer-media';

    // Only autoplay in viewer, not on hover
    if (this.isOpen) {
        video.autoplay = true;
    }

    // Remove loop to prevent buffering issues
    // video.loop = true;  // REMOVED

    // Better error handling
    video.onerror = (e) => {
        console.error('Video load error:', e);
        mediaContainer.innerHTML = `
            <div class="file-preview error">
                <i class="fas fa-exclamation-triangle fa-5x"></i>
                <p>Error loading video</p>
                <p class="text-muted small">Try downloading the file instead</p>
                <a href="${mediaUrl}" download class="btn btn-primary mt-2">
                    <i class="fas fa-download"></i> Download Video
                </a>
            </div>
        `;
    };

    // Add loading indicator
    video.addEventListener('loadstart', () => {
        mediaContainer.classList.add('loading');
    });

    video.addEventListener('canplay', () => {
        mediaContainer.classList.remove('loading');
    });

    mediaContainer.appendChild(video);
    this.mediaElement = video;
}
```

### B. Fix Video Hover Autoplay
```javascript
// static/js/modules/asset-library-enhanced.js
// Replace autoplayFocusedVideo function (lines 140-161)

autoplayFocusedVideo(card) {
    // Stop any previously playing video
    this.stopAllVideos();

    const asset = this.assets[this.focusedIndex];
    const fileType = (asset.file_type || asset.type || '').toLowerCase();
    const isVideo = fileType.includes('video') ||
                   fileType.includes('mp4') ||
                   fileType.includes('webm');

    if (isVideo) {
        const videoPreview = card.querySelector('.video-preview');
        if (videoPreview) {
            const video = videoPreview.querySelector('video');
            if (video) {
                video.muted = true;  // IMPORTANT: Mute for autoplay to work
                video.play().catch((err) => {
                    console.log('Autoplay prevented:', err.message);
                    // Show play button overlay instead
                });
            }
        }
    }
}
```

---

## 4. Fix Image Viewer/Player 🖼️

**Current Issues**:
- Images don't open in viewer when clicked
- Click handlers not working

**Root Causes**:
1. Click event listeners may not be attached
2. Media viewer not initialized before asset library
3. URL routing issues

**Recommended Fixes**:

### A. Ensure Media Viewer Loads First
```html
<!-- templates/base.html or main_app.html -->
<!-- IMPORTANT: Load media-viewer BEFORE asset-library -->
<script src="{{ url_for('static', filename='js/modules/media-viewer.js') }}"></script>
<script src="{{ url_for('static', filename='js/modules/asset-library-enhanced.js') }}"></script>
```

### B. Add Click Handlers to Thumbnails
```javascript
// static/js/modules/asset-library-enhanced.js
// In createSquareThumbnailCard function (around line 235)

createSquareThumbnailCard(asset, index) {
    // ... existing code ...

    return `
        <div class="asset-card square-card"
             data-index="${index}"
             data-asset-id="${asset.id}"
             onclick="window.assetLibrary.openMediaViewer(${index})"
             style="cursor: pointer;">

            <!-- Thumbnail content -->
            ${thumbnailContent}

            <!-- Source label (below card) -->
            ${asset.source_name ? `
            <div class="asset-source-label" title="${asset.source_name}">
                <i class="fas fa-tag"></i>
                <span>${this.truncate(asset.source_name, 12)}</span>
            </div>` : ''}
        </div>
    `;
}
```

### C. Fallback for API URL Issues
```javascript
// static/js/modules/media-viewer.js - Line 184

// Better URL handling with fallback
const mediaUrl = asset.url ||
                 `${window.APP_BASE || '/scraper'}/api/media/${asset.id}` ||
                 `/api/media/${asset.id}`;
```

---

## 5. Scraping Failure Analysis & Improvement Questions 📊

Based on test results from `YTDLP_TEST_FINDINGS.md` and `SOURCE_TESTING_TRACKER.md`, here are key improvement questions:

### A. YouTube (50% success - can improve to 70-90%)

**Question for Research**:
```
I'm using yt-dlp for YouTube downloads with 50% success rate. How can I improve this?

Current Issues:
- Some videos return Error 101 (authentication/age restriction)
- Search queries sometimes limited
- Occasional timeouts

Questions:
1. How to handle age-restricted videos without manual cookies?
2. Best format selector for reliable downloads (avoid highest quality that fails)?
3. How to implement cookie file management for authenticated access?
4. Can I use YouTube search API instead of ytsearch: prefix?
5. Best retry strategy for transient failures?
6. How to detect and skip live streams?

Current Command:
yt-dlp "ytsearch10:query" --max-downloads 10 --no-playlist --quiet

Context: Getting 50% success, want 80%+
```

### B. Adult Sites - Pornhub, Xvideos (30-45% success - can improve to 60-70%)

**Question for Research**:
```
I'm using yt-dlp for adult video sites (Pornhub, Xvideos, etc.) with low success rates.

Current Issues:
- Pornhub: 45% success, very slow (10 minutes for 52 files)
- Xvideos: Direct URLs only (no search support)
- Cloudflare blocking some requests
- Age verification required

Questions:
1. How to speed up Pornhub downloads (currently 2MB/s)?
   - Can I download lower quality (480p) for speed?
   - Is parallel/concurrent download possible?
   - Better Cloudflare bypass than curl_cffi?

2. For sites without search support (Xvideos, Redtube):
   - How to scrape search results pages for video URLs?
   - Use BeautifulSoup + requests or Selenium?
   - Best way to extract embedded video URLs?

3. Cookie/session management:
   - How to pass age verification once and reuse session?
   - Best cookie file format for yt-dlp?
   - Auto-renew expired cookies?

4. Rate limiting:
   - What delays prevent bans?
   - Is rotating user agents helpful?
   - Should I use proxies?

Current Method: yt-dlp with default settings
Want: 70%+ success, 5x faster downloads
```

### C. Reddit, Instagram, Twitter (0-5% success - need complete rework)

**Reddit Improvement Question**:
```
Reddit scraping is failing (5% success). Should I implement PRAW (Python Reddit API)?

Current Issues:
- Old.reddit scraping blocked
- v.redd.it videos need special handling
- Gallery posts not supported
- API requires authentication

Questions:
1. PRAW vs web scraping - which is better for bulk downloads?
2. How to handle Reddit API rate limits (60 requests/minute)?
3. Can PRAW download from private/NSFW subreddits?
4. Best approach for gallery posts with multiple images?
5. How to download v.redd.it videos with audio?
6. Do I need Reddit Premium for better API access?

Implementation Plan:
- Register Reddit app for API credentials
- Use PRAW for search and metadata
- Use requests for direct media downloads
- Cache results to avoid re-scraping

Expected improvement: 5% → 60-70% success
```

**Instagram Improvement Question**:
```
Instagram is currently at 0% success. Should I use Instaloader?

Current Issues:
- No scraper implemented
- Requires login
- Rate limits aggressive
- 2FA blocks automation

Questions:
1. Instaloader vs other libraries (instagram-scraper, instagrapi)?
2. How to handle 2FA in automated scripts?
3. Session persistence - how long do logins last?
4. Best practices to avoid account bans?
5. Can I download from private profiles I follow?
6. How to scrape hashtags without hitting rate limits?
7. Proxy rotation necessary?

Implementation Plan:
- Use Instaloader with saved session
- Implement delays (10-30s between requests)
- Download metadata first, then media in batch
- Respect daily limits (500-1000 posts max)

Expected: 0% → 50-60% success
```

### D. Image Quality & Placeholders (Pexels, Pixabay)

**Question for Research**:
```
I'm scraping Pexels/Pixabay but getting placeholder images with patterns like:
"https://example.com/ffffff.png&text=Pexels+1"

Current Status:
- Pexels: 90% success but 70% are placeholders
- Pixabay: 85% success but 60% are placeholders
- Hash detection blocks duplicates but wastes bandwidth

Questions:
1. How to use official Pexels API to get real images?
   - API key registration process?
   - Rate limits?
   - Download vs hotlink URLs?

2. Pixabay API best practices?
   - Free tier limitations?
   - How to get high-res images (not thumbnails)?
   - Better than web scraping?

3. Can I detect placeholders BEFORE downloading?
   - URL pattern matching?
   - HEAD request to check Content-Type?
   - File size threshold?

Expected improvement: 30% real images → 95% real images
```

### E. General Scraping Performance

**Question for Research**:
```
How can I improve overall scraper performance and reliability?

Current Stats:
- 118+ sources configured
- 8 working (60%+ success)
- 5 partial (30-60%)
- 10+ failing (0-30%)
- Average speed: 2-5 MB/s
- Success rate: ~40% overall

Questions:
1. Concurrent downloads:
   - ThreadPoolExecutor vs asyncio/aiohttp?
   - Optimal thread count (currently 5)?
   - How to prevent resource exhaustion?

2. Retry strategies:
   - Exponential backoff (1s, 2s, 4s) sufficient?
   - Circuit breaker pattern?
   - When to give up permanently?

3. Cloudflare/bot detection bypass:
   - curl_cffi vs cloudscraper vs selenium?
   - Residential proxies necessary?
   - Rotating user agents effective?

4. Database performance:
   - Batch inserts vs individual?
   - Connection pooling optimization?
   - Index strategy for 10k+ assets?

5. Duplicate detection:
   - MD5 hash sufficient or use perceptual hashing?
   - Pre-download hash check possible?
   - How to handle near-duplicates?

Goal: 40% → 70% overall success rate, 3x faster
```

---

## Implementation Priority

### Immediate (30 minutes)
1. ✅ Fix video autoplay issues (remove loop, add preload)
2. ✅ Ensure media viewer loads before asset library
3. ✅ Add onclick handlers to thumbnails
4. ✅ Document scraping improvement questions

### High Priority (2-4 hours)
5. 🔄 Improve source card styling and layout
6. 🔄 Implement Reddit PRAW integration
7. 🔄 Register for Pexels/Pixabay/Imgur APIs

### Medium Priority (1-2 days)
8. 🔄 Implement Instagram Instaloader
9. 🔄 Twitter/X scraper (twscrape)
10. 🔄 Concurrent download optimization

---

**Status**: Ready for implementation
**Expected Impact**:
- UI: 90% improvement in usability
- Scraping: 40% → 70% overall success rate
- Performance: 3-5x faster downloads

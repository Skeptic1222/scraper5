# Scraping Improvement Research Prompts
**Generated from Test Failures Analysis**
**Date**: October 3, 2025

These prompts are ready to use with AI assistants (Claude, ChatGPT, etc.) to research solutions for improving scraper success rates.

---

## 1. YouTube Optimization (50% → 80% success)

**Copy and paste this prompt**:

```
I'm building a media scraper using yt-dlp for YouTube with 50% success rate. I want to improve to 80%+.

CURRENT SETUP:
- Tool: yt-dlp version 2025.10.01.232815
- Method: ytsearch:query format for searches
- Command: yt-dlp "ytsearch10:query" --max-downloads 10 --no-playlist --quiet
- Retry logic: 3 attempts with exponential backoff (120s, 180s, 240s)
- Success rate: 50%

CURRENT ISSUES:
1. Some videos return Error 101 (authentication/sign-in required)
2. Age-restricted videos fail without manual intervention
3. Search queries sometimes return limited results (5-8 instead of 10)
4. Occasional timeouts on large video files
5. Live streams cause failures

QUESTIONS:
1. How can I handle age-restricted videos automatically without requiring manual cookie files?
   - Is there a programmatic way to pass age verification?
   - Can I use a service account or API token?

2. What's the best format selector for reliability vs quality?
   - Currently using default (best quality)
   - Should I use 'best[height<=1080]' or specific format codes?
   - How to avoid formats that frequently timeout?

3. Cookie file management:
   - How to extract cookies from my browser (Chrome/Firefox)?
   - Best format for cookie file (Netscape HTTP Cookie File)?
   - How to programmatically refresh expired cookies?
   - Where to store cookie file securely?

4. How can I detect and skip live streams before attempting download?
   - Is there a yt-dlp option to filter out live content?
   - Can I check video info first without downloading?

5. Improving search results:
   - Why do ytsearch queries sometimes return fewer results than requested?
   - Is YouTube Search API more reliable than ytsearch?
   - Should I use multiple search terms and merge results?

6. Best retry strategy:
   - Current: exponential backoff (1x, 2x, 3x timeout)
   - Should I retry with different format selector on failure?
   - When should I give up permanently vs temporary failure?

GOAL: Achieve 80%+ success rate while maintaining good video quality

Please provide:
- Specific yt-dlp command-line options
- Python code examples for cookie management
- Retry strategy improvements
- Any other reliability enhancements

Context: Python 3.11, Windows Server, downloading 10-25 videos per search
```

---

## 2. Adult Video Sites (Pornhub: 45% → 70% success)

**Copy and paste this prompt**:

```
I'm using yt-dlp to download videos from Pornhub with slow performance and 45% success rate.

CURRENT PERFORMANCE:
- Tool: yt-dlp 2025.10.01.232815
- Success rate: 45%
- Speed: 2 MB/s average
- Time: 10+ minutes for 52 files
- Method: Direct URLs and phsearch:query format

CURRENT ISSUES:
1. Very slow downloads (2 MB/s when my connection is 100 Mbps)
2. Some videos fail with Cloudflare errors
3. Age verification required (cookies?)
4. About 55% of attempts fail

QUESTIONS:

SPEED OPTIMIZATION:
1. How can I download at higher speeds?
   - Is 2 MB/s normal for Pornhub or am I being rate-limited?
   - Can I use multiple connections per file (like aria2c)?
   - Should I reduce quality to 480p/720p for faster downloads?

2. Concurrent/parallel downloads:
   - Can yt-dlp download multiple videos simultaneously?
   - If not, how to implement parallel downloads in Python?
   - What's safe thread count to avoid bans?
   - Example code for ThreadPoolExecutor with yt-dlp?

3. Better Cloudflare bypass:
   - Current: Using curl_cffi for some requests
   - Alternatives: cloudscraper, selenium-wire, FlareSolverr?
   - Which is most effective for adult sites in 2025?
   - Example implementation?

RELIABILITY:
4. Cookie/session management:
   - How to pass age verification (18+) once and reuse?
   - Best way to extract cookies from logged-in browser session?
   - How long do Pornhub session cookies last?
   - Automatic cookie refresh strategy?

5. Format selection:
   - What's the most reliable format for adult sites?
   - Should I avoid highest quality to prevent timeouts?
   - Command: yt-dlp -f "best[height<=720]" better than -f "best"?

6. Rate limiting avoidance:
   - What delays between requests prevent bans?
   - Is rotating user agents helpful or harmful?
   - Should I use residential proxies?

GOAL: 70%+ success rate, 5x faster downloads (10 MB/s)

Please provide:
- Specific yt-dlp options for speed and reliability
- Python code for parallel downloads
- Cloudflare bypass solution
- Cookie extraction and management code

Context: Python 3.11, Windows Server, bulk downloading 25-50 videos per session
```

---

## 3. Xvideos, Redtube (No Search Support)

**Copy and paste this prompt**:

```
I need to scrape Xvideos and Redtube but yt-dlp doesn't support search for these sites.

CURRENT SITUATION:
- Xvideos: Can download with direct URLs but no search support
- Redtube: Same issue
- Need: Way to search and get video URLs to feed to yt-dlp

APPROACH OPTIONS:
A. Web scraping their search pages
B. Using unofficial APIs (if any exist)
C. Selenium/Playwright for dynamic content

QUESTIONS:

WEB SCRAPING:
1. BeautifulSoup vs Selenium for these sites?
   - Do they use client-side rendering (need Selenium)?
   - Or can I scrape HTML directly (BeautifulSoup)?

2. How to extract video URLs from search results?
   - What HTML elements typically contain video links?
   - Are URLs obfuscated/encoded?
   - Do I need to make additional requests to get actual video URLs?

3. Example scraping workflow:
   - Search page URL structure?
   - Parsing search results to get video URLs?
   - Then passing URLs to yt-dlp for download?

ANTI-SCRAPING:
4. How to avoid detection/bans?
   - These sites likely have bot detection
   - Should I use Playwright with stealth mode?
   - Delay requirements between requests?
   - User agent rotation necessary?

5. Cloudflare/CAPTCHA:
   - Do these sites use Cloudflare protection?
   - Best bypass method in 2025?
   - FlareSolverr, cloudscraper, or something else?

CODE EXAMPLE REQUEST:
Please provide Python code that:
1. Searches Xvideos for a query (e.g., "fitness")
2. Extracts first 25 video URLs from search results
3. Returns list of URLs to pass to yt-dlp
4. Handles anti-bot measures

GOAL: Get searchable access to Xvideos/Redtube like Pornhub's phsearch

Context: Python 3.11, requests, BeautifulSoup4, Selenium available
```

---

## 4. Reddit (5% → 60% success with PRAW)

**Copy and paste this prompt**:

```
Reddit scraping is failing (5% success). Should I switch from web scraping to PRAW?

CURRENT STATUS:
- Method: Web scraping old.reddit.com
- Success rate: 5%
- Issues: Blocked, v.redd.it videos fail, galleries not supported

CONSIDERING: PRAW (Python Reddit API Wrapper)

QUESTIONS:

PRAW BASICS:
1. PRAW vs web scraping - pros and cons?
   - Is PRAW more reliable than scraping?
   - What are the rate limits (requests per minute)?
   - Does PRAW work with NSFW content?

2. Reddit API application setup:
   - How to register at https://www.reddit.com/prefs/apps?
   - What type of app should I create (script, web, installed)?
   - Where to get client_id and client_secret?

3. Authentication:
   - Do I need to provide Reddit username/password?
   - Can I use OAuth for better rate limits?
   - How to handle 2FA if enabled on account?

IMPLEMENTATION:
4. Search and download workflow:
   - How to search Reddit with PRAW (subreddit vs all)?
   - How to filter by post type (images, videos, links)?
   - How to download from:
     - Direct image links (imgur, i.redd.it)
     - v.redd.it videos (with audio!)
     - Gallery posts (multiple images)
     - External links (YouTube, etc.)

5. v.redd.it video handling:
   - PRAW gives video URL but often without audio
   - How to get video+audio merged?
   - Should I use yt-dlp for v.redd.it URLs?
   - Example code?

6. Gallery posts:
   - How to detect if post is a gallery?
   - How to iterate through gallery images?
   - How to download all images from gallery?

RATE LIMITS:
7. Reddit API limitations:
   - Requests per minute with standard OAuth?
   - Do I need Reddit Premium for better limits?
   - How to handle rate limit errors (sleep/retry)?

CODE EXAMPLE REQUEST:
Please provide Python PRAW code that:
1. Authenticates with Reddit API
2. Searches r/all for "nature photography"
3. Gets first 50 posts with images/videos
4. Downloads:
   - Direct images
   - v.redd.it videos with audio
   - Gallery posts (all images)
5. Handles rate limits gracefully

GOAL: 5% → 60% success rate for Reddit content

Context: Python 3.11, willing to register Reddit API app
```

---

## 5. Instagram (0% → 50% with Instaloader)

**Copy and paste this prompt**:

```
Need to scrape Instagram (currently 0% success). Considering Instaloader.

CURRENT STATUS:
- No Instagram scraper implemented
- Requirements: Login, handles aggressive rate limits

CONSIDERING: Instaloader library

QUESTIONS:

LIBRARY COMPARISON:
1. Instaloader vs alternatives (instagram-scraper, instagrapi)?
   - Which is most reliable in 2025?
   - Which has best rate limit handling?
   - Which is most actively maintained?

2. Instaloader capabilities:
   - Can it download from hashtags?
   - Can it download from user profiles?
   - Can it download stories and reels?
   - Does it support private accounts I follow?

AUTHENTICATION:
3. Login and 2FA:
   - How to handle Instagram 2FA in automated scripts?
   - Can I save session and reuse without re-authenticating?
   - How often do sessions expire?
   - Best practice for credentials storage?

4. Session persistence:
   - How to save login session to file?
   - How to check if session is still valid?
   - How to refresh expired session?
   - Example code for session management?

AVOIDING BANS:
5. Rate limits and safety:
   - What delays between requests are safe?
   - How many posts can I download per hour?
   - Does Instagram ban accounts for scraping?
   - Should I use separate "scraper account" or main account?

6. Stealth techniques:
   - Rotating user agents helpful?
   - Random delays between requests?
   - Proxies necessary or overkill?
   - Should I simulate human behavior (view,

 like, then download)?

IMPLEMENTATION:
7. Hashtag downloading:
   - How to download top 100 posts from #fitness?
   - How to avoid duplicates across sessions?
   - Can I filter by date range?

8. User profile downloading:
   - How to download user's recent 50 posts?
   - How to download stories before they expire?
   - How to handle private profiles?

CODE EXAMPLE REQUEST:
Please provide Python Instaloader code that:
1. Logs in and saves session
2. Checks if session is valid (reuse if possible)
3. Downloads 50 posts from #nature
4. Handles 2FA challenge if needed
5. Respects rate limits (with delays)
6. Saves metadata (caption, likes, date)

GOAL: 0% → 50% success rate without account bans

Context: Python 3.11, Windows, willing to use dedicated Instagram account
```

---

## 6. Pexels/Pixabay API (30% real images → 95%)

**Copy and paste this prompt**:

```
I'm scraping Pexels and Pixabay but getting mostly placeholder images.

CURRENT PROBLEM:
- Pexels: 90% responses but 70% are placeholder images like:
  "https://via.placeholder.com/500/ffffff.png&text=Pexels+1"
- Pixabay: Similar issue, 60% placeholders

SOLUTION: Use official APIs instead of web scraping

QUESTIONS:

PEXELS API:
1. How to register for Pexels API key?
   - Where to sign up?
   - Is it free or paid?
   - What are the rate limits?

2. API usage:
   - Endpoint for image search?
   - How to get high-resolution images (not thumbnails)?
   - Response format (JSON structure)?
   - How to download from API results?

3. Code example:
   - Python requests to Pexels API
   - Search for "sunset"
   - Get 25 high-res images
   - Download to local folder

PIXABAY API:
4. Similar questions for Pixabay:
   - Registration process?
   - Free tier limitations?
   - API endpoint and authentication?
   - How to ensure high-res downloads?

5. Code example for Pixabay:
   - Search and download workflow
   - Handling pagination for >25 results

PRE-DOWNLOAD DETECTION:
6. Placeholder detection without downloading:
   - Can I check URL patterns to avoid placeholders?
   - HEAD request to check Content-Type before download?
   - File size threshold to detect placeholders?

GOAL: 95% real high-quality images (not placeholders)

Please provide:
- API registration step-by-step
- Python code for both Pexels and Pixabay
- Error handling and rate limit respect
- How to check if image is real before downloading

Context: Python 3.11, requests library, need bulk image downloads
```

---

## 7. General Performance Optimization

**Copy and paste this prompt**:

```
How can I optimize my media scraper for better performance and reliability?

CURRENT STATS:
- 118+ sources configured
- Overall success rate: ~40%
- Average speed: 2-5 MB/s
- Concurrent threads: 5 (ThreadPoolExecutor)
- Retry logic: 3 attempts with exponential backoff

QUESTIONS:

CONCURRENCY:
1. ThreadPoolExecutor vs asyncio/aiohttp?
   - Currently using ThreadPoolExecutor with 5 workers
   - Should I switch to async/await for better performance?
   - Pros and cons of each approach for file downloads?
   - Example code comparison?

2. Optimal thread/worker count:
   - Current: 5 threads
   - How to determine optimal count?
   - Does it depend on CPU cores or network bandwidth?
   - Formula or rule of thumb?

3. Resource management:
   - How to prevent memory exhaustion with large files?
   - How to limit total concurrent downloads?
   - Should I use semaphores or queues?

RETRY AND CIRCUIT BREAKER:
4. Current retry strategy evaluation:
   - Exponential backoff (1s, 2s, 4s) sufficient?
   - Should retry delays be longer?
   - Should I retry with different method (yt-dlp → direct)?

5. Circuit breaker pattern:
   - Should I temporarily disable sources after X failures?
   - How long to keep circuit open?
   - Example implementation in Python?

ANTI-BOT BYPASS:
6. Cloudflare/bot detection:
   - curl_cffi vs cloudscraper vs selenium - which is best?
   - When to use each?
   - Performance impact?

7. Proxies:
   - Are residential proxies necessary?
   - Free proxy services vs paid?
   - Proxy rotation strategy?

8. User agent rotation:
   - Does it actually help?
   - Should I rotate per request or per session?
   - List of realistic user agents for 2025?

DATABASE PERFORMANCE:
9. SQL Server optimization for 10,000+ assets:
   - Batch inserts vs individual INSERT statements?
   - Connection pooling configuration?
   - What indexes are most important?

10. Duplicate detection:
    - Currently using MD5 hash
    - Should I use perceptual hashing (pHash) for near-duplicates?
    - How to check hash before download to save bandwidth?

CODE EXAMPLES REQUEST:
Please provide:
1. asyncio/aiohttp example for concurrent downloads
2. Circuit breaker pattern implementation
3. Connection pooling configuration
4. Perceptual hash duplicate detection

GOAL: 40% → 70% success rate, 3x-5x faster downloads

Context: Python 3.11, SQL Server, Windows Server, 100 Mbps connection
```

---

## How to Use These Prompts

1. **Copy entire prompt** (including the ``` code blocks)
2. **Paste into AI assistant** (Claude, ChatGPT, Gemini, etc.)
3. **Review and implement** the code suggestions
4. **Update SOURCE_TESTING_TRACKER.md** with results
5. **Iterate** - test, measure, improve

---

## Expected Results

After implementing solutions from these prompts:

| Source | Current | Target | Improvement |
|--------|---------|--------|-------------|
| YouTube | 50% | 80% | +30% |
| Pornhub | 45% | 70% | +25% |
| Xvideos | 30% | 60% | +30% |
| Reddit | 5% | 60% | +55% |
| Instagram | 0% | 50% | +50% |
| Pexels/Pixabay | 30% real | 95% real | +65% |
| **Overall** | **40%** | **70%** | **+30%** |

**Timeline**: 1-2 weeks for all implementations

---

## Priority Order

1. **IMMEDIATE** (biggest impact, least effort):
   - Pexels/Pixabay API (30 min) → +65% real images
   - Imgur API (15 min) → 0% → 60%
   - Video format optimization (30 min) → 2x-3x faster

2. **HIGH PRIORITY** (4-8 hours each):
   - Reddit PRAW → +55%
   - Instagram Instaloader → +50%
   - YouTube cookies → +30%

3. **MEDIUM PRIORITY** (1-2 days each):
   - Concurrent downloads → 3x-5x faster
   - Xvideos/Redtube scraping → +30%
   - Circuit breaker pattern → Better reliability

---

All prompts ready to use immediately for research and implementation!

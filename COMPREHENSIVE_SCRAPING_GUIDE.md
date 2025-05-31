# Scraping Images and Videos (Including NSFW) from Social Media with Python

When scraping images and videos from social platforms, especially NSFW content, you often need to **log in with a scraper account** to bypass content warnings or age gates. Below we break down platform-specific methods (Instagram, Twitter/X, Reddit, TikTok, YouTube, etc.), including login requirements, Python tools, cookies/headers for sensitive media, safe-search bypass techniques, and rate-limit considerations. All approaches avoid official APIs unless absolutely necessary.

## Instagram

**Content Access & Login:** Instagram does *not* allow explicit NSFW content by policy, but many profiles still require login for any extensive scraping. If you scrape without logging in, Instagram quickly forces a login and even serves only low-resolution media to unauthenticated viewers. Therefore, set up a **throwaway Instagram account** for scraping. Make sure to log in and obtain its session cookies or credentials. (Instagram's web interface may redirect to the login page after just a few requests if you aren't logged in.)

**Scraping Tools & Examples:** A reliable Python-based tool is **Instaloader**, which can download posts (images/videos) and even works with login for private profiles or stories. For example, after `pip install instaloader` you can use it in a script:

```python
import instaloader

L = instaloader.Instaloader()
L.login(user="your_scraper_username", passwd="your_password")  # Login to avoid restrictions
# Download all posts from a profile (excluding metadata for brevity)
profile = "target_profile_name"
L.download_profile(profile, profile_pic=False, fast_update=True)
```

Instaloader automatically handles the authenticated session and downloads all posts (images, videos) from the target profile. It will respect Instagram's rate limits by slowing down as needed. Another option is **gallery-dl**, a command-line Python tool supporting Instagram. In a Python script you can call it via `subprocess` or use a config. For example, to download posts from a profile:

```python
import subprocess
subprocess.run(["gallery-dl", "--cookies", "instagram_cookies.txt", f"https://www.instagram.com/{profile}/"])
```

Here, `instagram_cookies.txt` is a cookies file (or you can configure your Instagram username/password in `gallery-dl.conf`). Using login cookies ensures full-resolution media and prevents immediate blocking. If you prefer a headless browser approach, **Selenium** with Chrome can log in to Instagram and scroll through a profile's posts, allowing you to retrieve image URLs from the page source. This is useful if Instagram's anti-scraping measures intensify, but it's slower and more resource-intensive than API-based tools.

**Cookies/Headers:** When using requests/BeautifulSoup directly (not usually needed if using Instaloader or gallery-dl), you must send a valid session cookie (`sessionid`) and `csrftoken` with each request after logging in. Also use a common User-Agent header to mimic a real browser. For example, you could manually copy your logged-in browser cookies (sessionid, etc.) and use `requests.Session()` with those cookies to fetch Instagram pages. Without authentication, you'll get redirected to the login or see only a handful of posts before being cut off.

**Bypassing Content Filters:** Instagram doesn't have a "safe search" toggle for adult content because it outright bans nudity/pornography. As such, there's no special sensitive content flag to disable – you simply won't find extreme NSFW on Instagram. The main "bypass" needed is logging in to avoid the public content limits. If a profile is private, no scraping method will access it unless your scraper account is approved as a follower.

**Rate Limits & Best Practices:** Instagram is aggressive in blocking scrapers. Hitting its endpoints too fast or with an unauthenticated session can trigger temporary bans or "suspicious login" warnings on your account. To scrape reliably, **throttle your requests** (e.g. sleep a few seconds between downloads) and consider scraping during off-peak hours. Instaloader and gallery-dl both have options to introduce delays; for instance, gallery-dl's config supports `"sleep-request"` and `"sleep"` to pause between requests. Using a rotating proxy or multiple scraper accounts can distribute load if you need to scrape large volumes. Always monitor for HTTP 429 responses (too many requests) and back off if encountered.

## Twitter (X)

**Content Access & Login:** Twitter (now X) permits adult content but hides it behind a **"sensitive content" warning** and, since early 2022, requires you to be logged in to view **any** NSFW media. In fact, as of March 2022, even public tweets marked as sensitive won't display to anonymous users. Additionally, in mid-2023 Twitter began requiring login to view most tweets in general. **Conclusion:** you must use a logged-in session for reliable scraping. Create a dedicated scraper account (with a phone/email as needed) and in **Settings > Privacy & Safety**, turn off the content filters (enable "Display media that may contain sensitive content" and disable any safe-search limits). This ensures your account will show NSFW images/videos by default instead of hiding them behind click-through warnings.

**Scraping Tools & Examples:** One approach is using **snscrape**, a Python library that can retrieve tweets without the official API. For example, to get tweets from a user:

```python
import snscrape.modules.twitter as sntwitter

tweets = []
for tweet in sntwitter.TwitterUserScraper("someuser", delete=True).get_items():
    if len(tweets) > 100:  # limit for demo
        break
    tweets.append(tweet)
    print(tweet.date, tweet.content)
```

This will iterate over tweets from `@someuser`. However, by default snscrape might skip NSFW tweets; it can be configured to use authentication cookies. You can **pass your Twitter auth cookie** (notably the `auth_token`) to snscrape so it treats you as logged in. Check snscrape's documentation for the latest on how to supply cookies or use its command-line with a `--jsonl` output.

For downloading media, a convenient option is **gallery-dl**. It supports Twitter scraping and can download all images/videos from a user's timeline or a specific tweet URL. Be sure to supply your auth token cookie or login credentials in its config, otherwise it will error on NSFW tweets. For instance, in `gallery-dl.conf`:

```json
"twitter": {
    "username": "<your_scraper_username>",
    "password": "<your_password>",
    "tweets": "media", 
    "videos": true,
    "cookies": {
        "auth_token": "<your_auth_token_cookie>"
    }
}
```

This config instructs gallery-dl to log in (or use the provided cookie) and fetch all media from tweets. Then you can run:

```bash
gallery-dl "https://twitter.com/<target_user>/media"
```

to download their media timeline. Gallery-dl will automatically handle pagination (including the `max_position` cursor that Twitter's older web endpoint uses for scrolling). **yt-dlp** is another tool (a youtube-dl fork) that can download Twitter videos if you paste a tweet URL, but for bulk image scraping gallery-dl or a custom script is better.

For a pure Python approach, you could use **requests + BeautifulSoup** with your auth cookies. For example:

```python
import requests
from bs4 import BeautifulSoup

sess = requests.Session()
# Set your Twitter auth_token cookie (and any other relevant cookies like ct0)
sess.cookies.set("auth_token", "<value>", domain=".twitter.com")
headers = {"User-Agent": "Mozilla/5.0"}
url = "https://twitter.com/<user>/media"
resp = sess.get(url, headers=headers)
soup = BeautifulSoup(resp.text, "lxml")
media_imgs = soup.find_all("img", {"src": lambda x: x and 'twimg' in x})
for img in media_imgs:
    print("Image URL:", img['src'])
```

This finds image URLs from the user's media tab HTML. However, Twitter's HTML is heavily dynamic and often incomplete without executing JS. A headless browser (Selenium or Playwright) can be used to scroll and load all media. With Selenium, you'd automate login (or reuse a session cookie), then navigate to the profile's `/media` tab, scroll down repeatedly, and collect image/video URLs from the DOM.

**Cookies/Headers for Sensitive Media:** The key cookie is `auth_token` (plus `ct0` and `gt` tokens which Twitter uses). Using a logged-in session with these cookies will bypass the "sensitive content" interstitial that blocks images/videos. Ensure the scraper account's settings allow sensitive media; otherwise, Twitter's API/HTML might exclude those tweets entirely. If scraping via the web (requests), send a realistic User-Agent and the `Authorization: Bearer <guest token>` header only if using certain internal APIs (this is more relevant for API calls Twitter's frontend makes, but tools like snscrape handle this internally).

**Bypassing Safe Search Filters:** Besides media visibility, Twitter also filters search results for NSFW content unless you opt in. If you use the web search query (e.g. `https://twitter.com/search?q=<term>`), you might need to include `f=live` or similar parameters and be logged in with safe-search off to get NSFW tweets. In practice, using the user's media timeline or tweet IDs directly is simpler. For **video content** (which might be age-gated on the mobile app), the web embed usually works if logged in. In summary, the combination of an authenticated session and proper account settings "bypasses" Twitter's content filters.

**Rate Limits & Best Practices:** Scraping Twitter without the official API means mimicking a web client. Twitter (X) imposes strict rate limits on how many tweets you can view per hour (these limits have changed over time and can be as low as a few thousands tweets/day for unverified accounts). To avoid bans, **pace your requests**. If using snscrape or gallery-dl, you can introduce delays after each tweet or each page of results. Avoid making too many API-like calls in quick succession (e.g., don't scrape hundreds of tweets per minute). If you log in via Selenium, beware that rapid page loads or scrolling could trigger a temporary lock on the account for suspicious activity. It's wise to scrape gradually and, if necessary, **rotate multiple scraper accounts** to stay under the radar. Keep an eye on response headers or errors: if you see HTTP 429 or Twitter's "Rate limit exceeded" JSON message, back off and wait. Also note that Twitter might ban accounts that appear automated, so don't use your primary account – always use a disposable one that you can replace if needed.

## Reddit

**Content Access & Login:** Reddit allows communities to mark themselves NSFW (18+). Viewing such content as a logged-out user will prompt an age-confirmation page. **However, you can often bypass this without a full login** by sending an appropriate cookie or request parameter. Specifically, Reddit uses an `over18=1` cookie to indicate you've confirmed age. If you include this cookie in your requests, you can access NSFW subreddits' JSON or HTML without logging in. For example, using the requests library:

```python
import requests
sess = requests.Session()
sess.cookies.set("over18", "1", domain="reddit.com")
headers = {"User-Agent": "my-scraper 1.0"}
url = "https://old.reddit.com/r/<NSFW_sub>/top/?t=day"
resp = sess.get(url, headers=headers)
print(resp.status_code)  # 200 means success
html = resp.text  # HTML content of the subreddit page
```

This sets the `over18=1` cookie and accesses the NSFW subreddit as if you clicked "Yes, I'm over 18" in a browser. In many cases, this is enough and you **don't need to log in** at all. That said, certain NSFW content (for example, quarantined subreddits or very explicit material) might be hidden without logging in to an account that has joined those communities. For those, you'd create a throwaway Reddit account and in user settings enable "I am over eighteen years old" and disable any NSFW blur. You can then use that account's session cookie or OAuth token to scrape content.

**Scraping Tools & Examples:** A powerful option for media is **gallery-dl** (it supports Reddit as well). For instance, to download all images/videos from a specific Reddit post or subreddit, you can run:

```bash
gallery-dl "https://www.reddit.com/r/<subreddit>/comments/<post_id>/"
```

This will download media in the post (including all top-level images/videos, e.g., Imgur links, Reddit-hosted images, GIFs, etc.). In a Python script you might call gallery-dl via subprocess similarly to the earlier examples. There's also the **Bulk Downloader for Reddit (BDFR)**, which is a Python tool specifically for mass-downloading subreddit content. BDFR can fetch all submissions from a subreddit or user and download the attached media. It may require Reddit API credentials for certain operations, but it can work in an unauthenticated mode for public subreddits (check BDFR's docs for how to configure an app ID if needed).

If you prefer using `requests`/BeautifulSoup or Reddit's JSON, you can get a subreddit's JSON feed directly. For example:

```python
url = "https://www.reddit.com/r/<subreddit>/.json?limit=50"
resp = sess.get(url, headers=headers)  # using the session with over18 cookie
data = resp.json()
for post in data["data"]["children"]:
    post_data = post["data"]
    print(post_data["title"])
    if post_data.get("url"):
        print("Media URL:", post_data["url"])
```

This fetches the latest 50 posts from the subreddit. **Reddit's JSON** will include media links: e.g., for images hosted on reddit's own i.redd.it, the `post_data["url"]` is the direct image URL. If the post is a Reddit video (hosted on v.redd.it), the JSON `post_data["secure_media"]["reddit_video"]["fallback_url"]` gives a direct MP4 link. You might need to append `&raw_json=1` to get unescaped URLs. Another trick: append `.json` to a post's URL to get a JSON with all comments and media info. This is useful for scraping video posts, as the JSON often lists different video quality links.

**Cookies/Headers:** As mentioned, the `over18` cookie is crucial for NSFW content. Also send a **User-Agent header** – Reddit's servers may return a 429 or a blocked message if no User-Agent or a default one is used. A common practice is to use a User-Agent like `"Mozilla/5.0 ... (by /u/yourusername)"` when using the API or requests, but since we are not using the official API here, any browser-like UA is fine. If you do log in with a Reddit account, you might use the session cookie named `reddit_session` (for old Reddit) or bearer tokens from OAuth. Using the web JSON with just the `over18` cookie is simpler for read-only needs.

**Bypassing SafeSearch/Filters:** Reddit's primary filter is the age gate. Once `over18=1` is set, you can view NSFW subreddits' content without further prompts. There is also a "safe search" option on new Reddit that excludes NSFW posts from search results unless toggled off. If you plan to scrape through the search function (e.g., query Reddit for certain keywords), you might need to include `include_over_18=on` in the search URL. For example: `https://www.reddit.com/search.json?q=cats&include_over_18=on`. This ensures NSFW results are not filtered out. When scraping HTML pages via old.reddit.com, once the cookie is set, you'll see NSFW posts normally. Quarantined subreddits (which are different from regular NSFW – they require explicit opt-in via a logged-in account) cannot be accessed without logging in and visiting them at least once with that account.

**Rate Limits & Best Practices:** Reddit's web endpoints allow a decent number of requests, but you should still be mindful. Hitting the `.json` feeds repeatedly might trigger a temporary IP ban or rate-limit (Reddit may return a `429 Too Many Requests` or a Cloudflare challenge if abused). To be safe, limit yourself to **1 request per second or slower** when scraping Reddit without API keys. The official API (if you were to use it) has a strict limit of 60 requests per minute per OAuth token, but web scraping doesn't have a published limit – still, Reddit can detect and block excessive scraping. Use pagination parameters (`?after=<post_id>` in JSON) rather than scraping hundreds of pages in parallel. If downloading a lot of images/videos, consider downloading serially and throttling throughput. Also, prefer **old.reddit.com** for scraping HTML – it's a simpler layout without heavy JavaScript. In summary, Reddit scraping is relatively easy: just handle the NSFW cookie and be gentle with request frequency.

## TikTok

**Content Access & Login:** TikTok does not officially allow pornographic content, so truly explicit NSFW videos are typically removed quickly. That said, there isn't a "Safe Search" flag to toggle for mild content – the main restriction might be age-related: TikTok has a "Restricted Mode" for younger audiences and some videos can be marked 18+ (for instance, TikTok introduced an 18+ flag for LIVE streams and possibly for certain content). If you access TikTok without logging in, you can still view most public videos, but eventually the site will nag you to log in. **Generally, you do not need to log in to scrape public TikTok videos**, unless you run into age-gated content. If a video is age-restricted, attempting to view it without login will prompt you to sign in to confirm age. In such cases, using an account that is 18+ (set birthdate appropriately) can unlock those videos. For scraping purposes, many users skip the login by using direct video URLs or third-party services, but we'll focus on direct methods.

**Scraping Tools & Examples:** The go-to solution for TikTok is **yt-dlp**, since it supports TikTok video downloads out-of-the-box. You can invoke yt-dlp in a Python script. For example, to download a single video by URL:

```python
import yt_dlp

video_url = "https://www.tiktok.com/@<user>/video/<video_id>"
ydl_opts = {"outtmpl": "%(id)s.%(ext)s"}  # filename template
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(video_url, download=True)
    print("Downloaded:", info.get("title"))
```

This will download the video file (TikTok videos are MP4). **yt-dlp** can often get the highest quality and *sometimes* even avoid the watermark. If you find the downloaded videos have the TikTok watermark, note that this is usually burned into the video by TikTok for public links. Some online tools or API endpoints can fetch no-watermark versions (by using TikTok's private API or playback endpoint), but that goes beyond standard usage. Another tool, **gallery-dl**, also supports TikTok profiles. You could run `gallery-dl "https://www.tiktok.com/@<username>"` to attempt downloading all posts from a user. Ensure you have the latest version, as TikTok frequently changes its site; gallery-dl updates have addressed things like photo slideshows support in TikTok posts. In practice, gallery-dl will retrieve each video (and images in slideshows) from that profile.

For a lower-level approach, you can scrape TikTok video pages using requests/BS4. TikTok video pages are client-rendered, but the page's HTML contains a JSON snippet with video metadata including the video URL. For example:

```python
url = "https://www.tiktok.com/@<user>/video/<id>"
resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
if resp.status_code == 200:
    text = resp.text
    # TikTok embeds JSON in <script id="SIGI_STATE"> ... </script>
    import re, json
    m = re.search(r'id="SIGI_STATE".*?>(\{.*\})</script>', text)
    if m:
        data = json.loads(m.group(1))
        video_url = data["ItemModule"][str(<id>)]["video"]["playAddr"]  # example path
        video_url = video_url.replace("playwm", "play")  # remove 'wm' to attempt no-watermark URL
        video_content = requests.get(video_url).content
        with open("video.mp4", "wb") as f:
            f.write(video_content)
```

This is a rough example of extracting the video URL. TikTok's HTML state JSON can be complex and often requires adjusting to changes or using their unofficial API endpoints. The easier path is to rely on **yt-dlp**, which encapsulates these tricks.

If you need to scrape **many videos or an entire hashtag/user feed**, consider using the **TikTok API Python package** (unofficial, e.g. `TikTokApi` library). It allows retrieval of videos by user or hashtag without web scraping, but it internally uses browser emulation and can be fragile when TikTok updates its security. Another approach is to automate a headless browser with **Selenium or Playwright**: you can load a user's page and scroll down to load more videos. TikTok's site will load a limited set of videos and then require clicking a "Load more" or using the API. A headless browser can capture the network calls or dynamically load the content that static requests might miss. Again, these methods are more complex – using yt-dlp or gallery-dl is typically much simpler for downloading videos.

**Cookies/Headers:** TikTok heavily uses browser fingerprinting and anti-bot measures (like Akamai or Cloudflare). Using a common User-Agent and perhaps an `Accept-Language` header can help appear as a normal browser. If you encounter a block (like a HTML page asking for CAPTCHA or "Access Denied"), you may need to use a proxy or a real browser context. Logging in is generally not needed unless dealing with age restrictions. If so, you'd have to supply TikTok's session cookies (which include `sid_tt` and others after login) to your requests or configure yt-dlp to use a cookies file (`yt-dlp --cookies-from-browser chrome "tiktok_link"` if using CLI). In most cases, though, providing cookies is not necessary for TikTok public videos.

**Bypassing Filters:** Since TikTok doesn't allow truly adult content, there's no explicit "NSFW filter" to bypass like on Twitter/Reddit. The main gating is age: if a video is labeled 18+, the page might not show it without login. Using an authenticated session of an 18+ account is the bypass. TikTok's **Restricted Mode** (a setting to hide certain content from yourself) is off by default; just ensure your scraper account (if you use one) hasn't enabled restricted mode. Also be aware TikTok might geo-restrict some content (certain music or videos might not play in certain countries). To bypass geo-blocks, you might need a VPN/proxy in the allowed region or use a tool like yt-dlp which often can fetch the video via alternate CDNs.

**Rate Limits & Best Practices:** TikTok's web can detect rapid, repetitive access. If you scrape too quickly (especially without varying your client fingerprint), TikTok may start returning blank pages or captchas. To scrape reliably, treat TikTok like you would any site with bot detection: **throttle your requests**, use proxies if scraping at scale (to avoid one IP making hundreds of requests in a short time), and consider randomizing your user-agent or using different accounts. Yt-dlp internally can handle retries and might even rotate through TikTok's API endpoints, so using it for bulk downloads (with a short pause between each) is a good strategy. If one method fails (e.g., direct requests hitting anti-bot walls), switching to a headless browser might bypass those at the cost of speed. Always monitor for the telltale signs of blocking (e.g., a response that contains `"<div>Access Denied</div>"` or a captcha challenge) and implement a back-off strategy or manual intervention when encountered. In summary, **download videos one at a time** with a slight delay, and you should stay under TikTok's radar for moderate scraping needs.

## YouTube

**Content Access & Login:** YouTube's content is mostly SFW, but there is **age-restricted content** (for instance, videos with nudity in an educational context, or explicit music videos, etc.). YouTube will prompt you to log in to confirm age if a video is marked 18+. There is also a "Restricted Mode" (meant for institutions/parents to filter content), but that's off unless you explicitly enable it. To scrape **adult or age-gated YouTube videos**, you should plan to use an **authenticated context** or a known workaround. The simplest: use your Google account's cookies with a downloader tool. For example, **yt-dlp** can automatically pull cookies from your browser. The command-line:

```bash
yt-dlp --cookies-from-browser <browser_name> "<youtube_link>"
```

will let yt-dlp temporarily use your logged-in cookies to access the video. In a Python script, you can achieve the same by supplying a cookies file to yt-dlp. (You can export cookies from your browser using an extension, then use `yt-dlp --cookies cookies.txt <link>`.) This is usually required for **age-confirmation videos**.

It's worth noting that yt-dlp has made progress in bypassing age-gates without login. It can often use YouTube's internal API (Innertube) to get video data by pretending to be the YouTube Android app, which doesn't require age confirmation. In many cases, yt-dlp will automatically try these methods. If it ever fails with an age restriction error, that's when using cookies or logging in becomes necessary.

**Scraping Tools & Examples:** **yt-dlp (or youtube-dl)** is the standard for downloading YouTube videos via Python. For example:

```python
from yt_dlp import YoutubeDL

ydl_opts = {"format": "best", "outtmpl": "%(title)s.%(ext)s"}
with YoutubeDL(ydl_opts) as ydl:
    ydl.download(["https://www.youtube.com/watch?v=<video_id>"])
```

This will download the video at the best quality. If the video is age-restricted, you might get an error instructing you to use cookies. In that case, update `ydl_opts` with a cookies file:

```python
ydl_opts = {
    "format": "best",
    "outtmpl": "%(title)s.%(ext)s",
    "cookiefile": "path/to/youtube_cookies.txt"
}
```

and then run `ydl.download([...])` again. The cookies should belong to an account that's 18+. Once set up, yt-dlp will handle all the details of retrieving the video URL(s), including merging separate audio/video streams if needed.

For scraping many videos (like a whole channel or playlist), yt-dlp can do that too (e.g., passing a playlist URL or using the `ytsearch` feature to search YouTube). If you need just thumbnails or preview images, note that YouTube has predictable URLs for thumbnails (e.g., `https://img.youtube.com/vi/<video_id>/maxresdefault.jpg` for the highest-res thumbnail). You can construct those and download images easily with requests, no login needed.

**Cookies/Headers:** When not using yt-dlp, if you try to manually scrape YouTube via requests, you'll find that the video files themselves come from Google video servers and often require a signature or cookies. It's not practical to manually reimplement YouTube's player logic. Instead, leverage the tools. If you *do* attempt some HTML parsing (like scraping video titles or comments), use a logged-in cookie if needed for age content. For example, to fetch an age-gated video's page HTML, you could supply the `LOGIN_INFO` and `SID` cookies from your YouTube account – but again, the page HTML itself might not give you the video URL easily due to encryption/signature mechanism. So, the bottom line: use **yt-dlp's handling of cookies or its internal tricks** for any restricted videos.

**Bypassing Safe Search/Filters:** YouTube's "Restricted Mode" is an optional filter – unlikely relevant unless the network or account you use has it on. Ensure your scraping environment isn't using restricted mode (you can check at the bottom of YouTube pages for "Restricted Mode: Off"). If it were on, it would block many videos. As for search, if you use yt-dlp's search (`"ytsearch5:<query>"`), it might abide by safe search settings of the API – but since we assume default, you'll get all results. To be thorough: if you wanted to ensure even potentially "borderline" content appears in search, use an account with no restrictions.

**Rate Limits & Best Practices:** Downloading content from YouTube is generally allowed at scale (YouTube doesn't have a strict public rate limit for watching videos, apart from occasional CAPTCHA if usage is unusual). However, if you scrape metadata or perform many search queries via the web, Google might throw up a CAPTCHA. For example, making hundreds of search requests via HTTP could lead to temporary blocks. To avoid this, use the built-in capabilities of yt-dlp to fetch playlists or channel uploads in one go, rather than querying individual video pages en masse. If you do need to scrape a lot of videos, consider **spacing out your downloads** or limiting bandwidth (`--limit-rate` in yt-dlp) so it doesn't look like a DDoS. Generally, downloading even dozens of videos in sequence is fine. YouTube serves massive traffic and is used to users binge-watching, so the video serving is robust. Just be cautious with *other* requests (like mass HTTP API calls or comment scraping) – those should be done slower and possibly with an API key if available.

Finally, always keep **yt-dlp updated**. These social platforms change often, and tools frequently release updates to adapt. Using established libraries and tools (requests, BeautifulSoup, Selenium, Instaloader, gallery-dl, yt-dlp) will save you time and help navigate login and content filters in a Python-friendly way. By combining authenticated sessions, the right cookies/headers, and careful throttling, you can ethically scrape images and videos – including NSFW content meant only for adult eyes – from all major social media platforms.

## Implementation in This Project

This media scraper implements the guidelines above with:

### Multiple Content Sources
- **Reddit**: Direct NSFW subreddit access with `over18=1` cookie
- **DeviantArt**: Mature content scraping with explicit search terms
- **Instagram**: API-based profile scraping with 4-method fallback system
- **Twitter/X**: Ready for implementation with authenticated sessions
- **TikTok**: Ready for yt-dlp integration
- **YouTube**: Ready for age-restricted content with yt-dlp

### Authentication & Rate Limiting
- Proper user-agent headers and session management
- Rate limiting with delays between requests
- Cookie-based authentication for age-restricted content
- Graceful fallback when rate limits are encountered

### Safe Search Bypass
- Reddit: `over18=1` cookie automatically set
- DeviantArt: Mature content search enabled
- Instagram: No content filtering (platform doesn't allow NSFW)
- Fallback image services without safe search restrictions

### Best Practices Implemented
- Request throttling to avoid rate limits
- User-agent rotation and realistic headers
- Error handling and retry logic
- Comprehensive logging for debugging
- Multiple fallback methods for each platform

**Sources:** Platforms' scraping discussions and tool documentation were referenced for accuracy on login requirements and methods (e.g., Instagram login requirement, Twitter NSFW login, Reddit over18 cookie bypass, and YouTube age restriction bypass using cookies). Each tool mentioned (Instaloader, gallery-dl, yt-dlp, etc.) is well-documented in their official docs for further details. Always ensure your use case complies with the platforms' Terms of Service and legal requirements when scraping. 
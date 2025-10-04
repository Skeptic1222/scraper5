# EroGarga Crawler

The downloader includes a best-effort crawler to pull images from EroGarga without login. It works in two phases:

1. Discover thread pages
   - Uses DuckDuckGo HTML search with `site:erogarga.com <query>` to discover recent thread URLs.
   - Fetches the HTML via `_fetch_html()`. If the page needs JS, Firecrawl is used automatically when `FIRECRAWL_API_KEY` is present.

2. Extract images
   - Parses the thread HTML with BeautifulSoup and extracts `<img>` URLs (absolute URLs constructed if needed).
   - Downloads the first N images in parallel (small thread pool) via the robust `_download_file()` method.

Notes:
- This avoids login-only content. For richer results, consider adding a login-based crawler later.
- If EroGarga changes markup, adjust the discovery pattern in `_crawl_erogarga_threads()` accordingly.
- Firecrawl greatly improves success with dynamic content.

## Code Locations
- `working_media_downloader.py`
  - `_crawl_erogarga_threads()` — thread discovery + image extraction
  - `_search_erogarga()` — image-only fallback via DuckDuckGo Images API
  - `_fetch_html()` — requests → Firecrawl fallback
  - `_download_file()` — robust download with retries/stall detection

## Usage
- Select `EroGarga` in the UI and run a query (e.g., `cosplay`).
- The dashboard shows per-file progress. Results are saved under `downloads/erogarga/`.


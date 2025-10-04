"""
Enhanced Working Downloader - Bridges job system with actual downloading capability
Integrates working_media_downloader with job tracking and asset management
"""
import os
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
import subprocess
import re
import requests
from urllib.parse import quote
from threading import Lock
from working_media_downloader import media_downloader
from db_job_manager import db_job_manager
# Import simple asset manager as default
from simple_asset_manager import simple_asset_manager
# Import improved adult scraper
try:
    from improved_adult_scraper import ImprovedAdultScraper
    ADULT_SCRAPER_AVAILABLE = True
except ImportError:
    ADULT_SCRAPER_AVAILABLE = False
    logging.getLogger(__name__).warning("improved_adult_scraper not available")

# Import multi-method scraping framework
try:
    from scrapers.multi_method_integration import try_multi_method_scrape
    MULTI_METHOD_AVAILABLE = True
except ImportError:
    MULTI_METHOD_AVAILABLE = False
    logging.getLogger(__name__).warning("multi-method framework not available")

# Import source filtering system
try:
    from scrapers.source_filters import filter_sources, prioritize_sources, get_recommended_sources
    SOURCE_FILTER_AVAILABLE = True
except ImportError:
    SOURCE_FILTER_AVAILABLE = False
    logging.getLogger(__name__).warning("source_filters not available")

# Import image quality filtering
try:
    from scrapers.image_quality_filter import filter_valid_images, is_valid_image
    IMAGE_FILTER_AVAILABLE = True
except ImportError:
    IMAGE_FILTER_AVAILABLE = False
    logging.getLogger(__name__).warning("image_quality_filter not available")

# Import performance tracking
try:
    from scrapers.performance_tracker import (
        track_job_start, track_source_result, track_filtering, track_job_end
    )
    PERFORMANCE_TRACKING_AVAILABLE = True
except ImportError:
    PERFORMANCE_TRACKING_AVAILABLE = False
    logging.getLogger(__name__).warning("performance_tracker not available")

# ====================
# CONFIGURATION
# ====================
def get_config():
    """Get configuration from environment variables (loaded at runtime, not import time)"""
    return {
        'MAX_CONCURRENT_SOURCES': int(os.getenv('MAX_CONCURRENT_SOURCES', '5')),
        'SOURCE_TIMEOUT': int(os.getenv('SOURCE_TIMEOUT', '30')),
        'REQUEST_TIMEOUT': int(os.getenv('REQUEST_TIMEOUT', '15')),
        'MAX_RETRIES_PER_SOURCE': int(os.getenv('MAX_RETRIES_PER_SOURCE', '3')),
        'MAX_RETRIES_PER_ITEM': int(os.getenv('MAX_RETRIES_PER_ITEM', '2')),
        'MIN_DOWNLOAD_SPEED': int(os.getenv('MIN_DOWNLOAD_SPEED', '1024')),
        'STALL_TIMEOUT': int(os.getenv('STALL_TIMEOUT', '30')),
        'CIRCUIT_BREAKER_THRESHOLD': int(os.getenv('CIRCUIT_BREAKER_THRESHOLD', '5')),
        'CIRCUIT_BREAKER_TIMEOUT': int(os.getenv('CIRCUIT_BREAKER_TIMEOUT', '60'))
    }

# ====================
# UTILITY FUNCTIONS
# ====================
def cleanup_temp_files(directory):
    """
    Clean up temporary files (.ytdl, .part, .tmp, etc.) from download directory
    These are incomplete downloads or temporary files that should be removed
    """
    if not os.path.exists(directory):
        return

    temp_extensions = ['.ytdl', '.part', '.tmp', '.download', '.crdownload']
    removed_count = 0

    try:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                # Check if file has temp extension
                if any(filename.endswith(ext) for ext in temp_extensions):
                    filepath = os.path.join(root, filename)
                    try:
                        os.remove(filepath)
                        removed_count += 1
                        logging.info(f"Cleaned up temp file: {filename}")
                    except Exception as e:
                        logging.warning(f"Could not remove temp file {filename}: {e}")

        if removed_count > 0:
            logging.info(f"Cleanup complete: Removed {removed_count} temporary files from {directory}")
    except Exception as e:
        logging.error(f"Error during temp file cleanup: {e}")

# ====================
# ERROR LOGGING SETUP
# ====================
# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure error logger
error_logger = logging.getLogger('download_errors')
error_logger.setLevel(logging.INFO)

# File handler for download errors
error_handler = logging.FileHandler('logs/download_errors.log')
error_handler.setLevel(logging.INFO)
error_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)

# Console handler for debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(error_formatter)
error_logger.addHandler(console_handler)

# Thread-safe statistics
stats_lock = Lock()

def get_asset_manager():
    """Get the appropriate asset manager based on context"""
    try:
        # Try to import Flask and check if we're in app context
        from flask import has_app_context
        if has_app_context():
            # We're in Flask context, try to use database manager
            try:
                from db_asset_manager import db_asset_manager
                return db_asset_manager
            except:
                pass
    except:
        pass

    # Fall back to simple asset manager
    return simple_asset_manager
from scrapers.enhanced_scraper import enhanced_scraper, perform_enhanced_search
from scrapers.working_api_scraper import search_all_sources as api_search, search_source as api_search_single

def process_single_source(source, query, max_content, safe_search, output_dir, user_id, job_id, source_timeout=30):
    """
    Process a single source with timeout and error handling

    Args:
        source_timeout: Timeout in seconds for this source (default 30)

    Returns:
        dict: {
            'source': source_name,
            'success': bool,
            'downloaded': int,
            'images': int,
            'videos': int,
            'files': list,
            'error': str (if failed)
        }
    """
    result = {
        'source': source,
        'success': False,
        'downloaded': 0,
        'images': 0,
        'videos': 0,
        'files': [],
        'error': None
    }

    start_time = time.time()
    error_logger.info(f"Starting source: {source} | Query: {query} | Max: {max_content}")

    try:
        # Map source names
        source_map = {
            'google_images': 'google',
            'bing_images': 'bing',
            'yahoo_images': 'yahoo',
            'duckduckgo_images': 'duckduckgo',
            'yandex_images': 'yandex',
            'unsplash': 'unsplash',
            'pexels': 'pexels',
            'pixabay': 'pixabay',
            'imgur': 'imgur',
            'reddit': 'reddit',
            'picsum': 'picsum',
            'placeholder': 'placeholder',
            'dummyimage': 'dummyimage',
            'lorempixel': 'lorempixel',
            'robohash': 'robohash'
        }

        backend_source = source_map.get(source, source)
        enhanced_sources = ['google', 'bing', 'yahoo', 'duckduckgo', 'yandex']
        video_sources = ['youtube', 'vimeo', 'dailymotion', 'tiktok', 'twitch', 'rumble', 'bitchute', 'pornhub', 'xvideos', 'redtube', 'motherless', 'xhamster', 'youporn', 'spankbang', 'redgifs']
        api_sources = ['unsplash', 'pexels', 'pixabay', 'picsum', 'placeholder', 'dummyimage', 'lorempixel', 'robohash']

        if backend_source in api_sources:
            # Use working API scraper
            error_logger.info(f"API SCRAPER: {source} | Using working_api_scraper for {backend_source}")
            urls = api_search_single(backend_source, query, max_content, safe_search)

            error_logger.info(f"API SCRAPER: {source} | Got {len(urls)} URLs from {backend_source}")

            # Convert URLs to dict format for compatibility
            search_results = [{'url': url, 'title': f'{query}_{i}', 'source': backend_source, 'type': 'image'} for i, url in enumerate(urls)]

            # Log first few results
            for idx, item in enumerate(search_results[:3]):
                error_logger.info(f"API SCRAPER: {source} | Result {idx+1}: {item['url']}")

            # Download each result (ADDED - THIS WAS MISSING!)
            for idx, item in enumerate(search_results):
                try:
                    if not isinstance(item, dict) or 'url' not in item:
                        error_logger.error(f"INVALID ITEM: {source} | Item {idx}: {item}")
                        continue

                    error_logger.info(f"DOWNLOADING: {source} | Item {idx} | URL: {item['url'][:100]}")

                    file_info = media_downloader.download_direct_url(
                        url=item['url'],
                        title=f'{query}_{backend_source}_{idx}',
                        source=backend_source,
                        user_id=user_id,
                        progress_callback=None,
                        output_dir=output_dir
                    )

                    if file_info and file_info.get('filepath'):
                        result['downloaded'] += 1
                        result['images'] += 1
                        result['files'].append(file_info)
                        error_logger.info(f"SUCCESS: {source} | File: {os.path.basename(file_info['filepath'])}")
                        # Per-file progress update for dashboard
                        try:
                            db_job_manager.add_progress_update(
                                job_id,
                                message=f"Downloaded {os.path.basename(file_info['filepath'])} from {backend_source}",
                                progress=0,
                                downloaded=result['downloaded'],
                                images=result['images'],
                                videos=result['videos'],
                                current_file=file_info['filepath']
                            )
                        except Exception:
                            pass

                except Exception as e:
                    error_logger.warning(f"ERROR: {source} | Item {idx} | {str(e)}")
                    continue

        elif backend_source in video_sources:
            # Check if this is an adult source and use improved scraper
            adult_sources = ['pornhub', 'xvideos', 'redtube', 'motherless', 'xhamster', 'youporn', 'spankbang', 'redgifs']

            if backend_source in adult_sources and ADULT_SCRAPER_AVAILABLE:
                # Use improved adult scraper with curl_cffi and fixed selectors
                error_logger.info(f"ADULT SCRAPER: {source} | Using ImprovedAdultScraper for '{backend_source}'")

                try:
                    scraper = ImprovedAdultScraper(output_dir=output_dir)
                    video_files = scraper.scrape(backend_source, query, max_content)
                    error_logger.info(f"ADULT SCRAPER: {source} | Downloaded {len(video_files)} files")
                except Exception as e:
                    error_logger.warning(f"ADULT SCRAPER: {source} | Error: {e}")
                    video_files = []
            else:
                # Download videos using yt-dlp
                error_logger.info(f"VIDEO: {source} | Using yt-dlp for '{backend_source}'")

                def download_videos_with_ytdlp(src: str, q: str, count: int, out_dir: str):
                    try:
                        os.makedirs(out_dir, exist_ok=True)
                        before = set(os.listdir(out_dir))
                        base_cmd = [
                            'yt-dlp',
                            '--no-warnings',
                            '--quiet',
                            '--no-playlist',
                            '--format', 'best[ext=mp4]/best',
                            '--output', f'{out_dir}/%(title)s.%(ext)s',
                        ]

                        video_urls = []

                        # YouTube: use ytsearchN directly
                        if src == 'youtube':
                            video_urls = [f"ytsearch{max(1, count)}:{q}"]
                        else:
                            # Build search URL per platform
                            search_url = None
                            patterns = []
                            if src == 'vimeo':
                                search_url = f"https://vimeo.com/search?q={quote(q)}"
                                patterns = [r'https?://vimeo\.com/\d+']
                            elif src == 'dailymotion':
                                search_url = f"https://www.dailymotion.com/search/{quote(q)}"
                                patterns = [r'https?://www\.dailymotion\.com/video/[a-zA-Z0-9]+' ]
                            elif src == 'tiktok':
                                search_url = f"https://www.tiktok.com/search?q={quote(q)}"
                                patterns = [r"https?://www\.tiktok\.com/[^\"']+/video/\d+"]
                            elif src == 'twitch':
                                search_url = f"https://www.twitch.tv/search?term={quote(q)}"
                                patterns = [r'https?://www\.twitch\.tv/videos/\d+', r'https?://clips\.twitch\.tv/[\w-]+']
                            elif src == 'pornhub':
                                search_url = f"https://www.pornhub.com/video/search?search={quote(q)}"
                                patterns = [r'https?://www\.pornhub\.com/view_video\.php\?viewkey=[^"& ]+']
                            elif src == 'xvideos':
                                search_url = f"https://www.xvideos.com/?k={quote(q)}"
                                patterns = [r'https?://www\.xvideos\.com/video\d+/[^"/]+' ]
                            elif src == 'redtube':
                                search_url = f"https://www.redtube.com/?search={quote(q)}"
                                patterns = [r'https?://www\.redtube\.com/\d+']
                            elif src == 'motherless':
                                search_url = f"https://motherless.com/search/videos?term={quote(q)}"
                                patterns = [r'https?://motherless\.com/[^"\s]+' ]
                            elif src == 'rumble':
                                search_url = f"https://rumble.com/search/video?q={quote(q)}"
                                patterns = [r'https?://rumble\.com/v[^"\s]+']
                            elif src == 'bitchute':
                                search_url = f"https://www.bitchute.com/search/?query={quote(q)}"
                                patterns = [r'https?://www\.bitchute\.com/video/[A-Za-z0-9]+/']
                            elif src == 'xhamster':
                                search_url = f"https://xhamster.com/search/{quote(q)}"
                                patterns = [r'https?://xhamster\.com/videos/[^"\s>]+' ]
                            elif src == 'youporn':
                                search_url = f"https://www.youporn.com/search/?query={quote(q)}"
                                patterns = [r'https?://www\.youporn\.com/watch/[^"\s>]+' ]
                            elif src == 'spankbang':
                                search_url = f"https://spankbang.com/s/{quote(q)}"
                                patterns = [r'https?://spankbang\.com/[a-z0-9]+/video/[^"\s>]+' ]
                            elif src == 'redgifs':
                                search_url = f"https://www.redgifs.com/search?q={quote(q)}"
                                patterns = [r'https?://www\.redgifs\.com/watch/[^"\s>]+' ]

                            try:
                                if search_url:
                                    resp = requests.get(search_url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
                                    if resp.status_code == 200:
                                        html = resp.text
                                        urls_found = []
                                        for pat in patterns:
                                            urls_found.extend(re.findall(pat, html))
                                        # Resolve redirects / canonicalize and de-dup
                                        resolved = []
                                        seen = set()
                                        for u in urls_found:
                                            try:
                                                r = requests.head(u, allow_redirects=True, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                                                final = r.url or u
                                            except Exception:
                                                final = u
                                            if final not in seen:
                                                seen.add(final)
                                                resolved.append(final)
                                            if len(resolved) >= max(1, count):
                                                break
                                        video_urls = resolved
                            except Exception as e:
                                error_logger.warning(f"VIDEO: Failed to extract URLs for {src}: {e}")

                            # Fallback: use search URL directly if no URLs extracted
                            if not video_urls:
                                if search_url:
                                    video_urls = [search_url]

                        # Run yt-dlp for each video URL or search query item
                        for target in video_urls:
                            try:
                                result = subprocess.run(base_cmd + [target], capture_output=True, text=True, timeout=180)
                                if result.returncode != 0:
                                    error_logger.warning(f"VIDEO: yt-dlp returned {result.returncode} for {target}: {result.stderr[:200]}")
                            except subprocess.TimeoutExpired:
                                error_logger.warning(f"VIDEO: yt-dlp timeout for {target}")
                            except Exception as e:
                                error_logger.warning(f"VIDEO: Exception for {target}: {e}")

                        after = set(os.listdir(out_dir))
                        new_files = [f for f in sorted(after - before) if os.path.splitext(f)[1].lower() in ('.mp4', '.webm', '.mkv', '.mov')]
                        return [os.path.join(out_dir, f) for f in new_files]
                    except subprocess.TimeoutExpired:
                        error_logger.warning(f"VIDEO: yt-dlp timeout for {src}:{q}")
                        return []
                    except Exception as e:
                        error_logger.warning(f"VIDEO: Exception running yt-dlp: {e}")
                        return []

                video_files = download_videos_with_ytdlp(backend_source, query, max_content, output_dir)
                error_logger.info(f"VIDEO: {source} | Downloaded {len(video_files)} files")

            for fp in video_files:
                try:
                    if os.path.exists(fp):
                        result['downloaded'] += 1
                        result['videos'] += 1
                        result['files'].append({
                            'filename': os.path.basename(fp),
                            'filepath': fp,
                            'title': os.path.splitext(os.path.basename(fp))[0],
                            'source': backend_source,
                            'original_url': '',
                            'content_type': 'video/mp4',
                            'file_size': os.path.getsize(fp),
                            'download_time': 0,
                            'download_speed': 0,
                            'user_id': user_id,
                            'downloaded_at': datetime.utcnow().isoformat()
                        })
                except Exception as e:
                    error_logger.warning(f"VIDEO: Error adding file {fp}: {e}")

        elif backend_source in enhanced_sources:
            # Use enhanced scraper
            error_logger.info(f"ENHANCED SCRAPER: {source} | Using perform_enhanced_search for {backend_source}")
            search_results = perform_enhanced_search(
                query=query,
                sources=[backend_source],
                limit_per_source=max_content,
                safe_search=safe_search,
                include_videos=False,
                include_adult=not safe_search
            )

            error_logger.info(f"ENHANCED SCRAPER: {source} | Got {len(search_results)} search results from {backend_source}")

            # Log first few results for debugging
            for idx, item in enumerate(search_results[:3]):
                error_logger.info(f"ENHANCED SCRAPER: {source} | Result {idx+1}: {item}")

            # Download each result with timeout
            for idx, item in enumerate(search_results):
                try:
                    # Validate item is a dictionary
                    if not isinstance(item, dict):
                        error_logger.error(f"INVALID ITEM: {source} | Expected dict, got {type(item)}: {item}")
                        continue

                    if 'url' not in item:
                        error_logger.error(f"MISSING URL: {source} | Item {idx} missing 'url' key: {item}")
                        continue

                    error_logger.info(f"DOWNLOADING: {source} | Item {idx} | URL: {item['url'][:100]}")

                    # Add per-request timeout
                    import signal

                    def timeout_handler(signum, frame):
                        raise TimeoutError(f"Download timeout for {item.get('url', 'unknown')}")

                    # Note: signal.alarm only works on Unix, use threading.Timer for Windows
                    file_info = media_downloader.download_direct_url(
                        url=item['url'],
                        title=f'{query}_{backend_source}_{idx}',
                        source=backend_source,
                        user_id=user_id,
                        progress_callback=None,
                        output_dir=output_dir
                    )

                    if file_info and file_info.get('filepath'):
                        result['downloaded'] += 1
                        result['files'].append(file_info)

                        if item['type'] in ['image', 'adult']:
                            result['images'] += 1
                        elif item['type'] == 'video':
                            result['videos'] += 1

                        error_logger.info(f"SUCCESS: {source} | File: {os.path.basename(file_info['filepath'])}")

                except TimeoutError as te:
                    error_logger.warning(f"TIMEOUT: {source} | URL: {item.get('url')} | {str(te)}")
                    continue
                except Exception as e:
                    error_logger.warning(f"ERROR: {source} | Item {idx} | {str(e)}")
                    continue

        else:
            # Use basic downloader for free sources
            error_logger.info(f"BASIC DOWNLOADER: {source} | Using media_downloader.search_and_download for {backend_source}")
            # Wrap a progress callback to stream basic downloader progress
            def basic_progress(msg: str):
                try:
                    db_job_manager.add_progress_update(
                        job_id,
                        message=msg,
                        progress=0,
                        downloaded=result['downloaded'],
                        images=result['images'],
                        videos=result['videos'],
                        current_file=msg
                    )
                except Exception:
                    pass

            basic_result = media_downloader.search_and_download(
                query=query,
                sources=[backend_source],
                limit=max_content,
                safe_search=safe_search,
                progress_callback=basic_progress,
                user_id=user_id,
                output_dir=output_dir
            )

            error_logger.info(f"BASIC DOWNLOADER: {source} | Result: {basic_result.get('total', 0)} files, {len(basic_result.get('downloaded', []))} downloaded")

            if basic_result.get('downloaded'):
                for file_info in basic_result['downloaded']:
                    if file_info and file_info.get('filepath'):
                        result['downloaded'] += 1
                        result['images'] += 1  # Basic downloader typically gets images
                        result['files'].append(file_info)
                        error_logger.info(f"SUCCESS: {source} | File: {os.path.basename(file_info['filepath'])}")
                        # Per-file progress update so dashboard reflects threaded downloads too
                        try:
                            db_job_manager.add_progress_update(
                                job_id,
                                message=f"Downloaded {os.path.basename(file_info['filepath'])} from {backend_source}",
                                progress=0,
                                downloaded=result['downloaded'],
                                images=result['images'],
                                videos=result['videos'],
                                current_file=file_info['filepath']
                            )
                        except Exception:
                            pass

        # MULTI-METHOD FALLBACK: If primary methods failed, try multi-method framework
        if result['downloaded'] == 0 and MULTI_METHOD_AVAILABLE:
            error_logger.info(f"MULTI-METHOD FALLBACK: {source} | Primary methods failed, trying multi-method framework")
            try:
                multi_result = try_multi_method_scrape(
                    source=source,
                    query=query,
                    max_results=max_content,
                    output_dir=output_dir,
                    content_type='any'
                )

                if multi_result['success'] and multi_result['downloaded'] > 0:
                    error_logger.info(f"MULTI-METHOD SUCCESS: {source} | Downloaded: {multi_result['downloaded']} files using {multi_result.get('methods_tried', 0)} methods")
                    result['downloaded'] = multi_result['downloaded']
                    result['images'] = multi_result['images']
                    result['videos'] = multi_result['videos']
                    result['files'] = multi_result['files']
                else:
                    error_logger.warning(f"MULTI-METHOD FAILED: {source} | {multi_result.get('error', 'Unknown error')}")

            except Exception as multi_err:
                error_logger.error(f"MULTI-METHOD ERROR: {source} | {str(multi_err)}")

        result['success'] = result['downloaded'] > 0
        elapsed = time.time() - start_time
        error_logger.info(f"COMPLETED: {source} | Downloaded: {result['downloaded']} | Time: {elapsed:.2f}s")

    except TimeoutError as te:
        result['error'] = f"Timeout after {source_timeout}s"
        error_logger.error(f"TIMEOUT: {source} | {str(te)}")
    except Exception as e:
        result['error'] = str(e)
        error_logger.error(f"FAILED: {source} | Error: {str(e)}")

    return result

def run_download_job(job_id, query, sources, max_content, total_file_limit=0, total_size_limit=0, timeout_seconds=0, content_types=None, quality_settings=None, safe_search=True, user_id=None):
    """
    Main entry point for download jobs - connects all components

    Args:
        job_id: Unique job identifier
        query: Search query
        sources: List of sources to search
        max_content: Maximum content per source
        total_file_limit: Total files limit across all sources (0 = no limit)
        total_size_limit: Total size limit in MB (0 = no limit)
        timeout_seconds: Job timeout in seconds (0 = unlimited)
        content_types: Dict with 'images' and 'videos' boolean flags
        quality_settings: Dict with quality preferences (image_size, video_quality, etc.)
        safe_search: Enable safe search
        user_id: User ID for tracking
    """
    # Set defaults for optional parameters
    if content_types is None:
        content_types = {"images": True, "videos": True}
    if quality_settings is None:
        quality_settings = {}
    # Get Flask app instance for context
    from flask import current_app

    # Run within Flask app context to access database
    with current_app.app_context():
        job_start_time = time.time()
        try:
            # Load configuration at runtime (after .env is loaded by Flask)
            config = get_config()
            max_concurrent = config['MAX_CONCURRENT_SOURCES']
            source_timeout = config['SOURCE_TIMEOUT']

            # Job timeout - use user-specified timeout or fall back to env variable
            # 0 means unlimited (no timeout)
            if timeout_seconds == 0:
                global_job_timeout = int(os.getenv('GLOBAL_JOB_TIMEOUT', '0'))  # 0 = unlimited by default
            else:
                global_job_timeout = timeout_seconds

            # Update job status to running
            db_job_manager.update_job(
                job_id,
                status='running',
                message=f'Starting parallel search for "{query}" ({max_concurrent} concurrent sources)...',
                progress=0
            )

            # Create output directory
            output_dir = os.path.join('C:\\inetpub\\wwwroot\\scraper\\downloads',
                                     f'{query.replace(" ", "_")}_{int(time.time())}')
            os.makedirs(output_dir, exist_ok=True)

            # Calculate max content per source
            # Don't divide by sources - each source should try for the full amount
            # The total_file_limit will stop the job when enough files are collected
            max_per_source = max_content if max_content > 0 else 100  # 100 per source if no limit

            # APPLY SOURCE FILTERING - Remove blacklisted and inappropriate sources
            if SOURCE_FILTER_AVAILABLE:
                original_count = len(sources)

                # Determine content type filter
                content_type_filter = 'any'
                if content_types.get('images') and not content_types.get('videos'):
                    content_type_filter = 'images'
                elif content_types.get('videos') and not content_types.get('images'):
                    content_type_filter = 'videos'

                # Filter sources
                sources = filter_sources(sources, content_type=content_type_filter, query=query)

                # Prioritize remaining sources
                sources = prioritize_sources(sources, content_type=content_type_filter, query=query)

                filtered_count = original_count - len(sources)
                if filtered_count > 0:
                    error_logger.info(f"SOURCE FILTERING: Removed {filtered_count} inappropriate sources ({original_count} → {len(sources)})")
                    error_logger.info(f"FILTERED SOURCES: {sources[:10]}..." if len(sources) > 10 else f"FILTERED SOURCES: {sources}")
            else:
                error_logger.warning("SOURCE FILTERING: Not available - using all sources")

            # Log job start with configuration
            error_logger.info(f"=== JOB START === | Job ID: {job_id} | Query: {query} | Sources: {sources} | Max per source: {max_per_source}")
            error_logger.info(f"LIMITS: Total file limit: {total_file_limit if total_file_limit > 0 else 'No limit'} | Total size limit: {total_size_limit if total_size_limit > 0 else 'No limit'} MB | Max per source: {max_per_source}")
            error_logger.info(f"CONTENT TYPES: Images: {content_types.get('images', True)} | Videos: {content_types.get('videos', True)}")
            error_logger.info(f"QUALITY: {quality_settings}")
            error_logger.info(f"CONFIG: MAX_CONCURRENT_SOURCES={max_concurrent}, SOURCE_TIMEOUT={source_timeout}s, GLOBAL_TIMEOUT={global_job_timeout}s")
            error_logger.info(f"CONFIG: REQUEST_TIMEOUT={config['REQUEST_TIMEOUT']}s, MAX_RETRIES_PER_SOURCE={config['MAX_RETRIES_PER_SOURCE']}")
            error_logger.info(f"CONFIG: MIN_DOWNLOAD_SPEED={config['MIN_DOWNLOAD_SPEED']} bytes/s, STALL_TIMEOUT={config['STALL_TIMEOUT']}s")
            error_logger.info(f"CONFIG: CIRCUIT_BREAKER_THRESHOLD={config['CIRCUIT_BREAKER_THRESHOLD']}, CIRCUIT_BREAKER_TIMEOUT={config['CIRCUIT_BREAKER_TIMEOUT']}s")

            # START PERFORMANCE TRACKING
            if PERFORMANCE_TRACKING_AVAILABLE:
                track_job_start(job_id, query, sources)

            # Initialize statistics
            total_downloaded = 0
            total_images = 0
            total_videos = 0
            total_size_downloaded = 0  # in bytes
            all_results = []
            source_stats = {}
            failed_sources = []
            successful_sources = []
            placeholders_filtered = 0
            sources_blacklisted_count = original_count - len(sources) if SOURCE_FILTER_AVAILABLE else 0

            # Process sources in parallel with timeout
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                # Submit all source processing tasks
                future_to_source = {
                    executor.submit(
                        process_single_source,
                        source,
                        query,
                        max_per_source,
                        safe_search,
                        output_dir,
                        user_id,
                        job_id,
                        source_timeout  # Pass timeout to each source processor
                    ): source
                    for source in sources
                }

                # CRITICAL FIX: Process completed sources with proper timeout handling
                completed_count = 0
                try:
                    # Calculate remaining time for the iterator
                    # If timeout is 0 (unlimited), use None for as_completed
                    timeout_for_iterator = None if global_job_timeout == 0 else global_job_timeout

                    for future in as_completed(future_to_source, timeout=timeout_for_iterator):
                        source = future_to_source[future]

                        # Check if we've exceeded the global timeout (only if timeout is set)
                        elapsed = time.time() - job_start_time
                        if global_job_timeout > 0 and elapsed > global_job_timeout:
                            error_logger.error(f"GLOBAL TIMEOUT: Job {job_id} exceeded {global_job_timeout}s")
                            raise TimeoutError(f"Job exceeded global timeout of {global_job_timeout}s")

                        try:
                            # CRITICAL FIX: Get result with timeout
                            remaining_timeout = max(1, source_timeout)
                            source_result = future.result(timeout=remaining_timeout)
                            completed_count += 1

                            error_logger.info(f"SOURCE COMPLETED: {source} | Downloaded: {source_result['downloaded']} | Time: {elapsed:.2f}s")

                            # APPLY IMAGE QUALITY FILTERING - Remove placeholder/dummy images
                            filtered_count_for_source = 0
                            if IMAGE_FILTER_AVAILABLE and source_result.get('files'):
                                original_file_count = len(source_result['files'])
                                source_result['files'] = filter_valid_images(source_result['files'], check_dimensions=False)
                                filtered_count_for_source = original_file_count - len(source_result['files'])

                                if filtered_count_for_source > 0:
                                    error_logger.info(f"IMAGE FILTERING: {source} | Removed {filtered_count_for_source} placeholder/low-quality images ({original_file_count} → {len(source_result['files'])})")
                                    placeholders_filtered += filtered_count_for_source
                                    # Update counts
                                    source_result['downloaded'] = len(source_result['files'])
                                    # Recount images and videos
                                    source_result['images'] = sum(1 for f in source_result['files'] if any(f.get('filepath', '').endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']))
                                    source_result['videos'] = sum(1 for f in source_result['files'] if any(f.get('filepath', '').endswith(ext) for ext in ['.mp4', '.webm']))

                            # TRACK PERFORMANCE for this source
                            if PERFORMANCE_TRACKING_AVAILABLE:
                                source_duration = source_result.get('duration', 0)
                                source_method = source_result.get('method', 'unknown')
                                source_success = source_result['downloaded'] > 0
                                source_error = source_result.get('error', None)
                                track_source_result(
                                    source, source_method, source_duration,
                                    source_result['downloaded'], source_result['images'], source_result['videos'],
                                    source_success, source_error
                                )

                            # Update statistics
                            with stats_lock:
                                total_downloaded += source_result['downloaded']
                                total_images += source_result['images']
                                total_videos += source_result['videos']
                                all_results.extend(source_result['files'])

                                source_stats[source] = {
                                    'downloaded': source_result['downloaded'],
                                    'images': source_result['images'],
                                    'videos': source_result['videos'],
                                    'success': source_result['success'],
                                    'error': source_result.get('error')
                                }

                                if source_result['success']:
                                    successful_sources.append(source)
                                else:
                                    failed_sources.append(source)

                            # Add files to database
                            for file_info in source_result['files']:
                                if file_info.get('filepath') and os.path.exists(file_info['filepath']):
                                    file_type = 'image'
                                    if any(file_info['filepath'].endswith(ext) for ext in ['.mp4', '.webm']):
                                        file_type = 'video'

                                    # Track file size
                                    try:
                                        file_size = os.path.getsize(file_info['filepath'])
                                        total_size_downloaded += file_size
                                    except Exception:
                                        file_size = 0

                                    get_asset_manager().add_asset(
                                        job_id=job_id,
                                        filepath=file_info['filepath'],
                                        file_type=file_type,
                                        metadata={
                                            'source': source,
                                            'original_url': file_info.get('original_url', ''),
                                            'query': query,
                                            'user_id': user_id,
                                            'downloaded_via': 'parallel_processor'
                                        }
                                    )

                            # Update job progress
                            # For infinite mode (no limits), don't show percentage - use -1 to indicate infinite
                            if total_file_limit == 0 and total_size_limit == 0:
                                progress = -1  # Infinite mode indicator
                                progress_msg = f'Downloading... | {total_downloaded} files | {completed_count}/{len(sources)} sources searched'
                            else:
                                # Calculate progress based on file limit if set
                                if total_file_limit > 0:
                                    progress = min(100, int((total_downloaded / total_file_limit) * 100))
                                else:
                                    # Based on sources completed
                                    progress = int((completed_count / len(sources)) * 100)
                                progress_msg = f'Processed {completed_count}/{len(sources)} sources | Downloaded: {total_downloaded}'

                            db_job_manager.update_job(
                                job_id,
                                status='running',
                                progress=progress,
                                message=progress_msg,
                                downloaded=total_downloaded,
                                images=total_images,
                                videos=total_videos
                            )

                            # Check if total file limit has been reached
                            if total_file_limit > 0 and total_downloaded >= total_file_limit:
                                error_logger.info(f"TOTAL FILE LIMIT REACHED: {total_downloaded}/{total_file_limit} files downloaded, stopping remaining sources")
                                # Cancel all remaining futures
                                for remaining_future in future_to_source:
                                    if not remaining_future.done():
                                        remaining_future.cancel()
                                break

                            # Check if total size limit has been reached
                            if total_size_limit > 0:
                                total_size_mb = total_size_downloaded / (1024 * 1024)  # Convert bytes to MB
                                if total_size_mb >= total_size_limit:
                                    error_logger.info(f"TOTAL SIZE LIMIT REACHED: {total_size_mb:.2f}/{total_size_limit} MB downloaded, stopping remaining sources")
                                    # Cancel all remaining futures
                                    for remaining_future in future_to_source:
                                        if not remaining_future.done():
                                            remaining_future.cancel()
                                    break

                        except TimeoutError as te:
                            error_logger.error(f"TIMEOUT: Source '{source}' exceeded {source_timeout}s timeout | {str(te)}")
                            completed_count += 1
                            failed_sources.append(source)
                            source_stats[source] = {
                                'downloaded': 0,
                                'success': False,
                                'error': f'Timeout after {source_timeout}s'
                            }
                        except Exception as e:
                            error_logger.error(f"EXCEPTION: Source '{source}' | {str(e)}")
                            completed_count += 1
                            failed_sources.append(source)
                            source_stats[source] = {
                                'downloaded': 0,
                                'success': False,
                                'error': str(e)
                            }

                except TimeoutError as global_timeout:
                    # Handle global timeout for as_completed iterator
                    error_logger.error(f"GLOBAL TIMEOUT: Job {job_id} iterator timeout | {str(global_timeout)}")
                    # Mark remaining sources as failed
                    for future, source in future_to_source.items():
                        if source not in source_stats:
                            failed_sources.append(source)
                            source_stats[source] = {
                                'downloaded': 0,
                                'success': False,
                                'error': 'Global job timeout'
                            }

            # Generate summary message
            summary_parts = []
            if successful_sources:
                summary_parts.append(f"Success: {', '.join(successful_sources)}")
            if failed_sources:
                summary_parts.append(f"Failed: {', '.join(failed_sources)}")
            summary = ' | '.join(summary_parts)

            # Get and log download statistics
            download_stats = media_downloader.get_statistics()
            circuit_status = media_downloader.get_circuit_breaker_status()

            # Log final statistics
            error_logger.info(f"=== JOB COMPLETE === | Job ID: {job_id} | Downloaded: {total_downloaded} | Images: {total_images} | Videos: {total_videos}")
            error_logger.info(f"STATISTICS | {summary}")
            error_logger.info(f"DOWNLOAD STATS | Attempts: {download_stats['total_attempts']}, Successes: {download_stats['total_successes']}, Failures: {download_stats['total_failures']}, Retries: {download_stats['total_retries']}")
            error_logger.info(f"DOWNLOAD STATS | Total Bytes: {download_stats['total_bytes']:,} ({download_stats['total_bytes']/1024/1024:.2f} MB)")

            # Log per-source statistics
            for source, stats in download_stats['source_stats'].items():
                cb_status = circuit_status.get(source, {})
                error_logger.info(f"SOURCE STATS | {source}: Attempts={stats['attempts']}, Success={stats['successes']}, Fail={stats['failures']}, Bytes={stats['bytes']:,}, Circuit={'OPEN' if cb_status.get('is_open') else 'CLOSED'}")

            # TRACK PERFORMANCE - Record filtering and finalize job
            if PERFORMANCE_TRACKING_AVAILABLE:
                track_filtering(placeholders_filtered, sources_blacklisted_count)
                track_job_end()

            # Update job as completed
            db_job_manager.update_job(
                job_id,
                status='completed',
                progress=100,
                message=f'Download completed! Got {total_downloaded} files ({total_images} images, {total_videos} videos) | {summary}',
                downloaded=total_downloaded,
                images=total_images,
                videos=total_videos,
                detected=total_downloaded,
                results={
                    'total_downloaded': total_downloaded,
                    'total_images': total_images,
                    'total_videos': total_videos,
                    'files': all_results,
                    'source_stats': source_stats,
                    'successful_sources': successful_sources,
                    'failed_sources': failed_sources
                }
            )

            # Clean up temporary files (.ytdl, .part, .tmp, etc.)
            cleanup_temp_files(output_dir)

            print(f"[DOWNLOAD] Job {job_id} completed: {total_downloaded} files downloaded")
            return {
                'success': True,
                'downloaded': total_downloaded,
                'images': total_images,
                'videos': total_videos,
                'source_stats': source_stats
            }

        except Exception as e:
            error_logger.error(f"JOB FAILED | Job ID: {job_id} | Error: {str(e)}")
            print(f"[DOWNLOAD] Job {job_id} failed: {e}")
            db_job_manager.update_job(
                job_id,
                status='error',
                message=f'Download failed: {str(e)}',
                progress=0
            )
            return {
                'success': False,
                'error': str(e)
            }

def comprehensive_multi_source_scrape(**kwargs):
    """
    Compatibility wrapper for existing code
    """
    query = kwargs.get('query', '')
    search_type = kwargs.get('search_type', 'comprehensive')
    enabled_sources = kwargs.get('enabled_sources', [])
    max_content_per_source = kwargs.get('max_content_per_source', 10)
    safe_search = kwargs.get('safe_search', True)
    job_id = kwargs.get('job_id')

    # Calculate total max content
    max_content = max_content_per_source * len(enabled_sources) if enabled_sources else max_content_per_source

    # Run the download job
    if job_id:
        result = run_download_job(
            job_id=job_id,
            query=query,
            sources=enabled_sources,
            max_content=max_content,
            safe_search=safe_search,
            user_id=None
        )

        return {
            'total_detected': result.get('downloaded', 0),
            'total_downloaded': result.get('downloaded', 0),
            'total_images': result.get('images', 0),
            'total_videos': result.get('videos', 0),
            'sources': {},
            'success': result.get('success', False)
        }
    else:
        # Direct call without job tracking
        return {
            'total_detected': 0,
            'total_downloaded': 0,
            'total_images': 0,
            'total_videos': 0,
            'sources': {},
            'success': False
        }

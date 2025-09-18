"""
Optimized downloader with parallel downloads, caching, and performance improvements
"""
import hashlib
import json
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from urllib.parse import urlparse

import requests
import urllib3

import db_asset_manager
import db_job_manager

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global cache for downloaded files
DOWNLOAD_CACHE = {}
CACHE_LOCK = Lock()
CACHE_FILE = "download_cache.json"

# Performance settings
MAX_WORKERS = 5  # Number of parallel downloads
CHUNK_SIZE = 8192  # Download chunk size
CONNECTION_TIMEOUT = 10
READ_TIMEOUT = 30
MAX_RETRIES = 3

def load_cache():
    """Load download cache from disk"""
    global DOWNLOAD_CACHE
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                DOWNLOAD_CACHE = json.load(f)
                print(f"[CACHE] Loaded {len(DOWNLOAD_CACHE)} cached entries")
        except Exception as e:
            print(f"[CACHE] Error loading cache: {e}")
            DOWNLOAD_CACHE = {}

def save_cache():
    """Save download cache to disk"""
    try:
        with CACHE_LOCK:
            with open(CACHE_FILE, 'w') as f:
                json.dump(DOWNLOAD_CACHE, f)
    except Exception as e:
        print(f"[CACHE] Error saving cache: {e}")

def get_url_hash(url):
    """Generate hash for URL for caching"""
    return hashlib.md5(url.encode()).hexdigest()

def download_file_optimized(url, output_dir, headers=None, use_cache=True):
    """Optimized file download with caching and better error handling"""
    url_hash = get_url_hash(url)

    # Check cache first
    if use_cache and url_hash in DOWNLOAD_CACHE:
        cached_path = DOWNLOAD_CACHE[url_hash]
        if os.path.exists(cached_path):
            print(f"[CACHE] Using cached file for {url}")
            # Copy to new location to simulate fresh download
            filename = os.path.basename(cached_path)
            new_path = os.path.join(output_dir, filename)
            if cached_path != new_path:
                import shutil
                shutil.copy2(cached_path, new_path)
                return new_path
            return cached_path

    # Handle file:// URLs
    if url.startswith('file://'):
        source_path = url.replace('file://', '')
        filename = os.path.basename(source_path)
        dest_path = os.path.join(output_dir, filename)

        import shutil
        shutil.copy2(source_path, dest_path)

        # Cache the result
        with CACHE_LOCK:
            DOWNLOAD_CACHE[url_hash] = dest_path

        return dest_path

    # Download with optimizations
    if not headers:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    for attempt in range(MAX_RETRIES):
        try:
            # Use session for connection pooling
            session = requests.Session()
            session.headers.update(headers)

            # Stream download for memory efficiency
            response = session.get(
                url,
                stream=True,
                timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT),
                verify=False
            )
            response.raise_for_status()

            # Generate filename
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path) or f"download_{uuid.uuid4().hex[:8]}"

            # Determine extension from content-type if needed
            if not any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm']):
                content_type = response.headers.get('content-type', '')
                ext_map = {
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'video/mp4': '.mp4',
                    'video/webm': '.webm'
                }
                for mime, ext in ext_map.items():
                    if mime in content_type:
                        filename += ext
                        break
                else:
                    filename += '.jpg'  # Default

            filepath = os.path.join(output_dir, filename)

            # Download in chunks
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

            # Cache the successful download
            with CACHE_LOCK:
                DOWNLOAD_CACHE[url_hash] = filepath

            print(f"[DOWNLOAD] Success: {filename} ({os.path.getsize(filepath)} bytes)")
            return filepath

        except Exception as e:
            print(f"[DOWNLOAD] Attempt {attempt + 1}/{MAX_RETRIES} failed for {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(1 * (attempt + 1))  # Exponential backoff
            else:
                return None

def download_batch(urls, output_dir, progress_callback=None):
    """Download multiple URLs in parallel"""
    results = []
    total = len(urls)
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all downloads
        future_to_url = {
            executor.submit(download_file_optimized, url, output_dir): url
            for url in urls
        }

        # Process completed downloads
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                filepath = future.result()
                completed += 1

                if filepath:
                    results.append({
                        'url': url,
                        'filepath': filepath,
                        'success': True
                    })
                else:
                    results.append({
                        'url': url,
                        'filepath': None,
                        'success': False
                    })

                # Update progress
                if progress_callback:
                    progress = int((completed / total) * 100)
                    progress_callback(
                        f"Downloaded {completed}/{total} files",
                        progress
                    )

            except Exception as e:
                print(f"[DOWNLOAD] Exception for {url}: {e}")
                results.append({
                    'url': url,
                    'filepath': None,
                    'success': False,
                    'error': str(e)
                })

    return results

def comprehensive_multi_source_scrape_optimized(query, search_type='comprehensive',
                                              enabled_sources=None, max_content_per_source=10,
                                              output_dir=None, progress_callback=None,
                                              safe_search=True, use_queue=False, job_id=None):
    """Optimized multi-source scraper with parallel downloads"""
    print(f"[SCRAPE] Starting optimized search for '{query}' with sources: {enabled_sources}")

    # Import the real scraper
    from scrapers.real_scraper import search_and_download
    
    # Create output directory
    if not output_dir:
        output_dir = os.path.join('downloads', f'{query.replace(" ", "_")}_{int(time.time())}')
    os.makedirs(output_dir, exist_ok=True)

    # Define progress callback wrapper
    def wrapped_progress_callback(message, progress, downloaded, images, videos):
        if progress_callback:
            progress_callback(message, progress, downloaded, images, videos, "")
        
        # Update job progress if job_id provided
        if job_id:
            db_job_manager.update_job(
                job_id,
                progress=progress,
                message=message,
                downloaded=downloaded,
                images=images,
                videos=videos
            )

    # Use real scraper to search and download
    results = search_and_download(
        query=query,
        sources=enabled_sources,
        max_per_source=max_content_per_source,
        output_dir=output_dir,
        safe_search=safe_search,
        progress_callback=wrapped_progress_callback
    )
    
    # Add to assets if job_id provided
    if job_id and results['total_downloaded'] > 0:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                filepath = os.path.join(root, file)
                metadata = {
                    'query': query,
                    'search_type': search_type,
                    'safe_search': safe_search
                }
                # Determine content type
                if any(file.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    content_type = 'image'
                elif any(file.endswith(ext) for ext in ['.mp4', '.webm']):
                    content_type = 'video'
                else:
                    content_type = 'unknown'
                
                db_asset_manager.add_asset(job_id, filepath, content_type, metadata)
    
    # Update job with final results
    if job_id:
        db_job_manager.update_job(
            job_id,
            status='completed',
            progress=100,
            message=f'Search completed successfully! Downloaded {results["total_downloaded"]} files',
            detected=results['total_detected'],
            downloaded=results['total_downloaded'],
            images=results['total_images'],
            videos=results['total_videos'],
            sources=results['sources'],
            results=results
        )

    print(f"[SCRAPE] Search complete. Downloaded {results['total_downloaded']} files")
    return results

# Make the optimized version the default
comprehensive_multi_source_scrape = comprehensive_multi_source_scrape_optimized

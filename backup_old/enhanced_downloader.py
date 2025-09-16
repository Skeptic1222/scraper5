#!/usr/bin/env python3
"""
Enhanced Content Downloader with Multi-threading Support
Optimized for faster downloads and better performance
"""

import asyncio
import aiohttp
import concurrent.futures
import threading
import queue
import time
import os
from typing import Dict, List, Callable, Optional, Tuple
from urllib.parse import urlparse
import logging
from dataclasses import dataclass
from collections import defaultdict
import yt_dlp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DownloadTask:
    """Represents a download task"""
    url: str
    source: str
    output_dir: str
    is_video: bool = False
    metadata: Dict = None

@dataclass
class DownloadResult:
    """Result of a download operation"""
    success: bool
    url: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None
    download_time: float = 0.0

class EnhancedDownloader:
    """Multi-threaded downloader for improved performance"""
    
    def __init__(self, thread_count: int = 4, max_concurrent_downloads: int = 10):
        self.thread_count = thread_count
        self.max_concurrent_downloads = max_concurrent_downloads
        self.download_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.active_downloads = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.progress_callback = None
        self.stats = defaultdict(lambda: {'downloaded': 0, 'failed': 0, 'total_size': 0})
        
    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.progress_callback = callback
        
    def start_workers(self):
        """Start worker threads"""
        self.workers = []
        for i in range(self.thread_count):
            worker = threading.Thread(target=self._worker, args=(i,), daemon=True)
            worker.start()
            self.workers.append(worker)
            
    def stop_workers(self):
        """Stop all worker threads"""
        self.stop_event.set()
        # Add sentinel values to wake up workers
        for _ in range(self.thread_count):
            self.download_queue.put(None)
            
    def _worker(self, worker_id: int):
        """Worker thread function"""
        logger.info(f"Worker {worker_id} started")
        
        while not self.stop_event.is_set():
            try:
                task = self.download_queue.get(timeout=1)
                if task is None:  # Sentinel value
                    break
                    
                with self.lock:
                    self.active_downloads += 1
                    
                # Download the file
                result = self._download_file(task)
                self.results_queue.put(result)
                
                # Update stats
                with self.lock:
                    self.active_downloads -= 1
                    if result.success:
                        self.stats[task.source]['downloaded'] += 1
                        if result.file_size:
                            self.stats[task.source]['total_size'] += result.file_size
                    else:
                        self.stats[task.source]['failed'] += 1
                        
                # Call progress callback
                if self.progress_callback:
                    self._report_progress(task, result)
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                
    def _download_file(self, task: DownloadTask) -> DownloadResult:
        """Download a single file"""
        start_time = time.time()
        
        try:
            if task.is_video:
                return self._download_video(task)
            else:
                return self._download_image(task)
        except Exception as e:
            logger.error(f"Download error for {task.url}: {e}")
            return DownloadResult(
                success=False,
                url=task.url,
                error=str(e),
                download_time=time.time() - start_time
            )
            
    def _download_image(self, task: DownloadTask) -> DownloadResult:
        """Download an image file synchronously"""
        import requests
        start_time = time.time()
        
        try:
            # Create output directory
            os.makedirs(task.output_dir, exist_ok=True)
            
            # Generate filename
            parsed_url = urlparse(task.url)
            filename = os.path.basename(parsed_url.path) or f"{task.source}_{int(time.time())}.jpg"
            filepath = os.path.join(task.output_dir, filename)
            
            # Download with timeout
            response = requests.get(task.url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Write to file
            total_size = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
                        
            return DownloadResult(
                success=True,
                url=task.url,
                file_path=filepath,
                file_size=total_size,
                download_time=time.time() - start_time
            )
            
        except Exception as e:
            return DownloadResult(
                success=False,
                url=task.url,
                error=str(e),
                download_time=time.time() - start_time
            )
            
    def _download_video(self, task: DownloadTask) -> DownloadResult:
        """Download a video file using yt-dlp"""
        start_time = time.time()
        
        try:
            # Create output directory
            os.makedirs(task.output_dir, exist_ok=True)
            
            # Configure yt-dlp
            ydl_opts = {
                'outtmpl': os.path.join(task.output_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'format': 'best[ext=mp4]/best',
                'concurrent_fragment_downloads': 4,
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(task.url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Get file size
                file_size = 0
                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    
            return DownloadResult(
                success=True,
                url=task.url,
                file_path=filename,
                file_size=file_size,
                download_time=time.time() - start_time
            )
            
        except Exception as e:
            return DownloadResult(
                success=False,
                url=task.url,
                error=str(e),
                download_time=time.time() - start_time
            )
            
    def _report_progress(self, task: DownloadTask, result: DownloadResult):
        """Report progress to callback"""
        if not self.progress_callback:
            return
            
        try:
            # Calculate overall stats
            total_downloaded = sum(s['downloaded'] for s in self.stats.values())
            total_failed = sum(s['failed'] for s in self.stats.values())
            total_size = sum(s['total_size'] for s in self.stats.values())
            
            # Prepare message
            if result.success:
                size_str = f" ({self._format_size(result.file_size)})" if result.file_size else ""
                message = f"✅ Downloaded: {os.path.basename(result.file_path or task.url)}{size_str}"
            else:
                message = f"❌ Failed: {task.url} - {result.error}"
                
            # Call callback
            self.progress_callback(
                message=message,
                progress=0,  # Will be calculated by caller
                downloaded=total_downloaded,
                images=total_downloaded,  # Simplified for now
                videos=0,
                current_file=result.file_path,
                file_size=result.file_size,
                download_speed=result.file_size / result.download_time if result.download_time > 0 else 0
            )
            
        except Exception as e:
            logger.error(f"Progress callback error: {e}")
            
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
        
    def download_batch(self, urls: List[Tuple[str, str, bool]], output_dir: str, 
                      progress_callback: Optional[Callable] = None) -> Dict:
        """Download a batch of URLs with multi-threading"""
        self.progress_callback = progress_callback
        self.stats.clear()
        
        # Start workers
        self.start_workers()
        
        try:
            # Add tasks to queue
            for url, source, is_video in urls:
                task = DownloadTask(
                    url=url,
                    source=source,
                    output_dir=os.path.join(output_dir, source),
                    is_video=is_video
                )
                self.download_queue.put(task)
                
            # Wait for all tasks to complete
            self.download_queue.join()
            
            # Collect results
            results = []
            while not self.results_queue.empty():
                results.append(self.results_queue.get())
                
            # Calculate final stats
            total_downloaded = sum(s['downloaded'] for s in self.stats.values())
            total_failed = sum(s['failed'] for s in self.stats.values())
            total_size = sum(s['total_size'] for s in self.stats.values())
            
            return {
                'success': True,
                'downloaded': total_downloaded,
                'failed': total_failed,
                'total_size': total_size,
                'stats_by_source': dict(self.stats),
                'results': results
            }
            
        finally:
            self.stop_workers()
            
    async def download_batch_async(self, urls: List[Tuple[str, str, bool]], output_dir: str, 
                                  progress_callback: Optional[Callable] = None) -> Dict:
        """Async wrapper for download_batch"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.download_batch, 
            urls, 
            output_dir, 
            progress_callback
        )

# Integration with existing real_content_downloader.py
def create_enhanced_downloader(thread_count: int = 4) -> EnhancedDownloader:
    """Factory function to create enhanced downloader"""
    return EnhancedDownloader(thread_count=thread_count)

# Utility function to prepare URLs for batch download
def prepare_download_urls(search_results: Dict) -> List[Tuple[str, str, bool]]:
    """Convert search results to download URLs format"""
    urls = []
    
    for source, items in search_results.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and 'url' in item:
                    is_video = item.get('type') == 'video' or 'youtube' in source.lower()
                    urls.append((item['url'], source, is_video))
                elif isinstance(item, str):
                    urls.append((item, source, False))
                    
    return urls 
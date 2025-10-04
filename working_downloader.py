"""
Working Downloader - Fallback implementation for content downloading
Provides compatibility with existing code expecting this module
"""
from enhanced_working_downloader import run_download_job, comprehensive_multi_source_scrape

# Export the same functions for compatibility
__all__ = ['run_download_job', 'comprehensive_multi_source_scrape']
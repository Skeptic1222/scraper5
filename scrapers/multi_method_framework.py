"""
Multi-Method Scraping Framework
Comprehensive, scalable system for trying multiple scraping methods per source with aggressive retry/fallback

Key Features:
- Pluggable scraping methods
- Automatic fallback on failure
- Success tracking and method prioritization
- Aggressive retry with exponential backoff
- Rate limiting and circuit breakers
- Persistent learning (remembers what works)
"""

import os
import time
import json
import logging
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import hashlib

# Configure logging
logger = logging.getLogger('multi_method_scraper')
logger.setLevel(logging.INFO)

class MethodType(Enum):
    """Types of scraping methods"""
    YT_DLP = "yt-dlp"
    SELENIUM = "selenium"
    REQUESTS_BS4 = "requests+beautifulsoup"
    PLAYWRIGHT = "playwright"
    API_DIRECT = "api_direct"
    CURL_CFFI = "curl_cffi"
    GALLERY_DL = "gallery-dl"
    WGET = "wget"
    ARIA2 = "aria2"
    CUSTOM = "custom"

@dataclass
class MethodResult:
    """Result from a scraping method attempt"""
    success: bool
    method: str
    files_downloaded: int
    files: List[Dict[str, Any]]
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0

@dataclass
class MethodStats:
    """Statistics for a scraping method"""
    method: str
    source: str
    total_attempts: int = 0
    total_successes: int = 0
    total_failures: int = 0
    total_files: int = 0
    avg_execution_time: float = 0.0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    success_rate: float = 0.0
    priority: int = 0  # Lower is better

class ScrapingMethod:
    """Base class for all scraping methods"""

    def __init__(self, name: str, method_type: MethodType, priority: int = 100):
        self.name = name
        self.method_type = method_type
        self.priority = priority
        self.enabled = True

    def can_handle(self, source: str, content_type: str) -> bool:
        """Check if this method can handle the given source/content type"""
        return True

    def execute(self, source: str, query: str, max_results: int, **kwargs) -> MethodResult:
        """Execute the scraping method - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement execute()")

    def __repr__(self):
        return f"<ScrapingMethod: {self.name} ({self.method_type.value}) priority={self.priority}>"

class MethodRegistry:
    """Registry for all available scraping methods"""

    def __init__(self):
        self.methods: Dict[str, ScrapingMethod] = {}
        self.stats_file = 'method_stats.json'
        self.stats: Dict[str, Dict[str, MethodStats]] = {}
        self._load_stats()

    def register(self, method: ScrapingMethod):
        """Register a new scraping method"""
        self.methods[method.name] = method
        logger.info(f"Registered method: {method.name} ({method.method_type.value})")

    def get_methods_for_source(self, source: str, content_type: str = 'any') -> List[ScrapingMethod]:
        """Get all methods that can handle this source, sorted by priority/success rate"""
        applicable = [m for m in self.methods.values()
                     if m.enabled and m.can_handle(source, content_type)]

        # Sort by success rate (if we have stats) then by priority
        def sort_key(method):
            source_stats = self.stats.get(source, {})
            method_stats = source_stats.get(method.name)
            if method_stats:
                # Prioritize methods with high success rate
                return (-method_stats.success_rate, method.priority)
            return (0, method.priority)  # No stats yet, use default priority

        return sorted(applicable, key=sort_key)

    def record_attempt(self, source: str, method: ScrapingMethod, result: MethodResult):
        """Record a method attempt for statistics"""
        if source not in self.stats:
            self.stats[source] = {}

        if method.name not in self.stats[source]:
            self.stats[source][method.name] = MethodStats(
                method=method.name,
                source=source
            )

        stats = self.stats[source][method.name]
        stats.total_attempts += 1

        if result.success:
            stats.total_successes += 1
            stats.total_files += result.files_downloaded
            stats.last_success = datetime.now().isoformat()
        else:
            stats.total_failures += 1
            stats.last_failure = datetime.now().isoformat()

        # Update success rate
        if stats.total_attempts > 0:
            stats.success_rate = stats.total_successes / stats.total_attempts

        # Update average execution time
        if stats.total_attempts == 1:
            stats.avg_execution_time = result.execution_time
        else:
            stats.avg_execution_time = (stats.avg_execution_time * (stats.total_attempts - 1) + result.execution_time) / stats.total_attempts

        self._save_stats()

    def _load_stats(self):
        """Load method statistics from disk"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    # Convert dict back to MethodStats objects
                    for source, methods in data.items():
                        self.stats[source] = {}
                        for method_name, stats_dict in methods.items():
                            self.stats[source][method_name] = MethodStats(**stats_dict)
                logger.info(f"Loaded stats for {len(self.stats)} sources")
            except Exception as e:
                logger.error(f"Failed to load stats: {e}")

    def _save_stats(self):
        """Save method statistics to disk"""
        try:
            # Convert MethodStats objects to dicts
            data = {}
            for source, methods in self.stats.items():
                data[source] = {}
                for method_name, stats in methods.items():
                    data[source][method_name] = asdict(stats)

            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

class RetryStrategy:
    """Aggressive retry strategy with exponential backoff"""

    def __init__(self, max_retries: int = 5, base_delay: float = 1.0, max_delay: float = 60.0, exponential: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number"""
        if self.exponential:
            delay = self.base_delay * (2 ** attempt)
        else:
            delay = self.base_delay * attempt

        return min(delay, self.max_delay)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if we should retry based on attempt count and error type"""
        if attempt >= self.max_retries:
            return False

        # Don't retry certain errors
        non_retryable = [
            'AuthenticationError',
            'PermissionError',
            'NotFoundError',
            '404',
        ]

        error_str = str(error)
        if any(err in error_str for err in non_retryable):
            return False

        return True

class MultiMethodScraper:
    """
    Main multi-method scraper that coordinates method selection and fallback
    """

    def __init__(self, output_dir: str = 'downloads'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.registry = MethodRegistry()
        self.retry_strategy = RetryStrategy(max_retries=5, base_delay=1.0)

        # Circuit breaker per source
        self.circuit_breakers: Dict[str, Dict] = {}

    def scrape(self, source: str, query: str, max_results: int = 25, content_type: str = 'any', **kwargs) -> Dict[str, Any]:
        """
        Scrape with automatic method selection and fallback

        Args:
            source: Source name (e.g., 'pornhub', 'imgur', 'reddit')
            query: Search query
            max_results: Maximum results to retrieve
            content_type: 'images', 'videos', or 'any'
            **kwargs: Additional parameters passed to methods

        Returns:
            Dict with success status, files, and metadata
        """
        logger.info(f"[{source}] Starting multi-method scrape for query: '{query}' (max: {max_results})")

        # Check circuit breaker
        if self._is_circuit_open(source):
            logger.warning(f"[{source}] Circuit breaker is OPEN - skipping")
            return {
                'success': False,
                'files': [],
                'error': 'Circuit breaker open',
                'source': source
            }

        # Get applicable methods sorted by priority/success rate
        methods = self.registry.get_methods_for_source(source, content_type)

        if not methods:
            logger.error(f"[{source}] No applicable methods found")
            return {
                'success': False,
                'files': [],
                'error': 'No applicable methods',
                'source': source
            }

        logger.info(f"[{source}] Found {len(methods)} applicable methods: {[m.name for m in methods]}")

        # Try each method in priority order
        all_files = []
        last_error = None

        for method_idx, method in enumerate(methods):
            logger.info(f"[{source}] Method {method_idx + 1}/{len(methods)}: {method.name} ({method.method_type.value})")

            # Try this method with aggressive retry
            result = self._execute_with_retry(source, query, max_results, method, **kwargs)

            # Record attempt for learning
            self.registry.record_attempt(source, method, result)

            if result.success and result.files_downloaded > 0:
                logger.info(f"[{source}] ✅ SUCCESS with {method.name}: {result.files_downloaded} files in {result.execution_time:.2f}s")
                all_files.extend(result.files)

                # Check if we have enough files
                if len(all_files) >= max_results:
                    logger.info(f"[{source}] Reached target ({len(all_files)}/{max_results}), stopping")
                    break
            else:
                logger.warning(f"[{source}] ❌ FAILED with {method.name}: {result.error}")
                last_error = result.error

                # Update circuit breaker
                self._record_failure(source)

        # Final result
        success = len(all_files) > 0

        if success:
            logger.info(f"[{source}] 🎉 COMPLETE: Downloaded {len(all_files)} files total")
            self._reset_circuit_breaker(source)
        else:
            logger.error(f"[{source}] 💀 ALL METHODS EXHAUSTED: 0 files downloaded")
            self._record_failure(source)

        return {
            'success': success,
            'files': all_files,
            'total_files': len(all_files),
            'error': last_error if not success else None,
            'source': source,
            'methods_tried': len(methods)
        }

    def _execute_with_retry(self, source: str, query: str, max_results: int, method: ScrapingMethod, **kwargs) -> MethodResult:
        """Execute a method with aggressive retry logic"""
        attempt = 0
        last_error = None

        while attempt < self.retry_strategy.max_retries:
            try:
                start_time = time.time()

                # Execute the method
                result = method.execute(source, query, max_results, output_dir=self.output_dir, **kwargs)

                result.execution_time = time.time() - start_time
                result.retry_count = attempt

                if result.success:
                    if attempt > 0:
                        logger.info(f"[{source}] {method.name} succeeded on retry {attempt}")
                    return result

                # Method returned failure - check if we should retry
                last_error = result.error

            except Exception as e:
                logger.warning(f"[{source}] {method.name} attempt {attempt + 1} raised exception: {e}")
                last_error = str(e)

            # Check if we should retry
            if attempt < self.retry_strategy.max_retries - 1:
                delay = self.retry_strategy.get_delay(attempt)
                logger.info(f"[{source}] {method.name} failed, retrying in {delay:.1f}s (attempt {attempt + 1}/{self.retry_strategy.max_retries})")
                time.sleep(delay)
                attempt += 1
            else:
                break

        # All retries exhausted
        logger.error(f"[{source}] {method.name} exhausted all {self.retry_strategy.max_retries} retries")
        return MethodResult(
            success=False,
            method=method.name,
            files_downloaded=0,
            files=[],
            error=last_error or "Max retries exceeded",
            retry_count=attempt
        )

    def _is_circuit_open(self, source: str) -> bool:
        """Check if circuit breaker is open for this source"""
        if source not in self.circuit_breakers:
            return False

        cb = self.circuit_breakers[source]

        # Check if circuit breaker timeout has passed
        if datetime.now() >= cb['open_until']:
            self._reset_circuit_breaker(source)
            return False

        return cb['is_open']

    def _record_failure(self, source: str):
        """Record a failure for circuit breaker"""
        if source not in self.circuit_breakers:
            self.circuit_breakers[source] = {
                'failures': 0,
                'is_open': False,
                'open_until': None
            }

        cb = self.circuit_breakers[source]
        cb['failures'] += 1

        # Open circuit after 3 consecutive failures
        if cb['failures'] >= 3:
            cb['is_open'] = True
            cb['open_until'] = datetime.now() + timedelta(minutes=5)
            logger.warning(f"[{source}] Circuit breaker OPENED (5 min cooldown)")

    def _reset_circuit_breaker(self, source: str):
        """Reset circuit breaker after success"""
        if source in self.circuit_breakers:
            self.circuit_breakers[source] = {
                'failures': 0,
                'is_open': False,
                'open_until': None
            }
            logger.info(f"[{source}] Circuit breaker RESET")

# Global registry instance
global_registry = MethodRegistry()

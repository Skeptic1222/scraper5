# Comprehensive Media Scraping Methodology

## Table of Contents
1. [Introduction](#introduction)
2. [Technical Considerations](#technical-considerations)
3. [Platform-Specific Implementations](#platform-specific-implementations)
4. [Method Fallback System](#method-fallback-system)
5. [Adding New Sources](#adding-new-sources)
6. [Configuration and Optimization](#configuration-and-optimization)

## Introduction

This document outlines the comprehensive methodology for scraping multimedia content from various platforms. Our system implements a sophisticated fallback mechanism that tries multiple extraction methods until one succeeds, while maintaining configuration for optimized performance once the best method is determined.

### Core Architecture

The scraper uses a modular architecture with:
- **Base Scraper Interface** (`src/scrapers/base.py`)
- **Individual Source Scrapers** (Reddit, YouTube, Instagram, Bing, Google, etc.)
- **Method Fallback System** (`src/services/method_fallback.py`)
- **Persistent Method Configuration** (learns and optimizes)

## Technical Considerations

### Platform Configuration
- **Platform APIs**: Use official APIs when available
- **Robots.txt**: Parse robots.txt for allowed paths
- **Rate Limiting**: Implement delays between requests
- **User-Agent**: Use descriptive User-Agent headers

### Content Access
- Access publicly available content
- Handle various content formats
- Manage authentication when required
- Implement data processing pipelines

### Technical Guidelines
1. **Efficiency**: Optimize request patterns
2. **Stability**: Don't overload servers
3. **Security**: Protect collected data
4. **Monitoring**: Track platform changes

## Platform-Specific Implementations

### Static vs Dynamic Pages

#### Static Pages
Pages where content is directly in HTML. Use:
- **Requests**: For HTTP requests
- **Beautiful Soup**: For HTML parsing
- **Direct extraction**: Parse `<img>`, `<video>` tags

#### Dynamic Pages
Pages rendered with JavaScript. Use:
- **Selenium**: Browser automation
- **Playwright**: Modern browser automation (our preference)
- **API endpoints**: Intercept XHR/Fetch requests

### Current Platform Support

| Platform | Scraper Class | Methods Available | Best Method |
|----------|--------------|-------------------|-------------|
| Reddit | `RedditScraper` | JSON API, OAuth, Direct Media | JSON API |
| YouTube | `YouTubeScraper` | yt-dlp, API emulation | yt-dlp |
| Instagram | `InstagramScraper` | GraphQL, API, Embed, Web Scrape | GraphQL |
| Bing Images | `BingScraper` | API, Web Scrape, Async API | API |
| Google Images | `GoogleScraper` | JSON extraction, Web Scrape, API emulation | JSON extraction |

### Platform-Specific Tools Integration

#### YouTube
- **Primary**: yt-dlp (most comprehensive)
- **Fallback**: pytube for lightweight operations
- **Features**: Quality selection, audio extraction, playlist support

#### Instagram
- **Primary**: GraphQL API extraction
- **Fallback**: Web scraping with session management
- **Features**: Stories, reels, IGTV, galleries

#### TikTok (To be implemented)
- **Primary**: Unofficial API wrapper
- **Fallback**: Web scraping
- **Features**: Videos, user feeds, hashtags

#### SoundCloud (To be implemented)
- **Primary**: scdl wrapper around yt-dlp
- **Features**: Tracks, playlists, likes, metadata

## Method Fallback System

### How It Works

```python
# Pseudocode for method fallback
for method in sorted_methods_by_priority:
    try:
        result = await method.execute(url)
        if result.success:
            save_successful_method(url, method)
            return result
    except:
        continue
return failure
```

### Method Priority System

Each scraper defines methods with priorities:

```python
class RedditScraper(BaseScraper):
    def _setup_methods(self):
        self.methods = [
            ScraperMethod(
                name="reddit_json_api",
                function=self._extract_via_json_api,
                priority=100  # Highest priority
            ),
            ScraperMethod(
                name="reddit_oauth_api",
                function=self._extract_via_oauth,
                priority=90,
                requires_auth=True
            ),
            ScraperMethod(
                name="reddit_direct_media",
                function=self._extract_direct_media,
                priority=80  # Lowest priority
            )
        ]
```

### Persistent Configuration

Once a method succeeds, it's saved for future use:

```python
# Configuration stored in database
{
    "source": "reddit",
    "url_pattern": "reddit.com/r/*/comments/*",
    "successful_method": "reddit_json_api",
    "success_rate": 0.95,
    "last_updated": "2025-01-01T00:00:00Z"
}
```

## Adding New Sources

### Step 1: Create Scraper Class

Create a new file in `src/scrapers/`:

```python
# src/scrapers/newsource.py
from .base import BaseScraper, MediaItem, MediaType, ScraperCategory

class NewSourceScraper(BaseScraper):
    NAME = "NewSource"
    CATEGORY = ScraperCategory.SOCIAL
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO]
    BASE_URL = "https://newsource.com"
    
    def _setup_methods(self):
        """Define extraction methods in priority order"""
        self.methods = [
            ScraperMethod(
                name="api_method",
                function=self._extract_via_api,
                priority=100
            ),
            ScraperMethod(
                name="web_scrape",
                function=self._extract_via_web,
                priority=90
            )
        ]
    
    async def search(self, query, max_results=20, safe_search=True, 
                    media_type=None, progress_callback=None):
        # Implement search logic
        pass
    
    async def download(self, url, output_path, quality="best", 
                      progress_callback=None):
        # Implement download logic
        pass
    
    def validate_url(self, url):
        return 'newsource.com' in url
```

### Step 2: Register the Scraper

Add to `src/scrapers/__init__.py`:

```python
from .newsource import NewSourceScraper

# In register_all_scrapers()
scrapers = [
    # ... existing scrapers
    NewSourceScraper
]
```

### Step 3: Define Extraction Methods

Implement multiple extraction methods:

```python
async def _extract_via_api(self, url):
    """Try API endpoint first"""
    # Implementation
    
async def _extract_via_web(self, url):
    """Fallback to web scraping"""
    # Implementation
    
async def _extract_via_browser(self, url):
    """Last resort: browser automation"""
    # Implementation
```

## Configuration and Optimization

### Method Configuration Storage

```python
# src/models/method_config.py
class MethodConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)
    url_pattern = db.Column(db.String(200))
    method_name = db.Column(db.String(50))
    success_count = db.Column(db.Integer, default=0)
    failure_count = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float)
    last_success = db.Column(db.DateTime)
    
    @property
    def success_rate(self):
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0
```

### Automatic Method Selection

```python
class SmartMethodSelector:
    def get_best_method(self, source, url):
        # Check if we have a known good method
        config = MethodConfig.query.filter_by(
            source=source,
            url_pattern=self._get_pattern(url)
        ).order_by(MethodConfig.success_rate.desc()).first()
        
        if config and config.success_rate > 0.8:
            return config.method_name
        
        # Otherwise, try all methods
        return None
```

### Safe Search Configuration

| Platform | Parameter | Values |
|----------|-----------|--------|
| Bing | `adlt` | off, moderate, strict |
| Google | `safe` | off, moderate, active |
| Yahoo | `vm` | r (strict), p (moderate), off |
| Reddit | `include_over_18` | true/false |

### Rate Limiting Configuration

```python
RATE_LIMITS = {
    'reddit': 60,      # requests per minute
    'youtube': 30,     # YouTube is stricter
    'instagram': 30,   # Instagram has strict limits
    'bing': 60,
    'google': 60
}
```

## Universal Fallback Methods

For unknown sites, the system uses these universal methods in order:

1. **yt-dlp**: Supports thousands of sites
2. **Direct HTTP**: For direct media URLs
3. **Browser Automation**: Using Playwright
4. **API Detection**: Find and use hidden APIs
5. **HTML Parsing**: Extract from page source

### Example: Unknown Site Handling

```python
async def handle_unknown_site(url, output_path):
    fallback = MethodFallbackSystem()
    
    # Try all universal methods
    result = await fallback.download(url, output_path)
    
    if result['success']:
        # Learn from success
        save_method_config(url, result['method'])
        return result
    
    # All methods failed
    return {'success': False, 'error': 'No suitable method found'}
```

## Testing New Sources

### Unit Tests

```python
# tests/test_newsource.py
import pytest
from src.scrapers.newsource import NewSourceScraper

@pytest.mark.asyncio
async def test_newsource_search():
    scraper = NewSourceScraper()
    results = await scraper.search("test query", max_results=5)
    assert len(results) <= 5
    assert all(r.source == "NewSource" for r in results)

@pytest.mark.asyncio
async def test_newsource_methods():
    scraper = NewSourceScraper()
    # Test each method individually
    for method in scraper.methods:
        # Test method
        pass
```

### Integration Tests

```python
@pytest.mark.integration
async def test_fallback_system():
    url = "https://example.com/media"
    result = await fallback_system.download(url, "test.mp4")
    assert result['success'] or result['error']
```

## Performance Optimization

### Caching Successful Methods

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_method(source, url_pattern):
    return MethodConfig.query.filter_by(
        source=source,
        url_pattern=url_pattern
    ).first()
```

### Parallel Method Attempts

```python
async def try_methods_parallel(methods, url, timeout=30):
    """Try multiple methods in parallel for faster results"""
    tasks = []
    for method in methods[:3]:  # Try top 3 in parallel
        task = asyncio.create_task(method.function(url))
        tasks.append(task)
    
    # Return first successful result
    done, pending = await asyncio.wait(
        tasks, 
        return_when=asyncio.FIRST_COMPLETED,
        timeout=timeout
    )
    
    # Cancel pending tasks
    for task in pending:
        task.cancel()
    
    # Return first successful result
    for task in done:
        if task.result():
            return task.result()
    
    return None
```

## Monitoring and Analytics

### Success Rate Tracking

```python
class MethodAnalytics:
    @staticmethod
    def track_attempt(source, method, success, response_time):
        config = MethodConfig.query.filter_by(
            source=source,
            method_name=method
        ).first()
        
        if success:
            config.success_count += 1
            config.last_success = datetime.utcnow()
        else:
            config.failure_count += 1
        
        # Update average response time
        config.avg_response_time = (
            (config.avg_response_time * (config.success_count - 1) + response_time) 
            / config.success_count
        )
        
        db.session.commit()
```

## Conclusion

This scraping methodology provides:
1. **Flexibility**: Multiple methods per source
2. **Intelligence**: Learns best methods over time
3. **Reliability**: Fallback ensures maximum success rate
4. **Extensibility**: Easy to add new sources
5. **Optimization**: Configurable for performance
6. **Compatibility**: Respects platform configurations

The system automatically adapts to changes in source websites while maintaining high success rates through intelligent method selection and fallback mechanisms.
"""
Scraper modules initialization and registration
"""
import logging
from typing import Dict, List, Type

from .base import BaseScraper, MediaItem, MediaType, ScraperCategory
from .bing import BingScraper
from .google import GoogleScraper
from .instagram import InstagramScraper
from .reddit import RedditScraper
from .youtube import YouTubeScraper

# Import new scraper collections
try:
    from .video_sites import VIDEO_SCRAPERS
except ImportError:
    VIDEO_SCRAPERS = []

try:
    from .image_sites import IMAGE_SCRAPERS
except ImportError:
    IMAGE_SCRAPERS = []

try:
    from .search_engines import SEARCH_ENGINE_SCRAPERS
except ImportError:
    SEARCH_ENGINE_SCRAPERS = []

try:
    from .social_media import SOCIAL_MEDIA_SCRAPERS
except ImportError:
    SOCIAL_MEDIA_SCRAPERS = []

try:
    from .adult_sites import ADULT_SCRAPERS
except ImportError:
    ADULT_SCRAPERS = []

logger = logging.getLogger(__name__)


class ScraperRegistry:
    """Central registry for all scrapers"""

    def __init__(self):
        self._scrapers: Dict[str, Type[BaseScraper]] = {}
        self._categories: Dict[str, List[str]] = {}
        self._instances: Dict[str, BaseScraper] = {}

    def register(self, scraper_class: Type[BaseScraper]):
        """Register a new scraper class"""
        name = scraper_class.NAME.lower()
        category = scraper_class.CATEGORY.value

        self._scrapers[name] = scraper_class

        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)

        logger.info(f"Registered scraper: {name} ({category})")

    def get_scraper(self, name: str) -> BaseScraper:
        """Get scraper instance by name (cached)"""
        name_lower = name.lower()

        # Return cached instance if exists
        if name_lower in self._instances:
            return self._instances[name_lower]

        # Create new instance
        scraper_class = self._scrapers.get(name_lower)
        if not scraper_class:
            raise ValueError(f"Unknown scraper: {name}")

        instance = scraper_class()
        self._instances[name_lower] = instance
        return instance

    def list_scrapers(self, category: str = None,
                     safe_only: bool = False) -> List[Dict[str, any]]:
        """List available scrapers with details"""
        scrapers = []

        if category:
            names = self._categories.get(category, [])
        else:
            names = list(self._scrapers.keys())

        for name in names:
            scraper_class = self._scrapers[name]

            if safe_only and scraper_class.NSFW:
                continue

            scrapers.append({
                'name': scraper_class.NAME,
                'id': name,
                'category': scraper_class.CATEGORY.value,
                'supported_media': [mt.value for mt in scraper_class.SUPPORTED_MEDIA_TYPES],
                'requires_auth': scraper_class.REQUIRES_AUTH,
                'nsfw': scraper_class.NSFW,
                'rate_limit': scraper_class.RATE_LIMIT
            })

        return scrapers

    def get_categories(self) -> Dict[str, List[str]]:
        """Get all categories with their scrapers"""
        return self._categories.copy()

    def search_all(self, query: str, sources: List[str] = None,
                  max_results_per_source: int = 10) -> Dict[str, List[MediaItem]]:
        """Search across multiple sources"""
        results = {}

        if sources is None:
            sources = list(self._scrapers.keys())

        for source in sources:
            try:
                scraper = self.get_scraper(source)
                items = scraper.search(query, max_results_per_source)
                results[source] = items
            except Exception as e:
                logger.error(f"Search failed for {source}: {e}")
                results[source] = []

        return results


# Global registry instance
registry = ScraperRegistry()

# Register all available scrapers
def register_all_scrapers():
    """Register all implemented scrapers"""
    # Individual scrapers (legacy)
    individual_scrapers = [
        RedditScraper,
        YouTubeScraper,
        InstagramScraper,
        BingScraper,
        GoogleScraper
    ]

    # Combine all scraper collections
    all_scrapers = (
        individual_scrapers +
        VIDEO_SCRAPERS +
        IMAGE_SCRAPERS +
        SEARCH_ENGINE_SCRAPERS +
        SOCIAL_MEDIA_SCRAPERS +
        ADULT_SCRAPERS
    )

    # Track registered names to avoid duplicates
    registered_names = set()

    for scraper_class in all_scrapers:
        try:
            name = scraper_class.NAME.lower()
            # Skip duplicates
            if name not in registered_names:
                registry.register(scraper_class)
                registered_names.add(name)
        except Exception as e:
            logger.error(f"Failed to register {scraper_class.__name__}: {e}")

# Auto-register on import
register_all_scrapers()

# Export commonly used items
__all__ = [
    'BaseScraper',
    'MediaItem',
    'MediaType',
    'ScraperCategory',
    'ScraperRegistry',
    'registry',
    'RedditScraper',
    'YouTubeScraper',
    'InstagramScraper',
    'BingScraper',
    'GoogleScraper'
]

"""
Base Scraper Interface - Foundation for all content scrapers
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class MediaType(Enum):
    """Supported media types"""
    IMAGE = "image"
    VIDEO = "video"
    STREAM = "stream"
    AUDIO = "audio"
    ANIMATION = "animation"
    GIF = "gif"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class ScraperCategory(Enum):
    """Scraper categories"""
    SOCIAL = "social"
    SEARCH = "search"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    ART = "art"
    ADULT = "adult"


@dataclass
class MediaItem:
    """Standardized media item representation"""
    url: str
    title: str
    media_type: MediaType
    source: str
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    duration: Optional[int] = None  # seconds for video/audio
    resolution: Optional[str] = None  # e.g., "1920x1080"
    file_size: Optional[int] = None  # bytes
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'url': self.url,
            'title': self.title,
            'media_type': self.media_type.value,
            'source': self.source,
            'thumbnail': self.thumbnail,
            'description': self.description,
            'author': self.author,
            'duration': self.duration,
            'resolution': self.resolution,
            'file_size': self.file_size,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class ScraperMethod:
    """Represents a scraping method that can be tried"""
    name: str
    function: Callable
    priority: int = 0  # Higher priority tried first
    supports_batch: bool = False
    requires_auth: bool = False
    rate_limit: Optional[int] = None  # requests per minute

    def __lt__(self, other):
        return self.priority > other.priority  # Higher priority first


class BaseScraper(ABC):
    """Abstract base class for all content scrapers"""

    # Class attributes to be overridden by subclasses
    NAME: str = ""
    CATEGORY: ScraperCategory = ScraperCategory.SEARCH
    SUPPORTED_MEDIA_TYPES: List[MediaType] = []
    REQUIRES_AUTH: bool = False
    NSFW: bool = False
    BASE_URL: Optional[str] = None
    RATE_LIMIT: int = 60  # requests per minute

    def __init__(self):
        """Initialize the scraper"""
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.methods: List[ScraperMethod] = []
        self._setup_methods()

    @abstractmethod
    def _setup_methods(self):
        """Setup available scraping methods for this source"""
        pass

    @abstractmethod
    async def search(self, query: str, max_results: int = 20,
                    safe_search: bool = True, media_type: Optional[MediaType] = None,
                    progress_callback: Optional[Callable] = None) -> List[MediaItem]:
        """
        Search for content
        
        Args:
            query: Search query
            max_results: Maximum number of results
            safe_search: Filter NSFW content
            media_type: Filter by specific media type
            progress_callback: Callback for progress updates
            
        Returns:
            List of MediaItem objects
        """
        pass

    @abstractmethod
    async def download(self, url: str, output_path: str,
                      quality: str = "best",
                      progress_callback: Optional[Callable] = None) -> bool:
        """
        Download media from URL
        
        Args:
            url: Media URL
            output_path: Where to save the file
            quality: Download quality (best, high, medium, low)
            progress_callback: Callback for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Check if URL belongs to this source"""
        pass

    async def extract_media_info(self, url: str) -> Optional[MediaItem]:
        """
        Extract media information from URL
        
        Args:
            url: Media URL
            
        Returns:
            MediaItem with extracted information or None
        """
        if not self.validate_url(url):
            return None

        # Try each method in priority order
        for method in sorted(self.methods):
            try:
                logger.info(f"Trying method {method.name} for {url}")
                result = await method.function(url)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Method {method.name} failed: {e}")
                continue

        return None

    def get_supported_formats(self) -> List[str]:
        """Get list of supported download formats"""
        return ["mp4", "webm", "mp3", "jpg", "png", "gif"]

    def supports_media_type(self, media_type: MediaType) -> bool:
        """Check if scraper supports specific media type"""
        return media_type in self.SUPPORTED_MEDIA_TYPES

    async def test_connection(self) -> bool:
        """Test if the source is accessible"""
        # Override in subclasses for specific tests
        return True

    def __str__(self):
        return f"{self.NAME} Scraper ({self.CATEGORY.value})"

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.NAME}, category={self.CATEGORY.value})>"

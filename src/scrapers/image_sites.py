"""
Image sharing and search platform scrapers
Supports major image platforms with multiple extraction methods
"""
from .base import BaseScraper, MediaType, ScraperCategory, ScraperMethod


class GoogleImagesScraper(BaseScraper):
    """Google Images scraper"""
    NAME = "Google Images"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://images.google.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("google_json_api", self._extract_via_json_api, 100),
            ScraperMethod("google_web_scrape", self._extract_via_web, 90),
            ScraperMethod("google_api", self._extract_via_api, 80)
        ]

class BingImagesScraper(BaseScraper):
    """Bing Images scraper"""
    NAME = "Bing Images"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://www.bing.com/images"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("bing_api", self._extract_via_api, 100),
            ScraperMethod("bing_web", self._extract_via_web, 90),
            ScraperMethod("bing_async", self._extract_async, 80)
        ]

class DuckDuckGoImagesScraper(BaseScraper):
    """DuckDuckGo Images scraper"""
    NAME = "DuckDuckGo Images"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://duckduckgo.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("ddg_api", self._extract_via_api, 100),
            ScraperMethod("ddg_web", self._extract_via_web, 90)
        ]

class YahooImagesScraper(BaseScraper):
    """Yahoo Images scraper"""
    NAME = "Yahoo Images"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://www.yahoo.com/images"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("yahoo_api", self._extract_via_api, 100),
            ScraperMethod("yahoo_web", self._extract_via_web, 90)
        ]

class YandexImagesScraper(BaseScraper):
    """Yandex Images scraper"""
    NAME = "Yandex Images"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://yandex.com/images"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("yandex_api", self._extract_via_api, 100),
            ScraperMethod("yandex_web", self._extract_via_web, 90)
        ]

class ImgurScraper(BaseScraper):
    """Imgur image/gallery scraper"""
    NAME = "Imgur"
    CATEGORY = ScraperCategory.IMAGE
    BASE_URL = "https://imgur.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.GIF]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("imgur_api", self._extract_via_api, 100),
            ScraperMethod("imgur_direct", self._extract_direct, 90),
            ScraperMethod("imgur_gallery", self._extract_gallery, 80)
        ]

class FlickrScraper(BaseScraper):
    """Flickr photo scraper"""
    NAME = "Flickr"
    CATEGORY = ScraperCategory.IMAGE
    BASE_URL = "https://flickr.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("flickr_api", self._extract_via_api, 100),
            ScraperMethod("flickr_web", self._extract_via_web, 90)
        ]

class UnsplashScraper(BaseScraper):
    """Unsplash photo scraper"""
    NAME = "Unsplash"
    CATEGORY = ScraperCategory.IMAGE
    BASE_URL = "https://unsplash.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("unsplash_api", self._extract_via_api, 100),
            ScraperMethod("unsplash_download", self._extract_download_url, 90)
        ]

class PixabayScraper(BaseScraper):
    """Pixabay image scraper"""
    NAME = "Pixabay"
    CATEGORY = ScraperCategory.IMAGE
    BASE_URL = "https://pixabay.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("pixabay_api", self._extract_via_api, 100),
            ScraperMethod("pixabay_web", self._extract_via_web, 90)
        ]

class PexelsScraper(BaseScraper):
    """Pexels photo/video scraper"""
    NAME = "Pexels"
    CATEGORY = ScraperCategory.IMAGE
    BASE_URL = "https://www.pexels.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("pexels_api", self._extract_via_api, 100),
            ScraperMethod("pexels_web", self._extract_via_web, 90)
        ]

class DeviantArtScraper(BaseScraper):
    """DeviantArt artwork scraper"""
    NAME = "DeviantArt"
    CATEGORY = ScraperCategory.ART
    BASE_URL = "https://www.deviantart.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("deviantart_api", self._extract_via_api, 100),
            ScraperMethod("deviantart_web", self._extract_via_web, 90),
            ScraperMethod("deviantart_gallery", self._extract_gallery, 80)
        ]

class GiphyScraper(BaseScraper):
    """Giphy GIF scraper"""
    NAME = "Giphy"
    CATEGORY = ScraperCategory.IMAGE
    BASE_URL = "https://giphy.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.GIF]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("giphy_api", self._extract_via_api, 100),
            ScraperMethod("giphy_web", self._extract_via_web, 90)
        ]

class FiveHundredPXScraper(BaseScraper):
    """500px photo scraper"""
    NAME = "500px"
    CATEGORY = ScraperCategory.IMAGE
    BASE_URL = "https://500px.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("500px_api", self._extract_via_api, 100),
            ScraperMethod("500px_web", self._extract_via_web, 90)
        ]

# Export all image scrapers
IMAGE_SCRAPERS = [
    GoogleImagesScraper,
    BingImagesScraper,
    DuckDuckGoImagesScraper,
    YahooImagesScraper,
    YandexImagesScraper,
    ImgurScraper,
    FlickrScraper,
    UnsplashScraper,
    PixabayScraper,
    PexelsScraper,
    DeviantArtScraper,
    GiphyScraper,
    FiveHundredPXScraper
]

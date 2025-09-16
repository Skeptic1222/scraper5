"""
General search engine scrapers
Supports major search engines for content discovery
"""
from .base import BaseScraper, MediaType, ScraperCategory, ScraperMethod


class GoogleSearchScraper(BaseScraper):
    """Google Search scraper"""
    NAME = "Google Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://www.google.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("google_api", self._extract_via_api, 100),
            ScraperMethod("google_web", self._extract_via_web, 90),
            ScraperMethod("google_ajax", self._extract_via_ajax, 80)
        ]

class BingSearchScraper(BaseScraper):
    """Bing Search scraper"""
    NAME = "Bing Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://www.bing.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("bing_api", self._extract_via_api, 100),
            ScraperMethod("bing_web", self._extract_via_web, 90)
        ]

class DuckDuckGoSearchScraper(BaseScraper):
    """DuckDuckGo Search scraper"""
    NAME = "DuckDuckGo Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://duckduckgo.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("ddg_api", self._extract_via_api, 100),
            ScraperMethod("ddg_web", self._extract_via_web, 90),
            ScraperMethod("ddg_instant", self._extract_instant_answer, 80)
        ]

class YahooSearchScraper(BaseScraper):
    """Yahoo Search scraper"""
    NAME = "Yahoo Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://search.yahoo.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("yahoo_api", self._extract_via_api, 100),
            ScraperMethod("yahoo_web", self._extract_via_web, 90)
        ]

class YandexSearchScraper(BaseScraper):
    """Yandex Search scraper"""
    NAME = "Yandex Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://yandex.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("yandex_api", self._extract_via_api, 100),
            ScraperMethod("yandex_web", self._extract_via_web, 90)
        ]

class BaiduSearchScraper(BaseScraper):
    """Baidu Search scraper"""
    NAME = "Baidu Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://www.baidu.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("baidu_api", self._extract_via_api, 100),
            ScraperMethod("baidu_web", self._extract_via_web, 90)
        ]

class AskSearchScraper(BaseScraper):
    """Ask.com Search scraper"""
    NAME = "Ask Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://www.ask.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("ask_web", self._extract_via_web, 100),
            ScraperMethod("ask_api", self._extract_via_api, 90)
        ]

class StartpageSearchScraper(BaseScraper):
    """Startpage Search scraper"""
    NAME = "Startpage Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://www.startpage.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("startpage_web", self._extract_via_web, 100),
            ScraperMethod("startpage_api", self._extract_via_api, 90)
        ]

class QwantSearchScraper(BaseScraper):
    """Qwant Search scraper"""
    NAME = "Qwant Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://www.qwant.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("qwant_api", self._extract_via_api, 100),
            ScraperMethod("qwant_web", self._extract_via_web, 90)
        ]

class NaverSearchScraper(BaseScraper):
    """Naver Search scraper"""
    NAME = "Naver Search"
    CATEGORY = ScraperCategory.SEARCH
    BASE_URL = "https://naver.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.DOCUMENT]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("naver_api", self._extract_via_api, 100),
            ScraperMethod("naver_web", self._extract_via_web, 90)
        ]

# Export all search engine scrapers
SEARCH_ENGINE_SCRAPERS = [
    GoogleSearchScraper,
    BingSearchScraper,
    DuckDuckGoSearchScraper,
    YahooSearchScraper,
    YandexSearchScraper,
    BaiduSearchScraper,
    AskSearchScraper,
    StartpageSearchScraper,
    QwantSearchScraper,
    NaverSearchScraper
]

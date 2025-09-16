"""
Social media platform scrapers
Supports major social networks with various extraction methods
"""
from .base import BaseScraper, MediaType, ScraperCategory, ScraperMethod


class InstagramScraper(BaseScraper):
    """Instagram media scraper"""
    NAME = "Instagram"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.instagram.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("instagram_graphql", self._extract_via_graphql, 100),
            ScraperMethod("instagram_api", self._extract_via_api, 90),
            ScraperMethod("instagram_embed", self._extract_via_embed, 80),
            ScraperMethod("instagram_web", self._extract_via_web, 70)
        ]

class TwitterScraper(BaseScraper):
    """Twitter/X media scraper"""
    NAME = "Twitter"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://twitter.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.GIF]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("twitter_api", self._extract_via_api, 100),
            ScraperMethod("twitter_web", self._extract_via_web, 90),
            ScraperMethod("twitter_graphql", self._extract_via_graphql, 80)
        ]

class FacebookScraper(BaseScraper):
    """Facebook media scraper"""
    NAME = "Facebook"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.facebook.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("facebook_api", self._extract_via_api, 100),
            ScraperMethod("facebook_web", self._extract_via_web, 90),
            ScraperMethod("facebook_mobile", self._extract_via_mobile, 80)
        ]

class RedditScraper(BaseScraper):
    """Reddit media scraper"""
    NAME = "Reddit"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.reddit.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.GIF]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("reddit_json", self._extract_via_json_api, 100),
            ScraperMethod("reddit_oauth", self._extract_via_oauth, 90),
            ScraperMethod("reddit_direct", self._extract_direct_media, 80)
        ]

class PinterestScraper(BaseScraper):
    """Pinterest media scraper"""
    NAME = "Pinterest"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.pinterest.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.GIF]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("pinterest_api", self._extract_via_api, 100),
            ScraperMethod("pinterest_web", self._extract_via_web, 90),
            ScraperMethod("pinterest_ajax", self._extract_via_ajax, 80)
        ]

class TumblrScraper(BaseScraper):
    """Tumblr media scraper"""
    NAME = "Tumblr"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.tumblr.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.GIF]
    NSFW = True  # Tumblr has NSFW content

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("tumblr_api", self._extract_via_api, 100),
            ScraperMethod("tumblr_web", self._extract_via_web, 90),
            ScraperMethod("tumblr_blog", self._extract_blog_content, 80)
        ]

class LinkedInScraper(BaseScraper):
    """LinkedIn media scraper"""
    NAME = "LinkedIn"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.linkedin.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO]
    REQUIRES_AUTH = True

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("linkedin_api", self._extract_via_api, 100),
            ScraperMethod("linkedin_web", self._extract_via_web, 90)
        ]

class SnapchatScraper(BaseScraper):
    """Snapchat media scraper"""
    NAME = "Snapchat"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.snapchat.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("snapchat_api", self._extract_via_api, 100),
            ScraperMethod("snapchat_web", self._extract_via_web, 90)
        ]

class VKScraper(BaseScraper):
    """VK (VKontakte) media scraper"""
    NAME = "VK"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://vk.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.AUDIO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("vk_api", self._extract_via_api, 100),
            ScraperMethod("vk_web", self._extract_via_web, 90),
            ScraperMethod("vk_mobile", self._extract_via_mobile, 80)
        ]

class WeiboScraper(BaseScraper):
    """Weibo media scraper"""
    NAME = "Weibo"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.weibo.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("weibo_api", self._extract_via_api, 100),
            ScraperMethod("weibo_web", self._extract_via_web, 90),
            ScraperMethod("weibo_mobile", self._extract_via_mobile, 80)
        ]

# Export all social media scrapers
SOCIAL_MEDIA_SCRAPERS = [
    InstagramScraper,
    TwitterScraper,
    FacebookScraper,
    RedditScraper,
    PinterestScraper,
    TumblrScraper,
    LinkedInScraper,
    SnapchatScraper,
    VKScraper,
    WeiboScraper
]

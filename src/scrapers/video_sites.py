"""
Video hosting platform scrapers
Supports major video platforms with fallback methods
"""
from .base import BaseScraper, MediaType, ScraperCategory, ScraperMethod


class YouTubeScraper(BaseScraper):
    """YouTube video scraper"""
    NAME = "YouTube"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://www.youtube.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO, MediaType.AUDIO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("ytdlp_best", self._download_with_ytdlp, 100),
            ScraperMethod("youtube_api", self._extract_via_api, 90),
            ScraperMethod("youtube_embed", self._extract_via_embed, 80)
        ]

    async def _download_with_ytdlp(self, url: str, **kwargs):
        """Primary method using yt-dlp"""
        return await self._ytdlp_download(url, **kwargs)

    async def _extract_via_api(self, url: str, **kwargs):
        """Extract using YouTube API"""
        # Implementation for YouTube API
        pass

    async def _extract_via_embed(self, url: str, **kwargs):
        """Extract using embed API"""
        # Implementation for embed extraction
        pass

class VimeoScraper(BaseScraper):
    """Vimeo video scraper"""
    NAME = "Vimeo"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://vimeo.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("vimeo_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("vimeo_api", self._extract_via_api, 90)
        ]

class DailymotionScraper(BaseScraper):
    """Dailymotion video scraper"""
    NAME = "Dailymotion"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://www.dailymotion.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("dailymotion_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("dailymotion_api", self._extract_via_api, 90)
        ]

class TwitchScraper(BaseScraper):
    """Twitch video/stream scraper"""
    NAME = "Twitch"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://www.twitch.tv"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO, MediaType.STREAM]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("twitch_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("twitch_api", self._extract_via_api, 90),
            ScraperMethod("twitch_hls", self._extract_hls_stream, 80)
        ]

class TikTokScraper(BaseScraper):
    """TikTok video scraper"""
    NAME = "TikTok"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.tiktok.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("tiktok_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("tiktok_api", self._extract_via_api, 90),
            ScraperMethod("tiktok_web", self._extract_via_web, 80)
        ]

class FacebookWatchScraper(BaseScraper):
    """Facebook Watch video scraper"""
    NAME = "Facebook Watch"
    CATEGORY = ScraperCategory.SOCIAL
    BASE_URL = "https://www.facebook.com/watch"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("facebook_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("facebook_api", self._extract_via_api, 90)
        ]

class MetacafeScraper(BaseScraper):
    """Metacafe video scraper"""
    NAME = "Metacafe"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://www.metacafe.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("metacafe_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("metacafe_direct", self._extract_direct, 90)
        ]

class VeohScraper(BaseScraper):
    """Veoh video scraper"""
    NAME = "Veoh"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://www.veoh.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("veoh_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("veoh_api", self._extract_via_api, 90)
        ]

class BitchuteScraper(BaseScraper):
    """Bitchute video scraper"""
    NAME = "Bitchute"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://www.bitchute.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("bitchute_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("bitchute_direct", self._extract_direct, 90)
        ]

class BilibiliScraper(BaseScraper):
    """Bilibili video scraper"""
    NAME = "Bilibili"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://bilibili.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("bilibili_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("bilibili_api", self._extract_via_api, 90)
        ]

class NewgroundsScraper(BaseScraper):
    """Newgrounds video/animation scraper"""
    NAME = "Newgrounds"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://www.newgrounds.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO, MediaType.ANIMATION]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("newgrounds_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("newgrounds_api", self._extract_via_api, 90)
        ]

class NineGagTVScraper(BaseScraper):
    """9GAG TV video scraper"""
    NAME = "9GAG TV"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://www.9gag.com/tv"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("9gag_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("9gag_api", self._extract_via_api, 90)
        ]

class LiveLeakScraper(BaseScraper):
    """LiveLeak video scraper"""
    NAME = "LiveLeak"
    CATEGORY = ScraperCategory.VIDEO
    BASE_URL = "https://www.liveleak.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("liveleak_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("liveleak_direct", self._extract_direct, 90)
        ]

# Export all video scrapers
VIDEO_SCRAPERS = [
    YouTubeScraper,
    VimeoScraper,
    DailymotionScraper,
    TwitchScraper,
    TikTokScraper,
    FacebookWatchScraper,
    MetacafeScraper,
    VeohScraper,
    BitchuteScraper,
    BilibiliScraper,
    NewgroundsScraper,
    NineGagTVScraper,
    LiveLeakScraper
]

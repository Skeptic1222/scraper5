"""
Adult content platform scrapers
NSFW content - requires age verification and appropriate access controls
"""
from .base import BaseScraper, MediaType, ScraperCategory, ScraperMethod


# Base class for all adult scrapers
class AdultScraper(BaseScraper):
    """Base class for adult content scrapers"""
    CATEGORY = ScraperCategory.ADULT
    NSFW = True
    REQUIRES_AGE_VERIFICATION = True
    MIN_AGE = 18

class PornhubScraper(AdultScraper):
    """Pornhub video scraper"""
    NAME = "Pornhub"
    BASE_URL = "https://www.pornhub.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("pornhub_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("pornhub_api", self._extract_via_api, 90),
            ScraperMethod("pornhub_hls", self._extract_hls_stream, 80)
        ]

class XVideosScraper(AdultScraper):
    """XVideos video scraper"""
    NAME = "XVideos"
    BASE_URL = "https://www.xvideos.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("xvideos_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("xvideos_api", self._extract_via_api, 90),
            ScraperMethod("xvideos_direct", self._extract_direct, 80)
        ]

class XHamsterScraper(AdultScraper):
    """XHamster video scraper"""
    NAME = "XHamster"
    BASE_URL = "https://xhamster.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("xhamster_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("xhamster_api", self._extract_via_api, 90),
            ScraperMethod("xhamster_web", self._extract_via_web, 80)
        ]

class XNXXScraper(AdultScraper):
    """XNXX video scraper"""
    NAME = "XNXX"
    BASE_URL = "https://www.xnxx.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("xnxx_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("xnxx_api", self._extract_via_api, 90)
        ]

class SpankBangScraper(AdultScraper):
    """SpankBang video scraper"""
    NAME = "SpankBang"
    BASE_URL = "https://www.spankbang.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("spankbang_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("spankbang_api", self._extract_via_api, 90)
        ]

class TNAFlixScraper(AdultScraper):
    """TNAFlix video scraper"""
    NAME = "TNAFlix"
    BASE_URL = "https://www.tnaflix.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("tnaflix_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("tnaflix_api", self._extract_via_api, 90)
        ]

class TXXXScraper(AdultScraper):
    """TXXX video scraper"""
    NAME = "TXXX"
    BASE_URL = "https://www.txxx.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("txxx_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("txxx_api", self._extract_via_api, 90)
        ]

class DrTuberScraper(AdultScraper):
    """DrTuber video scraper"""
    NAME = "DrTuber"
    BASE_URL = "https://www.drtuber.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("drtuber_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("drtuber_api", self._extract_via_api, 90)
        ]

class FourTubeScraper(AdultScraper):
    """4tube video scraper"""
    NAME = "4tube"
    BASE_URL = "https://www.4tube.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("4tube_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("4tube_api", self._extract_via_api, 90)
        ]

class TwentyFourVideoScraper(AdultScraper):
    """24video video scraper"""
    NAME = "24video"
    BASE_URL = "https://www.24video.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("24video_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("24video_api", self._extract_via_api, 90)
        ]

class NinetyOnePornScraper(AdultScraper):
    """91porn video scraper"""
    NAME = "91porn"
    BASE_URL = "https://91porn.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("91porn_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("91porn_api", self._extract_via_api, 90)
        ]

class BeegScraper(AdultScraper):
    """Beeg video scraper"""
    NAME = "Beeg"
    BASE_URL = "https://www.beeg.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("beeg_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("beeg_api", self._extract_via_api, 90)
        ]

class AlphaPornoScraper(AdultScraper):
    """AlphaPorno video scraper"""
    NAME = "AlphaPorno"
    BASE_URL = "https://alpha-porno.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("alphaporno_ytdlp", self._download_with_ytdlp, 100)
        ]

class BehindKinkScraper(AdultScraper):
    """BehindKink video scraper"""
    NAME = "BehindKink"
    BASE_URL = "https://www.behindkink.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("behindkink_ytdlp", self._download_with_ytdlp, 100)
        ]

class BongaCamsScraper(AdultScraper):
    """BongaCams live stream scraper"""
    NAME = "BongaCams"
    BASE_URL = "https://www.bongacams.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.STREAM]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("bongacams_hls", self._extract_hls_stream, 100)
        ]

class CamModelsScraper(AdultScraper):
    """CamModels live stream scraper"""
    NAME = "CamModels"
    BASE_URL = "https://www.cammodels.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.STREAM]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("cammodels_hls", self._extract_hls_stream, 100)
        ]

class CamTubeScraper(AdultScraper):
    """CamTube video scraper"""
    NAME = "CamTube"
    BASE_URL = "https://www.camtube.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("camtube_ytdlp", self._download_with_ytdlp, 100)
        ]

class CamWithHerScraper(AdultScraper):
    """CamWithHer live stream scraper"""
    NAME = "CamWithHer"
    BASE_URL = "https://www.camwithher.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.STREAM]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("camwithher_hls", self._extract_hls_stream, 100)
        ]

class EmpFlixScraper(AdultScraper):
    """EmpFlix video scraper"""
    NAME = "EmpFlix"
    BASE_URL = "https://www.empflix.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("empflix_ytdlp", self._download_with_ytdlp, 100)
        ]

class EPornerScraper(AdultScraper):
    """EPorner video scraper"""
    NAME = "EPorner"
    BASE_URL = "https://www.eporner.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("eporner_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("eporner_api", self._extract_via_api, 90)
        ]

class EroProfileScraper(AdultScraper):
    """EroProfile video scraper"""
    NAME = "EroProfile"
    BASE_URL = "https://www.eroprofile.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO, MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("eroprofile_ytdlp", self._download_with_ytdlp, 100)
        ]

class ExtremeTubeScraper(AdultScraper):
    """ExtremeTube video scraper"""
    NAME = "ExtremeTube"
    BASE_URL = "https://www.extremetube.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("extremetube_ytdlp", self._download_with_ytdlp, 100)
        ]

class HellPornoScraper(AdultScraper):
    """HellPorno video scraper"""
    NAME = "HellPorno"
    BASE_URL = "https://hellporno.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("hellporno_ytdlp", self._download_with_ytdlp, 100)
        ]

class HentaiStigmaScraper(AdultScraper):
    """HentaiStigma anime video scraper"""
    NAME = "HentaiStigma"
    BASE_URL = "https://hentaistigma.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("hentaistigma_ytdlp", self._download_with_ytdlp, 100)
        ]

class HornBunnyScraper(AdultScraper):
    """HornBunny video scraper"""
    NAME = "HornBunny"
    BASE_URL = "https://hornbunny.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("hornbunny_ytdlp", self._download_with_ytdlp, 100)
        ]

class IwaraTVScraper(AdultScraper):
    """Iwara.tv anime video scraper"""
    NAME = "IwaraTV"
    BASE_URL = "https://iwara.tv"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("iwara_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("iwara_api", self._extract_via_api, 90)
        ]

class KeezMoviesScraper(AdultScraper):
    """KeezMovies video scraper"""
    NAME = "KeezMovies"
    BASE_URL = "https://www.keezmovies.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("keezmovies_ytdlp", self._download_with_ytdlp, 100)
        ]

class MotherlessScraper(AdultScraper):
    """Motherless video/image scraper"""
    NAME = "Motherless"
    BASE_URL = "https://motherless.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO, MediaType.IMAGE]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("motherless_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("motherless_direct", self._extract_direct, 90)
        ]

class TumblrNSFWScraper(AdultScraper):
    """Tumblr NSFW content scraper"""
    NAME = "Tumblr NSFW"
    BASE_URL = "https://www.tumblr.com/tagged/nsfw"
    SUPPORTED_MEDIA_TYPES = [MediaType.IMAGE, MediaType.VIDEO, MediaType.GIF]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("tumblr_api", self._extract_via_api, 100),
            ScraperMethod("tumblr_web", self._extract_via_web, 90)
        ]

class RedTubeScraper(AdultScraper):
    """RedTube video scraper"""
    NAME = "RedTube"
    BASE_URL = "https://www.redtube.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("redtube_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("redtube_api", self._extract_via_api, 90)
        ]

class YouPornScraper(AdultScraper):
    """YouPorn video scraper"""
    NAME = "YouPorn"
    BASE_URL = "https://www.youporn.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("youporn_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("youporn_api", self._extract_via_api, 90)
        ]

class TubeGaloreScraper(AdultScraper):
    """TubeGalore aggregator scraper"""
    NAME = "TubeGalore"
    BASE_URL = "https://www.tubegalore.com"
    SUPPORTED_MEDIA_TYPES = [MediaType.VIDEO]

    def _setup_methods(self):
        self.methods = [
            ScraperMethod("tubegalore_ytdlp", self._download_with_ytdlp, 100),
            ScraperMethod("tubegalore_aggregator", self._extract_aggregated, 90)
        ]

# Export all adult scrapers
ADULT_SCRAPERS = [
    PornhubScraper,
    XVideosScraper,
    XHamsterScraper,
    XNXXScraper,
    SpankBangScraper,
    TNAFlixScraper,
    TXXXScraper,
    DrTuberScraper,
    FourTubeScraper,
    TwentyFourVideoScraper,
    NinetyOnePornScraper,
    BeegScraper,
    AlphaPornoScraper,
    BehindKinkScraper,
    BongaCamsScraper,
    CamModelsScraper,
    CamTubeScraper,
    CamWithHerScraper,
    EmpFlixScraper,
    EPornerScraper,
    EroProfileScraper,
    ExtremeTubeScraper,
    HellPornoScraper,
    HentaiStigmaScraper,
    HornBunnyScraper,
    IwaraTVScraper,
    KeezMoviesScraper,
    MotherlessScraper,
    TumblrNSFWScraper,
    RedTubeScraper,
    YouPornScraper,
    TubeGaloreScraper
]

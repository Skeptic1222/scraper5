"""
Source Filtering and Validation System

Filters out sources that cannot be scraped or are inappropriate for given queries.
Improves performance by skipping impossible downloads.
"""

import logging
from typing import List, Set, Dict

logger = logging.getLogger(__name__)

# Sources that require authentication/subscriptions and cannot be scraped
BLACKLISTED_SOURCES = {
    # Streaming services (require paid subscriptions)
    'netflix', 'hulu', 'disney_plus', 'hbo_max', 'amazon_prime', 'peacock',
    'paramount_plus', 'apple_tv', 'crunchyroll', 'funimation',

    # Gaming platforms (require authentication, no scrapable media)
    'steam', 'epic_games', 'gog', 'origin', 'uplay', 'battlenet',
    'xbox_store', 'playstation_store', 'nintendo_eshop',

    # Messaging/Chat apps (require authentication, private content)
    'discord', 'slack', 'telegram', 'whatsapp', 'snapchat', 'wechat',
    'qq', 'mastodon', 'threads',

    # Premium stock photo sites (require paid accounts)
    'shutterstock', 'getty_images', 'istock', 'adobe_stock',

    # News agencies (mostly paywalled or protected)
    'reuters', 'ap_news',

    # Music streaming (require authentication)
    'spotify', 'apple_music', 'tidal', 'deezer', 'youtube_music', 'pandora',

    # Sports (require subscriptions)
    'espn', 'nfl', 'nba', 'mlb', 'nhl', 'fifa', 'uefa', 'sky_sports',

    # Developer platforms (no media content to scrape)
    'github', 'stackoverflow', 'hackernews', 'gitlab', 'bitbucket',
    'sourceforge', 'codeproject',

    # Education (require authentication)
    'coursera', 'udemy', 'khan_academy', 'edx', 'mit_ocw', 'skillshare', 'pluralsight',

    # Shopping sites (product images require different approach)
    'amazon_images', 'ebay_images', 'etsy', 'alibaba',

    # Other
    'linkedin', 'imdb', 'tmdb', 'spotify_covers', 'google_scholar', 'arxiv', 'pubmed',
}

# Source categories for smart filtering
SOURCE_CATEGORIES = {
    'adult_video': {
        'pornhub', 'xvideos', 'redtube', 'xhamster', 'youporn', 'spankbang',
        'redgifs', 'motherless', 'erogarga'
    },
    'general_video': {
        'youtube', 'vimeo', 'dailymotion', 'twitch', 'bitchute', 'rumble'
    },
    'social_media': {
        'instagram', 'twitter', 'tiktok', 'facebook', 'reddit', 'tumblr',
        'pinterest', 'bluesky', 'vkontakte', 'weibo'
    },
    'stock_photos': {
        'unsplash', 'pexels', 'pixabay', 'freepik', 'depositphotos',
        'dreamstime', 'alamy'
    },
    'image_search': {
        'google_images', 'bing_images', 'yandex_images', 'duckduckgo_images',
        'yahoo_images'
    },
    'art_portfolio': {
        'deviantart', 'artstation', 'behance', 'dribbble', 'flickr', '500px'
    },
    'music': {
        'soundcloud', 'bandcamp'
    },
    'anime_hentai': {
        'rule34', 'e621'
    }
}

# Sources known to return placeholder/dummy images
PLACEHOLDER_IMAGE_SOURCES = {
    'pexels', 'pixabay', 'unsplash', 'freepik'  # Often return low-quality placeholders
}


def filter_sources(sources: List[str], content_type: str = 'any', query: str = '') -> List[str]:
    """
    Filter sources to remove blacklisted and inappropriate ones

    Args:
        sources: List of source names
        content_type: 'images', 'videos', or 'any'
        query: Search query (used for relevance scoring)

    Returns:
        Filtered list of valid sources
    """
    filtered = []
    removed = []

    for source in sources:
        source_lower = source.lower()

        # Remove blacklisted sources
        if source_lower in BLACKLISTED_SOURCES:
            removed.append(source)
            logger.info(f"[FILTER] Skipping blacklisted source: {source}")
            continue

        # Content type filtering
        if content_type == 'videos':
            # Skip stock photo sites when looking for videos
            if source_lower in SOURCE_CATEGORIES.get('stock_photos', set()):
                removed.append(source)
                logger.info(f"[FILTER] Skipping {source} (stock photos not suitable for video query)")
                continue
            if source_lower in SOURCE_CATEGORIES.get('image_search', set()):
                removed.append(source)
                logger.info(f"[FILTER] Skipping {source} (image search not suitable for video query)")
                continue

        elif content_type == 'images':
            # Skip video-only sources when looking for images
            if source_lower in SOURCE_CATEGORIES.get('adult_video', set()):
                removed.append(source)
                logger.info(f"[FILTER] Skipping {source} (video source not suitable for image query)")
                continue

        # Query-based filtering
        if query:
            query_lower = query.lower()

            # Skip adult sites for non-adult queries
            if source_lower in SOURCE_CATEGORIES.get('adult_video', set()):
                adult_keywords = ['porn', 'sex', 'xxx', 'adult', 'nsfw', 'twerk', 'ass', 'boob', 'nude']
                if not any(keyword in query_lower for keyword in adult_keywords):
                    removed.append(source)
                    logger.info(f"[FILTER] Skipping {source} (adult source for non-adult query)")
                    continue

            # Skip anime/hentai sites for non-anime queries
            if source_lower in SOURCE_CATEGORIES.get('anime_hentai', set()):
                anime_keywords = ['anime', 'hentai', 'manga', 'rule34', 'e621', 'furry']
                if not any(keyword in query_lower for keyword in anime_keywords):
                    removed.append(source)
                    logger.info(f"[FILTER] Skipping {source} (anime source for non-anime query)")
                    continue

        filtered.append(source)

    logger.info(f"[FILTER] Original: {len(sources)} sources | Filtered: {len(filtered)} sources | Removed: {len(removed)} sources")

    return filtered


def prioritize_sources(sources: List[str], content_type: str = 'any', query: str = '') -> List[str]:
    """
    Prioritize sources based on relevance and success likelihood

    Args:
        sources: List of source names
        content_type: 'images', 'videos', or 'any'
        query: Search query

    Returns:
        Sorted list with most relevant sources first
    """
    priority_scores = {}

    for source in sources:
        score = 50  # Default score
        source_lower = source.lower()

        # Boost reliable sources
        if source_lower in {'youtube', 'pornhub', 'xvideos', 'unsplash', 'pexels'}:
            score += 20

        # Boost based on content type
        if content_type == 'videos':
            if source_lower in SOURCE_CATEGORIES.get('adult_video', set()):
                score += 15
            if source_lower in SOURCE_CATEGORIES.get('general_video', set()):
                score += 15
        elif content_type == 'images':
            if source_lower in SOURCE_CATEGORIES.get('stock_photos', set()):
                score += 10
            if source_lower in SOURCE_CATEGORIES.get('art_portfolio', set()):
                score += 10

        # Boost based on query relevance
        if query:
            query_lower = query.lower()

            # Match query to source categories
            if any(keyword in query_lower for keyword in ['porn', 'sex', 'xxx', 'adult']):
                if source_lower in SOURCE_CATEGORIES.get('adult_video', set()):
                    score += 30

            if any(keyword in query_lower for keyword in ['photo', 'picture', 'wallpaper', 'landscape']):
                if source_lower in SOURCE_CATEGORIES.get('stock_photos', set()):
                    score += 25

            if any(keyword in query_lower for keyword in ['art', 'artist', 'drawing', 'painting']):
                if source_lower in SOURCE_CATEGORIES.get('art_portfolio', set()):
                    score += 25

        # Penalize sources known for placeholder images
        if source_lower in PLACEHOLDER_IMAGE_SOURCES:
            score -= 10

        priority_scores[source] = score

    # Sort by score descending
    sorted_sources = sorted(sources, key=lambda s: priority_scores.get(s, 0), reverse=True)

    logger.info(f"[PRIORITY] Top 5 sources: {sorted_sources[:5]}")

    return sorted_sources


def get_recommended_sources(query: str, content_type: str = 'any', max_sources: int = 20) -> List[str]:
    """
    Get recommended sources for a query

    Args:
        query: Search query
        content_type: 'images', 'videos', or 'any'
        max_sources: Maximum number of sources to recommend

    Returns:
        List of recommended source names
    """
    query_lower = query.lower()
    recommended = []

    # Adult content detection
    is_adult = any(keyword in query_lower for keyword in ['porn', 'sex', 'xxx', 'adult', 'nsfw', 'twerk', 'ass', 'boob', 'nude', 'hentai'])

    # Anime content detection
    is_anime = any(keyword in query_lower for keyword in ['anime', 'hentai', 'manga', 'rule34', 'e621', 'furry'])

    # Art content detection
    is_art = any(keyword in query_lower for keyword in ['art', 'artist', 'drawing', 'painting', 'illustration'])

    # Photo/landscape detection
    is_photo = any(keyword in query_lower for keyword in ['photo', 'picture', 'wallpaper', 'landscape', 'nature', 'scenery'])

    if content_type in ['videos', 'any']:
        if is_adult:
            recommended.extend(['pornhub', 'xvideos', 'redtube', 'xhamster', 'youporn', 'spankbang'])
        else:
            recommended.extend(['youtube', 'vimeo', 'dailymotion'])

    if content_type in ['images', 'any']:
        if is_adult and not is_anime:
            recommended.extend(['redgifs', 'motherless'])
        elif is_anime:
            recommended.extend(['rule34', 'e621'])
        elif is_art:
            recommended.extend(['deviantart', 'artstation', 'behance'])
        elif is_photo:
            recommended.extend(['unsplash', 'pexels', 'pixabay'])
        else:
            recommended.extend(['google_images', 'reddit', 'instagram', 'twitter'])

    # Add social media for person/celebrity searches
    if query_lower[0].isupper() or ' ' not in query:  # Likely a name
        recommended.extend(['instagram', 'twitter', 'reddit', 'youtube'])

    # Deduplicate and limit
    recommended = list(dict.fromkeys(recommended))[:max_sources]

    logger.info(f"[RECOMMEND] Query: '{query}' | Type: {content_type} | Recommended: {recommended}")

    return recommended

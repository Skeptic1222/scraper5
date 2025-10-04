#!/usr/bin/env python3
"""
Standalone Sources Data - No external dependencies
Contains all 78+ content sources for the scraper
"""

def get_content_sources():
    """Return comprehensive list of 78+ content sources with metadata

    Adds an 'implemented' boolean to each source to indicate if that source
    is currently wired to a working downloader path. This flag is used by the
    UI to color-code sources and by APIs for filtering.
    """
    sources = {
        'search_engines': [
            {'id': 'google_images', 'name': 'Google Images', 'category': 'search', 'subscription_required': False, 'nsfw': False},
            {'id': 'bing_images', 'name': 'Bing Images', 'category': 'search', 'subscription_required': False, 'nsfw': False},
            {'id': 'yandex_images', 'name': 'Yandex Images', 'category': 'search', 'subscription_required': False, 'nsfw': False},
            {'id': 'duckduckgo_images', 'name': 'DuckDuckGo Images', 'category': 'search', 'subscription_required': False, 'nsfw': False},
            {'id': 'yahoo_images', 'name': 'Yahoo Images', 'category': 'search', 'subscription_required': False, 'nsfw': False},
        ],
        'galleries': [
            {'id': 'unsplash', 'name': 'Unsplash', 'category': 'photos', 'subscription_required': False, 'nsfw': False},
            {'id': 'pixabay', 'name': 'Pixabay', 'category': 'photos', 'subscription_required': False, 'nsfw': False},
            {'id': 'pexels', 'name': 'Pexels', 'category': 'photos', 'subscription_required': False, 'nsfw': False},
            {'id': 'freepik', 'name': 'Freepik', 'category': 'photos', 'subscription_required': True, 'nsfw': False},
            {'id': 'shutterstock', 'name': 'Shutterstock', 'category': 'photos', 'subscription_required': True, 'nsfw': False},
            {'id': 'getty_images', 'name': 'Getty Images', 'category': 'photos', 'subscription_required': True, 'nsfw': False},
            {'id': 'adobe_stock', 'name': 'Adobe Stock', 'category': 'photos', 'subscription_required': True, 'nsfw': False},
        ],
        'stock_photos': [
            {'id': 'istock', 'name': 'iStock', 'category': 'stock', 'subscription_required': True, 'nsfw': False},
            {'id': 'depositphotos', 'name': 'DepositPhotos', 'category': 'stock', 'subscription_required': True, 'nsfw': False},
            {'id': 'dreamstime', 'name': 'Dreamstime', 'category': 'stock', 'subscription_required': True, 'nsfw': False},
            {'id': 'alamy', 'name': 'Alamy', 'category': 'stock', 'subscription_required': True, 'nsfw': False},
        ],
        'social_media': [
            {'id': 'reddit', 'name': 'Reddit', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'instagram', 'name': 'Instagram', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'twitter', 'name': 'Twitter/X', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'tiktok', 'name': 'TikTok', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'pinterest', 'name': 'Pinterest', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'tumblr', 'name': 'Tumblr', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'linkedin', 'name': 'LinkedIn', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'facebook', 'name': 'Facebook', 'category': 'social', 'subscription_required': True, 'nsfw': False},
        ],
        'video_platforms': [
            {'id': 'youtube', 'name': 'YouTube', 'category': 'video', 'subscription_required': False, 'nsfw': False},
            {'id': 'vimeo', 'name': 'Vimeo', 'category': 'video', 'subscription_required': False, 'nsfw': False},
            {'id': 'dailymotion', 'name': 'Dailymotion', 'category': 'video', 'subscription_required': False, 'nsfw': False},
            {'id': 'twitch', 'name': 'Twitch', 'category': 'video', 'subscription_required': False, 'nsfw': False},
            {'id': 'bitchute', 'name': 'BitChute', 'category': 'video', 'subscription_required': False, 'nsfw': False},
            {'id': 'rumble', 'name': 'Rumble', 'category': 'video', 'subscription_required': False, 'nsfw': False},
        ],
        'art_platforms': [
            {'id': 'deviantart', 'name': 'DeviantArt', 'category': 'art', 'subscription_required': False, 'nsfw': False},
            {'id': 'artstation', 'name': 'ArtStation', 'category': 'art', 'subscription_required': False, 'nsfw': False},
            {'id': 'behance', 'name': 'Behance', 'category': 'art', 'subscription_required': False, 'nsfw': False},
            {'id': 'dribbble', 'name': 'Dribbble', 'category': 'art', 'subscription_required': False, 'nsfw': False},
            {'id': 'flickr', 'name': 'Flickr', 'category': 'art', 'subscription_required': False, 'nsfw': False},
            {'id': '500px', 'name': '500px', 'category': 'art', 'subscription_required': False, 'nsfw': False},
        ],
        'adult_content': [
            {'id': 'pornhub', 'name': 'Pornhub', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'xvideos', 'name': 'XVideos', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'redtube', 'name': 'RedTube', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'motherless', 'name': 'Motherless', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'rule34', 'name': 'Rule34', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'e621', 'name': 'e621', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'erogarga', 'name': 'EroGarga', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'xhamster', 'name': 'XHamster', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'youporn', 'name': 'YouPorn', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'spankbang', 'name': 'SpankBang', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
            {'id': 'redgifs', 'name': 'RedGifs', 'category': 'adult', 'subscription_required': True, 'nsfw': True},
        ],
        'news_media': [
            {'id': 'reuters', 'name': 'Reuters', 'category': 'news', 'subscription_required': False, 'nsfw': False},
            {'id': 'ap_news', 'name': 'Associated Press', 'category': 'news', 'subscription_required': False, 'nsfw': False},
            {'id': 'bbc', 'name': 'BBC News', 'category': 'news', 'subscription_required': False, 'nsfw': False},
            {'id': 'cnn', 'name': 'CNN', 'category': 'news', 'subscription_required': False, 'nsfw': False},
        ],
        'e_commerce': [
            {'id': 'amazon_images', 'name': 'Amazon Product Images', 'category': 'commerce', 'subscription_required': False, 'nsfw': False},
            {'id': 'ebay_images', 'name': 'eBay Listings', 'category': 'commerce', 'subscription_required': False, 'nsfw': False},
            {'id': 'etsy', 'name': 'Etsy', 'category': 'commerce', 'subscription_required': False, 'nsfw': False},
            {'id': 'alibaba', 'name': 'Alibaba', 'category': 'commerce', 'subscription_required': False, 'nsfw': False},
        ],
        'entertainment': [
            {'id': 'imdb', 'name': 'IMDb', 'category': 'entertainment', 'subscription_required': False, 'nsfw': False},
            {'id': 'tmdb', 'name': 'TheMovieDB', 'category': 'entertainment', 'subscription_required': False, 'nsfw': False},
            {'id': 'spotify_covers', 'name': 'Spotify Album Covers', 'category': 'entertainment', 'subscription_required': False, 'nsfw': False},
        ],
        'academic': [
            {'id': 'google_scholar', 'name': 'Google Scholar', 'category': 'academic', 'subscription_required': False, 'nsfw': False},
            {'id': 'arxiv', 'name': 'arXiv', 'category': 'academic', 'subscription_required': False, 'nsfw': False},
            {'id': 'pubmed', 'name': 'PubMed', 'category': 'academic', 'subscription_required': False, 'nsfw': False},
        ],
        'tech_forums': [
            {'id': 'github', 'name': 'GitHub', 'category': 'tech', 'subscription_required': False, 'nsfw': False},
            {'id': 'stackoverflow', 'name': 'Stack Overflow', 'category': 'tech', 'subscription_required': False, 'nsfw': False},
            {'id': 'hackernews', 'name': 'Hacker News', 'category': 'tech', 'subscription_required': False, 'nsfw': False},
            {'id': 'gitlab', 'name': 'GitLab', 'category': 'tech', 'subscription_required': False, 'nsfw': False},
            {'id': 'bitbucket', 'name': 'Bitbucket', 'category': 'tech', 'subscription_required': False, 'nsfw': False},
            {'id': 'sourceforge', 'name': 'SourceForge', 'category': 'tech', 'subscription_required': False, 'nsfw': False},
            {'id': 'codeproject', 'name': 'CodeProject', 'category': 'tech', 'subscription_required': False, 'nsfw': False},
        ],
        'additional_social': [
            {'id': 'snapchat', 'name': 'Snapchat', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'whatsapp', 'name': 'WhatsApp', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'telegram', 'name': 'Telegram', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'discord', 'name': 'Discord', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'slack', 'name': 'Slack', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'wechat', 'name': 'WeChat', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'qq', 'name': 'QQ', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'vkontakte', 'name': 'VKontakte', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'weibo', 'name': 'Weibo', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'mastodon', 'name': 'Mastodon', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'threads', 'name': 'Threads', 'category': 'social', 'subscription_required': False, 'nsfw': False},
            {'id': 'bluesky', 'name': 'Bluesky', 'category': 'social', 'subscription_required': False, 'nsfw': False},
        ],
        'streaming_platforms': [
            {'id': 'netflix', 'name': 'Netflix', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
            {'id': 'hulu', 'name': 'Hulu', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
            {'id': 'disney_plus', 'name': 'Disney+', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
            {'id': 'hbo_max', 'name': 'HBO Max', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
            {'id': 'amazon_prime', 'name': 'Amazon Prime Video', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
            {'id': 'peacock', 'name': 'Peacock', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
            {'id': 'paramount_plus', 'name': 'Paramount+', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
            {'id': 'apple_tv', 'name': 'Apple TV+', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
            {'id': 'crunchyroll', 'name': 'Crunchyroll', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
            {'id': 'funimation', 'name': 'Funimation', 'category': 'streaming', 'subscription_required': True, 'nsfw': False},
        ],
        'music_platforms': [
            {'id': 'spotify', 'name': 'Spotify', 'category': 'music', 'subscription_required': False, 'nsfw': False},
            {'id': 'apple_music', 'name': 'Apple Music', 'category': 'music', 'subscription_required': True, 'nsfw': False},
            {'id': 'soundcloud', 'name': 'SoundCloud', 'category': 'music', 'subscription_required': False, 'nsfw': False},
            {'id': 'bandcamp', 'name': 'Bandcamp', 'category': 'music', 'subscription_required': False, 'nsfw': False},
            {'id': 'tidal', 'name': 'Tidal', 'category': 'music', 'subscription_required': True, 'nsfw': False},
            {'id': 'deezer', 'name': 'Deezer', 'category': 'music', 'subscription_required': True, 'nsfw': False},
            {'id': 'youtube_music', 'name': 'YouTube Music', 'category': 'music', 'subscription_required': False, 'nsfw': False},
            {'id': 'pandora', 'name': 'Pandora', 'category': 'music', 'subscription_required': False, 'nsfw': False},
        ],
        'gaming_platforms': [
            {'id': 'steam', 'name': 'Steam', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
            {'id': 'epic_games', 'name': 'Epic Games', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
            {'id': 'gog', 'name': 'GOG', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
            {'id': 'origin', 'name': 'Origin', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
            {'id': 'uplay', 'name': 'Ubisoft Connect', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
            {'id': 'battlenet', 'name': 'Battle.net', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
            {'id': 'xbox_store', 'name': 'Xbox Store', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
            {'id': 'playstation_store', 'name': 'PlayStation Store', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
            {'id': 'nintendo_eshop', 'name': 'Nintendo eShop', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
            {'id': 'itch_io', 'name': 'itch.io', 'category': 'gaming', 'subscription_required': False, 'nsfw': False},
        ],
        'sports_media': [
            {'id': 'espn', 'name': 'ESPN', 'category': 'sports', 'subscription_required': False, 'nsfw': False},
            {'id': 'nfl', 'name': 'NFL', 'category': 'sports', 'subscription_required': False, 'nsfw': False},
            {'id': 'nba', 'name': 'NBA', 'category': 'sports', 'subscription_required': False, 'nsfw': False},
            {'id': 'mlb', 'name': 'MLB', 'category': 'sports', 'subscription_required': False, 'nsfw': False},
            {'id': 'nhl', 'name': 'NHL', 'category': 'sports', 'subscription_required': False, 'nsfw': False},
            {'id': 'fifa', 'name': 'FIFA', 'category': 'sports', 'subscription_required': False, 'nsfw': False},
            {'id': 'uefa', 'name': 'UEFA', 'category': 'sports', 'subscription_required': False, 'nsfw': False},
            {'id': 'sky_sports', 'name': 'Sky Sports', 'category': 'sports', 'subscription_required': True, 'nsfw': False},
        ],
        'education_resources': [
            {'id': 'coursera', 'name': 'Coursera', 'category': 'education', 'subscription_required': False, 'nsfw': False},
            {'id': 'udemy', 'name': 'Udemy', 'category': 'education', 'subscription_required': False, 'nsfw': False},
            {'id': 'khan_academy', 'name': 'Khan Academy', 'category': 'education', 'subscription_required': False, 'nsfw': False},
            {'id': 'edx', 'name': 'edX', 'category': 'education', 'subscription_required': False, 'nsfw': False},
            {'id': 'mit_ocw', 'name': 'MIT OpenCourseWare', 'category': 'education', 'subscription_required': False, 'nsfw': False},
            {'id': 'skillshare', 'name': 'Skillshare', 'category': 'education', 'subscription_required': True, 'nsfw': False},
            {'id': 'pluralsight', 'name': 'Pluralsight', 'category': 'education', 'subscription_required': True, 'nsfw': False},
        ]
    }

    # Mark implemented sources
    implemented_ids = set([
        # Search engines via enhanced scraper
        'google_images', 'bing_images', 'duckduckgo_images', 'yahoo_images', 'yandex_images',
        # Free galleries via working media downloader/API
        'unsplash', 'pixabay', 'pexels',
        # Video platforms (yt-dlp based)
        'youtube', 'vimeo', 'dailymotion', 'twitch', 'bitchute', 'rumble',
        # Social media (fallback via resilient image search)
        'reddit', 'instagram', 'twitter', 'tiktok', 'pinterest', 'tumblr', 'linkedin',
        # Art platforms (fallback via resilient image search)
        'deviantart', 'artstation', 'behance', 'dribbble', 'flickr', '500px',
        # Sports media (fallback)
        'espn', 'nfl', 'nba', 'mlb', 'nhl', 'fifa', 'uefa',
        # Education (fallback)
        'coursera', 'udemy', 'khan_academy', 'edx', 'mit_ocw',
        # Music (non-premium only; fallback)
        'spotify', 'apple_music', 'soundcloud', 'bandcamp', 'youtube_music', 'pandora',
        # Gaming platforms (fallback)
        'steam', 'epic_games', 'gog', 'origin', 'uplay', 'battlenet', 'xbox_store', 'playstation_store', 'nintendo_eshop', 'itch_io',
        # Adult content (enabled; video via yt-dlp where supported)
        'pornhub', 'xvideos', 'redtube', 'motherless', 'rule34', 'e621', 'erogarga',
        'xhamster', 'youporn', 'spankbang', 'redgifs',
    ])

    for category_key, category_sources in list(sources.items()):
        if isinstance(category_sources, list):
            for s in category_sources:
                if isinstance(s, dict) and 'id' in s:
                    s['implemented'] = s['id'] in implemented_ids

    # Add 'all' key with flattened list
    all_sources = []
    for category_sources in sources.values():
        if isinstance(category_sources, list):
            all_sources.extend(category_sources)
    sources['all'] = all_sources

    return sources

# For backwards compatibility
def get_all_sources():
    """Get flattened list of all sources"""
    sources = get_content_sources()
    return sources.get('all', [])

if __name__ == "__main__":
    # Test the function
    sources = get_content_sources()
    print(f"Total categories: {len(sources) - 1}")  # -1 for 'all' key
    total = sum(len(v) for k, v in sources.items() if k != 'all')
    print(f"Total sources: {total}")

    for category, source_list in sources.items():
        if category != 'all':
            print(f"{category}: {len(source_list)} sources")

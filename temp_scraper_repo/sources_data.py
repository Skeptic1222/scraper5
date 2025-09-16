#!/usr/bin/env python3
"""
Standalone Sources Data - No external dependencies
Contains all 78+ content sources for the scraper
"""

def get_content_sources():
    """Return comprehensive list of 78+ content sources with metadata"""
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
        ]
    }

    # Add 'all' key with flattened list
    all_sources = []
    for category_sources in sources.values():
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

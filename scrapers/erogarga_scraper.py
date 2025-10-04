"""
Erogarga.com scraper
Scrapes vintage adult film content from erogarga.com
"""
import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import subprocess
import json

# Configure logging
logger = logging.getLogger('erogarga_scraper')
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.FileHandler('logs/download_errors.log')
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.addHandler(handler)


def extract_video_from_page(url):
    """
    Extract video information from an erogarga.com page

    Args:
        url: URL to erogarga.com page

    Returns:
        dict: {
            'title': str,
            'description': str,
            'thumbnail': str,
            'player_url': str,
            'video_id': str,
            'video_urls': list (if extractable)
        }
    """
    results = {
        'title': None,
        'description': None,
        'thumbnail': None,
        'player_url': None,
        'video_id': None,
        'video_urls': [],
        'success': False,
        'error': None
    }

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.erogarga.com/'
        }

        logger.info(f"EROGARGA: Fetching {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title_tag = soup.find('meta', property='og:title') or soup.find('title')
        if title_tag:
            results['title'] = title_tag.get('content') if title_tag.get('content') else title_tag.text.strip()
            logger.info(f"EROGARGA: Title: {results['title']}")

        # Extract description
        desc_tag = soup.find('meta', property='og:description') or soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            results['description'] = desc_tag.get('content', '').strip()

        # Extract thumbnail
        thumb_tag = soup.find('meta', property='og:image')
        if thumb_tag:
            results['thumbnail'] = thumb_tag.get('content')
            logger.info(f"EROGARGA: Thumbnail: {results['thumbnail']}")

        # Extract cine-matik player iframe
        iframe = soup.find('iframe', src=re.compile(r'cine-matik\.com/player'))
        if iframe:
            player_url = iframe.get('src')
            results['player_url'] = player_url
            logger.info(f"EROGARGA: Found player: {player_url}")

            # Extract video ID from player URL
            vid_match = re.search(r'vid=([a-f0-9]{32})', player_url)
            if vid_match:
                results['video_id'] = vid_match.group(1)
                logger.info(f"EROGARGA: Video ID: {results['video_id']}")

            # Try to extract actual video URL from cine-matik player
            video_urls = extract_from_cine_matik_player(player_url)
            if video_urls:
                results['video_urls'] = video_urls
                logger.info(f"EROGARGA: Found {len(video_urls)} video URL(s)")

        # Try yt-dlp as fallback for actual video extraction
        if not results['video_urls']:
            logger.info(f"EROGARGA: Trying yt-dlp fallback for {url}")
            video_urls = try_ytdlp_extraction(url)
            if video_urls:
                results['video_urls'] = video_urls
                logger.info(f"EROGARGA: yt-dlp found {len(video_urls)} video URL(s)")

        results['success'] = True
        return results

    except requests.RequestException as e:
        logger.error(f"EROGARGA: Network error: {e}")
        results['error'] = f"Network error: {str(e)}"
        return results
    except Exception as e:
        logger.error(f"EROGARGA: Extraction error: {e}")
        results['error'] = f"Extraction error: {str(e)}"
        return results


def extract_from_cine_matik_player(player_url):
    """
    Extract video URL from cine-matik player by calling their API directly
    The player uses an AJAX endpoint to get the eporner iframe URL

    Args:
        player_url: URL to cine-matik player (contains vid= parameter)

    Returns:
        list: List of video URLs (if found)
    """
    video_urls = []

    try:
        # Extract video ID from player URL
        vid_match = re.search(r'vid=([a-f0-9]{32})', player_url)
        if not vid_match:
            logger.error("EROGARGA: Could not extract video ID from player URL")
            return video_urls

        video_id = vid_match.group(1)
        logger.info(f"EROGARGA: Calling cine-matik API for video ID: {video_id}")

        # Call the API endpoint that the player uses
        api_url = 'https://cine-matik.com/player/ajax_sources.php'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': player_url,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'vid': video_id,
            'alternative': '',
            'ord': '1'
        }

        response = requests.post(api_url, headers=headers, data=data, timeout=15)

        if response.status_code == 200:
            try:
                api_data = response.json()

                if api_data.get('status') == 'true' and api_data.get('iframe'):
                    eporner_url = api_data['iframe']
                    logger.info(f"EROGARGA: Got eporner embed URL from API: {eporner_url}")

                    # Extract video from eporner embed using yt-dlp
                    video_url = extract_from_eporner_embed(eporner_url)
                    if video_url:
                        video_urls.append(video_url)
                        logger.info(f"EROGARGA: Extracted video: {video_url}")
                else:
                    logger.warning(f"EROGARGA: API returned no iframe URL. Status: {api_data.get('status')}")

            except json.JSONDecodeError as e:
                logger.error(f"EROGARGA: Failed to parse API response: {e}")
        else:
            logger.warning(f"EROGARGA: API returned status {response.status_code}")

    except Exception as e:
        logger.error(f"EROGARGA: Error calling cine-matik API: {e}")

    return video_urls


def extract_from_eporner_embed(embed_url):
    """
    Extract video URL from eporner embed using yt-dlp

    Args:
        embed_url: URL to eporner embed page

    Returns:
        str: Video URL (if found)
    """
    try:
        logger.info(f"EROGARGA: Extracting from eporner embed: {embed_url}")

        # Use yt-dlp to extract video (supports eporner)
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-download',
            '--no-warnings',
            '--quiet',
            embed_url
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)

            # Get best quality video URL
            if 'url' in data:
                video_url = data['url']
                logger.info(f"EROGARGA: Found video via yt-dlp (default quality): {video_url}")
                return video_url
            elif 'formats' in data and data['formats']:
                # Get highest quality format
                formats = data['formats']
                best_format = max(formats, key=lambda f: f.get('height', 0))
                video_url = best_format.get('url')
                if video_url:
                    quality = best_format.get('format_id', 'unknown')
                    logger.info(f"EROGARGA: Found video via yt-dlp ({quality}): {video_url}")
                    return video_url

        logger.warning(f"EROGARGA: yt-dlp could not extract video from {embed_url}")
        return None

    except subprocess.TimeoutExpired:
        logger.error("EROGARGA: yt-dlp timeout while extracting eporner embed")
        return None
    except FileNotFoundError:
        logger.error("EROGARGA: yt-dlp not found, cannot extract eporner video")
        return None
    except Exception as e:
        logger.error(f"EROGARGA: Error extracting eporner video: {e}")
        return None


def try_ytdlp_extraction(url):
    """
    Try to extract video using yt-dlp as fallback

    Args:
        url: URL to extract from

    Returns:
        list: List of video URLs
    """
    video_urls = []

    try:
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-download',
            '--no-warnings',
            '--quiet',
            url
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)

            # Try to get direct URL
            if 'url' in data:
                video_urls.append(data['url'])
            elif 'formats' in data and data['formats']:
                # Get best format
                for fmt in data['formats']:
                    if fmt.get('url'):
                        video_urls.append(fmt['url'])
                        break

        else:
            logger.warning(f"EROGARGA: yt-dlp failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.error("EROGARGA: yt-dlp timeout")
    except FileNotFoundError:
        logger.warning("EROGARGA: yt-dlp not found")
    except Exception as e:
        logger.error(f"EROGARGA: yt-dlp error: {e}")

    return video_urls


def download_media(url, output_dir):
    """
    Download media from erogarga.com

    Args:
        url: URL to erogarga.com page
        output_dir: Directory to save downloads

    Returns:
        dict: Download results
    """
    results = extract_video_from_page(url)

    if not results['success']:
        return {
            'success': False,
            'error': results['error'],
            'downloaded': []
        }

    downloaded = []

    # Download thumbnail if available
    if results['thumbnail']:
        try:
            thumb_response = requests.get(results['thumbnail'], timeout=10)
            if thumb_response.status_code == 200:
                thumb_path = f"{output_dir}/thumbnail.jpg"
                with open(thumb_path, 'wb') as f:
                    f.write(thumb_response.content)
                downloaded.append({
                    'path': thumb_path,
                    'type': 'image',
                    'url': results['thumbnail']
                })
                logger.info(f"EROGARGA: Downloaded thumbnail to {thumb_path}")
        except Exception as e:
            logger.error(f"EROGARGA: Thumbnail download error: {e}")

    # Try to download video URLs
    for video_url in results['video_urls']:
        try:
            logger.info(f"EROGARGA: Downloading video from {video_url}")
            video_response = requests.get(video_url, timeout=60, stream=True)

            if video_response.status_code == 200:
                video_path = f"{output_dir}/video.mp4"
                with open(video_path, 'wb') as f:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                downloaded.append({
                    'path': video_path,
                    'type': 'video',
                    'url': video_url
                })
                logger.info(f"EROGARGA: Downloaded video to {video_path}")
                break  # Only download first working video

        except Exception as e:
            logger.error(f"EROGARGA: Video download error: {e}")
            continue

    return {
        'success': len(downloaded) > 0,
        'downloaded': downloaded,
        'metadata': {
            'title': results['title'],
            'description': results['description'],
            'source': 'erogarga'
        }
    }


if __name__ == '__main__':
    # Test the scraper
    test_url = 'https://www.erogarga.com/a-prisao-1980/'

    print(f"Testing erogarga scraper with: {test_url}\n")

    results = extract_video_from_page(test_url)

    print("Results:")
    print(f"  Title: {results['title']}")
    print(f"  Description: {results['description'][:100]}..." if results['description'] else "  Description: None")
    print(f"  Thumbnail: {results['thumbnail']}")
    print(f"  Player URL: {results['player_url']}")
    print(f"  Video ID: {results['video_id']}")
    print(f"  Video URLs found: {len(results['video_urls'])}")
    for url in results['video_urls']:
        print(f"    - {url}")
    print(f"  Success: {results['success']}")
    if results['error']:
        print(f"  Error: {results['error']}")

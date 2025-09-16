"""
Memory-based Asset Manager - Works without database
"""
import os
import uuid
from datetime import datetime

# In-memory asset storage
MEMORY_ASSETS = []

def add_asset(job_id, filepath, file_type, metadata=None):
    """Add asset to memory storage"""
    asset_id = str(uuid.uuid4())
    asset = {
        'id': asset_id,
        'job_id': job_id,
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'file_type': file_type,
        'metadata': metadata or {},
        'created_at': datetime.utcnow().isoformat(),
        'file_size': os.path.getsize(filepath) if os.path.exists(filepath) else 0
    }
    MEMORY_ASSETS.append(asset)
    print(f"[ASSETS] Added asset {asset_id}: {asset['filename']}")
    return asset_id

def get_assets(user_id=None, file_type=None, limit=100, offset=0):
    """Get assets from memory"""
    # Filter by file type if specified
    assets = MEMORY_ASSETS
    if file_type:
        if file_type == 'image':
            assets = [a for a in assets if a.get('file_type', '').startswith('image')]
        elif file_type == 'video':
            assets = [a for a in assets if a.get('file_type', '').startswith('video')]

    # Apply pagination
    start = max(0, len(assets) - offset - limit)
    end = len(assets) - offset
    if start < 0:
        start = 0
    if end < 0:
        return []
    return assets[start:end][::-1]  # Most recent first

def get_asset(asset_id):
    """Get specific asset from memory"""
    for asset in MEMORY_ASSETS:
        if asset['id'] == asset_id:
            return asset
    return None

def delete_asset(asset_id):
    """Delete asset from memory"""
    global MEMORY_ASSETS
    MEMORY_ASSETS = [a for a in MEMORY_ASSETS if a['id'] != asset_id]
    return True

def cleanup_missing_files():
    """Remove assets with missing files"""
    global MEMORY_ASSETS
    before = len(MEMORY_ASSETS)
    MEMORY_ASSETS = [a for a in MEMORY_ASSETS if os.path.exists(a.get('filepath', ''))]

def save_asset(**kwargs):
    """Save asset with flexible parameters"""
    asset_id = str(uuid.uuid4())
    asset = {
        'id': asset_id,
        'job_id': kwargs.get('job_id'),
        'user_id': kwargs.get('user_id'),
        'filename': kwargs.get('filename', 'unknown'),
        'file_path': kwargs.get('file_path', ''),
        'filepath': kwargs.get('file_path', ''),  # Alias for compatibility
        'original_url': kwargs.get('original_url', ''),
        'source': kwargs.get('source', 'unknown'),
        'content_type': kwargs.get('content_type', 'application/octet-stream'),
        'file_size': kwargs.get('file_size', 0),
        'title': kwargs.get('title', ''),
        'created_at': datetime.utcnow().isoformat(),
        'metadata': kwargs.get('metadata', {})
    }

    # Try to get file size if not provided
    if asset['file_size'] == 0 and asset['file_path'] and os.path.exists(asset['file_path']):
        asset['file_size'] = os.path.getsize(asset['file_path'])

    MEMORY_ASSETS.append(asset)
    print(f"[ASSETS] Saved asset {asset_id}: {asset['filename']} from {asset['source']}")
    return asset_id

# Create a class-like interface for compatibility
class DBAssetManager:
    """Memory-based asset manager"""
    add_asset = staticmethod(add_asset)
    get_assets = staticmethod(get_assets)
    get_asset = staticmethod(get_asset)
    delete_asset = staticmethod(delete_asset)
    cleanup_missing_files = staticmethod(cleanup_missing_files)
    save_asset = staticmethod(save_asset)

    @staticmethod
    def get_asset_statistics(user_id=None):
        """Get statistics about assets"""
        total_assets = len(MEMORY_ASSETS)

        # Count by file type
        image_count = 0
        video_count = 0
        other_count = 0

        for asset in MEMORY_ASSETS:
            file_type = asset.get('file_type', 'unknown')
            if file_type.startswith('image'):
                image_count += 1
            elif file_type.startswith('video'):
                video_count += 1
            else:
                other_count += 1

        # Calculate statistics
        stats = {
            'total_assets': total_assets,
            'total_images': image_count,  # Added for compatibility
            'total_videos': video_count,  # Added for compatibility
            'total_size': sum(a.get('file_size', 0) for a in MEMORY_ASSETS),
            'by_type': {
                'image': image_count,
                'video': video_count,
                'other': other_count
            },
            'by_source': {},
            'recent_assets': []
        }

        # Count by source
        for asset in MEMORY_ASSETS:
            source = asset.get('source', 'unknown')
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1

        # Get recent assets (last 5)
        stats['recent_assets'] = MEMORY_ASSETS[-5:] if MEMORY_ASSETS else []

        return stats

# Create instance for import
db_asset_manager = DBAssetManager()

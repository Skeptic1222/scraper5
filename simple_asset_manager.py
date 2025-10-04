"""
Simple Asset Manager - Works without database/Flask context
Stores asset information in memory and JSON file for persistence
"""
import json
import os
import uuid
from datetime import datetime

# In-memory asset storage
MEMORY_ASSETS = {}
ASSET_FILE = "assets.json"

def load_assets():
    """Load assets from JSON file"""
    global MEMORY_ASSETS
    if os.path.exists(ASSET_FILE):
        try:
            with open(ASSET_FILE, 'r') as f:
                MEMORY_ASSETS = json.load(f)
                print(f"[ASSETS] Loaded {len(MEMORY_ASSETS)} assets from file")
        except Exception as e:
            print(f"[ASSETS] Error loading assets: {e}")
            MEMORY_ASSETS = {}

def save_assets():
    """Save assets to JSON file"""
    try:
        with open(ASSET_FILE, 'w') as f:
            json.dump(MEMORY_ASSETS, f, indent=2)
    except Exception as e:
        print(f"[ASSETS] Error saving assets: {e}")

def add_asset(job_id, filepath, file_type, metadata=None):
    """Add asset to memory storage"""
    try:
        asset_id = str(uuid.uuid4())

        # Get file info
        filename = os.path.basename(filepath) if filepath else 'unknown'
        file_size = os.path.getsize(filepath) if filepath and os.path.exists(filepath) else 0

        asset = {
            'id': asset_id,
            'job_id': job_id,
            'filepath': filepath,
            'filename': filename,
            'file_type': file_type,
            'file_size': file_size,
            'metadata': metadata or {},
            'created_at': datetime.utcnow().isoformat(),
            'is_deleted': False
        }

        MEMORY_ASSETS[asset_id] = asset
        save_assets()

        print(f"[ASSETS] Added asset {asset_id}: {filename} ({file_type})")
        return asset_id

    except Exception as e:
        print(f"[ASSETS] Failed to add asset: {e}")
        return None

def get_assets(user_id=None, file_type=None, limit=100, offset=0):
    """Get assets from memory storage"""
    try:
        # Filter assets
        assets = []
        for asset in MEMORY_ASSETS.values():
            if asset.get('is_deleted'):
                continue
            if file_type and asset.get('file_type') != file_type:
                continue
            if user_id and asset.get('metadata', {}).get('user_id') != user_id:
                continue
            assets.append(asset)

        # Sort by created_at descending
        assets.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Apply offset and limit
        if offset:
            assets = assets[offset:]
        if limit:
            assets = assets[:limit]

        return assets

    except Exception as e:
        print(f"[ASSETS] Failed to get assets: {e}")
        return []

def get_asset_statistics(user_id=None):
    """Get statistics about assets"""
    try:
        total = 0
        images = 0
        videos = 0

        for asset in MEMORY_ASSETS.values():
            if asset.get('is_deleted'):
                continue
            if user_id and asset.get('metadata', {}).get('user_id') != user_id:
                continue

            total += 1
            if 'image' in asset.get('file_type', '').lower():
                images += 1
            elif 'video' in asset.get('file_type', '').lower():
                videos += 1

        return {
            'total': total,
            'images': images,
            'videos': videos,
            'all': total
        }

    except Exception as e:
        print(f"[ASSETS] Failed to get statistics: {e}")
        return {'total': 0, 'images': 0, 'videos': 0, 'all': 0}

# Initialize on import
load_assets()

# Create a class interface for compatibility
class SimpleAssetManager:
    """Simple asset manager without database"""
    add_asset = staticmethod(add_asset)
    get_assets = staticmethod(get_assets)
    get_asset_statistics = staticmethod(get_asset_statistics)

    @staticmethod
    def save_asset(**kwargs):
        """Save asset with flexible parameters"""
        filepath = kwargs.get('file_path', '')
        file_type = kwargs.get('content_type', 'unknown')
        metadata = kwargs.get('metadata', {})
        metadata.update({
            'source': kwargs.get('source', 'unknown'),
            'original_url': kwargs.get('url', ''),
            'title': kwargs.get('title', ''),
            'user_id': kwargs.get('user_id')
        })
        return add_asset(kwargs.get('job_id'), filepath, file_type, metadata)

# Create instance
simple_asset_manager = SimpleAssetManager()
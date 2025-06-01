# Bulk Operations and Video Download Implementation

## Overview
This document describes the implementation of bulk operations (select all, bulk delete, bulk move) and improvements to video downloading functionality.

## New Features

### 1. Bulk Selection and Operations

#### Select All Functionality
- Added master checkbox in the asset navigation bar
- `toggleSelectAll(checked)` function handles select/deselect all assets
- Visual feedback with checkbox state (checked, indeterminate for partial selection)

#### Bulk Delete
- New endpoint: `POST /api/assets/bulk-delete`
- Accepts array of asset IDs
- Properly deletes MediaBlobs from database
- Updates UI after successful deletion

#### Bulk Move to Containers
- New endpoint: `POST /api/assets/bulk-move`
- Allows moving assets to different containers/categories
- Dynamic container creation supported
- Container list endpoint: `GET /api/containers`

### 2. Database-Based Delete Operations

#### Updated Delete Logic
- `delete_asset()` now deletes associated MediaBlob
- Soft delete (marks as deleted) + hard delete of blob data
- Ensures no orphaned blobs in database

#### Bulk Delete Implementation
```python
def bulk_delete_assets(self, asset_ids, user_id=None):
    """Bulk delete multiple assets"""
    # Deletes both Asset records and MediaBlobs
    # Respects user permissions
    # Returns count of deleted assets
```

### 3. Enhanced Video Download Support

#### New Video Search Function
```python
def enhanced_video_search(query, max_results=50, safe_search=True):
    """
    Enhanced video search across multiple video platforms
    - YouTube search
    - Vimeo search  
    - Internet Archive videos
    """
```

#### Video Download with yt-dlp
```python
def download_videos_with_ytdlp(urls, output_dir, progress_callback=None):
    """
    Download videos using yt-dlp with proper progress tracking
    - Format limiting (720p max for size)
    - File size limits (100MB max)
    - Progress callback integration
    """
```

#### Integrated Video Search
- Comprehensive search now detects video-related queries
- Automatically searches video platforms for video queries
- Keywords: 'video', 'movie', 'clip', 'footage', 'tutorial'

## UI Updates

### Bulk Selection Toolbar
```html
<div class="bulk-selection-toolbar" id="bulkSelectionToolbar">
    <div class="selection-info">
        <i class="fas fa-check-circle"></i>
        <span id="selectedCount">0</span> selected
    </div>
    <div class="bulk-actions">
        <button onclick="downloadSelected()">Download</button>
        <button onclick="moveSelected()">Move</button>
        <button onclick="deleteSelected()">Delete</button>
        <button onclick="clearSelection()">Clear</button>
    </div>
</div>
```

### Asset Selection Updates
- Checkboxes now track asset IDs instead of file paths
- Selected assets stored in Set for efficient operations
- Visual feedback with `.selected` class

## API Changes

### New Endpoints

1. **Bulk Delete Assets**
   - `POST /api/assets/bulk-delete`
   - Body: `{ "asset_ids": [1, 2, 3] }`
   - Response: `{ "success": true, "deleted_count": 3 }`

2. **Bulk Move Assets**
   - `POST /api/assets/bulk-move`
   - Body: `{ "asset_ids": [1, 2, 3], "container": "vacation" }`
   - Response: `{ "success": true, "moved_count": 3 }`

3. **Get User Containers**
   - `GET /api/containers`
   - Response: `{ "success": true, "containers": ["default", "vacation", "work"] }`

## Database Changes

### Asset Model
- Assets now support container metadata
- Container stored in asset metadata JSON field

### MediaBlob Handling
- Proper cascade delete when asset is deleted
- No orphaned blobs left in database

## Video Download Improvements

### Detection Logic
- Enhanced file type detection using content-type headers
- Fallback to URL extension checking
- Video extensions: `.mp4`, `.webm`, `.avi`, `.mov`

### Progress Tracking
- Video downloads properly tracked in statistics
- Separate image/video counters
- Real-time progress updates

### Platform Support
- YouTube (via yt-dlp)
- Vimeo
- Internet Archive
- Standard video URLs (direct MP4, WebM, etc.)

## Testing

### Test Bulk Operations
1. Select multiple assets using checkboxes
2. Use "Select All" checkbox to select all visible assets
3. Click "Delete" to bulk delete selected assets
4. Click "Move" to move assets to a different container

### Test Video Downloads
1. Search for "tutorial video" or similar video query
2. System should detect video search and use video sources
3. Videos should download and display with proper thumbnails
4. Video duration should be shown in asset cards

## Known Limitations

1. Video downloads limited to 720p and 100MB for performance
2. Some video platforms may require authentication
3. Container feature currently text-based (no folder UI yet)

## Future Enhancements

1. Visual folder/container browser
2. Drag-and-drop for moving assets
3. Batch operations progress bar
4. Video streaming instead of download
5. Container-based permissions 
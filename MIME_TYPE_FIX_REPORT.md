# MIME Type Fix Report

## Issue Summary

**Problem**: Downloaded assets were opening as binary data instead of displaying as viewable images/videos in browsers.

**Date**: October 2, 2025
**Status**: RESOLVED

---

## Root Cause Analysis

### Investigation Steps

1. **Database Inspection** (`check_assets_db.py`)
   - Found 30 assets in database, all stored in MediaBlob
   - All assets had `mime_type: 'image'` instead of proper MIME types like `'image/jpeg'`
   - Files were JPEG images (verified by file signatures: `ffd8ffe1...`)

2. **Endpoint Testing** (`test_asset_serving.py`)
   - Serving endpoints returned `Content-Type: image` (invalid MIME type)
   - Browser sees invalid MIME type and downloads as binary instead of displaying

3. **Code Trace**
   - `enhanced_working_downloader.py` calls `add_asset(..., file_type='image', ...)`
   - `db_asset_manager.py` line 32 assigns `content_type = file_type` (sets 'image')
   - `db_asset_manager.py` line 77 creates MediaBlob with `mime_type=content_type` (stores 'image')
   - `blueprints/assets.py` line 249 serves file with `mimetype=media_blob.mime_type` (returns 'image')
   - Browser receives invalid `Content-Type: image` and downloads as binary

### Bug Flow Diagram

```
enhanced_working_downloader.py
  ↓
add_asset(file_type='image')  # Generic category, not MIME type
  ↓
db_asset_manager.py line 32: content_type = file_type  # BUG: assigns 'image'
  ↓
db_asset_manager.py line 77: MediaBlob(mime_type=content_type)  # Stores 'image'
  ↓
blueprints/assets.py line 249: Response(mimetype=media_blob.mime_type)
  ↓
Browser sees: Content-Type: image  # Invalid MIME type
  ↓
Browser downloads as binary (doesn't know how to display 'image' without subtype)
```

---

## Solution

### Code Changes

**File**: `C:\inetpub\wwwroot\scraper\db_asset_manager.py`

#### Change 1: `add_asset()` function (lines 31-58)

**Before**:
```python
# Determine content type
content_type = file_type  # <-- BUG: Used generic 'image' or 'video'
if not content_type or content_type == 'unknown':
    content_type, _ = mimetypes.guess_type(filename)
if not content_type:
    content_type = 'application/octet-stream'
```

**After**:
```python
# Determine content type - ALWAYS detect from file, not from generic file_type parameter
content_type = None

# First try to guess from filename extension
if filename:
    content_type, _ = mimetypes.guess_type(filename)

# If that fails, detect from file signature (magic bytes)
if not content_type and file_data and len(file_data) >= 12:
    # Check common image/video signatures
    if file_data.startswith(b'\xff\xd8\xff'):
        content_type = 'image/jpeg'
    elif file_data.startswith(b'\x89PNG\r\n\x1a\n'):
        content_type = 'image/png'
    elif file_data.startswith(b'GIF87a') or file_data.startswith(b'GIF89a'):
        content_type = 'image/gif'
    elif file_data.startswith(b'RIFF') and file_data[8:12] == b'WEBP':
        content_type = 'image/webp'
    elif file_data.startswith(b'BM'):
        content_type = 'image/bmp'
    elif file_data[4:12] == b'ftypmp42' or file_data[4:12] == b'ftypisom':
        content_type = 'video/mp4'
    elif file_data.startswith(b'\x1a\x45\xdf\xa3'):
        content_type = 'video/webm'

# Last resort: use generic type
if not content_type:
    content_type = 'application/octet-stream'
```

#### Change 2: `save_asset()` function (lines 334-363)

Applied the same fix to ensure all code paths properly detect MIME types.

### Database Migration Script

**File**: `C:\inetpub\wwwroot\scraper\fix_existing_mime_types.py`

- Fixed all 30 existing MediaBlob records
- Changed `mime_type: 'image'` → `'image/jpeg'` (detected from file signatures)
- All records updated successfully

---

## Testing Results

### Test 1: Existing Assets (`test_asset_serving.py`)

**Before Fix**:
```
Content-Type: image
Browser behavior: Downloads as binary
```

**After Fix**:
```
Content-Type: image/jpeg
Browser behavior: Displays image correctly
Status: SUCCESS
```

### Test 2: New Downloads (`test_new_download_mime.py`)

**Test Case**: File without extension (like `600_43`)

**Result**:
```
Input: file_type='image' (generic)
Detection: Magic bytes analyzed → JPEG signature found
MediaBlob mime_type: 'image/jpeg'
Status: SUCCESS
```

### Test 3: Database Verification (`check_mime_types_db.py`)

**Before Fix**:
```
30 assets with mime_type: 'image'
0 assets with valid MIME types
```

**After Fix**:
```
0 assets with invalid MIME types
30 assets with mime_type: 'image/jpeg'
```

---

## Impact Assessment

### Files Modified
1. `C:\inetpub\wwwroot\scraper\db_asset_manager.py` (2 functions)
2. Database: 30 MediaBlob records updated

### Affected Functionality
- **Asset Serving**: All existing and new assets now serve with correct MIME types
- **Browser Display**: Images/videos now display inline instead of downloading as binary
- **API Responses**: `/serve/<id>` and `/api/media/<id>` now return proper Content-Type headers

### Backward Compatibility
- Fully backward compatible
- No changes to API interfaces or database schema
- Only internal logic improved

---

## Additional Observations

### Issue 2: No Job Progress Indicators on Dashboard

**Status**: Not addressed in this fix (separate issue)

**Note**: This is a frontend/UI issue, not related to asset serving. The job progress system works (verified during testing), but may not be displaying on the dashboard. Requires separate investigation of dashboard JavaScript and template rendering.

---

## Recommendations

1. **Add Unit Tests**: Create automated tests for MIME type detection
2. **Monitor Logs**: Watch for any assets with `application/octet-stream` MIME type (indicates detection failure)
3. **File Extensions**: Consider adding proper file extensions during download to avoid reliance on magic byte detection
4. **Dashboard Issue**: Investigate job progress display separately

---

## Files Changed Summary

```
Modified:
- C:\inetpub\wwwroot\scraper\db_asset_manager.py

Created (for testing/fixing):
- C:\inetpub\wwwroot\scraper\check_assets_db.py
- C:\inetpub\wwwroot\scraper\test_asset_serving.py
- C:\inetpub\wwwroot\scraper\test_mime_detection.py
- C:\inetpub\wwwroot\scraper\check_mime_types_db.py
- C:\inetpub\wwwroot\scraper\fix_existing_mime_types.py
- C:\inetpub\wwwroot\scraper\test_new_download_mime.py
- C:\inetpub\wwwroot\scraper\MIME_TYPE_FIX_REPORT.md
```

---

## Conclusion

**Root Cause**: Generic `file_type` parameter ('image') was being used as MIME type instead of specific types like 'image/jpeg'

**Solution**: Implement proper MIME type detection using:
1. Filename extension (mimetypes.guess_type)
2. File signature analysis (magic bytes)
3. Fallback to application/octet-stream

**Result**: All assets now serve with correct MIME types and display properly in browsers

**Status**: RESOLVED ✓

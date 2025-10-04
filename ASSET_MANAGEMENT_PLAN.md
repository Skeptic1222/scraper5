# Asset Management & Dashboard Fix Plan

**Date**: 2025-10-02
**Priority**: CRITICAL
**Status**: Planning Complete, Ready for Implementation

---

## 🔴 Critical Issues Identified

### Issue 1: Active Downloads Not Showing
**Problem**: Dashboard updates asset count but never shows "Active Downloads" section
**Symptoms**:
- Asset count increases (downloads working)
- No progress indicators visible
- No job queue display
- No download metrics

**Root Causes to Investigate**:
1. JavaScript not loading properly
2. Jobs API endpoint requires authentication (confirmed: returns "Login to view job history")
3. Frontend polling code may not be running
4. Dashboard template may not include the updated JavaScript
5. Browser cache may be serving old version

### Issue 2: No Thumbnails
**Problem**: Downloaded files have no thumbnails
**Symptoms**:
- Assets display as blank/placeholder
- Can't preview content
- User doesn't know if image or video

**Root Causes to Investigate**:
1. Thumbnail generation not triggered
2. MediaBlob thumbnail field empty
3. Thumbnail endpoint not working
4. Frontend not requesting thumbnails

### Issue 3: No File Type Indicators
**Problem**: Can't tell if files are images, videos, or other
**Symptoms**:
- No badges or icons
- All assets look the same
- User can't filter by type

**Root Causes**:
1. No visual file type indicators in UI
2. File type not displayed
3. No icon differentiation

### Issue 4: No Asset Selection/Delete
**Problem**: Can't select and delete assets
**Requirements**:
- Checkbox on top-right of each thumbnail
- "Select All" button
- "Delete Selected" button
- Bulk delete functionality

---

## 📋 Implementation Plan

### Phase 1: Debug Active Downloads (IMMEDIATE - 15 min)

**Tasks**:
1. ✅ Verify simple-dashboard.js has Active Downloads code (DONE - confirmed exists)
2. ✅ Test /api/jobs endpoint (DONE - requires auth)
3. ⚠️ Check if dashboard template loads simple-dashboard.js
4. ⚠️ Check browser console for JavaScript errors
5. ⚠️ Verify authentication state in frontend
6. ⚠️ Test with authenticated user session

**Expected Fixes**:
- Add authentication to jobs polling
- Fix JavaScript loading order
- Clear browser cache
- Update template to load JS

**Files to Check**:
- `templates/dashboard.html` or `templates/index_simple.html`
- `static/js/simple-dashboard.js`
- `blueprints/jobs.py` (authentication requirement)

---

### Phase 2: Fix Thumbnail Generation (HIGH - 30 min)

**Tasks**:
1. Check if thumbnail generation runs on asset creation
2. Verify MediaBlob has thumbnail data
3. Test thumbnail endpoint `/api/media/<id>/thumbnail`
4. Add thumbnail generation if missing
5. Regenerate thumbnails for existing assets

**Implementation**:

**File**: `db_asset_manager.py` - Add to `add_asset()` and `save_asset()`
```python
def generate_thumbnail(filepath, max_size=(200, 200)):
    """Generate thumbnail from image or video"""
    from PIL import Image
    import io

    try:
        if filepath.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            # Image thumbnail
            with Image.open(filepath) as img:
                img.thumbnail(max_size, Image.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return buffer.getvalue()
        elif filepath.lower().endswith(('.mp4', '.webm', '.avi', '.mov')):
            # Video thumbnail - extract first frame
            import cv2
            cap = cv2.VideoCapture(filepath)
            ret, frame = cap.read()
            cap.release()
            if ret:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img.thumbnail(max_size, Image.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return buffer.getvalue()
    except Exception as e:
        print(f"Thumbnail generation failed: {e}")
    return None
```

**Files to Modify**:
- `db_asset_manager.py` (add thumbnail generation)
- Create `regenerate_thumbnails.py` (batch regeneration script)

---

### Phase 3: Add File Type Indicators (MEDIUM - 20 min)

**Tasks**:
1. Add file type badges to asset cards
2. Show icons for image/video/other
3. Color code by type (blue=image, green=video, gray=other)
4. Display file extension

**Implementation**:

**File**: Asset template (wherever assets are displayed)
```html
<div class="asset-card">
    <!-- File type badge -->
    <div class="file-type-badge" data-type="${asset.file_type}">
        <i class="fas fa-${asset.file_type === 'image' ? 'image' : 'video'}"></i>
        ${asset.file_type.toUpperCase()}
    </div>

    <!-- Thumbnail -->
    <img src="/scraper/api/media/${asset.id}/thumbnail" alt="Asset">

    <!-- File info -->
    <div class="file-info">
        <span class="file-ext">.${asset.filepath.split('.').pop()}</span>
        <span class="file-size">${formatFileSize(asset.size)}</span>
    </div>
</div>
```

**CSS**:
```css
.file-type-badge {
    position: absolute;
    top: 8px;
    left: 8px;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    background: rgba(0, 0, 0, 0.7);
    color: white;
}

.file-type-badge[data-type="image"] {
    background: rgba(59, 130, 246, 0.9);
}

.file-type-badge[data-type="video"] {
    background: rgba(16, 185, 129, 0.9);
}
```

**Files to Modify**:
- `templates/assets.html` (or wherever assets are rendered)
- `static/css/` (add badge styles)

---

### Phase 4: Implement Asset Selection & Bulk Delete (HIGH - 45 min)

**Tasks**:
1. Add checkbox to top-right of each thumbnail
2. Add "Select All" button to toolbar
3. Add "Delete Selected" button
4. Implement bulk delete API endpoint
5. Add confirmation dialog
6. Update UI after deletion

**Implementation**:

**HTML Structure**:
```html
<!-- Toolbar -->
<div class="asset-toolbar">
    <button id="select-all-btn" class="btn btn-secondary">
        <i class="fas fa-check-square"></i> Select All
    </button>
    <button id="delete-selected-btn" class="btn btn-danger" style="display: none;">
        <i class="fas fa-trash"></i> Delete Selected (<span id="selected-count">0</span>)
    </button>
</div>

<!-- Asset Card -->
<div class="asset-card" data-asset-id="${asset.id}">
    <!-- Selection checkbox -->
    <input type="checkbox" class="asset-checkbox"
           style="position: absolute; top: 8px; right: 8px;
                  width: 20px; height: 20px; cursor: pointer;">

    <!-- Thumbnail -->
    <img src="/scraper/api/media/${asset.id}/thumbnail" alt="Asset">
</div>
```

**JavaScript**:
```javascript
// Selection tracking
let selectedAssets = new Set();

// Select/deselect asset
document.addEventListener('change', (e) => {
    if (e.target.classList.contains('asset-checkbox')) {
        const assetId = e.target.closest('.asset-card').dataset.assetId;
        if (e.target.checked) {
            selectedAssets.add(assetId);
        } else {
            selectedAssets.delete(assetId);
        }
        updateDeleteButton();
    }
});

// Select all
document.getElementById('select-all-btn').addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('.asset-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);

    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
        const assetId = cb.closest('.asset-card').dataset.assetId;
        if (cb.checked) {
            selectedAssets.add(assetId);
        } else {
            selectedAssets.delete(assetId);
        }
    });

    updateDeleteButton();
});

// Update delete button
function updateDeleteButton() {
    const deleteBtn = document.getElementById('delete-selected-btn');
    const countSpan = document.getElementById('selected-count');

    if (selectedAssets.size > 0) {
        deleteBtn.style.display = 'inline-flex';
        countSpan.textContent = selectedAssets.size;
    } else {
        deleteBtn.style.display = 'none';
    }
}

// Delete selected
document.getElementById('delete-selected-btn').addEventListener('click', async () => {
    if (selectedAssets.size === 0) return;

    const confirmed = confirm(
        `Are you sure you want to delete ${selectedAssets.size} asset(s)? This cannot be undone.`
    );

    if (!confirmed) return;

    try {
        const response = await fetch('/scraper/api/assets/bulk-delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ asset_ids: Array.from(selectedAssets) })
        });

        const result = await response.json();

        if (result.success) {
            // Remove deleted assets from DOM
            selectedAssets.forEach(id => {
                document.querySelector(`[data-asset-id="${id}"]`)?.remove();
            });

            selectedAssets.clear();
            updateDeleteButton();

            alert(`Successfully deleted ${result.deleted} asset(s)`);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Error deleting assets: ${error.message}`);
    }
});
```

**Backend API**:
```python
# File: blueprints/assets.py

@assets_bp.route('/api/assets/bulk-delete', methods=['POST'])
@login_required
def bulk_delete_assets():
    """Delete multiple assets at once"""
    try:
        data = request.get_json()
        asset_ids = data.get('asset_ids', [])

        if not asset_ids:
            return jsonify({'success': False, 'error': 'No assets selected'})

        deleted_count = 0

        for asset_id in asset_ids:
            asset = Asset.query.filter_by(
                id=asset_id,
                user_id=current_user.id
            ).first()

            if asset:
                # Delete file if exists
                if asset.filepath and os.path.exists(asset.filepath):
                    os.remove(asset.filepath)

                # Delete MediaBlob
                MediaBlob.query.filter_by(asset_id=asset.id).delete()

                # Delete Asset
                db.session.delete(asset)
                deleted_count += 1

        db.session.commit()

        return jsonify({
            'success': True,
            'deleted': deleted_count,
            'message': f'Deleted {deleted_count} asset(s)'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
```

**Files to Create/Modify**:
- `blueprints/assets.py` (add bulk_delete_assets endpoint)
- `templates/assets.html` (add checkboxes and buttons)
- `static/js/asset-manager.js` (new file for asset management)
- `static/css/assets.css` (checkbox styles)

---

### Phase 5: Testing & Verification (15 min)

**Test Checklist**:

**Active Downloads**:
- [ ] Start a download job
- [ ] Open dashboard
- [ ] Verify "Active Downloads" section appears
- [ ] Verify progress bar animates
- [ ] Verify file counts update

**Thumbnails**:
- [ ] Download new assets
- [ ] Verify thumbnails generate
- [ ] Check existing assets have thumbnails
- [ ] Test video thumbnail generation

**File Type Indicators**:
- [ ] Verify image badge shows (blue)
- [ ] Verify video badge shows (green)
- [ ] Verify file extension displays
- [ ] Verify icons appear

**Selection & Delete**:
- [ ] Click checkbox on asset
- [ ] Verify "Delete Selected" button appears
- [ ] Click "Select All"
- [ ] Verify all checkboxes checked
- [ ] Click "Delete Selected"
- [ ] Verify confirmation dialog
- [ ] Confirm deletion
- [ ] Verify assets removed from UI
- [ ] Verify files deleted from disk

---

## 🛠️ Quick Fixes (Immediate Actions)

### Fix 1: Force JavaScript Reload
```bash
# Clear browser cache
Ctrl + Shift + Delete (Chrome/Edge)

# Hard refresh
Ctrl + F5 (Windows)
Cmd + Shift + R (Mac)
```

### Fix 2: Verify Dashboard Template
```bash
# Find dashboard template
grep -r "simple-dashboard.js" templates/

# Ensure script tag exists:
<script src="{{ url_for('static', filename='js/simple-dashboard.js') }}"></script>
```

### Fix 3: Check Job Status Endpoint
```bash
# Test while logged in (copy session cookie from browser)
curl -H "Cookie: session=..." http://localhost:5050/scraper/api/jobs?status=running
```

---

## 📦 Deliverables

### Scripts to Create:
1. `fix_dashboard_polling.py` - Debug and fix polling issues
2. `regenerate_thumbnails.py` - Batch thumbnail generation
3. `test_asset_selection.html` - Test selection UI

### Files to Modify:
1. `blueprints/assets.py` - Add bulk delete endpoint
2. `db_asset_manager.py` - Add thumbnail generation
3. `templates/assets.html` - Add selection UI
4. `static/js/asset-manager.js` - Asset management logic
5. `static/css/assets.css` - Selection styles

### Documentation:
1. `ASSET_MANAGEMENT_IMPLEMENTATION.md` - Complete guide
2. `THUMBNAIL_GENERATION_GUIDE.md` - Thumbnail setup
3. `BULK_DELETE_API.md` - API documentation

---

## ⏱️ Time Estimates

- Phase 1 (Debug Active Downloads): 15 minutes
- Phase 2 (Thumbnail Generation): 30 minutes
- Phase 3 (File Type Indicators): 20 minutes
- Phase 4 (Selection & Delete): 45 minutes
- Phase 5 (Testing): 15 minutes

**Total**: ~2 hours

---

## 🎯 Success Criteria

**Active Downloads**:
- ✓ Section appears when jobs running
- ✓ Progress updates in real-time
- ✓ Shows file counts and percentages

**Thumbnails**:
- ✓ All assets have thumbnails
- ✓ Images show preview
- ✓ Videos show first frame

**File Types**:
- ✓ Visual badges for image/video
- ✓ File extension visible
- ✓ Color-coded by type

**Asset Management**:
- ✓ Checkbox on each asset
- ✓ Select All works
- ✓ Bulk delete functional
- ✓ Confirmation dialog shows
- ✓ UI updates after delete
- ✓ Files deleted from disk

---

**Prepared by**: CC-Supercharge Orchestrator
**Status**: Ready for Implementation
**Next Action**: Begin Phase 1 - Debug Active Downloads

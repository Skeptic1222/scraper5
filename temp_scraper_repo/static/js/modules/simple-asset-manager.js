/**
 * Simplified Asset Manager - Fixes Video Crash Issues
 * Simple, robust asset management without complex video hover functionality
 */

class SimpleAssetManager {
    constructor(app) {
        this.app = app;
        this.assets = [];
        this.filteredAssets = [];
        this.selectedAssets = new Set();
        this.currentFilter = 'all';
        this.isLoading = false;
        
        console.log('🎬 Simple Asset Manager: Initializing...');
        this.init();
    }

    async init() {
        // Wait for DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupAndLoad());
        } else {
            this.setupAndLoad();
        }
    }

    async setupAndLoad() {
        this.setupEventListeners();
        await this.loadAssets();
        console.log('✅ Simple Asset Manager: Ready');
    }

    setupEventListeners() {
        // Filter buttons
        document.querySelectorAll('input[name="asset-filter"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.setFilter(e.target.value);
            });
        });

        // Refresh button
        const refreshBtn = document.getElementById('refresh-assets-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadAssets());
        }

        // Master select checkbox
        const selectAllCheckbox = document.getElementById('select-all-assets');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }

        // Bulk delete selected
        const deleteSelectedBtn = document.getElementById('delete-selected-btn');
        if (deleteSelectedBtn) {
            deleteSelectedBtn.addEventListener('click', () => this.bulkDeleteSelected());
        }

        // Cleanup missing assets (admin only)
        const cleanupBtn = document.getElementById('cleanup-assets-btn');
        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', () => this.cleanupMissingAssets());
        }

        // Delete all (current filtered)
        const deleteAllBtn = document.getElementById('delete-all-btn');
        if (deleteAllBtn) {
            deleteAllBtn.addEventListener('click', () => this.bulkDeleteAllFiltered());
        }
    }

    async loadAssets() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoading();

        // Safety timeout to prevent perpetual loading UI
        const safetyTimer = setTimeout(() => {
            if (this.isLoading) {
                console.warn('assets: safety timeout triggered, showing error');
                this.showError('Taking longer than expected...');
                this.isLoading = false;
            }
        }, 8000);

        try {
            console.log('🔄 Loading assets...');
            
            const assetsUrl = `${window.APP_BASE || ''}/api/assets`;
            const response = await fetch(assetsUrl);
            const data = await response.json();
            
            if (data.success) {
                this.assets = this.processAssets(data.assets || data.data || []);
                console.log(`✅ Loaded ${this.assets.length} assets`);
                
                this.applyCurrentFilter();
                this.updateCounts();
                this.renderAssets();
                return true;
            } else {
                throw new Error(data.error || 'Failed to load assets');
            }
        } catch (error) {
            console.error('❌ Error loading assets:', error);
            this.showError(error.message);
            return false;
        } finally {
            this.isLoading = false;
            clearTimeout(safetyTimer);
        }
    }

    processAssets(rawAssets) {
        return rawAssets.map((asset, index) => {
            const filename = asset.filename || asset.name || `Asset ${index + 1}`;
            const fileType = this.detectFileType(filename);
            
            return {
                id: asset.id || `asset_${index}`,
                filename: filename,
                file_type: fileType,
                source: asset.source || 'Unknown',
                file_size: asset.file_size || 0,
                created_at: asset.created_at || new Date().toISOString(),
                
                // Computed properties
                isImage: fileType === 'image',
                isVideo: fileType === 'video',
                formattedSize: this.formatFileSize(asset.file_size || 0),
                formattedDate: this.formatDate(asset.created_at),
                
                // URLs - safer approach
                viewUrl: `/api/media/${asset.id}`,
                downloadUrl: `/api/media/${asset.id}/download`,
                thumbnailUrl: asset.thumbnail_path || `/api/media/${asset.id}/thumbnail`,
                
                _raw: asset
            };
        });
    }

    detectFileType(filename) {
        const extension = filename.split('.').pop()?.toLowerCase() || '';
        
        if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(extension)) {
            return 'image';
        } else if (['mp4', 'avi', 'mov', 'webm', 'mkv'].includes(extension)) {
            return 'video';
        }
        
        return 'unknown';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) return 'Today';
        if (diffDays === 2) return 'Yesterday';
        if (diffDays <= 7) return `${diffDays} days ago`;
        
        return date.toLocaleDateString();
    }

    applyCurrentFilter() {
        switch (this.currentFilter) {
            case 'images':
                this.filteredAssets = this.assets.filter(asset => asset.isImage);
                break;
            case 'videos':
                this.filteredAssets = this.assets.filter(asset => asset.isVideo);
                break;
            default:
                this.filteredAssets = [...this.assets];
        }
        
        console.log(`📊 Filtered: ${this.filteredAssets.length}/${this.assets.length} assets (${this.currentFilter})`);
    }

    setFilter(filter) {
        this.currentFilter = filter;
        this.applyCurrentFilter();
        this.updateCounts();
        this.renderAssets();
    }

    // Compatibility method for app.js
    applyFilter(filter = null) {
        if (filter) {
            this.currentFilter = filter;
        }
        console.log('🔍 applyFilter called with:', this.currentFilter);
        
        // Ensure we have assets to filter
        if (!this.assets || !Array.isArray(this.assets)) {
            console.warn('⚠️ applyFilter: No assets to filter');
            this.filteredAssets = [];
            return;
        }
        
        this.applyCurrentFilter();
        this.updateCounts();
        this.renderAssets();
    }

    // Compatibility method
    filterAssets(filter) {
        this.setFilter(filter);
    }

    // Compatibility method for app.js error handling
    showEmptyState(message = 'No assets found') {
        console.log('📭 showEmptyState called with message:', message);
        const grid = document.getElementById('assets-grid');
        if (grid) {
            grid.innerHTML = `
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">${message}</h5>
                        <p class="text-muted">Try refreshing or check your connection.</p>
                        <button class="btn btn-outline-primary" onclick="window.mediaScraperApp?.modules?.assetManager?.loadAssets?.()">
                            <i class="fas fa-sync"></i> Refresh Assets
                        </button>
                    </div>
                </div>
            `;
        }
    }

    updateCounts() {
        const counts = {
            all: this.assets.length,
            images: this.assets.filter(asset => asset.isImage).length,
            videos: this.assets.filter(asset => asset.isVideo).length
        };

        // Update UI counts
        Object.entries(counts).forEach(([type, count]) => {
            const element = document.getElementById(`count-${type}`);
            if (element) {
                element.textContent = count;
            }
        });

        console.log('📊 Asset counts:', counts);
    }

    renderAssets() {
        console.log('🎨 Rendering assets...');
        
        const grid = document.getElementById('assets-grid');
        if (!grid) {
            console.error('❌ Assets grid not found');
            return;
        }

        this.hideAllStates();

        if (this.isLoading) {
            this.showLoading();
            return;
        }

        if (this.filteredAssets.length === 0) {
            this.showEmpty();
            return;
        }

        try {
            // Clear grid and set proper CSS classes
            grid.innerHTML = '';
            grid.className = 'assets-grid view-medium'; // Use the proper CSS class structure
            
            // Create asset cards - simplified approach
            const fragment = document.createDocumentFragment();
            
            this.filteredAssets.forEach((asset, index) => {
                try {
                    const card = this.createSimpleAssetCard(asset, index);
                    if (card) {
                        fragment.appendChild(card);
                    }
                } catch (error) {
                    console.warn('⚠️ Error creating card for asset:', asset.filename, error);
                }
            });
            
            grid.appendChild(fragment);
            grid.style.display = 'grid';
            
            console.log(`✅ Rendered ${this.filteredAssets.length} assets in grid layout`);
            
        } catch (error) {
            console.error('❌ Critical error during rendering:', error);
            this.showError('Failed to render assets');
        }
    }

    createSimpleAssetCard(asset, index) {
        const card = document.createElement('div');
        card.className = 'asset-card';
        card.dataset.assetId = asset.id;
        
        const isSelected = this.selectedAssets.has(asset.id);
        if (isSelected) {
            card.classList.add('selected');
        }

        // Use the exact structure expected by the latest CSS at the end of asset-grid.css
        card.innerHTML = `
            <div class="asset-media">
                ${this.createAssetThumbnail(asset)}
                <input type="checkbox" 
                       class="asset-checkbox" 
                       data-asset-id="${asset.id}" 
                       ${isSelected ? 'checked' : ''}>
                <div class="asset-type-badge ${asset.isImage ? 'image' : 'video'}">
                    <i class="fas fa-${asset.isImage ? 'image' : 'video'}"></i>
                </div>
                <div class="asset-overlay">
                    <div class="asset-actions">
                        <button class="btn btn-sm btn-light" onclick="simpleAssetManager.viewAsset('${asset.id}')" type="button">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-success" onclick="simpleAssetManager.downloadAsset('${asset.id}')" type="button">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
            </div>
            <div class="asset-info">
                <div class="asset-filename" title="${asset.filename}">${this.truncateFilename(asset.filename)}</div>
                <div class="asset-meta">
                    <span class="asset-source">${asset.source}</span>
                    <span class="asset-size">${asset.formattedSize}</span>
                </div>
                <div class="asset-date">${asset.formattedDate}</div>
            </div>
        `;

        // Wire checkbox selection
        const checkbox = card.querySelector('.asset-checkbox');
        if (checkbox) {
            checkbox.addEventListener('change', (e) => {
                const id = asset.id;
                if (e.target.checked) {
                    this.selectAsset(id);
                } else {
                    this.deselectAsset(id);
                }
                this.updateBulkActionUI();
            });
        }

        // Add simple event listeners
        this.addSimpleEventListeners(card, asset);

        return card;
    }

    createAssetThumbnail(asset) {
        if (asset.isImage) {
            return `
                <img src="${asset.thumbnailUrl}" 
                     alt="${asset.filename}" 
                     class="asset-thumbnail"
                     loading="lazy"
                     onerror="this.src='/static/images/image-placeholder.png'">
            `;
        } else if (asset.isVideo) {
            return `
                <img src="${asset.thumbnailUrl}" 
                     alt="${asset.filename}" 
                     class="asset-thumbnail"
                     loading="lazy"
                     onerror="this.src='/static/images/video-placeholder.png'">
                <div class="video-indicator">
                    <i class="fas fa-play"></i>
                </div>
            `;
        } else {
            return `
                <div class="asset-placeholder">
                    <i class="fas fa-file"></i>
                    <span>Unknown</span>
                </div>
            `;
        }
    }

    truncateFilename(filename, maxLength = 25) {
        if (filename.length <= maxLength) return filename;
        const extension = filename.split('.').pop();
        const nameWithoutExt = filename.substring(0, filename.lastIndexOf('.'));
        const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 4) + '...';
        return truncatedName + '.' + extension;
    }

    addSimpleEventListeners(card, asset) {
        // Click to view (not on checkbox)
        card.addEventListener('click', (e) => {
            if (!e.target.closest('.asset-checkbox')) {
                this.viewAsset(asset);
            }
        });

        // Checkbox handling
        const checkbox = card.querySelector('.asset-checkbox');
        if (checkbox) {
            checkbox.addEventListener('change', (e) => {
                e.stopPropagation();
                if (e.target.checked) {
                    this.selectAsset(asset.id);
                } else {
                    this.deselectAsset(asset.id);
                }
            });
        }
    }

    viewAsset(assetIdOrAsset) {
        const asset = typeof assetIdOrAsset === 'string' 
            ? this.assets.find(a => a.id === assetIdOrAsset)
            : assetIdOrAsset;
            
        if (!asset) {
            console.error('Asset not found:', assetIdOrAsset);
            return;
        }
        
        console.log('👁️ Viewing asset:', asset.filename);

        // Create simple modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-${asset.isImage ? 'image' : 'video'}"></i>
                            ${asset.filename}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        ${asset.isImage ? 
                            `<img src="${asset.viewUrl}" class="img-fluid" alt="${asset.filename}" style="max-height: 70vh;">` :
                            `<video controls class="img-fluid" style="max-height: 70vh;">
                                <source src="${asset.viewUrl}" type="video/mp4">
                                Your browser does not support video.
                            </video>`
                        }
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-success" onclick="simpleAssetManager.downloadAsset('${asset.id}')">
                            <i class="fas fa-download"></i> Download
                        </button>
                        <button class="btn btn-danger" onclick="simpleAssetManager.deleteAsset('${asset.id}'); bootstrap.Modal.getInstance(this.closest('.modal')).hide();">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Cleanup
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    async downloadAsset(assetId) {
        const asset = this.assets.find(a => a.id === assetId);
        if (!asset) return;

        try {
            const response = await fetch(asset.downloadUrl);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = asset.filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                if (this.app?.showSuccess) {
                    this.app.showSuccess(`Downloaded: ${asset.filename}`);
                }
            }
        } catch (error) {
            console.error('Download error:', error);
            if (this.app?.showError) {
                this.app.showError(`Failed to download: ${asset.filename}`);
            }
        }
    }

    async deleteAsset(assetId) {
        const asset = this.assets.find(a => a.id === assetId);
        if (!asset) return;

        if (!confirm(`Delete "${asset.filename}"?`)) return;

        try {
            const deleteUrl = `${window.APP_BASE || ''}/api/assets/${assetId}`;
            const response = await fetch(deleteUrl, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.removeAssetFromState(assetId);
                if (this.app?.showSuccess) {
                    this.app.showSuccess(`Deleted: ${asset.filename}`);
                }
            }
        } catch (error) {
            console.error('Delete error:', error);
            if (this.app?.showError) {
                this.app.showError(`Failed to delete: ${asset.filename}`);
            }
        }
    }

    selectAsset(assetId) {
        this.selectedAssets.add(assetId);
        const card = document.querySelector(`[data-asset-id="${assetId}"]`);
        if (card) {
            card.classList.add('selected');
            const checkbox = card.querySelector('.asset-checkbox');
            if (checkbox) checkbox.checked = true;
        }
        this.updateBulkActionUI();
    }

    deselectAsset(assetId) {
        this.selectedAssets.delete(assetId);
        const card = document.querySelector(`[data-asset-id="${assetId}"]`);
        if (card) {
            card.classList.remove('selected');
            const checkbox = card.querySelector('.asset-checkbox');
            if (checkbox) checkbox.checked = false;
        }
        this.updateBulkActionUI();
    }

    toggleSelectAll(selectAll) {
        this.filteredAssets.forEach(asset => {
            if (selectAll) {
                this.selectAsset(asset.id);
            } else {
                this.deselectAsset(asset.id);
            }
        });
        this.updateBulkActionUI();
    }

    removeAssetFromState(assetId) {
        this.assets = this.assets.filter(asset => asset.id !== assetId);
        this.selectedAssets.delete(assetId);
        this.applyCurrentFilter();
        this.updateCounts();
        this.renderAssets();
    }

    showLoading() {
        this.showState('assets-loading');
    }

    showError(message) {
        this.showState('assets-error');
        const messageEl = document.getElementById('error-message');
        if (messageEl) messageEl.textContent = message;
    }

    showEmpty() {
        this.showState('assets-empty');
    }

    showState(activeStateId) {
        const states = ['assets-loading', 'assets-error', 'assets-empty'];
        const grid = document.getElementById('assets-grid');
        
        states.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.style.display = id === activeStateId ? 'block' : 'none';
            }
        });
        
        if (grid) {
            grid.style.display = activeStateId ? 'none' : 'grid';
        }
    }

    hideAllStates() {
        this.showState(null);
    }

    updateBulkActionUI() {
        const deleteBtn = document.getElementById('delete-selected-btn');
        const countSpan = document.getElementById('delete-selected-count');
        const selectedCount = this.selectedAssets.size;
        if (deleteBtn) {
            deleteBtn.style.display = selectedCount > 0 ? 'inline-block' : 'none';
        }
        if (countSpan) {
            countSpan.textContent = String(selectedCount);
        }
    }

    async bulkDeleteSelected() {
        if (this.selectedAssets.size === 0) return;
        if (!confirm(`Delete ${this.selectedAssets.size} selected item(s)?`)) return;
        try {
            const bulkDeleteUrl = `${window.APP_BASE || ''}/api/assets/bulk-delete`;
            const resp = await fetch(bulkDeleteUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: Array.from(this.selectedAssets) })
            });
            const data = await resp.json();
            if (!resp.ok || !data.success) throw new Error(data.error || 'Bulk delete failed');
            // Remove from state
            Array.from(this.selectedAssets).forEach(id => this.removeAssetFromState(id));
            this.selectedAssets.clear();
            this.updateBulkActionUI();
            if (this.app?.showSuccess) this.app.showSuccess(`Deleted ${data.deleted} assets`);
        } catch (e) {
            console.error('Bulk delete error:', e);
            if (this.app?.showError) this.app.showError(e.message);
        }
    }

    async bulkDeleteAllFiltered() {
        if (this.filteredAssets.length === 0) return;
        if (!confirm(`Delete ALL ${this.filteredAssets.length} ${this.currentFilter} asset(s) currently listed?`)) return;
        try {
            const ids = this.filteredAssets.map(a => a.id);
            const bulkDeleteUrl = `${window.APP_BASE || ''}/api/assets/bulk-delete`;
            const resp = await fetch(bulkDeleteUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids })
            });
            const data = await resp.json();
            if (!resp.ok || !data.success) throw new Error(data.error || 'Bulk delete failed');
            await this.loadAssets();
            if (this.app?.showSuccess) this.app.showSuccess(`Deleted ${data.deleted} assets`);
        } catch (e) {
            console.error('Bulk delete all error:', e);
            if (this.app?.showError) this.app.showError(e.message);
        }
    }

    async cleanupMissingAssets() {
        if (!confirm('Cleanup missing/broken assets? (Admin only)')) return;
        try {
            const cleanupUrl = `${window.APP_BASE || ''}/api/assets/cleanup-missing`;
            const resp = await fetch(cleanupUrl, { method: 'POST' });
            const data = await resp.json();
            if (resp.status === 403) {
                throw new Error('Admin access required to cleanup.');
            }
            if (!resp.ok || !data.success) throw new Error(data.error || 'Cleanup failed');
            await this.loadAssets();
            if (this.app?.showSuccess) this.app.showSuccess(`Cleaned up ${data.updated} assets`);
        } catch (e) {
            console.error('Cleanup error:', e);
            if (this.app?.showError) this.app.showError(e.message);
        }
    }
}

// Export for global use
window.SimpleAssetManager = SimpleAssetManager;
window.simpleAssetManager = null; // Will be initialized by main app

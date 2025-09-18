/**
 * Enhanced Asset Library with thumbnail and list views
 */
class AssetLibraryEnhanced {
    constructor() {
        this.assets = [];
        this.currentView = 'thumbnail';
        this.selectedAssets = new Set();
        
        this.init();
    }
    
    init() {
        this.setupViewSwitching();
        this.loadAssets();
        this.setupRefreshButton();
    }
    
    setupViewSwitching() {
        const viewButtons = document.querySelectorAll('[data-view]');
        viewButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.currentTarget.dataset.view;
                this.switchView(view);
                
                // Update active button
                viewButtons.forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
            });
        });
    }
    
    switchView(view) {
        this.currentView = view;
        const assetGrid = document.getElementById('asset-grid');
        
        if (view === 'thumbnail') {
            assetGrid.classList.remove('list-view');
            assetGrid.classList.add('thumbnail-view');
        } else {
            assetGrid.classList.remove('thumbnail-view');
            assetGrid.classList.add('list-view');
        }
        
        this.renderAssets();
    }
    
    setupRefreshButton() {
        const refreshBtn = document.getElementById('refresh-assets');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                refreshBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Refreshing...';
                this.loadAssets().finally(() => {
                    refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Refresh';
                });
            });
        }
    }
    
    async loadAssets() {
        try {
            const response = await fetch('/api/assets');
            const data = await response.json();
            
            this.assets = data.assets || [];
            this.renderAssets();
            
            // Update asset count in dashboard
            const totalAssetsElem = document.getElementById('total-assets');
            if (totalAssetsElem) {
                totalAssetsElem.textContent = this.assets.length;
            }
        } catch (error) {
            console.error('Failed to load assets:', error);
            this.showError('Failed to load assets');
        }
    }
    
    renderAssets() {
        const assetGrid = document.getElementById('asset-grid');
        if (!assetGrid) return;
        
        if (this.assets.length === 0) {
            assetGrid.innerHTML = `
                <div class="text-center text-muted p-5">
                    <i class="fas fa-folder-open fa-4x mb-3"></i>
                    <h4>No assets yet</h4>
                    <p>Start downloading content to build your library</p>
                </div>
            `;
            return;
        }
        
        if (this.currentView === 'thumbnail') {
            this.renderThumbnailView(assetGrid);
        } else {
            this.renderListView(assetGrid);
        }
    }
    
    renderThumbnailView(container) {
        container.innerHTML = `
            <div class="asset-grid-container">
                ${this.assets.map(asset => this.createThumbnailCard(asset)).join('')}
            </div>
        `;
        
        // Add click handlers
        this.attachAssetHandlers();
    }
    
    renderListView(container) {
        container.innerHTML = `
            <div class="asset-list-container">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="select-all-assets"></th>
                            <th>Thumbnail</th>
                            <th>Name</th>
                            <th>Source</th>
                            <th>Type</th>
                            <th>Size</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.assets.map(asset => this.createListRow(asset)).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        // Setup select all checkbox
        const selectAll = document.getElementById('select-all-assets');
        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                const checkboxes = document.querySelectorAll('.asset-checkbox');
                checkboxes.forEach(cb => {
                    cb.checked = e.target.checked;
                    if (e.target.checked) {
                        this.selectedAssets.add(cb.value);
                    } else {
                        this.selectedAssets.clear();
                    }
                });
                this.updateBulkActions();
            });
        }
        
        // Add handlers
        this.attachAssetHandlers();
    }
    
    createThumbnailCard(asset) {
        const thumbnail = this.getAssetThumbnail(asset);
        const fileName = asset.filename || 'Unknown';
        const source = asset.source || 'Unknown';
        
        return `
            <div class="asset-card" data-asset-id="${asset.id}">
                <div class="asset-checkbox-container">
                    <input type="checkbox" class="asset-checkbox" value="${asset.id}">
                </div>
                <div class="asset-thumbnail">
                    ${thumbnail}
                </div>
                <div class="asset-info">
                    <div class="asset-name" title="${fileName}">${this.truncate(fileName, 20)}</div>
                    <div class="asset-source">${source}</div>
                </div>
                <div class="asset-actions">
                    <button class="btn btn-sm btn-icon" onclick="assetLibrary.viewAsset('${asset.id}')" title="View">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-icon" onclick="assetLibrary.downloadAsset('${asset.id}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-icon text-danger" onclick="assetLibrary.deleteAsset('${asset.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }
    
    createListRow(asset) {
        const thumbnail = this.getAssetThumbnail(asset, 40);
        const fileName = asset.filename || 'Unknown';
        const source = asset.source || 'Unknown';
        const type = asset.content_type || 'Unknown';
        const size = this.formatSize(asset.file_size || 0);
        const date = this.formatDate(asset.created_at);
        
        return `
            <tr data-asset-id="${asset.id}">
                <td><input type="checkbox" class="asset-checkbox" value="${asset.id}"></td>
                <td class="asset-list-thumbnail">${thumbnail}</td>
                <td class="asset-name">${fileName}</td>
                <td>${source}</td>
                <td><span class="badge bg-secondary">${type}</span></td>
                <td>${size}</td>
                <td>${date}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="assetLibrary.viewAsset('${asset.id}')" title="View">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="assetLibrary.downloadAsset('${asset.id}')" title="Download">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="assetLibrary.deleteAsset('${asset.id}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }
    
    getAssetThumbnail(asset, size = 150) {
        if (asset.content_type === 'image') {
            // Use actual image URL if available
            const imageUrl = `/api/media/${asset.id}/thumbnail` || `/api/media/${asset.id}`;
            return `<img src="${imageUrl}" alt="${asset.filename}" style="width: ${size}px; height: ${size}px; object-fit: cover;">`;
        } else if (asset.content_type === 'video') {
            return `<div class="asset-icon" style="width: ${size}px; height: ${size}px;"><i class="fas fa-video fa-3x"></i></div>`;
        } else {
            return `<div class="asset-icon" style="width: ${size}px; height: ${size}px;"><i class="fas fa-file fa-3x"></i></div>`;
        }
    }
    
    attachAssetHandlers() {
        // Checkbox handlers
        document.querySelectorAll('.asset-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectedAssets.add(e.target.value);
                } else {
                    this.selectedAssets.delete(e.target.value);
                }
                this.updateBulkActions();
            });
        });
    }
    
    updateBulkActions() {
        // Show/hide bulk action buttons based on selection
        if (this.selectedAssets.size > 0) {
            // Could show bulk action toolbar here
            console.log(`${this.selectedAssets.size} assets selected`);
        }
    }
    
    async viewAsset(assetId) {
        // Open asset in modal or new tab
        window.open(`/api/media/${assetId}`, '_blank');
    }
    
    async downloadAsset(assetId) {
        window.location.href = `/api/media/${assetId}/download`;
    }
    
    async deleteAsset(assetId) {
        if (!confirm('Are you sure you want to delete this asset?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/assets/${assetId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.loadAssets();
                this.showSuccess('Asset deleted successfully');
            } else {
                throw new Error('Failed to delete asset');
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showError('Failed to delete asset');
        }
    }
    
    truncate(str, length) {
        return str.length > length ? str.substring(0, length) + '...' : str;
    }
    
    formatSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatDate(dateStr) {
        if (!dateStr) return 'Unknown';
        const date = new Date(dateStr);
        return date.toLocaleDateString();
    }
    
    showSuccess(message) {
        // Could show toast notification
        console.log('Success:', message);
    }
    
    showError(message) {
        // Could show toast notification
        console.error('Error:', message);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.assetLibrary = new AssetLibraryEnhanced();
});
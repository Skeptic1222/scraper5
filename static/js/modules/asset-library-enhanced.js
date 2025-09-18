/**
 * Enhanced Asset Library with square thumbnails, keyboard navigation, and video hover autoplay
 */
class AssetLibraryEnhanced {
    constructor() {
        this.assets = [];
        this.currentView = 'thumbnail';
        this.selectedAssets = new Set();
        this.focusedIndex = 0;
        this.hoveredVideo = null;
        
        this.init();
    }
    
    init() {
        this.setupViewSwitching();
        this.loadAssets();
        this.setupRefreshButton();
        this.setupKeyboardNavigation();
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
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Only handle navigation if we're in the asset library section
            const assetSection = document.getElementById('asset-library');
            if (!assetSection || !assetSection.classList.contains('active')) return;
            
            // Don't interfere with form inputs
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            // If media viewer is open, let it handle the keys
            if (window.mediaViewer && window.mediaViewer.isOpen) return;
            
            const handled = this.handleKeyNavigation(e);
            if (handled) {
                e.preventDefault();
            }
        });
    }
    
    handleKeyNavigation(e) {
        if (this.currentView !== 'thumbnail' || this.assets.length === 0) return false;
        
        const cols = Math.floor(document.getElementById('asset-grid').offsetWidth / 180); // Approximate column count
        let newIndex = this.focusedIndex;
        
        switch(e.key) {
            case 'ArrowLeft':
            case 'a':
            case 'A':
                newIndex = Math.max(0, this.focusedIndex - 1);
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                newIndex = Math.min(this.assets.length - 1, this.focusedIndex + 1);
                break;
            case 'ArrowUp':
            case 'w':
            case 'W':
                newIndex = Math.max(0, this.focusedIndex - cols);
                break;
            case 'ArrowDown':
            case 's':
            case 'S':
                newIndex = Math.min(this.assets.length - 1, this.focusedIndex + cols);
                break;
            case ' ':
            case 'Enter':
                this.openMediaViewer(this.focusedIndex);
                return true;
            default:
                return false;
        }
        
        if (newIndex !== this.focusedIndex) {
            this.focusedIndex = newIndex;
            this.updateFocus();
            return true;
        }
        
        return false;
    }
    
    updateFocus() {
        // Remove all previous focus
        document.querySelectorAll('.asset-card').forEach((card, index) => {
            card.classList.remove('focused');
            if (index === this.focusedIndex) {
                card.classList.add('focused');
                card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                
                // Autoplay video if focused element is a video
                this.autoplayFocusedVideo(card);
            }
        });
    }
    
    autoplayFocusedVideo(card) {
        // Stop any previously playing video
        this.stopAllVideos();
        
        const asset = this.assets[this.focusedIndex];
        const fileType = (asset.file_type || asset.type || '').toLowerCase();
        const isVideo = fileType.includes('video') || 
                       fileType.includes('mp4') || 
                       fileType.includes('webm');
        
        if (isVideo) {
            const videoPreview = card.querySelector('.video-preview');
            if (videoPreview) {
                const video = videoPreview.querySelector('video');
                if (video) {
                    video.play().catch(() => {
                        // Autoplay failed, likely due to browser restrictions
                    });
                }
            }
        }
    }
    
    stopAllVideos() {
        document.querySelectorAll('.asset-card video').forEach(video => {
            video.pause();
            video.currentTime = 0;
        });
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
            
            // Update stats in dashboard
            if (data.counts) {
                const imageCount = document.getElementById('image-count');
                const videoCount = document.getElementById('video-count');
                if (imageCount) imageCount.textContent = data.counts.images || 0;
                if (videoCount) videoCount.textContent = data.counts.videos || 0;
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
                <div class="empty-state">
                    <i class="fas fa-folder-open fa-4x"></i>
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
            <div class="asset-grid-container square-grid">
                ${this.assets.map((asset, index) => this.createSquareThumbnailCard(asset, index)).join('')}
            </div>
        `;
        
        // Add hover handlers for video autoplay
        this.attachThumbnailHandlers();
        
        // Set initial focus
        if (this.focusedIndex >= 0 && this.focusedIndex < this.assets.length) {
            this.updateFocus();
        }
    }
    
    createSquareThumbnailCard(asset, index) {
        const fileType = (asset.file_type || asset.type || '').toLowerCase();
        const isImage = fileType.includes('image') || 
                       fileType.includes('jpeg') || 
                       fileType.includes('jpg') || 
                       fileType.includes('png') || 
                       fileType.includes('gif');
        const isVideo = fileType.includes('video') || 
                       fileType.includes('mp4') || 
                       fileType.includes('webm');
        
        const mediaUrl = asset.url || `/serve/${asset.id}`;
        const fileName = asset.filename || 'Unknown';
        
        let thumbnailContent = '';
        
        if (isImage) {
            thumbnailContent = `
                <div class="thumbnail-media">
                    <img src="${mediaUrl}" alt="${fileName}" loading="lazy">
                </div>
            `;
        } else if (isVideo) {
            thumbnailContent = `
                <div class="thumbnail-media video-preview">
                    <video src="${mediaUrl}" muted loop preload="metadata"></video>
                    <div class="video-overlay">
                        <i class="fas fa-play-circle"></i>
                    </div>
                </div>
            `;
        } else {
            thumbnailContent = `
                <div class="thumbnail-media file-icon">
                    <i class="fas fa-file fa-3x"></i>
                </div>
            `;
        }
        
        return `
            <div class="asset-card square-card" data-asset-id="${asset.id}" data-index="${index}">
                <div class="asset-card-inner">
                    ${thumbnailContent}
                    <div class="asset-overlay">
                        <div class="asset-name" title="${fileName}">${this.truncate(fileName, 15)}</div>
                        <div class="asset-actions">
                            <button class="btn-icon" onclick="assetLibrary.openMediaViewer(${index})" title="View">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn-icon" onclick="assetLibrary.downloadAsset('${asset.id}')" title="Download">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    attachThumbnailHandlers() {
        const cards = document.querySelectorAll('.asset-card');
        
        cards.forEach((card, index) => {
            // Click to open viewer
            card.addEventListener('click', (e) => {
                if (!e.target.closest('.asset-actions')) {
                    this.openMediaViewer(index);
                }
            });
            
            // Hover for video autoplay
            card.addEventListener('mouseenter', () => {
                const video = card.querySelector('video');
                if (video) {
                    video.play().catch(() => {});
                }
            });
            
            card.addEventListener('mouseleave', () => {
                const video = card.querySelector('video');
                if (video) {
                    video.pause();
                    video.currentTime = 0;
                }
            });
        });
    }
    
    renderListView(container) {
        container.innerHTML = `
            <div class="asset-list-container">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th width="60">Preview</th>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Size</th>
                            <th>Date</th>
                            <th width="120">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.assets.map((asset, index) => this.createListRow(asset, index)).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        // Add click handlers for rows
        document.querySelectorAll('.asset-list-row').forEach((row, index) => {
            row.addEventListener('click', (e) => {
                if (!e.target.closest('.btn-group')) {
                    this.openMediaViewer(index);
                }
            });
        });
    }
    
    createListRow(asset, index) {
        const fileType = (asset.file_type || asset.type || '').toLowerCase();
        const isImage = fileType.includes('image') || fileType.includes('jpeg') || fileType.includes('jpg') || fileType.includes('png');
        const mediaUrl = asset.url || `/serve/${asset.id}`;
        const fileName = asset.filename || 'Unknown';
        const size = this.formatSize(asset.file_size || asset.size || 0);
        const date = this.formatDate(asset.created_at || asset.modified);
        
        let preview = '';
        if (isImage) {
            preview = `<img src="${mediaUrl}" class="list-thumbnail" alt="${fileName}">`;
        } else {
            preview = `<div class="list-thumbnail-icon"><i class="fas fa-file"></i></div>`;
        }
        
        return `
            <tr class="asset-list-row" data-index="${index}">
                <td>${preview}</td>
                <td>${fileName}</td>
                <td><span class="badge badge-secondary">${fileType}</span></td>
                <td>${size}</td>
                <td>${date}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-sm btn-outline-primary" onclick="assetLibrary.openMediaViewer(${index})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="assetLibrary.downloadAsset('${asset.id}')">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }
    
    openMediaViewer(index) {
        if (window.mediaViewer) {
            window.mediaViewer.open(this.assets, index);
        }
    }
    
    async downloadAsset(assetId) {
        const asset = this.assets.find(a => a.id == assetId);
        if (asset) {
            const downloadUrl = `/api/media/${assetId}/download`;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = asset.filename || 'download';
            link.click();
        }
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
    
    // Utility methods
    truncate(str, length) {
        return str.length > length ? str.substring(0, length) + '...' : str;
    }
    
    formatSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    formatDate(dateStr) {
        if (!dateStr) return 'Unknown';
        const date = new Date(dateStr);
        return date.toLocaleDateString();
    }
    
    showSuccess(message) {
        // You can implement toast notifications here
        console.log('Success:', message);
    }
    
    showError(message) {
        // You can implement toast notifications here
        console.error('Error:', message);
    }
}

// Initialize asset library
window.assetLibrary = new AssetLibraryEnhanced();
/**
 * Asset Library Manager
 * Handles asset display, management and interactions
 */
class AssetLibrary {
    constructor() {
        this.assets = [];
        this.currentFilter = 'all';
        this.init();
    }

    async init() {
        await this.loadAssets();
        this.setupEventListeners();
    }

    async loadAssets() {
        try {
            const response = await fetch('/api/assets');
            const data = await response.json();
            
            if (data.success && data.assets) {
                this.assets = data.assets;
                this.displayAssets();
                this.updateStats();
            } else if (data.assets) {
                // Handle if success field is missing but assets exist
                this.assets = data.assets;
                this.displayAssets();
                this.updateStats();
            }
        } catch (error) {
            console.error('Failed to load assets:', error);
            this.showEmptyState();
        }
    }

    displayAssets() {
        const container = document.getElementById('asset-grid');
        if (!container) return;

        if (this.assets.length === 0) {
            this.showEmptyState();
            return;
        }

        container.innerHTML = '';
        
        const grid = document.createElement('div');
        grid.className = 'row g-3';
        
        this.assets.forEach(asset => {
            const assetCard = this.createAssetCard(asset);
            grid.appendChild(assetCard);
        });
        
        container.appendChild(grid);
    }

    createAssetCard(asset) {
        const col = document.createElement('div');
        col.className = 'col-sm-6 col-md-4 col-lg-3';
        
        const card = document.createElement('div');
        card.className = 'asset-card';
        card.style.cssText = `
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            cursor: pointer;
        `;
        
        // Thumbnail or placeholder
        const thumbnail = document.createElement('div');
        thumbnail.style.cssText = `
            height: 200px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 3rem;
        `;
        
        if (asset.thumbnail_url) {
            const img = document.createElement('img');
            img.src = asset.thumbnail_url;
            img.style.cssText = 'width: 100%; height: 100%; object-fit: cover;';
            img.onerror = () => {
                img.remove();
                thumbnail.innerHTML = this.getAssetIcon(asset.content_type);
            };
            thumbnail.innerHTML = '';
            thumbnail.appendChild(img);
        } else if (asset.id) {
            // Try to use media endpoint for thumbnail
            const img = document.createElement('img');
            img.src = `/api/media/${asset.id}/thumbnail`;
            img.style.cssText = 'width: 100%; height: 100%; object-fit: cover;';
            img.onerror = () => {
                img.remove();
                thumbnail.innerHTML = this.getAssetIcon(asset.content_type);
            };
            thumbnail.innerHTML = '';
            thumbnail.appendChild(img);
        } else {
            thumbnail.innerHTML = this.getAssetIcon(asset.content_type);
        }
        
        // Asset info
        const info = document.createElement('div');
        info.style.cssText = 'padding: 15px;';
        
        const title = document.createElement('h6');
        title.style.cssText = 'margin: 0 0 5px 0; font-size: 0.9rem; color: #333;';
        title.textContent = asset.filename || asset.title || 'Untitled';
        
        const meta = document.createElement('div');
        meta.style.cssText = 'font-size: 0.8rem; color: #666;';

        // Build metadata HTML
        let metaHTML = `
            <div>${this.formatFileSize(asset.file_size || 0)}</div>
            <div>${this.formatDate(asset.created_at)}</div>
        `;

        // Add source label if available
        if (asset.source_name) {
            const sourceLabel = asset.source_url
                ? `<div style="margin-top: 4px;"><strong>Source:</strong> <a href="${asset.source_url}" target="_blank" style="color: #667eea; text-decoration: none;">${asset.source_name}</a></div>`
                : `<div style="margin-top: 4px;"><strong>Source:</strong> ${asset.source_name}</div>`;
            metaHTML += sourceLabel;
        }

        meta.innerHTML = metaHTML;
        
        // Action buttons
        const actions = document.createElement('div');
        actions.style.cssText = 'padding: 10px 15px; background: #f8f9fa; display: flex; gap: 10px;';
        
        const viewBtn = document.createElement('button');
        viewBtn.className = 'btn btn-sm btn-outline-primary';
        viewBtn.innerHTML = '<i class="fas fa-eye"></i>';
        viewBtn.onclick = (e) => {
            e.stopPropagation();
            this.viewAsset(asset);
        };
        
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'btn btn-sm btn-outline-success';
        downloadBtn.innerHTML = '<i class="fas fa-download"></i>';
        downloadBtn.onclick = (e) => {
            e.stopPropagation();
            this.downloadAsset(asset);
        };
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'btn btn-sm btn-outline-danger';
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            this.deleteAsset(asset);
        };
        
        actions.appendChild(viewBtn);
        actions.appendChild(downloadBtn);
        actions.appendChild(deleteBtn);
        
        info.appendChild(title);
        info.appendChild(meta);
        
        card.appendChild(thumbnail);
        card.appendChild(info);
        card.appendChild(actions);
        
        col.appendChild(card);
        
        // Add hover effect
        card.onmouseenter = () => card.style.transform = 'translateY(-5px)';
        card.onmouseleave = () => card.style.transform = 'translateY(0)';
        
        return col;
    }

    getAssetIcon(contentType) {
        if (!contentType) return '📁';
        
        if (contentType.includes('image')) return '🖼️';
        if (contentType.includes('video')) return '🎥';
        if (contentType.includes('audio')) return '🎵';
        if (contentType.includes('pdf')) return '📄';
        if (contentType.includes('text')) return '📝';
        
        return '📁';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown date';
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    showEmptyState() {
        const container = document.getElementById('asset-grid');
        if (!container) return;
        
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-folder-open fa-4x text-muted mb-3"></i>
                <h5>No Assets Yet</h5>
                <p class="text-muted">Start by searching and downloading content to build your library</p>
                <button class="btn btn-primary" onclick="document.querySelector('[data-section="search-section"]').click()">
                    <i class="fas fa-search"></i> Start Searching
                </button>
            </div>
        `;
    }

    async viewAsset(asset) {
        if (asset.id) {
            window.open(`/api/media/${asset.id}`, '_blank');
        }
    }

    async downloadAsset(asset) {
        if (asset.id) {
            const link = document.createElement('a');
            link.href = `/api/media/${asset.id}/download`;
            link.download = asset.filename || 'download';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    async deleteAsset(asset) {
        if (!confirm('Are you sure you want to delete this asset?')) return;
        
        try {
            const response = await fetch(`/api/assets/${asset.id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.loadAssets();
                this.showToast('Asset deleted successfully', 'success');
            }
        } catch (error) {
            console.error('Failed to delete asset:', error);
            this.showToast('Failed to delete asset', 'danger');
        }
    }

    updateStats() {
        const countElement = document.getElementById('total-assets');
        if (countElement) {
            countElement.textContent = this.assets.length;
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        toast.textContent = message;
        
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    setupEventListeners() {
        // Filter buttons
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.onclick = () => {
                this.currentFilter = btn.dataset.filter;
                this.displayAssets();
            };
        });
        
        // Refresh button
        const refreshBtn = document.getElementById('refresh-assets');
        if (refreshBtn) {
            refreshBtn.onclick = () => this.loadAssets();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.assetLibrary = new AssetLibrary();
});
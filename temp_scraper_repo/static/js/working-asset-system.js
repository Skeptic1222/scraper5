/**
 * Working Asset System - Simple and functional
 * Handles asset display, updates, and management
 */

(function() {
    'use strict';

    // Asset System Manager
    class WorkingAssetSystem {
        constructor() {
            this.assets = [];
            this.stats = {
                total: 0,
                images: 0,
                videos: 0,
                audio: 0
            };
            this.isLoading = false;
            this.autoRefreshInterval = null;
            
            // Initialize when DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
            } else {
                this.init();
            }
        }

        init() {
            console.log('🚀 Initializing Working Asset System');
            
            // Load assets immediately
            this.loadAssets();
            
            // Set up auto-refresh every 5 seconds
            this.autoRefreshInterval = setInterval(() => {
                this.loadAssets();
                this.updateStats();
            }, 5000);
            
            // Set up event listeners
            this.setupEventListeners();
        }

        setupEventListeners() {
            // Refresh button
            const refreshBtn = document.getElementById('refresh-assets-btn');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => this.loadAssets());
            }

            // Filter buttons
            document.querySelectorAll('[data-filter-type]').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const filterType = e.target.dataset.filterType;
                    this.filterAssets(filterType);
                });
            });
        }

        async loadAssets() {
            if (this.isLoading) return;
            
            this.isLoading = true;
            this.showLoadingState();
            
            try {
                // Use APP_BASE prefix for API call
                const apiUrl = `${window.APP_BASE || ''}/api/assets`;
                const response = await fetch(apiUrl, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                if (data.success || data.assets) {
                    this.assets = data.assets || [];
                    this.stats = data.statistics || this.calculateStats();
                    
                    console.log(`✅ Loaded ${this.assets.length} assets`);
                    
                    // Update display
                    this.renderAssets();
                    this.updateStats();
                    this.hideLoadingState();
                } else {
                    console.error('Failed to load assets:', data.error);
                    this.showError('Failed to load assets');
                }
            } catch (error) {
                console.error('Error loading assets:', error);
                this.showError('Error loading assets: ' + error.message);
            } finally {
                this.isLoading = false;
            }
        }

        calculateStats() {
            const stats = {
                total: this.assets.length,
                images: 0,
                videos: 0,
                audio: 0
            };
            
            this.assets.forEach(asset => {
                if (asset.file_type === 'image') stats.images++;
                else if (asset.file_type === 'video') stats.videos++;
                else if (asset.file_type === 'audio') stats.audio++;
            });
            
            return stats;
        }

        renderAssets() {
            const grid = document.getElementById('assets-grid');
            if (!grid) {
                console.warn('Assets grid not found');
                return;
            }
            
            // Clear existing content
            grid.innerHTML = '';
            
            if (this.assets.length === 0) {
                grid.innerHTML = `
                    <div class="no-assets-message">
                        <i class="fas fa-inbox fa-3x text-muted"></i>
                        <p class="mt-3">No assets found</p>
                        <p class="text-muted">Download some media to see it here</p>
                    </div>
                `;
                return;
            }
            
            // Render each asset
            this.assets.forEach(asset => {
                const card = this.createAssetCard(asset);
                grid.appendChild(card);
            });
        }

        createAssetCard(asset) {
            const card = document.createElement('div');
            card.className = 'asset-card';
            card.dataset.assetId = asset.id;
            
            // Determine icon based on file type
            let icon = 'fa-file';
            let iconColor = 'text-secondary';
            
            if (asset.file_type === 'image') {
                icon = 'fa-image';
                iconColor = 'text-primary';
            } else if (asset.file_type === 'video') {
                icon = 'fa-video';
                iconColor = 'text-danger';
            } else if (asset.file_type === 'audio') {
                icon = 'fa-music';
                iconColor = 'text-warning';
            }
            
            // Create thumbnail or icon
            let mediaContent = '';
            if (asset.file_type === 'image') {
                // Use the asset endpoint to get the image with APP_BASE prefix
                const assetUrl = `${window.APP_BASE || ''}/api/asset/${asset.id}`;
                mediaContent = `
                    <div class="asset-thumbnail">
                        <img src="${assetUrl}" 
                             alt="${asset.filename}" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                        <div class="asset-icon-fallback" style="display:none;">
                            <i class="fas ${icon} fa-2x ${iconColor}"></i>
                        </div>
                    </div>
                `;
            } else {
                mediaContent = `
                    <div class="asset-icon">
                        <i class="fas ${icon} fa-3x ${iconColor}"></i>
                    </div>
                `;
            }
            
            // Format file size
            const fileSize = this.formatFileSize(asset.file_size || 0);
            
            card.innerHTML = `
                ${mediaContent}
                <div class="asset-info">
                    <div class="asset-filename" title="${asset.filename}">
                        ${asset.filename || 'Unnamed'}
                    </div>
                    <div class="asset-meta">
                        <span class="asset-size">${fileSize}</span>
                        <span class="asset-source">${asset.source_name || 'Unknown'}</span>
                    </div>
                </div>
                <div class="asset-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="workingAssets.viewAsset(${asset.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="workingAssets.deleteAsset(${asset.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            return card;
        }

        formatFileSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }

        updateStats() {
            // Update dashboard counters
            const elements = {
                'total-downloads': this.stats.total || 0,
                'total-images': this.stats.total_images || this.stats.images || 0,
                'total-videos': this.stats.total_videos || this.stats.videos || 0,
                'total-audio': this.stats.total_audio || this.stats.audio || 0,
                'total-size': this.formatFileSize(this.stats.total_size || 0)
            };
            
            for (const [id, value] of Object.entries(elements)) {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                }
            }
            
            // Update asset count in header
            const assetCount = document.getElementById('asset-count');
            if (assetCount) {
                assetCount.textContent = `(${this.stats.total || 0})`;
            }
        }

        showLoadingState() {
            const grid = document.getElementById('assets-grid');
            if (grid && !grid.querySelector('.loading-spinner')) {
                const spinner = document.createElement('div');
                spinner.className = 'loading-spinner';
                spinner.innerHTML = '<i class="fas fa-spinner fa-spin fa-2x"></i><p>Loading assets...</p>';
                grid.appendChild(spinner);
            }
        }

        hideLoadingState() {
            const spinner = document.querySelector('.loading-spinner');
            if (spinner) {
                spinner.remove();
            }
        }

        showError(message) {
            const grid = document.getElementById('assets-grid');
            if (grid) {
                grid.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle fa-2x text-danger"></i>
                        <p class="mt-2">${message}</p>
                        <button class="btn btn-primary btn-sm mt-2" onclick="workingAssets.loadAssets()">
                            <i class="fas fa-redo"></i> Retry
                        </button>
                    </div>
                `;
            }
        }

        filterAssets(type) {
            if (type === 'all') {
                this.renderAssets();
            } else {
                const filtered = this.assets.filter(asset => asset.file_type === type);
                const grid = document.getElementById('assets-grid');
                
                if (!grid) return;
                
                grid.innerHTML = '';
                
                if (filtered.length === 0) {
                    grid.innerHTML = `<div class="no-assets-message">No ${type}s found</div>`;
                } else {
                    filtered.forEach(asset => {
                        const card = this.createAssetCard(asset);
                        grid.appendChild(card);
                    });
                }
            }
        }

        async viewAsset(assetId) {
            // Open asset in new tab with APP_BASE prefix
            const assetUrl = `${window.APP_BASE || ''}/api/asset/${assetId}`;
            window.open(assetUrl, '_blank');
        }

        async deleteAsset(assetId) {
            if (!confirm('Are you sure you want to delete this asset?')) {
                return;
            }
            
            try {
                const deleteUrl = `${window.APP_BASE || ''}/api/asset/${assetId}`;
                const response = await fetch(deleteUrl, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Remove from local array
                    this.assets = this.assets.filter(a => a.id !== assetId);
                    this.stats = this.calculateStats();
                    
                    // Re-render
                    this.renderAssets();
                    this.updateStats();
                    
                    console.log(`✅ Deleted asset ${assetId}`);
                } else {
                    alert('Failed to delete asset: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error deleting asset:', error);
                alert('Error deleting asset');
            }
        }

        destroy() {
            // Clean up interval
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
            }
        }
    }

    // Create global instance
    window.workingAssets = new WorkingAssetSystem();
    
    // Export for use in other modules
    window.WorkingAssetSystem = WorkingAssetSystem;
})();
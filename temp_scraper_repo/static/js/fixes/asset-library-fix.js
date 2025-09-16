/**
 * Asset Library Fix
 * Fixes errors when loading the asset library section
 */

(function() {
    'use strict';
    
    console.log('🎨 Asset Library Fix initializing...');
    
    // Store original functions
    const originalLoadGallery = window.loadGallery;
    const originalFixAssetLibrary = window.fixAssetLibrary;
    
    // Enhanced asset loading function
    async function loadAssets(options = {}) {
        console.log('📥 Loading assets...');
        
        const {
            container = '#assets-section',
            limit = 50,
            offset = 0,
            showLoading = true
        } = options;
        
        try {
            // Show loading state
            if (showLoading) {
                showLoadingState(container);
            }
            
            // ⚠️ CRITICAL: NEVER ADD PORTS TO URLS! ⚠️
            // Always use /scraper prefix for IIS proxy (NO PORTS!)
            const apiPath = '/scraper/api/assets';  // NEVER add :5050 or any port!
            const response = await fetch(apiPath + '?' + new URLSearchParams({
                limit: limit,
                offset: offset
            }), {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to load assets: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success || data.assets) {
                const assets = data.assets || data.items || [];
                displayAssets(assets, container);
                return assets;
            } else {
                throw new Error(data.error || 'Failed to load assets');
            }
            
        } catch (error) {
            console.error('❌ Error loading assets:', error);
            showErrorState(container, error.message);
            
            // Return empty array to prevent further errors
            return [];
        }
    }
    
    // Display assets in the container
    function displayAssets(assets, containerSelector) {
        const container = document.querySelector(containerSelector);
        if (!container) {
            console.warn('Asset container not found:', containerSelector);
            return;
        }
        
        // Clear loading state
        container.innerHTML = '';
        
        if (!assets || assets.length === 0) {
            container.innerHTML = `
                <div class="empty-state text-center py-5">
                    <i class="fas fa-folder-open fa-4x text-muted mb-3"></i>
                    <h3>No Assets Found</h3>
                    <p class="text-muted">You haven't downloaded any media yet.</p>
                    <button class="btn btn-primary" onclick="showSection('search')">
                        <i class="fas fa-search"></i> Start Searching
                    </button>
                </div>
            `;
            return;
        }
        
        // Create asset grid
        const grid = document.createElement('div');
        grid.className = 'asset-grid row';
        
        assets.forEach(asset => {
            const assetCard = createAssetCard(asset);
            grid.appendChild(assetCard);
        });
        
        container.appendChild(grid);
        
        // Initialize asset interactions
        initializeAssetInteractions();
    }
    
    // Create individual asset card
    function createAssetCard(asset) {
        const card = document.createElement('div');
        card.className = 'col-lg-3 col-md-4 col-sm-6 mb-4';
        
        // Safely extract asset properties
        const {
            id = '',
            filename = 'Unknown',
            file_type = 'unknown',
            thumbnail_path = '',
            source_url = '',
            downloaded_at = '',
            file_size = 0
        } = asset || {};
        
        // Determine icon based on file type
        const icon = getFileTypeIcon(file_type);
        
        // Format file size
        const formattedSize = formatFileSize(file_size);
        
        // Format date
        const formattedDate = formatDate(downloaded_at);
        
        card.innerHTML = `
            <div class="card asset-card" data-asset-id="${escapeHtml(id)}">
                <div class="card-img-top asset-thumbnail-container">
                    ${thumbnail_path ? 
                        `<img src="${escapeHtml(thumbnail_path)}" alt="${escapeHtml(filename)}" class="asset-thumbnail" onerror="this.src='/static/images/placeholder.jpg'">` :
                        `<div class="asset-icon-placeholder"><i class="${icon} fa-3x"></i></div>`
                    }
                    <div class="asset-overlay">
                        <button class="btn btn-sm btn-light view-asset" data-id="${escapeHtml(id)}">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-light download-asset" data-url="${escapeHtml(source_url)}">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-sm btn-danger delete-asset" data-id="${escapeHtml(id)}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <h6 class="card-title text-truncate" title="${escapeHtml(filename)}">
                        ${escapeHtml(filename)}
                    </h6>
                    <p class="card-text small text-muted">
                        <i class="fas fa-calendar"></i> ${formattedDate}<br>
                        <i class="fas fa-file"></i> ${formattedSize}
                    </p>
                </div>
            </div>
        `;
        
        return card;
    }
    
    // Initialize asset interactions
    function initializeAssetInteractions() {
        // View asset
        document.querySelectorAll('.view-asset').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const assetId = this.dataset.id;
                viewAsset(assetId);
            });
        });
        
        // Download asset
        document.querySelectorAll('.download-asset').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const url = this.dataset.url;
                if (url) {
                    window.open(url, '_blank');
                }
            });
        });
        
        // Delete asset
        document.querySelectorAll('.delete-asset').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const assetId = this.dataset.id;
                if (confirm('Are you sure you want to delete this asset?')) {
                    deleteAsset(assetId);
                }
            });
        });
    }
    
    // View asset details
    async function viewAsset(assetId) {
        try {
            // ⚠️ NO PORTS! Always use /scraper prefix
            const apiPath = `/scraper/api/asset/${assetId}`;  // NEVER add ports!
            const response = await fetch(apiPath);
            if (response.ok) {
                const asset = await response.json();
                // Display asset in modal or viewer
                console.log('Viewing asset:', asset);
            }
        } catch (error) {
            console.error('Error viewing asset:', error);
        }
    }
    
    // Delete asset
    async function deleteAsset(assetId) {
        try {
            // ⚠️ NO PORTS! Always use /scraper prefix
            const apiPath = `/scraper/api/asset/${assetId}`;  // NEVER add ports!
            const response = await fetch(apiPath, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Remove from DOM
                const card = document.querySelector(`[data-asset-id="${assetId}"]`);
                if (card) {
                    card.closest('.col-lg-3').remove();
                }
                showNotification('Asset deleted successfully', 'success');
            } else {
                showNotification('Failed to delete asset', 'error');
            }
        } catch (error) {
            console.error('Error deleting asset:', error);
            showNotification('Error deleting asset', 'error');
        }
    }
    
    // Show loading state
    function showLoadingState(containerSelector) {
        const container = document.querySelector(containerSelector);
        if (container) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3">Loading assets...</p>
                </div>
            `;
        }
    }
    
    // Show error state
    function showErrorState(containerSelector, message) {
        const container = document.querySelector(containerSelector);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Error:</strong> ${escapeHtml(message)}
                    <button class="btn btn-sm btn-outline-danger ms-3" onclick="loadAssets()">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
        }
    }
    
    // Helper functions
    function getFileTypeIcon(fileType) {
        const typeMap = {
            'image': 'fas fa-image',
            'video': 'fas fa-video',
            'audio': 'fas fa-music',
            'document': 'fas fa-file-alt',
            'archive': 'fas fa-file-archive',
            'pdf': 'fas fa-file-pdf'
        };
        
        return typeMap[fileType] || 'fas fa-file';
    }
    
    function formatFileSize(bytes) {
        if (!bytes) return 'Unknown';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i];
    }
    
    function formatDate(dateString) {
        if (!dateString) return 'Unknown';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString();
        } catch {
            return dateString;
        }
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }
    
    function showNotification(message, type = 'info') {
        // Check if Bootstrap toast is available
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toastHtml = `
                <div class="toast" role="alert">
                    <div class="toast-body">
                        ${escapeHtml(message)}
                    </div>
                </div>
            `;
            
            const toastContainer = document.querySelector('.toast-container') || createToastContainer();
            const toastElement = document.createElement('div');
            toastElement.innerHTML = toastHtml;
            const toast = toastElement.firstElementChild;
            toastContainer.appendChild(toast);
            
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            toast.addEventListener('hidden.bs.toast', () => toast.remove());
        } else {
            // Fallback to console
            console.log(`[${type}] ${message}`);
        }
    }
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
    
    // Override global functions
    window.loadGallery = loadAssets;
    window.fixAssetLibrary = loadAssets;
    window.loadAssets = loadAssets;
    
    // Also attach to app if it exists
    if (window.app) {
        window.app.loadAssets = loadAssets;
    }
    
    // Listen for section changes to load assets
    window.addEventListener('hashchange', function() {
        if (window.location.hash === '#assets') {
            loadAssets();
        }
    });
    
    // Check if we're already on the assets page
    if (window.location.hash === '#assets' || 
        document.querySelector('#assets-section')?.style.display === 'block') {
        setTimeout(() => loadAssets(), 500);
    }
    
    console.log('✅ Asset Library Fix loaded');
})();
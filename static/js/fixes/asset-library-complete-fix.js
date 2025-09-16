/**
 * Complete Asset Library Fix
 * Resolves all errors when navigating to the asset library
 * 
 * CRITICAL: NO PORTS IN URLs! Use /scraper prefix only
 */

(function() {
    'use strict';
    
    console.log('🔧 Asset Library Complete Fix: Initializing...');
    
    // Ensure APP_BASE is set correctly (NO PORTS!)
    window.APP_BASE = window.APP_BASE || '/scraper';
    
    // Fix 1: Ensure SimpleAssetManager is available globally
    if (!window.SimpleAssetManager) {
        console.log('⚠️ SimpleAssetManager not found, creating fallback');
        
        window.SimpleAssetManager = class SimpleAssetManager {
            constructor(app) {
                this.app = app;
                this.assets = [];
                this.filteredAssets = [];
                this.selectedAssets = new Set();
                this.currentFilter = 'all';
                this.isLoading = false;
                
                console.log('🎬 Fallback Asset Manager: Initializing...');
                this.init();
            }
            
            async init() {
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', () => this.setupAndLoad());
                } else {
                    this.setupAndLoad();
                }
            }
            
            async setupAndLoad() {
                this.setupEventListeners();
                await this.loadAssets();
                console.log('✅ Fallback Asset Manager: Ready');
            }
            
            setupEventListeners() {
                // Safe event listener attachment
                const safeAddListener = (selector, event, handler) => {
                    const elements = document.querySelectorAll(selector);
                    elements.forEach(el => {
                        if (el && !el.hasAttribute('data-listener-attached')) {
                            el.addEventListener(event, handler);
                            el.setAttribute('data-listener-attached', 'true');
                        }
                    });
                };
                
                // Filter buttons
                safeAddListener('input[name="asset-filter"]', 'change', (e) => {
                    this.setFilter(e.target.value);
                });
                
                // Refresh button
                safeAddListener('#refresh-assets-btn', 'click', () => this.loadAssets());
                
                // Select all checkbox
                safeAddListener('#select-all-assets', 'change', (e) => {
                    this.toggleSelectAll(e.target.checked);
                });
                
                // Delete buttons
                safeAddListener('#delete-selected-btn', 'click', () => this.bulkDeleteSelected());
                safeAddListener('#cleanup-assets-btn', 'click', () => this.cleanupMissingAssets());
                safeAddListener('#delete-all-btn', 'click', () => this.bulkDeleteAllFiltered());
            }
            
            async loadAssets() {
                if (this.isLoading) return;
                
                this.isLoading = true;
                this.showLoading();
                
                const safetyTimer = setTimeout(() => {
                    if (this.isLoading) {
                        console.warn('⏱️ Asset loading timeout, showing empty state');
                        this.showEmpty();
                        this.isLoading = false;
                    }
                }, 8000);
                
                try {
                    console.log('🔄 Loading assets from API...');
                    
                    // CRITICAL: No ports in URL!
                    const assetsUrl = `${window.APP_BASE}/api/assets`;
                    console.log('📍 Fetching from:', assetsUrl);
                    
                    const response = await fetch(assetsUrl, {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'
                        },
                        credentials: 'same-origin'
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        this.assets = this.processAssets(data.assets || data.data || []);
                        console.log(`✅ Loaded ${this.assets.length} assets`);
                        this.applyFilter();
                        this.updateStatistics(data.statistics || {});
                    } else {
                        throw new Error(data.error || 'Failed to load assets');
                    }
                } catch (error) {
                    console.error('❌ Error loading assets:', error);
                    this.showError(`Failed to load assets: ${error.message}`);
                } finally {
                    clearTimeout(safetyTimer);
                    this.isLoading = false;
                }
            }
            
            processAssets(assets) {
                if (!Array.isArray(assets)) {
                    console.warn('⚠️ Assets is not an array, converting:', assets);
                    return [];
                }
                
                return assets.map(asset => ({
                    id: asset.id || asset.asset_id,
                    filename: asset.filename || asset.file_name || 'Unknown',
                    file_path: asset.file_path || asset.filepath || '',
                    media_type: asset.media_type || asset.type || 'other',
                    source: asset.source || 'Unknown',
                    download_date: asset.download_date || asset.created_at || new Date().toISOString(),
                    file_size: asset.file_size || asset.size || 0,
                    url: asset.url || '',
                    thumbnail_path: asset.thumbnail_path || '',
                    metadata: asset.metadata || {}
                }));
            }
            
            setFilter(filter) {
                this.currentFilter = filter;
                this.applyFilter();
            }
            
            applyFilter() {
                if (this.currentFilter === 'all') {
                    this.filteredAssets = [...this.assets];
                } else {
                    this.filteredAssets = this.assets.filter(asset => 
                        asset.media_type === this.currentFilter
                    );
                }
                this.renderAssets();
            }
            
            renderAssets() {
                const container = document.getElementById('assets-grid');
                if (!container) {
                    console.warn('⚠️ Assets grid container not found');
                    return;
                }
                
                if (this.filteredAssets.length === 0) {
                    this.showEmpty();
                    return;
                }
                
                const html = this.filteredAssets.map(asset => this.createAssetCard(asset)).join('');
                container.innerHTML = html;
                
                // Attach event listeners to new elements
                this.attachCardListeners();
            }
            
            createAssetCard(asset) {
                const typeIcon = this.getTypeIcon(asset.media_type);
                const size = this.formatFileSize(asset.file_size);
                const date = new Date(asset.download_date).toLocaleDateString();
                
                return `
                    <div class="asset-card" data-asset-id="${asset.id}">
                        <div class="asset-select">
                            <input type="checkbox" class="asset-checkbox" data-asset-id="${asset.id}">
                        </div>
                        <div class="asset-preview">
                            ${this.createPreview(asset)}
                        </div>
                        <div class="asset-info">
                            <div class="asset-name" title="${asset.filename}">
                                ${typeIcon} ${asset.filename}
                            </div>
                            <div class="asset-meta">
                                <span class="asset-source">${asset.source}</span>
                                <span class="asset-size">${size}</span>
                                <span class="asset-date">${date}</span>
                            </div>
                        </div>
                        <div class="asset-actions">
                            <button class="btn btn-sm btn-view" data-asset-id="${asset.id}" title="View">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-download" data-asset-id="${asset.id}" title="Download">
                                <i class="fas fa-download"></i>
                            </button>
                            <button class="btn btn-sm btn-delete" data-asset-id="${asset.id}" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
            }
            
            createPreview(asset) {
                if (asset.media_type === 'image') {
                    const src = asset.thumbnail_path || asset.file_path || '/static/img/placeholder.png';
                    return `<img src="${src}" alt="${asset.filename}" onerror="this.src='/static/img/placeholder.png'">`;
                } else if (asset.media_type === 'video') {
                    return `
                        <div class="video-placeholder">
                            <i class="fas fa-video fa-3x"></i>
                            <span>Video</span>
                        </div>
                    `;
                } else if (asset.media_type === 'audio') {
                    return `
                        <div class="audio-placeholder">
                            <i class="fas fa-music fa-3x"></i>
                            <span>Audio</span>
                        </div>
                    `;
                } else {
                    return `
                        <div class="file-placeholder">
                            <i class="fas fa-file fa-3x"></i>
                            <span>File</span>
                        </div>
                    `;
                }
            }
            
            getTypeIcon(type) {
                const icons = {
                    'image': '🖼️',
                    'video': '🎬',
                    'audio': '🎵',
                    'other': '📄'
                };
                return icons[type] || icons.other;
            }
            
            formatFileSize(bytes) {
                if (!bytes) return '0 B';
                const sizes = ['B', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(1024));
                return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
            }
            
            attachCardListeners() {
                // Checkbox selection
                document.querySelectorAll('.asset-checkbox').forEach(checkbox => {
                    checkbox.addEventListener('change', (e) => {
                        const assetId = e.target.dataset.assetId;
                        if (e.target.checked) {
                            this.selectedAssets.add(assetId);
                        } else {
                            this.selectedAssets.delete(assetId);
                        }
                        this.updateSelectionCount();
                    });
                });
                
                // Action buttons
                document.querySelectorAll('.btn-view').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const assetId = e.currentTarget.dataset.assetId;
                        this.viewAsset(assetId);
                    });
                });
                
                document.querySelectorAll('.btn-download').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const assetId = e.currentTarget.dataset.assetId;
                        this.downloadAsset(assetId);
                    });
                });
                
                document.querySelectorAll('.btn-delete').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const assetId = e.currentTarget.dataset.assetId;
                        this.deleteAsset(assetId);
                    });
                });
            }
            
            toggleSelectAll(checked) {
                const checkboxes = document.querySelectorAll('.asset-checkbox');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = checked;
                    const assetId = checkbox.dataset.assetId;
                    if (checked) {
                        this.selectedAssets.add(assetId);
                    } else {
                        this.selectedAssets.delete(assetId);
                    }
                });
                this.updateSelectionCount();
            }
            
            updateSelectionCount() {
                const count = this.selectedAssets.size;
                const countElement = document.getElementById('selection-count');
                if (countElement) {
                    countElement.textContent = count > 0 ? `${count} selected` : '';
                }
            }
            
            updateStatistics(stats) {
                const updateStat = (id, value) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value;
                    }
                };
                
                updateStat('total-assets', stats.total_assets || 0);
                updateStat('total-size', this.formatFileSize(stats.total_size || 0));
                updateStat('total-images', stats.total_images || 0);
                updateStat('total-videos', stats.total_videos || 0);
                updateStat('total-audio', stats.total_audio || 0);
            }
            
            showLoading() {
                const container = document.getElementById('assets-grid');
                if (container) {
                    container.innerHTML = `
                        <div class="loading-state">
                            <div class="spinner-border" role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                            <p>Loading assets...</p>
                        </div>
                    `;
                }
            }
            
            showEmpty() {
                const container = document.getElementById('assets-grid');
                if (container) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-folder-open fa-4x mb-3"></i>
                            <h4>No Assets Found</h4>
                            <p>Start downloading media to see assets here</p>
                        </div>
                    `;
                }
            }
            
            showError(message) {
                const container = document.getElementById('assets-grid');
                if (container) {
                    container.innerHTML = `
                        <div class="error-state">
                            <i class="fas fa-exclamation-triangle fa-4x mb-3"></i>
                            <h4>Error Loading Assets</h4>
                            <p>${message}</p>
                            <button class="btn btn-primary mt-3" onclick="location.reload()">
                                <i class="fas fa-refresh"></i> Refresh Page
                            </button>
                        </div>
                    `;
                }
            }
            
            async viewAsset(assetId) {
                console.log('Viewing asset:', assetId);
                // Implementation for viewing asset
            }
            
            async downloadAsset(assetId) {
                console.log('Downloading asset:', assetId);
                const asset = this.assets.find(a => a.id == assetId);
                if (asset && asset.file_path) {
                    window.open(asset.file_path, '_blank');
                }
            }
            
            async deleteAsset(assetId) {
                if (!confirm('Are you sure you want to delete this asset?')) return;
                
                try {
                    const response = await fetch(`${window.APP_BASE}/api/asset/${assetId}`, {
                        method: 'DELETE',
                        credentials: 'same-origin'
                    });
                    
                    if (response.ok) {
                        await this.loadAssets();
                    } else {
                        throw new Error('Failed to delete asset');
                    }
                } catch (error) {
                    console.error('Delete error:', error);
                    alert('Failed to delete asset');
                }
            }
            
            async bulkDeleteSelected() {
                // Implementation for bulk delete
                console.log('Bulk delete:', Array.from(this.selectedAssets));
            }
            
            async cleanupMissingAssets() {
                // Implementation for cleanup
                console.log('Cleanup missing assets');
            }
            
            async bulkDeleteAllFiltered() {
                // Implementation for delete all filtered
                console.log('Delete all filtered assets');
            }
        };
    }
    
    // Fix 2: Ensure asset library section exists
    function ensureAssetLibrarySection() {
        let section = document.getElementById('assets-section');
        if (!section) {
            console.log('⚠️ Creating missing assets section');
            section = document.createElement('div');
            section.id = 'assets-section';
            section.className = 'section-content';
            section.style.display = 'none';
            section.innerHTML = `
                <div class="container-fluid">
                    <h2>Asset Library</h2>
                    <div class="asset-controls mb-3">
                        <div class="btn-group" role="group">
                            <input type="radio" class="btn-check" name="asset-filter" id="filter-all" value="all" checked>
                            <label class="btn btn-outline-primary" for="filter-all">All</label>
                            
                            <input type="radio" class="btn-check" name="asset-filter" id="filter-images" value="image">
                            <label class="btn btn-outline-primary" for="filter-images">Images</label>
                            
                            <input type="radio" class="btn-check" name="asset-filter" id="filter-videos" value="video">
                            <label class="btn btn-outline-primary" for="filter-videos">Videos</label>
                            
                            <input type="radio" class="btn-check" name="asset-filter" id="filter-audio" value="audio">
                            <label class="btn btn-outline-primary" for="filter-audio">Audio</label>
                        </div>
                        <button id="refresh-assets-btn" class="btn btn-success ms-3">
                            <i class="fas fa-refresh"></i> Refresh
                        </button>
                        <span id="selection-count" class="ms-3"></span>
                    </div>
                    <div class="asset-statistics mb-3">
                        <span>Total: <strong id="total-assets">0</strong></span>
                        <span class="ms-3">Size: <strong id="total-size">0 B</strong></span>
                        <span class="ms-3">Images: <strong id="total-images">0</strong></span>
                        <span class="ms-3">Videos: <strong id="total-videos">0</strong></span>
                        <span class="ms-3">Audio: <strong id="total-audio">0</strong></span>
                    </div>
                    <div id="assets-grid" class="assets-grid"></div>
                </div>
            `;
            
            const mainContent = document.getElementById('main-content');
            if (mainContent) {
                mainContent.appendChild(section);
            } else {
                document.body.appendChild(section);
            }
        }
    }
    
    // Fix 3: Override showSection to handle assets properly
    const originalShowSection = window.showSection;
    window.showSection = function(sectionName) {
        console.log('🔄 Navigating to section:', sectionName);
        
        // Ensure asset section exists
        if (sectionName === 'assets' || sectionName === 'gallery') {
            ensureAssetLibrarySection();
        }
        
        // Call original if it exists
        if (originalShowSection) {
            originalShowSection(sectionName);
        } else {
            // Fallback implementation
            const sections = ['dashboard', 'search', 'assets', 'gallery', 'settings', 'subscription', 'tools', 'support'];
            sections.forEach(section => {
                const el = document.getElementById(`${section}-section`);
                if (el) {
                    el.style.display = (section === sectionName || 
                                       (sectionName === 'gallery' && section === 'assets')) ? 'block' : 'none';
                }
            });
        }
        
        // Initialize asset manager when showing assets
        if ((sectionName === 'assets' || sectionName === 'gallery') && window.app && !window.app.assetManager) {
            console.log('🎬 Initializing asset manager for section');
            window.app.assetManager = new SimpleAssetManager(window.app);
        }
    };
    
    // Fix 4: Ensure proper initialization on page load
    function initializeAssetLibrary() {
        console.log('🚀 Initializing Asset Library Fix');
        
        // Ensure section exists
        ensureAssetLibrarySection();
        
        // Wait for app to be ready
        const checkApp = setInterval(() => {
            if (window.app) {
                clearInterval(checkApp);
                
                // Initialize asset manager if needed
                if (!window.app.modules) {
                    window.app.modules = {};
                }
                
                if (!window.app.modules.assetManager && !window.app.assetManager) {
                    console.log('🎬 Creating asset manager instance');
                    const manager = new SimpleAssetManager(window.app);
                    window.app.assetManager = manager;
                    window.app.modules.assetManager = manager;
                }
            }
        }, 100);
        
        // Timeout safety
        setTimeout(() => clearInterval(checkApp), 5000);
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeAssetLibrary);
    } else {
        initializeAssetLibrary();
    }
    
    console.log('✅ Asset Library Complete Fix: Loaded');
})();
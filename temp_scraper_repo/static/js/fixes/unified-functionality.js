/**
 * UNIFIED FUNCTIONALITY FIX
 * Single solution for all functionality - replaces all other fix files
 * Handles: Select All, Download, Asset Library, Source Management
 */

(function() {
    'use strict';
    
    console.log('🚀 Unified Functionality Fix initializing...');
    
    // Configuration
    const CONFIG = {
        API_BASE: window.APP_BASE || '',
        DEBOUNCE_DELAY: 300,
        RETRY_ATTEMPTS: 3
    };
    
    // State management
    const STATE = {
        sources: new Set(),
        assets: [],
        selectedAssets: new Set(),
        isLoading: false
    };
    
    // ============================================
    // 1. SOURCE SELECTION FUNCTIONALITY
    // ============================================
    
    function initializeSourceSelection() {
        console.log('📌 Initializing source selection...');
        
        // Remove any existing controls first
        const existingControls = document.querySelectorAll('#unified-source-controls, .select-all-container, .source-controls-buttons');
        existingControls.forEach(el => el.remove());
        
        const sourcesContainer = document.getElementById('source-categories');
        if (!sourcesContainer) {
            console.warn('Source categories container not found');
            return;
        }
        
        // Create unified control panel
        const controlPanel = document.createElement('div');
        controlPanel.id = 'unified-source-controls';
        controlPanel.className = 'mb-3 p-3 bg-light rounded';
        controlPanel.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div class="form-check">
                    <input type="checkbox" id="select-all-sources" class="form-check-input">
                    <label for="select-all-sources" class="form-check-label fw-bold">
                        Select All Sources (<span id="source-count">0</span>/<span id="source-total">0</span>)
                    </label>
                </div>
                <div class="btn-group">
                    <button id="select-recommended-btn" class="btn btn-sm btn-info">
                        <i class="fas fa-star"></i> Recommended
                    </button>
                    <button id="clear-all-btn" class="btn btn-sm btn-warning">
                        <i class="fas fa-times"></i> Clear All
                    </button>
                    <button id="refresh-sources-btn" class="btn btn-sm btn-secondary">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
            </div>
        `;
        
        // Insert before sources container
        sourcesContainer.parentNode.insertBefore(controlPanel, sourcesContainer);
        
        // Attach event handlers
        attachSourceEventHandlers();
        updateSourceCount();
    }
    
    function attachSourceEventHandlers() {
        // Select All checkbox
        const selectAllCheckbox = document.getElementById('select-all-sources');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function(e) {
                const isChecked = e.target.checked;
                const checkboxes = document.querySelectorAll('#source-categories input[type="checkbox"]');
                
                checkboxes.forEach(cb => {
                    cb.checked = isChecked;
                    if (isChecked) {
                        STATE.sources.add(cb.value || cb.id);
                    } else {
                        STATE.sources.delete(cb.value || cb.id);
                    }
                });
                
                updateSourceCount();
            });
        }
        
        // Select Recommended button
        const recommendedBtn = document.getElementById('select-recommended-btn');
        if (recommendedBtn) {
            recommendedBtn.addEventListener('click', function() {
                const recommended = ['youtube', 'twitter', 'instagram', 'facebook', 'reddit', 'tiktok'];
                const checkboxes = document.querySelectorAll('#source-categories input[type="checkbox"]');
                
                checkboxes.forEach(cb => {
                    const label = cb.closest('label') || cb.parentElement;
                    const text = label ? label.textContent.toLowerCase() : '';
                    const isRecommended = recommended.some(rec => text.includes(rec));
                    
                    cb.checked = isRecommended;
                    if (isRecommended) {
                        STATE.sources.add(cb.value || cb.id);
                    } else {
                        STATE.sources.delete(cb.value || cb.id);
                    }
                });
                
                updateSourceCount();
                updateSelectAllState();
            });
        }
        
        // Clear All button
        const clearAllBtn = document.getElementById('clear-all-btn');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', function() {
                const checkboxes = document.querySelectorAll('#source-categories input[type="checkbox"]');
                checkboxes.forEach(cb => {
                    cb.checked = false;
                    STATE.sources.delete(cb.value || cb.id);
                });
                
                updateSourceCount();
                updateSelectAllState();
            });
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refresh-sources-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', function() {
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
                
                loadSources().then(() => {
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-sync"></i> Refresh';
                });
            });
        }
        
        // Individual checkbox changes
        const sourcesContainer = document.getElementById('source-categories');
        if (sourcesContainer) {
            sourcesContainer.addEventListener('change', function(e) {
                if (e.target.type === 'checkbox') {
                    const value = e.target.value || e.target.id;
                    if (e.target.checked) {
                        STATE.sources.add(value);
                    } else {
                        STATE.sources.delete(value);
                    }
                    
                    updateSourceCount();
                    updateSelectAllState();
                }
            });
        }
    }
    
    function updateSourceCount() {
        const checkboxes = document.querySelectorAll('#source-categories input[type="checkbox"]');
        const checked = document.querySelectorAll('#source-categories input[type="checkbox"]:checked');
        
        const countEl = document.getElementById('source-count');
        const totalEl = document.getElementById('source-total');
        
        if (countEl) countEl.textContent = checked.length;
        if (totalEl) totalEl.textContent = checkboxes.length;
    }
    
    function updateSelectAllState() {
        const selectAllCheckbox = document.getElementById('select-all-sources');
        if (!selectAllCheckbox) return;
        
        const checkboxes = document.querySelectorAll('#source-categories input[type="checkbox"]');
        const checked = document.querySelectorAll('#source-categories input[type="checkbox"]:checked');
        
        if (checkboxes.length === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (checked.length === 0) {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = false;
        } else if (checked.length === checkboxes.length) {
            selectAllCheckbox.checked = true;
            selectAllCheckbox.indeterminate = false;
        } else {
            selectAllCheckbox.checked = false;
            selectAllCheckbox.indeterminate = true;
        }
    }
    
    // ============================================
    // 2. ASSET LIBRARY FUNCTIONALITY
    // ============================================
    
    function initializeAssetLibrary() {
        console.log('📚 Initializing asset library...');
        
        // Remove any existing asset library containers
        const existingContainers = document.querySelectorAll('#asset-library-container, .asset-library');
        existingContainers.forEach(el => el.remove());
        
        // Find or create container
        let container = document.getElementById('asset-library-section');
        if (!container) {
            const mainContent = document.querySelector('.main-content, .content-area, #content');
            if (!mainContent) return;
            
            container = document.createElement('div');
            container.id = 'asset-library-section';
            container.className = 'mt-4';
            mainContent.appendChild(container);
        }
        
        // Create asset library UI
        container.innerHTML = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4><i class="fas fa-images"></i> Asset Library</h4>
                    <div class="btn-group">
                        <button id="select-all-assets-btn" class="btn btn-sm btn-primary">
                            <i class="fas fa-check-square"></i> Select All
                        </button>
                        <button id="download-selected-btn" class="btn btn-sm btn-success">
                            <i class="fas fa-download"></i> Download Selected
                        </button>
                        <button id="delete-selected-btn" class="btn btn-sm btn-danger">
                            <i class="fas fa-trash"></i> Delete Selected
                        </button>
                        <button id="refresh-assets-btn" class="btn btn-sm btn-secondary">
                            <i class="fas fa-sync"></i> Refresh
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div id="asset-grid" class="row g-3">
                        <div class="text-center p-5">
                            <i class="fas fa-spinner fa-spin fa-3x text-primary"></i>
                            <p class="mt-3">Loading assets...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Attach asset library event handlers
        attachAssetEventHandlers();
        
        // Load assets
        loadAssets();
    }
    
    function attachAssetEventHandlers() {
        // Select All Assets
        const selectAllAssetsBtn = document.getElementById('select-all-assets-btn');
        if (selectAllAssetsBtn) {
            selectAllAssetsBtn.addEventListener('click', function() {
                const checkboxes = document.querySelectorAll('.asset-checkbox');
                const allChecked = Array.from(checkboxes).every(cb => cb.checked);
                
                checkboxes.forEach(cb => {
                    cb.checked = !allChecked;
                    const assetId = cb.dataset.assetId;
                    if (!allChecked) {
                        STATE.selectedAssets.add(assetId);
                    } else {
                        STATE.selectedAssets.delete(assetId);
                    }
                });
                
                updateAssetSelectionUI();
            });
        }
        
        // Download Selected
        const downloadSelectedBtn = document.getElementById('download-selected-btn');
        if (downloadSelectedBtn) {
            downloadSelectedBtn.addEventListener('click', function() {
                if (STATE.selectedAssets.size === 0) {
                    showNotification('Please select assets to download', 'warning');
                    return;
                }
                
                downloadAssets(Array.from(STATE.selectedAssets));
            });
        }
        
        // Delete Selected
        const deleteSelectedBtn = document.getElementById('delete-selected-btn');
        if (deleteSelectedBtn) {
            deleteSelectedBtn.addEventListener('click', function() {
                if (STATE.selectedAssets.size === 0) {
                    showNotification('Please select assets to delete', 'warning');
                    return;
                }
                
                if (confirm(`Delete ${STATE.selectedAssets.size} selected assets?`)) {
                    deleteAssets(Array.from(STATE.selectedAssets));
                }
            });
        }
        
        // Refresh Assets
        const refreshAssetsBtn = document.getElementById('refresh-assets-btn');
        if (refreshAssetsBtn) {
            refreshAssetsBtn.addEventListener('click', function() {
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
                
                loadAssets().then(() => {
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-sync"></i> Refresh';
                });
            });
        }
    }
    
    // ============================================
    // 3. API FUNCTIONS
    // ============================================
    
    async function loadSources() {
        try {
            const response = await fetch(`${CONFIG.API_BASE}/api/sources`);
            if (!response.ok) throw new Error('Failed to load sources');
            
            const data = await response.json();
            // Process sources if needed
            console.log('Sources loaded:', data);
            
            return data;
        } catch (error) {
            console.error('Error loading sources:', error);
            showNotification('Failed to load sources', 'danger');
        }
    }
    
    async function loadAssets() {
        try {
            STATE.isLoading = true;
            const response = await fetch(`${CONFIG.API_BASE}/api/assets`);
            
            if (!response.ok) throw new Error('Failed to load assets');
            
            const data = await response.json();
            STATE.assets = data.assets || [];
            
            renderAssets();
            return data;
        } catch (error) {
            console.error('Error loading assets:', error);
            showNotification('Failed to load assets', 'danger');
            
            // Show empty state
            const grid = document.getElementById('asset-grid');
            if (grid) {
                grid.innerHTML = '<div class="col-12 text-center p-5"><p>No assets found or error loading assets</p></div>';
            }
        } finally {
            STATE.isLoading = false;
        }
    }
    
    function renderAssets() {
        const grid = document.getElementById('asset-grid');
        if (!grid) return;
        
        if (STATE.assets.length === 0) {
            grid.innerHTML = '<div class="col-12 text-center p-5"><p>No assets found</p></div>';
            return;
        }
        
        grid.innerHTML = STATE.assets.map(asset => `
            <div class="col-md-3 col-sm-6">
                <div class="card asset-card" data-asset-id="${asset.id}">
                    <div class="card-img-top position-relative">
                        ${asset.type === 'image' ? 
                            `<img src="${CONFIG.API_BASE}/api/media/${asset.id}/thumbnail" alt="${asset.filename}" class="img-fluid">` :
                            `<div class="video-thumbnail"><i class="fas fa-video fa-3x"></i></div>`
                        }
                        <div class="position-absolute top-0 start-0 p-2">
                            <input type="checkbox" class="asset-checkbox" data-asset-id="${asset.id}">
                        </div>
                    </div>
                    <div class="card-body p-2">
                        <p class="card-text small text-truncate">${asset.filename}</p>
                        <div class="btn-group btn-group-sm w-100">
                            <button class="btn btn-primary download-asset-btn" data-asset-id="${asset.id}">
                                <i class="fas fa-download"></i>
                            </button>
                            <button class="btn btn-danger delete-asset-btn" data-asset-id="${asset.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Attach individual asset event handlers
        attachIndividualAssetHandlers();
    }
    
    function attachIndividualAssetHandlers() {
        // Asset checkboxes
        document.querySelectorAll('.asset-checkbox').forEach(cb => {
            cb.addEventListener('change', function() {
                const assetId = this.dataset.assetId;
                if (this.checked) {
                    STATE.selectedAssets.add(assetId);
                } else {
                    STATE.selectedAssets.delete(assetId);
                }
                updateAssetSelectionUI();
            });
        });
        
        // Individual download buttons
        document.querySelectorAll('.download-asset-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                downloadAssets([this.dataset.assetId]);
            });
        });
        
        // Individual delete buttons
        document.querySelectorAll('.delete-asset-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                if (confirm('Delete this asset?')) {
                    deleteAssets([this.dataset.assetId]);
                }
            });
        });
    }
    
    async function downloadAssets(assetIds) {
        for (const assetId of assetIds) {
            try {
                const link = document.createElement('a');
                link.href = `${CONFIG.API_BASE}/api/media/${assetId}/download`;
                link.download = '';
                link.click();
                
                // Small delay between downloads
                await new Promise(resolve => setTimeout(resolve, 100));
            } catch (error) {
                console.error(`Error downloading asset ${assetId}:`, error);
            }
        }
        
        showNotification(`Downloading ${assetIds.length} asset(s)`, 'success');
    }
    
    async function deleteAssets(assetIds) {
        try {
            const response = await fetch(`${CONFIG.API_BASE}/api/assets/bulk-delete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ asset_ids: assetIds })
            });
            
            if (!response.ok) throw new Error('Failed to delete assets');
            
            showNotification(`Deleted ${assetIds.length} asset(s)`, 'success');
            STATE.selectedAssets.clear();
            
            // Reload assets
            loadAssets();
        } catch (error) {
            console.error('Error deleting assets:', error);
            showNotification('Failed to delete assets', 'danger');
        }
    }
    
    function updateAssetSelectionUI() {
        const btn = document.getElementById('select-all-assets-btn');
        if (btn) {
            const checkboxes = document.querySelectorAll('.asset-checkbox');
            const allChecked = Array.from(checkboxes).every(cb => cb.checked);
            
            btn.innerHTML = allChecked ? 
                '<i class="fas fa-square"></i> Deselect All' : 
                '<i class="fas fa-check-square"></i> Select All';
        }
    }
    
    // ============================================
    // 4. UTILITY FUNCTIONS
    // ============================================
    
    function showNotification(message, type = 'info') {
        // Remove existing notifications
        const existing = document.querySelector('.unified-notification');
        if (existing) existing.remove();
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} unified-notification position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '9999';
        notification.innerHTML = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // ============================================
    // 5. INITIALIZATION
    // ============================================
    
    function initialize() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initialize);
            return;
        }
        
        console.log('✅ Unified Functionality Fix ready');
        
        // Initialize all components
        initializeSourceSelection();
        initializeAssetLibrary();
        
        // Listen for navigation changes
        document.addEventListener('sectionChanged', function(e) {
            if (e.detail === 'search') {
                initializeSourceSelection();
            } else if (e.detail === 'library') {
                initializeAssetLibrary();
            }
        });
    }
    
    // Start initialization
    initialize();
    
    // Export for debugging
    window.UnifiedFunctionality = {
        STATE,
        CONFIG,
        reload: initialize,
        loadAssets,
        loadSources
    };
})();
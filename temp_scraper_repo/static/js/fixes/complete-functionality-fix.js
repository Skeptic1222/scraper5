/**
 * Complete Functionality Fix
 * Fixes: Select All for sources, Asset Library loading, Downloads
 */

(function() {
    'use strict';
    
    console.log('🔧 Complete Functionality Fix initializing...');
    
    // Ensure APP_BASE is set
    window.APP_BASE = window.APP_BASE || '/scraper';
    
    // ========================================
    // FIX 1: SELECT ALL FUNCTIONALITY
    // ========================================
    
    function fixSelectAll() {
        console.log('🔧 Fixing Select All functionality...');
        
        // Wait for DOM to be ready
        const setupSelectAll = () => {
            // Find or create Select All checkbox
            let selectAllCheckbox = document.getElementById('select-all-sources') || 
                                   document.querySelector('.select-all-checkbox') ||
                                   document.querySelector('input[data-select-all="true"]');
            
            if (!selectAllCheckbox) {
                // Create Select All if it doesn't exist
                const sourcesContainer = document.querySelector('.sources-grid') || 
                                       document.querySelector('.source-selection') ||
                                       document.querySelector('#sources-section');
                
                if (sourcesContainer) {
                    const selectAllDiv = document.createElement('div');
                    selectAllDiv.className = 'select-all-container mb-3';
                    selectAllDiv.innerHTML = `
                        <label class="form-check" style="font-weight: bold; cursor: pointer;">
                            <input type="checkbox" id="select-all-sources" class="form-check-input" style="cursor: pointer;">
                            <span class="form-check-label ms-2">Select All Sources</span>
                        </label>
                    `;
                    
                    // Insert before sources or at the top
                    const firstSource = sourcesContainer.querySelector('.source-item, .source-card');
                    if (firstSource) {
                        sourcesContainer.insertBefore(selectAllDiv, firstSource);
                    } else {
                        sourcesContainer.appendChild(selectAllDiv);
                    }
                    
                    selectAllCheckbox = document.getElementById('select-all-sources');
                }
            }
            
            if (selectAllCheckbox) {
                // Remove any existing listeners
                const newCheckbox = selectAllCheckbox.cloneNode(true);
                selectAllCheckbox.parentNode.replaceChild(newCheckbox, selectAllCheckbox);
                selectAllCheckbox = newCheckbox;
                
                // Add Select All handler
                selectAllCheckbox.addEventListener('change', function(e) {
                    const isChecked = e.target.checked;
                    console.log(`📝 Select All: ${isChecked}`);
                    
                    // Find all source checkboxes
                    const sourceCheckboxes = document.querySelectorAll(`
                        input[type="checkbox"][name="sources"],
                        input[type="checkbox"].source-checkbox,
                        .source-item input[type="checkbox"],
                        .source-card input[type="checkbox"],
                        input[type="checkbox"][data-source]
                    `);
                    
                    sourceCheckboxes.forEach(checkbox => {
                        if (checkbox.id !== 'select-all-sources') {
                            checkbox.checked = isChecked;
                            checkbox.disabled = false;
                            
                            // Trigger change event
                            const event = new Event('change', { bubbles: true });
                            checkbox.dispatchEvent(event);
                            
                            // Update visual state of parent
                            const parent = checkbox.closest('.source-item, .source-card');
                            if (parent) {
                                if (isChecked) {
                                    parent.classList.add('selected', 'active');
                                } else {
                                    parent.classList.remove('selected', 'active');
                                }
                            }
                        }
                    });
                    
                    console.log(`✅ Updated ${sourceCheckboxes.length} source checkboxes`);
                });
                
                // Update Select All state when individual checkboxes change
                document.addEventListener('change', function(e) {
                    if (e.target.type === 'checkbox' && 
                        e.target.id !== 'select-all-sources' &&
                        (e.target.name === 'sources' || e.target.classList.contains('source-checkbox'))) {
                        
                        const allCheckboxes = document.querySelectorAll(`
                            input[type="checkbox"][name="sources"],
                            input[type="checkbox"].source-checkbox
                        `);
                        
                        const checkedCount = Array.from(allCheckboxes).filter(cb => cb.checked).length;
                        
                        if (selectAllCheckbox) {
                            selectAllCheckbox.checked = checkedCount === allCheckboxes.length;
                            selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < allCheckboxes.length;
                        }
                    }
                });
            }
        };
        
        // Initial setup
        setupSelectAll();
        
        // Re-run after dynamic content loads
        setTimeout(setupSelectAll, 1000);
        setTimeout(setupSelectAll, 2000);
    }
    
    // ========================================
    // FIX 2: ASSET LIBRARY LOADING
    // ========================================
    
    async function fixAssetLibrary() {
        console.log('🖼️ Fixing Asset Library...');
        
        const gallery = document.getElementById('asset-library') || 
                       document.querySelector('.asset-grid') ||
                       document.querySelector('.gallery-grid');
        
        if (!gallery) {
            console.log('⚠️ No gallery container found');
            return;
        }
        
        // Show loading state
        if (!gallery.querySelector('.spinner-border')) {
            gallery.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading assets...</span>
                    </div>
                    <p class="mt-3">Loading your media library...</p>
                </div>
            `;
        }
        
        try {
            // Try multiple endpoints with better error handling
            const endpoints = [
                `${window.APP_BASE}/api/assets?limit=100`,
                `${window.APP_BASE}/api/assets`,
                `${window.APP_BASE}/api/search?type=all`
            ];
            
            let data = null;
            let successEndpoint = null;
            
            for (const endpoint of endpoints) {
                try {
                    console.log(`🔍 Trying endpoint: ${endpoint}`);
                    const response = await fetch(endpoint, {
                        method: 'GET',
                        credentials: 'same-origin',
                        headers: {
                            'Accept': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });
                    
                    if (response.ok) {
                        data = await response.json();
                        successEndpoint = endpoint;
                        break;
                    }
                } catch (err) {
                    console.warn(`Failed to fetch from ${endpoint}:`, err);
                }
            }
            
            if (data) {
                console.log('✅ Assets loaded from:', successEndpoint);
                console.log('📦 Data received:', data);
                
                // Clear loading state
                gallery.innerHTML = '';
                
                // Handle different response formats
                const assets = data.assets || data.results || data.items || [];
                
                if (assets.length > 0) {
                    // Add grid class if needed
                    if (!gallery.classList.contains('asset-grid')) {
                        gallery.classList.add('asset-grid');
                    }
                    
                    // Display each asset
                    assets.forEach(asset => {
                        const assetEl = createAssetElement(asset);
                        gallery.appendChild(assetEl);
                    });
                    
                    console.log(`✅ Displayed ${assets.length} assets`);
                } else {
                    // Show empty state
                    gallery.innerHTML = `
                        <div class="col-12 text-center py-5">
                            <i class="fas fa-images fa-4x text-muted mb-3"></i>
                            <h4>No Media Yet</h4>
                            <p class="text-muted">Start downloading content to build your library!</p>
                            <button class="btn btn-primary mt-3" onclick="document.getElementById('search-query')?.focus()">
                                <i class="fas fa-search me-2"></i>Start Searching
                            </button>
                        </div>
                    `;
                }
            } else {
                throw new Error('Failed to load assets from all endpoints');
            }
            
        } catch (error) {
            console.error('❌ Asset loading error:', error);
            gallery.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Unable to load media library. Please refresh the page or try again later.
                        <button class="btn btn-sm btn-outline-warning ms-3" onclick="location.reload()">
                            <i class="fas fa-redo"></i> Refresh
                        </button>
                    </div>
                </div>
            `;
        }
    }
    
    function createAssetElement(asset) {
        const div = document.createElement('div');
        div.className = 'asset-item';
        div.style.cssText = `
            position: relative;
            cursor: pointer;
            transition: transform 0.3s;
            border-radius: 8px;
            overflow: hidden;
            background: rgba(255,255,255,0.05);
        `;
        
        // Determine URLs
        const assetId = asset.id || asset.asset_id;
        const mediaUrl = asset.url || asset.file_path || 
                        (assetId ? `${window.APP_BASE}/api/asset/${assetId}` : null);
        const thumbnailUrl = asset.thumbnail_url || asset.thumbnail_path ||
                           (assetId ? `${window.APP_BASE}/api/asset/${assetId}/thumbnail` : mediaUrl);
        
        // Determine media type
        const isVideo = asset.file_type === 'video' || 
                       asset.media_type === 'video' ||
                       (asset.file_extension && ['.mp4', '.webm', '.mov'].includes(asset.file_extension));
        
        if (isVideo) {
            div.innerHTML = `
                <video src="${mediaUrl}" poster="${thumbnailUrl}" 
                       style="width: 100%; height: 200px; object-fit: cover;" muted>
                </video>
                <div class="asset-overlay" style="position: absolute; bottom: 0; left: 0; right: 0; 
                     background: linear-gradient(transparent, rgba(0,0,0,0.8)); padding: 10px; color: white;">
                    <div style="font-size: 14px; font-weight: bold;">${asset.filename || 'Video'}</div>
                    <div style="font-size: 12px; opacity: 0.8;">${asset.source_name || asset.source || 'Unknown'}</div>
                </div>
                <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.6); 
                     color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                    <i class="fas fa-play"></i> Video
                </div>
            `;
        } else {
            div.innerHTML = `
                <img src="${thumbnailUrl}" alt="${asset.filename || 'Image'}" 
                     style="width: 100%; height: 200px; object-fit: cover;" loading="lazy"
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'200\\' height=\\'200\\'%3E%3Crect fill=\\'%23ddd\\'/%3E%3Ctext x=\\'50%25\\' y=\\'50%25\\' text-anchor=\\'middle\\' dy=\\'.3em\\' fill=\\'%23999\\'%3ENo Preview%3C/text%3E%3C/svg%3E'">
                <div class="asset-overlay" style="position: absolute; bottom: 0; left: 0; right: 0; 
                     background: linear-gradient(transparent, rgba(0,0,0,0.8)); padding: 10px; color: white;">
                    <div style="font-size: 14px; font-weight: bold;">${asset.filename || 'Image'}</div>
                    <div style="font-size: 12px; opacity: 0.8;">${asset.source_name || asset.source || 'Unknown'}</div>
                </div>
            `;
        }
        
        // Add hover effect
        div.addEventListener('mouseenter', () => {
            div.style.transform = 'scale(1.05)';
            div.style.zIndex = '10';
        });
        
        div.addEventListener('mouseleave', () => {
            div.style.transform = 'scale(1)';
            div.style.zIndex = '1';
        });
        
        // Add click to download
        div.addEventListener('click', () => {
            if (assetId) {
                console.log(`📥 Downloading asset ${assetId}`);
                const downloadUrl = `${window.APP_BASE}/api/download-url?asset_id=${assetId}`;
                window.location.href = downloadUrl;
            }
        });
        
        return div;
    }
    
    // ========================================
    // FIX 3: DOWNLOAD FUNCTIONALITY
    // ========================================
    
    function fixDownloads() {
        console.log('📥 Fixing Download functionality...');
        
        // Override any broken download functions
        window.startDownload = async function(query, sources) {
            console.log('🚀 Starting download:', { query, sources });
            
            if (!query) {
                showNotification('Please enter a search query', 'warning');
                return;
            }
            
            // Show progress
            showProgress(true, 'Initializing download...');
            
            try {
                // Use the working /api/search endpoint
                const response = await fetch(`${window.APP_BASE}/api/search`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({
                        query: query,
                        sources: sources || getSelectedSources(),
                        max_results: 25,
                        content_types: {
                            images: true,
                            videos: true
                        }
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`Download failed: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('✅ Download response:', data);
                
                if (data.job_id) {
                    // Monitor job progress
                    monitorDownloadProgress(data.job_id);
                    showNotification('Download started! Monitoring progress...', 'success');
                } else if (data.results || data.assets) {
                    // Direct results
                    showNotification('Download completed!', 'success');
                    setTimeout(() => fixAssetLibrary(), 1000);
                }
                
                return data;
                
            } catch (error) {
                console.error('❌ Download error:', error);
                showNotification('Download failed: ' + error.message, 'error');
                showProgress(false);
            }
        };
        
        // Fix search form
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            // Clone to remove old handlers
            const newForm = searchForm.cloneNode(true);
            searchForm.parentNode.replaceChild(newForm, searchForm);
            
            newForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const queryInput = document.getElementById('search-query') || 
                                 document.querySelector('input[name="query"]');
                
                if (queryInput && queryInput.value.trim()) {
                    await window.startDownload(queryInput.value.trim());
                }
            });
        }
        
        // Add download button handler
        const downloadBtn = document.getElementById('start-download') || 
                          document.querySelector('.download-btn');
        
        if (downloadBtn) {
            downloadBtn.onclick = async () => {
                const query = document.getElementById('search-query')?.value;
                if (query) {
                    await window.startDownload(query);
                }
            };
        }
    }
    
    function getSelectedSources() {
        const sources = [];
        document.querySelectorAll(`
            input[type="checkbox"][name="sources"]:checked,
            input[type="checkbox"].source-checkbox:checked,
            input[type="checkbox"][data-source]:checked
        `).forEach(cb => {
            const value = cb.value || cb.dataset.source || cb.id;
            if (value && value !== 'select-all-sources') {
                sources.push(value);
            }
        });
        
        return sources.length > 0 ? sources : ['youtube', 'instagram', 'twitter'];
    }
    
    function monitorDownloadProgress(jobId) {
        console.log('📊 Monitoring job:', jobId);
        
        let attempts = 0;
        const maxAttempts = 60;
        
        const checkProgress = async () => {
            try {
                const response = await fetch(`${window.APP_BASE}/api/job/${jobId}/status`);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Progress:', data);
                    
                    // Update progress display
                    if (data.progress !== undefined) {
                        showProgress(true, `Downloading: ${Math.round(data.progress)}%`, data.progress);
                    }
                    
                    if (data.status === 'completed' || data.status === 'complete') {
                        showNotification('Download completed!', 'success');
                        showProgress(false);
                        setTimeout(() => fixAssetLibrary(), 1000);
                    } else if (data.status === 'failed' || data.status === 'error') {
                        showNotification('Download failed', 'error');
                        showProgress(false);
                    } else if (attempts < maxAttempts) {
                        attempts++;
                        setTimeout(checkProgress, 2000);
                    } else {
                        showProgress(false);
                    }
                }
            } catch (error) {
                console.error('Progress check error:', error);
                showProgress(false);
            }
        };
        
        checkProgress();
    }
    
    // ========================================
    // HELPER FUNCTIONS
    // ========================================
    
    function showNotification(message, type = 'info') {
        console.log(`💬 ${type.toUpperCase()}: ${message}`);
        
        // Remove existing notifications
        document.querySelectorAll('.fix-notification').forEach(n => n.remove());
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show fix-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.remove(), 5000);
    }
    
    function showProgress(show, message = '', percent = 0) {
        let progressContainer = document.getElementById('download-progress-fix');
        
        if (!show) {
            if (progressContainer) {
                progressContainer.remove();
            }
            return;
        }
        
        if (!progressContainer) {
            progressContainer = document.createElement('div');
            progressContainer.id = 'download-progress-fix';
            progressContainer.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 300px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 15px;
                z-index: 10000;
            `;
            document.body.appendChild(progressContainer);
        }
        
        progressContainer.innerHTML = `
            <div class="d-flex justify-content-between mb-2">
                <span>${message}</span>
                <span>${Math.round(percent)}%</span>
            </div>
            <div class="progress">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     style="width: ${percent}%"></div>
            </div>
        `;
    }
    
    // ========================================
    // INITIALIZATION
    // ========================================
    
    function initialize() {
        console.log('🚀 Initializing Complete Functionality Fix...');
        
        // Fix all three issues
        fixSelectAll();
        fixAssetLibrary();
        fixDownloads();
        
        // Make functions globally available
        window.fixSelectAll = fixSelectAll;
        window.fixAssetLibrary = fixAssetLibrary;
        window.fixDownloads = fixDownloads;
        window.startDownload = window.startDownload;
        
        console.log('✅ Complete Functionality Fix initialized');
    }
    
    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Re-initialize after delay for dynamic content
    setTimeout(initialize, 1500);
    setTimeout(() => {
        fixSelectAll();
        fixAssetLibrary();
    }, 3000);
    
})();
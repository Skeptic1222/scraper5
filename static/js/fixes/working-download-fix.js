/**
 * Working Download and Gallery Fix
 * Uses the actual working endpoints from the Flask app
 */

(function() {
    'use strict';
    
    console.log('🔧 Working Download Fix loading...');
    
    // Ensure APP_BASE is set
    window.APP_BASE = window.APP_BASE || '/scraper';
    
    // Override the search manager if it exists
    if (window.EnhancedSearchManager) {
        const originalSearch = EnhancedSearchManager.prototype.startBulletproofSearch || 
                               EnhancedSearchManager.prototype.startSearch;
        
        EnhancedSearchManager.prototype.startBulletproofSearch = async function(params) {
            console.log('🎯 Intercepting search with working endpoint');
            return await performSearch(params);
        };
        
        EnhancedSearchManager.prototype.startSearch = async function(params) {
            console.log('🎯 Intercepting search with working endpoint');
            return await performSearch(params);
        };
    }
    
    // Main search function that works
    async function performSearch(params) {
        console.log('🔍 Starting search with params:', params);
        
        try {
            // Use the /api/search endpoint which is registered in the blueprint
            const response = await fetch(`${window.APP_BASE}/api/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    query: params.query || params.search_query,
                    sources: params.enabled_sources || params.sources || ['youtube', 'instagram'],
                    max_results: params.max_content || params.max_results || 25,
                    content_types: params.content_types || {
                        images: true,
                        videos: true
                    }
                })
            });
            
            if (!response.ok) {
                throw new Error(`Search failed: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Search response:', data);
            
            // Handle different response formats
            if (data.job_id) {
                // Monitor job progress
                monitorJob(data.job_id);
            } else if (data.assets || data.results) {
                // Direct results returned
                displayResults(data.assets || data.results);
            }
            
            return data;
            
        } catch (error) {
            console.error('❌ Search error:', error);
            showNotification('Search failed. Please try again.', 'error');
            throw error;
        }
    }
    
    // Monitor job progress
    function monitorJob(jobId) {
        console.log('📊 Monitoring job:', jobId);
        
        const checkStatus = async () => {
            try {
                // Use the blueprint endpoint
                const response = await fetch(`${window.APP_BASE}/api/job/${jobId}/status`);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('Job status:', data);
                    
                    updateProgress(data);
                    
                    if (data.status === 'completed' || data.status === 'complete') {
                        showNotification('Download completed!', 'success');
                        loadAssets();
                    } else if (data.status === 'failed' || data.status === 'error') {
                        showNotification('Download failed', 'error');
                    } else {
                        // Check again in 2 seconds
                        setTimeout(checkStatus, 2000);
                    }
                }
            } catch (error) {
                console.error('Status check error:', error);
            }
        };
        
        checkStatus();
    }
    
    // Update progress display
    function updateProgress(data) {
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar && data.progress !== undefined) {
            progressBar.style.width = `${data.progress}%`;
            progressBar.textContent = `${Math.round(data.progress)}%`;
        }
    }
    
    // Load assets from database
    async function loadAssets() {
        console.log('🖼️ Loading assets...');
        
        try {
            // Use the blueprint endpoint with proper params
            const response = await fetch(`${window.APP_BASE}/api/assets?limit=50`, {
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Assets loaded:', data);
                displayResults(data.assets || []);
            }
        } catch (error) {
            console.error('Load assets error:', error);
        }
    }
    
    // Display results in gallery
    function displayResults(assets) {
        const gallery = document.getElementById('asset-library') || 
                       document.querySelector('.asset-grid') ||
                       document.querySelector('.gallery-grid');
                       
        if (!gallery || !assets || assets.length === 0) return;
        
        // Clear existing content
        gallery.innerHTML = '';
        
        assets.forEach(asset => {
            const item = createAssetItem(asset);
            gallery.appendChild(item);
        });
    }
    
    // Create asset item element
    function createAssetItem(asset) {
        const div = document.createElement('div');
        div.className = 'asset-item';
        div.style.cssText = 'cursor: pointer; position: relative;';
        
        // Determine the correct URL for the asset
        let mediaUrl = asset.url || asset.file_path;
        if (asset.id && !mediaUrl) {
            // Use the blueprint endpoint
            mediaUrl = `${window.APP_BASE}/api/asset/${asset.id}`;
        }
        
        const thumbnailUrl = asset.thumbnail_url || 
                           `${window.APP_BASE}/api/asset/${asset.id}/thumbnail` ||
                           mediaUrl;
        
        if (asset.file_type === 'video' || asset.media_type === 'video') {
            div.innerHTML = `
                <video src="${mediaUrl}" poster="${thumbnailUrl}" 
                       style="width: 100%; height: 200px; object-fit: cover;">
                </video>
                <div class="asset-info">
                    <div>${asset.filename || 'Video'}</div>
                    <small>${asset.source_name || 'Unknown'}</small>
                </div>
            `;
        } else {
            div.innerHTML = `
                <img src="${thumbnailUrl}" alt="${asset.filename || 'Image'}"
                     style="width: 100%; height: 200px; object-fit: cover;">
                <div class="asset-info">
                    <div>${asset.filename || 'Image'}</div>
                    <small>${asset.source_name || 'Unknown'}</small>
                </div>
            `;
        }
        
        // Add click handler for download
        div.addEventListener('click', () => {
            if (asset.id) {
                // Use the download endpoint
                window.location.href = `${window.APP_BASE}/api/download-url?asset_id=${asset.id}`;
            }
        });
        
        return div;
    }
    
    // Show notification
    function showNotification(message, type = 'info') {
        console.log(`💬 ${type}: ${message}`);
        
        // Try to use existing toast system
        if (window.showToast) {
            window.showToast(message, type);
            return;
        }
        
        // Create simple notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type}`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // Fix search form submission
    function fixSearchForm() {
        const searchForm = document.getElementById('search-form');
        if (!searchForm) return;
        
        // Remove old handlers
        const newForm = searchForm.cloneNode(true);
        searchForm.parentNode.replaceChild(newForm, searchForm);
        
        newForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const query = document.getElementById('search-query')?.value || 
                         document.querySelector('input[name="query"]')?.value;
                         
            if (!query) {
                showNotification('Please enter a search query', 'warning');
                return;
            }
            
            // Get selected sources
            const sources = [];
            document.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
                const value = cb.value || cb.dataset.source || cb.name;
                if (value && value !== 'sources') sources.push(value);
            });
            
            // Perform search
            await performSearch({
                query: query,
                enabled_sources: sources.length > 0 ? sources : ['youtube', 'instagram'],
                max_content: 25
            });
        });
    }
    
    // Initialize
    function initialize() {
        console.log('🚀 Initializing working download fix...');
        
        // Fix search form
        fixSearchForm();
        
        // Load assets on page load
        if (document.querySelector('.asset-grid, #asset-library')) {
            loadAssets();
        }
        
        // Make functions globally available
        window.performSearch = performSearch;
        window.loadAssets = loadAssets;
        
        console.log('✅ Working download fix initialized');
    }
    
    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Also initialize after delay for late-loading elements
    setTimeout(initialize, 1000);
    
})();
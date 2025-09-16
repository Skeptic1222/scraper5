/**
 * API Endpoint Fix
 * Fixes the search and download functionality by using correct endpoints
 */

(function() {
    'use strict';
    
    console.log('🔧 API Endpoint Fix loading...');
    
    // Store original fetch for intercepting
    const originalFetch = window.fetch;
    
    // Override fetch to fix API endpoints
    window.fetch = function(url, options) {
        let fixedUrl = url;
        
        // Fix search endpoint
        if (url.includes('/api/search') && !url.includes('/api/bulletproof-search')) {
            // Use bulletproof-search which exists in app.py
            fixedUrl = url.replace('/api/search', '/api/bulletproof-search');
            console.log('🔄 Redirecting /api/search to /api/bulletproof-search');
        }
        
        // Ensure APP_BASE is properly used
        if (fixedUrl.startsWith('/api/') && window.APP_BASE) {
            fixedUrl = window.APP_BASE + fixedUrl;
        }
        
        console.log(`📡 API Request: ${url} -> ${fixedUrl}`);
        
        return originalFetch.call(this, fixedUrl, options);
    };
    
    // Fix EnhancedSearchManager if it exists
    if (window.EnhancedSearchManager) {
        const originalStartSearch = EnhancedSearchManager.prototype.startBulletproofSearch;
        
        EnhancedSearchManager.prototype.startBulletproofSearch = async function(params) {
            console.log('🎯 Intercepting search, using bulletproof-search endpoint');
            
            try {
                // Use the correct endpoint
                const searchUrl = `${window.APP_BASE || ''}/api/bulletproof-search`;
                const response = await fetch(searchUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(params)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Search request failed');
                }
                
                const data = await response.json();
                this.currentJobId = data.job_id;
                
                console.log('✅ Search started with job ID:', this.currentJobId);
                
                // Start monitoring progress
                if (this.monitorJobProgress) {
                    this.monitorJobProgress();
                }
                
                return data;
                
            } catch (error) {
                console.error('❌ Search error:', error);
                throw error;
            }
        };
    }
    
    // Also create an alias for the missing /api/search endpoint
    document.addEventListener('DOMContentLoaded', function() {
        // Fix any hardcoded references in the DOM
        const scripts = document.querySelectorAll('script');
        scripts.forEach(script => {
            if (script.textContent && script.textContent.includes('/api/search')) {
                console.log('🔧 Found hardcoded /api/search reference, patching...');
                script.textContent = script.textContent.replace(
                    /\/api\/search(?!-)/g,
                    '/api/bulletproof-search'
                );
            }
        });
    });
    
    console.log('✅ API Endpoint Fix loaded');
})();

// Also fix the gallery loading
document.addEventListener('DOMContentLoaded', function() {
    // Fix stats API endpoint
    const loadStats = async function() {
        try {
            const response = await fetch(`${window.APP_BASE || ''}/api/stats`);
            if (response.ok) {
                const stats = await response.json();
                console.log('📊 Stats loaded:', stats);
                
                // Update stats display if elements exist
                if (document.getElementById('total-downloads')) {
                    document.getElementById('total-downloads').textContent = stats.total_downloads || 0;
                }
                if (document.getElementById('total-assets')) {
                    document.getElementById('total-assets').textContent = stats.total_assets || 0;
                }
                if (document.getElementById('storage-used')) {
                    document.getElementById('storage-used').textContent = stats.storage_used || '0 MB';
                }
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    };
    
    // Load gallery assets
    const loadGallery = async function() {
        try {
            const response = await fetch(`${window.APP_BASE || ''}/api/assets`);
            if (response.ok) {
                const data = await response.json();
                console.log('🖼️ Gallery assets loaded:', data);
                
                const gallery = document.getElementById('asset-library') || 
                               document.querySelector('.asset-grid') ||
                               document.querySelector('.gallery-grid');
                               
                if (gallery && data.assets) {
                    // Clear loading state
                    const loadingElement = gallery.querySelector('.spinner-border');
                    if (loadingElement) {
                        loadingElement.parentElement.remove();
                    }
                    
                    // Display assets
                    data.assets.forEach(asset => {
                        const assetElement = createAssetElement(asset);
                        if (assetElement) {
                            gallery.appendChild(assetElement);
                        }
                    });
                }
            }
        } catch (error) {
            console.error('Error loading gallery:', error);
        }
    };
    
    // Create asset element for gallery
    const createAssetElement = function(asset) {
        const div = document.createElement('div');
        div.className = 'asset-item gallery-item fade-in';
        div.dataset.assetId = asset.id;
        
        // Create media element
        let mediaHtml = '';
        if (asset.media_type === 'video') {
            mediaHtml = `<video src="${window.APP_BASE || ''}/api/media/${asset.id}" controls></video>`;
        } else {
            mediaHtml = `<img src="${window.APP_BASE || ''}/api/media/${asset.id}" alt="${asset.filename || 'Asset'}">`;
        }
        
        div.innerHTML = `
            ${mediaHtml}
            <div class="asset-info">
                <div class="asset-title">${asset.filename || 'Untitled'}</div>
                <div class="asset-meta">
                    ${asset.source || 'Unknown'} • ${asset.file_size || 'Unknown size'}
                </div>
            </div>
        `;
        
        // Add click handler for download
        div.addEventListener('click', function() {
            if (asset.id) {
                window.location.href = `${window.APP_BASE || ''}/api/media/${asset.id}/download`;
            }
        });
        
        return div;
    };
    
    // Auto-load on page ready
    if (document.getElementById('asset-library') || document.querySelector('.asset-grid')) {
        loadGallery();
    }
    
    if (document.getElementById('total-downloads') || document.querySelector('.stats-bar')) {
        loadStats();
    }
});
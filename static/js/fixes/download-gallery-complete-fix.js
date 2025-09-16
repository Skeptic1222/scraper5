/**
 * Complete Download and Gallery Fix
 * Comprehensive solution for fixing downloads and gallery
 */

(function() {
    'use strict';
    
    console.log('🔧 Complete Download & Gallery Fix loading...');
    
    // Fix APP_BASE if not set
    if (!window.APP_BASE) {
        window.APP_BASE = '/scraper';
        console.log('📍 Set APP_BASE to /scraper');
    }
    
    // Create a simple download function
    window.simpleDownload = async function(query, sources) {
        console.log('📥 Starting simple download:', query, sources);
        
        try {
            // Use comprehensive-search which doesn't require auth
            const endpoint = '/api/comprehensive-search';
            const url = `${window.APP_BASE}${endpoint}`;
            console.log(`🔍 Using endpoint: ${url}`);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    query: query,
                    search_type: 'comprehensive',
                    enabled_sources: sources || ['youtube', 'instagram', 'twitter'],
                    max_content: 25,
                    safe_search: true,
                    content_types: {
                        images: true,
                        videos: true
                    }
                })
            })
            
            if (response && response.ok) {
                const data = await response.json();
                console.log('✅ Download started:', data);
                
                // Show success message
                showMessage('Download started! Check progress below.', 'success');
                
                // Monitor progress if job_id is returned
                if (data.job_id) {
                    monitorJobProgress(data.job_id);
                }
                
                return data;
            } else {
                const errorText = await response.text();
                console.error('Response error:', errorText);
                throw new Error(`Download failed: ${response.status} ${response.statusText}`);
            }
        } catch (error) {
            console.error('❌ Download error:', error);
            showMessage('Download failed: ' + error.message, 'error');
        }
    };
    
    // Monitor job progress
    function monitorJobProgress(jobId) {
        const progressUrl = `${window.APP_BASE}/api/job-status/${jobId}`;
        let attempts = 0;
        const maxAttempts = 60;
        
        const checkProgress = async () => {
            try {
                const response = await fetch(progressUrl);
                if (response.ok) {
                    const data = await response.json();
                    console.log('📊 Job progress:', data);
                    
                    // Update progress display
                    updateProgressDisplay(data);
                    
                    if (data.status === 'completed' || data.status === 'complete') {
                        showMessage('Download completed!', 'success');
                        setTimeout(loadGallery, 1000); // Refresh gallery after delay
                    } else if (data.status === 'failed' || data.status === 'error') {
                        showMessage('Download failed: ' + (data.error || data.message || 'Unknown error'), 'error');
                    } else if (attempts < maxAttempts) {
                        attempts++;
                        setTimeout(checkProgress, 2000); // Check every 2 seconds
                    }
                }
            } catch (error) {
                console.error('Error checking progress:', error);
            }
        };
        
        checkProgress();
    }
    
    // Update progress display
    function updateProgressDisplay(data) {
        const progressContainer = document.getElementById('search-progress-container') ||
                                 document.querySelector('.progress-container');
        
        if (progressContainer) {
            progressContainer.style.display = 'block';
            
            const progressBar = progressContainer.querySelector('.progress-bar') ||
                               progressContainer.querySelector('[role="progressbar"]');
            
            if (progressBar && data.progress !== undefined) {
                progressBar.style.width = `${data.progress}%`;
                progressBar.textContent = `${Math.round(data.progress)}%`;
            }
            
            // Update status text
            const statusText = progressContainer.querySelector('.progress-status') ||
                             progressContainer.querySelector('.status-text');
            
            if (statusText) {
                statusText.textContent = data.message || `Processing... ${data.progress || 0}%`;
            }
        }
    }
    
    // Show message to user
    function showMessage(message, type = 'info') {
        console.log(`💬 ${type.toUpperCase()}: ${message}`);
        
        // Try to find or create message container
        let messageContainer = document.getElementById('message-container');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.id = 'message-container';
            messageContainer.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(messageContainer);
        }
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        messageContainer.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
    
    // Load and display gallery
    async function loadGallery() {
        console.log('🖼️ Loading gallery...');
        
        const gallery = document.getElementById('asset-library') ||
                       document.querySelector('.asset-grid') ||
                       document.querySelector('.gallery-grid') ||
                       document.querySelector('#gallery');
        
        if (!gallery) {
            console.log('⚠️ No gallery container found');
            return;
        }
        
        try {
            const response = await fetch(`${window.APP_BASE}/api/assets`, {
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Gallery data loaded:', data);
                
                // Clear loading state
                gallery.innerHTML = '';
                
                if (data.assets && data.assets.length > 0) {
                    // Create grid if needed
                    if (!gallery.classList.contains('asset-grid')) {
                        gallery.classList.add('asset-grid');
                    }
                    
                    data.assets.forEach(asset => {
                        const assetEl = createAssetElement(asset);
                        gallery.appendChild(assetEl);
                    });
                } else {
                    gallery.innerHTML = `
                        <div class="text-center py-5">
                            <i class="fas fa-images fa-3x text-muted mb-3"></i>
                            <p class="text-muted">No assets yet. Start downloading to build your library!</p>
                        </div>
                    `;
                }
            } else {
                throw new Error('Failed to load assets');
            }
        } catch (error) {
            console.error('❌ Gallery load error:', error);
            gallery.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    Unable to load gallery. Please refresh the page.
                </div>
            `;
        }
    }
    
    // Create asset element
    function createAssetElement(asset) {
        const div = document.createElement('div');
        div.className = 'asset-item gallery-item';
        div.style.cssText = `
            cursor: pointer;
            transition: transform 0.3s;
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
        `;
        
        // Determine media URL
        const mediaUrl = asset.url || `${window.APP_BASE}/api/media/${asset.id}`;
        const thumbnailUrl = asset.thumbnail_url || mediaUrl;
        
        // Create media element
        if (asset.media_type === 'video' || asset.file_extension === '.mp4') {
            div.innerHTML = `
                <video src="${mediaUrl}" poster="${thumbnailUrl}" style="width: 100%; height: 200px; object-fit: cover;">
                </video>
                <div class="asset-overlay" style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, rgba(0,0,0,0.8)); padding: 10px; color: white;">
                    <div style="font-size: 12px; font-weight: bold;">${asset.filename || 'Video'}</div>
                    <div style="font-size: 10px; opacity: 0.8;">${asset.source || 'Unknown'}</div>
                </div>
            `;
        } else {
            div.innerHTML = `
                <img src="${thumbnailUrl}" alt="${asset.filename || 'Image'}" style="width: 100%; height: 200px; object-fit: cover;" loading="lazy">
                <div class="asset-overlay" style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(transparent, rgba(0,0,0,0.8)); padding: 10px; color: white;">
                    <div style="font-size: 12px; font-weight: bold;">${asset.filename || 'Image'}</div>
                    <div style="font-size: 10px; opacity: 0.8;">${asset.source || 'Unknown'}</div>
                </div>
            `;
        }
        
        // Add hover effect
        div.addEventListener('mouseenter', () => {
            div.style.transform = 'scale(1.05)';
        });
        
        div.addEventListener('mouseleave', () => {
            div.style.transform = 'scale(1)';
        });
        
        // Add click to download
        div.addEventListener('click', () => {
            const downloadUrl = `${window.APP_BASE}/api/media/${asset.id}/download`;
            console.log('📥 Downloading:', downloadUrl);
            window.location.href = downloadUrl;
        });
        
        return div;
    }
    
    // Fix search form
    function fixSearchForm() {
        const searchForm = document.getElementById('search-form');
        if (!searchForm) return;
        
        console.log('🔧 Fixing search form...');
        
        // Remove old event listeners
        const newForm = searchForm.cloneNode(true);
        searchForm.parentNode.replaceChild(newForm, searchForm);
        
        // Add new handler
        newForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const query = document.getElementById('search-query')?.value;
            if (!query) {
                showMessage('Please enter a search query', 'warning');
                return;
            }
            
            // Get selected sources
            const selectedSources = [];
            document.querySelectorAll('input[type="checkbox"][name="sources"]:checked, .source-checkbox:checked').forEach(cb => {
                const sourceId = cb.value || cb.dataset.source || cb.id;
                if (sourceId) selectedSources.push(sourceId);
            });
            
            if (selectedSources.length === 0) {
                // Use default sources
                selectedSources.push('youtube', 'instagram', 'twitter');
            }
            
            console.log('🔍 Searching:', query, 'Sources:', selectedSources);
            
            // Show progress
            const progressContainer = document.getElementById('search-progress-container');
            if (progressContainer) {
                progressContainer.style.display = 'block';
            }
            
            // Start download
            await simpleDownload(query, selectedSources);
        });
    }
    
    // Initialize everything
    function initialize() {
        console.log('🚀 Initializing download & gallery fixes...');
        
        // Fix search form
        fixSearchForm();
        
        // Load gallery if on asset page
        if (window.location.pathname.includes('asset') || 
            document.getElementById('asset-library') ||
            document.querySelector('.asset-grid')) {
            loadGallery();
        }
        
        // Load stats
        loadStats();
        
        // Make functions globally available
        window.loadGallery = loadGallery;
        window.simpleDownload = simpleDownload;
        
        console.log('✅ Download & Gallery fixes initialized');
    }
    
    // Load stats
    async function loadStats() {
        try {
            const response = await fetch(`${window.APP_BASE}/api/stats`, {
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const stats = await response.json();
                console.log('📊 Stats:', stats);
                
                // Update stat displays
                ['total-downloads', 'total-assets', 'storage-used', 'active-jobs'].forEach(id => {
                    const el = document.getElementById(id);
                    if (el && stats[id.replace('-', '_')]) {
                        el.textContent = stats[id.replace('-', '_')];
                    }
                });
            }
        } catch (error) {
            console.error('Stats error:', error);
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Also initialize after a delay to catch late-loading elements
    setTimeout(initialize, 1000);
    
})();
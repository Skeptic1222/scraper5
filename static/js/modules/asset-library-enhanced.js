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
        this.selectAllUsed = false; // Track if Select All was clicked

        this.init();
    }
    
    init() {
        this.setupViewSwitching();
        this.loadAssets();
        this.setupRefreshButton();
        this.setupKeyboardNavigation();
        this.setupBulkDownload();
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

    setupBulkDownload() {
        console.log('[Setup] setupBulkDownload called');

        // Find ALL Download Selected buttons (there might be duplicates in the HTML)
        const downloadButtons = document.querySelectorAll('#download-selected-btn, [id="download-selected-btn"]');
        console.log(`[Setup] Found ${downloadButtons.length} download button(s)`);

        if (downloadButtons.length === 0) {
            console.log('[Setup] No buttons found in HTML, creating dynamically');
            // Fallback: Create button if it doesn't exist
            const deleteBtn = document.getElementById('delete-selected-btn');
            if (deleteBtn) {
                const downloadBtn = document.createElement('button');
                downloadBtn.type = 'button';
                downloadBtn.id = 'download-selected-btn';
                downloadBtn.className = 'btn btn-success';
                downloadBtn.style.cssText = 'display: inline-block !important; visibility: visible !important;';
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Selected';

                // Insert before delete button
                deleteBtn.parentNode.insertBefore(downloadBtn, deleteBtn);

                // Add event listener to the created button
                downloadBtn.addEventListener('click', () => {
                    console.log('[Setup] Download Selected button clicked (dynamic)!');
                    this.downloadSelected();
                });

                console.log('[Setup] Dynamic button created and event listener attached');
            } else {
                console.error('[Setup] Cannot create Download Selected button - delete button not found');
            }
            return;
        }

        // Attach event listeners to ALL download buttons found
        downloadButtons.forEach((btn, index) => {
            // Remove any existing event listeners by cloning
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);

            // Add fresh event listener
            newBtn.addEventListener('click', () => {
                console.log(`[Setup] Download Selected button ${index + 1} clicked!`);
                this.downloadSelected();
            });

            console.log(`[Setup] Event listener attached to Download Selected button ${index + 1}`);
        });
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
            // Request all assets (set high limit to get everything)
            const response = await fetch((window.APP_BASE || '/scraper') + '/api/assets?limit=10000', {
                credentials: 'include'
            });
            const data = await response.json();

            this.assets = data.assets || [];
            this.renderAssets();

            // Re-setup bulk download button after assets are loaded
            setTimeout(() => this.setupBulkDownload(), 100);

            // Update asset count in dashboard
            const totalAssetsElem = document.getElementById('total-assets');
            if (totalAssetsElem) {
                totalAssetsElem.textContent = this.assets.length;
            }

            // Also update dashboard total assets count
            const dashboardTotalAssets = document.getElementById('dashboard-total-assets');
            if (dashboardTotalAssets) {
                dashboardTotalAssets.textContent = this.assets.length;
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

        // Initialize lazy loading
        this.initLazyLoading();

        // Add hover handlers for video autoplay
        this.attachThumbnailHandlers();

        // Set initial focus
        if (this.focusedIndex >= 0 && this.focusedIndex < this.assets.length) {
            this.updateFocus();
        }
    }

    initLazyLoading() {
        // Use Intersection Observer for lazy loading images and videos
        const lazyElements = document.querySelectorAll('.lazy-load');

        if ('IntersectionObserver' in window) {
            const lazyObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;
                        const src = element.getAttribute('data-src');

                        if (src) {
                            element.src = src;
                            element.classList.remove('lazy-load');
                            observer.unobserve(element);
                        }
                    }
                });
            }, {
                rootMargin: '50px',  // Load 50px before entering viewport
                threshold: 0.01
            });

            lazyElements.forEach(element => {
                lazyObserver.observe(element);
            });
        } else {
            // Fallback for browsers without Intersection Observer
            lazyElements.forEach(element => {
                const src = element.getAttribute('data-src');
                if (src) element.src = src;
            });
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
                    <img data-src="${mediaUrl}" alt="${fileName}" loading="lazy" class="lazy-load">
                </div>
            `;
        } else if (isVideo) {
            thumbnailContent = `
                <div class="thumbnail-media video-preview">
                    <video data-src="${mediaUrl}" muted loop preload="none" class="lazy-load"></video>
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
                <!-- Selection checkbox -->
                <input type="checkbox" class="asset-checkbox" data-asset-id="${asset.id}"
                       style="position: absolute; top: 8px; right: 8px; width: 20px; height: 20px;
                              cursor: pointer; z-index: 10; accent-color: #3b82f6;">

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
                            <button class="btn-icon" onclick="assetLibrary.deleteAsset('${asset.id}')" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
                ${asset.source_name ? `
                <div class="asset-source-label" title="${asset.source_name}">
                    <i class="fas fa-tag" style="font-size: 0.7rem; opacity: 0.7; margin-right: 4px;"></i>
                    <span>${this.truncate(asset.source_name, 12)}</span>
                </div>` : ''}
            </div>
        `;
    }
    
    attachThumbnailHandlers() {
        const cards = document.querySelectorAll('.asset-card');

        cards.forEach((card, index) => {
            // Click to open viewer (but not on checkboxes or action buttons)
            card.addEventListener('click', (e) => {
                // Exclude clicks on checkboxes and action buttons
                if (!e.target.closest('.asset-actions') &&
                    !e.target.classList.contains('asset-checkbox') &&
                    e.target.type !== 'checkbox') {
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
                            <th>Source</th>
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
        
        const sourceDisplay = asset.source_name
            ? (asset.source_url
                ? `<a href="${asset.source_url}" target="_blank" style="color: #667eea; text-decoration: none;">${asset.source_name}</a>`
                : asset.source_name)
            : '<span class="text-muted">-</span>';

        return `
            <tr class="asset-list-row" data-index="${index}">
                <td>${preview}</td>
                <td>${fileName}</td>
                <td><span class="badge badge-secondary">${fileType}</span></td>
                <td>${size}</td>
                <td>${sourceDisplay}</td>
                <td>${date}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-sm btn-outline-primary" onclick="assetLibrary.openMediaViewer(${index})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="assetLibrary.downloadAsset('${asset.id}')">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="assetLibrary.deleteAsset('${asset.id}')">
                            <i class="fas fa-trash"></i>
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
        console.log(`[Download] downloadAsset called with ID: ${assetId}`);

        const asset = this.assets.find(a => a.id == assetId);
        if (!asset) {
            console.error('[Download] Asset not found:', assetId);
            console.log('[Download] Available assets:', this.assets.map(a => a.id));
            return;
        }

        try {
            console.log(`[Download] Starting download for asset ${assetId}: ${asset.filename}`);

            const downloadUrl = `${window.APP_BASE || '/scraper'}/api/media/${assetId}/download`;
            console.log(`[Download] Download URL: ${downloadUrl}`);

            // Method 1: Try fetch with blob (more reliable)
            try {
                const response = await fetch(downloadUrl, {
                    method: 'GET',
                    credentials: 'include'
                });

                console.log(`[Download] Fetch response status: ${response.status}`);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const blob = await response.blob();
                console.log(`[Download] Blob received, size: ${blob.size} bytes`);

                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = asset.filename || `asset_${assetId}`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);

                console.log(`[Download] Download initiated for ${asset.filename}`);
            } catch (fetchError) {
                console.error('[Download] Fetch method failed:', fetchError);

                // Method 2: Fallback to simple link (works for same-origin)
                console.log('[Download] Trying fallback method (direct link)');
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.download = asset.filename || `asset_${assetId}`;
                link.target = '_blank';  // Open in new tab if download fails
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                console.log(`[Download] Fallback download initiated`);
            }
        } catch (error) {
            console.error('[Download] Download error:', error);
        }
    }

    async downloadSelected() {
        console.log('[Download Selected] Function called');

        // Get all checked checkboxes
        const checkedBoxes = Array.from(document.querySelectorAll('.asset-checkbox:checked'));
        console.log(`[Download Selected] Found ${checkedBoxes.length} checked boxes`);

        if (checkedBoxes.length === 0) {
            console.log('[Download Selected] No assets selected');
            this.showError('Please select at least one asset to download');
            return;
        }

        const assetIds = checkedBoxes.map(cb => parseInt(cb.dataset.assetId)).filter(id => !isNaN(id));
        console.log(`[Download Selected] Asset IDs:`, assetIds);

        if (assetIds.length === 0) {
            console.log('[Download Selected] No valid asset IDs');
            this.showError('Invalid asset selection');
            return;
        }

        // Get button references
        const downloadBtn = document.getElementById('download-selected-btn');
        const originalHTML = downloadBtn ? downloadBtn.innerHTML : '';

        // Declare progress tracking variables at function level
        let progressInterval = null;
        let jobId = null;

        try {
            // Single file: direct download
            if (assetIds.length === 1) {
                console.log('[Download Selected] Single file - direct download');

                if (downloadBtn) {
                    downloadBtn.disabled = true;
                    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Preparing download...';
                }

                await this.downloadAsset(assetIds[0]);

                if (downloadBtn) {
                    downloadBtn.disabled = false;
                    downloadBtn.innerHTML = originalHTML;
                }
                return;
            }

            // Multiple files: create ZIP
            console.log('[Download Selected] Multiple files - creating ZIP');

            // Check global flag set by asset-selection.js
            const selectAllUsed = window.selectAllWasUsed || false;
            console.log('[Download Selected] Select All used:', selectAllUsed);

            if (downloadBtn) {
                downloadBtn.disabled = true;
                downloadBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Preparing... (0/${assetIds.length})`;
            }

            // Start the download request
            const fetchPromise = fetch(`${window.APP_BASE || '/scraper'}/api/media/bulk-download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    asset_ids: assetIds,
                    select_all_used: selectAllUsed  // Send flag to bypass limits
                })
            });

            // Try to get job_id from response header when available
            fetchPromise.then(response => {
                jobId = response.headers.get('X-Job-ID');
                console.log('[Download Selected] Job ID:', jobId);

                if (jobId && downloadBtn) {
                    // Start polling for progress
                    progressInterval = setInterval(async () => {
                        try {
                            const progressResponse = await fetch(
                                `${window.APP_BASE || '/scraper'}/api/media/bulk-download/progress/${jobId}`,
                                { credentials: 'include' }
                            );

                            if (progressResponse.ok) {
                                const progress = await progressResponse.json();
                                console.log('[Progress]', progress);

                                const percentage = Math.round((progress.processed / progress.total) * 100);
                                downloadBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${progress.message || `${progress.processed}/${progress.total}`} (${percentage}%)`;

                                if (progress.status === 'complete' || progress.status === 'failed') {
                                    clearInterval(progressInterval);
                                    if (progress.status === 'complete') {
                                        downloadBtn.innerHTML = `<i class="fas fa-check"></i> Downloading...`;
                                    }
                                }
                            }
                        } catch (err) {
                            console.error('[Progress] Error:', err);
                        }
                    }, 500);
                }
            });

            const response = await fetchPromise;

            // Clear progress polling when download starts
            if (progressInterval) {
                clearInterval(progressInterval);
            }

            console.log(`[Download Selected] Response status: ${response.status}`);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({error: 'Server error'}));
                console.error('[Download Selected] Server error:', errorData);
                throw new Error(errorData.error || `Server error (${response.status})`);
            }

            // Get file info from headers
            const filesAdded = response.headers.get('X-Files-Added');
            const filesFailed = response.headers.get('X-Files-Failed');
            console.log(`[Download Selected] Files added: ${filesAdded}, failed: ${filesFailed}`);

            // Download the ZIP file
            const blob = await response.blob();
            console.log(`[Download Selected] ZIP size: ${blob.size} bytes`);

            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;

            // Get filename from Content-Disposition header or use default
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'assets_download.zip';
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^"]+)"?/);
                if (match) {
                    filename = match[1];
                }
            }

            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);

            console.log(`[Download Selected] ZIP download initiated: ${filename}`);

        } catch (error) {
            console.error('[Download Selected] Error:', error);
            this.showError(`Download failed: ${error.message}`);
        } finally {
            // Clear any remaining progress polling
            if (progressInterval) {
                clearInterval(progressInterval);
            }

            // Restore button
            if (downloadBtn) {
                downloadBtn.disabled = false;
                downloadBtn.innerHTML = originalHTML;
            }

            // Reset the Select All flag after download attempt
            this.selectAllUsed = false;
        }
    }

    async deleteAsset(assetId) {
        if (!confirm('Are you sure you want to delete this asset?')) {
            return;
        }

        try {
            const response = await fetch(`${window.APP_BASE || '/scraper'}/api/assets/${assetId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (response.ok) {
                // Remove from DOM immediately
                const assetCard = document.querySelector(`.asset-card[data-asset-id="${assetId}"]`);
                if (assetCard) {
                    assetCard.style.transition = 'opacity 0.3s ease';
                    assetCard.style.opacity = '0';
                    setTimeout(() => assetCard.remove(), 300);
                }

                // Remove from internal assets array
                this.assets = this.assets.filter(a => a.id != assetId);

                // Update total count
                const totalElement = document.querySelector('#total-assets');
                if (totalElement) {
                    const currentTotal = parseInt(totalElement.textContent) || 0;
                    totalElement.textContent = Math.max(0, currentTotal - 1);
                }

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
        console.log('Success:', message);

        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast-notification toast-success';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        toast.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    showError(message) {
        console.error('Error:', message);

        // Create toast notification
        const toast = document.createElement('div');
        toast.className = 'toast-notification toast-error';
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        toast.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Initialize asset library
window.assetLibrary = new AssetLibraryEnhanced();
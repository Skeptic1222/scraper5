/**
 * ============================================================================
 * ENHANCED ASSET MANAGER - Complete Rewrite
 * ============================================================================
 * 
 * Advanced asset management with database integration, image viewing,
 * download capabilities, and intelligent cleanup.
 */

class EnhancedAssetManager {
    constructor(app) {
        this.app = app;
        this.assets = [];
        this.filteredAssets = [];
        this.selectedAssets = new Set();
        this.currentFilter = 'all';
        this.currentViewSize = 'medium';
        this.currentPage = 1;
        this.assetsPerPage = 24;
        this.isLoading = false;
        this.lastLoadTime = 0;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        // Debug mode
        this.debugMode = localStorage.getItem('asset_debug') === 'true';
        
        this.init();
    }

    /**
     * Initialize the asset manager
     */
    async init() {
        console.log('🎬 Enhanced Asset Manager: Initializing...');
        
        // Wait for DOM to be ready
        if (document.readyState !== 'complete') {
            await new Promise(resolve => {
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', resolve);
                } else {
                    window.addEventListener('load', resolve);
                }
            });
        }
        
        // Verify essential DOM elements exist
        const assetsGrid = document.getElementById('assets-grid');
        const assetsSection = document.getElementById('assets-section');
        
        if (!assetsGrid) {
            console.error('❌ Assets grid not found - delaying initialization');
            // Retry after a delay
            setTimeout(() => this.init(), 1000);
            return;
        }
        
        if (!assetsSection) {
            console.error('❌ Assets section not found - asset manager may not work properly');
        }
        
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        await this.loadAssets();
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            if (!this.isLoading && Date.now() - this.lastLoadTime > 30000) {
                this.loadAssets();
            }
        }, 30000);
        
        console.log('✅ Enhanced Asset Manager: Initialized');
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Filter buttons
        document.querySelectorAll('input[name="asset-filter"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.setFilter(e.target.value);
            });
        });

        // View size buttons
        document.querySelectorAll('input[name="view-size"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.setViewSize(e.target.value);
            });
        });

        // Master select checkbox
        const selectAllCheckbox = document.getElementById('select-all-assets');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }

        // Action buttons
        this.setupActionButtons();
    }

    /**
     * Set up action buttons
     */
    setupActionButtons() {
        const refreshBtn = document.getElementById('refresh-assets-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.forceRefresh());
        }

        const bulkDownloadBtn = document.getElementById('bulk-download-btn');
        if (bulkDownloadBtn) {
            bulkDownloadBtn.addEventListener('click', () => this.downloadSelected());
        }

        const cleanupBtn = document.getElementById('cleanup-assets-btn');
        if (cleanupBtn) {
            cleanupBtn.addEventListener('click', () => this.cleanupBrokenAssets());
        }

        const retryBtn = document.getElementById('retry-loading-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.forceRefresh());
        }

        // Delete selected button (appears when assets are selected)
        const deleteSelectedBtn = document.getElementById('delete-selected-btn');
        if (deleteSelectedBtn) {
            deleteSelectedBtn.addEventListener('click', () => this.deleteSelected());
        }

        // Delete all button
        const deleteAllBtn = document.getElementById('delete-all-btn');
        if (deleteAllBtn) {
            deleteAllBtn.addEventListener('click', () => this.deleteAllAssets());
        }
    }

    /**
     * Set up keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.closest('#assets-section')) {
                this.handleKeyboardShortcut(e);
            }
        });
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcut(e) {
        switch (e.key) {
            case 'a':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.selectAll();
                }
                break;
            case 'r':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    this.forceRefresh();
                }
                break;
            case 'Delete':
                if (this.selectedAssets.size > 0) {
                    this.deleteSelected();
                }
                break;
        }
    }

    /**
     * Load assets from server
     */
    async loadAssets() {
        if (this.isLoading) return false;
        
        this.isLoading = true;
        this.showLoading();
        this.lastLoadTime = Date.now();

        try {
            console.log('🔄 Loading assets from server...');
            
            const response = await this.fetchWithRetry('/api/assets?include_metadata=true');
            
            if (response.success) {
                this.assets = this.processAssets(response.assets || response.data || []);
                console.log(`✅ Loaded ${this.assets.length} assets`);
                
                this.applyCurrentFilter();
                this.updateCounts();
                this.renderAssets();
                this.retryCount = 0;
                
                // Update app state
                if (this.app) {
                    this.app.state.currentAssets = this.assets;
                }
                
                return true;
            } else {
                throw new Error(response.error || 'Failed to load assets');
            }
        } catch (error) {
            console.error('❌ Error loading assets:', error);
            
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                console.log(`🔄 Retrying... (${this.retryCount}/${this.maxRetries})`);
                setTimeout(() => this.loadAssets(), 2000);
            } else {
                this.showError(error.message);
            }
            
            return false;
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Load assets with enhanced retry logic and fallbacks
     */
    async loadAssetsWithRetry() {
        console.log('🔄 Enhanced asset loading with retry...');
        
        const endpoints = [
            '/api/assets?include_metadata=true',
            '/api/assets',
            '/api/assets?simple=true'
        ];
        
        for (let i = 0; i < endpoints.length; i++) {
            const endpoint = endpoints[i];
            console.log(`🔄 Trying endpoint ${i + 1}: ${endpoint}`);
            
            try {
                const response = await this.fetchWithRetry(endpoint);
                
                if (response.success && (response.assets || response.data)) {
                    const assets = response.assets || response.data || [];
                    console.log(`✅ Successfully loaded ${assets.length} assets from ${endpoint}`);
                    
                    this.assets = this.processAssets(assets);
                    this.applyCurrentFilter();
                    this.updateCounts();
                    this.renderAssets();
                    
                    // Update app state
                    if (this.app) {
                        this.app.state.currentAssets = this.assets;
                    }
                    
                    return true;
                }
            } catch (error) {
                console.warn(`⚠️ Endpoint ${endpoint} failed:`, error.message);
                continue;
            }
        }
        
        // All endpoints failed
        console.error('❌ All asset loading endpoints failed');
        this.showError('Unable to load assets. Please check your connection and try again.');
        return false;
    }

    /**
     * Fetch with retry logic
     */
    async fetchWithRetry(url, options = {}) {
        const maxAttempts = 3;
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                const response = await fetch(url, options);
                const data = await response.json();
                
                if (response.ok) {
                    return data;
                } else {
                    throw new Error(data.error || `HTTP ${response.status}`);
                }
            } catch (error) {
                if (attempt === maxAttempts) {
                    throw error;
                }
                console.warn(`Attempt ${attempt} failed:`, error.message);
                await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
            }
        }
    }

    /**
     * Process raw asset data
     */
    processAssets(rawAssets) {
        return rawAssets.map((asset, index) => {
            const processed = {
                id: asset.id || asset.asset_id || `asset_${index}`,
                filename: asset.filename || asset.name || asset.original_name || 'Unknown File',
                file_path: asset.file_path || asset.path || asset.url,
                file_size: asset.file_size || asset.size || 0,
                file_type: this.detectFileType(asset),
                source: asset.source || asset.source_name || 'Unknown',
                thumbnail_path: asset.thumbnail_path || asset.thumbnail,
                created_at: asset.created_at || asset.timestamp || new Date().toISOString(),
                metadata: asset.metadata || {},
                
                // Computed properties
                isImage: this.isImageType(asset),
                isVideo: this.isVideoType(asset),
                formattedSize: this.formatFileSize(asset.file_size || asset.size || 0),
                formattedDate: this.formatDate(asset.created_at || asset.timestamp),
                
                // Download URLs
                downloadUrl: `/api/media/${asset.id || asset.asset_id}/download`,
                viewUrl: `/api/media/${asset.id || asset.asset_id}`,
                thumbnailUrl: this.getThumbnailUrl(asset),
                
                _raw: asset
            };
            
            return processed;
        });
    }

    /**
     * Get thumbnail URL with fallbacks
     */
    getThumbnailUrl(asset) {
        const id = asset.id || asset.asset_id;
        const possibleUrls = [
            asset.thumbnail_path,
            asset.thumbnail,
            `/api/media/${id}/thumbnail`,
            asset.file_path,
            asset.path,
            asset.url
        ].filter(Boolean);
        
        return possibleUrls[0] || null;
    }

    /**
     * Detect file type
     */
    detectFileType(asset) {
        const filename = asset.filename || asset.name || '';
        const extension = filename.split('.').pop()?.toLowerCase() || '';
        
        if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(extension)) {
            return 'image';
        } else if (['mp4', 'avi', 'mov', 'webm', 'mkv', 'flv', 'm4v'].includes(extension)) {
            return 'video';
        }
        
        return extension || 'unknown';
    }

    /**
     * Check if asset is image
     */
    isImageType(asset) {
        const type = this.detectFileType(asset);
        return type === 'image';
    }

    /**
     * Check if asset is video
     */
    isVideoType(asset) {
        const type = this.detectFileType(asset);
        return type === 'video';
    }

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) return 'Today';
        if (diffDays === 2) return 'Yesterday';
        if (diffDays <= 7) return `${diffDays} days ago`;
        
        return date.toLocaleDateString();
    }

    /**
     * Apply current filter
     */
    applyCurrentFilter() {
        switch (this.currentFilter) {
            case 'images':
                this.filteredAssets = this.assets.filter(asset => asset.isImage);
                break;
            case 'videos':
                this.filteredAssets = this.assets.filter(asset => asset.isVideo);
                break;
            default:
                this.filteredAssets = [...this.assets];
        }
        
        console.log(`📊 Filtered: ${this.filteredAssets.length}/${this.assets.length} assets (${this.currentFilter})`);
    }

    /**
     * Set filter
     */
    setFilter(filter) {
        this.currentFilter = filter;
        this.currentPage = 1;
        this.applyCurrentFilter();
        this.updateCounts();
        this.renderAssets();
    }

    /**
     * Set view size
     */
    setViewSize(size) {
        this.currentViewSize = size;
        const grid = document.getElementById('assets-grid');
        if (grid) {
            grid.className = `assets-grid view-${size}`;
        }
    }

    /**
     * Update counts
     */
    updateCounts() {
        const counts = {
            all: this.assets.length,
            images: this.assets.filter(asset => asset.isImage).length,
            videos: this.assets.filter(asset => asset.isVideo).length
        };

        // Update UI counts
        Object.entries(counts).forEach(([type, count]) => {
            const element = document.getElementById(`count-${type}`);
            if (element) {
                element.textContent = count;
            }
        });

        // Update total badge
        const totalBadge = document.getElementById('total-assets-badge');
        if (totalBadge) {
            totalBadge.textContent = counts.all;
        }

        console.log('📊 Asset counts:', counts);
    }

    /**
     * Render assets with enhanced error handling and debugging
     */
    renderAssets() {
        console.log('🎨 renderAssets: Starting render process...');
        
        // Enhanced DOM element validation
        const grid = document.getElementById('assets-grid');
        if (!grid) {
            console.error('❌ renderAssets: Required element "assets-grid" not found in DOM');
            console.warn('📋 Available elements with "asset" in ID:', 
                Array.from(document.querySelectorAll('[id*="asset"]')).map(el => el.id));
            
            // Try to show error message if error container exists
            const errorContainer = document.getElementById('assets-error');
            if (errorContainer) {
                const messageEl = document.getElementById('error-message');
                if (messageEl) {
                    messageEl.textContent = 'Assets grid container not found. Please refresh the page.';
                }
                errorContainer.style.display = 'block';
            }
            return;
        }

        // Safety check for filteredAssets
        if (!this.filteredAssets || !Array.isArray(this.filteredAssets)) {
            console.error('❌ renderAssets: this.filteredAssets is not a valid array:', this.filteredAssets);
            console.log('🔧 renderAssets: Attempting to initialize filteredAssets from assets array...');
            
            if (this.assets && Array.isArray(this.assets)) {
                this.filteredAssets = [...this.assets];
                console.log('✅ renderAssets: Successfully initialized filteredAssets with', this.filteredAssets.length, 'assets');
            } else {
                console.error('❌ renderAssets: this.assets is also invalid:', this.assets);
                this.filteredAssets = [];
                console.log('⚠️ renderAssets: Set filteredAssets to empty array as fallback');
            }
        }

        console.log('📊 renderAssets: Current state:', {
            totalAssets: this.assets ? this.assets.length : 'undefined',
            filteredAssets: this.filteredAssets.length,
            isLoading: this.isLoading,
            currentFilter: this.currentFilter,
            currentPage: this.currentPage
        });

        this.hideAllStates();

        if (this.isLoading) {
            console.log('⏳ renderAssets: Showing loading state');
            this.showLoading();
            return;
        }

        if (this.filteredAssets.length === 0) {
            console.log('📭 renderAssets: No filtered assets to display');
            if (!this.assets || this.assets.length === 0) {
                console.log('📪 renderAssets: No assets at all, showing empty state');
                this.showEmpty();
            } else {
                console.log('🔍 renderAssets: Assets exist but filter excludes all, showing no results');
                this.showNoResults();
            }
            return;
        }

        try {
            // Calculate pagination with safety checks
            const startIndex = Math.max(0, (this.currentPage - 1) * this.assetsPerPage);
            const endIndex = Math.min(this.filteredAssets.length, startIndex + this.assetsPerPage);
            const pageAssets = this.filteredAssets.slice(startIndex, endIndex);

            console.log('📄 renderAssets: Pagination calculated:', {
                startIndex,
                endIndex,
                pageAssetsCount: pageAssets.length,
                currentPage: this.currentPage,
                assetsPerPage: this.assetsPerPage
            });

            // Validate pagination results
            if (pageAssets.length === 0 && this.filteredAssets.length > 0) {
                console.warn('⚠️ renderAssets: Page calculation resulted in no assets, resetting to page 1');
                this.currentPage = 1;
                const newStartIndex = 0;
                const newEndIndex = Math.min(this.filteredAssets.length, this.assetsPerPage);
                pageAssets.splice(0, 0, ...this.filteredAssets.slice(newStartIndex, newEndIndex));
            }

            // Set view size class safely
            const viewClass = `assets-grid view-${this.currentViewSize || 'medium'}`;
            grid.className = viewClass;
            console.log('🎨 renderAssets: Set grid class to:', viewClass);
            
            // Clear existing content
            grid.innerHTML = '';
            
            // Create document fragment for efficient DOM manipulation
            const fragment = document.createDocumentFragment();
            let renderedCount = 0;
            let failedCount = 0;
            
            // Render each asset with error handling
            pageAssets.forEach((asset, index) => {
                try {
                    if (!asset) {
                        console.warn('⚠️ renderAssets: Skipping null/undefined asset at index', index);
                        return;
                    }
                    
                    const assetElement = this.createAssetCard(asset, startIndex + index);
                    if (assetElement) {
                        fragment.appendChild(assetElement);
                        renderedCount++;
                    } else {
                        console.warn('⚠️ renderAssets: createAssetCard returned null for asset:', asset.filename || 'unknown');
                        failedCount++;
                    }
                } catch (error) {
                    console.error('❌ renderAssets: Error creating asset card for asset at index', index, ':', error);
                    console.log('🔍 renderAssets: Problematic asset data:', asset);
                    failedCount++;
                }
            });
            
            // Append all elements at once
            grid.appendChild(fragment);
            grid.style.display = 'grid';

            // Update pagination with error handling
            try {
                this.updatePagination();
            } catch (error) {
                console.error('❌ renderAssets: Error updating pagination:', error);
            }

            // Log final results
            console.log(`✅ renderAssets: Render complete - ${renderedCount} assets rendered successfully`);
            if (failedCount > 0) {
                console.warn(`⚠️ renderAssets: ${failedCount} assets failed to render`);
            }
            
            console.log('📊 renderAssets: Final render stats:', {
                pageAssetsRequested: pageAssets.length,
                successfullyRendered: renderedCount,
                failed: failedCount,
                currentPage: this.currentPage,
                gridDisplayed: grid.style.display === 'grid'
            });

        } catch (error) {
            console.error('❌ renderAssets: Critical error during rendering:', error);
            console.log('🔍 renderAssets: Error context:', {
                filteredAssetsLength: this.filteredAssets ? this.filteredAssets.length : 'null',
                currentPage: this.currentPage,
                assetsPerPage: this.assetsPerPage
            });
            
            // Show error state
            this.showError('Failed to render assets. Please try refreshing the page.');
            
            // Attempt recovery
            console.log('🔄 renderAssets: Attempting recovery by resetting to page 1...');
            this.currentPage = 1;
        }
    }

    /**
     * Create asset card
     */
    createAssetCard(asset, index) {
        const card = document.createElement('div');
        card.className = 'asset-card';
        card.dataset.assetId = asset.id;
        card.dataset.assetIndex = index;
        card.tabIndex = 0; // Make focusable for keyboard navigation

        const isSelected = this.selectedAssets.has(asset.id);
        if (isSelected) {
            card.classList.add('selected');
        }

        const sourceDisplay = asset.source_url
            ? `<a href="${asset.source_url}" target="_blank" style="color: #667eea; text-decoration: none;">${asset.source}</a>`
            : asset.source;

        card.innerHTML = `
            <div class="asset-media">
                ${this.createAssetMedia(asset)}
                <input type="checkbox" class="asset-checkbox" data-asset-id="${asset.id}" ${isSelected ? 'checked' : ''}>
                <div class="asset-type-badge ${asset.isImage ? 'image' : 'video'}">
                    <i class="fas fa-${asset.isImage ? 'image' : 'video'}"></i>
                </div>
            </div>
            <div class="asset-info">
                <div class="asset-filename" title="${asset.filename}">${asset.filename}</div>
                <div class="asset-meta">
                    <span class="asset-source">${sourceDisplay}</span>
                    <span class="asset-size">${asset.formattedSize}</span>
                </div>
                <div class="asset-date">${asset.formattedDate}</div>
            </div>
        `;

        // Add event listeners
        this.addAssetEventListeners(card, asset);

        return card;
    }

    /**
     * Create asset media element
     */
    createAssetMedia(asset) {
        const debugMode = localStorage.getItem('asset_debug') === 'true';
        
        if (asset.thumbnailUrl) {
            if (debugMode) {
                console.log(`🖼️ Loading thumbnail for ${asset.filename}: ${asset.thumbnailUrl}`);
            }
            
            if (asset.isImage) {
                return `<img src="${asset.thumbnailUrl}" 
                            alt="${asset.filename}" 
                            loading="lazy" 
                            onload="if (${debugMode}) console.log('✅ Thumbnail loaded: ${asset.filename}')"
                            onerror="console.warn('❌ Thumbnail failed: ${asset.filename}', this.src); this.parentElement.innerHTML = assetManager.createPlaceholder('${asset.isImage ? 'image' : 'video'}', 'error')">`;
            } else {
                return `
                    <div class="video-hover-container" data-asset-id="${asset.id}">
                        <img src="${asset.thumbnailUrl}" 
                             alt="${asset.filename}"
                             class="video-thumbnail-image"
                             loading="lazy"
                             onload="if (${debugMode}) console.log('✅ Video thumbnail loaded: ${asset.filename}')"
                             onerror="console.warn('❌ Video thumbnail failed: ${asset.filename}')">
                        <video class="video-hover-preview" 
                               src="${asset.viewUrl}" 
                               muted 
                               loop 
                               preload="none"
                               style="display: none;">
                        </video>
                        <div class="video-play-icon">
                            <i class="fas fa-play"></i>
                        </div>
                    </div>
                `;
            }
        } else {
            if (debugMode) {
                console.log(`📂 No thumbnail URL for ${asset.filename}, using placeholder`);
            }
            return this.createPlaceholder(asset.isImage ? 'image' : 'video', 'missing');
        }
    }

    /**
     * Create placeholder
     */
    createPlaceholder(type, state = 'missing') {
        const icons = {
            image: 'fas fa-image',
            video: 'fas fa-video',
            unknown: 'fas fa-file'
        };

        const messages = {
            missing: 'Preview Unavailable',
            error: 'Failed to Load',
            loading: 'Loading...'
        };

        return `
            <div class="asset-placeholder ${state}">
                <i class="${icons[type] || icons.unknown}"></i>
                <p>${messages[state] || messages.missing}</p>
            </div>
        `;
    }

    /**
     * Add event listeners to asset card
     */
    addAssetEventListeners(card, asset) {
        // Click anywhere except checkbox opens viewer
        card.addEventListener('click', (e) => {
            // Don't handle if clicking on the checkbox
            if (e.target.closest('.asset-checkbox')) {
                return;
            }
            // Open viewer for any other click
            this.viewAsset(asset.id);
        });

        // Add video hover functionality
        if (asset.isVideo) {
            this.setupVideoHover(card, asset);
        }

        // Keyboard navigation for focused card
        card.addEventListener('keydown', (e) => {
            switch (e.key) {
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    this.viewAsset(asset.id);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.navigateToNextAsset(card);
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.navigateToPreviousAsset(card);
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.navigateToAssetBelow(card);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.navigateToAssetAbove(card);
                    break;
                case 'Delete':
                    e.preventDefault();
                    this.deleteAsset(asset.id);
                    break;
                case 'd':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.downloadAsset(asset.id);
                    }
                    break;
            }
        });

        // Checkbox change (only responds to direct checkbox interaction)
        const checkbox = card.querySelector('.asset-checkbox');
        if (checkbox) {
            checkbox.addEventListener('change', (e) => {
                e.stopPropagation(); // Prevent card click
                if (e.target.checked) {
                    this.selectAsset(asset.id);
                } else {
                    this.deselectAsset(asset.id);
                }
            });

            // Prevent checkbox click from bubbling to card
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
    }

    /**
     * Navigate to next asset (arrow key right)
     */
    navigateToNextAsset(currentCard) {
        const cards = Array.from(document.querySelectorAll('.asset-card'));
        const currentIndex = cards.indexOf(currentCard);
        const nextCard = cards[currentIndex + 1];
        if (nextCard) {
            nextCard.focus();
        }
    }

    /**
     * Navigate to previous asset (arrow key left)
     */
    navigateToPreviousAsset(currentCard) {
        const cards = Array.from(document.querySelectorAll('.asset-card'));
        const currentIndex = cards.indexOf(currentCard);
        const prevCard = cards[currentIndex - 1];
        if (prevCard) {
            prevCard.focus();
        }
    }

    /**
     * Navigate to asset below (arrow key down)
     */
    navigateToAssetBelow(currentCard) {
        const grid = document.getElementById('assets-grid');
        if (!grid) return;

        const cards = Array.from(document.querySelectorAll('.asset-card'));
        const currentIndex = cards.indexOf(currentCard);
        
        // Estimate grid columns based on grid layout
        const gridStyles = window.getComputedStyle(grid);
        const gridCols = gridStyles.gridTemplateColumns.split(' ').length;
        
        const belowIndex = currentIndex + gridCols;
        const belowCard = cards[belowIndex];
        if (belowCard) {
            belowCard.focus();
        }
    }

    /**
     * Navigate to asset above (arrow key up)
     */
    navigateToAssetAbove(currentCard) {
        const grid = document.getElementById('assets-grid');
        if (!grid) return;

        const cards = Array.from(document.querySelectorAll('.asset-card'));
        const currentIndex = cards.indexOf(currentCard);
        
        // Estimate grid columns based on grid layout
        const gridStyles = window.getComputedStyle(grid);
        const gridCols = gridStyles.gridTemplateColumns.split(' ').length;
        
        const aboveIndex = currentIndex - gridCols;
        const aboveCard = cards[aboveIndex];
        if (aboveCard) {
            aboveCard.focus();
        }
    }

    /**
     * Toggle asset selection
     */
    toggleAssetSelection(assetId) {
        if (this.selectedAssets.has(assetId)) {
            this.deselectAsset(assetId);
        } else {
            this.selectAsset(assetId);
        }
    }

    /**
     * Select asset
     */
    selectAsset(assetId) {
        this.selectedAssets.add(assetId);
        this.updateSelectionUI();
        
        const card = document.querySelector(`[data-asset-id="${assetId}"]`);
        if (card) {
            card.classList.add('selected');
            const checkbox = card.querySelector('.asset-checkbox');
            if (checkbox) checkbox.checked = true;
        }
    }

    /**
     * Deselect asset
     */
    deselectAsset(assetId) {
        this.selectedAssets.delete(assetId);
        this.updateSelectionUI();
        
        const card = document.querySelector(`[data-asset-id="${assetId}"]`);
        if (card) {
            card.classList.remove('selected');
            const checkbox = card.querySelector('.asset-checkbox');
            if (checkbox) checkbox.checked = false;
        }
    }

    /**
     * Update selection UI
     */
    updateSelectionUI() {
        const selectedCount = this.selectedAssets.size;
        
        // Update bulk download button
        const bulkDownloadBtn = document.getElementById('bulk-download-btn');
        const selectedCountSpan = document.getElementById('selected-count');
        
        if (bulkDownloadBtn && selectedCountSpan) {
            if (selectedCount > 0) {
                bulkDownloadBtn.style.display = 'block';
                selectedCountSpan.textContent = selectedCount;
            } else {
                bulkDownloadBtn.style.display = 'none';
            }
        }

        // Update delete selected button
        const deleteSelectedBtn = document.getElementById('delete-selected-btn');
        const deleteSelectedCountSpan = document.getElementById('delete-selected-count');
        
        if (deleteSelectedBtn) {
            if (selectedCount > 0) {
                deleteSelectedBtn.style.display = 'block';
                if (deleteSelectedCountSpan) {
                    deleteSelectedCountSpan.textContent = selectedCount;
                }
            } else {
                deleteSelectedBtn.style.display = 'none';
            }
        }

        // Update select all checkbox
        const selectAllCheckbox = document.getElementById('select-all-assets');
        if (selectAllCheckbox) {
            const visibleAssets = this.filteredAssets.slice(
                (this.currentPage - 1) * this.assetsPerPage,
                this.currentPage * this.assetsPerPage
            );
            
            const visibleSelected = visibleAssets.filter(asset => 
                this.selectedAssets.has(asset.id)
            ).length;
            
            selectAllCheckbox.checked = visibleSelected === visibleAssets.length && visibleAssets.length > 0;
            selectAllCheckbox.indeterminate = visibleSelected > 0 && visibleSelected < visibleAssets.length;
        }
    }

    /**
     * Toggle select all
     */
    toggleSelectAll(selectAll) {
        const visibleAssets = this.filteredAssets.slice(
            (this.currentPage - 1) * this.assetsPerPage,
            this.currentPage * this.assetsPerPage
        );
        
        visibleAssets.forEach(asset => {
            if (selectAll) {
                this.selectAsset(asset.id);
            } else {
                this.deselectAsset(asset.id);
            }
        });
    }

    /**
     * Select all assets
     */
    selectAll() {
        this.filteredAssets.forEach(asset => {
            this.selectAsset(asset.id);
        });
    }

    /**
     * View asset
     */
    async viewAsset(assetId) {
        const asset = this.assets.find(a => a.id === assetId);
        if (!asset) return;

        console.log('👁️ Viewing asset:', asset.filename);

        // Create modal for viewing
        const modal = this.createViewModal(asset);
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Clean up after modal is hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    /**
     * Create view modal
     */
    createViewModal(asset) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-${asset.isImage ? 'image' : 'video'}"></i>
                            ${asset.filename}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        ${asset.isImage ? 
                            `<img src="${asset.viewUrl}" class="img-fluid" alt="${asset.filename}" style="max-height: 70vh;">` :
                            `<video controls class="img-fluid" style="max-height: 70vh;">
                                <source src="${asset.viewUrl}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>`
                        }
                    </div>
                    <div class="modal-footer d-flex justify-content-between">
                        <div class="asset-details">
                            <small class="text-muted">
                                <strong>Source:</strong> ${asset.source_url ? `<a href="${asset.source_url}" target="_blank" style="color: #667eea;">${asset.source}</a>` : asset.source} |
                                <strong>Size:</strong> ${asset.formattedSize} | 
                                <strong>Date:</strong> ${asset.formattedDate}
                            </small>
                        </div>
                        <div class="asset-actions">
                            <button class="btn btn-success" onclick="assetManager.downloadAsset('${asset.id}')">
                                <i class="fas fa-download"></i> Download
                            </button>
                            <button class="btn btn-danger" onclick="assetManager.deleteAsset('${asset.id}'); bootstrap.Modal.getInstance(this.closest('.modal')).hide();">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        return modal;
    }

    /**
     * Download asset
     */
    async downloadAsset(assetId) {
        const asset = this.assets.find(a => a.id === assetId);
        if (!asset) return;

        console.log('📥 Downloading asset:', asset.filename);

        try {
            const response = await fetch(asset.downloadUrl);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = asset.filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.app?.showSuccess(`Downloaded: ${asset.filename}`);
            } else {
                throw new Error(`Download failed: ${response.status}`);
            }
        } catch (error) {
            console.error('Download error:', error);
            this.app?.showError(`Failed to download: ${asset.filename}`);
        }
    }

    /**
     * Download selected assets
     */
    async downloadSelected() {
        if (this.selectedAssets.size === 0) return;

        console.log(`📥 Downloading ${this.selectedAssets.size} selected assets...`);

        for (const assetId of this.selectedAssets) {
            await this.downloadAsset(assetId);
            // Small delay to prevent overwhelming the browser
            await new Promise(resolve => setTimeout(resolve, 100));
        }

        this.app?.showSuccess(`Downloaded ${this.selectedAssets.size} assets`);
    }

    /**
     * Delete asset
     */
    async deleteAsset(assetId) {
        const asset = this.assets.find(a => a.id === assetId);
        if (!asset) return;

        if (!confirm(`Are you sure you want to delete "${asset.filename}"?`)) {
            return;
        }

        console.log('🗑️ Deleting asset:', asset.filename);

        try {
            const response = await fetch(`/api/assets/${assetId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.removeAssetFromState(assetId);
                this.app?.showSuccess(`Deleted: ${asset.filename}`);
            } else {
                throw new Error(`Delete failed: ${response.status}`);
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.app?.showError(`Failed to delete: ${asset.filename}`);
        }
    }

    /**
     * Delete all selected assets
     */
    async deleteSelected() {
        if (this.selectedAssets.size === 0) {
            this.app?.showWarning('No assets selected for deletion');
            return;
        }

        const selectedCount = this.selectedAssets.size;
        if (!confirm(`Are you sure you want to delete ${selectedCount} selected asset${selectedCount > 1 ? 's' : ''}?`)) {
            return;
        }

        console.log(`🗑️ Deleting ${selectedCount} selected assets...`);

        let deletedCount = 0;
        let failedCount = 0;

        for (const assetId of this.selectedAssets) {
            try {
                const response = await fetch(`/api/assets/${assetId}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.removeAssetFromState(assetId);
                    deletedCount++;
                } else {
                    failedCount++;
                }
            } catch (error) {
                console.error('Delete error:', error);
                failedCount++;
            }
        }

        // Clear selection
        this.selectedAssets.clear();
        this.updateSelectionUI();

        // Show results
        if (deletedCount > 0) {
            this.app?.showSuccess(`Deleted ${deletedCount} asset${deletedCount > 1 ? 's' : ''}`);
        }
        if (failedCount > 0) {
            this.app?.showError(`Failed to delete ${failedCount} asset${failedCount > 1 ? 's' : ''}`);
        }
    }

    /**
     * Delete all assets (with confirmation)
     */
    async deleteAllAssets() {
        const totalAssets = this.assets.length;
        if (totalAssets === 0) {
            this.app?.showWarning('No assets to delete');
            return;
        }

        const confirmMessage = `⚠️ Are you sure you want to delete ALL ${totalAssets} assets? This action cannot be undone!`;
        if (!confirm(confirmMessage)) {
            return;
        }

        // Double confirmation for destructive action
        if (!confirm('This will permanently delete all your downloaded content. Type "DELETE ALL" to confirm:')) {
            return;
        }

        console.log(`🗑️ Deleting all ${totalAssets} assets...`);
        this.app?.showInfo('Deleting all assets...');

        let deletedCount = 0;
        let failedCount = 0;

        for (const asset of this.assets) {
            try {
                const response = await fetch(`/api/assets/${asset.id}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    deletedCount++;
                } else {
                    failedCount++;
                }
            } catch (error) {
                console.error('Delete error:', error);
                failedCount++;
            }
        }

        // Refresh asset list
        await this.loadAssets();

        // Show results
        if (deletedCount > 0) {
            this.app?.showSuccess(`Deleted ${deletedCount} of ${totalAssets} assets`);
        }
        if (failedCount > 0) {
            this.app?.showError(`Failed to delete ${failedCount} assets`);
        }
    }

    /**
     * Remove asset from state
     */
    removeAssetFromState(assetId) {
        this.assets = this.assets.filter(asset => asset.id !== assetId);
        this.selectedAssets.delete(assetId);
        this.applyCurrentFilter();
        this.updateCounts();
        this.renderAssets();
    }

    /**
     * Clean up broken assets
     */
    async cleanupBrokenAssets() {
        if (!confirm('This will remove assets that can no longer be accessed. Continue?')) {
            return;
        }

        console.log('🧹 Cleaning up broken assets...');
        this.app?.showInfo('Checking assets for broken links...');

        let removedCount = 0;
        const assetsToCheck = [...this.assets];

        for (const asset of assetsToCheck) {
            try {
                const response = await fetch(asset.viewUrl, { method: 'HEAD' });
                if (!response.ok) {
                    await this.deleteAsset(asset.id);
                    removedCount++;
                }
            } catch (error) {
                await this.deleteAsset(asset.id);
                removedCount++;
            }
        }

        if (removedCount > 0) {
            this.app?.showSuccess(`Cleanup complete: ${removedCount} broken assets removed`);
        } else {
            this.app?.showInfo('No broken assets found');
        }
    }

    /**
     * Force refresh
     */
    async forceRefresh() {
        this.retryCount = 0;
        this.selectedAssets.clear();
        await this.loadAssets();
    }

    /**
     * Show loading state
     */
    showLoading() {
        const loadingEl = document.getElementById('assets-loading');
        const errorEl = document.getElementById('assets-error');
        const emptyEl = document.getElementById('assets-empty');
        const gridEl = document.getElementById('assets-grid');
        
        if (loadingEl) loadingEl.style.display = 'block';
        if (errorEl) errorEl.style.display = 'none';
        if (emptyEl) emptyEl.style.display = 'none';
        if (gridEl) gridEl.style.display = 'none';
    }

    /**
     * Show error state
     */
    showError(message) {
        const loadingEl = document.getElementById('assets-loading');
        const errorEl = document.getElementById('assets-error');
        const emptyEl = document.getElementById('assets-empty');
        const gridEl = document.getElementById('assets-grid');
        const messageEl = document.getElementById('error-message');
        
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) errorEl.style.display = 'block';
        if (emptyEl) emptyEl.style.display = 'none';
        if (gridEl) gridEl.style.display = 'none';
        if (messageEl) messageEl.textContent = message;
    }

    /**
     * Show empty state
     */
    showEmpty() {
        const loadingEl = document.getElementById('assets-loading');
        const errorEl = document.getElementById('assets-error');
        const emptyEl = document.getElementById('assets-empty');
        const gridEl = document.getElementById('assets-grid');
        
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) errorEl.style.display = 'none';
        if (emptyEl) emptyEl.style.display = 'block';
        if (gridEl) gridEl.style.display = 'none';
    }

    /**
     * Show no results state
     */
    showNoResults() {
        const emptyDiv = document.getElementById('assets-empty');
        if (emptyDiv) {
            emptyDiv.innerHTML = `
                <div class="text-muted mb-3">
                    <i class="fas fa-filter fa-3x"></i>
                </div>
                <h4>No ${this.currentFilter === 'all' ? 'assets' : this.currentFilter} found</h4>
                <p class="text-muted">Try adjusting your filter or search for different content.</p>
                <button class="btn btn-outline-primary" onclick="assetManager.setFilter('all')">
                    <i class="fas fa-eye"></i> Show All Assets
                </button>
            `;
            emptyDiv.style.display = 'block';
        }
    }

    /**
     * Hide all state elements
     */
    hideAllStates() {
        ['assets-loading', 'assets-error', 'assets-empty'].forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });
        
        const grid = document.getElementById('assets-grid');
        if (grid) grid.style.display = 'none';
    }

    /**
     * Update pagination
     */
    updatePagination() {
        const totalPages = Math.ceil(this.filteredAssets.length / this.assetsPerPage);
        const pagination = document.getElementById('assets-pagination');
        
        if (!pagination) return;

        if (totalPages <= 1) {
            pagination.style.display = 'none';
            return;
        }

        pagination.style.display = 'block';
        
        // Update pagination buttons
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        const currentPageBtn = document.getElementById('current-page');
        
        if (prevBtn) {
            prevBtn.classList.toggle('disabled', this.currentPage === 1);
        }
        
        if (nextBtn) {
            nextBtn.classList.toggle('disabled', this.currentPage === totalPages);
        }
        
        if (currentPageBtn) {
            currentPageBtn.querySelector('a').textContent = `${this.currentPage} of ${totalPages}`;
        }
    }

    /**
     * Set up video hover functionality
     */
    setupVideoHover(card, asset) {
        const videoContainer = card.querySelector('.video-hover-container');
        if (!videoContainer) return;

        const thumbnailImg = videoContainer.querySelector('.video-thumbnail-image');
        const videoPreview = videoContainer.querySelector('.video-hover-preview');
        const playIcon = videoContainer.querySelector('.video-play-icon');
        
        let hoverTimeout = null;
        let isVideoLoaded = false;

        // Mouse enter - start hover timer
        card.addEventListener('mouseenter', () => {
            hoverTimeout = setTimeout(() => {
                if (!isVideoLoaded && videoPreview) {
                    // Load and play video
                    videoPreview.load();
                    videoPreview.play().then(() => {
                        thumbnailImg.style.display = 'none';
                        videoPreview.style.display = 'block';
                        playIcon.style.opacity = '0.3';
                        isVideoLoaded = true;
                    }).catch(error => {
                        console.warn('Video hover play failed:', error);
                    });
                } else if (isVideoLoaded && videoPreview) {
                    // Resume video if already loaded
                    thumbnailImg.style.display = 'none';
                    videoPreview.style.display = 'block';
                    playIcon.style.opacity = '0.3';
                    videoPreview.play().catch(error => {
                        console.warn('Video hover resume failed:', error);
                    });
                }
            }, 500); // 500ms delay as per original implementation
        });

        // Mouse leave - stop video and show thumbnail
        card.addEventListener('mouseleave', () => {
            if (hoverTimeout) {
                clearTimeout(hoverTimeout);
                hoverTimeout = null;
            }
            
            if (videoPreview && isVideoLoaded) {
                videoPreview.pause();
                videoPreview.style.display = 'none';
                thumbnailImg.style.display = 'block';
                playIcon.style.opacity = '1';
            }
        });

        // Cleanup video on card removal
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.removedNodes.forEach((node) => {
                    if (node === card && videoPreview) {
                        videoPreview.pause();
                        videoPreview.src = '';
                    }
                });
            });
        });
        
        observer.observe(card.parentNode, { childList: true });
    }

    /**
     * Show debug information for troubleshooting
     */
    showDebugInfo() {
        console.group('🐛 Enhanced Asset Manager Debug Information');
        
        console.log('📊 Basic Stats:');
        console.log(`  - Total assets: ${this.assets ? this.assets.length : 'null/undefined'}`);
        console.log(`  - Filtered assets: ${this.filteredAssets ? this.filteredAssets.length : 'null/undefined'}`);
        console.log(`  - Selected assets: ${this.selectedAssets.size}`);
        console.log(`  - Current filter: ${this.currentFilter}`);
        console.log(`  - Current page: ${this.currentPage}`);
        console.log(`  - Is loading: ${this.isLoading}`);
        
        // Debug asset type detection
        if (this.assets && this.assets.length > 0) {
            const imageCount = this.assets.filter(asset => asset.isImage).length;
            const videoCount = this.assets.filter(asset => asset.isVideo).length;
            const unknownCount = this.assets.length - imageCount - videoCount;
            
            console.log('📁 Asset Type Breakdown:');
            console.log(`  - Images: ${imageCount}`);
            console.log(`  - Videos: ${videoCount}`);
            console.log(`  - Unknown/Other: ${unknownCount}`);
            
            console.log('🔗 Sample Assets (first 5):');
            this.assets.slice(0, 5).forEach((asset, i) => {
                console.log(`  Asset ${i + 1}:`);
                console.log(`    - Filename: ${asset.filename}`);
                console.log(`    - File type: ${asset.file_type}`);
                console.log(`    - isImage: ${asset.isImage}, isVideo: ${asset.isVideo}`);
                console.log(`    - Raw filename: ${asset._raw?.filename || asset._raw?.name || 'N/A'}`);
            });
        } else {
            console.log('❌ No assets available for type analysis');
        }
        
        console.log('🌐 DOM Elements:');
        const elements = [
            'assets-grid',
            'assets-loading', 
            'assets-error',
            'assets-empty',
            'count-all',
            'count-images',
            'count-videos'
        ];
        
        elements.forEach(id => {
            const el = document.getElementById(id);
            console.log(`  - ${id}: ${el ? '✅ Found' : '❌ Missing'}`);
        });
        
        console.log('💡 Debug commands:');
        console.log('  - assetManager.showDebugInfo() - Show this info');
        console.log('  - assetManager.loadAssetsWithRetry() - Force reload with retries');
        console.log('  - localStorage.setItem("asset_debug", "true") - Enable debug mode');
        console.log('  - localStorage.removeItem("asset_debug") - Disable debug mode');
        
        console.groupEnd();
        
        return {
            totalAssets: this.assets.length,
            filteredAssets: this.filteredAssets.length,
            selectedAssets: this.selectedAssets.size,
            currentFilter: this.currentFilter,
            isLoading: this.isLoading
        };
    }

    /**
     * Apply current filter (compatibility method for app.js)
     */
    applyFilter(filter = null) {
        if (filter) {
            this.currentFilter = filter;
        }
        console.log('🔍 applyFilter called with:', this.currentFilter);
        
        // Ensure we have assets to filter
        if (!this.assets || !Array.isArray(this.assets)) {
            console.warn('⚠️ applyFilter: No assets to filter');
            this.filteredAssets = [];
            return;
        }
        
        this.applyCurrentFilter();
        this.updateCounts();
        this.renderAssets();
    }
    
    /**
     * Filter assets (compatibility method)
     */
    filterAssets(filter) {
        this.setFilter(filter);
    }

    /**
     * Show empty state (compatibility method for app.js)
     */
    showEmptyState(message = 'No assets found') {
        console.log('📭 showEmptyState called with message:', message);
        const grid = document.getElementById('assets-grid');
        if (grid) {
            grid.innerHTML = `
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">${message}</h5>
                        <p class="text-muted">Try refreshing or check your connection.</p>
                        <button class="btn btn-outline-primary" onclick="window.mediaScraperApp?.modules?.assetManager?.loadAssets?.()">
                            <i class="fas fa-sync"></i> Refresh Assets
                        </button>
                    </div>
                </div>
            `;
        }
    }
}

// Make available globally
window.EnhancedAssetManager = EnhancedAssetManager;
window.assetManager = null; // Will be set during initialization 
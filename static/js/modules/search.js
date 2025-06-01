/**
 * ============================================================================
 * SEARCH MODULE
 * ============================================================================
 * 
 * Handles search functionality and form management
 */

class SearchManager {
    constructor(app) {
        this.app = app;
        this.sources = {};
        this.activeJob = null;
        this.progressInterval = null;
        this.selectedSources = new Set();
    }

    /**
     * Initialize search functionality
     */
    init() {
        this.setupSearchForm();
        this.setupSourceToggle();
        this.loadSources();
    }

    /**
     * Set up search form event listeners
     */
    setupSearchForm() {
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', this.handleSearchSubmit.bind(this));
        }

        // Safe search toggle - handle locally, no redirect
        const safeSearchToggle = document.getElementById('safe-search-toggle');
        if (safeSearchToggle) {
            safeSearchToggle.addEventListener('change', this.handleSafeSearchToggle.bind(this));
        }

        // NSFW sources toggle
        const nsfwToggle = document.getElementById('nsfw-sources-toggle');
        if (nsfwToggle) {
            nsfwToggle.addEventListener('change', this.toggleNSFWChevron.bind(this));
        }
    }

    /**
     * Set up source control buttons
     */
    setupSourceToggle() {
        // Select all/deselect all sources
        const selectAllBtn = document.getElementById('select-all-sources');
        const deselectAllBtn = document.getElementById('deselect-all-sources');
        const refreshBtn = document.getElementById('refresh-sources');

        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => this.toggleAllSources(true));
        }

        if (deselectAllBtn) {
            deselectAllBtn.addEventListener('click', () => this.toggleAllSources(false));
        }

        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadSources());
        }
    }

    /**
     * Handle search form submission
     */
    async handleSearchSubmit(event) {
        event.preventDefault();

        try {
            // Get form data
            const formData = new FormData(event.target);
            const searchQuery = SecurityUtils.sanitizeSearchInput(formData.get('search-query') || '');
            const searchType = formData.get('search-type') || 'comprehensive';
            const maxItems = parseInt(formData.get('max-items')) || 25;
            const safeSearch = document.getElementById('safe-search-toggle')?.checked || true;

            // Validate input
            if (!searchQuery.trim()) {
                this.app.showError('Please enter a search query');
                return;
            }

            if (maxItems < 5 || maxItems > 100) {
                this.app.showError('Max items must be between 5 and 100');
                return;
            }

            // Get selected sources
            const enabledSources = this.getSelectedSources();
            if (enabledSources.length === 0) {
                this.app.showError('Please select at least one content source');
                return;
            }

            // Start search
            await this.startSearch({
                query: searchQuery,
                search_type: searchType,
                max_content: maxItems,
                enabled_sources: enabledSources,
                safe_search: safeSearch
            });

        } catch (error) {
            console.error('Search submission error:', error);
            this.app.showError('Failed to start search. Please try again.');
        }
    }

    /**
     * Start search request
     */
    async startSearch(params) {
        try {
            this.showProgressPanel();
            this.updateProgress('Initializing search...', 0);

            const response = await fetch('/api/comprehensive-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });

            const data = await response.json();

            if (response.status === 402) {
                this.hideProgressPanel();
                this.app.showError(data.error || 'Upgrade required to continue');
                return;
            }

            if (data.success) {
                this.activeJob = data.job_id;
                this.app.showSuccess(`Search started! Job ID: ${this.activeJob}`);
                this.startProgressUpdates();
            } else {
                throw new Error(data.error || 'Search failed');
            }

        } catch (error) {
            this.hideProgressPanel();
            throw error;
        }
    }

    /**
     * Get selected sources from form
     */
    getSelectedSources() {
        const checkboxes = document.querySelectorAll('.source-checkbox-unique:checked');
        return Array.from(checkboxes).map(cb => cb.dataset.source);
    }

    /**
     * Handle safe search toggle (local only, no server redirect)
     */
    handleSafeSearchToggle(event) {
        const isEnabled = event.target.checked;
        console.log('🔒 Safe search toggled:', isEnabled ? 'ON' : 'OFF');
        
        this.updateSafeSearchStatus(isEnabled);
        
        // Show/hide NSFW sources section
        const nsfwSection = document.getElementById('nsfw-sources-section');
        if (nsfwSection) {
            nsfwSection.style.display = isEnabled ? 'none' : 'block';
        }
        
        // Reload sources with new safe search setting but don't redirect
        this.loadSources();
    }

    /**
     * Update safe search status display
     */
    updateSafeSearchStatus(enabled) {
        const statusElement = document.getElementById('safe-search-status');
        if (statusElement) {
            if (enabled) {
                statusElement.textContent = 'ON';
                statusElement.className = 'safe-search-status badge bg-success';
            } else {
                statusElement.textContent = 'OFF';
                statusElement.className = 'safe-search-status badge bg-danger';
            }
        }
    }

    /**
     * Toggle NSFW chevron icon
     */
    toggleNSFWChevron() {
        const chevron = document.getElementById('nsfw-chevron');
        if (chevron) {
            setTimeout(() => {
                const isExpanded = document.getElementById('nsfw-sources-list').classList.contains('show');
                chevron.className = isExpanded ? 'fas fa-chevron-up ms-1' : 'fas fa-chevron-down ms-1';
            }, 150);
        }
    }

    /**
     * Load available sources
     */
    async loadSources() {
        try {
            const safeSearch = document.getElementById('safe-search-toggle')?.checked || true;
            const response = await fetch(`/api/sources?safe_search=${safeSearch}`);
            const data = await response.json();

            if (data.success) {
                this.sources = data.sources;
                this.displaySources();
                this.updateSourceCount();
            } else {
                throw new Error(data.error || 'Failed to load sources');
            }
        } catch (error) {
            console.error('Error loading sources:', error);
            this.app.showError('Failed to load sources: ' + error.message);
        }
    }

    /**
     * Display sources in the UI (called from main app)
     */
    displaySources() {
        const container = document.getElementById('source-categories');
        if (!container) {
            console.warn('⚠️ Source categories container not found');
            return;
        }

        console.log('🎨 Displaying sources...', this.sources);
        
        // COMPREHENSIVE CLEANUP - Remove ALL existing content and listeners
        container.innerHTML = '';
        
        // Remove any existing event listeners to prevent duplicates
        document.removeEventListener('change', this.handleSourceCheckboxChange);
        
        // Clear any existing checkboxes globally to prevent conflicts
        const existingCheckboxes = document.querySelectorAll('.source-checkbox, .form-check-input[data-source]');
        existingCheckboxes.forEach(checkbox => {
            checkbox.removeEventListener('change', this.handleSourceCheckboxChange);
        });
        
        if (!this.sources || Object.keys(this.sources).length === 0) {
            container.innerHTML = `
                <div class="text-center py-3">
                    <div class="spinner-border spinner-border-sm" role="status">
                        <span class="visually-hidden">Loading sources...</span>
                    </div>
                    <p class="mt-2 text-muted">Loading available sources...</p>
                </div>
            `;
            return;
        }

        // Group sources by category
        const categories = this.groupSourcesByCategory();
        
        // Create category sections with UNIQUE IDs and classes
        Object.entries(categories).forEach(([categoryName, categoryData]) => {
            const categorySection = this.createCategorySection(categoryName, categoryData);
            container.appendChild(categorySection);
        });

        // Update source count
        const totalSources = Object.keys(this.sources).length;
        const sourceCountElement = document.getElementById('source-count');
        if (sourceCountElement) {
            sourceCountElement.textContent = `(${totalSources} available)`;
        }

        // Set up event listeners ONCE per source after all creation is complete
        this.setupSourceEventListeners();
        
        console.log(`✅ Successfully displayed ${totalSources} sources in ${Object.keys(categories).length} categories`);
    }

    /**
     * Create a category section with proper cleanup
     */
    createCategorySection(categoryName, categoryData) {
        const section = document.createElement('div');
        section.className = 'source-category mb-3';
        
        const categoryId = `category-${categoryName.toLowerCase().replace(/\s+/g, '-')}`;
        section.id = categoryId;

        const { sources, description } = categoryData;
        const availableCount = sources.filter(source => source.available).length;

        section.innerHTML = `
            <div class="source-category-header mb-2">
                <h6 class="mb-1">
                    <i class="fas fa-${this.getCategoryIcon(categoryName)}" aria-hidden="true"></i>
                    ${categoryName}
                    <span class="badge bg-primary ms-2">${availableCount}/${sources.length}</span>
                </h6>
                ${description ? `<small class="text-muted">${description}</small>` : ''}
            </div>
            <div class="sources-grid">
                ${sources.map(source => this.createSourceItem(source)).join('')}
            </div>
        `;

        return section;
    }

    /**
     * Create a single source item with clean aligned layout
     */
    createSourceItem(source) {
        const uniqueId = `source-${source.name.toLowerCase().replace(/[^a-z0-9]/g, '-')}-${Date.now()}`;
        const isAvailable = source.available;
        
        return `
            <div class="source-item-clean ${isAvailable ? 'available' : 'locked'}" data-source="${source.name}">
                <div class="source-icon">
                    ${isAvailable ? 
                        `<input type="checkbox" 
                                class="form-check-input source-checkbox-unique" 
                                id="${uniqueId}"
                                data-source="${source.name}"
                                ${this.selectedSources.has(source.name) ? 'checked' : ''}>` :
                        `<i class="fas fa-lock text-warning" title="Upgrade required"></i>`
                    }
                </div>
                <label class="source-label ${isAvailable ? '' : 'disabled'}" for="${uniqueId}">
                    ${source.display_name || source.name}
                </label>
            </div>
        `;
    }

    /**
     * Set up event listeners for all sources ONCE
     */
    setupSourceEventListeners() {
        // Remove any existing listeners first
        document.removeEventListener('change', this.handleSourceCheckboxChange);
        
        // Add single event listener using event delegation
        document.addEventListener('change', (event) => {
            if (event.target.matches('.source-checkbox-unique')) {
                this.handleSourceCheckboxChange(event);
            }
        });
        
        console.log('✅ Source event listeners set up with delegation');
    }

    /**
     * Group sources by category for better organization
     */
    groupSourcesByCategory() {
        const categories = {};
        
        Object.entries(this.sources).forEach(([sourceName, sourceData]) => {
            const category = sourceData.category || 'General';
            
            if (!categories[category]) {
                categories[category] = {
                    sources: [],
                    description: sourceData.category_description || null
                };
            }
            
            categories[category].sources.push({
                name: sourceName,
                display_name: sourceData.display_name || sourceName,
                description: sourceData.description || 'Content source',
                available: !sourceData.locked,
                category: category,
                ...sourceData
            });
        });
        
        return categories;
    }

    /**
     * Handle source checkbox changes (updated for new structure)
     */
    handleSourceCheckboxChange(event) {
        const checkbox = event.target;
        const sourceName = checkbox.dataset.source;
        
        if (!sourceName) {
            console.warn('⚠️ Source checkbox missing data-source attribute');
            return;
        }

        if (checkbox.checked) {
            this.selectedSources.add(sourceName);
            console.log(`✅ Selected source: ${sourceName}`);
        } else {
            this.selectedSources.delete(sourceName);
            console.log(`❌ Deselected source: ${sourceName}`);
        }

        // Update source count display
        this.updateSourceCount();
        
        // Update NSFW section visibility if needed
        this.updateNsfwVisibility();
    }

    /**
     * Update source count display
     */
    updateSourceCount() {
        const sourceCountElement = document.getElementById('source-count');
        if (sourceCountElement) {
            const selectedCount = this.selectedSources.size;
            const totalCount = Object.keys(this.sources).length;
            sourceCountElement.textContent = `(${selectedCount}/${totalCount} selected)`;
        }
    }

    /**
     * Update NSFW section visibility based on safe search
     */
    updateNsfwVisibility() {
        const nsfwSection = document.getElementById('nsfw-sources-section');
        const safeSearchToggle = document.getElementById('safe-search-toggle');
        
        if (nsfwSection && safeSearchToggle) {
            nsfwSection.style.display = safeSearchToggle.checked ? 'none' : 'block';
        }
    }

    /**
     * Get category display name
     */
    getCategoryDisplayName(category) {
        const categoryNames = {
            social: 'Social Media',
            video: 'Video Platforms',
            search: 'Search Engines',
            art: 'Art & Creative',
            gallery: 'Image Galleries',
            stock: 'Stock Photos',
            news: 'News & Media',
            direct: 'Direct Sources',
            adult: 'Adult Content (18+)'
        };
        return categoryNames[category] || category;
    }

    /**
     * Get category icon
     */
    getCategoryIcon(category) {
        const categoryIcons = {
            social: 'fab fa-twitter',
            video: 'fas fa-video',
            search: 'fas fa-search',
            art: 'fas fa-palette',
            gallery: 'fas fa-images',
            stock: 'fas fa-camera',
            news: 'fas fa-newspaper',
            direct: 'fas fa-link',
            adult: 'fas fa-exclamation-triangle'
        };
        return categoryIcons[category] || 'fas fa-globe';
    }

    /**
     * Get category color
     */
    getCategoryColor(category) {
        const categoryColors = {
            social: '#1da1f2',
            video: '#ff0000',
            search: '#4285f4',
            art: '#e91e63',
            gallery: '#ff9800',
            stock: '#00bcd4',
            news: '#607d8b',
            direct: '#795548',
            adult: '#f44336'
        };
        return categoryColors[category] || '#6c757d';
    }

    /**
     * Toggle all sources
     */
    toggleAllSources(enable) {
        const checkboxes = document.querySelectorAll('.source-checkbox-unique:not(:disabled)');
        checkboxes.forEach(checkbox => {
            checkbox.checked = enable;
            
            // Trigger the change event to update selection tracking
            const event = new Event('change', { bubbles: true });
            checkbox.dispatchEvent(event);
        });
        
        console.log(`🔄 ${enable ? 'Selected' : 'Deselected'} all available sources (${checkboxes.length} sources)`);
    }

    /**
     * Show progress panel
     */
    showProgressPanel() {
        const progressPanel = document.getElementById('progress-panel');
        if (progressPanel) {
            progressPanel.style.display = 'block';
            progressPanel.scrollIntoView({ behavior: 'smooth' });
        }
    }

    /**
     * Hide progress panel
     */
    hideProgressPanel() {
        const progressPanel = document.getElementById('progress-panel');
        if (progressPanel) {
            progressPanel.style.display = 'none';
        }
    }

    /**
     * Update progress display
     */
    updateProgress(message, progress = 0, stats = {}) {
        // Update progress bar
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const progressMessage = document.getElementById('progress-message');
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
            progressBar.textContent = `${Math.round(progress)}%`;
            
            // Update progress bar color based on status
            progressBar.className = 'progress-bar progress-bar-striped';
            if (progress === 100) {
                progressBar.classList.add('bg-success');
            } else if (progress > 0) {
                progressBar.classList.add('progress-bar-animated', 'bg-primary');
            }
        }
        
        // Update status message
        if (progressText) {
            progressText.textContent = message;
        }
        
        if (progressMessage) {
            // Update alert style based on progress
            progressMessage.className = 'alert mb-3';
            if (progress === 100) {
                progressMessage.classList.add('alert-success');
                progressMessage.innerHTML = '<i class="fas fa-check-circle me-2"></i><span id="progress-text">' + message + '</span>';
            } else if (progress > 0) {
                progressMessage.classList.add('alert-info');
                progressMessage.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i><span id="progress-text">' + message + '</span>';
            } else {
                progressMessage.classList.add('alert-secondary');
                progressMessage.innerHTML = '<i class="fas fa-info-circle me-2"></i><span id="progress-text">' + message + '</span>';
            }
        }
        
        // Update statistics
        if (stats.detected !== undefined) {
            const detectedEl = document.getElementById('progress-detected');
            if (detectedEl) detectedEl.textContent = stats.detected || 0;
        }
        
        if (stats.downloaded !== undefined) {
            const downloadedEl = document.getElementById('progress-downloaded');
            if (downloadedEl) downloadedEl.textContent = stats.downloaded || 0;
        }
        
        if (stats.images !== undefined) {
            const imagesEl = document.getElementById('progress-images');
            if (imagesEl) imagesEl.textContent = stats.images || 0;
        }
        
        if (stats.videos !== undefined) {
            const videosEl = document.getElementById('progress-videos');
            if (videosEl) videosEl.textContent = stats.videos || 0;
        }
        
        // Update active sources
        if (stats.sources) {
            const activeSourcesList = document.getElementById('active-sources-list');
            if (activeSourcesList) {
                const sourceNames = Object.keys(stats.sources);
                if (sourceNames.length > 0) {
                    activeSourcesList.textContent = sourceNames.join(', ');
                } else {
                    activeSourcesList.textContent = 'No sources active';
                }
            }
        }
        
        // Update current file
        if (stats.current_file) {
            const currentFileInfo = document.getElementById('current-file-info');
            const currentFileName = document.getElementById('current-file-name');
            if (currentFileInfo && currentFileName) {
                currentFileInfo.style.display = 'block';
                currentFileName.textContent = stats.current_file;
            }
        } else {
            const currentFileInfo = document.getElementById('current-file-info');
            if (currentFileInfo) {
                currentFileInfo.style.display = 'none';
            }
        }
        
        // Add to progress log
        this.addToProgressLog(message, progress, stats);
        
        console.log(`Progress: ${progress}% - ${message}`, stats);
    }
    
    /**
     * Add entry to progress log
     */
    addToProgressLog(message, progress, stats) {
        const logContent = document.getElementById('progress-log-content');
        if (!logContent) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = 'log-entry mb-1';
        logEntry.innerHTML = `<span class="text-muted">[${timestamp}]</span> ${SecurityUtils.escapeHTML(message)}`;
        
        logContent.appendChild(logEntry);
        
        // Scroll to bottom
        logContent.scrollTop = logContent.scrollHeight;
        
        // Keep only last 50 entries
        const entries = logContent.querySelectorAll('.log-entry');
        if (entries.length > 50) {
            entries[0].remove();
        }
    }

    /**
     * Start progress updates
     */
    startProgressUpdates() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/job-status/${this.activeJob}`);
                const data = await response.json();

                if (data.success || data.status) {
                    const progress = data.status?.progress || data.progress || 0;
                    const message = data.status?.message || data.message || 'Processing...';
                    
                    this.updateProgress(message, progress, data.status || data);

                    if (data.status?.completed || data.completed) {
                        this.stopProgressUpdates();
                        this.app.showSuccess('Search completed successfully!');
                        
                        console.log('🎉 Search completed, refreshing assets...');
                        
                        // Refresh assets in multiple ways to ensure they show up
                        if (this.app.modules.assetManager) {
                            console.log('🔄 Calling asset manager loadAssets...');
                            await this.app.modules.assetManager.loadAssets();
                        }
                        
                        // Also refresh in the main app
                        console.log('🔄 Calling app loadAssets...');
                        await this.app.loadAssets();
                        
                        // Force a render
                        if (this.app.modules.assetManager) {
                            console.log('🎨 Force rendering assets...');
                            this.app.modules.assetManager.renderAssets();
                        }
                        
                        // Update dashboard stats
                        console.log('📊 Updating dashboard stats...');
                        await this.app.loadDashboardStats();
                        
                        console.log('✅ Search completion refresh complete');
                    }
                }
            } catch (error) {
                console.error('Error checking progress:', error);
            }
        }, 2000);
    }

    /**
     * Stop progress updates
     */
    stopProgressUpdates() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        setTimeout(() => {
            this.hideProgressPanel();
        }, 3000);
    }

    /**
     * Cleanup module
     */
    destroy() {
        this.stopProgressUpdates();
    }
}

// Export to global scope
window.SearchManager = SearchManager; 
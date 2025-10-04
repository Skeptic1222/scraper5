/**
 * Enhanced Search Manager with Bulletproof Download Engine Integration
 * Handles the new UI, source selection, and AI-monitored downloads
 */

class EnhancedSearchManager {
    constructor(app = null) {
        this.app = app;
        this.sources = {};
        this.selectedSources = new Set();
        this.isSearching = false;
        this.currentJobId = null;
        this.downloadProgress = {};
        
        // Initialize after DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        console.log('🚀 Enhanced Search Manager initializing...');
        console.log('📍 Current URL:', window.location.href);
        console.log('📍 Current state:', this);
        
        // Check if source-categories exists
        const container = document.getElementById('source-categories');
        console.log('📍 source-categories element:', container);
        
        this.setupEventListeners();
        this.loadSources();
        
        console.log('✅ Enhanced Search Manager initialized');
    }
    
    setupEventListeners() {
        // Search form submission
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => this.handleSearchSubmit(e));
        }
        
        // Source control buttons
        this.setupSourceControlButtons();
        
        // Progress control buttons
        this.setupProgressControlButtons();
        
        // Safe search toggle (support legacy/new IDs)
        const safeTogglePrimary = document.getElementById('safe-search-toggle');
        const safeToggleAlt = document.getElementById('safe-search');
        const activeSafeToggle = safeTogglePrimary || safeToggleAlt;
        if (activeSafeToggle) {
            activeSafeToggle.addEventListener('change', () => this.handleSafeSearchToggle());
        }
        
        // Adult content toggle (support legacy/new IDs)
        const adultToggle = document.getElementById('show-adult-sources') || document.getElementById('nsfw-sources-toggle');
        if (adultToggle) {
            adultToggle.addEventListener('change', () => this.handleAdultContentToggle());
        }
        
        // Quality settings
        this.setupQualitySettingsListeners();
    }
    
    setupSourceControlButtons() {
        // Select recommended sources
        const selectRecommendedBtn = document.getElementById('select-recommended-sources');
        if (selectRecommendedBtn) {
            selectRecommendedBtn.addEventListener('click', () => this.selectRecommendedSources());
        }
        
        // Select all sources
        const selectAllBtn = document.getElementById('select-all-sources');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => this.selectAllSources());
        }
        
        // Deselect all sources
        const deselectAllBtn = document.getElementById('deselect-all-sources');
        if (deselectAllBtn) {
            deselectAllBtn.addEventListener('click', () => this.deselectAllSources());
        }
        
        // Select free sources only
        const selectFreeBtn = document.getElementById('select-free-sources');
        if (selectFreeBtn) {
            selectFreeBtn.addEventListener('click', () => this.selectFreeSources());
        }
        
        // Select premium sources only
        const selectPremiumBtn = document.getElementById('select-premium-sources');
        if (selectPremiumBtn) {
            selectPremiumBtn.addEventListener('click', () => this.selectPremiumSources());
        }
        
        // Refresh sources
        const refreshBtn = document.getElementById('refresh-sources');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadSources());
        }
    }
    
    setupProgressControlButtons() {
        // Cancel search
        const cancelBtn = document.getElementById('cancel-search');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelSearch());
        }
        
        // Clear log
        const clearLogBtn = document.getElementById('clear-log');
        if (clearLogBtn) {
            clearLogBtn.addEventListener('click', () => this.clearLog());
        }
    }
    
    setupQualitySettingsListeners() {
        // Image quality settings
        const imageSize = document.getElementById('image-size');
        const imageFormat = document.getElementById('image-format');
        const highQualityImages = document.getElementById('high-quality-images');
        
        // Video quality settings
        const videoQuality = document.getElementById('video-quality');
        const videoFormat = document.getElementById('video-format');
        const extractAudio = document.getElementById('extract-audio');
        
        [imageSize, imageFormat, highQualityImages, videoQuality, videoFormat, extractAudio].forEach(element => {
            if (element) {
                element.addEventListener('change', () => this.saveQualitySettings());
            }
        });
    }
    
    async loadSources() {
        try {
            // 1) Prefer server-injected JSON if present
            try {
                const serverNode = document.getElementById('server-sources');
                if (serverNode && serverNode.textContent && serverNode.textContent.trim().length > 0) {
                    const injected = JSON.parse(serverNode.textContent);
                    if (injected && injected.categories && Object.keys(injected.categories).length > 0) {
                        console.log('📦 Using server-injected sources payload');
                        this.sources = {};
                        Object.entries(injected.categories).forEach(([cat, list]) => {
                            this.sources[cat] = (list || []).map(s => ({
                                ...s,
                                subscription_required: Boolean(s.subscription_required || s.requires_auth),
                                enabled: s.enabled !== false
                            }));
                        });
                        // Determine id style for normalization during submit
                        this.idStyleUnderscore = Object.values(this.sources).flat().some(s => /_/.test(s.id));
                        this.displaySources();
                        // proceed to refresh via API in background
                        setTimeout(() => this.fetchSourcesFromApi(), 0);
                        return;
                    }
                }
            } catch (e) {
                console.warn('⚠️ Failed to use server-injected sources:', e);
            }
            
            console.log('📋 Loading sources from API...');
            
            // Use correct API URL with prefix and safe_search toggle
            const safeTogglePrimary = document.getElementById('safe-search-toggle');
            const safeToggleAlt = document.getElementById('safe-search');
            const safeSearch = (safeTogglePrimary && typeof safeTogglePrimary.checked === 'boolean')
                ? safeTogglePrimary.checked
                : (safeToggleAlt && typeof safeToggleAlt.checked === 'boolean' ? safeToggleAlt.checked : false);
            const apiUrl = (window.APP_BASE || '') + `/api/sources?safe_search=${safeSearch}`;
            console.log('📋 API URL:', apiUrl);
            
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📦 Raw API response:', data);
            
            // Normalize backend formats to { [category]: [sources] }
            this.sources = {};
            let totalSourcesConverted = 0;
            
            if (data && Array.isArray(data.sources)) {
                // Format: { sources: [ { category, sources: [...] }, ... ] }
                console.log('📦 Converting array format in data.sources...');
                data.sources.forEach(categoryData => {
                    if (categoryData?.category && Array.isArray(categoryData.sources)) {
                        this.sources[categoryData.category] = categoryData.sources.map(s => ({
                            ...s,
                            // Ensure property names used by UI exist
                            subscription_required: Boolean(s.subscription_required || s.requires_auth),
                            enabled: s.enabled !== false
                        }));
                        totalSourcesConverted += categoryData.sources.length;
                    }
                });
            } else if (data && data.categories && typeof data.categories === 'object') {
                // Format: { categories: { [name]: [ { id, name, nsfw, enabled, requires_auth } ] } }
                console.log('📦 Converting object format in data.categories...');
                Object.entries(data.categories).forEach(([categoryName, sources]) => {
                    if (Array.isArray(sources)) {
                        this.sources[categoryName] = sources.map(s => ({
                            ...s,
                            subscription_required: Boolean(s.subscription_required || s.requires_auth),
                            enabled: s.enabled !== false
                        }));
                        totalSourcesConverted += sources.length;
                    }
                });
            } else if (data && data.sources && typeof data.sources === 'object') {
                // Already in object format
                console.log('📦 Using object format from data.sources');
                Object.entries(data.sources).forEach(([categoryName, sources]) => {
                    this.sources[categoryName] = (sources || []).map(s => ({
                        ...s,
                        subscription_required: Boolean(s.subscription_required || s.requires_auth),
                        enabled: s.enabled !== false
                    }));
                    totalSourcesConverted += (sources || []).length;
                });
            } else {
                console.warn('⚠️ Unrecognized sources payload shape; defaulting to empty');
            }
            
            console.log('✅ Sources normalized. Categories:', Object.keys(this.sources));
            console.log('📊 Total sources:', totalSourcesConverted);

            // Fallback: if API returns no sources, use a minimal default set so UI remains usable
            if (Object.keys(this.sources).length === 0) {
                console.warn('⚠️ No sources available from API. Using minimal defaults.');
                this.sources = {
                    'Search Engines': [
                        { id: 'google images', name: 'Google Images', enabled: true, requires_auth: false },
                        { id: 'bing images', name: 'Bing Images', enabled: true, requires_auth: false }
                    ],
                    'Video Platforms': [
                        { id: 'youtube', name: 'YouTube', enabled: true, requires_auth: false }
                    ],
                    'Social Media': [
                        { id: 'reddit', name: 'Reddit', enabled: true, requires_auth: false }
                    ]
                };
                // Prefer legacy-friendly IDs when falling back during search submission
                this.idStyleUnderscore = true;
            }
            
        // Determine id style for normalization during submit
        this.idStyleUnderscore = Object.values(this.sources).flat().some(s => /_/.test(s.id));
        this.displaySources();
            
            // Auto-select recommended sources for better UX
            setTimeout(() => {
                this.selectRecommendedSources();
            }, 100);
            
            console.log('📊 Source loading summary:');
            console.log('- Total categories:', Object.keys(this.sources).length);
            console.log('- Selected sources count:', this.selectedSources.size);
            console.log('- Selected sources:', Array.from(this.selectedSources));
            
        } catch (error) {
            console.error('❌ Failed to load sources:', error);
            this.showError('Failed to load content sources. Please refresh the page.');
            // As a last resort, provide minimal defaults
            this.sources = {
                'Search Engines': [
                    { id: 'google images', name: 'Google Images', enabled: true, requires_auth: false },
                    { id: 'bing images', name: 'Bing Images', enabled: true, requires_auth: false }
                ],
                'Video Platforms': [
                    { id: 'youtube', name: 'YouTube', enabled: true, requires_auth: false }
                ]
            };
            this.idStyleUnderscore = true;
            this.displaySources();
        }
    }

    async fetchSourcesFromApi() {
        try {
            const safeTogglePrimary = document.getElementById('safe-search-toggle');
            const safeToggleAlt = document.getElementById('safe-search');
            const safeSearch = (safeTogglePrimary && typeof safeTogglePrimary.checked === 'boolean')
                ? safeTogglePrimary.checked
                : (safeToggleAlt && typeof safeToggleAlt.checked === 'boolean' ? safeToggleAlt.checked : false);
            const apiUrl = (window.APP_BASE || '') + `/api/sources?safe_search=${safeSearch}`;
            console.log('📋 API URL (refresh):', apiUrl);

            const response = await fetch(apiUrl);
            if (!response.ok) return; // Leave current display
            const data = await response.json();

            const updated = {};
            if (data && data.categories && typeof data.categories === 'object') {
                Object.entries(data.categories).forEach(([categoryName, sources]) => {
                    if (Array.isArray(sources)) {
                        updated[categoryName] = sources.map(s => ({
                            ...s,
                            subscription_required: Boolean(s.subscription_required || s.requires_auth),
                            enabled: s.enabled !== false
                        }));
                    }
                });
            }
            if (Object.keys(updated).length > 0) {
                this.sources = updated;
                this.displaySources();
            }
        } catch (e) {
            console.warn('⚠️ Background refresh of sources failed:', e);
        }
    }
    
    displaySources() {
        const container = document.getElementById('source-categories');
        console.log('🎨 displaySources called, container:', container);
        if (!container) {
            console.error('❌ source-categories container not found!');
            return;
        }
        
        console.log('🎨 Displaying enhanced sources...');
        console.log('📊 this.sources:', this.sources);
        console.log('📊 Object.keys(this.sources):', Object.keys(this.sources));
        
        container.innerHTML = '';
        // Ensure visible
        container.style.display = 'block';

        // Update source count badge if present
        const totalSources = Object.values(this.sources).reduce((acc, arr) => acc + (Array.isArray(arr) ? arr.length : 0), 0);
        const sourceCountEl = document.getElementById('source-count');
        if (sourceCountEl) {
            sourceCountEl.textContent = `(${totalSources} sources)`;
        }
        
        // Clear any previous placeholder content and build fresh UI
        
        const categories = Object.keys(this.sources).sort();
        console.log('📊 Categories to display:', categories);
        
        if (categories.length === 0) {
            console.warn('⚠️ No categories found in sources!');
            const noSourcesDiv = document.createElement('div');
            noSourcesDiv.className = 'alert alert-warning';
            noSourcesDiv.innerHTML = 'No sources available. Please check the API.';
            container.appendChild(noSourcesDiv);
            return;
        }
        
        categories.forEach(categoryName => {
            const sources = this.sources[categoryName];
            console.log(`📁 Processing category: ${categoryName}, sources:`, sources);
            if (!sources || sources.length === 0) {
                console.log(`  ⏭️ Skipping empty category: ${categoryName}`);
                return;
            }
            
            const categoryElement = this.createCategoryElement(categoryName, sources);
            container.appendChild(categoryElement);
        });
        
        console.log('✅ Enhanced sources display complete');
        console.log('📊 Final container children:', container.children.length);
    }
    
    createCategoryElement(categoryName, sources) {
        const isAdultCategory = categoryName.toLowerCase().includes('adult');
        
        // Category container
        const categoryDiv = document.createElement('div');
        categoryDiv.className = `source-category-enhanced ${isAdultCategory ? 'adult-category' : ''}`;
        
        // Category header
        const headerDiv = document.createElement('div');
        headerDiv.className = `category-header-enhanced ${isAdultCategory ? 'adult-category' : ''}`;
        
        const availableCount = sources.filter(source => !source.subscription_required).length;
        const totalCount = sources.length;
        
        headerDiv.innerHTML = `
            <h4>
                <i class="fas ${this.getCategoryIcon(categoryName)}"></i>
                ${categoryName}
                <span class="badge ${isAdultCategory ? 'bg-danger' : 'bg-secondary'} ms-2">
                    ${availableCount}/${totalCount}
                </span>
                ${isAdultCategory ? '<span class="badge bg-danger ms-1">18+</span>' : ''}
            </h4>
        `;
        // Add category-level actions
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'ms-auto';
        const onlyCatBtn = document.createElement('button');
        onlyCatBtn.type = 'button';
        onlyCatBtn.className = 'btn btn-sm btn-outline-secondary';
        onlyCatBtn.textContent = 'Only This Category';
        onlyCatBtn.title = 'Deselect others and select all in this category';
        onlyCatBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.selectOnlyCategory(categoryName);
        });
        actionsDiv.appendChild(onlyCatBtn);
        headerDiv.appendChild(actionsDiv);
        
        // Category sources
        const sourcesList = document.createElement('ul');
        sourcesList.className = 'source-list-enhanced';
        
        sources.forEach(source => {
            const sourceElement = this.createSourceElement(source, isAdultCategory);
            sourcesList.appendChild(sourceElement);
        });
        
        categoryDiv.appendChild(headerDiv);
        categoryDiv.appendChild(sourcesList);
        
        return categoryDiv;
    }
    
    createSourceElement(source, isAdultCategory) {
        const isAvailable = source.enabled;
        const isLocked = source.subscription_required;
        const isPremium = source.subscription_required && !source.nsfw;
        const isAdult = source.nsfw;
        
        console.log('🔍 Creating source element:', {
            id: source.id,
            name: source.name,
            enabled: source.enabled,
            subscription_required: source.subscription_required,
            isAvailable: isAvailable,
            isLocked: isLocked
        });
        
        const li = document.createElement('li');
        li.className = `source-item-enhanced ${isAdultCategory ? 'adult-source' : ''} ${isLocked ? 'locked' : ''}`;
        li.dataset.sourceId = source.id;
        
        // Control column (checkbox or lock)
        const controlDiv = document.createElement('div');
        controlDiv.className = 'source-control-enhanced';
        
        if (isAvailable) {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            // Include both classes for compatibility with app.js and enhanced UI
            checkbox.className = 'source-checkbox-enhanced source-checkbox';
            checkbox.setAttribute('data-source', source.id);
            checkbox.value = source.id;
            // Provide a stable id for label targeting
            const inputId = `source-${(source.id || '').toString().replace(/\s+/g,'_')}`;
            checkbox.id = inputId;
            checkbox.checked = false;  // Start unchecked - let user select
            checkbox.addEventListener('change', (e) => {
                this.handleSourceToggle(source.id, e.target.checked);
            });
            controlDiv.appendChild(checkbox);
            console.log('🔍 Available source created:', source.id, source.name);
        } else {
            const lockIcon = document.createElement('i');
            lockIcon.className = `fas fa-lock source-lock-enhanced ${isPremium ? 'premium' : ''} ${isAdult ? 'adult' : ''}`;
            lockIcon.title = isAdult ? 'Adult content - Premium subscription required' : 'Premium subscription required';
            controlDiv.appendChild(lockIcon);
        }
        
        // Info column
        const infoDiv = document.createElement('div');
        infoDiv.className = 'source-info-enhanced';
        
        const nameP = document.createElement('p');
        nameP.className = 'source-name-enhanced';
        // Make label clickable for better UX
        if (isAvailable) {
            const label = document.createElement('label');
            label.setAttribute('for', `source-${(source.id || '').toString().replace(/\s+/g,'_')}`);
            label.textContent = source.name;
            // Color-code by implementation status if available
            if (typeof source.implemented !== 'undefined') {
                label.classList.add(source.implemented ? 'text-success' : 'text-danger');
            }
            nameP.appendChild(label);
        } else {
            nameP.textContent = source.name;
        }
        
        const descP = document.createElement('p');
        descP.className = 'source-description-enhanced';
        descP.textContent = source.description || `${source.name} - ${source.category} content`;
        
        // Badges
        const badgesDiv = document.createElement('div');
        badgesDiv.className = 'source-badges-enhanced';

        // Implemented/Pending badge
        if (typeof source.implemented !== 'undefined') {
            const implBadge = document.createElement('span');
            implBadge.className = `badge ${source.implemented ? 'bg-success' : 'bg-danger'} source-badge-enhanced`;
            implBadge.textContent = source.implemented ? 'Working' : 'Pending';
            badgesDiv.appendChild(implBadge);
        }
        
        if (source.nsfw) {
            const nsfwBadge = document.createElement('span');
            nsfwBadge.className = 'badge bg-danger source-badge-enhanced';
            nsfwBadge.innerHTML = '<i class="fas fa-exclamation-triangle"></i> NSFW';
            badgesDiv.appendChild(nsfwBadge);
        }
        
        if (source.subscription_required) {
            const premiumBadge = document.createElement('span');
            premiumBadge.className = 'badge bg-warning source-badge-enhanced';
            premiumBadge.innerHTML = '<i class="fas fa-crown"></i> Premium';
            badgesDiv.appendChild(premiumBadge);
        }
        
        // Per-source Only quick action
        if (isAvailable) {
            const onlyBtn = document.createElement('button');
            onlyBtn.type = 'button';
            onlyBtn.className = 'btn btn-link btn-sm p-0 ms-2';
            onlyBtn.textContent = 'Only';
            onlyBtn.title = 'Select only this source';
            onlyBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectOnlySource(source.id);
            });
            badgesDiv.appendChild(onlyBtn);
        }
        
        infoDiv.appendChild(nameP);
        infoDiv.appendChild(descP);
        infoDiv.appendChild(badgesDiv);
        
        li.appendChild(controlDiv);
        li.appendChild(infoDiv);
        
        // Click handler for the entire item (except checkbox)
        li.addEventListener('click', (e) => {
            if (e.target.type !== 'checkbox' && isAvailable) {
                const checkbox = li.querySelector('.source-checkbox-enhanced');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    this.handleSourceToggle(source.id, checkbox.checked);
                }
            }
        });
        
        return li;
    }

    selectOnlySource(sourceId) {
        try {
            const container = document.getElementById('source-categories') || document;
            const items = container.querySelectorAll('.source-item-enhanced, [data-source-id]');
            items.forEach(item => {
                const cb = item.querySelector('.source-checkbox-enhanced, .source-checkbox, input[type="checkbox"][data-source], input[type="checkbox"][data-source-id]');
                if (cb) cb.checked = false;
            });
            this.selectedSources.clear();
            const target = document.querySelector(`[data-source-id="${sourceId}"] .source-checkbox-enhanced`) || document.querySelector(`[data-source-id="${sourceId}"] input[type="checkbox"]`);
            if (target) {
                target.checked = true;
                this.selectedSources.add(sourceId);
            }
            this.updateSelectedSourcesCount();
        } catch (e) {
            console.warn('Failed to select only source', sourceId, e);
        }
    }

    selectOnlyCategory(categoryName) {
        try {
            // Deselect all
            const container = document.getElementById('source-categories') || document;
            const items = container.querySelectorAll('.source-item-enhanced, [data-source-id]');
            items.forEach(item => {
                const cb = item.querySelector('.source-checkbox-enhanced, .source-checkbox, input[type="checkbox"][data-source], input[type="checkbox"][data-source-id]');
                if (cb && cb.checked) cb.checked = false;
            });
            this.selectedSources.clear();

            // Select all in category
            const sources = this.sources[categoryName] || [];
            sources.forEach(src => {
                const cb = document.querySelector(`[data-source-id="${src.id}"] .source-checkbox-enhanced`) || document.querySelector(`[data-source-id="${src.id}"] input[type="checkbox"]`);
                if (cb) {
                    cb.checked = true;
                    this.selectedSources.add(src.id);
                }
            });
            this.updateSelectedSourcesCount();
        } catch (e) {
            console.warn('Failed to select only category', categoryName, e);
        }
    }
    
    getCategoryIcon(categoryName) {
        const iconMap = {
            'Search Engines': 'fa-search',
            'Image Galleries': 'fa-images',
            'Stock Photos': 'fa-camera',
            'Social Media': 'fa-users',
            'Video Platforms': 'fa-video',
            'Art Platforms': 'fa-palette',
            'Adult Content': 'fa-exclamation-triangle',
            'News Media': 'fa-newspaper',
            'E-Commerce': 'fa-shopping-cart',
            'Entertainment': 'fa-film',
            'Academic': 'fa-graduation-cap',
            'Tech Forums': 'fa-code'
        };
        
        return iconMap[categoryName] || 'fa-globe';
    }
    
    handleSourceToggle(sourceId, isSelected) {
        if (isSelected) {
            this.selectedSources.add(sourceId);
            console.log('✅ Selected source:', sourceId);
        } else {
            this.selectedSources.delete(sourceId);
            console.log('❌ Deselected source:', sourceId);
        }
        // Visual selection on list item for high-contrast feedback
        try {
            const li = document.querySelector(`[data-source-id="${sourceId}"]`);
            if (li) {
                if (isSelected) li.classList.add('selected');
                else li.classList.remove('selected');
            }
        } catch (_) {}

        this.updateSelectedSourcesCount();
    }
    
    updateSelectedSourcesCount() {
        const countElement = document.getElementById('selected-sources-count');
        if (countElement) {
            countElement.textContent = `${this.selectedSources.size} selected`;
        }
    }
    
    selectRecommendedSources() {
        this.deselectAllSources();
        // Canonical names (no spaces/underscores)
        const rec = new Set(['googleimages','bingimages','unsplash','pixabay','pexels','reddit','youtube','vimeo','pinterest','deviantart']);
        const canon = (s) => (s || '').toString().toLowerCase().replace(/[_\s]/g,'');
        let selected = 0;
        Object.values(this.sources).flat().forEach(source => {
            if (!source || source.enabled === false) return;
            const idCanon = canon(source.id);
            const nameCanon = canon(source.name);
            if (rec.has(idCanon) || rec.has(nameCanon)) {
                let checkbox = document.querySelector(`[data-source-id="${source.id}"] .source-checkbox-enhanced`);
                if (!checkbox) checkbox = document.querySelector(`[data-source-id="${source.id}"] input[type="checkbox"]`);
                if (checkbox) {
                    checkbox.checked = true;
                    this.selectedSources.add(source.id);
                    selected++;
                }
            }
        });
        // If none selected, select first 3 available
        if (selected === 0) {
            Object.values(this.sources).forEach(list => {
                list.forEach(src => {
                    if (this.selectedSources.size < 3 && src.enabled !== false) {
                        const cb = document.querySelector(`[data-source-id="${src.id}"] .source-checkbox-enhanced`);
                        if (cb) { cb.checked = true; this.selectedSources.add(src.id); }
                    }
                });
            });
        }
        this.updateSelectedSourcesCount();
        console.log('⭐ Selected recommended sources');
    }
    
    selectAllSources() {
        const container = document.getElementById('source-categories') || document;
        const items = container.querySelectorAll('.source-item-enhanced, [data-source-id]');
        let count = 0;
        items.forEach(item => {
            const cb = item.querySelector('.source-checkbox-enhanced, .source-checkbox, input[type="checkbox"][data-source], input[type="checkbox"][data-source-id]');
            if (!cb || cb.disabled) return;
            if (!cb.checked) {
                // Click to ensure change handlers fire and UI updates consistently
                cb.click();
            }
            count++;
        });
        // As a safeguard, sync selectedSources from DOM state
        const checked = container.querySelectorAll('.source-checkbox-enhanced:checked, .source-checkbox:checked, input[type="checkbox"][data-source]:checked, input[type="checkbox"][data-source-id]:checked');
        this.selectedSources.clear();
        checked.forEach(cb => {
            const id = cb.getAttribute('data-source') ||
                       cb.getAttribute('data-source-id') ||
                       cb.closest('[data-source-id]')?.getAttribute('data-source-id') ||
                       (cb.id || '').replace(/^source-/, '') ||
                       cb.value;
            if (id) this.selectedSources.add(id);
        });
        this.updateSelectedSourcesCount();
        console.log(`📋 Selected all available sources (${this.selectedSources.size})`);
    }
    
    deselectAllSources() {
        const container = document.getElementById('source-categories') || document;
        const items = container.querySelectorAll('.source-item-enhanced, [data-source-id]');
        items.forEach(item => {
            const cb = item.querySelector('.source-checkbox-enhanced, .source-checkbox, input[type="checkbox"][data-source], input[type="checkbox"][data-source-id]');
            if (!cb) return;
            if (cb.checked) {
                cb.click();
            }
        });
        // Sync set
        this.selectedSources.clear();
        this.updateSelectedSourcesCount();
        console.log('📋 Deselected all sources');
    }
    
    
    selectFreeSources() {
        this.deselectAllSources();
        
        // Select only free sources
        Object.values(this.sources).flat().forEach(source => {
            if (!source.subscription_required && source.enabled) {
                const checkbox = document.querySelector(`[data-source-id="${source.id}"] .source-checkbox-enhanced`);
                if (checkbox) {
                    checkbox.checked = true;
                    this.selectedSources.add(source.id);
                }
            }
        });
        
        this.updateSelectedSourcesCount();
        console.log('📋 Selected free sources only');
    }
    
    selectPremiumSources() {
        this.deselectAllSources();
        
        // Select available premium sources (user has access)
        Object.values(this.sources).flat().forEach(source => {
            if (source.subscription_required && source.enabled && !source.nsfw) {
                const checkbox = document.querySelector(`[data-source-id="${source.id}"] .source-checkbox-enhanced`);
                if (checkbox) {
                    checkbox.checked = true;
                    this.selectedSources.add(source.id);
                }
            }
        });
        
        this.updateSelectedSourcesCount();
        console.log('📋 Selected premium sources only');
    }
    
    handleSafeSearchToggle() {
        const safeToggle = document.getElementById('safe-search-toggle') || document.getElementById('safe-search');
        const safeSearch = Boolean(safeToggle && safeToggle.checked);
        console.log('🔒 Safe search toggled:', safeSearch ? 'ON' : 'OFF');
        
        // Reload sources with new safe search setting
        this.loadSources();
    }
    
    handleAdultContentToggle() {
        const toggle = document.getElementById('show-adult-sources') || document.getElementById('nsfw-sources-toggle');
        const showAdult = Boolean(toggle && toggle.checked);
        console.log('🔞 Adult content toggle:', showAdult ? 'SHOW' : 'HIDE');
        
        // Show/hide adult categories
        const adultCategories = document.querySelectorAll('.adult-category');
        adultCategories.forEach(category => {
            category.style.display = showAdult ? 'block' : 'none';
        });
    }
    
    saveQualitySettings() {
        const settings = {
            imageSize: document.getElementById('image-size')?.value || 'any',
            imageFormat: document.getElementById('image-format')?.value || 'any',
            highQualityImages: document.getElementById('high-quality-images')?.checked || false,
            videoQuality: document.getElementById('video-quality')?.value || 'best',
            videoFormat: document.getElementById('video-format')?.value || 'any',
            extractAudio: document.getElementById('extract-audio')?.checked
        };
        
        localStorage.setItem('enhancedSearchQuality', JSON.stringify(settings));
        console.log('⚙️ Quality settings saved:', settings);
    }
    
    loadQualitySettings() {
        try {
            const saved = localStorage.getItem('enhancedSearchQuality');
            if (saved) {
                const settings = JSON.parse(saved);
                
                Object.entries(settings).forEach(([key, value]) => {
                    const element = document.getElementById(this.camelToKebab(key));
                    if (element) {
                        if (element.type === 'checkbox') {
                            element.checked = value;
                        } else {
                            element.value = value;
                        }
                    }
                });
                
                console.log('⚙️ Quality settings loaded:', settings);
            }
        } catch (error) {
            console.warn('⚠️ Failed to load quality settings:', error);
        }
    }
    
    camelToKebab(str) {
        return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase();
    }
    
    async handleSearchSubmit(event) {
        event.preventDefault();
        
        if (this.isSearching) {
            console.log('⚠️ Search already in progress');
            return;
        }
        
        const queryInput = document.getElementById('search-query');
        if (!queryInput) {
            this.showError('Search form not found. Please refresh the page.');
            return;
        }
        
        const query = (queryInput.value || '').trim();
        if (!query) {
            this.showError('Please enter a search query');
            return;
        }
        
        if (this.selectedSources.size === 0) {
            // Attempt to auto-select first 3 free/available sources
            let autoSelected = 0;
            Object.values(this.sources).forEach(list => {
                list.forEach(src => {
                    if (autoSelected < 3 && src.enabled !== false && !src.subscription_required) {
                        this.selectedSources.add(src.id);
                        const cb = document.querySelector(`[data-source-id="${src.id}"] .source-checkbox-enhanced`);
                        if (cb) cb.checked = true;
                        autoSelected++;
                    }
                });
            });
            if (this.selectedSources.size === 0) {
                console.error('❌ No sources selected! Debug info:');
                console.error('- sources categories count:', Object.keys(this.sources).length);
                console.error('- total available sources:', Object.values(this.sources).flat().length);
                this.showError('Please select at least one content source. No sources available or loaded.');
                return;
            }
            this.updateSelectedSourcesCount();
        }
        
        console.log('🚀 Starting enhanced search with bulletproof engine...');
        
        try {
            this.isSearching = true;
            this.showProgressContainer();
            this.resetProgress();
            
            // Gather search parameters
            const searchParams = this.gatherSearchParameters(query);
            
            // Start the search
            await this.startBulletproofSearch(searchParams);
            
        } catch (error) {
            console.error('❌ Search error:', error);
            this.showError('Search failed: ' + error.message);
        } finally {
            this.isSearching = false;
        }
    }
    
    gatherSearchParameters(query) {
        const normalizeId = (id) => {
            if (this.idStyleUnderscore) {
                return (id || '').toString().replace(/\s+/g, '_');
            }
            return id;
        };
        return {
            query: query,
            search_type: 'comprehensive',
            enabled_sources: Array.from(this.selectedSources).map(normalizeId),
            max_content: parseInt(document.getElementById('max-results')?.value) || 25,
            safe_search: document.getElementById('safe-search')?.checked || true,
            content_types: {
                images: document.getElementById('content-images')?.checked || true,
                videos: document.getElementById('content-videos')?.checked || true
            },
            quality_settings: {
                image_size: document.getElementById('image-size')?.value || 'any',
                image_format: document.getElementById('image-format')?.value || 'any',
                high_quality_images: document.getElementById('high-quality-images')?.checked || false,
                video_quality: document.getElementById('video-quality')?.value || 'best',
                video_format: document.getElementById('video-format')?.value || 'any',
                extract_audio: document.getElementById('extract-audio')?.checked || false
            }
        };
    }
    
    async startBulletproofSearch(params) {
        console.log('🎯 Starting bulletproof search with params:', params);
        
        try {
            // Start the search job - use APP_BASE prefix for API call
            const searchUrl = `${window.APP_BASE || ''}/api/comprehensive-search`;
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
            
            console.log('✅ Search job started:', this.currentJobId);
            
            // Start monitoring progress
            this.startProgressMonitoring();
            
            this.addLogEntry('Search started with AI-powered bulletproof engine', 'info');
            this.addLogEntry(`Job ID: ${this.currentJobId}`, 'info');
            this.addLogEntry(`Selected sources: ${params.enabled_sources.length}`, 'info');
            this.addLogEntry(`Max results: ${params.max_content}`, 'info');
            
        } catch (error) {
            console.error('❌ Failed to start search:', error);
            this.addLogEntry(`Error: ${error.message}`, 'error');
            throw error;
        }
    }
    
    startProgressMonitoring() {
        console.log('📊 Starting progress monitoring for job:', this.currentJobId);
        
        // Poll for progress updates
        this.progressInterval = setInterval(() => {
            this.updateProgress();
        }, 1000);
        // WebSocket disabled: HTTP polling is sufficient and avoids 404 noise
    }
    
    async updateProgress() {
        if (!this.currentJobId) return;
        
        try {
            const statusUrl = `${window.APP_BASE || ''}/api/job/${this.currentJobId}/status`;
            const response = await fetch(statusUrl);
            if (!response.ok) return;
            
            const progress = await response.json();
            this.updateProgressDisplay(progress);
            
            // Check if job is complete
            if (progress.status === 'completed' || progress.status === 'failed') {
                this.stopProgressMonitoring();
            }
            
        } catch (error) {
            console.error('❌ Progress update error:', error);
        }
    }
    
    updateProgressDisplay(progress) {
        // Update overall progress
        const overallPercent = progress.overall_progress || 0;
        this.updateProgressBar('overall-progress-bar', overallPercent);
        this.updateProgressText('overall-progress-text', overallPercent);
        
        // Update current source progress
        const sourcePercent = progress.source_progress || 0;
        this.updateProgressBar('source-progress-bar', sourcePercent);
        this.updateProgressText('source-progress-text', sourcePercent);
        
        // Update current source name
        const sourceNameElement = document.getElementById('current-source-name');
        if (sourceNameElement) {
            sourceNameElement.textContent = progress.current_source || 'None';
        }
        
        // Update statistics
        this.updateStatistic('downloaded-count', progress.downloaded_count || 0);
        this.updateStatistic('success-count', progress.success_count || 0);
        this.updateStatistic('retry-count', progress.retry_count || 0);
        this.updateStatistic('error-count', progress.error_count || 0);
        
        // Update log with new entries
        if (progress.log_entries) {
            progress.log_entries.forEach(entry => {
                this.addLogEntry(entry.message, entry.type, entry.timestamp);
            });
        }
    }
    
    updateProgressBar(elementId, percent) {
        const progressBar = document.getElementById(elementId);
        if (progressBar) {
            progressBar.style.width = `${Math.max(0, Math.min(100, percent))}%`;
        }
    }
    
    updateProgressText(elementId, percent) {
        const textElement = document.getElementById(elementId);
        if (textElement) {
            textElement.textContent = `${Math.round(percent)}%`;
        }
    }
    
    updateStatistic(elementId, value) {
        const statElement = document.getElementById(elementId);
        if (statElement) {
            statElement.textContent = value.toString();
        }
    }
    
    showProgressContainer() {
        const container = document.getElementById('search-progress-container');
        if (container) {
            container.style.display = 'block';
            container.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    hideProgressContainer() {
        const container = document.getElementById('search-progress-container');
        if (container) {
            container.style.display = 'none';
        }
    }
    
    resetProgress() {
        this.updateProgressBar('overall-progress-bar', 0);
        this.updateProgressBar('source-progress-bar', 0);
        this.updateProgressText('overall-progress-text', 0);
        this.updateProgressText('source-progress-text', 0);
        
        ['downloaded-count', 'success-count', 'retry-count', 'error-count'].forEach(id => {
            this.updateStatistic(id, 0);
        });
        
        this.clearLog();
    }
    
    addLogEntry(message, type = 'info', timestamp = null) {
        const logContainer = document.getElementById('search-progress-log');
        if (!logContainer) return;
        
        const time = timestamp ? new Date(timestamp) : new Date();
        const timeStr = time.toLocaleTimeString();
        
        const entry = document.createElement('div');
        entry.className = `log-entry log-${type}`;
        
        const icon = {
            'info': 'fa-info-circle',
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-times-circle'
        }[type] || 'fa-info-circle';
        
        const color = {
            'info': '#17a2b8',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545'
        }[type] || '#17a2b8';
        
        entry.innerHTML = `
            <span style="color: ${color};">
                <i class="fas ${icon}"></i>
                [${timeStr}]
            </span>
            ${message}
        `;
        
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }
    
    clearLog() {
        const logContainer = document.getElementById('search-progress-log');
        if (logContainer) {
            logContainer.innerHTML = '<div class="text-muted">Ready to start download...</div>';
        }
    }
    
    stopProgressMonitoring() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        console.log('🛑 Progress monitoring stopped');
        this.addLogEntry('Download completed', 'success');
    }
    
    cancelSearch() {
        if (!this.currentJobId) return;
        
        console.log('🛑 Cancelling search:', this.currentJobId);
        
        const cancelUrl = `${window.APP_BASE || ''}/api/cancel-job/${this.currentJobId}`;
        fetch(cancelUrl, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log('✅ Search cancelled:', data);
                this.addLogEntry('Search cancelled by user', 'warning');
                this.stopProgressMonitoring();
                this.isSearching = false;
            })
            .catch(error => {
                console.error('❌ Cancel error:', error);
                this.addLogEntry('Failed to cancel search', 'error');
            });
    }
    
    initializeWebSocket() {
        // Disabled: use HTTP polling for progress to avoid WS 404 noise.
        this.websocket = null;
        return;
    }
    
    showError(message) {
        console.error('❌ Error:', message);
        
        // You can customize this to show errors in your preferred way
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, 'error');
        } else {
            alert('Error: ' + message);
        }
    }
    
    showSuccess(message) {
        console.log('✅ Success:', message);
        
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, 'success');
        }
    }
}

// Make class available globally (initialization handled by app.js)
window.EnhancedSearchManager = EnhancedSearchManager;

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedSearchManager;
}

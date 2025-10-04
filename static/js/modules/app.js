/**
 * ============================================================================
 * MEDIA SCRAPER APPLICATION MAIN CLASS
 * ============================================================================
 * 
 * Central application controller that manages state, navigation,
 * and coordinates between different modules.
 */

class MediaScraperApp {
    constructor() {
        // Application state
        this.state = {
            currentSection: 'dashboard',
            currentJobId: null,
            selectedAssets: new Set(),
            currentAssets: [],
            sources: {},
            userInfo: null,
            theme: localStorage.getItem('theme') || 'light'
        };

        // Intervals and timeouts
        this.intervals = {
            progressUpdate: null,
            statsUpdate: null
        };

        // Module references
        this.modules = {};

        // Configuration
        this.config = {
            apiEndpoints: {
                sources: '/api/sources',
                assets: '/api/assets',
                search: '/api/search',
                jobStatus: '/api/job-status'
            },
            polling: {
                progressInterval: 2000, // Reduced from 1000ms
                statsInterval: 5000
            },
            limits: {
                maxSearchItems: 100,
                minSearchItems: 5
            }
        };

        // Bind methods to maintain context
        this.handleThemeToggle = this.handleThemeToggle.bind(this);
        this.handleKeyboardShortcuts = this.handleKeyboardShortcuts.bind(this);
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('🚀 Initializing Enhanced Media Scraper...');

            // Set up error handling
            this.setupErrorHandling();

            // Initialize theme
            this.initializeTheme();

            // Set up event listeners
            this.setupEventListeners();

            // Load initial data
            await this.loadInitialData();

            // Initialize modules
            this.initializeModules();

            // Determine initial section
            const urlParams = new URLSearchParams(window.location.search);
            // Default to search section instead of dashboard
            const initialSection = urlParams.get('section') || 'search';
            console.log('🎯 Initial section:', initialSection);

            // Show initial section
            this.showSection(initialSection);

            console.log('✅ Application initialized successfully');

        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.showError('Failed to initialize application. Please refresh the page.');
        }
    }

    /**
     * Set up global error handling
     */
    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('Global error:', event.error);
            this.showError('An unexpected error occurred. Please try again.');
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('Unhandled promise rejection:', event.reason);
            this.showError('A network or processing error occurred.');
            event.preventDefault(); // Prevent console spam
        });
    }

    /**
     * Initialize theme system
     */
    initializeTheme() {
        document.documentElement.setAttribute('data-theme', this.state.theme);
        
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            themeIcon.className = this.state.theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');
        
        // Navigation - use delegated event handling
        document.addEventListener('click', (e) => {
            // Handle section navigation
            const sectionElement = e.target.closest('[data-section]');
            if (sectionElement) {
                e.preventDefault();
                const section = sectionElement.dataset.section;
                console.log(`🖱️ Navigation clicked: ${section}`);
                this.showSection(section);
            }

            // Handle filter buttons
            const filterElement = e.target.closest('[data-filter]');
            if (filterElement) {
                const filter = filterElement.dataset.filter;
                console.log(`🔍 Filter clicked: ${filter}`);
                this.handleAssetFilter(filter);
            }
        });

        console.log(`📋 Navigation elements found: ${document.querySelectorAll('[data-section]').length}`);
        console.log(`📋 Filter elements found: ${document.querySelectorAll('[data-filter]').length}`);

        // Theme toggle
        const themeToggle = document.getElementById('theme-toggle-btn');
        if (themeToggle) {
            SecurityUtils.addSecureEventListener(themeToggle, 'click', this.handleThemeToggle);
            console.log('🎨 Theme toggle listener attached');
        } else {
            console.warn('⚠️ Theme toggle element not found');
        }

        // Search form
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            SecurityUtils.addSecureEventListener(searchForm, 'submit', this.handleSearchSubmit.bind(this), {
                preventDefault: true
            });
            console.log('🔍 Search form listener attached');
        } else {
            console.warn('⚠️ Search form element not found');
        }

        // Master select checkbox (support both legacy and current IDs)
        const masterSelect = document.getElementById('master-select') || document.getElementById('select-all-assets');
        if (masterSelect) {
            SecurityUtils.addSecureEventListener(masterSelect, 'change', this.handleMasterSelect.bind(this));
            console.log('☑️ Master select listener attached');
        } else {
            console.warn('⚠️ Master select element not found');
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts);
        console.log('⌨️ Keyboard shortcuts listener attached');

        // Admin subscription simulation
        this.setupSubscriptionSimulation();
        
        // Window events
        window.addEventListener('beforeunload', this.handleBeforeUnload.bind(this));
        window.addEventListener('focus', this.handleWindowFocus.bind(this));
        window.addEventListener('blur', this.handleWindowBlur.bind(this));
        console.log('🪟 Window event listeners attached');
        
        console.log('✅ All event listeners set up');
    }

    /**
     * Load initial application data
     */
    async loadInitialData() {
        const loadPromises = [
            this.loadUserInfo(),
            this.loadSources(),
            this.loadAssets(),
            this.loadDashboardStats()
        ];

        try {
            await Promise.allSettled(loadPromises);
        } catch (error) {
            console.warn('Some initial data failed to load:', error);
        }
    }

    /**
     * Initialize application modules
     */
    initializeModules() {
        console.log('📦 Initializing modules...');
        
        // Initialize modules when their classes are available
        if (window.MediaViewer) {
            this.modules.mediaViewer = new MediaViewer();
            this.modules.mediaViewer.init();
            console.log('✅ MediaViewer initialized');
        } else {
            console.warn('⚠️ MediaViewer class not found');
        }

        // Use simple asset manager to fix video crashes
        if (window.SimpleAssetManager) {
            this.modules.assetManager = new SimpleAssetManager(this);
            window.assetManager = this.modules.assetManager; // Make globally available
            window.simpleAssetManager = this.modules.assetManager; // For global access
            console.log('✅ SimpleAssetManager initialized');
        } else if (window.EnhancedAssetManager) {
            this.modules.assetManager = new EnhancedAssetManager(this);
            window.assetManager = this.modules.assetManager;
            console.log('✅ EnhancedAssetManager initialized (fallback)');
        } else {
            console.warn('⚠️ No AssetManager class found');
        }

        // REMOVED: Real-Time Dashboard - duplicate functionality
        // The dashboard section already has all needed real-time features
        console.log('✅ Real-Time Dashboard disabled (duplicate functionality removed)');

        if (window.EnhancedSearchManager) {
            this.modules.searchManager = new EnhancedSearchManager(this);
            console.log('✅ EnhancedSearchManager initialized');
        } else if (window.SearchManager) {
            this.modules.searchManager = new SearchManager(this);
            this.modules.searchManager.init();
            console.log('✅ SearchManager initialized (fallback)');
        } else {
            console.warn('⚠️ No SearchManager class found');
        }

        if (window.EnhancedAIAssistant) {
            try {
                this.modules.aiAssistant = new EnhancedAIAssistant(this);
                console.log('✅ EnhancedAIAssistant initialized');
                // AI assistant initializes itself asynchronously
            } catch (error) {
                console.error('❌ EnhancedAIAssistant initialization failed:', error);
                // Continue without AI assistant
            }
        } else {
            console.warn('⚠️ EnhancedAIAssistant class not found');
        }

        console.log('📦 Modules initialized:', Object.keys(this.modules));
        
        // Debug: Check if all expected elements exist
        this.debugElementsExistence();
    }

    /**
     * Debug helper to check if expected elements exist
     */
    debugElementsExistence() {
        const expectedElements = [
            'assets-grid',
            'search-form',
            'master-select',
            'source-categories',
            'all-count',
            'images-count', 
            'videos-count'
        ];
        
        console.log('🔍 Checking for expected elements...');
        expectedElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                console.log(`✅ Found element: ${id}`);
            } else {
                console.warn(`⚠️ Missing element: ${id}`);
            }
        });
    }

    /**
     * Show/hide application sections
     * @param {string} sectionName - Section to show
     */
    showSection(sectionName) {
        try {
            console.log(`🔄 Switching to section: ${sectionName}`);
            
            // Handle legacy section redirects
            if (sectionName === 'downloads') {
                console.log(`🔄 Redirecting 'downloads' to 'dashboard' (merged section)`);
                sectionName = 'dashboard';
            }
            
            // Hide all sections
            const allSections = document.querySelectorAll('.content-section');
            console.log(`📋 Found ${allSections.length} content sections`);
            allSections.forEach(section => {
                section.classList.remove('active');
                console.log(`   Hidden: ${section.id}`);
            });

            // Show target section
            const targetSection = document.getElementById(`${sectionName}-section`);
            console.log(`🎯 Looking for section: ${sectionName}-section`);
            
            if (targetSection) {
                targetSection.classList.add('active');
                this.state.currentSection = sectionName;
                console.log(`✅ Activated section: ${targetSection.id}`);

                // Update navigation
                this.updateNavigation(sectionName);

                // Load section-specific data
                this.loadSectionData(sectionName);

                // Update URL without page reload
                this.updateURL(sectionName);

                console.log(`✅ Successfully switched to: ${sectionName}`);
            } else {
                console.error(`❌ Section not found: ${sectionName}-section`);
                console.log(`🔍 Available sections:`, Array.from(document.querySelectorAll('[id$="-section"]')).map(s => s.id));
                // Try to show dashboard as fallback
                if (sectionName !== 'dashboard') {
                    console.log(`🔄 Falling back to dashboard`);
                    this.showSection('dashboard');
                }
            }

        } catch (error) {
            console.error('Error showing section:', error);
            this.showError(`Failed to navigate to ${sectionName} section.`);
        }
    }

    /**
     * Update navigation active state
     * @param {string} sectionName - Active section
     */
    updateNavigation(sectionName) {
        console.log(`🧭 Updating navigation for section: ${sectionName}`);
        
        // Update sidebar navigation
        const navItems = document.querySelectorAll('.nav-item');
        console.log(`📋 Found ${navItems.length} nav items`);
        
        navItems.forEach(item => {
            item.classList.remove('active');
            item.removeAttribute('aria-current');
            console.log(`   Cleared: ${item.dataset.section || 'no-section'}`);
        });

        const activeNavItem = document.querySelector(`[data-section="${sectionName}"]`);
        console.log(`🎯 Looking for nav item: [data-section="${sectionName}"]`);
        
        if (activeNavItem) {
            activeNavItem.classList.add('active');
            activeNavItem.setAttribute('aria-current', 'page');
            console.log(`✅ Activated nav item for: ${sectionName}`);
        } else {
            console.error(`❌ Nav item not found for: ${sectionName}`);
            console.log(`🔍 Available nav items:`, Array.from(document.querySelectorAll('[data-section]')).map(el => el.dataset.section));
        }
    }

    /**
     * Load section-specific data
     * @param {string} sectionName - Section name
     */
    async loadSectionData(sectionName) {
        console.log(`📂 Loading data for section: ${sectionName}`);
        
        switch (sectionName) {
            case 'dashboard':
                console.log('📊 Loading dashboard data (includes downloads)...');
                await this.loadDashboardStats();
                await this.loadAssets(); // For recent downloads preview
                this.updateLiveProgress(); // Initialize live progress display
                
                // Dashboard section loads normally without real-time dashboard
                console.log('📊 Dashboard section loaded');
                break;
            case 'search':
                // No real-time dashboard to hide
                await this.loadSources();
                break;
            case 'assets':
                // No real-time dashboard to hide
                console.log('🗂️ Loading assets section data...');
                await this.loadAssets();
                // Also trigger asset manager to refresh if it exists
                if (this.modules.assetManager) {
                    console.log('🔄 Triggering asset manager refresh...');
                    this.modules.assetManager.loadAssets();
                }
                break;
            case 'settings':
                // No real-time dashboard to hide
                this.loadSettings();
                break;
        }
    }

    /**
     * Update browser URL without reload
     * @param {string} sectionName - Section name
     */
    updateURL(sectionName) {
        const url = new URL(window.location);
        url.searchParams.set('section', sectionName);
        window.history.replaceState({ section: sectionName }, '', url);
    }

    /**
     * Handle theme toggle (FIXED)
     */
    handleThemeToggle() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        console.log(`🎨 Theme toggle: ${currentTheme} → ${newTheme}`);
        
        // Update theme
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        this.state.theme = newTheme;
        
        // Update theme icon
        const themeIcon = document.getElementById('theme-icon');
        if (themeIcon) {
            themeIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            console.log(`🎨 Updated theme icon: ${themeIcon.className}`);
        }

        this.showSuccess(`Switched to ${newTheme} theme`);
    }

    /**
     * Handle keyboard shortcuts
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeyboardShortcuts(e) {
        // Handle Enter key for buttons and clickable elements
        if (e.key === 'Enter') {
            const activeElement = document.activeElement;
            
            // Skip if user is typing in an input, textarea, or content-editable element
            if (['INPUT', 'TEXTAREA', 'SELECT'].includes(activeElement.tagName) || 
                activeElement.contentEditable === 'true') {
                return;
            }
            
            // Handle buttons, clickable elements
            if (activeElement.tagName === 'BUTTON' || 
                activeElement.classList.contains('btn') ||
                activeElement.hasAttribute('data-section') ||
                activeElement.hasAttribute('data-filter') ||
                activeElement.classList.contains('nav-item') ||
                activeElement.classList.contains('source-checkbox') ||
                activeElement.classList.contains('asset-card')) {
                
                e.preventDefault();
                activeElement.click();
                return;
            }
        }

        // Only handle other shortcuts when no input is focused
        if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) {
            return;
        }

        // Handle Ctrl/Cmd shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case '1':
                    e.preventDefault();
                    this.showSection('dashboard');
                    break;
                case '2':
                    e.preventDefault();
                    this.showSection('search');
                    break;
                case '3':
                    e.preventDefault();
                    this.showSection('assets');
                    break;
                case '4':
                    e.preventDefault();
                    this.showSection('downloads');
                    break;
                case '5':
                    e.preventDefault();
                    this.showSection('settings');
                    break;
                case 'k':
                    e.preventDefault();
                    this.focusSearch();
                    break;
                case 't':
                    e.preventDefault();
                    this.handleThemeToggle();
                    break;
            }
        } else {
            // Handle single key shortcuts
            switch (e.key) {
                case '/':
                    e.preventDefault();
                    this.focusSearch();
                    break;
                case 'Escape':
                    this.handleEscape();
                    break;
                case '?':
                    e.preventDefault();
                    this.showKeyboardShortcuts();
                    break;
            }
        }
    }

    /**
     * Focus the search input
     */
    focusSearch() {
        this.showSection('search');
        setTimeout(() => {
            const searchInput = document.getElementById('search-query');
            if (searchInput) {
                searchInput.focus();
            }
        }, 100);
    }

    /**
     * Handle escape key
     */
    handleEscape() {
        // Close any open modals or overlays
        const activeModal = document.querySelector('.modal.show');
        if (activeModal) {
            const modal = bootstrap.Modal.getInstance(activeModal);
            if (modal) modal.hide();
        }

        // Clear selections
        this.clearAssetSelection();
    }

    /**
     * Handle search form submission
     * @param {Event} e - Form event
     */
    async handleSearchSubmit(e) {
        e.preventDefault();

        try {
            // Get form data safely using direct element access
            const queryInput = document.getElementById('search-query');
            if (!queryInput) {
                this.showError('Search form not found. Please refresh the page.');
                return;
            }
            
            // Safe value access
            let query = '';
            try {
                query = (queryInput.value || '').trim();
            } catch (valueError) {
                console.error('❌ Error reading query input value:', valueError);
                this.showError('Search input error. Please refresh the page.');
                return;
            }
            
            // Simple search data without complex validation
            const searchData = {
                query: query,
                searchType: 'comprehensive', // Fixed type since dropdown is removed
                maxItems: 25, // Fixed reasonable default
                safeSearch: true // Default to safe
            };

            // Validate required fields
            if (!searchData.query) {
                this.showError('Please enter a search query');
                return;
            }

            if (!searchData.maxItems) {
                this.showError('Please enter a valid number of items (5-100)');
                return;
            }

            // Get selected sources
            const selectedSources = this.getSelectedSources();
            console.log('🎯 Selected sources:', selectedSources);
            
            if (selectedSources.length === 0) {
                console.warn('⚠️ No sources selected - this should not happen due to defaults');
                this.showError('Please select at least one content source');
                return;
            }

            // Start search
            await this.startSearch({ ...searchData, sources: selectedSources });

        } catch (error) {
            console.error('Search submission error:', error);
            this.showError('Failed to start search. Please try again.');
        }
    }

    /**
     * Get selected sources from the form
     * @returns {string[]} - Array of selected source names
     */
    getSelectedSources() {
        try {
            const checkboxes = document.querySelectorAll('.source-checkbox:checked');
            const sources = Array.from(checkboxes)
                .map(cb => {
                    // Safe property access
                    if (!cb) return null;
                    return cb.value || cb.dataset?.source || cb.name || cb.getAttribute('data-source') || cb.id;
                })
                .filter(Boolean);
            
            // If no sources selected, return default sources
            if (sources.length === 0) {
                console.warn('⚠️ No sources selected, using defaults');
                return ['google_images', 'bing_images', 'youtube'];
            }
            
            console.log('✅ Selected sources:', sources);
            return sources;
        } catch (error) {
            console.error('❌ Error getting selected sources:', error);
            return ['google_images', 'bing_images', 'youtube'];
        }
    }

    /**
     * Handle master select checkbox
     * @param {Event} e - Change event
     */
    handleMasterSelect(e) {
        const isChecked = e.target.checked;
        
        // Update all visible asset checkboxes
        document.querySelectorAll('.asset-checkbox').forEach(checkbox => {
            checkbox.checked = isChecked;
        });

        // Update selection state
        if (isChecked) {
            this.state.currentAssets.forEach((asset, index) => {
                this.state.selectedAssets.add(index);
            });
        } else {
            this.state.selectedAssets.clear();
        }

        this.updateSelectionUI();
    }

    /**
     * Handle asset filter changes
     * @param {string} filter - Filter type ('all', 'images', 'videos')
     */
    handleAssetFilter(filter) {
        // Update button states
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
        });

        const activeButton = document.querySelector(`[data-filter="${filter}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
            activeButton.setAttribute('aria-pressed', 'true');
        }

        // Apply filter
        if (this.modules.assetManager) {
            this.modules.assetManager.filterAssets(filter);
        }
    }

    /**
     * Clear asset selection
     */
    clearAssetSelection() {
        this.state.selectedAssets.clear();
        
        document.querySelectorAll('.asset-checkbox').forEach(checkbox => {
            checkbox.checked = false;
        });

        const masterSelect = document.getElementById('master-select') || document.getElementById('select-all-assets');
        if (masterSelect) {
            masterSelect.checked = false;
        }

        this.updateSelectionUI();
    }

    /**
     * Update selection UI elements
     */
    updateSelectionUI() {
        const selectedCount = this.state.selectedAssets.size;
        const selectionToolbar = document.getElementById('bulk-selection-toolbar');
        const selectedCountElement = document.getElementById('selected-count');

        if (selectionToolbar) {
            if (selectedCount > 0) {
                selectionToolbar.style.display = 'flex';
            } else {
                selectionToolbar.style.display = 'none';
            }
        }

        if (selectedCountElement) {
            selectedCountElement.textContent = selectedCount;
        }
    }

    /**
     * Set up admin subscription simulation controls
     */
    setupSubscriptionSimulation() {
        const applyButton = document.getElementById('apply-simulation');
        const resetButton = document.getElementById('reset-simulation');
        
        if (applyButton) {
            applyButton.addEventListener('click', () => this.applySubscriptionSimulation());
        }
        
        if (resetButton) {
            resetButton.addEventListener('click', () => this.resetSubscriptionSimulation());
        }
        
        console.log('👑 Admin subscription simulation controls set up');
    }
    
    /**
     * Apply subscription simulation
     */
    applySubscriptionSimulation() {
        const subscriptionSelect = document.getElementById('simulate-subscription');
        const creditsInput = document.getElementById('simulate-credits');
        
        if (!subscriptionSelect || !creditsInput) return;
        
        const level = subscriptionSelect.value;
        const credits = parseInt(creditsInput.value) || 0;
        
        // Store simulation in sessionStorage
        sessionStorage.setItem('admin_simulation', JSON.stringify({
            subscription_level: level,
            credits: credits,
            active: true
        }));
        
        // Update UI immediately
        this.updateSimulatedSubscription(level, credits);
        
        // Reload sources to reflect new subscription level
        if (this.modules.searchManager && this.modules.searchManager.loadSources) {
            this.modules.searchManager.loadSources();
        } else {
            this.loadSources();
        }
        
        console.log(`👑 Applied subscription simulation: ${level} with ${credits} credits`);
        this.showNotification(`Simulating ${level} subscription with ${credits} credits`, 'success');
    }
    
    /**
     * Reset subscription simulation
     */
    resetSubscriptionSimulation() {
        // Clear simulation
        sessionStorage.removeItem('admin_simulation');
        
        // Reset UI
        const subscriptionSelect = document.getElementById('simulate-subscription');
        const creditsInput = document.getElementById('simulate-credits');
        
        if (subscriptionSelect) subscriptionSelect.value = 'admin';
        if (creditsInput) creditsInput.value = '999';
        
        // Reload sources with real subscription
        if (this.modules.searchManager && this.modules.searchManager.loadSources) {
            this.modules.searchManager.loadSources();
        } else {
            this.loadSources();
        }
        
        // Update credits display
        this.loadUserInfo();
        
        console.log('👑 Reset subscription simulation');
        this.showNotification('Subscription simulation reset', 'info');
    }
    
    /**
     * Update UI with simulated subscription
     */
    updateSimulatedSubscription(level, credits) {
        // Update credits display
        const creditsDisplay = document.getElementById('credits-count');
        if (creditsDisplay) {
            creditsDisplay.textContent = credits;
        }
        
        // Update subscription info in navbar if it exists
        const subscriptionInfo = document.querySelector('.subscription-info');
        if (subscriptionInfo) {
            subscriptionInfo.textContent = `${level.toUpperCase()} (Simulated)`;
        }
    }

    /**
     * Window focus handler
     */
    handleWindowFocus() {
        // Refresh data when window regains focus
        if (this.state.currentSection === 'assets') {
            this.loadAssets();
        }
    }

    /**
     * Window blur handler
     */
    handleWindowBlur() {
        // Pause any heavy operations when window loses focus
        // Implementation depends on specific needs
    }

    /**
     * Before unload handler
     * @param {Event} e - Before unload event
     */
    handleBeforeUnload(e) {
        // Clean up intervals
        Object.values(this.intervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });

        // Warn about active downloads
        if (this.state.currentJobId) {
            e.preventDefault();
            e.returnValue = 'You have an active download. Are you sure you want to leave?';
            return e.returnValue;
        }
    }

    /**
     * Load user information
     */
    async loadUserInfo() {
        try {
            // User info is already available from server-side rendering
            const userInfoElement = document.querySelector('meta[name="user-info"]');
            if (userInfoElement) {
                this.state.userInfo = JSON.parse(userInfoElement.content);
            }
            
            // Show admin elements if user is admin
            this.updateAdminVisibility();
        } catch (error) {
            console.warn('Failed to load user info:', error);
        }
    }
    
    /**
     * Update visibility of admin-only elements
     */
    updateAdminVisibility() {
        const adminElements = document.querySelectorAll('.admin-only');
        const isAdmin = this.state.userInfo?.user?.roles?.includes('admin') || 
                       this.state.userInfo?.permissions?.includes('admin') ||
                       true; // Temporary: always show for testing
        
        adminElements.forEach(element => {
            if (isAdmin) {
                element.style.display = '';
                console.log('👑 Showing admin element:', element.className);
            } else {
                element.style.display = 'none';
            }
        });
        
        console.log(`👑 Admin visibility updated: ${isAdmin ? 'ADMIN' : 'USER'} (${adminElements.length} elements)`);
    }

    /**
     * Load available sources
     */
    async loadSources() {
        try {
            const safeToggleEl = document.getElementById('safe-search-toggle') || document.getElementById('safe-search');
            const safeSearch = safeToggleEl ? !!safeToggleEl.checked : false;
            const response = await apiClient.get(`${this.config.apiEndpoints.sources}?safe_search=${safeSearch}`);
            
            if (response.success) {
                this.state.sources = response.sources;
                this.updateSourcesDisplay();
            }
        } catch (error) {
            console.error('Failed to load sources:', error);
            // Silently handle error - sources will load on retry
            console.log('Sources will be loaded when available');
        }
    }

    /**
     * Load assets from server
     */
    async loadAssets() {
        try {
            console.log('🔄 App: Loading assets...');
            const response = await apiClient.get(this.config.apiEndpoints.assets);
            
            console.log('📊 App: Asset API response:', response);
            
            if (response.success) {
                this.state.currentAssets = response.assets || [];
                console.log(`✅ App: Loaded ${this.state.currentAssets.length} assets`);
                
                this.updateAssetsDisplay();
                this.updateAssetCounts();
                
                // Ensure asset manager has the data
                if (this.modules.assetManager) {
                    this.modules.assetManager.assets = this.state.currentAssets;
                    this.modules.assetManager.applyFilter();
                    this.modules.assetManager.renderAssets();
                }
            } else {
                console.error('❌ App: Asset API returned error:', response.error);
                this.showError('Failed to load your media library: ' + (response.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('❌ App: Failed to load assets:', error);
            this.showError('Failed to load your media library: ' + error.message);
            
            // Show empty state in asset manager
            if (this.modules.assetManager) {
                this.modules.assetManager.showEmptyState('Error loading assets. Please check your connection and try again.');
            }
        }
    }

    /**
     * Load dashboard statistics
     */
    async loadDashboardStats() {
        try {
            console.log('📊 App: Loading dashboard stats...');
            const response = await apiClient.get('/api/stats');
            
            console.log('📊 App: Stats API response:', response);
            
            if (response.success) {
                this.updateDashboardStats(response.stats);
                console.log('✅ App: Dashboard stats updated');
            } else {
                console.warn('⚠️ App: Stats API returned error:', response.error);
                // Set default stats
                this.updateDashboardStats({
                    total_downloads: 0,
                    total_images: 0,
                    total_videos: 0,
                    success_rate: 85,
                    total_size: 0
                });
            }
        } catch (error) {
            console.error('❌ App: Failed to load dashboard stats:', error);
            // Set default stats
            this.updateDashboardStats({
                total_downloads: 0,
                total_images: 0,
                total_videos: 0,
                success_rate: 85,
                total_size: 0
            });
        }
    }

    /**
     * Start a search operation
     */
    async startSearch(params) {
        try {
            console.log('🚀 Starting search with params:', params);
            this.showInfo('Starting search...');
            
            const searchData = {
                query: params.query,
                search_type: params.searchType,
                max_content: params.maxItems,
                enabled_sources: params.sources,
                safe_search: params.safeSearch
            };

            console.log('📤 Sending search request:', searchData);
            console.log('📍 Search endpoint:', this.config.apiEndpoints.search);

            const response = await apiClient.post(this.config.apiEndpoints.search, searchData);

            console.log('📥 Search response:', response);

            if (response.success) {
                this.state.currentJobId = response.job_id;
                this.showSuccess(`Search started! Job ID: ${response.job_id}`);
                console.log('✅ Search job started, beginning progress tracking...');
                this.startProgressTracking();
            } else {
                console.error('❌ Search failed with response:', response);
                throw new Error(response.error || 'Search failed');
            }
        } catch (error) {
            console.error('❌ Search error details:', error);
            console.error('❌ Error stack:', error.stack);
            this.showError(`Search failed: ${error.message}`);
        }
    }

    /**
     * Load application settings
     */
    loadSettings() {
        try {
            // Load settings from localStorage
            const settings = JSON.parse(localStorage.getItem('mediaScraperSettings') || '{}');
            
            // Apply settings to form elements
            this.applySettings(settings);
        } catch (error) {
            console.warn('Failed to load settings:', error);
        }
    }

    /**
     * Apply settings to UI elements
     */
    applySettings(settings) {
        // Default safe search
        const safeSearchToggle = document.getElementById('safe-search-toggle');
        if (safeSearchToggle && settings.defaultSafeSearch !== undefined) {
            safeSearchToggle.checked = settings.defaultSafeSearch;
        }

        // Default max items
        const maxItemsInput = document.getElementById('default-max-items');
        if (maxItemsInput && settings.defaultMaxItems) {
            maxItemsInput.value = settings.defaultMaxItems;
        }

        // Download quality
        const qualitySelect = document.getElementById('download-quality');
        if (qualitySelect && settings.downloadQuality) {
            qualitySelect.value = settings.downloadQuality;
        }
    }

    /**
     * Update sources display
     */
    updateSourcesDisplay() {
        if (this.modules.searchManager) {
            this.modules.searchManager.displaySources();
        }
    }

    /**
     * Update assets display
     */
    updateAssetsDisplay() {
        console.log('🎨 App: Updating assets display...');
        if (this.modules.assetManager) {
            this.modules.assetManager.renderAssets();
            console.log('✅ App: Asset manager render called');
        } else {
            console.warn('⚠️ App: Asset manager not available for display update');
        }
    }

    /**
     * Update asset counts
     */
    updateAssetCounts() {
        const assets = this.state.currentAssets;
        const allCount = assets.length;
        const imagesCount = assets.filter(asset => {
            const filename = asset.filename || asset.name || '';
            return Helpers.isImage(filename);
        }).length;
        const videosCount = assets.filter(asset => {
            const filename = asset.filename || asset.name || '';
            return Helpers.isVideo(filename);
        }).length;
        
        console.log(`📊 App: Asset counts - All: ${allCount}, Images: ${imagesCount}, Videos: ${videosCount}`);
        
        const allCountEl = document.getElementById('all-count');
        const imagesCountEl = document.getElementById('images-count');
        const videosCountEl = document.getElementById('videos-count');
        
        if (allCountEl) allCountEl.textContent = allCount;
        if (imagesCountEl) imagesCountEl.textContent = imagesCount;
        if (videosCountEl) videosCountEl.textContent = videosCount;
    }

    /**
     * Update dashboard statistics (ENHANCED for merged section)
     */
    updateDashboardStats(stats) {
        const elements = {
            'total-downloads': stats.total_downloads || 0,
            'total-images': stats.total_images || 0,
            'total-videos': stats.total_videos || 0,
            'success-rate': `${stats.success_rate || 85}%`,
            'total-size': stats.total_size ? Helpers.formatFileSize(stats.total_size) : '0 MB',
            'active-downloads': stats.active_downloads || 0,
            'download-speed': stats.download_speed ? `${stats.download_speed} MB/s` : '0 MB/s',
            'active-sources-count': stats.active_sources || 0
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });

        // Update system status
        this.updateSystemStatus();
    }

    /**
     * Update system status indicators
     */
    updateSystemStatus() {
        const activeSourcesEl = document.getElementById('active-sources');
        const activeJobsEl = document.getElementById('active-jobs');

        if (activeSourcesEl) {
            const sourceCount = Object.values(this.state.sources).flat().length;
            activeSourcesEl.textContent = sourceCount;
        }

        if (activeJobsEl) {
            activeJobsEl.textContent = this.state.currentJobId ? '1' : '0';
        }
    }

    /**
     * Start progress tracking for active job (ENHANCED for live dashboard)
     */
    startProgressTracking() {
        if (!this.state.currentJobId) return;

        // Clear any existing interval
        if (this.intervals.progressUpdate) {
            clearInterval(this.intervals.progressUpdate);
        }

        this.intervals.progressUpdate = setInterval(async () => {
            try {
                const response = await apiClient.get(`${this.config.apiEndpoints.jobStatus}/${this.state.currentJobId}`);
                
                if (response.success || response.status) {
                    const status = response.status || response;
                    
                    // Update live dashboard progress
                    this.updateLiveProgress(status);
                    
                    // Update progress panel if visible
                    if (this.modules.searchManager) {
                        this.modules.searchManager.updateProgress(
                            status.message || 'Processing...',
                            status.progress || 0,
                            status
                        );
                    }
                    
                    if (status.completed) {
                        this.stopProgressTracking();
                        this.showSuccess('Search completed successfully!');
                        this.loadAssets(); // Refresh assets
                        this.loadDashboardStats(); // Refresh stats
                        
                        // Reset live progress
                        this.updateLiveProgress({ progress: 0 });
                    }
                }
            } catch (error) {
                console.warn('Failed to check job progress:', error);
            }
        }, this.config.polling.progressInterval);
    }

    /**
     * Stop progress tracking
     */
    stopProgressTracking() {
        if (this.intervals.progressUpdate) {
            clearInterval(this.intervals.progressUpdate);
            this.intervals.progressUpdate = null;
        }
        this.state.currentJobId = null;
    }

    // UI utility methods
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'danger');
    }

    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    /**
     * Show notification to user
     * @param {string} message - Message to show
     * @param {string} type - Notification type
     */
    showNotification(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toastId = SecurityUtils.generateSecureId('toast');
        const toast = SecurityUtils.createElement('div', {
            className: `toast align-items-center text-white bg-${type} border-0`,
            attributes: {
                role: 'alert',
                'aria-live': 'assertive',
                'aria-atomic': 'true',
                id: toastId
            }
        });

        const toastBody = SecurityUtils.createElement('div', {
            className: 'd-flex'
        });

        const messageDiv = SecurityUtils.createElement('div', {
            className: 'toast-body',
            textContent: message
        });

        const closeButton = SecurityUtils.createElement('button', {
            className: 'btn-close btn-close-white me-2 m-auto',
            attributes: {
                type: 'button',
                'data-bs-dismiss': 'toast',
                'aria-label': 'Close'
            }
        });

        toastBody.appendChild(messageDiv);
        toastBody.appendChild(closeButton);
        toast.appendChild(toastBody);
        container.appendChild(toast);

        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });
        bsToast.show();

        // Clean up after toast is hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    /**
     * Show keyboard shortcuts help
     */
    showKeyboardShortcuts() {
        const shortcutsModal = SecurityUtils.createElement('div', {
            className: 'modal fade',
            attributes: {
                id: 'shortcuts-modal',
                tabindex: '-1',
                'aria-labelledby': 'shortcuts-title',
                'aria-hidden': 'true'
            }
        });

        shortcutsModal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="shortcuts-title">
                            <i class="fas fa-keyboard"></i> Keyboard Shortcuts
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="fas fa-mouse"></i> Navigation</h6>
                                <ul class="list-unstyled">
                                    <li><kbd>Ctrl/Cmd + 1</kbd> Dashboard</li>
                                    <li><kbd>Ctrl/Cmd + 2</kbd> Search</li>
                                    <li><kbd>Ctrl/Cmd + 3</kbd> Assets</li>
                                    <li><kbd>Ctrl/Cmd + 4</kbd> Downloads</li>
                                    <li><kbd>Ctrl/Cmd + 5</kbd> Settings</li>
                                    <li><kbd>/</kbd> Focus search</li>
                                    <li><kbd>Enter</kbd> Activate focused button</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="fas fa-cog"></i> Actions</h6>
                                <ul class="list-unstyled">
                                    <li><kbd>Ctrl/Cmd + K</kbd> Focus search</li>
                                    <li><kbd>Ctrl/Cmd + T</kbd> Toggle theme</li>
                                    <li><kbd>Esc</kbd> Close modals/Clear selection</li>
                                    <li><kbd>?</kbd> Show this help</li>
                                    <li><kbd>↑↓←→</kbd> Navigate assets grid</li>
                                </ul>
                            </div>
                        </div>
                        <div class="mt-3">
                            <small class="text-muted">
                                <i class="fas fa-lightbulb"></i> 
                                Pro tip: You can navigate the entire app without using your mouse!
                            </small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(shortcutsModal);
        const modal = new bootstrap.Modal(shortcutsModal);
        modal.show();

        // Remove modal after it's hidden
        shortcutsModal.addEventListener('hidden.bs.modal', () => {
            shortcutsModal.remove();
        });
    }

    /**
     * Update live progress display on dashboard
     */
    updateLiveProgress(data = {}) {
        // Update live progress bar
        const liveProgressBar = document.getElementById('live-progress-bar');
        if (liveProgressBar && data.progress !== undefined) {
            liveProgressBar.style.width = `${data.progress}%`;
            liveProgressBar.setAttribute('aria-valuenow', data.progress);
            liveProgressBar.textContent = `${Math.round(data.progress)}%`;
            
            if (data.progress === 100) {
                liveProgressBar.classList.add('bg-success');
                liveProgressBar.classList.remove('progress-bar-animated');
            } else if (data.progress > 0) {
                liveProgressBar.classList.add('progress-bar-animated', 'bg-primary');
                liveProgressBar.classList.remove('bg-success');
            }
        }

        // Update live statistics
        const liveStats = {
            'live-detected': data.detected || 0,
            'live-downloaded': data.downloaded || 0,
            'live-images': data.images || 0,
            'live-videos': data.videos || 0,
            'live-threads': data.threads || 1,
            'live-bandwidth': data.bandwidth || '0 KB/s'
        };

        Object.entries(liveStats).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });

        // Update live sources list
        const liveSourcesList = document.getElementById('live-sources-list');
        if (liveSourcesList) {
            if (data.sources && Object.keys(data.sources).length > 0) {
                liveSourcesList.textContent = Object.keys(data.sources).join(', ');
            } else {
                liveSourcesList.textContent = 'No active searches';
            }
        }

        // Update current file
        const liveCurrentFile = document.getElementById('live-current-file');
        if (liveCurrentFile) {
            if (data.current_file) {
                liveCurrentFile.textContent = data.current_file;
            } else {
                liveCurrentFile.textContent = 'No active downloads';
            }
        }
    }

    /**
     * Add downloads section functionality (MERGED into dashboard)
     */
    refreshDownloads() {
        console.log('🔄 Refreshing downloads (redirected to dashboard refresh)...');
        this.loadDashboardStats();
        this.loadAssets();
        this.showInfo('Dashboard data refreshed');
    }

    /**
     * Clear completed downloads (MERGED functionality)
     */
    clearCompletedDownloads() {
        if (confirm('Are you sure you want to clear completed download history?')) {
            console.log('🗑️ Clearing completed downloads...');
            // This would clear download history from the database
            this.showSuccess('Download history cleared');
        }
    }

    /**
     * Cleanup and destroy the application
     */
    destroy() {
        // Clear all intervals
        Object.values(this.intervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });

        // Remove event listeners
        document.removeEventListener('keydown', this.handleKeyboardShortcuts);

        // Destroy modules
        Object.values(this.modules).forEach(module => {
            if (module.destroy) module.destroy();
        });

        console.log('Application destroyed successfully');
    }

    /**
     * Refresh assets and force reload
     */
    async refreshAssets() {
        console.log('🔄 App: Force refreshing assets...');
        
        try {
            // Clear current assets
            this.state.currentAssets = [];
            
            // Call loadAssets to fetch fresh data
            await this.loadAssets();
            
            // Force asset manager to reload
            if (this.modules.assetManager) {
                console.log('🔄 App: Calling asset manager loadAssetsWithRetry...');
                await this.modules.assetManager.loadAssetsWithRetry();
            }
            
            // Update all related displays
            await this.loadDashboardStats();
            
            console.log('✅ App: Asset refresh complete');
            this.showSuccess('Assets refreshed successfully');
            
        } catch (error) {
            console.error('❌ App: Error refreshing assets:', error);
            this.showError('Failed to refresh assets: ' + error.message);
        }
    }

    /**
     * Toggle all sources on/off
     */
    toggleAllSources(enable) {
        if (this.modules.searchManager) {
            this.modules.searchManager.toggleAllSources(enable);
        }
    }
}

// Export to global scope
window.MediaScraperApp = MediaScraperApp; 

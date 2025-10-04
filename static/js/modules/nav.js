/**
 * Navigation Module
 * Handles sidebar navigation, section switching, and mobile menu
 */
class NavigationManager {
    constructor() {
        this.currentSection = null;  // Don't pre-set - let loadInitialSection determine it
        this.initializedSections = new Set();  // Track which sections have been initialized
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialSection();
        this.setupMobileMenu();
    }

    setupEventListeners() {
        // Handle navigation clicks
        const navItems = document.querySelectorAll('[data-section]');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.showSection(section);
                this.setActiveNavItem(item);
                
                // Update URL hash
                const hash = item.getAttribute('href');
                if (hash && hash.startsWith('#')) {
                    history.pushState(null, '', hash);
                }
                
                // Close mobile menu if open
                this.closeMobileMenu();
            });
        });

        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            this.loadSectionFromHash();
        });
    }

    setupMobileMenu() {
        const toggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        
        if (toggle) {
            toggle.addEventListener('click', () => {
                sidebar.classList.toggle('show');
                overlay.classList.toggle('show');
                toggle.setAttribute('aria-expanded', sidebar.classList.contains('show'));
            });
        }
        
        if (overlay) {
            overlay.addEventListener('click', () => {
                this.closeMobileMenu();
            });
        }
    }

    closeMobileMenu() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        const toggle = document.getElementById('sidebar-toggle');
        
        if (sidebar) sidebar.classList.remove('show');
        if (overlay) overlay.classList.remove('show');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }

    loadInitialSection() {
        // Check URL hash first - ALWAYS prioritize hash over localStorage
        const hash = window.location.hash;
        if (hash && hash.length > 1) {
            // Hash exists, use it
            this.loadSectionFromHash();
        } else {
            // No hash, check localStorage
            const lastSection = localStorage.getItem('lastSection') || 'dashboard-section';
            this.showSection(lastSection);

            // Set active nav item
            const navItem = document.querySelector(`[data-section="${lastSection}"]`);
            if (navItem) {
                this.setActiveNavItem(navItem);
            }
        }
    }

    loadSectionFromHash() {
        const hash = window.location.hash.slice(1); // Remove #
        const sectionMap = {
            'dashboard': 'dashboard-section',
            'search': 'search-section',
            'assets': 'assets-section',
            'settings': 'settings-section',
            'upload': 'upload-section'
        };

        const section = sectionMap[hash] || 'dashboard-section';  // Default to dashboard
        this.showSection(section);

        // Update active nav item
        const navItem = document.querySelector(`[data-section="${section}"]`);
        if (navItem) {
            this.setActiveNavItem(navItem);
        }
    }

    showSection(sectionId) {
        // Don't re-show the section if it's already active (unless it's the initial load)
        if (this.currentSection === sectionId && this.currentSection !== null) {
            return;
        }

        // Hide all sections
        const sections = document.querySelectorAll('.content-section');
        sections.forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
            this.currentSection = sectionId;

            // Save to localStorage
            localStorage.setItem('lastSection', sectionId);

            // Trigger section-specific initialization (only once per section)
            this.initializeSection(sectionId);
        }
    }

    setActiveNavItem(item) {
        // Remove active class from all nav items (only <a> elements in sidebar, not sections)
        const navItems = document.querySelectorAll('.sidebar .nav-item[data-section]');
        navItems.forEach(navItem => {
            navItem.classList.remove('active');
        });

        // Add active class to selected item
        item.classList.add('active');
    }

    initializeSection(sectionId) {
        // Dashboard needs special handling - always call init to ensure visibility
        if (sectionId === 'dashboard-section') {
            if (window.downloadDashboard) {
                window.downloadDashboard.init();
            }
            return;
        }

        // Only initialize once per section (for non-dashboard sections)
        if (this.initializedSections.has(sectionId)) {
            return;
        }

        this.initializedSections.add(sectionId);

        // Trigger section-specific initialization
        switch(sectionId) {
            case 'dashboard-section':
                // This case is now handled above
                break;
            
            case 'search-section':
                // Initialize search UI
                if (window.searchUI && !window.searchUI.initialized) {
                    window.searchUI.init();
                    window.searchUI.initialized = true;
                }
                break;
            
            case 'assets-section':
                // Refresh asset library
                if (window.assetLibrary) {
                    window.assetLibrary.loadAssets();
                }
                break;
            
            case 'settings-section':
                // Initialize settings if needed
                break;
        }
    }
}

// Initialize navigation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.navManager = new NavigationManager();
});
/**
 * Navigation Module
 * Handles sidebar navigation, section switching, and mobile menu
 */
class NavigationManager {
    constructor() {
        this.currentSection = 'dashboard-section';
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
        // Check URL hash first
        const hash = window.location.hash;
        if (hash) {
            this.loadSectionFromHash();
        } else {
            // Load last visited section from localStorage or default
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
            'settings': 'settings-section'
        };
        
        const section = sectionMap[hash] || 'dashboard-section';
        this.showSection(section);
        
        // Update active nav item
        const navItem = document.querySelector(`[data-section="${section}"]`);
        if (navItem) {
            this.setActiveNavItem(navItem);
        }
    }

    showSection(sectionId) {
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
            
            // Trigger section-specific initialization
            this.initializeSection(sectionId);
        }
    }

    setActiveNavItem(item) {
        // Remove active class from all nav items
        const navItems = document.querySelectorAll('[data-section]');
        navItems.forEach(navItem => {
            navItem.classList.remove('active');
        });
        
        // Add active class to selected item
        item.classList.add('active');
    }

    initializeSection(sectionId) {
        // Trigger section-specific initialization
        switch(sectionId) {
            case 'dashboard-section':
                // Initialize dashboard if needed
                if (window.initializeDashboard) {
                    window.initializeDashboard();
                }
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
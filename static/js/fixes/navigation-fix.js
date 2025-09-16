/**
 * Navigation Fix
 * Fixes all navigation links including Asset Library and other menu items
 */

(function() {
    'use strict';
    
    console.log('🧭 Navigation Fix initializing...');
    
    // Store original navigation handler if it exists
    const originalShowSection = window.showSection;
    
    // Create navigation handler
    function handleNavigation(section) {
        console.log(`📍 Navigating to: ${section}`);
        
        // Try multiple methods to handle navigation
        
        // Method 1: Use app's navigation if available
        if (window.app && window.app.showSection) {
            console.log('Using app.showSection');
            window.app.showSection(section);
            return;
        }
        
        // Method 2: Use original showSection if it existed
        if (originalShowSection && typeof originalShowSection === 'function') {
            console.log('Using original showSection');
            originalShowSection(section);
            return;
        }
        
        // Method 3: Manual section display
        console.log('Using manual section display');
        
        // Hide all sections
        const sections = [
            'dashboard-section',
            'search-section', 
            'assets-section',
            'settings-section',
            'admin-section',
            'subscription-section'
        ];
        
        sections.forEach(sectionId => {
            const el = document.getElementById(sectionId);
            if (el) {
                el.style.display = 'none';
                el.classList.remove('active');
            }
        });
        
        // Show the requested section
        const targetSection = document.getElementById(`${section}-section`) || 
                            document.getElementById(section);
        
        if (targetSection) {
            targetSection.style.display = 'block';
            targetSection.classList.add('active');
            
            // Trigger any initialization for the section
            switch(section) {
                case 'assets':
                case 'asset-library':
                    // Load assets when showing asset library
                    if (window.fixAssetLibrary) {
                        window.fixAssetLibrary();
                    } else if (window.loadGallery) {
                        window.loadGallery();
                    }
                    // Also try to load through asset manager
                    if (window.app && window.app.modules && window.app.modules.assetManager) {
                        window.app.modules.assetManager.loadAssets();
                    }
                    break;
                    
                case 'search':
                    // Initialize search if needed
                    if (window.app && window.app.modules && window.app.modules.searchManager) {
                        window.app.modules.searchManager.loadSources();
                    }
                    break;
                    
                case 'dashboard':
                    // Update dashboard stats
                    if (window.updateDashboardStats) {
                        window.updateDashboardStats();
                    }
                    break;
            }
        } else {
            console.warn(`Section not found: ${section}`);
        }
        
        // Update active nav item
        updateActiveNavItem(section);
    }
    
    // Update active state in navigation
    function updateActiveNavItem(section) {
        // Remove active from all nav items
        document.querySelectorAll('.nav-link, .sidebar-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active to current
        const activeLinks = document.querySelectorAll(`
            [data-section="${section}"],
            [onclick*="showSection('${section}')"],
            [href="#${section}"],
            [data-target="${section}"]
        `);
        
        activeLinks.forEach(link => {
            link.classList.add('active');
        });
    }
    
    // Fix all navigation links
    function fixNavigationLinks() {
        console.log('🔧 Fixing navigation links...');
        
        // Fix sidebar links
        const navLinks = document.querySelectorAll(`
            .nav-link[onclick*="showSection"],
            .sidebar-link[onclick*="showSection"],
            a[onclick*="showSection"],
            [data-section]
        `);
        
        navLinks.forEach(link => {
            // Get the section from various attributes
            let section = link.dataset.section;
            
            if (!section) {
                // Try to extract from onclick
                const onclickAttr = link.getAttribute('onclick');
                if (onclickAttr) {
                    const match = onclickAttr.match(/showSection\(['"]([^'"]+)['"]\)/);
                    if (match) {
                        section = match[1];
                    }
                }
            }
            
            if (!section) {
                // Try to extract from href
                const href = link.getAttribute('href');
                if (href && href.startsWith('#')) {
                    section = href.substring(1);
                }
            }
            
            if (section) {
                console.log(`📎 Fixing link for section: ${section}`);
                
                // Remove old onclick
                link.removeAttribute('onclick');
                
                // Add new click handler
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    handleNavigation(section);
                });
                
                // Make it look clickable
                link.style.cursor = 'pointer';
            }
        });
        
        // Fix specific navigation items by text content
        const navigationMap = {
            'Dashboard': 'dashboard',
            'Search & Download': 'search',
            'Asset Library': 'assets',
            'Settings': 'settings',
            'Admin Panel': 'admin',
            'Subscription': 'subscription'
        };
        
        Object.entries(navigationMap).forEach(([text, section]) => {
            const links = Array.from(document.querySelectorAll('a, .nav-link, .sidebar-link')).filter(
                link => link.textContent.trim().includes(text)
            );
            
            links.forEach(link => {
                if (!link.dataset.fixed) {
                    console.log(`📎 Fixing link by text: ${text} -> ${section}`);
                    link.dataset.fixed = 'true';
                    link.dataset.section = section;
                    
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        handleNavigation(section);
                    });
                    
                    link.style.cursor = 'pointer';
                }
            });
        });
    }
    
    // Override global showSection function
    window.showSection = handleNavigation;
    
    // Also create aliases for compatibility
    window.navigateTo = handleNavigation;
    window.showPage = handleNavigation;
    
    // Fix Asset Library specific link
    function fixAssetLibraryLink() {
        // Get links that might contain assets or gallery references
        const assetLinks = document.querySelectorAll(`
            [onclick*="assets"],
            [onclick*="gallery"]
        `);
        
        // Also check text content separately
        const allLinks = document.querySelectorAll('a, .nav-link, .sidebar-link');
        Array.from(allLinks).forEach(link => {
            if (link.textContent.includes('Asset Library') || 
                link.textContent.includes('Gallery') ||
                link.textContent.includes('Media Library')) {
                
                console.log('🖼️ Fixing Asset Library link');
                
                link.onclick = null;
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Show assets section
                    handleNavigation('assets');
                    
                    // Load assets
                    setTimeout(() => {
                        if (window.fixAssetLibrary) {
                            window.fixAssetLibrary();
                        }
                        if (window.loadGallery) {
                            window.loadGallery();
                        }
                    }, 100);
                });
            }
        });
    }
    
    // Initialize navigation fixes
    function initialize() {
        console.log('🚀 Initializing navigation fixes...');
        
        fixNavigationLinks();
        fixAssetLibraryLink();
        
        // Set up MutationObserver to fix dynamically added links
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    setTimeout(fixNavigationLinks, 100);
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('✅ Navigation fixes applied');
    }
    
    // Start initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Also fix after a delay to catch late-loading elements
    setTimeout(initialize, 1000);
    setTimeout(fixAssetLibraryLink, 1500);
    
    // Make functions globally available
    window.fixNavigationLinks = fixNavigationLinks;
    window.handleNavigation = handleNavigation;
    
    console.log('✅ Navigation Fix loaded');
})();
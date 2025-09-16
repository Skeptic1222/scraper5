/**
 * SIDEBAR SCROLL RESET
 * Ensures sidebar starts at top and all navigation items are visible
 */

(function() {
    'use strict';
    
    // Function to reset sidebar scroll position
    function resetSidebarScroll() {
        // Find all sidebar elements
        const sidebarSelectors = [
            '.sidebar',
            '#sidebar',
            'aside.sidebar',
            '[class*="sidebar"]',
            '.nav-sidebar',
            '.sidebar-nav'
        ];
        
        sidebarSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(sidebar => {
                if (sidebar) {
                    // Reset scroll position to top
                    sidebar.scrollTop = 0;
                    
                    // Ensure sidebar is visible
                    sidebar.style.display = 'block';
                    sidebar.style.visibility = 'visible';
                    sidebar.style.opacity = '1';
                    
                    // Remove any transforms that might push content off screen
                    sidebar.style.transform = 'none';
                    
                    // Log for debugging
                    console.log('✅ Sidebar scroll reset:', selector);
                }
            });
        });
        
        // Also reset any nav lists that might have their own scroll
        const navLists = document.querySelectorAll('.nav-list, .sidebar-nav');
        navLists.forEach(nav => {
            if (nav && nav.scrollTop !== undefined) {
                nav.scrollTop = 0;
            }
        });
    }
    
    // Function to ensure navigation items are visible
    function ensureNavItemsVisible() {
        const navItems = document.querySelectorAll('.nav-item, .nav-link');
        navItems.forEach((item, index) => {
            // Remove any negative margins or transforms
            item.style.marginTop = '0';
            item.style.transform = 'translateY(0)';
            
            // Ensure visibility
            item.style.visibility = 'visible';
            item.style.opacity = '1';
            
            // Log first few items for debugging
            if (index < 3) {
                console.log(`✅ Nav item ${index + 1} visible:`, item.textContent?.trim());
            }
        });
    }
    
    // Function to fix sidebar height
    function fixSidebarHeight() {
        const sidebars = document.querySelectorAll('.sidebar, #sidebar');
        sidebars.forEach(sidebar => {
            // Get navbar height
            const navbar = document.querySelector('.navbar, nav');
            const navbarHeight = navbar ? navbar.offsetHeight : 60;
            
            // Set proper height
            sidebar.style.maxHeight = `calc(100vh - ${navbarHeight}px)`;
            sidebar.style.overflowY = 'auto';
            sidebar.style.overflowX = 'hidden';
        });
    }
    
    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            resetSidebarScroll();
            ensureNavItemsVisible();
            fixSidebarHeight();
        });
    } else {
        // DOM already loaded
        resetSidebarScroll();
        ensureNavItemsVisible();
        fixSidebarHeight();
    }
    
    // Run after a short delay to catch any dynamic content
    setTimeout(function() {
        resetSidebarScroll();
        ensureNavItemsVisible();
        fixSidebarHeight();
    }, 100);
    
    // Also reset on window load (after all resources loaded)
    window.addEventListener('load', function() {
        resetSidebarScroll();
        ensureNavItemsVisible();
        fixSidebarHeight();
    });
    
    // Monitor for dynamic changes
    const observer = new MutationObserver(function(mutations) {
        // Check if sidebar was added or modified
        const sidebarModified = mutations.some(mutation => {
            return Array.from(mutation.addedNodes).some(node => 
                node.nodeType === 1 && (
                    node.classList?.contains('sidebar') ||
                    node.id === 'sidebar' ||
                    node.querySelector?.('.sidebar')
                )
            );
        });
        
        if (sidebarModified) {
            setTimeout(function() {
                resetSidebarScroll();
                ensureNavItemsVisible();
                fixSidebarHeight();
            }, 50);
        }
    });
    
    // Start observing
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Expose functions globally for debugging
    window.resetSidebarScroll = resetSidebarScroll;
    window.ensureNavItemsVisible = ensureNavItemsVisible;
    window.fixSidebarHeight = fixSidebarHeight;
    
    console.log('🔧 Sidebar scroll reset script loaded');
})();
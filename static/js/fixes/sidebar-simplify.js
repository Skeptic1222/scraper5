/**
 * SIDEBAR SIMPLIFICATION FIX
 * Removes all unnecessary content from sidebar
 * Ensures no scrollbar is needed
 */

(function() {
    'use strict';
    
    function simplifySidebar() {
        const sidebar = document.querySelector('.sidebar, #sidebar');
        if (!sidebar) return;
        
        // Remove system status section
        const systemStatus = sidebar.querySelector('.system-status');
        if (systemStatus) {
            systemStatus.remove();
            console.log('✅ Removed system status section');
        }
        
        // Remove user profile section
        const userProfile = sidebar.querySelector('.user-profile, #user-profile-section');
        if (userProfile) {
            userProfile.remove();
            console.log('✅ Removed user profile section');
        }
        
        // Remove footer
        const footer = sidebar.querySelector('.sidebar-footer, footer');
        if (footer) {
            footer.remove();
            console.log('✅ Removed sidebar footer');
        }
        
        // Remove any other sections that aren't navigation
        const sections = sidebar.querySelectorAll('section');
        sections.forEach(section => {
            if (!section.querySelector('.nav-list')) {
                section.remove();
                console.log('✅ Removed extra section:', section.className);
            }
        });
        
        // Ensure sidebar has no scroll
        sidebar.style.overflow = 'hidden';
        sidebar.style.overflowY = 'hidden';
        sidebar.style.overflowX = 'hidden';
        sidebar.scrollTop = 0;
        
        // Remove any inline height styles
        sidebar.style.height = 'auto';
        sidebar.style.maxHeight = 'calc(100vh - 60px)';
        
        // Compact the header
        const header = sidebar.querySelector('.sidebar-header');
        if (header) {
            header.style.marginBottom = '10px';
            header.style.paddingBottom = '10px';
            
            const logoSection = header.querySelector('.logo-section');
            if (logoSection) {
                logoSection.style.marginBottom = '10px';
            }
        }
        
        // Compact navigation
        const navList = sidebar.querySelector('.nav-list');
        if (navList) {
            navList.style.gap = '5px';
            
            const navItems = navList.querySelectorAll('.nav-item');
            navItems.forEach(item => {
                item.style.padding = '10px 15px';
                item.style.fontSize = '0.95rem';
            });
        }
        
        console.log('✅ Sidebar simplified - no scrollbar needed');
    }
    
    // Run immediately
    simplifySidebar();
    
    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', simplifySidebar);
    }
    
    // Run after a delay to catch dynamic content
    setTimeout(simplifySidebar, 100);
    setTimeout(simplifySidebar, 500);
    
    // Monitor for changes
    const observer = new MutationObserver(function(mutations) {
        const sidebarChanged = mutations.some(mutation => {
            return Array.from(mutation.addedNodes).some(node => {
                if (node.nodeType !== 1) return false;
                return node.classList?.contains('system-status') ||
                       node.classList?.contains('user-profile') ||
                       node.classList?.contains('sidebar-footer') ||
                       node.tagName === 'FOOTER';
            });
        });
        
        if (sidebarChanged) {
            setTimeout(simplifySidebar, 50);
        }
    });
    
    // Start observing
    const sidebar = document.querySelector('.sidebar, #sidebar');
    if (sidebar) {
        observer.observe(sidebar, {
            childList: true,
            subtree: true
        });
    }
    
    // Expose for debugging
    window.simplifySidebar = simplifySidebar;
})();
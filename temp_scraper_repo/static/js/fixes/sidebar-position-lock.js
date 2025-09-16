/**
 * Sidebar Position Lock
 * Ensures sidebar NEVER moves when switching sections
 * This fix addresses the issue where sidebar moves down off screen
 */

(function() {
    'use strict';
    
    console.log('🔒 Sidebar Position Lock initializing...');
    
    // Store the correct sidebar position
    const SIDEBAR_TOP = '60px';
    const SIDEBAR_LEFT = '0px';
    const SIDEBAR_WIDTH = '260px';
    const SIDEBAR_HEIGHT = 'calc(100vh - 60px)';
    
    function lockSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (!sidebar) {
            console.warn('⚠️ Sidebar not found');
            return;
        }
        
        // Force the sidebar to stay in position
        sidebar.style.cssText = `
            position: fixed !important;
            top: ${SIDEBAR_TOP} !important;
            left: ${SIDEBAR_LEFT} !important;
            width: ${SIDEBAR_WIDTH} !important;
            height: ${SIDEBAR_HEIGHT} !important;
            z-index: 9998 !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
            transform: none !important;
            transition: none !important;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
        `;
        
        // Also ensure content area has proper margin
        const contentArea = document.querySelector('.content-area, #main-content');
        if (contentArea) {
            contentArea.style.marginLeft = '260px';
            contentArea.style.paddingTop = '0';
        }
    }
    
    // Lock sidebar immediately
    lockSidebar();
    
    // Re-lock on DOM changes
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.type === 'attributes' && 
                (mutation.target.classList.contains('sidebar') || 
                 mutation.attributeName === 'style')) {
                lockSidebar();
            }
            
            // Check for section changes
            if (mutation.target.classList && 
                mutation.target.classList.contains('content-section')) {
                lockSidebar();
            }
        }
    });
    
    // Start observing when DOM is ready
    function startObserving() {
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('#main-content');
        
        if (sidebar && mainContent) {
            observer.observe(document.body, {
                attributes: true,
                attributeFilter: ['style', 'class'],
                childList: true,
                subtree: true
            });
            console.log('✅ Sidebar position lock active');
        } else {
            setTimeout(startObserving, 100);
        }
    }
    
    // Override any function that might move the sidebar
    if (window.MediaScraperApp) {
        const originalShowSection = window.MediaScraperApp.prototype.showSection;
        window.MediaScraperApp.prototype.showSection = function(sectionName) {
            const result = originalShowSection.call(this, sectionName);
            lockSidebar();
            return result;
        };
    }
    
    // Listen for navigation events
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a[data-section], .nav-link');
        if (link) {
            setTimeout(lockSidebar, 0);
        }
    });
    
    // Lock sidebar after any section transition
    window.addEventListener('transitionend', lockSidebar);
    window.addEventListener('animationend', lockSidebar);
    
    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startObserving);
    } else {
        startObserving();
    }
    
    console.log('🔒 Sidebar Position Lock initialized');
})();
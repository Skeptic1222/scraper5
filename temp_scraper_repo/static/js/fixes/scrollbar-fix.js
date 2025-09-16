/**
 * Scrollbar Fix
 * Eliminates double vertical scrollbars
 */

(function() {
    'use strict';
    
    console.log('📜 Scrollbar Fix initializing...');
    
    function fixScrollbars() {
        // Find all elements that might have unnecessary scrollbars
        const elements = document.querySelectorAll('*');
        
        elements.forEach(element => {
            const computed = window.getComputedStyle(element);
            const hasVerticalScroll = computed.overflowY === 'scroll' || computed.overflowY === 'auto';
            const hasHorizontalScroll = computed.overflowX === 'scroll' || computed.overflowX === 'auto';
            
            // Check if element actually needs scrollbar
            if (hasVerticalScroll) {
                const needsScroll = element.scrollHeight > element.clientHeight;
                if (!needsScroll && !element.classList.contains('sidebar') && 
                    !element.classList.contains('content-area') && 
                    element.id !== 'main-content' &&
                    element.id !== 'source-categories') {
                    // Remove unnecessary scrollbar
                    element.style.overflowY = 'hidden';
                }
            }
            
            // Always hide horizontal scrollbars except for specific elements
            if (hasHorizontalScroll && !element.classList.contains('table-responsive')) {
                element.style.overflowX = 'hidden';
            }
        });
        
        // Ensure proper scrollbar setup for main elements
        const html = document.documentElement;
        const body = document.body;
        const sidebar = document.querySelector('.sidebar');
        const contentArea = document.querySelector('.content-area, #main-content');
        const mainContainer = document.querySelector('.main-container');
        
        // HTML and BODY should not scroll
        html.style.overflow = 'hidden';
        body.style.overflow = 'hidden';
        body.style.height = '100vh';
        body.style.margin = '0';
        body.style.padding = '0';
        
        // Main container should use flexbox
        if (mainContainer) {
            mainContainer.style.cssText = `
                position: fixed !important;
                top: 60px !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                display: flex !important;
                overflow: hidden !important;
            `;
        }
        
        // Sidebar should scroll if needed
        if (sidebar) {
            sidebar.style.cssText = `
                position: relative !important;
                width: 260px !important;
                height: 100% !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                flex-shrink: 0 !important;
            `;
        }
        
        // Content area should scroll
        if (contentArea) {
            contentArea.style.cssText = `
                flex: 1 !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                height: 100% !important;
                padding: 20px !important;
            `;
        }
        
        // Remove any duplicate scrollbars from nested containers
        const nestedContainers = document.querySelectorAll('.container, .container-fluid, .row, .col, .card-body');
        nestedContainers.forEach(container => {
            if (container.style.overflow || container.style.overflowY || container.style.overflowX) {
                container.style.overflow = 'visible';
            }
        });
    }
    
    // Fix scrollbars on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixScrollbars);
    } else {
        fixScrollbars();
    }
    
    // Fix scrollbars after any dynamic content changes
    const observer = new MutationObserver(() => {
        fixScrollbars();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
    });
    
    // Re-fix on window resize
    window.addEventListener('resize', fixScrollbars);
    
    // Re-fix on section changes
    document.addEventListener('click', (e) => {
        if (e.target.closest('a[data-section], .nav-link')) {
            setTimeout(fixScrollbars, 100);
        }
    });
    
    console.log('✅ Scrollbar Fix active');
})();
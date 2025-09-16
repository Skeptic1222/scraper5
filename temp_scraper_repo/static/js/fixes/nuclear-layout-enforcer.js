/**
 * NUCLEAR LAYOUT ENFORCER
 * This script FORCES the layout to stay correct no matter what
 * It runs continuously and fixes any layout issues immediately
 */

(function() {
    'use strict';
    
    console.log('☢️ NUCLEAR LAYOUT ENFORCER ACTIVATED');
    
    // The correct layout that MUST be maintained
    const LAYOUT_RULES = {
        navbar: {
            position: 'absolute',
            top: '0px',
            left: '0px',
            right: '0px',
            height: '60px',
            zIndex: '999999',
            width: '100vw'
        },
        mainContainer: {
            position: 'absolute',
            top: '60px',
            left: '0px',
            right: '0px',
            bottom: '0px',
            display: 'grid',
            gridTemplateColumns: '260px 1fr',
            overflow: 'hidden',
            width: '100vw',
            height: 'calc(100vh - 60px)'
        },
        sidebar: {
            gridColumn: '1',
            width: '260px',
            height: '100%',
            position: 'relative',
            overflowY: 'auto',
            overflowX: 'hidden',
            padding: '20px'
        },
        contentArea: {
            gridColumn: '2',
            width: '100%',
            height: '100%',
            position: 'relative',
            overflowY: 'auto',
            overflowX: 'hidden',
            padding: '20px'
        }
    };
    
    function enforceLayout() {
        // Fix HTML and BODY
        document.documentElement.style.cssText = 'width: 100vw; height: 100vh; overflow: hidden; position: fixed; top: 0; left: 0;';
        document.body.style.cssText = 'width: 100vw; height: 100vh; overflow: hidden; position: fixed; top: 0; left: 0; margin: 0; padding: 0;';
        
        // Fix Navbar
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            Object.assign(navbar.style, LAYOUT_RULES.navbar);
        }
        
        // Fix Main Container
        const mainContainer = document.querySelector('.main-container');
        if (mainContainer) {
            Object.assign(mainContainer.style, LAYOUT_RULES.mainContainer);
        }
        
        // Fix Sidebar
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            Object.assign(sidebar.style, LAYOUT_RULES.sidebar);
            // Ensure sidebar NEVER moves
            sidebar.style.transform = 'none';
            sidebar.style.left = 'auto';
            sidebar.style.top = 'auto';
            sidebar.style.position = 'relative';
        }
        
        // Fix Content Area
        const contentArea = document.querySelector('.content-area, #main-content');
        if (contentArea) {
            Object.assign(contentArea.style, LAYOUT_RULES.contentArea);
        }
        
        // Remove scrollbars from everything else
        const unnecessaryScrollElements = document.querySelectorAll(
            '.container, .container-fluid, .row, .col, .card, .card-body, .modal-body'
        );
        unnecessaryScrollElements.forEach(el => {
            el.style.overflow = 'visible';
            el.style.maxHeight = 'none';
            el.style.height = 'auto';
        });
        
        // Count and remove duplicate scrollbars
        const allElements = document.querySelectorAll('*');
        let scrollbarCount = 0;
        
        allElements.forEach(el => {
            const computed = getComputedStyle(el);
            const hasVerticalScroll = computed.overflowY === 'scroll' || computed.overflowY === 'auto';
            
            if (hasVerticalScroll) {
                // Only allow scrollbars on sidebar and content area
                if (!el.classList.contains('sidebar') && 
                    !el.classList.contains('content-area') && 
                    el.id !== 'main-content' &&
                    el.id !== 'source-categories') {
                    
                    const needsScroll = el.scrollHeight > el.clientHeight;
                    if (!needsScroll) {
                        el.style.overflowY = 'hidden';
                    }
                }
                scrollbarCount++;
            }
        });
        
        // Log if we have more than 2 scrollbars (sidebar + content)
        if (scrollbarCount > 2) {
            console.warn(`⚠️ Found ${scrollbarCount} scrollbars, should only have 2`);
        }
    }
    
    // Run enforcer immediately
    enforceLayout();
    
    // Run enforcer on every possible event
    const events = [
        'DOMContentLoaded', 'load', 'resize', 'scroll',
        'click', 'mousedown', 'mouseup', 'touchstart',
        'touchend', 'transitionend', 'animationend'
    ];
    
    events.forEach(event => {
        window.addEventListener(event, enforceLayout, true);
        document.addEventListener(event, enforceLayout, true);
    });
    
    // Continuously monitor and fix
    let enforceInterval = setInterval(enforceLayout, 100);
    
    // After 5 seconds, reduce frequency to save performance
    setTimeout(() => {
        clearInterval(enforceInterval);
        enforceInterval = setInterval(enforceLayout, 1000);
    }, 5000);
    
    // Monitor DOM mutations
    const observer = new MutationObserver((mutations) => {
        enforceLayout();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
    });
    
    // Override any attempts to change sidebar position
    const originalSetAttribute = Element.prototype.setAttribute;
    Element.prototype.setAttribute = function(name, value) {
        if (this.classList && this.classList.contains('sidebar')) {
            if (name === 'style' && value.includes('transform')) {
                console.warn('🛑 Blocked attempt to transform sidebar');
                return;
            }
        }
        return originalSetAttribute.call(this, name, value);
    };
    
    // Expose debug function
    window.debugLayout = function() {
        console.log('📊 Layout Debug:');
        const sidebar = document.querySelector('.sidebar');
        const content = document.querySelector('.content-area, #main-content');
        
        if (sidebar) {
            console.log('Sidebar:', {
                position: sidebar.style.position,
                transform: sidebar.style.transform,
                left: sidebar.style.left,
                top: sidebar.style.top,
                width: sidebar.style.width
            });
        }
        
        if (content) {
            console.log('Content:', {
                overflow: content.style.overflow,
                height: content.style.height,
                scrollHeight: content.scrollHeight
            });
        }
        
        // Count scrollbars
        let count = 0;
        document.querySelectorAll('*').forEach(el => {
            const computed = getComputedStyle(el);
            if (computed.overflowY === 'scroll' || computed.overflowY === 'auto') {
                if (el.scrollHeight > el.clientHeight) {
                    count++;
                    console.log('Scrollbar on:', el);
                }
            }
        });
        console.log(`Total active scrollbars: ${count}`);
    };
    
    console.log('✅ NUCLEAR LAYOUT ENFORCER READY');
    console.log('💡 Use window.debugLayout() to debug layout issues');
})();
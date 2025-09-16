// Emergency UI Fix - Prevents UI from disappearing due to JavaScript errors
(function() {
    'use strict';
    
    console.log('🚨 Emergency UI Fix Loading...');
    
    // Override any attempts to hide the main UI
    const originalDisplay = Element.prototype.style;
    Object.defineProperty(Element.prototype, 'style', {
        get: function() {
            return new Proxy(originalDisplay, {
                set: function(target, property, value) {
                    // Prevent hiding critical UI elements
                    const criticalElements = [
                        'dashboard-section',
                        'search-section', 
                        'assets-section',
                        'main-content',
                        'source-categories',
                        'assets-grid'
                    ];
                    
                    const elementId = this.id || '';
                    const elementClass = this.className || '';
                    
                    // Check if this is a critical element
                    const isCritical = criticalElements.some(id => 
                        elementId.includes(id) || elementClass.includes(id)
                    );
                    
                    // Prevent hiding critical elements
                    if (isCritical && property === 'display' && value === 'none') {
                        console.log('🛡️ Blocked attempt to hide:', elementId || elementClass);
                        return true; // Block the change
                    }
                    
                    if (isCritical && property === 'visibility' && value === 'hidden') {
                        console.log('🛡️ Blocked attempt to hide:', elementId || elementClass);
                        return true; // Block the change
                    }
                    
                    if (isCritical && property === 'opacity' && value === '0') {
                        console.log('🛡️ Blocked attempt to hide:', elementId || elementClass);
                        return true; // Block the change
                    }
                    
                    // Allow other changes
                    target[property] = value;
                    return true;
                }
            });
        }
    });
    
    // Ensure all sections remain visible
    function ensureVisibility() {
        const sections = [
            '#dashboard-section',
            '#search-section',
            '#assets-section',
            '#main-content',
            '.content-section',
            '#source-categories',
            '#assets-grid'
        ];
        
        sections.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (el) {
                    el.style.display = 'block';
                    el.style.visibility = 'visible';
                    el.style.opacity = '1';
                }
            });
        });
    }
    
    // Run immediately
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ensureVisibility);
    } else {
        ensureVisibility();
    }
    
    // Also run periodically to counteract any delayed hiding
    setInterval(ensureVisibility, 1000);
    
    // Prevent errors from cascading and hiding the UI
    const originalError = window.onerror;
    window.onerror = function(msg, url, lineNo, columnNo, error) {
        console.error('🚨 Error caught, preventing UI hide:', msg);
        ensureVisibility(); // Ensure UI stays visible even on error
        
        // Call original error handler if it exists
        if (originalError) {
            return originalError.apply(this, arguments);
        }
        return true; // Prevent default error handling
    };
    
    // Prevent unhandled promise rejections from hiding UI
    window.addEventListener('unhandledrejection', function(event) {
        console.error('🚨 Unhandled promise rejection, preventing UI hide:', event.reason);
        ensureVisibility();
    });
    
    console.log('✅ Emergency UI Fix Active - UI will remain visible');
    
})();
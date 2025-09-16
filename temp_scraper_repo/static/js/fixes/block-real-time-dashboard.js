/**
 * Block Real-Time Dashboard
 * Prevents any cached RealTimeDashboard from being created
 * This ensures the duplicate dashboard never appears
 */

(function() {
    'use strict';
    
    console.log('🚫 Blocking RealTimeDashboard creation...');
    
    // Override the RealTimeDashboard constructor if it exists
    if (window.RealTimeDashboard) {
        window.RealTimeDashboard = function() {
            console.log('❌ RealTimeDashboard creation blocked - duplicate functionality removed');
            return {
                showDashboard: function() {},
                hideDashboard: function() {},
                init: function() {},
                destroy: function() {}
            };
        };
    }
    
    // Prevent future definition
    Object.defineProperty(window, 'RealTimeDashboard', {
        get: function() {
            return function() {
                console.log('❌ RealTimeDashboard blocked');
                return {
                    showDashboard: function() {},
                    hideDashboard: function() {},
                    init: function() {},
                    destroy: function() {}
                };
            };
        },
        set: function() {
            console.log('❌ Attempt to define RealTimeDashboard blocked');
        },
        configurable: false
    });
    
    // Also remove any existing real-time dashboard divs
    function removeRealTimeDashboard() {
        const rtd = document.querySelectorAll('#real-time-dashboard, .real-time-dashboard');
        rtd.forEach(el => {
            console.log('🗑️ Removing real-time dashboard element:', el);
            el.remove();
        });
    }
    
    // Remove on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', removeRealTimeDashboard);
    } else {
        removeRealTimeDashboard();
    }
    
    // Monitor for any attempts to create it
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) { // Element node
                    if (node.id === 'real-time-dashboard' || 
                        node.classList && node.classList.contains('real-time-dashboard')) {
                        console.log('🚫 Blocking real-time dashboard insertion');
                        node.remove();
                    }
                }
            });
        });
    });
    
    // Start observing
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('✅ RealTimeDashboard blocker active');
})();
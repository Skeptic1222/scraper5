/**
 * Bootstrap Compatibility Fix
 * Ensures Bootstrap is available before other scripts try to use it
 */

(function() {
    'use strict';
    
    console.log('🔧 Bootstrap Compatibility Fix initializing...');
    
    // Wait for Bootstrap to be loaded
    function waitForBootstrap(callback, maxAttempts = 50) {
        let attempts = 0;
        
        const checkBootstrap = function() {
            attempts++;
            
            if (typeof bootstrap !== 'undefined' && bootstrap.Toast && bootstrap.Modal) {
                console.log('✅ Bootstrap loaded successfully');
                if (callback) callback();
                return;
            }
            
            if (attempts >= maxAttempts) {
                console.error('❌ Bootstrap failed to load after maximum attempts');
                // Create a minimal fallback
                window.bootstrap = window.bootstrap || {
                    Toast: function() {
                        return { show: function() {}, hide: function() {} };
                    },
                    Modal: function() {
                        return { show: function() {}, hide: function() {} };
                    },
                    Tooltip: function() {
                        return { show: function() {}, hide: function() {} };
                    },
                    Popover: function() {
                        return { show: function() {}, hide: function() {} };
                    },
                    Dropdown: function() {
                        return { show: function() {}, hide: function() {} };
                    }
                };
                console.log('⚠️ Bootstrap fallback created');
                if (callback) callback();
                return;
            }
            
            // Try again in 100ms
            setTimeout(checkBootstrap, 100);
        };
        
        checkBootstrap();
    }
    
    // Initialize Bootstrap components when ready
    waitForBootstrap(function() {
        // Initialize tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
            try {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            } catch (e) {
                console.warn('Failed to initialize tooltip:', e);
            }
        });
        
        // Initialize popovers
        const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => {
            try {
                return new bootstrap.Popover(popoverTriggerEl);
            } catch (e) {
                console.warn('Failed to initialize popover:', e);
            }
        });
        
        console.log('✅ Bootstrap components initialized');
    });
    
    // Also expose a global function to check Bootstrap availability
    window.ensureBootstrap = function(callback) {
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            callback();
        } else {
            waitForBootstrap(callback);
        }
    };
    
    // Fix for scripts that try to use bootstrap immediately
    if (typeof bootstrap === 'undefined') {
        // Create temporary placeholder
        window.bootstrap = {
            _pending: true,
            Toast: function(...args) {
                waitForBootstrap(() => {
                    new bootstrap.Toast(...args);
                });
                return { show: function() {}, hide: function() {} };
            },
            Modal: function(...args) {
                waitForBootstrap(() => {
                    new bootstrap.Modal(...args);
                });
                return { show: function() {}, hide: function() {} };
            }
        };
    }
    
    console.log('✅ Bootstrap Compatibility Fix loaded');
})();
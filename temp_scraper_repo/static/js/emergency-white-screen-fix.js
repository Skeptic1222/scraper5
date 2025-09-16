/**
 * EMERGENCY FIX: Prevent white screen and flashing
 * This must run IMMEDIATELY before any other scripts
 */

(function() {
    'use strict';

    // Prevent multiple initializations that cause flashing
    if (window.__EMERGENCY_FIX_APPLIED) {
        return;
    }
    window.__EMERGENCY_FIX_APPLIED = true;

    // Stop all animations during page load
    const style = document.createElement('style');
    style.id = 'emergency-no-flash';
    style.innerHTML = `
        * {
            animation: none !important;
            transition: none !important;
        }

        body {
            opacity: 1 !important;
            visibility: visible !important;
            background: #f8f9fa !important;
            display: block !important;
        }

        /* Prevent white flash */
        html, body {
            background-color: #f8f9fa !important;
            min-height: 100vh !important;
        }

        /* Force main content visible */
        .main-content, #app, .container, main {
            opacity: 1 !important;
            visibility: visible !important;
            display: block !important;
        }

        /* Hide loading screens */
        .loading, .spinner, .loader {
            display: none !important;
        }
    `;

    // Add style immediately
    if (document.head) {
        document.head.insertBefore(style, document.head.firstChild);
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            document.head.insertBefore(style, document.head.firstChild);
        });
    }

    // Prevent script conflicts
    const originalAddEventListener = window.addEventListener;
    const blockedEvents = new Set();

    window.addEventListener = function(event, handler, options) {
        const key = event + '_' + handler.toString().substring(0, 50);

        // Prevent duplicate event handlers
        if (blockedEvents.has(key)) {
            console.warn('Blocked duplicate event handler:', event);
            return;
        }
        blockedEvents.add(key);

        return originalAddEventListener.call(this, event, handler, options);
    };

    // Fix DOMContentLoaded multiple firing
    let domReady = false;
    document.addEventListener('DOMContentLoaded', function() {
        if (domReady) return;
        domReady = true;

        // Remove no-flash styles after load
        setTimeout(function() {
            const noFlash = document.getElementById('emergency-no-flash');
            if (noFlash) {
                noFlash.innerHTML = `
                    * {
                        animation: revert !important;
                        transition: revert !important;
                    }
                `;
            }
        }, 500);
    });

    // Prevent console spam
    const originalConsoleError = console.error;
    const errorCounts = {};

    console.error = function() {
        const msg = Array.from(arguments).join(' ');
        const key = msg.substring(0, 100);

        if (!errorCounts[key]) {
            errorCounts[key] = 0;
        }

        errorCounts[key]++;

        // Only show first 3 occurrences of each error
        if (errorCounts[key] <= 3) {
            originalConsoleError.apply(console, arguments);
        }
    };

    console.log('🛡️ Emergency white screen fix applied');
})();
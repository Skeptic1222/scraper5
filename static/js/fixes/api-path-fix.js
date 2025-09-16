/**
 * API Path Fix
 * Ensures all API calls use the correct base path
 * This fixes the mismatch between frontend expecting /scraper/api/* and backend serving /api/*
 */

(function() {
    'use strict';
    
    console.log('🔧 API Path Fix initializing...');
    
    // Store original fetch
    const originalFetch = window.fetch;
    
    // Helper function to fix API paths
    function fixApiPath(url) {
        // ⚠️ CRITICAL: NEVER ADD PORTS TO URLS! ⚠️
        // IIS proxy handles routing - we MUST use /scraper prefix without ports
        
        // If it's already a full URL, REMOVE any port numbers
        if (url.startsWith('http://') || url.startsWith('https://')) {
            // Strip port numbers from URLs (e.g., :5050, :5000, :3000)
            url = url.replace(/:\d+/, '');
        }
        
        // ALWAYS use /scraper as base path (NO PORTS!)
        const basePath = '/scraper';  // NEVER change this to include a port!
        
        // Handle various API path patterns
        if (url.startsWith('/api/')) {
            // Direct API path - add /scraper prefix
            return `${basePath}${url}`;  // Results in /scraper/api/...
        } else if (url.startsWith('/scraper/api/')) {
            // Already has correct /scraper prefix - keep it!
            return url;  // NO PORTS!
        } else if (url.includes('/api/')) {
            // Contains API somewhere in the path
            if (basePath && !url.includes(basePath)) {
                // Add base path if not already present
                const apiIndex = url.indexOf('/api/');
                return url.substring(0, apiIndex) + basePath + url.substring(apiIndex);
            }
        }
        
        return url;
    }
    
    // Override fetch to fix API paths
    window.fetch = function(...args) {
        // Fix the URL if it's a string
        if (typeof args[0] === 'string') {
            args[0] = fixApiPath(args[0]);
            console.log('📡 Fixed API path:', args[0]);
        } else if (args[0] instanceof Request) {
            // Handle Request objects
            const request = args[0];
            const fixedUrl = fixApiPath(request.url);
            if (fixedUrl !== request.url) {
                args[0] = new Request(fixedUrl, request);
                console.log('📡 Fixed API Request path:', fixedUrl);
            }
        }
        
        // Call original fetch with fixed arguments
        return originalFetch.apply(this, args);
    };
    
    // Also fix XMLHttpRequest for older code
    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        const fixedUrl = fixApiPath(url);
        if (fixedUrl !== url) {
            console.log('📡 Fixed XHR path:', fixedUrl);
        }
        return originalXHROpen.call(this, method, fixedUrl, ...args);
    };
    
    // Fix jQuery AJAX if it exists
    if (typeof $ !== 'undefined' && $.ajax) {
        const originalAjax = $.ajax;
        $.ajax = function(options) {
            if (typeof options === 'string') {
                // URL is first argument
                arguments[0] = fixApiPath(options);
            } else if (options && options.url) {
                // URL is in options object
                options.url = fixApiPath(options.url);
            }
            return originalAjax.apply(this, arguments);
        };
    }
    
    // Fix common API endpoints used in the app
    const commonEndpoints = [
        '/api/sources',
        '/api/assets', 
        '/api/search',
        '/api/download',
        '/api/stats',
        '/api/jobs',
        '/api/user',
        '/api/settings',
        '/api/asset',
        '/api/media'
    ];
    
    // Create global helper function for building API URLs
    window.buildApiUrl = function(endpoint, params) {
        let url = fixApiPath(endpoint);
        
        if (params && typeof params === 'object') {
            const queryString = new URLSearchParams(params).toString();
            if (queryString) {
                url += (url.includes('?') ? '&' : '?') + queryString;
            }
        }
        
        return url;
    };
    
    // Export for use in other modules
    window.apiPathFix = {
        fixPath: fixApiPath,
        buildUrl: window.buildApiUrl,
        endpoints: commonEndpoints.reduce((acc, endpoint) => {
            const key = endpoint.replace('/api/', '').replace('/', '_');
            acc[key] = () => fixApiPath(endpoint);
            return acc;
        }, {})
    };
    
    console.log('✅ API Path Fix loaded - All API calls will now use correct paths');
    console.log('📍 Current APP_BASE:', window.APP_BASE || '(empty - direct API access)');
})();
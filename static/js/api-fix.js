/**
 * API Fix for IIS Routing
 * Ensures all API calls use the correct base URL
 */

// Save original fetch function
const originalFetch = window.fetch;

// Override fetch to automatically fix API URLs
window.fetch = function(url, options) {
    // Check if this is an API call
    if (typeof url === 'string' && url.startsWith('/api/')) {
        // Fix the URL by adding the APP_BASE prefix
        const baseUrl = window.APP_BASE || '/scraper';
        url = baseUrl + url;
        console.log('[API Fix] Rewriting API URL to:', url);
    }

    // Call original fetch with fixed URL
    return originalFetch.call(this, url, options);
};

// Also fix any jQuery AJAX calls if jQuery is available
if (typeof $ !== 'undefined' && $.ajax) {
    const originalAjax = $.ajax;
    $.ajax = function(settings) {
        if (settings && settings.url && settings.url.startsWith('/api/')) {
            const baseUrl = window.APP_BASE || '/scraper';
            settings.url = baseUrl + settings.url;
            console.log('[API Fix] Rewriting jQuery AJAX URL to:', settings.url);
        }
        return originalAjax.call(this, settings);
    };
}

console.log('[API Fix] API URL interceptor loaded - all /api/* calls will be routed through', window.APP_BASE || '/scraper');
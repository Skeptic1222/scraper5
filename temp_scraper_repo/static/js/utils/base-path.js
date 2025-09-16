/**
 * Base path and fetch wrapper for hosting under subpath (e.g., /scraper)
 * - Sets a global APP_BASE from window.APP_BASE (injected by template)
 * - Prefixes any fetch URL starting with "/api/" with APP_BASE
 */
(function() {
  try {
    // Prefer explicit APP_BASE, else meta tag app-prefix, else ""
    var metaBase = '';
    try {
      var m = document.querySelector('meta[name="app-prefix"]');
      if (m && m.content) metaBase = m.content;
    } catch (e) {}
    var explicit = (typeof window.APP_BASE === 'string') ? window.APP_BASE : undefined;
    var base = (explicit && explicit.length) ? explicit : (metaBase || '');
    if (base === '/') base = '';
    if (base && !base.startsWith('/')) base = '/' + base;
    if (base.endsWith('/')) base = base.slice(0, -1);
    window.APP_BASE = base;

    // Patch fetch so absolute API calls work under /scraper
    var originalFetch = window.fetch;
    window.fetch = function(input, init) {
      try {
        if (typeof input === 'string') {
          if (input.startsWith('/api/')) {
            input = (window.APP_BASE || '') + input;
          }
        } else if (input && input.url && typeof input.url === 'string') {
          if (input.url.startsWith('/api/')) {
            var newUrl = (window.APP_BASE || '') + input.url;
            input = new Request(newUrl, input);
          }
        }
      } catch (e) {
        // Non-fatal, fall through
      }
      return originalFetch.call(this, input, init);
    };
  } catch (err) {
    console.error('Failed to initialize APP_BASE fetch wrapper:', err);
  }
})();

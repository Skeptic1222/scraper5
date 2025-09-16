/**
 * CRITICAL API PATH FIX
 * Ensures all API calls use the correct /scraper prefix for IIS deployment
 * Addresses 404 errors: /scraper/api/assets, /scraper/api/sources, /scraper/api/stats
 */

(function() {
    'use strict';

    console.log('🚨 CRITICAL: API path fix loading...');

    // Get the correct app base path
    const APP_BASE = window.APP_BASE || '/scraper';
    console.log(`📍 CRITICAL: Using APP_BASE: ${APP_BASE}`);

    // API ENDPOINT MAPPING
    const API_ENDPOINTS = {
        assets: `${APP_BASE}/api/assets`,
        sources: `${APP_BASE}/api/sources`,
        stats: `${APP_BASE}/api/stats`,
        search: `${APP_BASE}/api/search`,
        jobs: `${APP_BASE}/api/jobs`,
        admin: `${APP_BASE}/api/admin`,
        auth: `${APP_BASE}/auth`
    };

    // ENHANCED FETCH WRAPPER
    function apiRequest(endpoint, options = {}) {
        // Ensure endpoint has proper prefix
        let url = endpoint;
        if (!url.startsWith('http') && !url.startsWith(APP_BASE)) {
            // Handle relative URLs
            if (url.startsWith('/api/')) {
                url = APP_BASE + url;
            } else if (url.startsWith('api/')) {
                url = APP_BASE + '/' + url;
            } else if (!url.startsWith('/')) {
                url = APP_BASE + '/api/' + url;
            }
        }

        console.log(`🌐 CRITICAL: API request to ${url}`);

        // Default options
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };

        // Merge options
        const finalOptions = { ...defaultOptions, ...options };
        if (finalOptions.headers && options.headers) {
            finalOptions.headers = { ...defaultOptions.headers, ...options.headers };
        }

        // Add CSRF token if available
        const csrfToken = document.querySelector('meta[name=csrf-token]');
        if (csrfToken && finalOptions.method !== 'GET') {
            finalOptions.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
        }

        return fetch(url, finalOptions)
            .then(response => {
                console.log(`📊 CRITICAL: API response ${response.status} for ${url}`);

                if (!response.ok) {
                    console.error(`❌ CRITICAL: API error ${response.status} for ${url}`);
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                return response;
            })
            .catch(error => {
                console.error(`💥 CRITICAL: API request failed for ${url}:`, error);
                throw error;
            });
    }

    // ASSET API FUNCTIONS
    window.assetAPI = {
        getAssets: () => apiRequest(API_ENDPOINTS.assets),
        deleteAsset: (assetId) => apiRequest(`${API_ENDPOINTS.assets}/${assetId}`, { method: 'DELETE' }),
        bulkDelete: (assetIds) => apiRequest(`${API_ENDPOINTS.assets}/bulk-delete`, {
            method: 'POST',
            body: JSON.stringify({ asset_ids: assetIds })
        }),
        bulkMove: (assetIds, targetFolder) => apiRequest(`${API_ENDPOINTS.assets}/bulk-move`, {
            method: 'POST',
            body: JSON.stringify({ asset_ids: assetIds, target_folder: targetFolder })
        })
    };

    // SOURCES API FUNCTIONS
    window.sourcesAPI = {
        getSources: (safeSearch = true) => apiRequest(`${API_ENDPOINTS.sources}?safe_search=${safeSearch}`),
        updateSource: (sourceId, enabled) => apiRequest(`${API_ENDPOINTS.sources}/${sourceId}`, {
            method: 'PUT',
            body: JSON.stringify({ enabled })
        })
    };

    // STATS API FUNCTIONS
    window.statsAPI = {
        getStats: () => apiRequest(API_ENDPOINTS.stats),
        getSystemInfo: () => apiRequest(`${API_ENDPOINTS.stats}/system`)
    };

    // SEARCH API FUNCTIONS
    window.searchAPI = {
        startSearch: (searchData) => apiRequest(API_ENDPOINTS.search, {
            method: 'POST',
            body: JSON.stringify(searchData)
        }),
        getSearchResults: (jobId) => apiRequest(`${API_ENDPOINTS.search}/${jobId}`)
    };

    // JOBS API FUNCTIONS
    window.jobsAPI = {
        getJobs: () => apiRequest(API_ENDPOINTS.jobs),
        getJob: (jobId) => apiRequest(`${API_ENDPOINTS.jobs}/${jobId}`),
        cancelJob: (jobId) => apiRequest(`${API_ENDPOINTS.jobs}/${jobId}/cancel`, { method: 'POST' }),
        deleteJob: (jobId) => apiRequest(`${API_ENDPOINTS.jobs}/${jobId}`, { method: 'DELETE' })
    };

    // OVERRIDE GLOBAL FETCH FOR API CALLS
    const originalFetch = window.fetch;
    window.fetch = function(input, init) {
        let url = input;

        // Handle Request objects
        if (input instanceof Request) {
            url = input.url;
        }

        // Only modify API calls
        if (typeof url === 'string' && url.includes('/api/')) {
            // Ensure API calls have proper prefix
            if (!url.startsWith('http') && !url.startsWith(APP_BASE)) {
                if (url.startsWith('/api/')) {
                    url = APP_BASE + url;
                } else if (url.startsWith('api/')) {
                    url = APP_BASE + '/' + url;
                }

                console.log(`🔧 CRITICAL: Fixed API URL from ${input} to ${url}`);

                // Update the input parameter
                if (input instanceof Request) {
                    input = new Request(url, input);
                } else {
                    input = url;
                }
            }
        }

        return originalFetch.call(this, input, init);
    };

    // PATCH EXISTING API CALLS IN APPLICATION
    function patchExistingAPICalls() {
        // Patch any existing global API functions
        if (window.app && window.app.modules) {
            // Asset manager
            if (window.app.modules.assetManager) {
                const assetManager = window.app.modules.assetManager;
                const originalLoadAssets = assetManager.loadAssets;
                if (originalLoadAssets) {
                    assetManager.loadAssets = function() {
                        return window.assetAPI.getAssets()
                            .then(response => response.json())
                            .then(data => {
                                if (this.updateAssetGrid) {
                                    this.updateAssetGrid(data.assets || []);
                                }
                                return data;
                            })
                            .catch(error => {
                                console.error('❌ CRITICAL: Asset loading failed:', error);
                                return { assets: [] };
                            });
                    };
                }
            }

            // Search manager
            if (window.app.modules.searchManager) {
                const searchManager = window.app.modules.searchManager;
                const originalLoadSources = searchManager.loadSources;
                if (originalLoadSources) {
                    searchManager.loadSources = function() {
                        return window.sourcesAPI.getSources()
                            .then(response => response.json())
                            .then(data => {
                                if (this.updateSourceGrid) {
                                    this.updateSourceGrid(data);
                                }
                                return data;
                            })
                            .catch(error => {
                                console.error('❌ CRITICAL: Sources loading failed:', error);
                                return {};
                            });
                    };
                }
            }
        }

        console.log('🔧 CRITICAL: API calls patched');
    }

    // INITIALIZATION
    function initializeAPIFix() {
        console.log('🚀 CRITICAL: Initializing API fix...');

        // Patch existing calls
        patchExistingAPICalls();

        // Test API endpoints
        setTimeout(testAPIEndpoints, 1000);

        console.log('✅ CRITICAL: API fix initialized');
    }

    // TEST API ENDPOINTS
    function testAPIEndpoints() {
        console.log('🧪 CRITICAL: Testing API endpoints...');

        // Test critical endpoints
        const tests = [
            { name: 'Assets', endpoint: API_ENDPOINTS.assets },
            { name: 'Sources', endpoint: API_ENDPOINTS.sources },
            { name: 'Stats', endpoint: API_ENDPOINTS.stats }
        ];

        tests.forEach(test => {
            fetch(test.endpoint, { method: 'GET', credentials: 'same-origin' })
                .then(response => {
                    if (response.ok) {
                        console.log(`✅ CRITICAL: ${test.name} API working`);
                    } else {
                        console.error(`❌ CRITICAL: ${test.name} API failed: ${response.status}`);
                    }
                })
                .catch(error => {
                    console.error(`💥 CRITICAL: ${test.name} API error:`, error);
                });
        });
    }

    // MULTIPLE INITIALIZATION TRIGGERS
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeAPIFix);
    } else {
        initializeAPIFix();
    }

    // Also initialize when app is ready
    let appCheckInterval = setInterval(() => {
        if (window.app) {
            clearInterval(appCheckInterval);
            patchExistingAPICalls();
        }
    }, 100);

    // Cleanup interval after 10 seconds
    setTimeout(() => {
        if (appCheckInterval) {
            clearInterval(appCheckInterval);
        }
    }, 10000);

    console.log('🛡️ CRITICAL: API path fix script loaded');

})();
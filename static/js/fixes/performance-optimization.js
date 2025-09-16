/**
 * Performance Optimization Module
 * Addresses sluggish and slow performance issues
 */

(function() {
    'use strict';
    
    console.log('⚡ Performance Optimization Module initializing...');
    
    // Debounce utility function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Throttle utility function
    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // Lazy loading for images
    function setupLazyLoading() {
        const images = document.querySelectorAll('img:not([loading="lazy"])');
        images.forEach(img => {
            if (!img.complete) {
                img.setAttribute('loading', 'lazy');
            }
        });
        
        // Use Intersection Observer for better performance
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            observer.unobserve(img);
                        }
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });
            
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }
    
    // Optimize scroll events
    function optimizeScrollEvents() {
        const scrollElements = document.querySelectorAll('.sidebar, .content-area, .activity-feed, .progress-body');
        
        scrollElements.forEach(element => {
            let isScrolling;
            
            // Throttle scroll events
            element.addEventListener('scroll', throttle(() => {
                // Add scrolling class for performance
                element.classList.add('is-scrolling');
                
                // Remove scrolling class after scrolling stops
                clearTimeout(isScrolling);
                isScrolling = setTimeout(() => {
                    element.classList.remove('is-scrolling');
                }, 150);
            }, 100));
        });
    }
    
    // Optimize input events
    function optimizeInputEvents() {
        // Debounce search inputs
        const searchInputs = document.querySelectorAll('.search-input, .filter-input, input[type="search"]');
        searchInputs.forEach(input => {
            const originalHandler = input.oninput;
            if (originalHandler) {
                input.oninput = debounce(originalHandler, 300);
            }
            
            // Also handle input event listeners
            const clone = input.cloneNode(true);
            input.parentNode.replaceChild(clone, input);
            clone.addEventListener('input', debounce((e) => {
                // Trigger custom event for other handlers
                const event = new CustomEvent('debounced-input', { detail: e.target.value });
                clone.dispatchEvent(event);
            }, 300));
        });
    }
    
    // Reduce reflows and repaints
    function optimizeDOMManipulation() {
        // Batch DOM updates
        const fragment = document.createDocumentFragment();
        
        // Use requestAnimationFrame for visual updates
        let rafId;
        const scheduleUpdate = (callback) => {
            if (rafId) {
                cancelAnimationFrame(rafId);
            }
            rafId = requestAnimationFrame(callback);
        };
        
        // Make it globally available
        window.scheduleVisualUpdate = scheduleUpdate;
    }
    
    // Optimize animations
    function optimizeAnimations() {
        // Use CSS transforms instead of position changes
        const animatedElements = document.querySelectorAll('.nav-item, .enhanced-stat-card, .card');
        animatedElements.forEach(element => {
            // Force GPU acceleration
            element.style.willChange = 'transform';
            element.style.transform = 'translateZ(0)';
        });
        
        // Reduce animation duration on slower devices
        if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4) {
            document.documentElement.style.setProperty('--transition-fast', '150ms');
            document.documentElement.style.setProperty('--transition-normal', '250ms');
            document.documentElement.style.setProperty('--transition-slow', '350ms');
        }
    }
    
    // Memory leak prevention
    function preventMemoryLeaks() {
        // Clean up event listeners on navigation
        const originalShowSection = window.app?.showSection;
        if (originalShowSection) {
            window.app.showSection = function(section) {
                // Clean up before switching sections
                const activeSection = document.querySelector('.content-section.active');
                if (activeSection) {
                    // Remove event listeners from old section
                    const oldListeners = activeSection.querySelectorAll('[data-listener]');
                    oldListeners.forEach(el => {
                        const newEl = el.cloneNode(true);
                        el.parentNode.replaceChild(newEl, el);
                    });
                }
                
                // Call original function
                originalShowSection.call(this, section);
            };
        }
    }
    
    // Optimize API calls
    function optimizeAPICalls() {
        // Cache API responses
        const apiCache = new Map();
        const cacheTimeout = 60000; // 1 minute
        
        // Wrap fetch to add caching
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            // Only cache GET requests
            if (!options.method || options.method === 'GET') {
                const cacheKey = url + JSON.stringify(options);
                const cached = apiCache.get(cacheKey);
                
                if (cached && Date.now() - cached.timestamp < cacheTimeout) {
                    console.log('📦 Using cached response for:', url);
                    return Promise.resolve(cached.response.clone());
                }
                
                return originalFetch(url, options).then(response => {
                    // Cache successful responses
                    if (response.ok) {
                        apiCache.set(cacheKey, {
                            response: response.clone(),
                            timestamp: Date.now()
                        });
                        
                        // Clean old cache entries
                        if (apiCache.size > 50) {
                            const firstKey = apiCache.keys().next().value;
                            apiCache.delete(firstKey);
                        }
                    }
                    return response;
                });
            }
            
            return originalFetch(url, options);
        };
    }
    
    // Reduce unnecessary re-renders
    function optimizeReRenders() {
        // Prevent unnecessary dashboard updates
        let lastUpdateTime = 0;
        const minUpdateInterval = 5000; // 5 seconds
        
        if (window.app?.modules?.dashboard?.update) {
            const originalUpdate = window.app.modules.dashboard.update;
            window.app.modules.dashboard.update = function(...args) {
                const now = Date.now();
                if (now - lastUpdateTime > minUpdateInterval) {
                    lastUpdateTime = now;
                    originalUpdate.apply(this, args);
                }
            };
        }
    }
    
    // Web Worker for heavy computations (if needed)
    function setupWebWorker() {
        // Create a simple worker for heavy calculations
        const workerCode = `
            self.addEventListener('message', function(e) {
                const { type, data } = e.data;
                
                switch(type) {
                    case 'process-data':
                        // Process data in worker thread
                        const result = data; // Process as needed
                        self.postMessage({ type: 'data-processed', result });
                        break;
                }
            });
        `;
        
        const blob = new Blob([workerCode], { type: 'application/javascript' });
        const workerUrl = URL.createObjectURL(blob);
        
        // Make worker available globally if needed
        window.performanceWorker = new Worker(workerUrl);
    }
    
    // Initialize all optimizations
    function initialize() {
        setupLazyLoading();
        optimizeScrollEvents();
        optimizeInputEvents();
        optimizeDOMManipulation();
        optimizeAnimations();
        preventMemoryLeaks();
        optimizeAPICalls();
        optimizeReRenders();
        
        // Only setup worker if needed for heavy computations
        if (window.Worker) {
            setupWebWorker();
        }
        
        // Add performance monitoring
        if (window.performance && window.performance.mark) {
            window.performance.mark('performance-optimizations-complete');
            
            // Log performance metrics
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    console.log('📊 Performance Metrics:');
                    console.log(`  DOM Content Loaded: ${Math.round(perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart)}ms`);
                    console.log(`  Load Complete: ${Math.round(perfData.loadEventEnd - perfData.loadEventStart)}ms`);
                    console.log(`  Total Load Time: ${Math.round(perfData.loadEventEnd - perfData.fetchStart)}ms`);
                }
            }, 1000);
        }
        
        console.log('✅ Performance optimizations applied');
    }
    
    // Run optimizations when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Also run after window load for late-loading resources
    window.addEventListener('load', () => {
        setTimeout(initialize, 1000);
    });
    
    // Export utilities for global use
    window.performanceUtils = {
        debounce,
        throttle,
        scheduleVisualUpdate: window.scheduleVisualUpdate
    };
})();
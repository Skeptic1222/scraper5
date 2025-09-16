/**
 * Browser Error Logger
 * Captures all browser errors and sends them to the server for logging
 * Logs are saved to /logs/browser-errors.log in the project folder
 */

(function() {
    'use strict';
    
    console.log('🔍 Browser Error Logger initialized');
    
    // Configuration
    const ERROR_LOG_ENDPOINT = window.APP_BASE + '/api/log-browser-error';
    const MAX_ERROR_LENGTH = 5000; // Maximum error message length
    const ERROR_BATCH_INTERVAL = 5000; // Send errors every 5 seconds
    const MAX_ERRORS_PER_BATCH = 10; // Maximum errors to send at once
    
    // Error queue
    let errorQueue = [];
    let isProcessing = false;
    
    /**
     * Format error for logging
     */
    function formatError(error, source, lineno, colno, errorObj) {
        const errorData = {
            timestamp: new Date().toISOString(),
            message: error ? error.toString() : 'Unknown error',
            source: source || 'unknown',
            line: lineno || 0,
            column: colno || 0,
            userAgent: navigator.userAgent,
            url: window.location.href,
            stack: '',
            type: 'javascript-error'
        };
        
        // Add stack trace if available
        if (errorObj && errorObj.stack) {
            errorData.stack = errorObj.stack.substring(0, MAX_ERROR_LENGTH);
        }
        
        // Add additional context
        errorData.context = {
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            },
            screen: {
                width: screen.width,
                height: screen.height
            },
            section: getCurrentSection(),
            memory: getMemoryUsage()
        };
        
        return errorData;
    }
    
    /**
     * Get current section from URL or DOM
     */
    function getCurrentSection() {
        // Try to get from URL hash
        if (window.location.hash) {
            return window.location.hash.substring(1);
        }
        
        // Try to get from active section
        const activeSection = document.querySelector('.content-section.active');
        if (activeSection) {
            return activeSection.id.replace('-section', '');
        }
        
        return 'unknown';
    }
    
    /**
     * Get memory usage if available
     */
    function getMemoryUsage() {
        if (performance.memory) {
            return {
                usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1048576) + ' MB',
                totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1048576) + ' MB',
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1048576) + ' MB'
            };
        }
        return null;
    }
    
    /**
     * Send error to server
     */
    async function sendErrorToServer(errorData) {
        try {
            const response = await fetch(ERROR_LOG_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(errorData)
            });
            
            if (!response.ok) {
                console.warn('Failed to log error to server:', response.status);
            }
        } catch (err) {
            // Silently fail - we don't want to create an error loop
            console.warn('Could not send error to server:', err);
        }
    }
    
    /**
     * Process error queue
     */
    async function processErrorQueue() {
        if (isProcessing || errorQueue.length === 0) {
            return;
        }
        
        isProcessing = true;
        
        // Get batch of errors
        const batch = errorQueue.splice(0, MAX_ERRORS_PER_BATCH);
        
        // Send batch to server
        try {
            await sendErrorToServer({
                type: 'error-batch',
                errors: batch,
                timestamp: new Date().toISOString()
            });
            
            console.log(`📊 Sent ${batch.length} errors to server`);
        } catch (err) {
            // Put errors back in queue
            errorQueue = batch.concat(errorQueue);
        }
        
        isProcessing = false;
    }
    
    /**
     * Global error handler
     */
    window.addEventListener('error', function(event) {
        const errorData = formatError(
            event.message,
            event.filename,
            event.lineno,
            event.colno,
            event.error
        );
        
        // Add to queue
        errorQueue.push(errorData);
        
        // Log to console for development
        console.error('🔴 JavaScript Error:', errorData);
        
        // Don't prevent default handling
        return false;
    });
    
    /**
     * Promise rejection handler
     */
    window.addEventListener('unhandledrejection', function(event) {
        const errorData = {
            timestamp: new Date().toISOString(),
            message: event.reason ? event.reason.toString() : 'Unhandled Promise Rejection',
            type: 'unhandled-rejection',
            url: window.location.href,
            stack: event.reason && event.reason.stack ? event.reason.stack : '',
            userAgent: navigator.userAgent,
            context: {
                section: getCurrentSection(),
                memory: getMemoryUsage()
            }
        };
        
        // Add to queue
        errorQueue.push(errorData);
        
        // Log to console
        console.error('🔴 Unhandled Promise Rejection:', errorData);
    });
    
    /**
     * Console error interceptor
     */
    const originalConsoleError = console.error;
    console.error = function(...args) {
        // Call original console.error
        originalConsoleError.apply(console, args);
        
        // Format and queue the error
        const errorData = {
            timestamp: new Date().toISOString(),
            message: args.map(arg => {
                if (typeof arg === 'object') {
                    try {
                        return JSON.stringify(arg);
                    } catch (e) {
                        return arg.toString();
                    }
                }
                return arg;
            }).join(' '),
            type: 'console-error',
            url: window.location.href,
            userAgent: navigator.userAgent,
            context: {
                section: getCurrentSection(),
                memory: getMemoryUsage()
            }
        };
        
        errorQueue.push(errorData);
    };
    
    /**
     * Network error handler
     */
    function logNetworkError(url, status, statusText) {
        const errorData = {
            timestamp: new Date().toISOString(),
            message: `Network Error: ${status} ${statusText}`,
            type: 'network-error',
            url: window.location.href,
            requestUrl: url,
            status: status,
            userAgent: navigator.userAgent,
            context: {
                section: getCurrentSection(),
                memory: getMemoryUsage()
            }
        };
        
        errorQueue.push(errorData);
        console.error('🔴 Network Error:', errorData);
    }
    
    /**
     * Intercept fetch to catch network errors
     */
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch.apply(this, args).catch(err => {
            logNetworkError(args[0], 0, err.message);
            throw err;
        }).then(response => {
            if (!response.ok && response.status >= 500) {
                logNetworkError(response.url, response.status, response.statusText);
            }
            return response;
        });
    };
    
    /**
     * Process queue periodically
     */
    setInterval(processErrorQueue, ERROR_BATCH_INTERVAL);
    
    /**
     * Send remaining errors before page unload
     */
    window.addEventListener('beforeunload', function() {
        if (errorQueue.length > 0) {
            // Try to send remaining errors synchronously
            const xhr = new XMLHttpRequest();
            xhr.open('POST', ERROR_LOG_ENDPOINT, false); // Synchronous
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({
                type: 'error-batch',
                errors: errorQueue,
                timestamp: new Date().toISOString(),
                unloading: true
            }));
        }
    });
    
    /**
     * Manual error logging function for debugging
     */
    window.logError = function(message, details) {
        const errorData = {
            timestamp: new Date().toISOString(),
            message: message,
            type: 'manual-log',
            details: details,
            url: window.location.href,
            userAgent: navigator.userAgent,
            context: {
                section: getCurrentSection(),
                memory: getMemoryUsage()
            }
        };
        
        errorQueue.push(errorData);
        console.log('📝 Manual error logged:', errorData);
    };
    
    console.log('✅ Browser error logging active - errors will be saved to /logs/browser-errors.log');
})();
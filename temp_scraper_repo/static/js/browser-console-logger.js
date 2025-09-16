
// Browser Console Logger - Captures all console output
(function() {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    const originalInfo = console.info;
    const originalDebug = console.debug;

    const logs = [];
    const maxLogs = 1000;

    function captureLog(type, args) {
        const log = {
            type: type,
            timestamp: new Date().toISOString(),
            message: Array.from(args).map(arg => {
                try {
                    if (typeof arg === 'object') {
                        return JSON.stringify(arg, null, 2);
                    }
                    return String(arg);
                } catch (e) {
                    return '[Unable to stringify]';
                }
            }).join(' '),
            stack: new Error().stack
        };

        logs.push(log);
        if (logs.length > maxLogs) {
            logs.shift();
        }

        // Send to server
        try {
            fetch('/api/browser-log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(log)
            }).catch(() => {});
        } catch (e) {}

        return log;
    }

    console.log = function() {
        captureLog('log', arguments);
        originalLog.apply(console, arguments);
    };

    console.error = function() {
        captureLog('error', arguments);
        originalError.apply(console, arguments);
    };

    console.warn = function() {
        captureLog('warn', arguments);
        originalWarn.apply(console, arguments);
    };

    console.info = function() {
        captureLog('info', arguments);
        originalInfo.apply(console, arguments);
    };

    console.debug = function() {
        captureLog('debug', arguments);
        originalDebug.apply(console, arguments);
    };

    // Capture unhandled errors
    window.addEventListener('error', function(e) {
        captureLog('error', [e.message, e.filename, e.lineno, e.colno, e.error]);
    });

    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        captureLog('error', ['Unhandled Promise Rejection:', e.reason]);
    });

    // Expose logs for debugging
    window.__browserLogs = logs;
    window.__getBrowserLogs = () => logs;
    window.__clearBrowserLogs = () => logs.length = 0;

    console.log('[Browser Logger] Console logging enabled - all output will be captured');
})();

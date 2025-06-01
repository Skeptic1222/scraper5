/**
 * ============================================================================
 * SECURITY UTILITIES
 * ============================================================================
 * 
 * Provides secure methods for DOM manipulation, input sanitization,
 * and XSS prevention to replace unsafe innerHTML usage.
 */

class SecurityUtils {
    /**
     * Sanitize HTML content to prevent XSS attacks
     * @param {string} input - The input string to sanitize
     * @returns {string} - Sanitized string
     */
    static sanitizeHTML(input) {
        if (typeof input !== 'string') return '';
        
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }

    /**
     * Sanitize and validate URLs
     * @param {string} url - The URL to validate
     * @returns {string|null} - Valid URL or null if invalid
     */
    static sanitizeURL(url) {
        if (typeof url !== 'string') return null;
        
        try {
            const parsedURL = new URL(url);
            // Only allow http, https, and data URLs
            if (['http:', 'https:', 'data:'].includes(parsedURL.protocol)) {
                return parsedURL.href;
            }
        } catch (error) {
            console.warn('Invalid URL provided:', url);
        }
        
        return null;
    }

    /**
     * Safely create DOM elements with content
     * @param {string} tagName - HTML tag name
     * @param {Object} options - Element options
     * @param {string} options.textContent - Safe text content
     * @param {string} options.className - CSS classes
     * @param {Object} options.attributes - HTML attributes
     * @param {Object} options.dataset - Data attributes
     * @returns {HTMLElement} - Created element
     */
    static createElement(tagName, options = {}) {
        const element = document.createElement(tagName);
        
        if (options.textContent) {
            element.textContent = options.textContent;
        }
        
        if (options.className) {
            element.className = options.className;
        }
        
        if (options.attributes) {
            Object.entries(options.attributes).forEach(([key, value]) => {
                // Sanitize attribute values
                if (typeof value === 'string') {
                    element.setAttribute(key, this.sanitizeHTML(value));
                }
            });
        }
        
        if (options.dataset) {
            Object.entries(options.dataset).forEach(([key, value]) => {
                element.dataset[key] = this.sanitizeHTML(String(value));
            });
        }
        
        return element;
    }

    /**
     * Safely set element content without XSS risk
     * @param {HTMLElement} element - Target element
     * @param {string} content - Content to set
     * @param {boolean} isHTML - Whether content is HTML (will be sanitized)
     */
    static setContent(element, content, isHTML = false) {
        if (!element || typeof content !== 'string') return;
        
        if (isHTML) {
            // Sanitize HTML content
            element.innerHTML = this.sanitizeHTML(content);
        } else {
            // Safe text content
            element.textContent = content;
        }
    }

    /**
     * Validate and sanitize search input
     * @param {string} input - Search query
     * @returns {string} - Sanitized search query
     */
    static sanitizeSearchInput(input) {
        if (typeof input !== 'string') return '';
        
        // Remove potentially dangerous characters
        return input
            .trim()
            .replace(/[<>"/&']/g, '') // Remove HTML special chars
            .replace(/javascript:/gi, '') // Remove javascript: protocol
            .replace(/on\w+=/gi, '') // Remove event handlers
            .substring(0, 500); // Limit length
    }

    /**
     * Validate numeric input
     * @param {any} input - Input to validate
     * @param {number} min - Minimum value
     * @param {number} max - Maximum value
     * @returns {number|null} - Valid number or null
     */
    static validateNumber(input, min = -Infinity, max = Infinity) {
        const num = Number(input);
        
        if (isNaN(num) || num < min || num > max) {
            return null;
        }
        
        return num;
    }

    /**
     * Create secure event listeners that prevent common attacks
     * @param {HTMLElement} element - Target element
     * @param {string} event - Event type
     * @param {Function} handler - Event handler
     * @param {Object} options - Event options
     */
    static addSecureEventListener(element, event, handler, options = {}) {
        if (!element || typeof handler !== 'function') return;
        
        const secureHandler = (e) => {
            try {
                // Prevent default if needed
                if (options.preventDefault) {
                    e.preventDefault();
                }
                
                // Call original handler
                handler(e);
            } catch (error) {
                console.error('Event handler error:', error);
                // Don't let errors break the application
            }
        };
        
        element.addEventListener(event, secureHandler, options);
    }

    /**
     * Generate secure random ID for elements
     * @param {string} prefix - ID prefix
     * @returns {string} - Secure random ID
     */
    static generateSecureId(prefix = 'id') {
        const timestamp = Date.now().toString(36);
        const random = Math.random().toString(36).substring(2);
        return `${prefix}-${timestamp}-${random}`;
    }

    /**
     * Escape special regex characters in user input
     * @param {string} string - Input string
     * @returns {string} - Escaped string
     */
    static escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * Validate file types for uploads
     * @param {File} file - File object
     * @param {string[]} allowedTypes - Allowed MIME types
     * @returns {boolean} - Whether file is valid
     */
    static validateFileType(file, allowedTypes = []) {
        if (!file || !allowedTypes.length) return false;
        
        return allowedTypes.includes(file.type);
    }

    /**
     * Create secure form data from object
     * @param {Object} data - Data object
     * @returns {FormData} - Secure form data
     */
    static createSecureFormData(data) {
        const formData = new FormData();
        
        Object.entries(data).forEach(([key, value]) => {
            if (typeof value === 'string') {
                formData.append(key, this.sanitizeHTML(value));
            } else if (typeof value === 'number') {
                formData.append(key, value.toString());
            } else if (value instanceof File) {
                formData.append(key, value);
            }
        });
        
        return formData;
    }

    /**
     * Throttle function execution to prevent abuse
     * @param {Function} func - Function to throttle
     * @param {number} delay - Delay in milliseconds
     * @returns {Function} - Throttled function
     */
    static throttle(func, delay) {
        let timeoutId;
        let lastExecTime = 0;
        
        return function(...args) {
            const currentTime = Date.now();
            
            if (currentTime - lastExecTime > delay) {
                func.apply(this, args);
                lastExecTime = currentTime;
            } else {
                clearTimeout(timeoutId);
                timeoutId = setTimeout(() => {
                    func.apply(this, args);
                    lastExecTime = Date.now();
                }, delay - (currentTime - lastExecTime));
            }
        };
    }

    /**
     * Debounce function execution
     * @param {Function} func - Function to debounce
     * @param {number} delay - Delay in milliseconds
     * @returns {Function} - Debounced function
     */
    static debounce(func, delay) {
        let timeoutId;
        
        return function(...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text
     */
    static escapeHtml(text) {
        if (typeof text !== 'string') return '';
        
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export for use in other modules
window.SecurityUtils = SecurityUtils; 
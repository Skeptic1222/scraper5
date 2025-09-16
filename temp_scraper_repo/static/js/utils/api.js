/**
 * ============================================================================
 * API UTILITIES
 * ============================================================================
 * 
 * HTTP request utilities and API management
 */

class ApiClient {
    constructor() {
        this.baseUrl = (typeof window !== 'undefined' && window.APP_BASE) ? window.APP_BASE : '';
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    /**
     * Make a GET request
     */
    async get(endpoint, options = {}) {
        return this.request('GET', endpoint, null, options);
    }

    /**
     * Make a POST request
     */
    async post(endpoint, data = null, options = {}) {
        return this.request('POST', endpoint, data, options);
    }

    /**
     * Make a PUT request
     */
    async put(endpoint, data = null, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }

    /**
     * Make a DELETE request
     */
    async delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }

    /**
     * Generic request method
     */
    async request(method, endpoint, data = null, options = {}) {
        const url = this.baseUrl + endpoint;
        const config = {
            method,
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            config.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    /**
     * Upload file
     */
    async uploadFile(endpoint, file, options = {}) {
        const formData = new FormData();
        formData.append('file', file);

        const config = {
            method: 'POST',
            body: formData,
            ...options
        };

        // Don't set Content-Type header for FormData
        if (config.headers) {
            delete config.headers['Content-Type'];
        }

        return this.request('POST', endpoint, null, config);
    }
}

// Create global instance
window.apiClient = new ApiClient();

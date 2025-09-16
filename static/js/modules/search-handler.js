/**
 * Search Handler
 * Manages search form submission and results display
 */
class SearchHandler {
    constructor() {
        this.init();
        this.isSearching = false;
        this.currentJobId = null;
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => this.handleSearch(e));
        }
    }

    getCsrfToken() {
        // Try to get CSRF token from meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.content;
        }
        
        // Try to get from cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrf_token') {
                return decodeURIComponent(value);
            }
        }
        
        // If no CSRF token found, return null
        return null;
    }

    async handleSearch(e) {
        e.preventDefault();
        
        if (this.isSearching) {
            alert('Search already in progress...');
            return;
        }
        
        const query = document.getElementById('search-query').value;
        if (!query) {
            alert('Please enter a search query');
            return;
        }
        
        // Get selected sources
        const selectedSources = window.searchUI ? window.searchUI.getSelectedSources() : [];
        
        if (selectedSources.length === 0) {
            alert('Please select at least one source to search');
            return;
        }
        
        console.log('Starting search for:', query);
        console.log('Selected sources:', selectedSources);
        
        this.isSearching = true;
        this.showProgress('Starting search...');
        
        try {
            // Get CSRF token
            const csrfToken = this.getCsrfToken();
            
            // Try with FormData first (works better with Flask-WTF)
            const formData = new FormData();
            formData.append('search-query', query);
            formData.append('search-type', 'comprehensive');
            formData.append('sources', selectedSources.join(','));
            formData.append('limit', '50');
            if (csrfToken) {
                formData.append('csrf_token', csrfToken);
            }
            
            // Try the search endpoint with form data
            const response = await fetch('/api/search', {
                method: 'POST',
                credentials: 'same-origin',
                body: formData
            });
            
            if (!response.ok) {
                // Try comprehensive-search with JSON
                const headers = {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                };
                
                if (csrfToken) {
                    headers['X-CSRFToken'] = csrfToken;
                }
                
                const jsonResponse = await fetch('/api/comprehensive-search', {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: headers,
                    body: JSON.stringify({
                        query: query,
                        sources: selectedSources,
                        limit: 50,
                        safe_search: true
                    })
                });
                
                if (jsonResponse.ok) {
                    const data = await jsonResponse.json();
                    this.handleSearchResponse(data);
                } else {
                    // Try without CSRF as a last resort (development mode)
                    const devResponse = await fetch('/api/bulletproof-search', {
                        method: 'POST',
                        credentials: 'same-origin',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({
                            query: query,
                            sources: selectedSources,
                            limit: 50,
                            safe_search: true
                        })
                    });
                    
                    if (devResponse.ok) {
                        const data = await devResponse.json();
                        this.handleSearchResponse(data);
                    } else {
                        throw new Error(`Search failed: ${devResponse.statusText}`);
                    }
                }
            } else {
                const data = await response.json();
                this.handleSearchResponse(data);
            }
            
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed: ' + error.message);
            this.isSearching = false;
        }
    }

    handleSearchResponse(data) {
        if (data.job_id) {
            // Async search with job ID
            this.currentJobId = data.job_id;
            this.monitorProgress(data.job_id);
        } else if (data.results) {
            // Direct results
            this.displayResults(data.results);
            this.isSearching = false;
        } else {
            this.showError('Unexpected response format');
            this.isSearching = false;
        }
    }

    async monitorProgress(jobId) {
        const progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/job-progress/${jobId}`);
                const data = await response.json();
                
                if (data.status === 'completed') {
                    clearInterval(progressInterval);
                    this.displayResults(data.results || []);
                    this.isSearching = false;
                } else if (data.status === 'failed') {
                    clearInterval(progressInterval);
                    this.showError('Search failed: ' + (data.error || 'Unknown error'));
                    this.isSearching = false;
                } else {
                    const progress = data.progress || 0;
                    this.updateProgress(progress, data.status);
                }
            } catch (error) {
                console.error('Progress monitoring error:', error);
                clearInterval(progressInterval);
                this.isSearching = false;
            }
        }, 2000);
        
        // Stop monitoring after 60 seconds
        setTimeout(() => {
            clearInterval(progressInterval);
            if (this.isSearching) {
                this.showError('Search timeout - took too long');
                this.isSearching = false;
            }
        }, 60000);
    }

    displayResults(results) {
        const container = document.getElementById('search-results');
        if (!container) {
            console.error('Search results container not found');
            return;
        }
        
        if (!results || results.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> No results found. Try different keywords or sources.
                </div>
            `;
            return;
        }
        
        // Create results grid
        const grid = document.createElement('div');
        grid.className = 'row g-3';
        
        results.forEach((result, index) => {
            const col = document.createElement('div');
            col.className = 'col-sm-6 col-md-4 col-lg-3';
            
            const card = document.createElement('div');
            card.className = 'result-card';
            card.style.cssText = `
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.2s;
                cursor: pointer;
                height: 100%;
            `;
            
            // Thumbnail
            const thumbnail = document.createElement('div');
            thumbnail.style.cssText = `
                height: 200px;
                background: #f0f0f0;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            
            if (result.thumbnail || result.url) {
                const img = document.createElement('img');
                img.src = result.thumbnail || result.url;
                img.style.cssText = 'width: 100%; height: 100%; object-fit: cover;';
                img.onerror = () => {
                    img.remove();
                    thumbnail.innerHTML = '<i class="fas fa-image fa-3x text-muted"></i>';
                };
                thumbnail.appendChild(img);
            } else {
                thumbnail.innerHTML = '<i class="fas fa-image fa-3x text-muted"></i>';
            }
            
            // Info
            const info = document.createElement('div');
            info.style.cssText = 'padding: 15px;';
            
            const title = document.createElement('h6');
            title.style.cssText = 'margin: 0 0 5px 0; font-size: 0.9rem;';
            title.textContent = result.title || `Result ${index + 1}`;
            
            const source = document.createElement('div');
            source.style.cssText = 'font-size: 0.8rem; color: #666;';
            source.textContent = result.source || 'Unknown source';
            
            // Actions
            const actions = document.createElement('div');
            actions.style.cssText = 'padding: 10px 15px; background: #f8f9fa; margin-top: auto;';
            
            const downloadBtn = document.createElement('button');
            downloadBtn.className = 'btn btn-sm btn-primary w-100';
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download';
            downloadBtn.onclick = (e) => {
                e.stopPropagation();
                this.downloadResult(result);
            };
            
            actions.appendChild(downloadBtn);
            info.appendChild(title);
            info.appendChild(source);
            
            card.appendChild(thumbnail);
            card.appendChild(info);
            card.appendChild(actions);
            col.appendChild(card);
            grid.appendChild(col);
            
            // Add hover effect
            card.onmouseenter = () => card.style.transform = 'translateY(-5px)';
            card.onmouseleave = () => card.style.transform = 'translateY(0)';
        });
        
        container.innerHTML = `
            <div class="mb-3">
                <h5>Found ${results.length} results</h5>
            </div>
        `;
        container.appendChild(grid);
        
        this.hideProgress();
    }

    async downloadResult(result) {
        console.log('Downloading:', result);
        
        // Simple download using the URL
        if (result.url) {
            const link = document.createElement('a');
            link.href = result.url;
            link.download = result.title || 'download';
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    showProgress(message) {
        const container = document.getElementById('search-progress');
        if (container) {
            container.style.display = 'block';
            container.innerHTML = `
                <div class="alert alert-info">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    ${message}
                </div>
            `;
        }
    }

    updateProgress(percent, status) {
        const container = document.getElementById('search-progress');
        if (container) {
            container.innerHTML = `
                <div class="progress" style="height: 25px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" 
                         style="width: ${percent}%"
                         aria-valuenow="${percent}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        ${percent}% - ${status || 'Processing...'}
                    </div>
                </div>
            `;
        }
    }

    hideProgress() {
        const container = document.getElementById('search-progress');
        if (container) {
            container.style.display = 'none';
        }
    }

    showError(message) {
        const container = document.getElementById('search-results');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </div>
            `;
        }
        this.hideProgress();
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.searchHandler = new SearchHandler();
});
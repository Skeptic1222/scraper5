// Enhanced Media Scraper - Full Functionality
(function() {
    'use strict';
    
    // State management
    const state = {
        selectedSources: new Set(),
        currentFilter: 'all',
        allSources: {},
        assets: [],
        currentJob: null,
        searchResults: []
    };
    
    // Initialize application
    document.addEventListener('DOMContentLoaded', init);
    
    function init() {
        console.log('Initializing Enhanced Media Scraper...');
        
        // Load initial data
        loadSources();
        loadDashboardStats();
        loadAssets();
        checkAuthentication();
        
        // Setup event listeners
        setupEventListeners();
        
        // Show search section by default
        showSection('search');
    }
    
    function setupEventListeners() {
        // Search form
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', performSearch);
        }
        
        // Navigation
        document.querySelectorAll('[data-section]').forEach(btn => {
            btn.addEventListener('click', function() {
                showSection(this.dataset.section);
            });
        });
        
        // Filter buttons
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.addEventListener('click', function() {
                filterAssets(this.dataset.filter);
            });
        });
        
        // Select all/none buttons
        const selectAllBtn = document.getElementById('selectAllSources');
        const selectNoneBtn = document.getElementById('selectNoneSources');
        
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => selectAllSources());
        }
        if (selectNoneBtn) {
            selectNoneBtn.addEventListener('click', () => selectNoSources());
        }
    }
    
    // Navigation
    function showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show target section
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Update nav
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        const activeNav = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeNav) {
            activeNav.classList.add('active');
        }
        
        // Load section data
        if (sectionName === 'assets') {
            loadAssets();
        } else if (sectionName === 'dashboard') {
            loadDashboardStats();
        }
    }
    
    // Load sources from API
    async function loadSources() {
        try {
            const response = await fetch('/api/sources');
            const data = await response.json();
            
            console.log('Sources loaded:', data);
            
            const container = document.getElementById('sourceCategories');
            if (!container) return;
            
            container.innerHTML = '';
            
            // Process and categorize sources
            const categories = {};
            
            // Handle different API response formats
            let sourcesArray = [];
            if (data.sources && Array.isArray(data.sources)) {
                sourcesArray = data.sources;
            } else if (data.categories) {
                // Flatten categories into array
                Object.values(data.categories).forEach(catSources => {
                    if (Array.isArray(catSources)) {
                        sourcesArray = sourcesArray.concat(catSources);
                    }
                });
            }
            
            // Categorize sources
            sourcesArray.forEach(source => {
                if (!source || !source.id) return;
                
                const category = source.category || 'Other';
                if (!categories[category]) {
                    categories[category] = [];
                }
                categories[category].push(source);
                state.allSources[source.id] = source;
            });
            
            // Render categories
            Object.entries(categories).forEach(([categoryName, sources]) => {
                const categoryDiv = document.createElement('div');
                categoryDiv.className = 'source-category';
                
                const categoryHTML = `
                    <h5>${categoryName} (${sources.length})</h5>
                    <div class="source-grid">
                        ${sources.map(source => `
                            <div class="source-item" 
                                 data-source-id="${source.id}" 
                                 onclick="window.toggleSource('${source.id}')">
                                <i class="fas ${getSourceIcon(source.category)}"></i>
                                <div>${source.name}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
                
                categoryDiv.innerHTML = categoryHTML;
                container.appendChild(categoryDiv);
            });
            
            // Select default sources
            const defaultSources = ['google_images', 'bing_images', 'unsplash', 'pixabay'];
            defaultSources.forEach(id => {
                if (state.allSources[id]) {
                    state.selectedSources.add(id);
                    const element = document.querySelector(`[data-source-id="${id}"]`);
                    if (element) element.classList.add('selected');
                }
            });
            
        } catch (error) {
            console.error('Error loading sources:', error);
            const container = document.getElementById('sourceCategories');
            if (container) {
                container.innerHTML = '<div class="alert alert-warning">Failed to load sources. Using defaults.</div>';
            }
        }
    }
    
    // Toggle source selection
    window.toggleSource = function(sourceId) {
        if (state.selectedSources.has(sourceId)) {
            state.selectedSources.delete(sourceId);
        } else {
            state.selectedSources.add(sourceId);
        }
        
        const element = document.querySelector(`[data-source-id="${sourceId}"]`);
        if (element) {
            element.classList.toggle('selected');
        }
        
        updateSelectedCount();
    };
    
    function selectAllSources() {
        document.querySelectorAll('.source-item').forEach(element => {
            const sourceId = element.dataset.sourceId;
            if (sourceId) {
                state.selectedSources.add(sourceId);
                element.classList.add('selected');
            }
        });
        updateSelectedCount();
    }
    
    function selectNoSources() {
        state.selectedSources.clear();
        document.querySelectorAll('.source-item').forEach(element => {
            element.classList.remove('selected');
        });
        updateSelectedCount();
    }
    
    function updateSelectedCount() {
        const countElement = document.getElementById('selectedCount');
        if (countElement) {
            countElement.textContent = `${state.selectedSources.size} sources selected`;
        }
    }
    
    // Perform search
    async function performSearch(event) {
        event.preventDefault();
        
        const query = document.getElementById('searchInput').value.trim();
        if (!query) {
            alert('Please enter a search query');
            return;
        }
        
        const sources = Array.from(state.selectedSources);
        if (sources.length === 0) {
            alert('Please select at least one source');
            return;
        }
        
        const searchBtn = document.querySelector('#searchForm button[type="submit"]');
        const spinner = document.getElementById('searchSpinner');
        const results = document.getElementById('searchResults');
        
        // Show loading state
        if (searchBtn) searchBtn.disabled = true;
        if (spinner) spinner.classList.add('active');
        if (results) results.innerHTML = '';
        
        try {
            // Start bulletproof search
            const response = await fetch('/api/bulletproof-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    sources: sources,
                    limit: 50,
                    safe_search: document.getElementById('safeSearchToggle')?.checked !== false
                })
            });
            
            const data = await response.json();
            
            if (data.job_id) {
                state.currentJob = data.job_id;
                monitorJobProgress(data.job_id);
            } else if (data.results) {
                displaySearchResults(data.results);
            } else {
                throw new Error('Invalid response from search API');
            }
            
        } catch (error) {
            console.error('Search error:', error);
            if (spinner) spinner.classList.remove('active');
            if (results) {
                results.innerHTML = '<div class="alert alert-danger">Search failed. Please try again.</div>';
            }
        } finally {
            if (searchBtn) searchBtn.disabled = false;
        }
    }
    
    // Monitor job progress
    async function monitorJobProgress(jobId) {
        const progressBar = document.getElementById('searchProgress');
        const spinner = document.getElementById('searchSpinner');
        
        const checkProgress = async () => {
            try {
                const response = await fetch(`/api/job-progress/${jobId}`);
                const data = await response.json();
                
                if (progressBar) {
                    progressBar.style.width = `${data.progress || 0}%`;
                }
                
                if (data.status === 'completed') {
                    if (spinner) spinner.classList.remove('active');
                    displaySearchResults(data.results || []);
                    state.currentJob = null;
                } else if (data.status === 'failed') {
                    if (spinner) spinner.classList.remove('active');
                    document.getElementById('searchResults').innerHTML = 
                        '<div class="alert alert-danger">Search failed. Please try again.</div>';
                    state.currentJob = null;
                } else {
                    // Continue monitoring
                    setTimeout(checkProgress, 1000);
                }
                
            } catch (error) {
                console.error('Error checking job progress:', error);
                if (spinner) spinner.classList.remove('active');
            }
        };
        
        checkProgress();
    }
    
    // Display search results
    function displaySearchResults(results) {
        const container = document.getElementById('searchResults');
        if (!container) return;
        
        state.searchResults = results;
        
        if (!results || results.length === 0) {
            container.innerHTML = '<div class="alert alert-info">No results found. Try different keywords or sources.</div>';
            return;
        }
        
        const resultsHTML = `
            <h4>Found ${results.length} results</h4>
            <div class="mb-3">
                <button class="btn btn-success" onclick="downloadAllResults()">
                    <i class="fas fa-download"></i> Download All
                </button>
            </div>
            <div class="row g-3">
                ${results.map((result, index) => `
                    <div class="col-md-3">
                        <div class="card result-card">
                            <img src="${result.thumbnail || result.url || '/static/placeholder.jpg'}" 
                                 class="card-img-top" 
                                 alt="${result.title || 'Image'}"
                                 onerror="this.src='/static/placeholder.jpg'">
                            <div class="card-body">
                                <p class="card-text small">${result.title || 'Untitled'}</p>
                                <div class="text-muted small">${result.source || ''}</div>
                                <button class="btn btn-sm btn-primary mt-2" 
                                        onclick="downloadAsset('${result.url}', ${index})">
                                    <i class="fas fa-download"></i> Download
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = resultsHTML;
    }
    
    // Download asset
    window.downloadAsset = async function(url, index) {
        try {
            const response = await fetch('/api/download-asset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    metadata: state.searchResults[index] || {}
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Download started successfully!');
                // Refresh assets if on assets page
                if (document.getElementById('assets').classList.contains('active')) {
                    loadAssets();
                }
            } else {
                alert('Download failed: ' + (data.error || 'Unknown error'));
            }
            
        } catch (error) {
            console.error('Download error:', error);
            alert('Failed to start download');
        }
    };
    
    // Load dashboard statistics
    async function loadDashboardStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            // Update stat cards
            updateStatCard('totalAssets', stats.total_assets || 0);
            updateStatCard('recentDownloads', stats.recent_downloads || 0);
            updateStatCard('activeJobs', stats.active_jobs || 0);
            updateStatCard('storageUsed', `${(stats.storage_mb || 0).toFixed(2)} MB`);
            
            // Update recent activity
            updateRecentActivity(stats.recent_activity || []);
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    function updateStatCard(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    function updateRecentActivity(activities) {
        const container = document.getElementById('recentActivity');
        if (!container) return;
        
        if (activities.length === 0) {
            container.innerHTML = '<p class="text-muted">No recent activity</p>';
            return;
        }
        
        const activityHTML = activities.map(activity => `
            <div class="activity-item">
                <i class="fas ${getActivityIcon(activity.type)}"></i>
                <span>${activity.description}</span>
                <small class="text-muted">${formatTime(activity.timestamp)}</small>
            </div>
        `).join('');
        
        container.innerHTML = activityHTML;
    }
    
    // Load assets
    async function loadAssets() {
        const spinner = document.getElementById('assetsSpinner');
        const grid = document.getElementById('assetsGrid');
        
        if (spinner) spinner.classList.add('active');
        
        try {
            const response = await fetch('/api/assets');
            const data = await response.json();
            
            if (spinner) spinner.classList.remove('active');
            
            state.assets = data.assets || data || [];
            displayAssets(state.assets);
            
        } catch (error) {
            console.error('Error loading assets:', error);
            if (spinner) spinner.classList.remove('active');
            if (grid) {
                grid.innerHTML = '<div class="alert alert-danger">Failed to load assets.</div>';
            }
        }
    }
    
    // Display assets
    function displayAssets(assets) {
        const grid = document.getElementById('assetsGrid');
        if (!grid) return;
        
        if (!assets || assets.length === 0) {
            grid.innerHTML = '<div class="col-12"><div class="alert alert-info">No assets yet. Start searching and downloading media!</div></div>';
            return;
        }
        
        const filteredAssets = state.currentFilter === 'all' 
            ? assets 
            : assets.filter(asset => {
                const type = getAssetType(asset);
                return type === state.currentFilter;
            });
        
        const assetsHTML = filteredAssets.map(asset => `
            <div class="asset-card" data-asset-id="${asset.id}">
                <img src="/api/media/${asset.id}/thumbnail" 
                     class="asset-thumbnail" 
                     alt="${asset.name || asset.filename || 'Asset'}"
                     onerror="this.src='/static/placeholder.jpg'">
                <div class="asset-info">
                    <h6>${asset.name || asset.filename || 'Untitled'}</h6>
                    <small class="text-muted">
                        ${formatFileSize(asset.size || asset.file_size || 0)}
                        • ${asset.mime_type || asset.content_type || 'Unknown'}
                    </small>
                    <div class="asset-actions mt-2">
                        <button class="btn btn-sm btn-primary" onclick="viewAsset(${asset.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-success" onclick="downloadAssetById(${asset.id})">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteAsset(${asset.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        grid.innerHTML = assetsHTML || '<div class="col-12">No assets match the current filter.</div>';
    }
    
    // Filter assets
    window.filterAssets = function(type) {
        state.currentFilter = type;
        
        // Update button states
        document.querySelectorAll('[data-filter]').forEach(btn => {
            if (btn.dataset.filter === type) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
        
        displayAssets(state.assets);
    };
    
    // View asset
    window.viewAsset = function(id) {
        window.open(`/api/media/${id}`, '_blank');
    };
    
    // Download asset by ID
    window.downloadAssetById = function(id) {
        window.location.href = `/api/media/${id}/download`;
    };
    
    // Delete asset
    window.deleteAsset = async function(id) {
        if (!confirm('Are you sure you want to delete this asset?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/assets/${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert('Asset deleted successfully');
                loadAssets();
            } else {
                alert('Failed to delete asset');
            }
        } catch (error) {
            console.error('Delete error:', error);
            alert('Failed to delete asset');
        }
    };
    
    // Check authentication
    async function checkAuthentication() {
        try {
            const response = await fetch('/auth/check');
            const data = await response.json();
            
            const userDisplay = document.getElementById('userDisplay');
            if (userDisplay) {
                if (data.authenticated) {
                    userDisplay.innerHTML = `
                        <div><i class="fas fa-user"></i> ${data.user?.email || 'User'}</div>
                        <small>${data.user?.is_admin ? 'Admin' : 'Member'}</small>
                    `;
                } else {
                    userDisplay.innerHTML = `
                        <div><i class="fas fa-user"></i> Guest User</div>
                        <small>Limited Access</small>
                    `;
                }
            }
        } catch (error) {
            console.error('Auth check error:', error);
        }
    }
    
    // Helper functions
    function getSourceIcon(category) {
        const icons = {
            'search': 'fa-search',
            'social': 'fa-users',
            'photos': 'fa-image',
            'videos': 'fa-video',
            'art': 'fa-palette',
            'adult': 'fa-exclamation-triangle'
        };
        return icons[category] || 'fa-globe';
    }
    
    function getActivityIcon(type) {
        const icons = {
            'download': 'fa-download',
            'search': 'fa-search',
            'upload': 'fa-upload',
            'delete': 'fa-trash'
        };
        return icons[type] || 'fa-circle';
    }
    
    function getAssetType(asset) {
        const mimeType = asset.mime_type || asset.content_type || '';
        if (mimeType.startsWith('image/')) return 'images';
        if (mimeType.startsWith('video/')) return 'videos';
        if (mimeType.startsWith('application/')) return 'documents';
        return 'other';
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    function formatTime(timestamp) {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return Math.floor(diff / 60000) + ' min ago';
        if (diff < 86400000) return Math.floor(diff / 3600000) + ' hours ago';
        return date.toLocaleDateString();
    }
    
    // Expose necessary functions to global scope
    window.showSection = showSection;
    window.performSearch = performSearch;
    
})();
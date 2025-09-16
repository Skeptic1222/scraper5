/**
 * ============================================================================
 * ENHANCED MEDIA SCRAPER APPLICATION
 * ============================================================================
 * 
 * Comprehensive UI and functionality enhancements
 */

class EnhancedMediaScraperApp {
    constructor() {
        this.state = {
            currentSection: 'dashboard',
            selectedAssets: new Set(),
            bandwidthData: [],
            activityFeed: [],
            currentJob: null,
            retryAttempts: new Map()
        };
        
        this.config = {
            maxRetries: 3,
            retryDelay: 2000,
            bandwidthSamples: 50,
            activityMaxItems: 100
        };
        
        this.intervals = {
            dashboard: null,
            bandwidth: null,
            activity: null
        };
        
        this.bind();
    }
    
    bind() {
        this.updateDashboard = this.updateDashboard.bind(this);
        this.handleAdvancedSearch = this.handleAdvancedSearch.bind(this);
        this.handleAssetSelection = this.handleAssetSelection.bind(this);
        this.addActivity = this.addActivity.bind(this);
    }
    
    /**
     * Initialize enhanced application
     */
    async init() {
        console.log('🚀 Initializing Enhanced Media Scraper...');
        
        try {
            // Set up enhanced UI handlers
            this.setupAdvancedFilters();
            this.setupAssetManagement();
            this.setupDashboardUpdates();
            this.setupAIAssistant();
            this.setupKeyboardShortcuts();
            
            // Load initial data
            await this.loadInitialData();
            
            console.log('✅ Enhanced application initialized');
        } catch (error) {
            console.error('❌ Enhanced initialization failed:', error);
            this.showToast('Failed to initialize enhanced features', 'danger');
        }
    }
    
    /**
     * Set up advanced filter handling
     */
    setupAdvancedFilters() {
        // Advanced filter toggles
        document.querySelectorAll('[id^="enable-"]').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const targetId = e.target.id.replace('enable-', '') + '-filters';
                const target = document.getElementById(targetId) || 
                              document.getElementById(e.target.id.replace('enable-', '') + '-filter-inputs');
                if (target) {
                    target.style.display = e.target.checked ? 'block' : 'none';
                }
            });
        });
        
        // Enhanced search form submission
        const searchForm = document.getElementById('search-form');
        if (searchForm) {
            searchForm.addEventListener('submit', this.handleAdvancedSearch);
        }
    }
    
    /**
     * Handle advanced search with all filters
     */
    async handleAdvancedSearch(e) {
        e.preventDefault();
        
        const formData = this.gatherSearchData();
        console.log('🔍 Starting advanced search:', formData);
        
        try {
            const response = await this.submitSearchWithRetry(formData);
            
            if (response.success) {
                this.currentJob = response.job_id;
                this.showToast(`Search started! Job ID: ${response.job_id}`, 'success');
                this.addActivity('Search started', 'info', `Query: "${formData.query}"`);
                
                // Switch to dashboard and start monitoring
                this.showSection('dashboard');
                this.startJobMonitoring(response.job_id);
            } else {
                throw new Error(response.error || 'Search failed');
            }
        } catch (error) {
            console.error('Search failed:', error);
            this.showToast(`Search failed: ${error.message}`, 'danger');
            this.addActivity('Search failed', 'error', error.message);
        }
    }
    
    /**
     * Gather comprehensive search data including advanced filters
     */
    gatherSearchData() {
        const query = document.getElementById('search-query')?.value?.trim();
        
        // Basic data
        const searchData = {
            query: query,
            search_type: 'comprehensive',
            max_content: parseInt(document.getElementById('max-items')?.value || '25'),
            safe_search: document.getElementById('safe-search-toggle')?.checked !== false,
            prevent_duplicates: document.getElementById('prevent-duplicates')?.checked !== false,
            quality: document.getElementById('download-quality')?.value || 'medium'
        };
        
        // Content types
        searchData.content_types = [];
        if (document.getElementById('content-images')?.checked) searchData.content_types.push('images');
        if (document.getElementById('content-videos')?.checked) searchData.content_types.push('videos');
        if (document.getElementById('content-audio')?.checked) searchData.content_types.push('audio');
        
        // Advanced filters
        searchData.filters = {
            include_keywords: this.parseKeywords(document.getElementById('include-keywords')?.value),
            exclude_keywords: this.parseKeywords(document.getElementById('exclude-keywords')?.value)
        };
        
        // Size filters
        if (document.getElementById('enable-image-size-filter')?.checked) {
            searchData.filters.image_size = {
                min: this.convertToBytes(
                    document.getElementById('min-image-size')?.value,
                    document.getElementById('min-image-unit')?.value
                ),
                max: this.convertToBytes(
                    document.getElementById('max-image-size')?.value,
                    document.getElementById('max-image-unit')?.value
                )
            };
        }
        
        if (document.getElementById('enable-video-size-filter')?.checked) {
            searchData.filters.video_size = {
                min: this.convertToBytes(
                    document.getElementById('min-video-size')?.value,
                    document.getElementById('min-video-unit')?.value
                ),
                max: this.convertToBytes(
                    document.getElementById('max-video-size')?.value,
                    document.getElementById('max-video-unit')?.value
                )
            };
        }
        
        if (document.getElementById('enable-audio-size-filter')?.checked) {
            searchData.filters.audio_size = {
                min: this.convertToBytes(
                    document.getElementById('min-audio-size')?.value,
                    document.getElementById('min-audio-unit')?.value
                ),
                max: this.convertToBytes(
                    document.getElementById('max-audio-size')?.value,
                    document.getElementById('max-audio-unit')?.value
                )
            };
        }
        
        // Duration filters
        if (document.getElementById('enable-duration-filter')?.checked) {
            searchData.filters.duration = {
                min: parseInt(document.getElementById('min-duration')?.value || '0'),
                max: parseInt(document.getElementById('max-duration')?.value || '0')
            };
        }
        
        // Resolution filters
        if (document.getElementById('enable-resolution-filter')?.checked) {
            searchData.filters.min_resolution = document.getElementById('min-resolution')?.value;
        }
        
        // Selected sources
        searchData.enabled_sources = [];
        document.querySelectorAll('.source-checkbox:checked').forEach(cb => {
            searchData.enabled_sources.push(cb.value);
        });
        
        // Default sources if none selected
        if (searchData.enabled_sources.length === 0) {
            searchData.enabled_sources = ['google_images', 'bing_images', 'reddit', 'imgur', 'youtube'];
        }
        
        return searchData;
    }
    
    /**
     * Submit search with retry logic
     */
    async submitSearchWithRetry(searchData, attempt = 1) {
        try {
            const response = await fetch('/api/comprehensive-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (!result.success && attempt < this.config.maxRetries) {
                console.warn(`Search attempt ${attempt} failed, retrying...`);
                await this.delay(this.config.retryDelay * attempt);
                return this.submitSearchWithRetry(searchData, attempt + 1);
            }
            
            return result;
        } catch (error) {
            if (attempt < this.config.maxRetries) {
                console.warn(`Search attempt ${attempt} failed with error, retrying...`, error);
                await this.delay(this.config.retryDelay * attempt);
                return this.submitSearchWithRetry(searchData, attempt + 1);
            }
            throw error;
        }
    }
    
    /**
     * Set up enhanced asset management
     */
    setupAssetManagement() {
        // Select all functionality
        const selectAllCheckbox = document.getElementById('select-all-assets');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                const checkboxes = document.querySelectorAll('.asset-checkbox');
                checkboxes.forEach(cb => {
                    cb.checked = e.target.checked;
                    if (e.target.checked) {
                        this.state.selectedAssets.add(cb.value);
                    } else {
                        this.state.selectedAssets.delete(cb.value);
                    }
                });
                this.updateSelectionUI();
            });
        }
        
        // Individual asset selection
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('asset-checkbox')) {
                this.handleAssetSelection(e);
            }
        });
        
        // Bulk operations
        document.getElementById('delete-selected-btn')?.addEventListener('click', () => {
            this.deleteSelectedAssets();
        });
        
        document.getElementById('bulk-download-btn')?.addEventListener('click', () => {
            this.downloadSelectedAssets();
        });
        
        // Asset filters
        document.querySelectorAll('input[name="asset-filter"]').forEach(radio => {
            radio.addEventListener('change', this.filterAssets.bind(this));
        });
    }
    
    /**
     * Handle individual asset selection
     */
    handleAssetSelection(e) {
        const assetId = e.target.value;
        
        if (e.target.checked) {
            this.state.selectedAssets.add(assetId);
        } else {
            this.state.selectedAssets.delete(assetId);
        }
        
        this.updateSelectionUI();
    }
    
    /**
     * Update selection UI elements
     */
    updateSelectionUI() {
        const count = this.state.selectedAssets.size;
        
        // Update counters
        document.getElementById('selected-count').textContent = count;
        document.getElementById('delete-selected-count').textContent = count;
        
        // Toggle bulk action buttons
        const deleteBtn = document.getElementById('delete-selected-btn');
        const downloadBtn = document.getElementById('bulk-download-btn');
        
        if (count > 0) {
            deleteBtn.style.display = 'inline-block';
            downloadBtn.style.display = 'inline-block';
        } else {
            deleteBtn.style.display = 'none';
            downloadBtn.style.display = 'none';
        }
        
        // Update select all checkbox
        const selectAll = document.getElementById('select-all-assets');
        const totalCheckboxes = document.querySelectorAll('.asset-checkbox').length;
        
        if (selectAll) {
            selectAll.indeterminate = count > 0 && count < totalCheckboxes;
            selectAll.checked = count === totalCheckboxes && totalCheckboxes > 0;
        }
    }
    
    /**
     * Delete selected assets
     */
    async deleteSelectedAssets() {
        if (this.state.selectedAssets.size === 0) return;
        
        const confirmMsg = `Delete ${this.state.selectedAssets.size} selected assets? This cannot be undone.`;
        if (!confirm(confirmMsg)) return;
        
        const assetIds = Array.from(this.state.selectedAssets);
        
        try {
            const deletePromises = assetIds.map(id => this.deleteAssetWithRetry(id));
            const results = await Promise.allSettled(deletePromises);
            
            const successCount = results.filter(r => r.status === 'fulfilled').length;
            const failCount = results.length - successCount;
            
            if (successCount > 0) {
                this.showToast(`Deleted ${successCount} assets successfully`, 'success');
                this.addActivity(`Deleted ${successCount} assets`, 'success');
            }
            
            if (failCount > 0) {
                this.showToast(`Failed to delete ${failCount} assets`, 'warning');
            }
            
            // Refresh assets and clear selection
            this.state.selectedAssets.clear();
            this.loadAssets();
            this.updateSelectionUI();
            
        } catch (error) {
            console.error('Bulk delete failed:', error);
            this.showToast('Failed to delete assets', 'danger');
        }
    }
    
    /**
     * Delete single asset with retry
     */
    async deleteAssetWithRetry(assetId, attempt = 1) {
        try {
            const response = await fetch(`/api/assets/${assetId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            if (!result.success && attempt < this.config.maxRetries) {
                await this.delay(this.config.retryDelay);
                return this.deleteAssetWithRetry(assetId, attempt + 1);
            }
            
            return result;
        } catch (error) {
            if (attempt < this.config.maxRetries) {
                await this.delay(this.config.retryDelay);
                return this.deleteAssetWithRetry(assetId, attempt + 1);
            }
            throw error;
        }
    }
    
    /**
     * Set up dashboard real-time updates
     */
    setupDashboardUpdates() {
        // Only run dashboard updates on dashboard page
        if (this.state.currentSection === 'dashboard') {
            this.startDashboardMonitoring();
        }
    }
    
    /**
     * Start dashboard monitoring
     */
    startDashboardMonitoring() {
        // Clear existing intervals
        Object.values(this.intervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });
        
        // Update dashboard stats every 5 seconds
        this.intervals.dashboard = setInterval(this.updateDashboard, 5000);
        
        // Update bandwidth chart every 2 seconds
        this.intervals.bandwidth = setInterval(() => {
            this.updateBandwidthChart();
        }, 2000);
        
        // Initial updates
        this.updateDashboard();
        this.updateBandwidthChart();
    }
    
    /**
     * Stop dashboard monitoring
     */
    stopDashboardMonitoring() {
        Object.values(this.intervals).forEach(interval => {
            if (interval) clearInterval(interval);
        });
    }
    
    /**
     * Update dashboard with real-time data
     */
    async updateDashboard() {
        try {
            const [statsResponse, jobResponse] = await Promise.allSettled([
                fetch('/api/stats'),
                this.currentJob ? fetch(`/api/job-status/${this.currentJob}`) : Promise.resolve(null)
            ]);
            
            // Update general stats
            if (statsResponse.status === 'fulfilled') {
                const stats = await statsResponse.value.json();
                if (stats.success) {
                    this.updateStatistics(stats);
                }
            }
            
            // Update job progress
            if (jobResponse.status === 'fulfilled' && jobResponse.value) {
                const jobData = await jobResponse.value.json();
                if (jobData.success) {
                    this.updateJobProgress(jobData.job);
                }
            }
            
        } catch (error) {
            console.error('Dashboard update failed:', error);
        }
    }
    
    /**
     * Update statistics display
     */
    updateStatistics(stats) {
        // Update main stats
        document.getElementById('total-downloads').textContent = stats.total_downloads || 0;
        document.getElementById('total-images').textContent = stats.total_images || 0;
        document.getElementById('total-videos').textContent = stats.total_videos || 0;
        document.getElementById('total-audio').textContent = stats.total_audio || 0;
        document.getElementById('total-size').textContent = this.formatFileSize(stats.total_size || 0);
        document.getElementById('success-rate').textContent = (stats.success_rate || 0).toFixed(1) + '%';
        
        // Update change indicators
        document.getElementById('downloads-change').textContent = `+${stats.downloads_today || 0} today`;
        document.getElementById('images-change').textContent = `+${stats.images_today || 0} today`;
        document.getElementById('videos-change').textContent = `+${stats.videos_today || 0} today`;
        document.getElementById('audio-change').textContent = `+${stats.audio_today || 0} today`;
        document.getElementById('size-change').textContent = `+${this.formatFileSize(stats.size_today || 0)} today`;
    }
    
    /**
     * Update job progress
     */
    updateJobProgress(job) {
        // Update progress bar
        const progress = job.progress || 0;
        const progressFill = document.getElementById('live-progress-fill');
        const progressText = document.getElementById('live-progress-text');
        
        if (progressFill) {
            progressFill.style.width = progress + '%';
        }
        if (progressText) {
            progressText.textContent = progress.toFixed(1) + '%';
        }
        
        // Update metrics
        document.getElementById('live-detected').textContent = job.detected || 0;
        document.getElementById('live-downloaded').textContent = job.downloaded || 0;
        document.getElementById('detection-rate').textContent = `${job.detection_rate || 0}/min`;
        document.getElementById('download-rate').textContent = `${job.download_rate || 0}/min`;
        document.getElementById('live-bandwidth').textContent = this.formatSpeed(job.current_speed || 0);
        document.getElementById('bandwidth-trend').textContent = job.bandwidth_trend || 'Stable';
        
        // Update job info
        document.getElementById('current-job-info').textContent = 
            job.status === 'running' ? `Downloading: ${job.current_source || 'Unknown'}` : 
            job.status || 'No active downloads';
        
        // Show/hide controls based on job status
        const pauseBtn = document.getElementById('pause-downloads');
        const stopBtn = document.getElementById('stop-downloads');
        
        if (job.status === 'running') {
            if (pauseBtn) pauseBtn.style.display = 'inline-block';
            if (stopBtn) stopBtn.style.display = 'inline-block';
        } else {
            if (pauseBtn) pauseBtn.style.display = 'none';
            if (stopBtn) stopBtn.style.display = 'none';
        }
        
        // Add activity for significant events
        if (job.last_event && job.last_event !== this.lastJobEvent) {
            this.addActivity(job.last_event.type, job.last_event.level, job.last_event.message);
            this.lastJobEvent = job.last_event;
        }
    }
    
    /**
     * Update bandwidth chart
     */
    updateBandwidthChart() {
        // Simulate or fetch real bandwidth data
        const now = Date.now();
        const speed = Math.random() * 1000 + 100; // Simulate speed in KB/s
        
        this.state.bandwidthData.push({ time: now, speed });
        
        // Keep only recent samples
        if (this.state.bandwidthData.length > this.config.bandwidthSamples) {
            this.state.bandwidthData.shift();
        }
        
        this.drawBandwidthChart();
    }
    
    /**
     * Draw bandwidth chart on canvas
     */
    drawBandwidthChart() {
        const canvas = document.getElementById('bandwidth-canvas');
        if (!canvas || this.state.bandwidthData.length < 2) return;
        
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Find max speed for scaling
        const maxSpeed = Math.max(...this.state.bandwidthData.map(d => d.speed));
        const scale = height / (maxSpeed * 1.1);
        
        // Draw line
        ctx.strokeStyle = '#4A5FDB';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        this.state.bandwidthData.forEach((point, index) => {
            const x = (index / (this.state.bandwidthData.length - 1)) * width;
            const y = height - (point.speed * scale);
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Fill area under curve
        ctx.fillStyle = 'rgba(74, 95, 219, 0.1)';
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        ctx.fill();
    }
    
    /**
     * Add activity to feed
     */
    addActivity(message, type = 'info', details = '') {
        const activity = {
            id: Date.now(),
            message,
            type,
            details,
            time: new Date().toLocaleTimeString()
        };
        
        this.state.activityFeed.unshift(activity);
        
        // Limit feed size
        if (this.state.activityFeed.length > this.config.activityMaxItems) {
            this.state.activityFeed.pop();
        }
        
        this.updateActivityFeed();
    }
    
    /**
     * Update activity feed display
     */
    updateActivityFeed() {
        const feedBody = document.getElementById('activity-feed-body');
        if (!feedBody) return;
        
        feedBody.innerHTML = this.state.activityFeed.map(activity => `
            <div class="activity-item new">
                <div class="activity-icon ${activity.type}">
                    <i class="fas fa-${this.getActivityIcon(activity.type)}"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-message">${activity.message}</div>
                    ${activity.details ? `<div class="activity-details small text-muted">${activity.details}</div>` : ''}
                    <div class="activity-time">${activity.time}</div>
                </div>
            </div>
        `).join('');
        
        // Remove 'new' class after animation
        setTimeout(() => {
            feedBody.querySelectorAll('.activity-item.new').forEach(item => {
                item.classList.remove('new');
            });
        }, 300);
    }
    
    /**
     * Set up AI Assistant with real OpenAI integration
     */
    setupAIAssistant() {
        const aiForm = document.getElementById('ai-form');
        if (aiForm) {
            aiForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleAIQuery();
            });
        }
    }
    
    /**
     * Handle AI Assistant query
     */
    async handleAIQuery() {
        const input = document.getElementById('ai-input');
        const output = document.getElementById('ai-output');
        
        if (!input || !output) return;
        
        const query = input.value.trim();
        if (!query) return;
        
        try {
            // Show loading state
            output.innerHTML = '<div class="text-muted"><i class="fas fa-spinner fa-spin"></i> Thinking...</div>';
            
            const response = await fetch('/api/ai-assistant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query })
            });
            
            const result = await response.json();
            
            if (result.success) {
                output.innerHTML = `
                    <div class="alert alert-info">
                        <strong>AI Assistant:</strong><br>
                        ${result.response}
                    </div>
                `;
            } else {
                throw new Error(result.error || 'AI request failed');
            }
            
        } catch (error) {
            output.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error:</strong> ${error.message}
                </div>
            `;
        }
        
        input.value = '';
    }
    
    /**
     * Set up keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Only handle shortcuts when not typing in inputs
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            
            switch(e.key) {
                case '1':
                    this.showSection('dashboard');
                    break;
                case '2':
                    this.showSection('search');
                    break;
                case '3':
                    this.showSection('assets');
                    break;
                case 'Escape':
                    this.clearSelections();
                    break;
                case 'r':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.refreshCurrentSection();
                    }
                    break;
            }
        });
    }
    
    /**
     * Show section with enhanced handling
     */
    showSection(sectionName) {
        console.log('Showing section:', sectionName);
        
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
            section.style.display = 'none';
        });
        
        // Show target section
        const targetSection = document.getElementById(sectionName + '-section');
        if (targetSection) {
            targetSection.classList.add('active');
            targetSection.style.display = 'block';
            this.state.currentSection = sectionName;
            
            // Section-specific initialization
            if (sectionName === 'dashboard') {
                this.startDashboardMonitoring();
            } else {
                this.stopDashboardMonitoring();
            }
            
            if (sectionName === 'assets') {
                this.loadAssets();
            }
        }
        
        // Update navigation
        document.querySelectorAll('[data-section]').forEach(navItem => {
            navItem.classList.toggle('active', navItem.getAttribute('data-section') === sectionName);
        });
    }
    
    /**
     * Load initial data
     */
    async loadInitialData() {
        const promises = [
            this.loadSources(),
            this.loadAssets(),
            this.updateDashboard()
        ];
        
        await Promise.allSettled(promises);
    }
    
    /**
     * Utility functions
     */
    parseKeywords(input) {
        return input ? input.split(',').map(k => k.trim()).filter(k => k) : [];
    }
    
    convertToBytes(value, unit) {
        const num = parseFloat(value) || 0;
        switch(unit) {
            case 'KB': return num * 1024;
            case 'MB': return num * 1024 * 1024;
            case 'GB': return num * 1024 * 1024 * 1024;
            default: return num;
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatSpeed(bytesPerSec) {
        return this.formatFileSize(bytesPerSec) + '/s';
    }
    
    getActivityIcon(type) {
        switch(type) {
            case 'download': return 'download';
            case 'error': return 'exclamation-triangle';
            case 'success': return 'check';
            case 'info': return 'info';
            default: return 'circle';
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    showToast(message, type = 'info') {
        // Use existing toast function or create one
        if (window.showToast) {
            window.showToast(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Initialize enhanced app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        window.enhancedApp = new EnhancedMediaScraperApp();
        await window.enhancedApp.init();
        
        // Make functions globally available
        window.showSection = window.enhancedApp.showSection.bind(window.enhancedApp);
        
        console.log('✅ Enhanced Media Scraper ready');
    } catch (error) {
        console.error('❌ Enhanced app initialization failed:', error);
    }
});
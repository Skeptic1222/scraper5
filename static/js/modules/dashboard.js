/**
 * Enhanced Dashboard with Statistics and Activity
 */
class DashboardManager {
    constructor() {
        this.activeJobs = [];
        this.completedJobs = [];
        this.assets = [];
        this.metrics = {
            totalDownloads: 0,
            totalAssets: 0,
            activeJobs: 0,
            totalSources: 118,
            imageCount: 0,
            videoCount: 0,
            totalSize: 0
        };
        
        this.initialized = false;
        this.refreshInterval = null;
    }
    
    init() {
        if (this.initialized) return;
        this.initialized = true;
        
        console.log('Initializing enhanced dashboard...');
        
        // Create dashboard content first
        this.createDashboardContent();
        
        // Then load data
        this.loadData();
        this.startAutoRefresh();
    }
    
    createDashboardContent() {
        const dashboardSection = document.getElementById('dashboard');
        if (!dashboardSection) return;
        
        dashboardSection.innerHTML = `
            <div class="dashboard-container">
                <h2>Welcome to Enhanced Media Scraper</h2>
                <p class="text-muted">Your comprehensive media downloading and management platform</p>
                
                <!-- Statistics Cards -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-download"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="total-downloads">0</h3>
                            <p>Total Downloads</p>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-folder"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="total-assets">0</h3>
                            <p>Total Assets</p>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-image"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="image-count">0</h3>
                            <p>Images</p>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-video"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="video-count">0</h3>
                            <p>Videos</p>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-server"></i>
                        </div>
                        <div class="stat-content">
                            <h3 id="storage-used">0 MB</h3>
                            <p>Storage Used</p>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-icon">
                            <i class="fas fa-globe"></i>
                        </div>
                        <div class="stat-content">
                            <h3>118+</h3>
                            <p>Content Sources</p>
                        </div>
                    </div>
                </div>
                
                <!-- Active Jobs Section -->
                <div class="dashboard-section">
                    <h3><i class="fas fa-spinner"></i> Active Downloads</h3>
                    <div id="active-jobs-container" class="jobs-container">
                        <div class="empty-state">
                            <i class="fas fa-check-circle fa-3x"></i>
                            <p>No active downloads</p>
                        </div>
                    </div>
                </div>
                
                <!-- Recent Assets Section -->
                <div class="dashboard-section">
                    <h3><i class="fas fa-clock"></i> Recent Downloads</h3>
                    <div id="recent-assets-container" class="recent-assets-grid">
                        <div class="empty-state">
                            <i class="fas fa-history fa-3x"></i>
                            <p>No recent downloads</p>
                        </div>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="dashboard-section">
                    <h3><i class="fas fa-bolt"></i> Quick Actions</h3>
                    <div class="quick-actions">
                        <button class="action-btn" onclick="window.navigation.switchSection('search-download')">
                            <i class="fas fa-search"></i>
                            <span>New Search</span>
                        </button>
                        <button class="action-btn" onclick="window.navigation.switchSection('asset-library')">
                            <i class="fas fa-folder-open"></i>
                            <span>View Library</span>
                        </button>
                        <button class="action-btn" onclick="dashboard.clearCache()">
                            <i class="fas fa-broom"></i>
                            <span>Clear Cache</span>
                        </button>
                        <button class="action-btn" onclick="dashboard.exportStats()">
                            <i class="fas fa-file-export"></i>
                            <span>Export Stats</span>
                        </button>
                    </div>
                </div>
                
                <!-- System Status -->
                <div class="dashboard-section">
                    <h3><i class="fas fa-heartbeat"></i> System Status</h3>
                    <div class="system-status">
                        <div class="status-item">
                            <span class="status-indicator online"></span>
                            <span>Database Connected</span>
                        </div>
                        <div class="status-item">
                            <span class="status-indicator online"></span>
                            <span>118 Sources Available</span>
                        </div>
                        <div class="status-item">
                            <span class="status-indicator online"></span>
                            <span>API Services Active</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add dashboard-specific styles
        this.addDashboardStyles();
    }
    
    addDashboardStyles() {
        if (document.getElementById('dashboard-styles')) return;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = 'dashboard-styles';
        styleSheet.textContent = `
            .dashboard-container {
                padding: 2rem;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin: 2rem 0;
            }
            
            .stat-card {
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                display: flex;
                align-items: center;
                gap: 1rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }
            
            .stat-icon {
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 1.5rem;
            }
            
            .stat-content h3 {
                margin: 0;
                font-size: 1.8rem;
                font-weight: bold;
            }
            
            .stat-content p {
                margin: 0;
                color: #6c757d;
                font-size: 0.9rem;
            }
            
            .dashboard-section {
                margin: 2rem 0;
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .dashboard-section h3 {
                margin-bottom: 1rem;
                color: #333;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .dashboard-section h3 i {
                color: #667eea;
            }
            
            .jobs-container {
                min-height: 100px;
            }
            
            .job-card {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.5rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .job-progress {
                flex: 1;
                height: 6px;
                background: #e9ecef;
                border-radius: 3px;
                margin: 0 1rem;
                overflow: hidden;
            }
            
            .job-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                transition: width 0.3s ease;
            }
            
            .recent-assets-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                gap: 0.5rem;
            }
            
            .recent-asset-thumb {
                aspect-ratio: 1/1;
                background: #f8f9fa;
                border-radius: 8px;
                overflow: hidden;
                cursor: pointer;
                transition: transform 0.3s ease;
            }
            
            .recent-asset-thumb:hover {
                transform: scale(1.05);
            }
            
            .recent-asset-thumb img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            
            .quick-actions {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }
            
            .action-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 1rem;
                cursor: pointer;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.5rem;
                transition: transform 0.3s ease;
            }
            
            .action-btn:hover {
                transform: translateY(-2px);
            }
            
            .action-btn i {
                font-size: 1.5rem;
            }
            
            .system-status {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }
            
            .status-item {
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }
            
            .status-indicator {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            .status-indicator.online {
                background: #28a745;
            }
            
            .status-indicator.offline {
                background: #dc3545;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .empty-state {
                text-align: center;
                padding: 2rem;
                color: #6c757d;
            }
            
            .empty-state i {
                margin-bottom: 0.5rem;
                opacity: 0.5;
            }
        `;
        
        document.head.appendChild(styleSheet);
    }
    
    async loadData() {
        await Promise.all([
            this.loadJobs(),
            this.loadAssets()
        ]);
        this.updateDisplay();
    }
    
    async loadJobs() {
        try {
            const response = await fetch('/api/jobs');
            const data = await response.json();
            
            if (data.jobs) {
                this.activeJobs = data.jobs.filter(job => job.status === 'running' || job.status === 'pending');
                this.completedJobs = data.jobs.filter(job => job.status === 'completed');
                
                this.metrics.activeJobs = this.activeJobs.length;
                this.metrics.totalDownloads = this.completedJobs.reduce((sum, job) => 
                    sum + (job.downloaded || 0), 0);
            }
        } catch (error) {
            console.error('Failed to load jobs:', error);
        }
    }
    
    async loadAssets() {
        try {
            const response = await fetch('/api/assets');
            const data = await response.json();
            
            if (data.assets) {
                this.assets = data.assets;
                this.metrics.totalAssets = data.assets.length;
                
                // Count by type
                this.metrics.imageCount = 0;
                this.metrics.videoCount = 0;
                this.metrics.totalSize = 0;
                
                data.assets.forEach(asset => {
                    const fileType = (asset.file_type || asset.type || '').toLowerCase();
                    if (fileType.includes('image') || fileType.includes('jpeg') || fileType.includes('png')) {
                        this.metrics.imageCount++;
                    } else if (fileType.includes('video') || fileType.includes('mp4')) {
                        this.metrics.videoCount++;
                    }
                    this.metrics.totalSize += (asset.file_size || asset.size || 0);
                });
            }
        } catch (error) {
            console.error('Failed to load assets:', error);
        }
    }
    
    updateDisplay() {
        // Update statistics
        document.getElementById('total-downloads').textContent = this.metrics.totalDownloads;
        document.getElementById('total-assets').textContent = this.metrics.totalAssets;
        document.getElementById('image-count').textContent = this.metrics.imageCount;
        document.getElementById('video-count').textContent = this.metrics.videoCount;
        document.getElementById('storage-used').textContent = this.formatSize(this.metrics.totalSize);
        
        // Update active jobs
        this.updateActiveJobs();
        
        // Update recent assets
        this.updateRecentAssets();
    }
    
    updateActiveJobs() {
        const container = document.getElementById('active-jobs-container');
        if (!container) return;
        
        if (this.activeJobs.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-check-circle fa-3x"></i>
                    <p>No active downloads</p>
                </div>
            `;
        } else {
            container.innerHTML = this.activeJobs.map(job => `
                <div class="job-card">
                    <div>
                        <strong>${job.query || 'Download'}</strong>
                        <small class="text-muted"> - ${job.downloaded || 0} files</small>
                    </div>
                    <div class="job-progress">
                        <div class="job-progress-bar" style="width: ${job.progress || 0}%"></div>
                    </div>
                    <span class="badge badge-primary">${job.status}</span>
                </div>
            `).join('');
        }
    }
    
    updateRecentAssets() {
        const container = document.getElementById('recent-assets-container');
        if (!container) return;
        
        const recentAssets = this.assets.slice(0, 12); // Show last 12 assets
        
        if (recentAssets.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history fa-3x"></i>
                    <p>No recent downloads</p>
                </div>
            `;
        } else {
            container.innerHTML = recentAssets.map((asset, index) => {
                const fileType = (asset.file_type || asset.type || '').toLowerCase();
                const isImage = fileType.includes('image') || fileType.includes('jpeg') || fileType.includes('png');
                const mediaUrl = asset.url || `/serve/${asset.id}`;
                
                if (isImage) {
                    return `
                        <div class="recent-asset-thumb" onclick="window.mediaViewer.open(window.dashboard.assets, ${index})">
                            <img src="${mediaUrl}" alt="${asset.filename || 'Asset'}">
                        </div>
                    `;
                } else {
                    return `
                        <div class="recent-asset-thumb" onclick="window.mediaViewer.open(window.dashboard.assets, ${index})">
                            <div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; background:#f8f9fa;">
                                <i class="fas fa-file fa-2x text-muted"></i>
                            </div>
                        </div>
                    `;
                }
            }).join('');
        }
    }
    
    formatSize(bytes) {
        if (bytes === 0) return '0 MB';
        const mb = bytes / (1024 * 1024);
        return mb.toFixed(2) + ' MB';
    }
    
    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Refresh every 10 seconds
        this.refreshInterval = setInterval(() => {
            this.loadData();
        }, 10000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    clearCache() {
        if (confirm('Clear all cached data?')) {
            sessionStorage.clear();
            localStorage.clear();
            alert('Cache cleared successfully!');
            location.reload();
        }
    }
    
    exportStats() {
        const stats = {
            exportDate: new Date().toISOString(),
            metrics: this.metrics,
            assets: this.assets.length,
            recentJobs: this.completedJobs.slice(0, 10)
        };
        
        const dataStr = JSON.stringify(stats, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
        
        const exportLink = document.createElement('a');
        exportLink.setAttribute('href', dataUri);
        exportLink.setAttribute('download', `scraper-stats-${Date.now()}.json`);
        exportLink.click();
    }
    
    destroy() {
        this.stopAutoRefresh();
        this.initialized = false;
    }
}

// Initialize dashboard manager
window.dashboard = new DashboardManager();
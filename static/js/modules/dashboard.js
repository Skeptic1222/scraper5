/**
 * Dashboard Manager - Shows download metrics, active jobs, and system status
 */
class DashboardManager {
    constructor() {
        this.activeJobs = [];
        this.completedJobs = [];
        this.metrics = {
            totalDownloads: 0,
            totalBytes: 0,
            activeThreads: 0,
            downloadSpeed: 0,
            queueLength: 0
        };
        
        this.init();
    }
    
    init() {
        this.loadJobs();
        this.startMetricsUpdate();
    }
    
    async loadJobs() {
        try {
            const response = await fetch('/api/jobs');
            const data = await response.json();
            
            if (data.jobs) {
                this.activeJobs = data.jobs.filter(job => job.status === 'running');
                this.completedJobs = data.jobs.filter(job => job.status === 'completed');
                this.updateDashboard();
            }
        } catch (error) {
            console.error('Failed to load jobs:', error);
        }
    }
    
    startMetricsUpdate() {
        // Update metrics every 3 seconds
        this.updateMetrics();
        setInterval(() => {
            this.updateMetrics();
            this.loadJobs();
        }, 3000);
    }
    
    async updateMetrics() {
        try {
            // Get download metrics from active jobs
            const activeCount = this.activeJobs.length;
            const totalDownloaded = this.completedJobs.reduce((sum, job) => 
                sum + (job.downloaded || 0), 0);
            
            this.metrics = {
                totalDownloads: totalDownloaded,
                totalBytes: this.formatBytes(totalDownloaded * 1024 * 1024), // Estimate
                activeThreads: activeCount * 5, // 5 threads per job
                downloadSpeed: this.calculateSpeed(),
                queueLength: this.activeJobs.length
            };
            
            this.updateMetricsDisplay();
        } catch (error) {
            console.error('Failed to update metrics:', error);
        }
    }
    
    calculateSpeed() {
        // Simulated speed calculation
        const activeJobs = this.activeJobs.length;
        if (activeJobs === 0) return '0 MB/s';
        
        const baseSpeed = 2.5; // MB/s per job
        const totalSpeed = activeJobs * baseSpeed;
        return `${totalSpeed.toFixed(1)} MB/s`;
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    updateDashboard() {
        const dashboardSection = document.querySelector('[data-section="dashboard"]');
        if (!dashboardSection) return;
        
        // Create dashboard HTML
        dashboardSection.innerHTML = `
            <div class="dashboard-container">
                <h2 class="mb-4">Dashboard</h2>
                
                <!-- Metrics Cards -->
                <div class="dashboard-metrics">
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-download"></i></div>
                        <div class="metric-value" id="metric-downloads">${this.metrics.totalDownloads}</div>
                        <div class="metric-label">Total Downloads</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-tachometer-alt"></i></div>
                        <div class="metric-value" id="metric-speed">${this.metrics.downloadSpeed}</div>
                        <div class="metric-label">Download Speed</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-layer-group"></i></div>
                        <div class="metric-value" id="metric-threads">${this.metrics.activeThreads}</div>
                        <div class="metric-label">Active Threads</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-list"></i></div>
                        <div class="metric-value" id="metric-queue">${this.metrics.queueLength}</div>
                        <div class="metric-label">Queue Length</div>
                    </div>
                </div>
                
                <!-- Active Jobs -->
                <div class="row mt-4">
                    <div class="col-lg-6">
                        <div class="active-downloads">
                            <h5><i class="fas fa-running"></i> Active Jobs</h5>
                            <div id="active-jobs-list">
                                ${this.renderActiveJobs()}
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-lg-6">
                        <div class="queue-status">
                            <h5><i class="fas fa-clock"></i> Queued Jobs</h5>
                            <div id="queue-list">
                                ${this.renderQueuedJobs()}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Download Progress -->
                <div class="mt-4">
                    <div class="active-downloads">
                        <h5><i class="fas fa-file-download"></i> Current Downloads</h5>
                        <div id="current-downloads">
                            ${this.renderCurrentDownloads()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderActiveJobs() {
        if (this.activeJobs.length === 0) {
            return '<p class="text-muted">No active jobs</p>';
        }
        
        return this.activeJobs.map(job => `
            <div class="job-status-card">
                <div class="job-header">
                    <h6>${job.query || 'Search Job'}</h6>
                    <span class="job-id">${job.id.substring(0, 8)}...</span>
                </div>
                <div class="job-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${job.progress || 0}%"></div>
                    </div>
                    <span class="progress-text">${job.progress || 0}% complete</span>
                </div>
                <div class="job-stats">
                    <span class="stat"><i class="fas fa-download"></i> ${job.downloaded || 0}</span>
                    <span class="stat"><i class="fas fa-search"></i> ${job.detected || 0}</span>
                    <span class="stat"><i class="fas fa-image"></i> ${job.images || 0}</span>
                    <span class="stat"><i class="fas fa-video"></i> ${job.videos || 0}</span>
                </div>
                <div class="job-message">${job.message || 'Processing...'}</div>
            </div>
        `).join('');
    }
    
    renderQueuedJobs() {
        const queuedJobs = this.activeJobs.filter(job => job.status === 'queued');
        
        if (queuedJobs.length === 0) {
            return '<p class="text-muted">No queued jobs</p>';
        }
        
        return queuedJobs.map((job, index) => `
            <div class="queue-item">
                <span class="queue-position">#${index + 1}</span>
                <span class="queue-query">${job.query || 'Search'}</span>
                <span class="queue-sources">${job.sources?.length || 0} sources</span>
            </div>
        `).join('');
    }
    
    renderCurrentDownloads() {
        // Simulated current downloads
        if (this.activeJobs.length === 0) {
            return '<p class="text-muted">No active downloads</p>';
        }
        
        // Create sample download items from active jobs
        const downloads = this.activeJobs.slice(0, 5).map(job => ({
            name: `image_${Math.random().toString(36).substring(7)}.jpg`,
            source: job.sources?.[0] || 'google_images',
            progress: Math.floor(Math.random() * 100)
        }));
        
        return downloads.map(dl => `
            <div class="download-item">
                <img class="download-thumbnail" src="https://via.placeholder.com/50" alt="Download">
                <div class="download-info">
                    <div class="download-name">${dl.name}</div>
                    <div class="download-source">from ${dl.source}</div>
                </div>
                <div class="download-progress">
                    <div class="download-progress-fill" style="width: ${dl.progress}%"></div>
                </div>
            </div>
        `).join('');
    }
    
    updateMetricsDisplay() {
        // Update metric values
        const elements = {
            'metric-downloads': this.metrics.totalDownloads,
            'metric-speed': this.metrics.downloadSpeed,
            'metric-threads': this.metrics.activeThreads,
            'metric-queue': this.metrics.queueLength
        };
        
        Object.keys(elements).forEach(id => {
            const elem = document.getElementById(id);
            if (elem) {
                elem.textContent = elements[id];
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on dashboard section
    const dashboardSection = document.querySelector('[data-section="dashboard"]');
    if (dashboardSection) {
        window.dashboardManager = new DashboardManager();
    }
});
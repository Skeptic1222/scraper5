/**
 * Dashboard Manager - Shows download metrics, active jobs, and system status
 */
class DashboardManager {
    constructor() {
        this.activeJobs = [];
        this.completedJobs = [];
        this.metrics = {
            totalDownloads: 0,
            totalAssets: 0,
            activeJobs: 0,
            totalSources: 118
        };
        
        this.initialized = false;
    }
    
    init() {
        if (this.initialized) return;
        this.initialized = true;
        
        console.log('Initializing dashboard...');
        
        // Set initial values immediately
        this.updateMetricCard('metric-downloads', 0);
        this.updateMetricCard('total-assets', 0);
        this.updateMetricCard('active-jobs-count', 0);
        
        // Show initial empty state
        this.showEmptyState();
        
        // Then load actual data
        this.loadData();
        this.startAutoRefresh();
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
            
            if (data.jobs && data.jobs.length > 0) {
                this.activeJobs = data.jobs.filter(job => job.status === 'running');
                this.completedJobs = data.jobs.filter(job => job.status === 'completed');
                
                // Calculate metrics
                this.metrics.activeJobs = this.activeJobs.length;
                this.metrics.totalDownloads = this.completedJobs.reduce((sum, job) => 
                    sum + (job.downloaded || 0), 0);
            } else {
                // For guest users, show cached session data if available
                const sessionJobs = JSON.parse(sessionStorage.getItem('recentJobs') || '[]');
                this.activeJobs = sessionJobs.filter(job => job.status === 'running');
                this.completedJobs = sessionJobs.filter(job => job.status === 'completed');
                
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
                this.metrics.totalAssets = data.assets.length;
            }
        } catch (error) {
            console.error('Failed to load assets:', error);
        }
    }
    
    updateDisplay() {
        // Update the metric cards
        this.updateMetricCard('metric-downloads', this.metrics.totalDownloads);
        this.updateMetricCard('total-assets', this.metrics.totalAssets);
        this.updateMetricCard('active-jobs-count', this.metrics.activeJobs);
        
        // Update dynamic content area
        this.updateDynamicContent();
    }
    
    showEmptyState() {
        const dynamicContent = document.getElementById('dashboard-dynamic-content');
        if (!dynamicContent) return;
        
        dynamicContent.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body text-center py-5">
                            <i class="fas fa-search fa-3x text-muted mb-3"></i>
                            <h5 class="text-muted">Welcome to Enhanced Media Scraper</h5>
                            <p class="text-muted mb-4">Start searching to download images and videos from 118+ sources</p>
                            <a href="#search" class="btn btn-primary">
                                <i class="fas fa-search"></i> Go to Search
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateMetricCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }
    
    updateDynamicContent() {
        const dynamicContent = document.getElementById('dashboard-dynamic-content');
        if (!dynamicContent) return;
        
        // Build the dynamic content HTML
        let html = `
            <div class="row mt-4">
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-running"></i> Active Jobs</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderActiveJobs()}
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-check-circle"></i> Recent Completions</h5>
                        </div>
                        <div class="card-body">
                            ${this.renderCompletedJobs()}
                        </div>
                    </div>
                </div>
            </div>
            
            ${this.activeJobs.length > 0 ? this.renderProgressSection() : ''}
        `;
        
        dynamicContent.innerHTML = html;
    }
    
    renderActiveJobs() {
        if (this.activeJobs.length === 0) {
            return '<p class="text-muted">No active jobs at the moment</p>';
        }
        
        return this.activeJobs.slice(0, 5).map(job => `
            <div class="mb-3 p-3 border rounded">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <strong>${job.query || 'Search Job'}</strong>
                    <small class="text-muted">#${job.id.substring(0, 8)}</small>
                </div>
                <div class="progress mb-2" style="height: 20px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" 
                         style="width: ${job.progress || 0}%"
                         aria-valuenow="${job.progress || 0}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        ${job.progress || 0}%
                    </div>
                </div>
                <div class="d-flex justify-content-between text-small">
                    <span><i class="fas fa-download"></i> ${job.downloaded || 0} files</span>
                    <span><i class="fas fa-image"></i> ${job.images || 0}</span>
                    <span><i class="fas fa-video"></i> ${job.videos || 0}</span>
                </div>
                <small class="text-muted d-block mt-2">${job.message || 'Processing...'}</small>
            </div>
        `).join('');
    }
    
    renderCompletedJobs() {
        const recentJobs = this.completedJobs.slice(0, 5);
        
        if (recentJobs.length === 0) {
            return '<p class="text-muted">No completed jobs yet</p>';
        }
        
        return recentJobs.map(job => `
            <div class="mb-2 p-2 border rounded bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <span>${job.query || 'Search'}</span>
                    <span class="badge bg-success">
                        <i class="fas fa-download"></i> ${job.downloaded || 0}
                    </span>
                </div>
                <small class="text-muted">Completed ${this.getRelativeTime(job.created_at)}</small>
            </div>
        `).join('');
    }
    
    renderProgressSection() {
        return `
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-line"></i> Download Progress</h5>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-md-3">
                                    <h4 class="text-primary">${this.calculateSpeed()}</h4>
                                    <small class="text-muted">Download Speed</small>
                                </div>
                                <div class="col-md-3">
                                    <h4 class="text-success">${this.activeJobs.length * 5}</h4>
                                    <small class="text-muted">Active Threads</small>
                                </div>
                                <div class="col-md-3">
                                    <h4 class="text-warning">${this.getTotalProgress()}%</h4>
                                    <small class="text-muted">Overall Progress</small>
                                </div>
                                <div class="col-md-3">
                                    <h4 class="text-info">${this.getEstimatedTime()}</h4>
                                    <small class="text-muted">Est. Time Remaining</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    calculateSpeed() {
        const activeCount = this.activeJobs.length;
        if (activeCount === 0) return '0 MB/s';
        const speed = activeCount * 2.5; // Estimated 2.5 MB/s per job
        return `${speed.toFixed(1)} MB/s`;
    }
    
    getTotalProgress() {
        if (this.activeJobs.length === 0) return 100;
        const totalProgress = this.activeJobs.reduce((sum, job) => 
            sum + (job.progress || 0), 0);
        return Math.round(totalProgress / this.activeJobs.length);
    }
    
    getEstimatedTime() {
        const avgProgress = this.getTotalProgress();
        if (avgProgress === 0 || avgProgress === 100) return '--:--';
        
        const remainingProgress = 100 - avgProgress;
        const estimatedMinutes = Math.round(remainingProgress / 10); // Rough estimate
        
        if (estimatedMinutes < 1) return '< 1 min';
        if (estimatedMinutes === 1) return '1 min';
        return `${estimatedMinutes} mins`;
    }
    
    getRelativeTime(dateString) {
        if (!dateString) return 'recently';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'just now';
        if (diffMins === 1) return '1 minute ago';
        if (diffMins < 60) return `${diffMins} minutes ago`;
        
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours === 1) return '1 hour ago';
        if (diffHours < 24) return `${diffHours} hours ago`;
        
        const diffDays = Math.floor(diffHours / 24);
        if (diffDays === 1) return '1 day ago';
        return `${diffDays} days ago`;
    }
    
    startAutoRefresh() {
        // Refresh every 3 seconds
        setInterval(() => {
            this.loadData();
        }, 3000);
    }
}

// Create global instance
window.dashboardManager = new DashboardManager();

// Initialize when dashboard section is shown
document.addEventListener('DOMContentLoaded', () => {
    // Check if dashboard is visible on page load
    const dashboardSection = document.getElementById('dashboard-section');
    if (dashboardSection && dashboardSection.classList.contains('active')) {
        window.dashboardManager.init();
    }
});

// Also initialize when switching to dashboard
if (window.Navigation) {
    const originalShowSection = window.Navigation.prototype.showSection;
    window.Navigation.prototype.showSection = function(sectionName) {
        originalShowSection.call(this, sectionName);
        if (sectionName === 'dashboard' && window.dashboardManager) {
            window.dashboardManager.init();
        }
    };
}
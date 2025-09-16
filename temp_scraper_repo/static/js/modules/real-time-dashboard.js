/**
 * Real-Time Dashboard Module
 * Shows live file operations, metrics, and job queue status
 */

class RealTimeDashboard {
    constructor(app) {
        this.app = app;
        this.updateInterval = null;
        this.refreshRate = 2000; // 2 seconds
        this.maxLogEntries = 50;
        this.activeJobs = new Map();
        
        this.init();
    }
    
    init() {
        console.log('🚀 Real-Time Dashboard initializing...');
        
        // Don't auto-initialize on page load - wait for explicit showDashboard call
        console.log('ℹ️ Real-Time Dashboard ready - will show when dashboard section is activated');
    }
    
    showDashboard() {
        console.log('📊 Showing Real-Time Dashboard...');
        this.createDashboardUI();
        this.startRealTimeUpdates();
    }
    
    hideDashboard() {
        console.log('🔽 Hiding Real-Time Dashboard...');
        this.stopRealTimeUpdates();
        const container = document.getElementById('real-time-dashboard');
        if (container) {
            container.remove();
        }
    }
    
    isDashboardPage() {
        // Check if we're on the dashboard section
        const dashboardSection = document.getElementById('dashboard-section');
        const isActive = dashboardSection && dashboardSection.classList.contains('active');
        const currentSection = this.app?.state?.currentSection;
        
        console.log('🔍 Dashboard page check:', {
            dashboardSection: !!dashboardSection,
            isActive,
            currentSection,
            pathname: window.location.pathname,
            search: window.location.search
        });
        
        // Only show on dashboard if explicitly requested or no section is specified
        const isOnDashboard = isActive || 
                             currentSection === 'dashboard' || 
                             (window.location.pathname === '/' && window.location.search.includes('section=dashboard')) ||
                             (window.location.pathname === '/' && !window.location.search && currentSection !== 'search' && currentSection !== 'assets' && currentSection !== 'settings');
        
        console.log('🎯 Dashboard should show:', isOnDashboard);
        return isOnDashboard;
    }
    
    createDashboardUI() {
        // Find or create dashboard container
        let container = document.getElementById('real-time-dashboard');
        if (!container) {
            container = document.createElement('div');
            container.id = 'real-time-dashboard';
            container.className = 'real-time-dashboard';
            
            // Insert at top of main content
            const mainContent = document.querySelector('.main-content') || document.body;
            mainContent.insertBefore(container, mainContent.firstChild);
        }
        
        container.innerHTML = `
            <div class="dashboard-header">
                <h3><i class="fas fa-tachometer-alt"></i> Real-Time Dashboard</h3>
                <div class="dashboard-controls">
                    <button id="dashboard-toggle" class="btn btn-sm btn-secondary">
                        <i class="fas fa-chevron-up"></i> Collapse
                    </button>
                    <button id="dashboard-refresh" class="btn btn-sm btn-primary">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
            </div>
            
            <div class="dashboard-content" id="dashboard-content">
                <!-- Metrics Row -->
                <div class="row metrics-row">
                    <div class="col-md-3">
                        <div class="metric-card">
                            <h4><i class="fas fa-download text-primary"></i> Active Downloads</h4>
                            <div class="metric-value" id="active-downloads">0</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <h4><i class="fas fa-clock text-warning"></i> Queue Length</h4>
                            <div class="metric-value" id="queue-length">0</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <h4><i class="fas fa-check-circle text-success"></i> Completed Today</h4>
                            <div class="metric-value" id="completed-today">0</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <h4><i class="fas fa-hdd text-info"></i> Total Assets</h4>
                            <div class="metric-value" id="total-assets">0</div>
                        </div>
                    </div>
                </div>
                
                <!-- Active Jobs Row -->
                <div class="row">
                    <div class="col-md-6">
                        <div class="dashboard-panel">
                            <h4><i class="fas fa-tasks"></i> Active Jobs</h4>
                            <div id="active-jobs-list" class="jobs-list">
                                <div class="no-jobs">No active jobs</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Live Activity Log -->
                    <div class="col-md-6">
                        <div class="dashboard-panel">
                            <h4><i class="fas fa-stream"></i> Live Activity</h4>
                            <div id="activity-log" class="activity-log">
                                <div class="activity-entry">
                                    <span class="timestamp">${new Date().toLocaleTimeString()}</span>
                                    <span class="message">Dashboard initialized</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- File Operations Row -->
                <div class="row">
                    <div class="col-12">
                        <div class="dashboard-panel">
                            <h4><i class="fas fa-file-alt"></i> Recent File Operations</h4>
                            <div id="file-operations" class="file-operations">
                                <div class="no-operations">No recent file operations</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
        this.addDashboardStyles();
    }
    
    addDashboardStyles() {
        if (document.getElementById('dashboard-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'dashboard-styles';
        styles.textContent = `
            .real-time-dashboard {
                background: var(--bg-secondary, #f8f9fa);
                border: 1px solid var(--border-color, #dee2e6);
                border-radius: 8px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                position: relative;
                z-index: 1;
            }
            
            .dashboard-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                background: linear-gradient(135deg, var(--primary-color, #667eea) 0%, var(--secondary-color, #764ba2) 100%);
                color: white;
                border-radius: 8px 8px 0 0;
            }
            
            .dashboard-header h3 {
                margin: 0;
                font-size: 1.2rem;
            }
            
            .dashboard-controls {
                display: flex;
                gap: 10px;
            }
            
            .dashboard-content {
                padding: 20px;
            }
            
            .metrics-row {
                margin-bottom: 20px;
            }
            
            .metric-card {
                background: var(--card-bg, white);
                color: var(--text-primary);
                padding: 15px;
                border-radius: 6px;
                border: 1px solid var(--border-color, #e9ecef);
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .metric-card h4 {
                font-size: 0.9rem;
                color: #6c757d;
                margin-bottom: 10px;
            }
            
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #495057;
            }
            
            .dashboard-panel {
                background: var(--card-bg, white);
                color: var(--text-primary);
                padding: 15px;
                border-radius: 6px;
                border: 1px solid var(--border-color, #e9ecef);
                margin-bottom: 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .dashboard-panel h4 {
                font-size: 1rem;
                color: #495057;
                margin-bottom: 15px;
                border-bottom: 1px solid #e9ecef;
                padding-bottom: 5px;
            }
            
            .jobs-list, .activity-log, .file-operations {
                max-height: 200px;
                overflow-y: auto;
            }
            
            .job-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid #f1f3f4;
            }
            
            .job-item:last-child {
                border-bottom: none;
            }
            
            .job-info {
                flex: 1;
            }
            
            .job-query {
                font-weight: 500;
                color: #495057;
            }
            
            .job-status {
                font-size: 0.8rem;
                color: #6c757d;
            }
            
            .job-progress {
                width: 100px;
                height: 6px;
                background: #e9ecef;
                border-radius: 3px;
                overflow: hidden;
                margin: 5px 0;
            }
            
            .job-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #28a745, #20c997);
                transition: width 0.3s ease;
            }
            
            .activity-entry {
                display: flex;
                align-items: center;
                padding: 4px 0;
                font-size: 0.85rem;
                border-bottom: 1px solid #f8f9fa;
            }
            
            .activity-entry:last-child {
                border-bottom: none;
            }
            
            .timestamp {
                color: #6c757d;
                margin-right: 10px;
                font-family: monospace;
                min-width: 80px;
            }
            
            .message {
                color: #495057;
            }
            
            .file-operation {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 6px 0;
                border-bottom: 1px solid #f1f3f4;
            }
            
            .file-operation:last-child {
                border-bottom: none;
            }
            
            .file-name {
                font-weight: 500;
                color: #495057;
            }
            
            .file-details {
                font-size: 0.8rem;
                color: #6c757d;
            }
            
            .operation-status {
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 0.7rem;
                font-weight: 500;
            }
            
            .status-downloading {
                background: #fff3cd;
                color: #856404;
            }
            
            .status-completed {
                background: #d4edda;
                color: #155724;
            }
            
            .status-failed {
                background: #f8d7da;
                color: #721c24;
            }
            
            .no-jobs, .no-operations {
                text-align: center;
                color: #6c757d;
                font-style: italic;
                padding: 20px;
            }
            
            .dashboard-collapsed .dashboard-content {
                display: none;
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    setupEventListeners() {
        // Toggle dashboard
        const toggleBtn = document.getElementById('dashboard-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleDashboard());
        }
        
        // Refresh dashboard
        const refreshBtn = document.getElementById('dashboard-refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshDashboard());
        }
    }
    
    toggleDashboard() {
        const dashboard = document.getElementById('real-time-dashboard');
        const toggleBtn = document.getElementById('dashboard-toggle');
        const icon = toggleBtn.querySelector('i');
        
        dashboard.classList.toggle('dashboard-collapsed');
        
        if (dashboard.classList.contains('dashboard-collapsed')) {
            icon.className = 'fas fa-chevron-down';
            toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i> Expand';
        } else {
            icon.className = 'fas fa-chevron-up';
            toggleBtn.innerHTML = '<i class="fas fa-chevron-up"></i> Collapse';
        }
    }
    
    refreshDashboard() {
        this.updateMetrics();
        this.updateActiveJobs();
        this.addActivityEntry('Dashboard refreshed manually');
    }
    
    startRealTimeUpdates() {
        this.updateInterval = setInterval(() => {
            this.updateMetrics();
            this.updateActiveJobs();
        }, this.refreshRate);
        
        console.log('📊 Real-time updates started');
    }
    
    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    async updateMetrics() {
        try {
            // Get stats from API
            const statsUrl = `${window.APP_BASE || ''}/api/stats`;
            const statsResponse = await fetch(statsUrl);
            const stats = await statsResponse.json();
            
            // Get jobs from API
            const jobsUrl = `${window.APP_BASE || ''}/api/jobs?limit=100`;
            const jobsResponse = await fetch(jobsUrl);
            const jobs = await jobsResponse.json();
            
            if (stats.success) {
                // Update metric cards (support both legacy and enhanced IDs)
                const elTotalDownloads = document.getElementById('total-downloads') || document.getElementById('total-assets');
                if (elTotalDownloads) elTotalDownloads.textContent = stats.stats.total_downloads || 0;
                const elTotalImages = document.getElementById('total-images');
                if (elTotalImages) elTotalImages.textContent = stats.stats.total_images || 0;
                const elTotalVideos = document.getElementById('total-videos');
                if (elTotalVideos) elTotalVideos.textContent = stats.stats.total_videos || 0;
                const elSuccessRate = document.getElementById('success-rate');
                if (elSuccessRate) elSuccessRate.textContent = (stats.stats.success_rate || 0) + '%';
            }
            
            if (jobs.success) {
                // Count active and queued jobs
                const activeJobs = jobs.jobs.filter(job => job.status === 'running' || job.status === 'starting');
                const queuedJobs = jobs.jobs.filter(job => job.status === 'pending' || job.status === 'waiting');
                const elActive = document.getElementById('active-downloads');
                if (elActive) elActive.textContent = activeJobs.length;
                const elQueue = document.getElementById('queue-length');
                if (elQueue) elQueue.textContent = queuedJobs.length;
                // Completed today (optional element)
                const elCompletedToday = document.getElementById('completed-today');
                if (elCompletedToday) {
                    const today = new Date().toDateString();
                    const completedToday = jobs.jobs.filter(job => job.status === 'completed' && new Date(job.created_at).toDateString() === today).length;
                    elCompletedToday.textContent = completedToday;
                }
            }
            
        } catch (error) {
            console.error('Error updating metrics:', error);
        }
    }
    
    async updateActiveJobs() {
        try {
            const jobsUrl = `${window.APP_BASE || ''}/api/jobs?limit=10`;
            const response = await fetch(jobsUrl);
            const data = await response.json();
            
            if (!data.success) return;
            
            const activeJobs = data.jobs.filter(job => 
                job.status === 'running' || job.status === 'starting' || job.status === 'pending'
            );
            
            const container = document.getElementById('active-jobs-list');
            
            if (activeJobs.length === 0) {
                container.innerHTML = '<div class="no-jobs">No active jobs</div>';
                return;
            }
            
            container.innerHTML = activeJobs.map(job => {
                const progress = job.progress || 0;
                const statusColor = this.getStatusColor(job.status);
                
                return `
                    <div class="job-item">
                        <div class="job-info">
                            <div class="job-query">${job.query || 'Unknown job'}</div>
                            <div class="job-status" style="color: ${statusColor}">
                                ${job.status} - ${job.downloaded || 0} downloaded
                            </div>
                            <div class="job-progress">
                                <div class="job-progress-bar" style="width: ${progress}%"></div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            
            // Update active jobs tracking
            activeJobs.forEach(job => {
                if (!this.activeJobs.has(job.id)) {
                    this.activeJobs.set(job.id, job);
                    this.addActivityEntry(`Started job: ${job.query}`);
                } else {
                    const oldJob = this.activeJobs.get(job.id);
                    if (oldJob.progress !== job.progress) {
                        this.addActivityEntry(`Job progress: ${job.query} (${job.progress}%)`);
                    }
                    if (oldJob.downloaded !== job.downloaded) {
                        this.addActivityEntry(`Downloaded: ${job.downloaded} items for "${job.query}"`);
                    }
                    this.activeJobs.set(job.id, job);
                }
            });
            
            // Remove completed jobs from tracking
            for (const [jobId, job] of this.activeJobs.entries()) {
                if (!activeJobs.find(aj => aj.id === jobId)) {
                    this.addActivityEntry(`Completed job: ${job.query}`);
                    this.activeJobs.delete(jobId);
                }
            }
            
        } catch (error) {
            console.error('Error updating active jobs:', error);
        }
    }
    
    getStatusColor(status) {
        const colors = {
            'running': '#28a745',
            'starting': '#ffc107',
            'pending': '#6c757d',
            'completed': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#6c757d'
        };
        return colors[status] || '#6c757d';
    }
    
    addActivityEntry(message, type = 'info') {
        const container = document.getElementById('activity-log');
        const timestamp = new Date().toLocaleTimeString();
        
        const entry = document.createElement('div');
        entry.className = 'activity-entry';
        entry.innerHTML = `
            <span class="timestamp">${timestamp}</span>
            <span class="message">${message}</span>
        `;
        
        container.insertBefore(entry, container.firstChild);
        
        // Limit number of entries
        const entries = container.querySelectorAll('.activity-entry');
        if (entries.length > this.maxLogEntries) {
            entries[entries.length - 1].remove();
        }
    }
    
    addFileOperation(filename, status, details = '') {
        const container = document.getElementById('file-operations');
        
        // Remove "no operations" message
        const noOps = container.querySelector('.no-operations');
        if (noOps) noOps.remove();
        
        const operation = document.createElement('div');
        operation.className = 'file-operation';
        operation.innerHTML = `
            <div>
                <div class="file-name">${filename}</div>
                <div class="file-details">${details}</div>
            </div>
            <div class="operation-status status-${status}">${status}</div>
        `;
        
        container.insertBefore(operation, container.firstChild);
        
        // Limit number of operations
        const operations = container.querySelectorAll('.file-operation');
        if (operations.length > 20) {
            operations[operations.length - 1].remove();
        }
        
        // Add to activity log
        this.addActivityEntry(`File operation: ${filename} (${status})`);
    }
    
    destroy() {
        this.stopRealTimeUpdates();
        const dashboard = document.getElementById('real-time-dashboard');
        if (dashboard) {
            dashboard.remove();
        }
    }
}

// Export for use in other modules
window.RealTimeDashboard = RealTimeDashboard;

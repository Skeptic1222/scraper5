/**
 * Real-time Download Dashboard with Progress Tracking
 */
class DownloadDashboard {
    constructor() {
        this.activeDownloads = new Map();
        this.downloadQueue = [];
        this.completedDownloads = [];
        this.stats = {
            totalSpeed: 0,
            activeThreads: 0,
            totalDownloaded: 0,
            queuedJobs: 0,
            avgSpeed: 0,
            peakSpeed: 0,
            totalFiles: 0,
            failedFiles: 0
        };
        this.refreshInterval = null;
        this.initialized = false;
    }
    
    init() {
        if (this.initialized) return;
        this.initialized = true;
        
        console.log('Initializing real-time download dashboard...');
        this.createDashboardUI();
        this.startMonitoring();
    }
    
    createDashboardUI() {
        let container = document.getElementById('dashboard-dynamic-content');
        console.log('Looking for dashboard container...');
        console.log('Container found:', container ? 'YES' : 'NO');
        if (!container) {
            console.error('Dashboard dynamic content container not found');
            // Try to find the dashboard section and create the container
            const dashboardSection = document.getElementById('dashboard-section');
            if (dashboardSection) {
                console.log('Dashboard section found, checking for container...');
                let dynamicContent = dashboardSection.querySelector('#dashboard-dynamic-content');
                if (!dynamicContent) {
                    console.log('Creating dashboard-dynamic-content container...');
                    dynamicContent = document.createElement('div');
                    dynamicContent.id = 'dashboard-dynamic-content';
                    dashboardSection.appendChild(dynamicContent);
                }
                container = dynamicContent;
            } else {
                console.error('Dashboard section not found either!');
                return;
            }
        }
        
        console.log('Populating dashboard HTML...');
        // Clear any existing content and populate with the dashboard
        container.innerHTML = `
            <div class="download-dashboard">
                <!-- Download Stats Header -->
                <div class="download-stats-header">
                    <div class="stat-card primary">
                        <i class="fas fa-tachometer-alt"></i>
                        <div class="stat-content">
                            <span class="stat-value" id="total-speed">0 MB/s</span>
                            <span class="stat-label">Download Speed</span>
                        </div>
                    </div>
                    <div class="stat-card success">
                        <i class="fas fa-tasks"></i>
                        <div class="stat-content">
                            <span class="stat-value" id="active-threads">0</span>
                            <span class="stat-label">Active Threads</span>
                        </div>
                    </div>
                    <div class="stat-card info">
                        <i class="fas fa-download"></i>
                        <div class="stat-content">
                            <span class="stat-value" id="total-downloaded">0</span>
                            <span class="stat-label">Files Downloaded</span>
                        </div>
                    </div>
                    <div class="stat-card warning">
                        <i class="fas fa-list"></i>
                        <div class="stat-content">
                            <span class="stat-value" id="queued-jobs">0</span>
                            <span class="stat-label">Queued Jobs</span>
                        </div>
                    </div>
                </div>
                
                <!-- Active Downloads Section -->
                <div class="download-section">
                    <h3 class="section-title">
                        <i class="fas fa-spinner fa-pulse"></i> Active Downloads
                        <span class="badge" id="active-count">0</span>
                    </h3>
                    <div id="active-downloads-container" class="downloads-container">
                        <div class="empty-downloads">
                            <i class="fas fa-check-circle fa-3x"></i>
                            <p>No active downloads</p>
                            <button class="btn btn-primary" onclick="window.navigation.switchSection('search-section')">
                                <i class="fas fa-search"></i> Start New Search
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Download Queue Section -->
                <div class="download-section">
                    <h3 class="section-title">
                        <i class="fas fa-clock"></i> Download Queue
                        <span class="badge" id="queue-count">0</span>
                    </h3>
                    <div id="download-queue-container" class="queue-container">
                        <div class="empty-queue">
                            <i class="fas fa-inbox fa-3x"></i>
                            <p>No queued downloads</p>
                        </div>
                    </div>
                </div>
                
                <!-- Performance Graph -->
                <div class="download-section">
                    <h3 class="section-title">
                        <i class="fas fa-chart-line"></i> Performance Monitor
                    </h3>
                    <div class="performance-monitor">
                        <div class="speed-graph" id="speed-graph">
                            <canvas id="speed-canvas" width="800" height="200"></canvas>
                        </div>
                        <div class="performance-stats">
                            <div class="perf-stat">
                                <span class="perf-label">Average Speed:</span>
                                <span class="perf-value" id="avg-speed">0 MB/s</span>
                            </div>
                            <div class="perf-stat">
                                <span class="perf-label">Peak Speed:</span>
                                <span class="perf-value" id="peak-speed">0 MB/s</span>
                            </div>
                            <div class="perf-stat">
                                <span class="perf-label">Success Rate:</span>
                                <span class="perf-value" id="success-rate">100%</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Completed Downloads -->
                <div class="download-section">
                    <h3 class="section-title">
                        <i class="fas fa-check"></i> Recent Completions
                        <button class="btn btn-sm btn-outline-danger" onclick="downloadDashboard.clearCompleted()">
                            Clear All
                        </button>
                    </h3>
                    <div id="completed-downloads-container" class="completed-container">
                        <div class="empty-completed">
                            <i class="fas fa-history fa-3x"></i>
                            <p>No completed downloads yet</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.addStyles();
        this.initSpeedGraph();
    }
    
    addStyles() {
        if (document.getElementById('download-dashboard-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'download-dashboard-styles';
        styles.textContent = `
            .download-dashboard {
                padding: 1.5rem;
                max-width: 1600px;
                margin: 0 auto;
            }
            
            .download-stats-header {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .stat-card {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                display: flex;
                align-items: center;
                gap: 1rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
                border-left: 4px solid;
            }
            
            .stat-card.primary { border-color: #667eea; }
            .stat-card.success { border-color: #10b981; }
            .stat-card.info { border-color: #3b82f6; }
            .stat-card.warning { border-color: #f59e0b; }
            
            .stat-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }
            
            .stat-card i {
                font-size: 2rem;
                opacity: 0.8;
            }
            
            .stat-card.primary i { color: #667eea; }
            .stat-card.success i { color: #10b981; }
            .stat-card.info i { color: #3b82f6; }
            .stat-card.warning i { color: #f59e0b; }
            
            .stat-content {
                flex: 1;
            }
            
            .stat-value {
                display: block;
                font-size: 1.8rem;
                font-weight: bold;
                color: #1f2937;
            }
            
            .stat-label {
                display: block;
                font-size: 0.9rem;
                color: #6b7280;
                margin-top: 0.25rem;
            }
            
            .download-section {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .section-title {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #f3f4f6;
                color: #1f2937;
            }
            
            .section-title i {
                margin-right: 0.5rem;
                color: #667eea;
            }
            
            .badge {
                background: #667eea;
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.85rem;
                font-weight: 600;
            }
            
            .downloads-container {
                max-height: 400px;
                overflow-y: auto;
            }
            
            .download-item {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.75rem;
                transition: all 0.3s ease;
            }
            
            .download-item:hover {
                background: #f3f4f6;
                border-color: #d1d5db;
            }
            
            .download-header {
                display: flex;
                justify-content: space-between;
                align-items: start;
                margin-bottom: 0.75rem;
            }
            
            .download-info {
                flex: 1;
            }
            
            .download-filename {
                font-weight: 600;
                color: #1f2937;
                display: block;
                margin-bottom: 0.25rem;
            }
            
            .download-source {
                font-size: 0.85rem;
                color: #6b7280;
            }
            
            .download-source i {
                margin-right: 0.25rem;
            }
            
            .download-stats {
                text-align: right;
                font-size: 0.85rem;
                color: #6b7280;
            }
            
            .download-speed {
                font-weight: 600;
                color: #10b981;
                display: block;
            }
            
            .download-progress-bar {
                background: #e5e7eb;
                border-radius: 6px;
                height: 8px;
                overflow: hidden;
                margin-bottom: 0.5rem;
            }
            
            .download-progress-fill {
                background: linear-gradient(90deg, #667eea, #764ba2);
                height: 100%;
                transition: width 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .download-progress-fill::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(
                    90deg,
                    transparent,
                    rgba(255, 255, 255, 0.3),
                    transparent
                );
                animation: shimmer 1.5s infinite;
            }
            
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            .download-details {
                display: flex;
                justify-content: space-between;
                font-size: 0.85rem;
                color: #6b7280;
            }
            
            .queue-item {
                background: #fef3c7;
                border: 1px solid #fde68a;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 0.5rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .queue-info {
                flex: 1;
            }
            
            .queue-title {
                font-weight: 600;
                color: #92400e;
                display: block;
                margin-bottom: 0.25rem;
            }
            
            .queue-details {
                font-size: 0.85rem;
                color: #b45309;
            }
            
            .queue-actions {
                display: flex;
                gap: 0.5rem;
            }
            
            .btn-queue {
                padding: 0.25rem 0.75rem;
                border-radius: 6px;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.85rem;
            }
            
            .btn-start {
                background: #10b981;
                color: white;
            }
            
            .btn-start:hover {
                background: #059669;
            }
            
            .btn-cancel {
                background: #ef4444;
                color: white;
            }
            
            .btn-cancel:hover {
                background: #dc2626;
            }
            
            .completed-item {
                background: #ecfdf5;
                border: 1px solid #a7f3d0;
                border-radius: 8px;
                padding: 0.75rem;
                margin-bottom: 0.5rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.9rem;
            }
            
            .completed-info {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .completed-info i {
                color: #10b981;
            }
            
            .completed-time {
                color: #6b7280;
                font-size: 0.85rem;
            }
            
            .performance-monitor {
                padding: 1rem;
                background: #f9fafb;
                border-radius: 8px;
            }
            
            .speed-graph {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            .performance-stats {
                display: flex;
                justify-content: space-around;
                padding-top: 1rem;
                border-top: 1px solid #e5e7eb;
            }
            
            .perf-stat {
                text-align: center;
            }
            
            .perf-label {
                display: block;
                font-size: 0.85rem;
                color: #6b7280;
                margin-bottom: 0.25rem;
            }
            
            .perf-value {
                display: block;
                font-size: 1.25rem;
                font-weight: bold;
                color: #1f2937;
            }
            
            .empty-downloads, .empty-queue, .empty-completed {
                text-align: center;
                padding: 3rem;
                color: #9ca3af;
            }
            
            .empty-downloads i, .empty-queue i, .empty-completed i {
                margin-bottom: 1rem;
            }
        `;
        document.head.appendChild(styles);
    }
    
    initSpeedGraph() {
        const canvas = document.getElementById('speed-canvas');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        this.speedHistory = new Array(50).fill(0);
        this.graphCtx = ctx;
        
        this.drawSpeedGraph();
    }
    
    drawSpeedGraph() {
        if (!this.graphCtx) return;
        
        const canvas = this.graphCtx.canvas;
        const ctx = this.graphCtx;
        const width = canvas.width;
        const height = canvas.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw grid
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        
        for (let i = 0; i < 5; i++) {
            const y = (height / 4) * i;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
        
        // Draw speed line
        ctx.strokeStyle = '#667eea';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        const maxSpeed = Math.max(...this.speedHistory, 1);
        
        this.speedHistory.forEach((speed, index) => {
            const x = (width / this.speedHistory.length) * index;
            const y = height - (speed / maxSpeed) * height;
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
        
        // Fill area under line
        ctx.fillStyle = 'rgba(102, 126, 234, 0.1)';
        ctx.lineTo(width, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        ctx.fill();
    }
    
    startMonitoring() {
        this.refreshData();
        
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            this.refreshData();
        }, 1000); // Update every second for real-time monitoring
    }
    
    async refreshData() {
        try {
            // Fetch active jobs
            const jobsResponse = await fetch('/api/jobs');
            const jobsData = await jobsResponse.json();
            
            // Process jobs
            this.processJobs(jobsData.jobs || []);
            
            // Update UI
            this.updateDisplay();
        } catch (error) {
            console.error('Error refreshing download data:', error);
        }
    }
    
    processJobs(jobs) {
        // Clear current data
        this.activeDownloads.clear();
        this.downloadQueue = [];
        
        let totalSpeed = 0;
        let activeThreads = 0;
        
        jobs.forEach(job => {
            if (job.status === 'running' || job.status === 'downloading') {
                // Active download
                const downloadInfo = {
                    id: job.id,
                    filename: job.current_file || `Job ${job.id}`,
                    source: job.source || 'Multiple Sources',
                    progress: job.progress || 0,
                    speed: job.speed || Math.random() * 10, // Simulated speed
                    downloaded: job.downloaded || 0,
                    total: job.total || 100,
                    eta: job.eta || this.calculateETA(job.progress),
                    query: job.query || 'Search Query'
                };
                
                this.activeDownloads.set(job.id, downloadInfo);
                totalSpeed += downloadInfo.speed;
                activeThreads++;
            } else if (job.status === 'pending' || job.status === 'queued') {
                // Queued download
                this.downloadQueue.push({
                    id: job.id,
                    query: job.query || 'Search Query',
                    sources: job.sources || 0,
                    estimatedFiles: job.estimated || 0,
                    priority: job.priority || 'normal'
                });
            } else if (job.status === 'completed') {
                // Add to completed if recent
                const completedTime = new Date(job.completed_at || Date.now());
                const minutesAgo = (Date.now() - completedTime) / (1000 * 60);
                
                if (minutesAgo < 30) { // Show last 30 minutes
                    this.completedDownloads.push({
                        id: job.id,
                        query: job.query || 'Search Query',
                        files: job.downloaded || 0,
                        time: completedTime,
                        size: job.total_size || 0
                    });
                }
            }
        });
        
        // Update stats
        this.stats.totalSpeed = totalSpeed;
        this.stats.activeThreads = activeThreads;
        this.stats.queuedJobs = this.downloadQueue.length;
        
        // Update speed history for graph
        this.speedHistory.shift();
        this.speedHistory.push(totalSpeed);
        
        // Calculate averages
        this.stats.avgSpeed = this.speedHistory.reduce((a, b) => a + b) / this.speedHistory.length;
        this.stats.peakSpeed = Math.max(...this.speedHistory, this.stats.peakSpeed);
    }
    
    updateDisplay() {
        // Update stats
        document.getElementById('total-speed').textContent = `${this.stats.totalSpeed.toFixed(2)} MB/s`;
        document.getElementById('active-threads').textContent = this.stats.activeThreads;
        document.getElementById('total-downloaded').textContent = this.stats.totalDownloaded;
        document.getElementById('queued-jobs').textContent = this.stats.queuedJobs;
        
        // Update performance stats
        document.getElementById('avg-speed').textContent = `${this.stats.avgSpeed.toFixed(2)} MB/s`;
        document.getElementById('peak-speed').textContent = `${this.stats.peakSpeed.toFixed(2)} MB/s`;
        
        const successRate = this.stats.totalFiles > 0 
            ? ((this.stats.totalFiles - this.stats.failedFiles) / this.stats.totalFiles * 100).toFixed(1)
            : 100;
        document.getElementById('success-rate').textContent = `${successRate}%`;
        
        // Update counts
        document.getElementById('active-count').textContent = this.activeDownloads.size;
        document.getElementById('queue-count').textContent = this.downloadQueue.length;
        
        // Update active downloads
        this.updateActiveDownloads();
        
        // Update queue
        this.updateQueue();
        
        // Update completed
        this.updateCompleted();
        
        // Update graph
        this.drawSpeedGraph();
    }
    
    updateActiveDownloads() {
        const container = document.getElementById('active-downloads-container');
        if (!container) return;
        
        if (this.activeDownloads.size === 0) {
            container.innerHTML = `
                <div class="empty-downloads">
                    <i class="fas fa-check-circle fa-3x"></i>
                    <p>No active downloads</p>
                    <button class="btn btn-primary" onclick="window.navigation.switchSection('search-section')">
                        <i class="fas fa-search"></i> Start New Search
                    </button>
                </div>
            `;
            return;
        }
        
        const downloadsHTML = Array.from(this.activeDownloads.values()).map(download => `
            <div class="download-item" data-id="${download.id}">
                <div class="download-header">
                    <div class="download-info">
                        <span class="download-filename">${download.filename}</span>
                        <span class="download-source">
                            <i class="fas fa-globe"></i> ${download.source} | ${download.query}
                        </span>
                    </div>
                    <div class="download-stats">
                        <span class="download-speed">${download.speed.toFixed(2)} MB/s</span>
                        <span>ETA: ${download.eta}</span>
                    </div>
                </div>
                <div class="download-progress-bar">
                    <div class="download-progress-fill" style="width: ${download.progress}%"></div>
                </div>
                <div class="download-details">
                    <span>${download.downloaded} / ${download.total} files</span>
                    <span>${download.progress.toFixed(1)}%</span>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = downloadsHTML;
    }
    
    updateQueue() {
        const container = document.getElementById('download-queue-container');
        if (!container) return;
        
        if (this.downloadQueue.length === 0) {
            container.innerHTML = `
                <div class="empty-queue">
                    <i class="fas fa-inbox fa-3x"></i>
                    <p>No queued downloads</p>
                </div>
            `;
            return;
        }
        
        const queueHTML = this.downloadQueue.map(item => `
            <div class="queue-item" data-id="${item.id}">
                <div class="queue-info">
                    <span class="queue-title">${item.query}</span>
                    <span class="queue-details">
                        ${item.sources} sources | ~${item.estimatedFiles} files | Priority: ${item.priority}
                    </span>
                </div>
                <div class="queue-actions">
                    <button class="btn-queue btn-start" onclick="downloadDashboard.startQueued('${item.id}')">
                        <i class="fas fa-play"></i> Start
                    </button>
                    <button class="btn-queue btn-cancel" onclick="downloadDashboard.cancelQueued('${item.id}')">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = queueHTML;
    }
    
    updateCompleted() {
        const container = document.getElementById('completed-downloads-container');
        if (!container) return;
        
        if (this.completedDownloads.length === 0) {
            container.innerHTML = `
                <div class="empty-completed">
                    <i class="fas fa-history fa-3x"></i>
                    <p>No completed downloads yet</p>
                </div>
            `;
            return;
        }
        
        const completedHTML = this.completedDownloads
            .slice(0, 10) // Show last 10
            .map(item => {
                const timeAgo = this.formatTimeAgo(item.time);
                return `
                    <div class="completed-item">
                        <div class="completed-info">
                            <i class="fas fa-check-circle"></i>
                            <span>${item.query} - ${item.files} files</span>
                        </div>
                        <span class="completed-time">${timeAgo}</span>
                    </div>
                `;
            }).join('');
        
        container.innerHTML = completedHTML;
    }
    
    calculateETA(progress) {
        if (progress === 0) return 'Calculating...';
        const remaining = (100 - progress) / (progress / 60); // Rough estimate
        if (remaining < 60) return `${Math.round(remaining)} seconds`;
        return `${Math.round(remaining / 60)} minutes`;
    }
    
    formatTimeAgo(date) {
        const seconds = Math.floor((Date.now() - date) / 1000);
        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
        return `${Math.floor(seconds / 3600)} hours ago`;
    }
    
    startQueued(jobId) {
        console.log('Starting queued job:', jobId);
        // Trigger API to start the job
        fetch(`/api/jobs/${jobId}/start`, { method: 'POST' })
            .then(() => this.refreshData());
    }
    
    cancelQueued(jobId) {
        if (confirm('Cancel this download?')) {
            fetch(`/api/jobs/${jobId}`, { method: 'DELETE' })
                .then(() => this.refreshData());
        }
    }
    
    clearCompleted() {
        this.completedDownloads = [];
        this.updateCompleted();
    }
    
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        this.initialized = false;
    }
}

// Initialize download dashboard
window.downloadDashboard = new DownloadDashboard();

// Update the initialization function
window.initializeDashboard = function() {
    if (window.downloadDashboard) {
        window.downloadDashboard.init();
    }
};
/**
 * Real-Time Dashboard Module
 * Provides live updates for download progress with detailed metrics
 */

class RealtimeDashboard {
    constructor() {
        this.jobId = null;
        this.pollInterval = null;
        this.updateFrequency = 500; // Update every 500ms for smooth UI
        this.metrics = {
            discovered: 0,
            queued: 0,
            downloading: 0,
            completed: 0,
            failed: 0,
            images: 0,
            videos: 0,
            totalSpeed: 0,
            activeThreads: 0,
            totalBytes: 0
        };
        this.activeDownloads = [];
        this.recentFiles = [];
        this.maxRecentFiles = 50;

        this.init();
    }

    init() {
        // Listen for job creation events
        window.addEventListener('jobCreated', (e) => {
            this.startMonitoring(e.detail.jobId);
        });
    }

    switchToDashboardTab() {
        // Find and activate the dashboard tab
        const dashboardTab = document.querySelector('a[href="#dashboard"]');
        if (dashboardTab) {
            // Use Bootstrap 5 tab activation
            const tab = new bootstrap.Tab(dashboardTab);
            tab.show();
        }
    }

    startMonitoring(jobId) {
        this.jobId = jobId;
        this.showDashboard();
        this.startPolling();
    }

    stopMonitoring() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    showDashboard() {
        // Switch to dashboard tab automatically
        this.switchToDashboardTab();

        const container = document.getElementById('dashboard-progress-container');
        if (!container) return;

        container.style.display = 'block';
        container.innerHTML = `
            <div class="card border-primary">
                <div class="card-header bg-primary text-white">
                    <h3 class="h6 mb-0 d-flex justify-content-between align-items-center">
                        <span>
                            <i class="fas fa-download"></i> Download Progress
                        </span>
                        <span class="badge bg-light text-primary ms-2" id="job-timer">
                            <i class="fas fa-clock"></i> <span id="elapsed-time">00:00</span> / <span id="timeout-display">Unlimited</span>
                        </span>
                        <button type="button" class="btn btn-sm btn-outline-light" id="cancel-search">
                            <i class="fas fa-stop"></i> Cancel
                        </button>
                    </h3>
                </div>
                <div class="card-body">
                    <!-- Status Overview -->
                    <div class="row text-center mb-3">
                        <div class="col-6 col-md-2">
                            <div class="metric-card">
                                <div class="metric-value text-info" id="metric-discovered">0</div>
                                <div class="metric-label">Discovered</div>
                            </div>
                        </div>
                        <div class="col-6 col-md-2">
                            <div class="metric-card">
                                <div class="metric-value text-warning" id="metric-queued">0</div>
                                <div class="metric-label">Queued</div>
                            </div>
                        </div>
                        <div class="col-6 col-md-2">
                            <div class="metric-card">
                                <div class="metric-value text-primary" id="metric-downloading">0</div>
                                <div class="metric-label">Downloading</div>
                            </div>
                        </div>
                        <div class="col-6 col-md-2">
                            <div class="metric-card">
                                <div class="metric-value text-success" id="metric-completed">0</div>
                                <div class="metric-label">Completed</div>
                            </div>
                        </div>
                        <div class="col-6 col-md-2">
                            <div class="metric-card">
                                <div class="metric-value text-danger" id="metric-failed">0</div>
                                <div class="metric-label">Failed</div>
                            </div>
                        </div>
                        <div class="col-6 col-md-2">
                            <div class="metric-card">
                                <div class="metric-value text-muted" id="metric-threads">0</div>
                                <div class="metric-label">Threads</div>
                            </div>
                        </div>
                    </div>

                    <!-- File Types & Speed -->
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <div class="stat-box">
                                <i class="fas fa-image text-info"></i>
                                <span class="stat-value" id="stat-images">0</span>
                                <span class="stat-label">Images</span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stat-box">
                                <i class="fas fa-video text-danger"></i>
                                <span class="stat-value" id="stat-videos">0</span>
                                <span class="stat-label">Videos</span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="stat-box">
                                <i class="fas fa-tachometer-alt text-success"></i>
                                <span class="stat-value" id="stat-speed">0 KB/s</span>
                                <span class="stat-label">Total Speed</span>
                            </div>
                        </div>
                    </div>

                    <!-- Active Downloads -->
                    <div class="mb-3">
                        <h6 class="mb-2">
                            <i class="fas fa-download"></i> Active Downloads
                            <span class="badge bg-primary ms-2" id="active-count">0</span>
                        </h6>
                        <div id="active-downloads" class="active-downloads-container">
                            <div class="text-muted text-center py-3">
                                <i class="fas fa-hourglass-half"></i> Waiting for downloads to start...
                            </div>
                        </div>
                    </div>

                    <!-- Recent Files -->
                    <div>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0">
                                <i class="fas fa-list"></i> Recent Files
                            </h6>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="clear-log">
                                <i class="fas fa-trash"></i> Clear
                            </button>
                        </div>
                        <div id="recent-files" class="recent-files-container bg-dark text-light p-2 rounded">
                            <div class="text-muted">Ready to start download...</div>
                        </div>
                    </div>

                    <!-- Transfer Summary -->
                    <div class="mt-3 text-center text-muted small">
                        <i class="fas fa-database"></i> Total Transfer: <span id="total-transfer">0 MB</span>
                    </div>
                </div>
            </div>
        `;

        // Setup event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        const cancelBtn = document.getElementById('cancel-search');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelJob());
        }

        const clearLogBtn = document.getElementById('clear-log');
        if (clearLogBtn) {
            clearLogBtn.addEventListener('click', () => this.clearRecentFiles());
        }
    }

    startPolling() {
        // Clear any existing interval
        this.stopMonitoring();

        // Poll for updates
        this.pollInterval = setInterval(() => {
            this.fetchProgress();
        }, this.updateFrequency);

        // Fetch immediately
        this.fetchProgress();
    }

    async fetchProgress() {
        if (!this.jobId) return;

        try {
            const response = await fetch(`${window.APP_BASE || '/scraper'}/api/job-progress/${this.jobId}`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to fetch progress');
            }

            const data = await response.json();
            this.updateDashboard(data);

            // Check if job is complete
            if (data.status === 'completed' || data.status === 'failed' || data.status === 'error') {
                this.stopMonitoring();
                this.handleJobComplete(data);
            }
        } catch (error) {
            console.error('Progress fetch error:', error);
        }
    }

    updateDashboard(data) {
        // Update metrics
        this.updateMetric('discovered', data.downloaded_count || 0);
        this.updateMetric('completed', data.success_count || 0);
        this.updateMetric('failed', data.error_count || 0);

        // Estimate queued and downloading (simplified)
        const discovered = data.downloaded_count || 0;
        const completed = data.success_count || 0;
        const failed = data.error_count || 0;
        const downloading = Math.max(0, discovered - completed - failed);

        this.updateMetric('downloading', downloading);
        this.updateMetric('queued', 0); // Would need backend support
        this.updateMetric('threads', 5); // Default concurrent threads

        // Update file types
        this.updateStat('images', data.downloaded_count || 0); // Simplified
        this.updateStat('videos', 0); // Would need backend support

        // Update speed (estimate based on progress)
        const speed = this.estimateSpeed(data);
        this.updateStat('speed', this.formatSpeed(speed));

        // Update total transfer
        this.updateTotalTransfer(data);

        // Update recent files
        if (data.current_file && data.current_file !== this.lastFile) {
            this.addRecentFile(data.current_file, 'completed');
            this.lastFile = data.current_file;
        }

        // Update active downloads (mock data for now)
        this.updateActiveDownloads(data);
    }

    updateMetric(name, value) {
        const elem = document.getElementById(`metric-${name}`);
        if (elem) {
            elem.textContent = value;
            // Add animation class
            elem.classList.add('metric-updated');
            setTimeout(() => elem.classList.remove('metric-updated'), 300);
        }
    }

    updateStat(name, value) {
        const elem = document.getElementById(`stat-${name}`);
        if (elem) {
            elem.textContent = value;
        }
    }

    updateActiveDownloads(data) {
        const container = document.getElementById('active-downloads');
        if (!container) return;

        const activeCount = document.getElementById('active-count');

        // For now, show current file if downloading
        if (data.status === 'running' && data.current_file) {
            if (activeCount) activeCount.textContent = '1';

            container.innerHTML = `
                <div class="download-item">
                    <div class="download-info">
                        <i class="fas fa-file text-primary"></i>
                        <span class="filename">${this.truncate(data.current_file, 40)}</span>
                    </div>
                    <div class="download-progress">
                        <div class="progress" style="height: 4px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated bg-success"
                                 style="width: ${data.overall_progress || 0}%"></div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            if (activeCount) activeCount.textContent = '0';
            container.innerHTML = `
                <div class="text-muted text-center py-2">
                    <i class="fas fa-check-circle"></i> No active downloads
                </div>
            `;
        }
    }

    addRecentFile(filename, status) {
        const container = document.getElementById('recent-files');
        if (!container) return;

        // Remove placeholder text
        if (container.querySelector('.text-muted')) {
            container.innerHTML = '';
        }

        const entry = document.createElement('div');
        entry.className = `file-entry ${status}`;

        const icon = status === 'completed' ? 'fa-check-circle text-success' :
                     status === 'failed' ? 'fa-times-circle text-danger' :
                     'fa-spinner fa-spin text-primary';

        entry.innerHTML = `
            <i class="fas ${icon}"></i>
            <span class="filename">${this.truncate(filename, 60)}</span>
            <span class="timestamp">${new Date().toLocaleTimeString()}</span>
        `;

        container.insertBefore(entry, container.firstChild);

        // Limit to max recent files
        while (container.children.length > this.maxRecentFiles) {
            container.removeChild(container.lastChild);
        }

        // Scroll to top
        container.scrollTop = 0;
    }

    clearRecentFiles() {
        const container = document.getElementById('recent-files');
        if (container) {
            container.innerHTML = '<div class="text-muted">Log cleared</div>';
        }
    }

    estimateSpeed(data) {
        // Estimate based on elapsed time and completed files
        const elapsed = data.elapsed_seconds || 1;
        const completed = data.success_count || 0;
        const avgSize = 500 * 1024; // Assume 500KB average file size
        const totalBytes = completed * avgSize;
        return totalBytes / elapsed; // Bytes per second
    }

    formatSpeed(bytesPerSecond) {
        if (bytesPerSecond < 1024) {
            return `${Math.round(bytesPerSecond)} B/s`;
        } else if (bytesPerSecond < 1024 * 1024) {
            return `${(bytesPerSecond / 1024).toFixed(1)} KB/s`;
        } else {
            return `${(bytesPerSecond / (1024 * 1024)).toFixed(2)} MB/s`;
        }
    }

    updateTotalTransfer(data) {
        const completed = data.success_count || 0;
        const avgSize = 500; // KB average
        const totalMB = (completed * avgSize) / 1024;

        const elem = document.getElementById('total-transfer');
        if (elem) {
            elem.textContent = `${totalMB.toFixed(1)} MB`;
        }
    }

    handleJobComplete(data) {
        // Update final stats
        const container = document.getElementById('dashboard-progress-container');
        if (container) {
            const header = container.querySelector('.card-header');
            if (header) {
                if (data.status === 'completed') {
                    header.classList.remove('bg-primary');
                    header.classList.add('bg-success');
                } else {
                    header.classList.remove('bg-primary');
                    header.classList.add('bg-danger');
                }
            }
        }

        // Add completion message
        this.addRecentFile(
            data.status === 'completed' ?
                `✓ Job completed! Downloaded ${data.success_count || 0} files` :
                `✗ Job failed: ${data.current_file || 'Unknown error'}`,
            data.status
        );

        // Refresh asset library if available
        if (window.assetLibrary && typeof window.assetLibrary.loadAssets === 'function') {
            setTimeout(() => {
                window.assetLibrary.loadAssets();
            }, 1000);
        }
    }

    async cancelJob() {
        if (!this.jobId) return;

        if (!confirm('Are you sure you want to cancel this job?')) {
            return;
        }

        try {
            const response = await fetch(`${window.APP_BASE || '/scraper'}/api/jobs/${this.jobId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (response.ok) {
                this.addRecentFile('Job cancelled by user', 'failed');
                this.stopMonitoring();
            }
        } catch (error) {
            console.error('Cancel error:', error);
        }
    }

    truncate(str, length) {
        if (!str) return '';
        return str.length > length ? str.substring(0, length) + '...' : str;
    }
}

// Initialize dashboard
window.realtimeDashboard = new RealtimeDashboard();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealtimeDashboard;
}

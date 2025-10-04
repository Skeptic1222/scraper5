/**
 * Enhanced Job Dashboard - Shows detailed download progress
 * Displays individual file details, threads, download speed, file types, etc.
 */

class EnhancedJobDashboard {
    constructor() {
        this.currentJobId = null;
        this.updateInterval = null;
        this.files = {};
        this.stats = {
            totalFiles: 0,
            downloadedFiles: 0,
            failedFiles: 0,
            totalBytes: 0,
            downloadedBytes: 0,
            activeThreads: 0,
            downloadSpeed: 0,
            avgSpeed: 0,
            eta: 0,
            startTime: null,
            fileTypes: {}
        };
    }

    /**
     * Start tracking a job
     */
    trackJob(jobId) {
        this.currentJobId = jobId;
        this.files = {};
        this.stats.startTime = Date.now();

        // Clear existing interval
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        // Update every 500ms for smooth progress
        this.updateInterval = setInterval(() => this.updateProgress(), 500);

        // Create or show the dashboard
        this.showDashboard();
    }

    /**
     * Update progress from server
     */
    async updateProgress() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`${window.APP_BASE}/api/job-progress/${this.currentJobId}`);
            const data = await response.json();

            if (data.error) {
                console.error('[Job Dashboard] Error:', data.error);
                return;
            }

            // Update job status
            this.updateJobStatus(data);

            // Update stats from API response (using existing fields)
            this.stats.totalFiles = data.downloaded_count || 0;
            this.stats.downloadedFiles = data.success_count || 0;
            this.stats.failedFiles = data.error_count || 0;
            this.stats.activeThreads = data.status === 'running' ? 1 : 0;

            // Create a simulated file entry for current file
            if (data.current_file) {
                const fileId = data.current_file;
                if (!this.files[fileId]) {
                    this.files[fileId] = {
                        id: fileId,
                        filename: data.current_file,
                        status: data.status === 'running' ? 'downloading' : data.status,
                        downloaded: 0,
                        size: 0,
                        speed: 0,
                        type: this.getFileType(data.current_file)
                    };
                }
            }

            // Calculate stats
            this.calculateStats(data);

            // Update UI
            this.renderDashboard();

            // Stop tracking if job is complete
            if (data.status === 'completed' || data.status === 'error') {
                this.stopTracking();
            }
        } catch (error) {
            console.error('[Job Dashboard] Update error:', error);
        }
    }

    /**
     * Update job status
     */
    updateJobStatus(data) {
        this.jobData = data;
    }

    /**
     * Update file list with detailed information
     */
    updateFileList(files) {
        files.forEach(file => {
            const fileId = file.url || file.path || Math.random().toString(36);

            // Initialize or update file tracking
            if (!this.files[fileId]) {
                this.files[fileId] = {
                    id: fileId,
                    url: file.url,
                    filename: file.filename || 'Unknown',
                    size: file.size || 0,
                    downloaded: file.downloaded || 0,
                    status: file.status || 'pending',
                    speed: file.speed || 0,
                    startTime: file.startTime || Date.now(),
                    endTime: file.endTime,
                    error: file.error,
                    type: file.type || this.getFileType(file.filename),
                    threadId: file.threadId || 0
                };
            } else {
                // Update existing file
                Object.assign(this.files[fileId], file);
            }

            // Update file type stats
            const fileType = this.files[fileId].type;
            if (!this.stats.fileTypes[fileType]) {
                this.stats.fileTypes[fileType] = 0;
            }
            if (file.status === 'completed') {
                this.stats.fileTypes[fileType]++;
            }
        });
    }

    /**
     * Calculate overall stats
     */
    calculateStats(data) {
        // Count files by status
        const fileArray = Object.values(this.files);

        // Calculate bytes
        this.stats.totalBytes = fileArray.reduce((sum, f) => sum + (f.size || 0), 0);
        this.stats.downloadedBytes = fileArray.reduce((sum, f) => sum + (f.downloaded || 0), 0);

        // Calculate download speed (bytes per second)
        const elapsedSeconds = (Date.now() - this.stats.startTime) / 1000;
        this.stats.avgSpeed = elapsedSeconds > 0 ? this.stats.downloadedBytes / elapsedSeconds : 0;

        // Current speed from active downloads
        const activeFiles = fileArray.filter(f => f.status === 'downloading');
        this.stats.downloadSpeed = activeFiles.reduce((sum, f) => sum + (f.speed || 0), 0);

        // Calculate ETA (estimate based on progress)
        const progress = this.jobData?.overall_progress || 0;
        if (progress > 0 && progress < 100 && elapsedSeconds > 0) {
            const estimatedTotal = (elapsedSeconds / progress) * 100;
            this.stats.eta = estimatedTotal - elapsedSeconds;
        } else {
            this.stats.eta = 0;
        }

        // Update file type stats
        fileArray.forEach(file => {
            const fileType = file.type;
            if (!this.stats.fileTypes[fileType]) {
                this.stats.fileTypes[fileType] = 0;
            }
            if (file.status === 'completed') {
                this.stats.fileTypes[fileType]++;
            }
        });
    }

    /**
     * Get file type from filename
     */
    getFileType(filename) {
        if (!filename) return 'unknown';
        const ext = filename.split('.').pop().toLowerCase();

        const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico'];
        const videoExts = ['mp4', 'webm', 'avi', 'mov', 'mkv', 'flv', 'm4v'];
        const audioExts = ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'];

        if (imageExts.includes(ext)) return 'image';
        if (videoExts.includes(ext)) return 'video';
        if (audioExts.includes(ext)) return 'audio';
        return 'other';
    }

    /**
     * Show dashboard
     */
    showDashboard() {
        // Create dashboard container if it doesn't exist
        let dashboard = document.getElementById('enhanced-job-dashboard');
        if (!dashboard) {
            dashboard = document.createElement('div');
            dashboard.id = 'enhanced-job-dashboard';
            dashboard.className = 'enhanced-job-dashboard';
            document.body.appendChild(dashboard);
        }

        dashboard.style.display = 'block';
        this.renderDashboard();
    }

    /**
     * Render dashboard UI
     */
    renderDashboard() {
        const dashboard = document.getElementById('enhanced-job-dashboard');
        if (!dashboard) return;

        const fileArray = Object.values(this.files);
        const progress = this.stats.totalFiles > 0 ? (this.stats.downloadedFiles / this.stats.totalFiles) * 100 : 0;

        const query = this.jobData?.data?.query || this.jobData?.query || 'Download Job';

        dashboard.innerHTML = `
            <div class="job-dashboard-header">
                <h3>Download Progress: ${query}</h3>
                <button class="close-btn" onclick="window.jobDashboard.hide()">&times;</button>
            </div>

            <div class="job-stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${this.stats.downloadedFiles} / ${this.stats.totalFiles}</div>
                    <div class="stat-label">Files</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${this.formatBytes(this.stats.downloadedBytes)} / ${this.formatBytes(this.stats.totalBytes)}</div>
                    <div class="stat-label">Data</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${this.formatSpeed(this.stats.downloadSpeed)}</div>
                    <div class="stat-label">Current Speed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${this.formatSpeed(this.stats.avgSpeed)}</div>
                    <div class="stat-label">Avg Speed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${this.stats.activeThreads}</div>
                    <div class="stat-label">Active Threads</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${this.formatTime(this.stats.eta)}</div>
                    <div class="stat-label">ETA</div>
                </div>
            </div>

            <div class="overall-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
                <div class="progress-text">${progress.toFixed(1)}% Complete</div>
            </div>

            <div class="file-types-chart">
                <h4>File Types</h4>
                <div class="file-types-list">
                    ${Object.entries(this.stats.fileTypes).map(([type, count]) => `
                        <div class="file-type-item">
                            <span class="file-type-icon ${type}">${this.getFileTypeIcon(type)}</span>
                            <span class="file-type-label">${type}</span>
                            <span class="file-type-count">${count}</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="files-list">
                <h4>Files (${fileArray.length})</h4>
                <div class="files-table">
                    ${fileArray.map(file => this.renderFileRow(file)).join('')}
                </div>
            </div>
        `;
    }

    /**
     * Render individual file row
     */
    renderFileRow(file) {
        const fileProgress = file.size > 0 ? (file.downloaded / file.size) * 100 : 0;
        const statusClass = file.status === 'completed' ? 'success' : file.status === 'error' ? 'error' : 'active';
        const statusIcon = file.status === 'completed' ? '✓' : file.status === 'error' ? '✗' : '↓';

        return `
            <div class="file-row ${statusClass}">
                <div class="file-info">
                    <span class="file-status">${statusIcon}</span>
                    <span class="file-icon">${this.getFileTypeIcon(file.type)}</span>
                    <span class="file-name" title="${file.filename}">${this.truncate(file.filename, 50)}</span>
                </div>
                <div class="file-details">
                    <span class="file-size">${this.formatBytes(file.size)}</span>
                    <span class="file-speed">${file.status === 'downloading' ? this.formatSpeed(file.speed) : ''}</span>
                    <span class="file-thread">T${file.threadId}</span>
                </div>
                <div class="file-progress-bar">
                    <div class="file-progress-fill" style="width: ${fileProgress}%"></div>
                </div>
                ${file.error ? `<div class="file-error">${file.error}</div>` : ''}
            </div>
        `;
    }

    /**
     * Get file type icon
     */
    getFileTypeIcon(type) {
        const icons = {
            'image': '🖼️',
            'video': '🎬',
            'audio': '🎵',
            'other': '📄',
            'unknown': '❓'
        };
        return icons[type] || icons.unknown;
    }

    /**
     * Format bytes to human readable
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Format speed (bytes/sec to human readable)
     */
    formatSpeed(bytesPerSec) {
        return this.formatBytes(bytesPerSec) + '/s';
    }

    /**
     * Format time (seconds to HH:MM:SS)
     */
    formatTime(seconds) {
        if (!seconds || !isFinite(seconds)) return '--:--';
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        return `${h > 0 ? h + ':' : ''}${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }

    /**
     * Truncate string
     */
    truncate(str, length) {
        if (!str) return '';
        return str.length > length ? str.substring(0, length) + '...' : str;
    }

    /**
     * Stop tracking
     */
    stopTracking() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    /**
     * Hide dashboard
     */
    hide() {
        const dashboard = document.getElementById('enhanced-job-dashboard');
        if (dashboard) {
            dashboard.style.display = 'none';
        }
        this.stopTracking();
    }
}

// Create global instance
window.jobDashboard = new EnhancedJobDashboard();

// Auto-track jobs from search results
document.addEventListener('DOMContentLoaded', () => {
    // Listen for job creation events
    window.addEventListener('jobCreated', (event) => {
        if (event.detail && event.detail.jobId) {
            window.jobDashboard.trackJob(event.detail.jobId);
        }
    });
});

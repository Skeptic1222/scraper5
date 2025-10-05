/**
 * Dashboard Manager Module
 * Manages system statistics and dashboard initialization
 */

class DashboardManager {
    constructor() {
        this.refreshInterval = null;
        this.refreshFrequency = 30000; // Refresh every 30 seconds
        this.stats = {
            totalAssets: 0,
            totalJobs: 0,
            storageUsed: 0,
            activeSources: 0
        };

        this.init();
    }

    init() {
        // Load initial stats
        this.loadSystemStats();

        // Listen for dashboard tab shown event
        document.addEventListener('shown.bs.tab', (e) => {
            if (e.target.getAttribute('href') === '#dashboard') {
                this.onDashboardShown();
            }
        });

        // Start periodic refresh
        this.startPeriodicRefresh();
    }

    onDashboardShown() {
        // Refresh stats when dashboard is shown
        this.loadSystemStats();

        // Load recent activity
        this.loadRecentJobs();
        this.loadRecentAssets();
    }

    startPeriodicRefresh() {
        // Refresh stats periodically
        this.refreshInterval = setInterval(() => {
            // Only refresh if dashboard tab is visible
            const dashboardTab = document.querySelector('#dashboard');
            if (dashboardTab && dashboardTab.classList.contains('active')) {
                this.loadSystemStats();
                this.loadRecentJobs();
                this.loadRecentAssets();
            }
        }, this.refreshFrequency);
    }

    async loadSystemStats() {
        try {
            // Fetch user stats
            const response = await fetch(`${window.APP_BASE || '/scraper'}/api/user-stats`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to fetch stats');
            }

            const data = await response.json();
            this.updateSystemStats(data);
        } catch (error) {
            console.error('Failed to load system stats:', error);
        }
    }

    updateSystemStats(data) {
        // Update Total Assets
        this.updateStat('total-assets', data.total_assets || 0);

        // Update Total Jobs
        this.updateStat('total-jobs', data.total_jobs || 0);

        // Update Storage Used (convert bytes to GB)
        const storageGB = ((data.storage_used || 0) / (1024 * 1024 * 1024)).toFixed(2);
        this.updateStat('storage-used', `${storageGB} GB`);

        // Update Active Sources (count available sources)
        this.updateStat('active-sources', data.active_sources || 118);
    }

    updateStat(elementId, value) {
        const elem = document.getElementById(elementId);
        if (elem) {
            elem.textContent = value;

            // Add pulse animation
            elem.classList.add('stat-updated');
            setTimeout(() => elem.classList.remove('stat-updated'), 500);
        }
    }

    async loadRecentJobs() {
        try {
            const response = await fetch(`${window.APP_BASE || '/scraper'}/api/jobs?limit=5`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to fetch jobs');
            }

            const data = await response.json();
            this.displayRecentJobs(data.jobs || []);
        } catch (error) {
            console.error('Failed to load recent jobs:', error);
        }
    }

    displayRecentJobs(jobs) {
        const container = document.getElementById('recent-jobs-list');
        if (!container) return;

        if (jobs.length === 0) {
            container.innerHTML = '<div class="text-muted text-center py-3">No recent jobs</div>';
            return;
        }

        container.innerHTML = jobs.map(job => {
            const statusBadge = this.getStatusBadge(job.status);
            const date = new Date(job.created_at).toLocaleString();

            return `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${this.escapeHtml(job.query || 'Search Job')}</h6>
                            <small class="text-muted">
                                <i class="fas fa-clock"></i> ${date}
                            </small>
                        </div>
                        <div class="text-end">
                            ${statusBadge}
                            <div class="small text-muted mt-1">
                                ${job.success_count || 0} files
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    async loadRecentAssets() {
        try {
            const response = await fetch(`${window.APP_BASE || '/scraper'}/api/assets?limit=6`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to fetch assets');
            }

            const data = await response.json();
            this.displayRecentAssets(data.assets || []);
        } catch (error) {
            console.error('Failed to load recent assets:', error);
        }
    }

    displayRecentAssets(assets) {
        const container = document.getElementById('recent-assets-grid');
        if (!container) return;

        if (assets.length === 0) {
            container.innerHTML = '<div class="text-muted text-center py-3">No recent assets</div>';
            return;
        }

        container.innerHTML = assets.map(asset => {
            const thumbnailUrl = asset.thumbnail_url ||
                                 `${window.APP_BASE || '/scraper'}/api/media/${asset.id}/thumbnail`;
            const assetUrl = `${window.APP_BASE || '/scraper'}/api/media/${asset.id}`;

            return `
                <div class="col-md-2 col-4 mb-3">
                    <div class="asset-thumbnail" data-asset-id="${asset.id}">
                        <img src="${thumbnailUrl}"
                             alt="${this.escapeHtml(asset.filename || 'Asset')}"
                             class="img-fluid rounded"
                             onerror="this.src='${window.APP_BASE || '/scraper'}/static/images/placeholder.png'">
                        <div class="asset-overlay">
                            <a href="${assetUrl}" target="_blank" class="btn btn-sm btn-light">
                                <i class="fas fa-eye"></i>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    getStatusBadge(status) {
        const badges = {
            'completed': '<span class="badge bg-success">Completed</span>',
            'running': '<span class="badge bg-primary">Running</span>',
            'failed': '<span class="badge bg-danger">Failed</span>',
            'cancelled': '<span class="badge bg-warning">Cancelled</span>',
            'pending': '<span class="badge bg-secondary">Pending</span>'
        };

        return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize dashboard manager
window.dashboardManager = new DashboardManager();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardManager;
}

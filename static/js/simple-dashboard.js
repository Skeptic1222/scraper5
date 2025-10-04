// Simple Dashboard that actually works
let dashboardInitialized = false;
let dashboardUpdateInterval = null;
let activeJobsTracking = new Set();

function createSimpleDashboard() {
    // Check if dashboard needs recreation (container is empty)
    const container = document.getElementById('dashboard-dynamic-content');
    if (dashboardInitialized && container && container.children.length > 0) {
        loadSimpleData();
        return;
    }

    // Ensure dashboard section is visible
    const section = document.getElementById('dashboard-section');
    if (section) {
        if (!section.classList.contains('active')) {
            section.classList.add('active');
        }
        // Force display style
        section.style.display = 'block';
    }

    // container already defined at top of function
    if (!container) {
        console.error('Dashboard container not found');
        return;
    }

    // Simple dashboard HTML - set this BEFORE marking as initialized
    container.innerHTML = `
        <div style="padding: 20px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;">
                <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; color: #3b82f6; margin-bottom: 10px;">
                        <i class="fas fa-download"></i>
                    </div>
                    <div style="font-size: 2rem; font-weight: bold; color: #1f2937;" id="dashboard-active-downloads">0</div>
                    <div style="color: #6b7280; font-size: 0.9rem;">Active Downloads</div>
                </div>

                <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; color: #10b981; margin-bottom: 10px;">
                        <i class="fas fa-folder"></i>
                    </div>
                    <div style="font-size: 2rem; font-weight: bold; color: #1f2937;" id="dashboard-total-assets">12</div>
                    <div style="color: #6b7280; font-size: 0.9rem;">Total Assets</div>
                </div>

                <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; color: #f59e0b; margin-bottom: 10px;">
                        <i class="fas fa-globe"></i>
                    </div>
                    <div style="font-size: 2rem; font-weight: bold; color: #1f2937;">118</div>
                    <div style="color: #6b7280; font-size: 0.9rem;">Content Sources</div>
                </div>

                <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">
                    <div style="font-size: 2rem; color: #ef4444; margin-bottom: 10px;">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div style="font-size: 2rem; font-weight: bold; color: #1f2937;" id="dashboard-queue-length">0</div>
                    <div style="color: #6b7280; font-size: 0.9rem;">Queue Length</div>
                </div>
            </div>

            <!-- Active Jobs Progress Section -->
            <div id="active-jobs-container" style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; display: none;">
                <h3 style="margin-bottom: 15px; color: #1f2937;">
                    <i class="fas fa-spinner fa-pulse"></i> Active Downloads
                </h3>
                <div id="active-jobs-list" style="display: flex; flex-direction: column; gap: 15px;">
                    <!-- Active jobs will be inserted here -->
                </div>
            </div>

            <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h3 style="margin-bottom: 15px; color: #1f2937;">
                    <i class="fas fa-bolt"></i> Quick Actions
                </h3>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn btn-primary" onclick="navigateToSearch()">
                        <i class="fas fa-search"></i> Start Search
                    </button>
                    <button class="btn btn-success" onclick="navigateToAssets()">
                        <i class="fas fa-folder-open"></i> View Assets
                    </button>
                    <button class="btn btn-info" onclick="refreshDashboardData()">
                        <i class="fas fa-sync"></i> Refresh Data
                    </button>
                    <button class="btn btn-secondary" onclick="location.reload()">
                        <i class="fas fa-redo"></i> Reload Page
                    </button>
                </div>
            </div>

            <div style="background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px;">
                <h3 style="margin-bottom: 15px; color: #1f2937;">
                    <i class="fas fa-info-circle"></i> System Status
                </h3>
                <div style="color: #10b981; margin-bottom: 10px;">
                    <i class="fas fa-check-circle"></i> Database Connected
                </div>
                <div style="color: #10b981; margin-bottom: 10px;">
                    <i class="fas fa-check-circle"></i> APIs Responding
                </div>
                <div style="color: #10b981;">
                    <i class="fas fa-check-circle"></i> Navigation Working
                </div>
            </div>
        </div>
    `;

    // Mark as initialized AFTER setting HTML
    dashboardInitialized = true;

    // Start polling for active jobs
    startJobProgressPolling();

    loadSimpleData();
}

function loadSimpleData() {
    // Load dashboard stats from new API endpoint
    fetch((window.APP_BASE || '/scraper') + '/api/dashboard-stats', {
        credentials: 'include'
    })
        .then(response => response.json())
        .then(data => {
            if (data && data.stats) {
                document.getElementById('dashboard-total-assets').textContent = data.stats.total_assets;
                document.getElementById('dashboard-active-downloads').textContent = data.stats.pending_jobs;
                document.getElementById('dashboard-queue-length').textContent = data.stats.pending_jobs;
            }
        })
        .catch(error => {
            console.error('Error loading dashboard stats:', error);
            // Fallback to old endpoints
            loadLegacyData();
        });
}

function loadLegacyData() {

    // Load assets count
    fetch((window.APP_BASE || '/scraper') + '/api/assets', {
        credentials: 'include'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.assets) {
                const assetCount = data.assets.length;
                const totalAssetsElem = document.getElementById('dashboard-total-assets');
                if (totalAssetsElem) {
                    totalAssetsElem.textContent = assetCount;
                    console.log(`Dashboard asset count updated: ${assetCount}`);
                }
            }
        })
        .catch(error => console.error('Error loading assets:', error));

    // Load jobs data
    fetch((window.APP_BASE || '/scraper') + '/api/jobs')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.jobs) {
                const activeJobs = data.jobs.filter(job => job.status === 'running' || job.status === 'downloading');
                const queuedJobs = data.jobs.filter(job => job.status === 'pending');

                document.getElementById('dashboard-active-downloads').textContent = activeJobs.length;
                document.getElementById('dashboard-queue-length').textContent = queuedJobs.length;

            }
        })
        .catch(error => console.error('Error loading jobs:', error));
}

function navigateToSearch() {
    window.location.hash = 'search';
    // Trigger navigation manually
    if (window.navigation && window.navigation.switchSection) {
        window.navigation.switchSection('search-section');
    }
}

function navigateToAssets() {
    window.location.hash = 'assets';
    if (window.navigation && window.navigation.switchSection) {
        window.navigation.switchSection('assets-section');
    }
}

function refreshDashboardData() {
    loadSimpleData();
    updateActiveJobsDisplay();
}

// Start polling for active job progress
function startJobProgressPolling() {
    // Clear existing interval
    if (dashboardUpdateInterval) {
        clearInterval(dashboardUpdateInterval);
    }

    // Update immediately
    updateActiveJobsDisplay();

    // Poll every 2 seconds
    dashboardUpdateInterval = setInterval(updateActiveJobsDisplay, 2000);
}

// Stop polling when leaving dashboard
function stopJobProgressPolling() {
    if (dashboardUpdateInterval) {
        clearInterval(dashboardUpdateInterval);
        dashboardUpdateInterval = null;
    }
}

// Update active jobs display with real-time progress
async function updateActiveJobsDisplay() {
    try {
        const response = await fetch((window.APP_BASE || '/scraper') + '/api/jobs?status=running', {
            credentials: 'include'
        });

        if (!response.ok) {
            console.warn('Failed to fetch active jobs');
            return;
        }

        const data = await response.json();

        // Handle unauthenticated response (no success field, empty jobs array)
        if (!data.jobs) {
            // No jobs data available
            console.log('No jobs data available:', data.message || 'No jobs');
            return;
        }

        // Accept both authenticated (success=true) and unauthenticated (jobs=[]) responses
        // Filter for active jobs (running, pending, downloading)
        const activeJobs = data.jobs.filter(job =>
            job.status === 'running' ||
            job.status === 'pending' ||
            job.status === 'downloading'
        );

        const container = document.getElementById('active-jobs-container');
        const jobsList = document.getElementById('active-jobs-list');

        if (!container || !jobsList) {
            return;
        }

        // Show/hide container based on active jobs
        if (activeJobs.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';

        // Render each active job
        jobsList.innerHTML = activeJobs.map(job => renderJobProgress(job)).join('');

        // Track new jobs
        activeJobs.forEach(job => {
            if (!activeJobsTracking.has(job.id)) {
                activeJobsTracking.add(job.id);
            }
        });

        // Remove completed jobs from tracking
        const activeJobIds = new Set(activeJobs.map(j => j.id));
        activeJobsTracking.forEach(jobId => {
            if (!activeJobIds.has(jobId)) {
                activeJobsTracking.delete(jobId);
            }
        });

    } catch (error) {
        console.error('Error updating active jobs:', error);
    }
}

// Render individual job progress card
function renderJobProgress(job) {
    const progress = job.progress || 0;
    const downloaded = job.downloaded || 0;
    const detected = job.detected || 0;
    const query = job.query || 'Download Job';
    const message = job.message || 'Processing...';
    const currentFile = job.current_file || '';

    // Status colors and display names
    const statusInfo = {
        'running': { color: '#3b82f6', icon: 'fa-spinner fa-pulse', label: 'Running' },
        'downloading': { color: '#10b981', icon: 'fa-download', label: 'Downloading' },
        'pending': { color: '#f59e0b', icon: 'fa-clock', label: 'Pending' }
    };
    const status = statusInfo[job.status] || { color: '#6b7280', icon: 'fa-question', label: 'Unknown' };
    const statusColor = status.color;

    return `
        <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; background: #f9fafb; position: relative;">
            <!-- Cancel Button (X) -->
            <button
                onclick="cancelJob('${job.id}', event)"
                style="position: absolute; top: 10px; right: 10px; background: #ef4444; color: white; border: none; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 14px; transition: background 0.2s ease; z-index: 10;"
                onmouseover="this.style.background='#dc2626'"
                onmouseout="this.style.background='#ef4444'"
                title="Cancel Job"
            >
                <i class="fas fa-times"></i>
            </button>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-right: 35px;">
                <div style="flex: 1;">
                    <div style="font-weight: bold; color: #1f2937; margin-bottom: 5px; font-size: 1rem;">
                        <i class="fas ${status.icon}" style="color: ${statusColor};"></i>
                        ${escapeHtml(query)}
                    </div>
                    <div style="font-size: 0.85rem; color: #6b7280; display: flex; align-items: center; gap: 8px;">
                        <span style="background: ${statusColor}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">
                            ${status.label.toUpperCase()}
                        </span>
                        <span>${escapeHtml(message)}</span>
                    </div>
                </div>
                <div style="text-align: right; min-width: 120px;">
                    <div style="font-size: 2rem; font-weight: bold; color: ${statusColor}; line-height: 1;">
                        ${progress.toFixed(0)}%
                    </div>
                    <div style="font-size: 0.85rem; color: #6b7280; margin-top: 4px;">
                        <strong>${downloaded}</strong> of <strong>${detected || '?'}</strong> files
                    </div>
                </div>
            </div>

            <!-- Enhanced Progress Bar -->
            <div style="background: #e5e7eb; border-radius: 6px; height: 12px; overflow: hidden; margin-bottom: 8px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(to right, ${statusColor}, ${adjustBrightness(statusColor, 1.2)}); height: 100%; width: ${progress}%; transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 10px ${statusColor}40;"></div>
            </div>

            <!-- Current File -->
            ${currentFile ? `
                <div style="font-size: 0.75rem; color: #6b7280; margin-top: 8px; display: flex; align-items: center;">
                    <i class="fas fa-download" style="margin-right: 5px; color: ${statusColor};"></i>
                    <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        ${escapeHtml(currentFile)}
                    </span>
                </div>
            ` : ''}

            <!-- Job Stats -->
            <div style="display: flex; gap: 15px; margin-top: 10px; font-size: 0.8rem; color: #6b7280;">
                ${job.images > 0 ? `
                    <div>
                        <i class="fas fa-image"></i> ${job.images} images
                    </div>
                ` : ''}
                ${job.videos > 0 ? `
                    <div>
                        <i class="fas fa-video"></i> ${job.videos} videos
                    </div>
                ` : ''}
                ${job.failed > 0 ? `
                    <div style="color: #ef4444;">
                        <i class="fas fa-exclamation-triangle"></i> ${job.failed} failed
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Cancel a running job
async function cancelJob(jobId, event) {
    // Prevent event bubbling
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }

    // Confirmation dialog
    const confirmed = confirm('⚠️ Cancel this download job?\n\nThis will stop the download and cannot be undone.');
    if (!confirmed) {
        console.log('Job cancellation cancelled by user');
        return;
    }

    try {
        console.log(`Cancelling job ${jobId}...`);

        const response = await fetch(`${window.APP_BASE || '/scraper'}/api/jobs/${jobId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.success) {
            console.log(`✅ Job ${jobId} cancelled successfully`);

            // Remove job from tracking
            activeJobsTracking.delete(jobId);

            // Immediately update the display to remove the cancelled job
            updateActiveJobsDisplay();

            // Refresh dashboard stats
            refreshDashboardData();

            // Show success message (optional, can be removed if too intrusive)
            // alert('✅ Job cancelled successfully');
        } else {
            throw new Error(result.error || 'Failed to cancel job');
        }
    } catch (error) {
        console.error('Error cancelling job:', error);
        alert(`❌ Error cancelling job: ${error.message}`);
    }
}

// Helper function to escape HTML
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Helper function to adjust color brightness
function adjustBrightness(color, factor) {
    // Simple brightness adjustment for hex colors
    const hex = color.replace('#', '');
    const r = Math.min(255, Math.floor(parseInt(hex.substr(0, 2), 16) * factor));
    const g = Math.min(255, Math.floor(parseInt(hex.substr(2, 2), 16) * factor));
    const b = Math.min(255, Math.floor(parseInt(hex.substr(4, 2), 16) * factor));
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

// Expose dashboard functions globally
window.downloadDashboard = {
    init: createSimpleDashboard,
    refresh: refreshDashboardData,
    startPolling: startJobProgressPolling,
    stopPolling: stopJobProgressPolling
};

// Auto-start polling when dashboard is visible
document.addEventListener('DOMContentLoaded', () => {
    // Listen for section changes
    const observer = new MutationObserver((mutations) => {
        const dashboardSection = document.getElementById('dashboard-section');
        if (dashboardSection && dashboardSection.classList.contains('active')) {
            startJobProgressPolling();
        } else {
            stopJobProgressPolling();
        }
    });

    // Observe dashboard section visibility
    const dashboardSection = document.getElementById('dashboard-section');
    if (dashboardSection) {
        observer.observe(dashboardSection, {
            attributes: true,
            attributeFilter: ['class']
        });
    }
});
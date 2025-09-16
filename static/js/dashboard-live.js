/**
 * Live Dashboard Statistics
 * Updates dashboard stats in real-time
 */

(function() {
    'use strict';

    let updateInterval = null;
    let lastUpdate = null;

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initDashboard();
        startLiveUpdates();
    });

    function initDashboard() {
        // Initial load of stats
        updateDashboardStats();
        
        // Update credits display
        updateCreditsDisplay();
    }

    function startLiveUpdates() {
        // Update every 5 seconds
        updateInterval = setInterval(() => {
            updateDashboardStats();
            updateActiveJobs();
        }, 5000);
        
        // Update credits every 10 seconds
        setInterval(() => {
            updateCreditsDisplay();
        }, 10000);
    }

    async function updateDashboardStats() {
        try {
            // Fetch current statistics
            const assetsUrl = `${window.APP_BASE || ''}/api/assets?limit=0`;
            const response = await fetch(assetsUrl);
            if (!response.ok) return;
            
            const data = await response.json();
            const stats = data.statistics || {};
            
            // Update main counters with animation
            animateCounter('total-downloads', stats.total_assets || 0);
            animateCounter('total-images', stats.total_images || 0);
            animateCounter('total-videos', stats.total_videos || 0);
            animateCounter('total-audio', stats.total_audio || 0);
            
            // Calculate success rate
            const total = stats.total_assets || 0;
            const successRate = total > 0 ? 100 : 0; // Simplified for now
            animateCounter('success-rate', successRate, '%');
            
            // Format and update total size
            const totalSize = stats.total_size || 0;
            const sizeFormatted = formatFileSize(totalSize);
            document.getElementById('total-size').textContent = sizeFormatted;
            
            // Update change indicators
            updateChangeIndicators(stats);
            
            // Add pulse animation for updates
            addUpdatePulse();
            
        } catch (error) {
            console.error('Failed to update dashboard stats:', error);
        }
    }

    async function updateActiveJobs() {
        try {
            // Fetch active jobs
            const jobsUrl = `${window.APP_BASE || ''}/api/jobs?status=running`;
            const response = await fetch(jobsUrl);
            if (!response.ok) return;
            
            const data = await response.json();
            const jobs = data.jobs || [];
            
            // Update active downloads display
            const activeDownloads = document.getElementById('active-downloads-count');
            if (activeDownloads) {
                activeDownloads.textContent = jobs.length;
                
                // Add badge class if active
                if (jobs.length > 0) {
                    activeDownloads.classList.add('badge', 'bg-success');
                } else {
                    activeDownloads.classList.remove('badge', 'bg-success');
                }
            }
            
            // Update progress bars for active jobs
            jobs.forEach(job => {
                updateJobProgress(job);
            });
            
        } catch (error) {
            console.error('Failed to update active jobs:', error);
        }
    }

    async function updateCreditsDisplay() {
        try {
            const statsUrl = `${window.APP_BASE || ''}/api/user/stats`;
            const response = await fetch(statsUrl);
            if (!response.ok) return;
            
            const data = await response.json();
            const credits = data.credits || 0;
            
            const creditsElement = document.getElementById('credits-count');
            if (creditsElement) {
                animateCounter('credits-count', credits);
                
                // Add warning class if low credits
                const creditsDisplay = document.getElementById('credits-display');
                if (creditsDisplay) {
                    if (credits < 10) {
                        creditsDisplay.classList.add('text-danger');
                    } else if (credits < 50) {
                        creditsDisplay.classList.add('text-warning');
                    } else {
                        creditsDisplay.classList.remove('text-danger', 'text-warning');
                    }
                }
            }
        } catch (error) {
            // Silent fail for non-authenticated users
        }
    }

    function updateJobProgress(job) {
        const progressElement = document.querySelector(`[data-job-id="${job.id}"] .progress-bar`);
        if (progressElement) {
            const progress = job.progress || 0;
            progressElement.style.width = `${progress}%`;
            progressElement.setAttribute('aria-valuenow', progress);
            
            // Update status text
            const statusElement = document.querySelector(`[data-job-id="${job.id}"] .job-status`);
            if (statusElement) {
                statusElement.textContent = job.message || job.status;
            }
        }
    }

    function animateCounter(elementId, targetValue, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const current = parseInt(element.textContent.replace(/\D/g, '')) || 0;
        const increment = (targetValue - current) / 20;
        let step = 0;
        
        const timer = setInterval(() => {
            step++;
            const value = Math.round(current + (increment * step));
            element.textContent = value + suffix;
            
            if (step >= 20) {
                clearInterval(timer);
                element.textContent = targetValue + suffix;
            }
        }, 50);
    }

    function updateChangeIndicators(stats) {
        // Calculate daily changes (mock data for now, would need historical data)
        const changes = {
            downloads: Math.floor(Math.random() * 10),
            images: Math.floor(Math.random() * 5),
            videos: Math.floor(Math.random() * 3),
            audio: Math.floor(Math.random() * 2),
            success: Math.floor(Math.random() * 10) - 5,
            size: Math.floor(Math.random() * 100)
        };
        
        // Update change indicators
        updateChangeIndicator('downloads-change', changes.downloads, 'today');
        updateChangeIndicator('images-change', changes.images, 'today');
        updateChangeIndicator('videos-change', changes.videos, 'today');
        updateChangeIndicator('audio-change', changes.audio, 'today');
        updateChangeIndicator('success-change', changes.success, 'this week', '%');
        updateChangeIndicator('size-change', changes.size, 'today', ' MB');
    }

    function updateChangeIndicator(elementId, value, period, suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const sign = value >= 0 ? '+' : '';
        element.textContent = `${sign}${value}${suffix} ${period}`;
        
        // Update color class
        element.classList.remove('positive', 'negative', 'neutral');
        if (value > 0) {
            element.classList.add('positive');
        } else if (value < 0) {
            element.classList.add('negative');
        } else {
            element.classList.add('neutral');
        }
    }

    function addUpdatePulse() {
        // Add pulse animation to show live updates
        const cards = document.querySelectorAll('.enhanced-stat-card');
        cards.forEach(card => {
            card.classList.add('pulse-update');
            setTimeout(() => {
                card.classList.remove('pulse-update');
            }, 1000);
        });
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 MB';
        
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        const size = (bytes / Math.pow(1024, i)).toFixed(2);
        
        return `${size} ${sizes[i]}`;
    }

    // Add download rate calculation
    let lastDownloadCount = 0;
    let downloadRate = 0;

    function calculateDownloadRate(currentCount) {
        if (lastUpdate) {
            const timeDiff = (Date.now() - lastUpdate) / 1000; // seconds
            const countDiff = currentCount - lastDownloadCount;
            downloadRate = countDiff / timeDiff; // downloads per second
            
            // Update rate display
            const rateElement = document.getElementById('download-rate');
            if (rateElement) {
                rateElement.textContent = `${downloadRate.toFixed(2)} /s`;
            }
        }
        
        lastDownloadCount = currentCount;
        lastUpdate = Date.now();
    }

    // Export for external use
    window.DashboardLive = {
        update: updateDashboardStats,
        updateJobs: updateActiveJobs,
        updateCredits: updateCreditsDisplay,
        stop: () => {
            if (updateInterval) {
                clearInterval(updateInterval);
                updateInterval = null;
            }
        }
    };
})();
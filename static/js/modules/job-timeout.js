/**
 * Job Timeout and Timer Module
 * Handles job timeout settings and displays elapsed time timer
 */

// Global timer state
let jobTimerInterval = null;
let jobStartTime = null;
let jobTimeoutSeconds = 0;

document.addEventListener('DOMContentLoaded', () => {
    const timeoutSelect = document.getElementById('job-timeout');
    const customTimeoutContainer = document.getElementById('custom-timeout-container');

    // Handle timeout selection changes
    if (timeoutSelect) {
        timeoutSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                customTimeoutContainer.style.display = 'block';
            } else {
                customTimeoutContainer.style.display = 'none';
            }
        });
    }
});

/**
 * Get the timeout value in seconds
 */
function getTimeoutSeconds() {
    const timeoutSelect = document.getElementById('job-timeout');
    if (!timeoutSelect) return 0;

    const value = timeoutSelect.value;

    if (value === 'custom') {
        const hoursInput = document.getElementById('custom-timeout-hours');
        const minutesInput = document.getElementById('custom-timeout-minutes');

        const hours = parseInt(hoursInput?.value || 0);
        const minutes = parseInt(minutesInput?.value || 0);

        return (hours * 3600) + (minutes * 60);
    } else if (value === '0') {
        return 0; // Unlimited
    } else {
        return parseInt(value);
    }
}

/**
 * Format seconds to HH:MM:SS or MM:SS
 */
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

/**
 * Format timeout display text
 */
function formatTimeoutDisplay(seconds) {
    if (seconds === 0) {
        return 'Unlimited';
    }

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0 && minutes > 0) {
        return `${hours}h ${minutes}m`;
    } else if (hours > 0) {
        return `${hours} hour${hours > 1 ? 's' : ''}`;
    } else {
        return `${minutes} min${minutes > 1 ? 's' : ''}`;
    }
}

/**
 * Start the job timer
 */
function startJobTimer(timeoutSeconds = 0) {
    // Clear any existing timer
    stopJobTimer();

    // Set start time and timeout
    jobStartTime = Date.now();
    jobTimeoutSeconds = timeoutSeconds;

    // Update timeout display
    const timeoutDisplay = document.getElementById('timeout-display');
    if (timeoutDisplay) {
        timeoutDisplay.textContent = formatTimeoutDisplay(timeoutSeconds);
    }

    // Start interval to update elapsed time
    jobTimerInterval = setInterval(() => {
        const elapsedSeconds = Math.floor((Date.now() - jobStartTime) / 1000);

        // Update elapsed time display
        const elapsedTimeElem = document.getElementById('elapsed-time');
        if (elapsedTimeElem) {
            elapsedTimeElem.textContent = formatTime(elapsedSeconds);
        }

        // Check if timeout reached (if not unlimited)
        if (timeoutSeconds > 0 && elapsedSeconds >= timeoutSeconds) {
            handleJobTimeout();
        }

        // Update timer color based on remaining time
        const jobTimerBadge = document.getElementById('job-timer');
        if (jobTimerBadge && timeoutSeconds > 0) {
            const remainingSeconds = timeoutSeconds - elapsedSeconds;
            const percentRemaining = (remainingSeconds / timeoutSeconds) * 100;

            // Change color based on remaining time
            if (percentRemaining < 10) {
                jobTimerBadge.className = 'badge bg-danger text-white ms-2';
            } else if (percentRemaining < 25) {
                jobTimerBadge.className = 'badge bg-warning text-dark ms-2';
            } else {
                jobTimerBadge.className = 'badge bg-light text-primary ms-2';
            }
        }
    }, 1000);
}

/**
 * Stop the job timer
 */
function stopJobTimer() {
    if (jobTimerInterval) {
        clearInterval(jobTimerInterval);
        jobTimerInterval = null;
    }
    jobStartTime = null;
}

/**
 * Handle job timeout
 */
function handleJobTimeout() {
    stopJobTimer();

    // Update UI to show timeout
    const progressText = document.getElementById('overall-progress-text');
    if (progressText) {
        progressText.textContent = 'Timeout reached';
    }

    const progressBar = document.getElementById('overall-progress-bar');
    if (progressBar) {
        progressBar.classList.remove('progress-bar-animated');
        progressBar.classList.add('bg-warning');
    }

    // Show notification
    if (typeof showNotification === 'function') {
        showNotification('Job timeout reached. Download stopped.', 'warning');
    }

    // Try to cancel the job via API
    const currentJobId = window.currentJobId;
    if (currentJobId) {
        cancelJob(currentJobId);
    }
}

/**
 * Cancel a job via API
 */
async function cancelJob(jobId) {
    try {
        const response = await fetch(`${window.APP_BASE || '/scraper'}/api/jobs/${jobId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (response.ok) {
            console.log(`Job ${jobId} cancelled due to timeout`);
        }
    } catch (error) {
        console.error('Error cancelling job:', error);
    }
}

/**
 * Reset timer display
 */
function resetTimerDisplay() {
    const elapsedTimeElem = document.getElementById('elapsed-time');
    const timeoutDisplay = document.getElementById('timeout-display');
    const jobTimerBadge = document.getElementById('job-timer');

    if (elapsedTimeElem) elapsedTimeElem.textContent = '00:00';
    if (timeoutDisplay) timeoutDisplay.textContent = 'Unlimited';
    if (jobTimerBadge) jobTimerBadge.className = 'badge bg-light text-primary ms-2';
}

// Export functions for use by other modules
window.getTimeoutSeconds = getTimeoutSeconds;
window.startJobTimer = startJobTimer;
window.stopJobTimer = stopJobTimer;
window.resetTimerDisplay = resetTimerDisplay;
window.formatTime = formatTime;
window.formatTimeoutDisplay = formatTimeoutDisplay;

/**
 * URL Scraper Module
 * Handles direct URL scraping functionality
 */

// Mode switching between keyword search and URL paste
document.addEventListener('DOMContentLoaded', () => {
    const modeKeyword = document.getElementById('mode-keyword');
    const modeUrl = document.getElementById('mode-url');
    const keywordContainer = document.getElementById('keyword-search-container');
    const urlContainer = document.getElementById('url-paste-container');
    const urlScrapeBtn = document.getElementById('url-scrape-btn');
    const urlInput = document.getElementById('url-paste-input');
    const sourceCategories = document.querySelector('#source-categories')?.closest('.card');

    // Toggle between keyword search and URL paste modes
    function switchMode(mode) {
        if (mode === 'keyword') {
            keywordContainer.style.display = 'block';
            urlContainer.style.display = 'none';
            if (sourceCategories) sourceCategories.style.display = 'block';
        } else {
            keywordContainer.style.display = 'none';
            urlContainer.style.display = 'block';
            if (sourceCategories) sourceCategories.style.display = 'none';
        }
    }

    if (modeKeyword) {
        modeKeyword.addEventListener('change', () => {
            if (modeKeyword.checked) switchMode('keyword');
        });
    }

    if (modeUrl) {
        modeUrl.addEventListener('change', () => {
            if (modeUrl.checked) switchMode('url');
        });
    }

    // Handle URL scrape button click
    if (urlScrapeBtn) {
        urlScrapeBtn.addEventListener('click', async () => {
            const url = urlInput.value.trim();

            if (!url) {
                showNotification('Please enter a URL', 'warning');
                urlInput.focus();
                return;
            }

            // Basic URL validation
            if (!url.startsWith('http://') && !url.startsWith('https://')) {
                showNotification('Invalid URL. Must start with http:// or https://', 'error');
                urlInput.focus();
                return;
            }

            // Disable button during request
            urlScrapeBtn.disabled = true;
            urlScrapeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';

            try {
                // Call the scrape-url API endpoint
                const response = await fetch(`${window.APP_BASE || '/scraper'}/api/scrape-url`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify({ url: url })
                });

                const data = await response.json();

                if (data.success) {
                    showNotification(
                        `URL scraping started! Detected: ${data.source} (using ${data.method})`,
                        'success'
                    );

                    // Clear input
                    urlInput.value = '';

                    // Show progress container
                    const progressContainer = document.getElementById('search-progress-container');
                    if (progressContainer) {
                        progressContainer.style.display = 'block';
                    }

                    // Start polling for job status
                    if (data.job_id && typeof window.startJobPolling === 'function') {
                        window.startJobPolling(data.job_id);
                    } else if (data.job_id) {
                        // Fallback: manual polling
                        pollJobStatus(data.job_id);
                    }
                } else {
                    showNotification(`Error: ${data.error}`, 'error');
                }
            } catch (error) {
                console.error('URL scrape error:', error);
                showNotification(`Request failed: ${error.message}`, 'error');
            } finally {
                // Re-enable button
                urlScrapeBtn.disabled = false;
                urlScrapeBtn.innerHTML = '<i class="fas fa-download"></i> Scrape URL';
            }
        });
    }

    // Allow Enter key to trigger scrape
    if (urlInput) {
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                urlScrapeBtn.click();
            }
        });
    }
});

/**
 * Poll job status for URL scraping
 */
function pollJobStatus(jobId) {
    const pollInterval = 1000; // 1 second
    const maxPolls = 600; // 10 minutes max
    let pollCount = 0;

    const intervalId = setInterval(async () => {
        pollCount++;

        if (pollCount > maxPolls) {
            clearInterval(intervalId);
            showNotification('Job polling timeout', 'warning');
            return;
        }

        try {
            const response = await fetch(`${window.APP_BASE || '/scraper'}/api/job-progress/${jobId}`, {
                credentials: 'include'
            });

            if (!response.ok) {
                clearInterval(intervalId);
                showNotification('Failed to get job status', 'error');
                return;
            }

            const data = await response.json();

            // Update progress UI
            updateProgressUI(data);

            // Check if job is complete
            if (data.status === 'completed') {
                clearInterval(intervalId);
                showNotification(
                    `Download complete! ${data.downloaded_count || 0} file(s) downloaded`,
                    'success'
                );

                // Refresh asset library if available
                if (window.assetLibrary && typeof window.assetLibrary.loadAssets === 'function') {
                    window.assetLibrary.loadAssets();
                }
            } else if (data.status === 'error' || data.status === 'failed') {
                clearInterval(intervalId);
                showNotification(`Job failed: ${data.current_file || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, pollInterval);
}

/**
 * Update progress UI with job data
 */
function updateProgressUI(jobData) {
    // Update progress bar
    const progressBar = document.getElementById('overall-progress-bar');
    const progressText = document.getElementById('overall-progress-text');
    if (progressBar && progressText) {
        const progress = jobData.overall_progress || 0;
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;
    }

    // Update counts
    const downloadedCount = document.getElementById('downloaded-count');
    const successCount = document.getElementById('success-count');
    const retryCount = document.getElementById('retry-count');
    const errorCount = document.getElementById('error-count');

    if (downloadedCount) downloadedCount.textContent = jobData.downloaded_count || 0;
    if (successCount) successCount.textContent = jobData.success_count || 0;
    if (retryCount) retryCount.textContent = jobData.retry_count || 0;
    if (errorCount) errorCount.textContent = jobData.error_count || 0;

    // Update log
    const progressLog = document.getElementById('search-progress-log');
    if (progressLog && jobData.current_file) {
        const logEntry = document.createElement('div');
        logEntry.className = 'text-success mb-1';
        logEntry.innerHTML = `<i class="fas fa-check-circle"></i> ${jobData.current_file}`;
        progressLog.appendChild(logEntry);

        // Scroll to bottom
        progressLog.scrollTop = progressLog.scrollHeight;

        // Limit log entries to last 50
        while (progressLog.children.length > 50) {
            progressLog.removeChild(progressLog.firstChild);
        }
    }
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Try to use existing notification system
    if (typeof window.showToast === 'function') {
        window.showToast(message, type);
        return;
    }

    // Fallback: use alert or console
    if (type === 'error') {
        console.error(message);
        alert(message);
    } else if (type === 'warning') {
        console.warn(message);
    } else {
        console.log(message);
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { pollJobStatus, updateProgressUI, showNotification };
}

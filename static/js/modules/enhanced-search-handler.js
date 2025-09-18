/**
 * Enhanced Search Handler with Video and Adult Content Support
 */
class EnhancedSearchHandler {
    constructor() {
        this.currentJobId = null;
        this.pollInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.addEnhancedControls();
    }

    addEnhancedControls() {
        // Find the search form
        const searchForm = document.querySelector('.search-form');
        if (!searchForm) return;

        // Create enhanced controls container
        const controlsDiv = document.createElement('div');
        controlsDiv.className = 'enhanced-controls';
        controlsDiv.style.cssText = `
            display: flex;
            gap: 20px;
            margin-top: 15px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            flex-wrap: wrap;
            align-items: center;
        `;

        // Video download toggle
        const videoToggle = this.createToggle('include-videos', 'Include Videos', 
            'Download videos from YouTube, TikTok, etc.', false);
        
        // Safe search bypass toggle
        const safeSearchToggle = this.createToggle('bypass-safe-search', 'Bypass Safe Search', 
            'Disable content filtering (18+ only)', false);
        
        // Adult content toggle
        const adultToggle = this.createToggle('include-adult', 'Include Adult Content', 
            'Search adult content sources (18+ only)', false);
        
        // Advanced settings button
        const advancedBtn = document.createElement('button');
        advancedBtn.className = 'btn-advanced';
        advancedBtn.innerHTML = `
            <i class="fas fa-cog"></i>
            Advanced Settings
        `;
        advancedBtn.style.cssText = `
            padding: 8px 16px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        `;
        advancedBtn.addEventListener('click', () => this.showAdvancedSettings());

        // Add controls to container
        controlsDiv.appendChild(videoToggle);
        controlsDiv.appendChild(safeSearchToggle);
        controlsDiv.appendChild(adultToggle);
        controlsDiv.appendChild(advancedBtn);

        // Insert after search form
        const searchContainer = searchForm.parentElement;
        searchContainer.appendChild(controlsDiv);

        // Add warning for adult content
        this.addAgeWarning(controlsDiv);
    }

    createToggle(id, label, description, defaultChecked = false) {
        const toggleDiv = document.createElement('div');
        toggleDiv.className = 'toggle-control';
        toggleDiv.style.cssText = 'display: flex; align-items: center; gap: 10px;';
        
        toggleDiv.innerHTML = `
            <label class="switch" style="position: relative; display: inline-block; width: 50px; height: 24px;">
                <input type="checkbox" id="${id}" ${defaultChecked ? 'checked' : ''}>
                <span class="slider" style="
                    position: absolute;
                    cursor: pointer;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-color: #ccc;
                    transition: .4s;
                    border-radius: 24px;
                "></span>
            </label>
            <div>
                <span style="font-weight: 500; color: var(--text-primary);">${label}</span>
                <br>
                <small style="color: var(--text-secondary);">${description}</small>
            </div>
        `;

        // Add toggle styling
        const style = document.createElement('style');
        style.textContent = `
            .switch input {
                opacity: 0;
                width: 0;
                height: 0;
            }
            .switch input:checked + .slider {
                background-color: var(--primary-color);
            }
            .switch .slider:before {
                position: absolute;
                content: "";
                height: 18px;
                width: 18px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }
            .switch input:checked + .slider:before {
                transform: translateX(26px);
            }
        `;
        if (!document.querySelector('style[data-enhanced-toggle]')) {
            style.setAttribute('data-enhanced-toggle', 'true');
            document.head.appendChild(style);
        }

        return toggleDiv;
    }

    addAgeWarning(container) {
        const warningDiv = document.createElement('div');
        warningDiv.id = 'age-warning';
        warningDiv.style.cssText = `
            display: none;
            margin-top: 10px;
            padding: 10px;
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            border-radius: 6px;
            color: #ffc107;
            font-size: 14px;
        `;
        warningDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <strong>Warning:</strong> Adult content features are enabled. You must be 18+ to use these features.
            Content may be explicit and NSFW.
        `;
        container.appendChild(warningDiv);

        // Show/hide warning based on toggles
        const adultToggle = document.getElementById('include-adult');
        const safeSearchToggle = document.getElementById('bypass-safe-search');
        
        const checkWarning = () => {
            if (adultToggle?.checked || safeSearchToggle?.checked) {
                warningDiv.style.display = 'block';
            } else {
                warningDiv.style.display = 'none';
            }
        };

        adultToggle?.addEventListener('change', checkWarning);
        safeSearchToggle?.addEventListener('change', checkWarning);
    }

    showAdvancedSettings() {
        // Create modal for advanced settings
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        `;

        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 12px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        `;

        modalContent.innerHTML = `
            <h3>Advanced Search Settings</h3>
            <div style="margin-top: 20px;">
                <h4>Video Sources</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
                    <label><input type="checkbox" value="youtube" checked> YouTube</label>
                    <label><input type="checkbox" value="tiktok" checked> TikTok</label>
                    <label><input type="checkbox" value="vimeo"> Vimeo</label>
                    <label><input type="checkbox" value="dailymotion"> Dailymotion</label>
                    <label><input type="checkbox" value="twitch"> Twitch Clips</label>
                    <label><input type="checkbox" value="instagram"> Instagram Reels</label>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <h4>Adult Sources (18+)</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
                    <label><input type="checkbox" value="motherless"> Motherless</label>
                    <label><input type="checkbox" value="xvideos"> XVideos</label>
                    <label><input type="checkbox" value="xhamster"> XHamster</label>
                    <label><input type="checkbox" value="pornhub"> PornHub</label>
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <h4>Download Settings</h4>
                <div style="margin-top: 10px;">
                    <label>Max file size (MB): <input type="number" id="max-file-size" value="500" min="10" max="2000"></label>
                </div>
                <div style="margin-top: 10px;">
                    <label>Video quality: 
                        <select id="video-quality">
                            <option value="best">Best Available</option>
                            <option value="1080p">1080p</option>
                            <option value="720p">720p</option>
                            <option value="480p">480p</option>
                        </select>
                    </label>
                </div>
            </div>
            
            <div style="margin-top: 30px; display: flex; justify-content: flex-end; gap: 10px;">
                <button onclick="this.closest('.modal-overlay').remove()" style="padding: 10px 20px; border: 1px solid #ccc; background: white; border-radius: 6px; cursor: pointer;">Cancel</button>
                <button onclick="window.enhancedSearchHandler.saveAdvancedSettings(this)" style="padding: 10px 20px; background: var(--primary-color); color: white; border: none; border-radius: 6px; cursor: pointer;">Save Settings</button>
            </div>
        `;

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    saveAdvancedSettings(button) {
        // Save settings to localStorage
        const modal = button.closest('.modal-overlay');
        const settings = {
            videoSources: Array.from(modal.querySelectorAll('input[type="checkbox"]:checked'))
                .map(cb => cb.value),
            maxFileSize: modal.querySelector('#max-file-size').value,
            videoQuality: modal.querySelector('#video-quality').value
        };
        
        localStorage.setItem('enhancedSearchSettings', JSON.stringify(settings));
        
        // Show success message
        const successMsg = document.createElement('div');
        successMsg.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            z-index: 10001;
            animation: slideIn 0.3s;
        `;
        successMsg.textContent = '✓ Settings saved successfully!';
        document.body.appendChild(successMsg);
        
        setTimeout(() => successMsg.remove(), 3000);
        modal.remove();
    }

    setupEventListeners() {
        // Override the existing search button handler
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.performEnhancedSearch();
            });
        }

        // Handle enter key in search input
        const searchInput = document.getElementById('search-query');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.performEnhancedSearch();
                }
            });
        }
    }

    async performEnhancedSearch() {
        const query = document.getElementById('search-query')?.value?.trim();
        if (!query) {
            this.showNotification('Please enter a search query', 'error');
            return;
        }

        // Get enhanced options
        const includeVideos = document.getElementById('include-videos')?.checked || false;
        const includeAdult = document.getElementById('include-adult')?.checked || false;
        const bypassSafeSearch = document.getElementById('bypass-safe-search')?.checked || false;

        // Get selected sources
        const selectedSources = Array.from(document.querySelectorAll('.source-checkbox:checked'))
            .map(cb => cb.value);

        if (selectedSources.length === 0) {
            selectedSources.push('google', 'bing', 'duckduckgo');
        }

        // Show loading state
        this.showLoadingState();

        try {
            const response = await fetch('/api/enhanced-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    sources: selectedSources,
                    max_content: 30,
                    include_videos: includeVideos,
                    include_adult: includeAdult,
                    bypass_safe_search: bypassSafeSearch
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentJobId = data.job_id;
                this.showNotification(
                    `Enhanced search started! ${data.safe_search_enabled ? 'Safe search: ON' : 'Safe search: BYPASSED'}`, 
                    'success'
                );
                this.startPolling();
            } else {
                // Fallback to regular search if enhanced not available
                this.performRegularSearch(query, selectedSources);
            }
        } catch (error) {
            console.error('Enhanced search error:', error);
            // Fallback to regular search
            this.performRegularSearch(query, selectedSources);
        }
    }

    async performRegularSearch(query, sources) {
        // Fallback to regular comprehensive search
        try {
            const response = await fetch('/api/comprehensive-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    search_type: 'all',
                    max_content: 20,
                    enabled_sources: sources
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentJobId = data.job_id;
                this.showNotification('Search started!', 'success');
                this.startPolling();
            } else {
                this.showNotification(data.error || 'Search failed', 'error');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showNotification('Failed to start search', 'error');
        }
    }

    startPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        // Poll for job status
        this.pollInterval = setInterval(() => {
            this.checkJobStatus();
        }, 2000);
    }

    async checkJobStatus() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`/api/job-progress/${this.currentJobId}`);
            const data = await response.json();

            if (data.status === 'completed' || data.status === 'error') {
                clearInterval(this.pollInterval);
                this.pollInterval = null;
                
                if (data.status === 'completed') {
                    this.showNotification(
                        `Search completed! Downloaded ${data.downloaded || 0} files`, 
                        'success'
                    );
                } else {
                    this.showNotification('Search failed: ' + (data.message || 'Unknown error'), 'error');
                }
                
                this.hideLoadingState();
            }
        } catch (error) {
            console.error('Error checking job status:', error);
        }
    }

    showLoadingState() {
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.disabled = true;
            searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
        }
    }

    hideLoadingState() {
        const searchBtn = document.getElementById('search-btn');
        if (searchBtn) {
            searchBtn.disabled = false;
            searchBtn.innerHTML = '<i class="fas fa-search"></i> Search';
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 10000;
            animation: slideIn 0.3s;
            max-width: 400px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        `;

        const colors = {
            success: '#4CAF50',
            error: '#f44336',
            warning: '#ff9800',
            info: '#2196F3'
        };

        notification.style.background = colors[type] || colors.info;
        notification.style.color = 'white';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s';
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
}

// Initialize the enhanced search handler
window.enhancedSearchHandler = new EnhancedSearchHandler();

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
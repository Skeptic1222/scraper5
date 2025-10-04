/**
 * Settings Module
 * Handles user preferences storage and persistence
 */
class SettingsManager {
    constructor() {
        this.settings = this.loadSettings();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.applySettings();
    }

    setupEventListeners() {
        // Save settings button
        const saveButton = document.querySelector('#settings-section .btn-primary');
        if (saveButton) {
            saveButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.saveSettings();
            });
        }

        // Listen for changes to safe search toggle in settings
        const settingsSafeSearch = document.querySelector('#settings-section #safe-search-toggle');
        if (settingsSafeSearch) {
            settingsSafeSearch.addEventListener('change', (e) => {
                this.settings.safeSearch = e.target.checked;
                // Sync with search section toggle
                const searchSafeSearch = document.querySelector('#search-section #safe-search-toggle');
                if (searchSafeSearch) {
                    searchSafeSearch.checked = e.target.checked;
                }
            });
        }

        // Listen for changes to safe search toggle in search section
        const searchSafeSearch = document.querySelector('#search-section #safe-search-toggle');
        if (searchSafeSearch) {
            searchSafeSearch.addEventListener('change', (e) => {
                this.settings.safeSearch = e.target.checked;
                // Sync with settings section toggle
                const settingsSafeSearch = document.querySelector('#settings-section #safe-search-toggle');
                if (settingsSafeSearch) {
                    settingsSafeSearch.checked = e.target.checked;
                }
                // Auto-save this setting
                this.saveToLocalStorage();
            });
        }

        // Download quality
        const qualitySelect = document.querySelector('#settings-section select.form-select');
        if (qualitySelect) {
            qualitySelect.addEventListener('change', (e) => {
                this.settings.downloadQuality = e.target.value;
            });
        }

        // Concurrent downloads
        const concurrentInput = document.querySelector('#settings-section input[type="number"]');
        if (concurrentInput) {
            concurrentInput.addEventListener('change', (e) => {
                this.settings.concurrentDownloads = parseInt(e.target.value);
            });
        }
    }

    loadSettings() {
        // Load from localStorage
        const stored = localStorage.getItem('enhanced_media_scraper_settings');
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch (e) {
                console.error('Failed to parse stored settings:', e);
            }
        }

        // Return default settings
        return {
            safeSearch: true,
            downloadQuality: 'medium',
            concurrentDownloads: 5,
            theme: 'light',
            autoPlay: false,
            notifications: true
        };
    }

    applySettings() {
        // Apply safe search setting to both toggles
        const searchToggle = document.querySelector('#search-section #safe-search-toggle');
        const settingsToggle = document.querySelector('#settings-section #safe-search-toggle');

        if (searchToggle) {
            searchToggle.checked = this.settings.safeSearch;
        }
        if (settingsToggle) {
            settingsToggle.checked = this.settings.safeSearch;
        }

        // Apply download quality
        const qualitySelect = document.querySelector('#settings-section select.form-select');
        if (qualitySelect) {
            qualitySelect.value = this.settings.downloadQuality;
        }

        // Apply concurrent downloads
        const concurrentInput = document.querySelector('#settings-section input[type="number"]');
        if (concurrentInput) {
            concurrentInput.value = this.settings.concurrentDownloads;
        }

        console.log('Settings applied:', this.settings);
    }

    saveSettings() {
        // Save to localStorage
        this.saveToLocalStorage();

        // Save to backend (if user is logged in)
        this.saveToBackend();

        // Show success message
        this.showNotification('Settings saved successfully!', 'success');
    }

    saveToLocalStorage() {
        try {
            localStorage.setItem('enhanced_media_scraper_settings', JSON.stringify(this.settings));
            console.log('Settings saved to localStorage:', this.settings);
            return true;
        } catch (e) {
            console.error('Failed to save settings to localStorage:', e);
            return false;
        }
    }

    async saveToBackend() {
        try {
            const response = await fetch((window.APP_BASE || '/scraper') + '/api/user/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.settings)
            });

            if (!response.ok) {
                throw new Error('Failed to save to backend');
            }

            const data = await response.json();
            console.log('Settings saved to backend:', data);
        } catch (error) {
            // Backend save is optional, don't show error to user
            console.log('Could not save to backend (user may not be logged in):', error);
        }
    }

    showNotification(message, type = 'info') {
        // Find or create notification container
        let container = document.getElementById('settings-notification');
        if (!container) {
            container = document.createElement('div');
            container.id = 'settings-notification';
            container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
            document.body.appendChild(container);
        }

        // Create notification
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        container.innerHTML = '';
        container.appendChild(notification);

        // Auto-hide after 3 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => container.innerHTML = '', 150);
        }, 3000);
    }

    getSetting(key) {
        return this.settings[key];
    }

    setSetting(key, value) {
        this.settings[key] = value;
        this.saveToLocalStorage();
    }
}

// Initialize settings manager when DOM is ready
let settingsManagerInitialized = false;
document.addEventListener('DOMContentLoaded', () => {
    if (settingsManagerInitialized) {
        console.log('Settings manager already initialized, skipping...');
        return;
    }

    window.settingsManager = new SettingsManager();
    settingsManagerInitialized = true;

    // Re-apply settings when navigation changes sections
    let applyTimeout = null;
    const observer = new MutationObserver((mutations) => {
        // Only process if a section became active (not inactive)
        const hasActiveChange = mutations.some(mutation => {
            const target = mutation.target;
            return target.classList.contains('active') && target.classList.contains('content-section');
        });

        if (hasActiveChange) {
            // Debounce: only apply once after all mutations settle
            clearTimeout(applyTimeout);
            applyTimeout = setTimeout(() => {
                if (window.settingsManager) {
                    window.settingsManager.applySettings();
                }
            }, 100);
        }
    });

    // Observe all content sections for changes
    document.querySelectorAll('.content-section').forEach(section => {
        observer.observe(section, {
            attributes: true,
            attributeFilter: ['class']
        });
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SettingsManager;
}
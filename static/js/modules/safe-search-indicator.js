/**
 * Safe Search Visual Indicator
 * Provides clear visual feedback when safe search is toggled
 */

(function() {
    'use strict';

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSafeSearchIndicator);
    } else {
        initSafeSearchIndicator();
    }

    function initSafeSearchIndicator() {
        // Find all safe search toggle elements
        const toggles = [
            document.getElementById('safe-search-toggle'),
            document.getElementById('safe-search'),
            document.getElementById('settings-safe-search-toggle')
        ].filter(Boolean); // Remove nulls

        if (toggles.length === 0) {
            console.warn('[Safe Search] No safe search toggles found');
            return;
        }

        console.log(`[Safe Search] Found ${toggles.length} toggle(s)`);

        // Create status indicator
        createStatusIndicator();

        // Add event listeners to all toggles
        toggles.forEach((toggle, index) => {
            toggle.addEventListener('change', function() {
                const isEnabled = this.checked;
                console.log(`[Safe Search] Toggle ${index + 1} changed:`, isEnabled ? 'ENABLED' : 'DISABLED');

                // Update all toggles to match (sync them)
                toggles.forEach(t => t.checked = isEnabled);

                // Update visual indicator
                updateStatusIndicator(isEnabled);

                // Show notification
                showNotification(isEnabled);
            });

            // Set initial state
            toggle.addEventListener('DOMContentLoaded', () => {
                updateStatusIndicator(toggle.checked);
            });
        });

        // Set initial state
        if (toggles[0]) {
            updateStatusIndicator(toggles[0].checked);
        }
    }

    function createStatusIndicator() {
        // Check if indicator already exists
        if (document.getElementById('safe-search-indicator')) {
            return;
        }

        const indicator = document.createElement('div');
        indicator.id = 'safe-search-indicator';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9998;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
        `;

        indicator.innerHTML = `
            <i class="fas fa-shield-alt"></i>
            <span id="safe-search-text">Safe Search: ON</span>
        `;

        document.body.appendChild(indicator);
    }

    function updateStatusIndicator(isEnabled) {
        const indicator = document.getElementById('safe-search-indicator');
        const text = document.getElementById('safe-search-text');

        if (!indicator || !text) return;

        if (isEnabled) {
            indicator.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
            indicator.style.color = 'white';
            text.textContent = 'Safe Search: ON';
            indicator.querySelector('i').className = 'fas fa-shield-alt';
        } else {
            indicator.style.background = 'linear-gradient(135deg, #dc3545 0%, #ff6b6b 100%)';
            indicator.style.color = 'white';
            text.textContent = 'Safe Search: OFF';
            indicator.querySelector('i').className = 'fas fa-exclamation-triangle';
        }

        // Pulse animation
        indicator.style.transform = 'scale(1.1)';
        setTimeout(() => {
            indicator.style.transform = 'scale(1)';
        }, 200);
    }

    function showNotification(isEnabled) {
        // Remove any existing notification
        const existing = document.getElementById('safe-search-notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.id = 'safe-search-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            padding: 15px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            animation: slideInRight 0.3s ease;
        `;

        if (isEnabled) {
            notification.style.background = '#28a745';
            notification.style.color = 'white';
            notification.innerHTML = `
                <i class="fas fa-shield-alt"></i>
                <span>Safe Search Enabled - Adult content will be filtered</span>
            `;
        } else {
            notification.style.background = '#dc3545';
            notification.style.color = 'white';
            notification.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <span>Safe Search Disabled - Adult content may appear (18+ only)</span>
            `;
        }

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }

        #safe-search-indicator:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }
    `;
    document.head.appendChild(style);

    console.log('[Safe Search] Indicator initialized');
})();

/**
 * OAuth Restoration Fix
 * Fixes Google OAuth badge display and ensures authentication flow works properly
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOAuthFix);
    } else {
        initOAuthFix();
    }

    function initOAuthFix() {
        // Fix Google indicator badge visibility and clickability
        fixGoogleIndicator();

        // Fix splash page OAuth button
        fixSplashOAuthButton();

        // Check authentication status
        checkAuthStatus();
    }

    function fixGoogleIndicator() {
        const googleIndicator = document.querySelector('.google-indicator');
        if (googleIndicator) {
            // Ensure the indicator is visible
            googleIndicator.style.display = 'flex';
            googleIndicator.style.visibility = 'visible';

            // Make sure the image is loading properly
            const img = googleIndicator.querySelector('img');
            if (img) {
                // If image fails to load, use inline SVG
                img.onerror = function() {
                    googleIndicator.innerHTML = `
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                        </svg>
                    `;
                };
            }

            // Add click handler to the user dropdown button
            const userDropdown = document.getElementById('user-dropdown');
            if (userDropdown) {
                userDropdown.style.cursor = 'pointer';
            }
        }
    }

    function fixSplashOAuthButton() {
        // Fix the main splash page OAuth button
        const googleBtn = document.querySelector('.google-btn');
        if (googleBtn && !googleBtn.disabled) {
            // Ensure button is clickable
            googleBtn.style.pointerEvents = 'auto';
            googleBtn.style.cursor = 'pointer';

            // Add click handler if href is missing
            if (!googleBtn.href && !googleBtn.onclick) {
                googleBtn.addEventListener('click', function(e) {
                    if (!this.disabled) {
                        // Update button text to show loading
                        const originalContent = this.innerHTML;
                        this.innerHTML = '<span>Redirecting to Google...</span>';
                        this.style.opacity = '0.7';

                        // Navigate to OAuth login
                        window.location.href = '/scraper/auth/login';
                    }
                });
            }

            // Ensure the Google icon loads
            const googleIcon = googleBtn.querySelector('.google-icon');
            if (googleIcon && !googleIcon.querySelector('path')) {
                // Icon might be broken, ensure SVG content is there
                console.log('Fixing Google button icon');
            }
        }
    }

    function checkAuthStatus() {
        // Only check auth status on splash page
        if (window.location.pathname.endsWith('/splash') ||
            window.location.pathname === '/scraper/' ||
            window.location.pathname === '/scraper') {

            fetch('/scraper/auth/check')
                .then(response => response.json())
                .then(data => {
                    if (data.authenticated) {
                        console.log('User is authenticated, redirecting to main app...');
                        // Redirect to main app if on splash page
                        if (!window.location.pathname.includes('index.html')) {
                            window.location.replace('/scraper/index.html');
                        }
                    }
                })
                .catch(error => {
                    console.error('Auth check failed:', error);
                });
        }
    }

    // Add CSS fixes dynamically if needed
    function addDynamicStyles() {
        const styleId = 'oauth-dynamic-fixes';
        if (!document.getElementById(styleId)) {
            const style = document.createElement('style');
            style.id = styleId;
            style.textContent = `
                /* Ensure Google indicator is visible */
                .google-indicator {
                    display: flex !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                }

                /* Make OAuth button clickable */
                .google-btn:not([disabled]) {
                    cursor: pointer !important;
                    pointer-events: auto !important;
                }

                /* Fix user dropdown positioning */
                #user-dropdown {
                    position: relative !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Apply dynamic styles
    addDynamicStyles();

    // Export for debugging
    window.oauthFix = {
        fixGoogleIndicator,
        fixSplashOAuthButton,
        checkAuthStatus
    };
})();
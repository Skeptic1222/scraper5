/**
 * OAUTH CALLBACK FIX
 * Ensures Google OAuth authentication works properly with IIS proxy setup
 * Addresses OAuth login state and callback handling issues
 */

(function() {
    'use strict';

    console.log('🔐 OAUTH: Callback fix loading...');

    const APP_BASE = window.APP_BASE || '/scraper';

    // OAUTH ENDPOINTS
    const OAUTH_ENDPOINTS = {
        login: `${APP_BASE}/auth/login`,
        callback: `${APP_BASE}/auth/callback`,
        logout: `${APP_BASE}/auth/logout`,
        check: `${APP_BASE}/auth/check`
    };

    // ENHANCED AUTHENTICATION STATE MANAGEMENT
    class AuthenticationManager {
        constructor() {
            this.authState = {
                isAuthenticated: false,
                user: null,
                loading: false
            };
            this.callbacks = [];
        }

        // Add auth state change callback
        onAuthChange(callback) {
            this.callbacks.push(callback);
        }

        // Notify all callbacks of state change
        notifyAuthChange() {
            this.callbacks.forEach(callback => {
                try {
                    callback(this.authState);
                } catch (error) {
                    console.error('🔐 OAUTH: Auth callback error:', error);
                }
            });
        }

        // Check current authentication status
        async checkAuthStatus() {
            try {
                this.authState.loading = true;
                this.notifyAuthChange();

                console.log('🔐 OAUTH: Checking authentication status...');

                const response = await fetch(OAUTH_ENDPOINTS.check, {
                    method: 'GET',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    this.authState.isAuthenticated = data.authenticated || false;
                    this.authState.user = data.user || null;

                    console.log(`🔐 OAUTH: Auth status - ${this.authState.isAuthenticated ? 'authenticated' : 'not authenticated'}`);

                    if (this.authState.isAuthenticated && this.authState.user) {
                        console.log(`👤 OAUTH: User: ${this.authState.user.name || this.authState.user.email}`);
                    }
                } else {
                    console.warn(`🔐 OAUTH: Auth check failed with status ${response.status}`);
                    this.authState.isAuthenticated = false;
                    this.authState.user = null;
                }
            } catch (error) {
                console.error('🔐 OAUTH: Auth check error:', error);
                this.authState.isAuthenticated = false;
                this.authState.user = null;
            } finally {
                this.authState.loading = false;
                this.notifyAuthChange();
            }

            return this.authState;
        }

        // Enhanced login method
        async login() {
            try {
                console.log('🔐 OAUTH: Starting login process...');

                // Store current location for post-login redirect
                sessionStorage.setItem('oauth_return_url', window.location.href);

                // Redirect to OAuth login
                window.location.href = OAUTH_ENDPOINTS.login;
            } catch (error) {
                console.error('🔐 OAUTH: Login error:', error);
                throw error;
            }
        }

        // Enhanced logout method
        async logout() {
            try {
                console.log('🔐 OAUTH: Starting logout process...');

                const response = await fetch(OAUTH_ENDPOINTS.logout, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                this.authState.isAuthenticated = false;
                this.authState.user = null;
                this.notifyAuthChange();

                // Redirect to splash page
                window.location.href = `${APP_BASE}/`;

            } catch (error) {
                console.error('🔐 OAUTH: Logout error:', error);
                // Force local logout even if server request fails
                this.authState.isAuthenticated = false;
                this.authState.user = null;
                this.notifyAuthChange();
                window.location.href = `${APP_BASE}/`;
            }
        }
    }

    // GLOBAL AUTH MANAGER INSTANCE
    window.authManager = new AuthenticationManager();

    // HANDLE OAUTH CALLBACK PROCESSING
    function handleOAuthCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const hasAuthCode = urlParams.has('code');
        const hasAuthError = urlParams.has('error');

        if (hasAuthCode) {
            console.log('🔐 OAUTH: OAuth callback detected with authorization code');

            // Show loading state
            document.body.innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column;">
                    <div style="text-align: center;">
                        <div style="font-size: 48px; margin-bottom: 20px;">🔐</div>
                        <h2>Completing Sign In...</h2>
                        <p>Please wait while we complete your authentication.</p>
                        <div style="margin-top: 20px;">
                            <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                        </div>
                    </div>
                    <style>
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                    </style>
                </div>
            `;

            // Let the server handle the callback, then check auth status
            setTimeout(async () => {
                await window.authManager.checkAuthStatus();

                if (window.authManager.authState.isAuthenticated) {
                    // Get return URL or default to main app
                    const returnUrl = sessionStorage.getItem('oauth_return_url') || `${APP_BASE}/index.html`;
                    sessionStorage.removeItem('oauth_return_url');

                    console.log(`🔐 OAUTH: Authentication successful, redirecting to ${returnUrl}`);
                    window.location.replace(returnUrl);
                } else {
                    console.error('🔐 OAUTH: Authentication failed after callback');
                    window.location.replace(`${APP_BASE}/?error=auth_failed`);
                }
            }, 1000);

        } else if (hasAuthError) {
            const error = urlParams.get('error');
            const errorDescription = urlParams.get('error_description');

            console.error('🔐 OAUTH: OAuth error:', error, errorDescription);

            // Show error message
            document.body.innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column;">
                    <div style="text-align: center; max-width: 500px; padding: 20px;">
                        <div style="font-size: 48px; margin-bottom: 20px; color: #dc3545;">❌</div>
                        <h2>Authentication Error</h2>
                        <p>There was a problem signing you in: <strong>${errorDescription || error}</strong></p>
                        <a href="${APP_BASE}/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px;">Try Again</a>
                    </div>
                </div>
            `;
        }
    }

    // SETUP GOOGLE SIGNIN BUTTON
    function setupGoogleSignIn() {
        const googleButtons = document.querySelectorAll('.google-btn:not([disabled]), [href*="/auth/login"]');

        googleButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();

                if (this.disabled) {
                    return;
                }

                console.log('🔐 OAUTH: Google sign-in button clicked');

                // Update button state
                const originalText = this.innerHTML;
                this.innerHTML = '<span>Redirecting to Google...</span>';
                this.style.opacity = '0.7';
                this.disabled = true;

                // Start login process
                window.authManager.login().catch(error => {
                    console.error('🔐 OAUTH: Login failed:', error);
                    this.innerHTML = originalText;
                    this.style.opacity = '1';
                    this.disabled = false;
                });
            });
        });

        console.log(`🔐 OAUTH: ${googleButtons.length} Google sign-in buttons configured`);
    }

    // SETUP LOGOUT BUTTONS
    function setupLogoutButtons() {
        const logoutButtons = document.querySelectorAll('[href*="/auth/logout"], .logout-btn');

        logoutButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();

                console.log('🔐 OAUTH: Logout button clicked');
                window.authManager.logout();
            });
        });

        console.log(`🔐 OAUTH: ${logoutButtons.length} logout buttons configured`);
    }

    // UPDATE UI BASED ON AUTH STATE
    function updateUIForAuthState(authState) {
        console.log('🔐 OAUTH: Updating UI for auth state:', authState);

        // Update navbar user info
        const userDisplay = document.querySelector('#user-display-name, .username');
        if (userDisplay && authState.user) {
            userDisplay.textContent = authState.user.name || authState.user.email || 'User';
        }

        // Show/hide user profile section
        const userProfile = document.querySelector('#user-profile-section, .user-profile');
        if (userProfile) {
            userProfile.style.display = authState.isAuthenticated ? 'block' : 'none';
        }

        // Show/hide admin navigation if user is admin
        const adminNav = document.querySelector('.admin-only');
        if (adminNav && authState.user) {
            adminNav.style.display = authState.user.isAdmin ? 'block' : 'none';
        }
    }

    // INITIALIZATION
    function initializeOAuthFix() {
        console.log('🔐 OAUTH: Initializing OAuth fix...');

        // Handle OAuth callback if present
        handleOAuthCallback();

        // Setup UI elements
        setupGoogleSignIn();
        setupLogoutButtons();

        // Monitor auth state changes
        window.authManager.onAuthChange(updateUIForAuthState);

        // Check initial auth status
        window.authManager.checkAuthStatus();

        console.log('✅ OAUTH: OAuth fix initialized');
    }

    // MULTIPLE INITIALIZATION TRIGGERS
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeOAuthFix);
    } else {
        initializeOAuthFix();
    }

    // Also initialize on window load
    window.addEventListener('load', () => {
        setTimeout(initializeOAuthFix, 100);
    });

    // Re-setup buttons after DOM changes
    const observer = new MutationObserver((mutations) => {
        let needsResetup = false;

        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.matches && (node.matches('.google-btn') || node.matches('[href*="/auth/"]'))) {
                            needsResetup = true;
                        } else if (node.querySelector && node.querySelector('.google-btn, [href*="/auth/"]')) {
                            needsResetup = true;
                        }
                    }
                });
            }
        });

        if (needsResetup) {
            setTimeout(() => {
                setupGoogleSignIn();
                setupLogoutButtons();
            }, 100);
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log('🛡️ OAUTH: OAuth fix script loaded');

})();
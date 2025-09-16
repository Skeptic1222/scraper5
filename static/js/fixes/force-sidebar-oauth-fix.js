/**
 * Force Sidebar and OAuth Fix
 * Ensures sidebar is visible and OAuth login works properly
 */

(function() {
    'use strict';

    console.log('🔧 Force Sidebar & OAuth Fix initializing...');

    // Force sidebar visibility
    function forceSidebarVisible() {
        const sidebar = document.querySelector('.sidebar, #sidebar, aside.sidebar, [class*="sidebar"]');

        if (sidebar) {
            // Remove any hiding classes
            sidebar.classList.remove('d-none', 'hidden', 'collapsed', 'hide');

            // Force visibility with inline styles (highest priority)
            sidebar.style.display = 'flex';
            sidebar.style.visibility = 'visible';
            sidebar.style.opacity = '1';
            sidebar.style.position = 'fixed';
            sidebar.style.left = '0';
            sidebar.style.top = '0';
            sidebar.style.height = '100vh';
            sidebar.style.width = '250px';
            sidebar.style.zIndex = '1000';
            sidebar.style.background = 'var(--sidebar-bg, #1a1a2e)';
            sidebar.style.transform = 'translateX(0)';

            console.log('✅ Sidebar forced visible');

            // Ensure navigation items are clickable
            const navItems = sidebar.querySelectorAll('.nav-item, [data-section]');
            navItems.forEach(item => {
                item.style.pointerEvents = 'auto';
                item.style.cursor = 'pointer';

                // Add click handler if missing
                if (!item.hasAttribute('data-listener-attached')) {
                    item.setAttribute('data-listener-attached', 'true');
                    item.addEventListener('click', function(e) {
                        e.preventDefault();
                        const section = this.getAttribute('data-section');
                        console.log(`📍 Navigation clicked: ${section}`);

                        // Handle navigation
                        handleNavigation(section);
                    });
                }
            });

            // Adjust main content margin
            const mainContent = document.querySelector('.main-content, main, .content-wrapper, [class*="main"]');
            if (mainContent) {
                mainContent.style.marginLeft = '250px';
                mainContent.style.transition = 'margin-left 0.3s ease';
            }

            return true;
        }

        return false;
    }

    // Handle navigation between sections
    function handleNavigation(section) {
        console.log(`🔄 Navigating to: ${section}`);

        // Hide all sections
        const sections = document.querySelectorAll('.content-section, [data-content], .section');
        sections.forEach(s => {
            s.style.display = 'none';
            s.classList.remove('active');
        });

        // Show target section
        const targetSection = document.querySelector(`#${section}, [data-content="${section}"], .${section}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
            targetSection.classList.add('active');
            console.log(`✅ Section shown: ${section}`);
        }

        // Update active nav item
        const navItems = document.querySelectorAll('.nav-item, [data-section]');
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-section') === section) {
                item.classList.add('active');
            }
        });
    }

    // Fix OAuth login
    function fixOAuthLogin() {
        // Find Google sign-in button
        const signInButtons = document.querySelectorAll(
            '.google-signin-btn, ' +
            '#google-signin-btn, ' +
            '[onclick*="google"], ' +
            '[href*="/auth/google"], ' +
            '.btn-google, ' +
            '[class*="google"][class*="sign"], ' +
            'button:has(.fa-google), ' +
            'a:has(.fa-google)'
        );

        signInButtons.forEach(btn => {
            // Ensure button is visible
            btn.style.display = 'inline-flex';
            btn.style.visibility = 'visible';
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';

            console.log('✅ Google sign-in button made visible');

            // Add click handler for OAuth
            if (!btn.hasAttribute('data-oauth-fixed')) {
                btn.setAttribute('data-oauth-fixed', 'true');

                btn.addEventListener('click', function(e) {
                    console.log('🔐 Google OAuth initiated');

                    // If it's a link with href, let it proceed
                    if (this.href && this.href.includes('/auth/')) {
                        console.log('📍 Redirecting to:', this.href);
                        return true;
                    }

                    // Otherwise handle programmatically
                    e.preventDefault();
                    const authUrl = '/scraper/auth/login';
                    console.log('📍 Redirecting to OAuth:', authUrl);
                    window.location.href = authUrl;
                });
            }
        });

        // Check authentication status
        checkAuthStatus();
    }

    // Check authentication status
    function checkAuthStatus() {
        const authCheckUrl = '/scraper/auth/check';

        fetch(authCheckUrl)
            .then(response => response.json())
            .then(data => {
                console.log('🔐 Auth status:', data);

                if (data.authenticated) {
                    console.log('✅ User authenticated:', data.user?.email);
                    updateUIForAuthenticatedUser(data.user);
                } else {
                    console.log('❌ User not authenticated');
                    showLoginPrompt();
                }
            })
            .catch(error => {
                console.error('❌ Auth check failed:', error);
            });
    }

    // Update UI for authenticated user
    function updateUIForAuthenticatedUser(user) {
        // Update user avatar
        const avatarElements = document.querySelectorAll('.user-avatar, #user-avatar, [class*="avatar"]');
        avatarElements.forEach(avatar => {
            if (user.picture) {
                avatar.src = user.picture;
                avatar.style.display = 'block';
            }
        });

        // Update user name
        const nameElements = document.querySelectorAll('.user-name, #user-name, [class*="username"]');
        nameElements.forEach(nameEl => {
            nameEl.textContent = user.name || user.email;
        });

        // Hide login buttons
        const loginButtons = document.querySelectorAll('.google-signin-btn, [class*="signin"], [class*="login"]');
        loginButtons.forEach(btn => {
            if (btn.textContent.toLowerCase().includes('sign in') ||
                btn.textContent.toLowerCase().includes('login')) {
                btn.style.display = 'none';
            }
        });

        // Show logout button
        const logoutButtons = document.querySelectorAll('.logout-btn, [href*="logout"], [class*="logout"]');
        logoutButtons.forEach(btn => {
            btn.style.display = 'inline-flex';
        });
    }

    // Show login prompt
    function showLoginPrompt() {
        const loginPrompt = document.querySelector('.login-prompt, .auth-prompt');
        if (loginPrompt) {
            loginPrompt.style.display = 'block';
        }

        // Ensure sign-in buttons are visible
        const signInButtons = document.querySelectorAll('.google-signin-btn, [class*="signin"]');
        signInButtons.forEach(btn => {
            btn.style.display = 'inline-flex';
        });
    }

    // Monitor for dynamic changes
    function startMonitoring() {
        // Monitor for sidebar being hidden
        const sidebarObserver = new MutationObserver(() => {
            const sidebar = document.querySelector('.sidebar, #sidebar');
            if (sidebar && (
                sidebar.style.display === 'none' ||
                sidebar.classList.contains('d-none') ||
                sidebar.classList.contains('collapsed')
            )) {
                console.log('⚠️ Sidebar was hidden, forcing visible...');
                forceSidebarVisible();
            }
        });

        // Start observing
        const sidebar = document.querySelector('.sidebar, #sidebar');
        if (sidebar) {
            sidebarObserver.observe(sidebar, {
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        }

        // Also observe body for new elements
        sidebarObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Initialize on DOM ready
    function initialize() {
        console.log('🚀 Initializing Force Sidebar & OAuth Fix...');

        // Force sidebar visible
        if (forceSidebarVisible()) {
            console.log('✅ Sidebar successfully forced visible');
        } else {
            console.log('⚠️ Sidebar not found, will retry...');
        }

        // Fix OAuth
        fixOAuthLogin();

        // Start monitoring
        startMonitoring();

        // Set default section
        const defaultSection = 'dashboard';
        handleNavigation(defaultSection);

        console.log('✅ Force Sidebar & OAuth Fix ready');
    }

    // Multiple initialization strategies
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }

    // Also try after a delay
    setTimeout(initialize, 100);
    setTimeout(initialize, 500);
    setTimeout(initialize, 1000);

    // Re-check periodically
    setInterval(() => {
        const sidebar = document.querySelector('.sidebar, #sidebar');
        if (!sidebar || sidebar.style.display === 'none') {
            console.log('🔄 Re-checking sidebar visibility...');
            forceSidebarVisible();
        }
    }, 2000);

})();
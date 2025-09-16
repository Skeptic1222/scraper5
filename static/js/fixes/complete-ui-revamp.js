/**
 * Complete UI Revamp - Fix Google Badge and Rebuild Sidebar Navigation
 * This completely replaces the broken sidebar with a new working implementation
 */

(function() {
    'use strict';

    console.log('🔧 Complete UI Revamp initializing...');

    // Store authenticated user data
    let currentUser = null;

    // Create new sidebar HTML structure
    function createNewSidebar() {
        // Remove any existing broken sidebar
        const oldSidebars = document.querySelectorAll('.sidebar, #sidebar, aside.sidebar, [class*="sidebar"]');
        oldSidebars.forEach(sidebar => sidebar.remove());

        // Create new sidebar container
        const sidebar = document.createElement('aside');
        sidebar.id = 'new-sidebar';
        sidebar.className = 'revamped-sidebar';
        sidebar.innerHTML = `
            <div class="sidebar-header">
                <div class="app-logo">
                    <i class="fas fa-download"></i>
                    <span>Media Scraper</span>
                </div>
            </div>

            <nav class="sidebar-nav">
                <div class="nav-item active" data-page="dashboard">
                    <i class="fas fa-tachometer-alt"></i>
                    <span>Dashboard</span>
                </div>
                <div class="nav-item" data-page="search">
                    <i class="fas fa-search"></i>
                    <span>Search</span>
                </div>
                <div class="nav-item" data-page="assets">
                    <i class="fas fa-folder"></i>
                    <span>Asset Library</span>
                </div>
                <div class="nav-item" data-page="sources">
                    <i class="fas fa-globe"></i>
                    <span>Sources</span>
                </div>
                <div class="nav-item" data-page="ai-assistant">
                    <i class="fas fa-robot"></i>
                    <span>AI Assistant</span>
                </div>
                <div class="nav-item" data-page="settings">
                    <i class="fas fa-cog"></i>
                    <span>Settings</span>
                </div>
            </nav>

            <div class="sidebar-footer">
                <div class="user-section" id="sidebar-user-section">
                    <!-- User info will be inserted here -->
                </div>
            </div>
        `;

        // Add CSS for the new sidebar
        const style = document.createElement('style');
        style.textContent = `
            /* Complete Sidebar Revamp Styles */
            .revamped-sidebar {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 250px !important;
                height: 100vh !important;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                display: flex !important;
                flex-direction: column !important;
                z-index: 10000 !important;
                box-shadow: 2px 0 10px rgba(0,0,0,0.1) !important;
                visibility: visible !important;
                opacity: 1 !important;
                transform: translateX(0) !important;
            }

            .sidebar-header {
                padding: 20px !important;
                border-bottom: 1px solid rgba(255,255,255,0.1) !important;
            }

            .app-logo {
                display: flex !important;
                align-items: center !important;
                color: white !important;
                font-size: 1.2rem !important;
                font-weight: bold !important;
            }

            .app-logo i {
                margin-right: 10px !important;
                font-size: 1.5rem !important;
            }

            .sidebar-nav {
                flex: 1 !important;
                padding: 20px 0 !important;
                overflow-y: auto !important;
            }

            .nav-item {
                display: flex !important;
                align-items: center !important;
                padding: 12px 20px !important;
                color: rgba(255,255,255,0.8) !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                margin: 2px 10px !important;
                border-radius: 8px !important;
            }

            .nav-item:hover {
                background: rgba(255,255,255,0.1) !important;
                color: white !important;
            }

            .nav-item.active {
                background: rgba(255,255,255,0.2) !important;
                color: white !important;
                font-weight: 500 !important;
            }

            .nav-item i {
                margin-right: 12px !important;
                width: 20px !important;
                text-align: center !important;
            }

            .sidebar-footer {
                padding: 20px !important;
                border-top: 1px solid rgba(255,255,255,0.1) !important;
            }

            .user-section {
                display: flex !important;
                align-items: center !important;
                color: white !important;
            }

            .user-avatar {
                width: 35px !important;
                height: 35px !important;
                border-radius: 50% !important;
                margin-right: 10px !important;
                border: 2px solid white !important;
            }

            .user-info {
                flex: 1 !important;
            }

            .user-name {
                font-weight: 500 !important;
                font-size: 0.9rem !important;
            }

            .user-email {
                font-size: 0.75rem !important;
                opacity: 0.8 !important;
            }

            /* Adjust main content for sidebar */
            body {
                padding-left: 250px !important;
            }

            .main-content,
            main,
            .content-wrapper,
            [class*="main"] {
                margin-left: 250px !important;
            }

            /* Fix navbar to account for sidebar */
            .navbar {
                left: 250px !important;
                width: calc(100% - 250px) !important;
            }
        `;
        document.head.appendChild(style);

        // Insert sidebar at the beginning of body
        document.body.insertBefore(sidebar, document.body.firstChild);

        // Attach event listeners
        attachSidebarListeners();

        return sidebar;
    }

    // Attach event listeners to sidebar navigation
    function attachSidebarListeners() {
        const navItems = document.querySelectorAll('.nav-item[data-page]');

        navItems.forEach(item => {
            item.addEventListener('click', function() {
                const page = this.getAttribute('data-page');

                // Remove active class from all items
                navItems.forEach(nav => nav.classList.remove('active'));

                // Add active class to clicked item
                this.classList.add('active');

                // Handle navigation
                navigateToPage(page);
            });
        });
    }

    // Navigate to different pages/sections
    function navigateToPage(page) {
        console.log(`📍 Navigating to: ${page}`);

        // Hide all sections
        const sections = document.querySelectorAll('.content-section, [data-content], .section, .page-content');
        sections.forEach(section => {
            section.style.display = 'none';
            section.classList.remove('active');
        });

        // Show the target section
        const targetSelectors = [
            `#${page}`,
            `#${page}-section`,
            `[data-content="${page}"]`,
            `.${page}-content`,
            `.${page}-section`
        ];

        let found = false;
        for (const selector of targetSelectors) {
            const target = document.querySelector(selector);
            if (target) {
                target.style.display = 'block';
                target.classList.add('active');
                found = true;
                console.log(`✅ Showing section: ${selector}`);
                break;
            }
        }

        if (!found) {
            console.log(`⚠️ Section not found for: ${page}`);
            // Show dashboard as fallback
            const dashboard = document.querySelector('#dashboard, .dashboard-content');
            if (dashboard) {
                dashboard.style.display = 'block';
                dashboard.classList.add('active');
            }
        }
    }

    // Fix Google Badge and Authentication Display
    function fixGoogleBadge() {
        console.log('🔐 Fixing Google authentication display...');

        // Check authentication status
        fetch('/scraper/auth/check')
            .then(response => response.json())
            .then(data => {
                if (data.authenticated && data.user) {
                    currentUser = data.user;
                    console.log('✅ User authenticated:', currentUser.email);
                    updateAuthenticatedUI();
                } else {
                    console.log('❌ User not authenticated');
                    updateUnauthenticatedUI();
                }
            })
            .catch(error => {
                console.error('❌ Auth check failed:', error);
                updateUnauthenticatedUI();
            });
    }

    // Update UI for authenticated user
    function updateAuthenticatedUI() {
        // Update sidebar user section
        const userSection = document.getElementById('sidebar-user-section');
        if (userSection && currentUser) {
            userSection.innerHTML = `
                <img src="${currentUser.picture || '/static/img/default-avatar.png'}"
                     alt="User Avatar"
                     class="user-avatar"
                     onerror="this.src='/static/img/default-avatar.png'">
                <div class="user-info">
                    <div class="user-name">${currentUser.name || 'User'}</div>
                    <div class="user-email">${currentUser.email || ''}</div>
                </div>
            `;
        }

        // Fix navbar Google badge
        fixNavbarGoogleBadge();

        // Hide sign-in buttons
        const signInButtons = document.querySelectorAll('.google-signin-btn, .signin-btn, [class*="sign-in"]');
        signInButtons.forEach(btn => {
            if (btn.textContent.toLowerCase().includes('sign') ||
                btn.textContent.toLowerCase().includes('login')) {
                btn.style.display = 'none';
            }
        });

        // Show logout button
        showLogoutButton();
    }

    // Update UI for unauthenticated user
    function updateUnauthenticatedUI() {
        // Update sidebar user section
        const userSection = document.getElementById('sidebar-user-section');
        if (userSection) {
            userSection.innerHTML = `
                <button class="sidebar-signin-btn" onclick="window.location.href='/scraper/auth/login'">
                    <i class="fab fa-google"></i>
                    Sign in with Google
                </button>
            `;
        }

        // Add styles for sign-in button
        if (!document.getElementById('signin-btn-styles')) {
            const style = document.createElement('style');
            style.id = 'signin-btn-styles';
            style.textContent = `
                .sidebar-signin-btn {
                    width: 100%;
                    padding: 10px;
                    background: white;
                    color: #667eea;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s ease;
                }

                .sidebar-signin-btn:hover {
                    background: rgba(255,255,255,0.9);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }

                .sidebar-signin-btn i {
                    margin-right: 8px;
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Fix navbar Google badge display
    function fixNavbarGoogleBadge() {
        if (!currentUser) return;

        // Find navbar user section
        const navbarUserSections = document.querySelectorAll('.navbar-nav, .user-menu, .navbar-right, .ms-auto');

        navbarUserSections.forEach(section => {
            // Look for existing user display
            const existingUser = section.querySelector('.user-avatar, .user-badge, [class*="user"]');

            if (!existingUser) {
                // Create Google badge
                const googleBadge = document.createElement('div');
                googleBadge.className = 'google-user-badge';
                googleBadge.innerHTML = `
                    <div class="dropdown">
                        <button class="btn btn-link dropdown-toggle" data-bs-toggle="dropdown">
                            <img src="${currentUser.picture}"
                                 alt="${currentUser.name}"
                                 class="google-avatar"
                                 onerror="this.src='/static/img/default-avatar.png'">
                            <span class="user-name-badge">${currentUser.name}</span>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li class="dropdown-header">${currentUser.email}</li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/scraper/profile">Profile</a></li>
                            <li><a class="dropdown-item" href="/scraper/settings">Settings</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="/scraper/auth/logout">Logout</a></li>
                        </ul>
                    </div>
                `;

                // Add styles for Google badge
                if (!document.getElementById('google-badge-styles')) {
                    const style = document.createElement('style');
                    style.id = 'google-badge-styles';
                    style.textContent = `
                        .google-user-badge {
                            display: flex;
                            align-items: center;
                        }

                        .google-avatar {
                            width: 32px;
                            height: 32px;
                            border-radius: 50%;
                            margin-right: 8px;
                            border: 2px solid white;
                        }

                        .user-name-badge {
                            color: white;
                            margin-right: 5px;
                        }

                        .google-user-badge .dropdown-toggle {
                            display: flex;
                            align-items: center;
                            text-decoration: none;
                            color: white;
                        }

                        .google-user-badge .dropdown-toggle::after {
                            margin-left: 5px;
                        }
                    `;
                    document.head.appendChild(style);
                }

                section.appendChild(googleBadge);
                console.log('✅ Google badge added to navbar');
            }
        });
    }

    // Show logout button
    function showLogoutButton() {
        const logoutBtns = document.querySelectorAll('.logout-btn, [href*="logout"]');
        logoutBtns.forEach(btn => {
            btn.style.display = 'inline-flex';
            btn.style.visibility = 'visible';
        });
    }

    // Initialize the complete revamp
    function initialize() {
        console.log('🚀 Starting Complete UI Revamp...');

        // Create new sidebar
        const sidebar = createNewSidebar();
        console.log('✅ New sidebar created');

        // Fix Google authentication display
        fixGoogleBadge();

        // Set default page
        navigateToPage('dashboard');

        // Monitor for changes
        startMonitoring();

        console.log('✅ Complete UI Revamp initialized');
    }

    // Monitor for dynamic changes
    function startMonitoring() {
        // Re-check auth status periodically
        setInterval(() => {
            fixGoogleBadge();
        }, 5000);

        // Monitor for sidebar being removed
        const observer = new MutationObserver(() => {
            if (!document.getElementById('new-sidebar')) {
                console.log('⚠️ Sidebar was removed, recreating...');
                createNewSidebar();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: false
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }

    // Also initialize after a short delay to ensure everything is loaded
    setTimeout(initialize, 500);

})();
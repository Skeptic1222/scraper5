// Final UI Fix - Complete sidebar and OAuth badge solution
// This file combines all fixes into one working solution

window.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Final UI Fix starting...');

    // Force remove old broken sidebars
    document.querySelectorAll('.sidebar, #sidebar, aside.sidebar').forEach(el => el.remove());

    // Create brand new working sidebar
    const newSidebar = document.createElement('div');
    newSidebar.id = 'working-sidebar';
    newSidebar.innerHTML = `
        <style>
            #working-sidebar {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 250px !important;
                height: 100vh !important;
                background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%) !important;
                z-index: 9999 !important;
                display: flex !important;
                flex-direction: column !important;
                box-shadow: 2px 0 10px rgba(0,0,0,0.2) !important;
            }

            #working-sidebar .sidebar-logo {
                padding: 20px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                color: white;
                font-size: 1.3rem;
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            #working-sidebar .nav-menu {
                flex: 1;
                padding: 20px 0;
            }

            #working-sidebar .nav-link {
                display: flex;
                align-items: center;
                padding: 12px 20px;
                color: rgba(255,255,255,0.9);
                text-decoration: none;
                transition: all 0.3s;
                cursor: pointer;
                gap: 12px;
            }

            #working-sidebar .nav-link:hover {
                background: rgba(255,255,255,0.1);
                padding-left: 25px;
            }

            #working-sidebar .nav-link.active {
                background: rgba(255,255,255,0.2);
                border-left: 3px solid white;
            }

            #working-sidebar .user-area {
                padding: 20px;
                border-top: 1px solid rgba(255,255,255,0.1);
                color: white;
            }

            body.has-working-sidebar {
                margin-left: 250px !important;
            }

            .main-content {
                margin-left: 250px !important;
            }

            .navbar {
                left: 250px !important;
                width: calc(100% - 250px) !important;
            }

            .google-auth-badge {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 5px 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                color: white;
            }

            .google-auth-badge img {
                width: 30px;
                height: 30px;
                border-radius: 50%;
                border: 2px solid white;
            }
        </style>

        <div class="sidebar-logo">
            <i class="fas fa-download"></i>
            Media Scraper
        </div>

        <div class="nav-menu">
            <a class="nav-link active" data-navigate="dashboard">
                <i class="fas fa-home"></i>
                Dashboard
            </a>
            <a class="nav-link" data-navigate="search">
                <i class="fas fa-search"></i>
                Search Media
            </a>
            <a class="nav-link" data-navigate="library">
                <i class="fas fa-images"></i>
                Asset Library
            </a>
            <a class="nav-link" data-navigate="sources">
                <i class="fas fa-database"></i>
                Sources
            </a>
            <a class="nav-link" data-navigate="ai">
                <i class="fas fa-robot"></i>
                AI Assistant
            </a>
            <a class="nav-link" data-navigate="settings">
                <i class="fas fa-cog"></i>
                Settings
            </a>
        </div>

        <div class="user-area" id="user-area">
            <!-- User info will go here -->
        </div>
    `;

    document.body.insertBefore(newSidebar, document.body.firstChild);
    document.body.classList.add('has-working-sidebar');

    // Handle navigation
    document.querySelectorAll('[data-navigate]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.dataset.navigate;

            // Update active state
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            // Hide all sections
            document.querySelectorAll('.content-section, [data-content], .section').forEach(s => {
                s.style.display = 'none';
            });

            // Show target section
            const section = document.querySelector(`#${target}, [data-content="${target}"], .${target}-section`);
            if (section) {
                section.style.display = 'block';
                console.log('✅ Navigated to:', target);
            }
        });
    });

    // Fix Google authentication display
    fetch('/scraper/auth/check')
        .then(r => r.json())
        .then(data => {
            const userArea = document.getElementById('user-area');

            if (data.authenticated && data.user) {
                // User is logged in - show their info
                userArea.innerHTML = `
                    <div class="google-auth-badge">
                        <img src="${data.user.picture || '/static/img/avatar.png'}"
                             onerror="this.src='/static/img/avatar.png'">
                        <div>
                            <div style="font-weight: 500">${data.user.name || 'User'}</div>
                            <div style="font-size: 0.8rem; opacity: 0.8">${data.user.email || ''}</div>
                        </div>
                    </div>
                `;

                // Hide any login buttons
                document.querySelectorAll('.google-signin-btn, [class*="sign-in"], [class*="login"]').forEach(btn => {
                    if (btn.textContent.toLowerCase().includes('sign') ||
                        btn.textContent.toLowerCase().includes('login')) {
                        btn.style.display = 'none';
                    }
                });

                // Update navbar if exists
                const navbar = document.querySelector('.navbar-nav.ms-auto, .navbar-nav.ml-auto');
                if (navbar && !navbar.querySelector('.google-auth-badge')) {
                    const badge = document.createElement('div');
                    badge.className = 'google-auth-badge';
                    badge.style.marginLeft = 'auto';
                    badge.innerHTML = `
                        <img src="${data.user.picture || '/static/img/avatar.png'}" style="width: 30px; height: 30px; border-radius: 50%;">
                        <span>${data.user.name}</span>
                    `;
                    navbar.appendChild(badge);
                }

                console.log('✅ User authenticated:', data.user.email);
            } else {
                // User not logged in - show login button
                userArea.innerHTML = `
                    <button onclick="location.href='/scraper/auth/login'"
                            style="width: 100%; padding: 10px; background: white; color: #2a5298; border: none; border-radius: 5px; cursor: pointer; font-weight: 500;">
                        <i class="fab fa-google" style="margin-right: 8px;"></i>
                        Sign in with Google
                    </button>
                `;
                console.log('❌ User not authenticated');
            }
        })
        .catch(err => {
            console.error('Auth check failed:', err);
        });

    console.log('✅ Final UI Fix complete!');
});
/**
 * Sidebar Navigation Fix
 * Ensures sidebar navigation properly switches between sections
 */

(function() {
    'use strict';
    
    console.log('📍 Sidebar Navigation Fix initializing...');
    
    // Define the showSection function
    function showSection(sectionName) {
        console.log(`🔄 Switching to section: ${sectionName}`);
        
        // Define all possible sections
        const sections = [
            'dashboard-section',
            'search-section',
            'assets-section',
            'admin-section',
            'settings-section',
            'subscription-section'
        ];
        
        // Hide all sections
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.style.display = 'none';
                section.classList.remove('active');
            }
        });
        
        // Show the requested section
        let targetSection = document.getElementById(`${sectionName}-section`);
        
        // If not found, try without -section suffix
        if (!targetSection) {
            targetSection = document.getElementById(sectionName);
        }
        
        // If still not found, try common variations
        if (!targetSection) {
            const variations = [
                sectionName,
                `${sectionName}-container`,
                `${sectionName}-content`,
                `${sectionName}-view`,
                `${sectionName}-panel`
            ];
            
            for (const variant of variations) {
                targetSection = document.getElementById(variant);
                if (targetSection) break;
            }
        }
        
        if (targetSection) {
            targetSection.style.display = 'block';
            targetSection.classList.add('active');
            console.log(`✅ Section ${sectionName} displayed`);
            
            // Trigger section-specific initialization
            initializeSectionContent(sectionName);
            
            // Update URL hash
            window.location.hash = sectionName;
            
            // Update document title
            const titles = {
                'dashboard': 'Dashboard',
                'search': 'Search & Download',
                'assets': 'Asset Library',
                'admin': 'Admin Panel',
                'settings': 'Settings',
                'subscription': 'Subscription'
            };
            
            if (titles[sectionName]) {
                document.title = `${titles[sectionName]} - Media Scraper`;
            }
            
            // Update sidebar active state
            updateSidebarActiveState(sectionName);
            
        } else {
            console.warn(`⚠️ Section not found: ${sectionName}`);
            
            // Try to create a placeholder section if it doesn't exist
            createPlaceholderSection(sectionName);
        }
    }
    
    // Initialize section content
    function initializeSectionContent(sectionName) {
        switch(sectionName) {
            case 'dashboard':
                // Load dashboard stats
                if (typeof updateDashboardStats === 'function') {
                    updateDashboardStats();
                }
                break;
                
            case 'search':
                // Initialize search interface
                if (window.app && window.app.modules && window.app.modules.searchManager) {
                    window.app.modules.searchManager.loadSources();
                }
                break;
                
            case 'assets':
                // Load asset library
                if (typeof loadGallery === 'function') {
                    loadGallery();
                } else if (typeof fixAssetLibrary === 'function') {
                    fixAssetLibrary();
                } else if (window.app && window.app.modules && window.app.modules.assetManager) {
                    window.app.modules.assetManager.loadAssets();
                }
                break;
                
            case 'settings':
                // Load settings
                if (typeof loadSettings === 'function') {
                    loadSettings();
                }
                break;
                
            case 'admin':
                // Load admin panel
                if (typeof loadAdminPanel === 'function') {
                    loadAdminPanel();
                }
                break;
        }
    }
    
    // Update sidebar active state
    function updateSidebarActiveState(sectionName) {
        // Remove active class from all nav items
        const navItems = document.querySelectorAll('.nav-item, .sidebar-link, [data-section]');
        navItems.forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to matching nav item
        const activeItem = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }
    
    // Create placeholder section if it doesn't exist
    function createPlaceholderSection(sectionName) {
        console.log(`📦 Creating placeholder for section: ${sectionName}`);
        
        const mainContent = document.querySelector('main') || 
                          document.querySelector('.main-content') || 
                          document.querySelector('#content') ||
                          document.body;
        
        const placeholder = document.createElement('div');
        placeholder.id = `${sectionName}-section`;
        placeholder.className = 'section-content';
        placeholder.style.display = 'block';
        placeholder.innerHTML = `
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-body">
                                <h2 class="card-title">
                                    ${sectionName.charAt(0).toUpperCase() + sectionName.slice(1)} Section
                                </h2>
                                <p class="text-muted">
                                    This section is currently being loaded...
                                </p>
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">Loading...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        mainContent.appendChild(placeholder);
    }
    
    // Handle hash changes
    function handleHashChange() {
        const hash = window.location.hash.replace('#', '');
        if (hash) {
            showSection(hash);
        }
    }
    
    // Initialize sidebar navigation
    function initializeSidebarNavigation() {
        console.log('🚀 Initializing sidebar navigation...');
        
        // Attach click handlers to all nav items
        const navItems = document.querySelectorAll('[data-section]');
        navItems.forEach(item => {
            // Remove any existing click handlers
            const newItem = item.cloneNode(true);
            item.parentNode.replaceChild(newItem, item);
            
            // Add new click handler
            newItem.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const section = this.dataset.section;
                if (section) {
                    console.log(`👆 Nav item clicked: ${section}`);
                    showSection(section);
                }
            });
        });
        
        // Handle browser back/forward
        window.addEventListener('hashchange', handleHashChange);
        
        // Show initial section based on hash or default to dashboard
        const initialHash = window.location.hash.replace('#', '');
        const initialSection = initialHash || 'dashboard';
        
        // Small delay to ensure DOM is ready
        setTimeout(() => {
            showSection(initialSection);
        }, 100);
    }
    
    // Make showSection globally available
    window.showSection = showSection;
    
    // Also attach to window.app if it exists
    if (window.app) {
        window.app.showSection = showSection;
    } else {
        // Create app object if it doesn't exist
        window.app = window.app || {};
        window.app.showSection = showSection;
    }
    
    // Also create aliases for compatibility
    window.navigateToSection = showSection;
    window.switchSection = showSection;
    window.loadSection = showSection;
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeSidebarNavigation);
    } else {
        initializeSidebarNavigation();
    }
    
    // Also initialize after a delay to catch late-loading elements
    setTimeout(initializeSidebarNavigation, 500);
    
    console.log('✅ Sidebar Navigation Fix loaded');
})();
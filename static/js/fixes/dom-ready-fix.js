// DOM Ready Fix - Ensures all elements are found and visible
(function() {
    'use strict';
    
    console.log('🚀 DOM Ready Fix initializing...');
    
    // Override the showSection function immediately
    window.showSection = function(sectionName) {
        console.log(`🔄 Showing section: ${sectionName}`);
        
        // Hide all sections
        const sections = document.querySelectorAll('.content-section');
        sections.forEach(section => {
            section.classList.remove('active');
            section.style.display = 'none';
        });
        
        // Show the requested section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
            targetSection.style.display = 'block';
            targetSection.style.visibility = 'visible';
            targetSection.style.opacity = '1';
            console.log(`✅ Section displayed: ${sectionName}`);
        } else {
            console.error(`❌ Section not found: ${sectionName}-section`);
        }
        
        // Update sidebar navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.dataset.section === sectionName) {
                item.classList.add('active');
            }
        });
    };
    
    // Wait for DOM content to be loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    function initialize() {
        console.log('✅ DOM Ready - Initializing fixes');
        
        // Fix sidebar visibility immediately
        fixSidebar();
        
        // Fix section visibility
        fixSections();
        
        // Set up navigation
        setupNavigation();
        
        // Show dashboard by default
        setTimeout(() => {
            showSection('dashboard');
        }, 100);
        
        // Keep elements visible
        setInterval(() => {
            const sidebar = document.getElementById('sidebar') || document.querySelector('.sidebar');
            if (sidebar && (sidebar.style.display === 'none' || sidebar.style.visibility === 'hidden')) {
                sidebar.style.display = 'flex';
                sidebar.style.visibility = 'visible';
                sidebar.style.opacity = '1';
            }
            
            const activeSection = document.querySelector('.content-section.active');
            if (activeSection && activeSection.style.display === 'none') {
                activeSection.style.display = 'block';
                activeSection.style.visibility = 'visible';
                activeSection.style.opacity = '1';
            }
        }, 500);
        
        console.log('✅ DOM Ready Fix complete');
    }
    
    function fixSidebar() {
        const sidebar = document.getElementById('sidebar') || document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.style.display = 'flex';
            sidebar.style.visibility = 'visible';
            sidebar.style.opacity = '1';
            sidebar.style.position = 'fixed';
            sidebar.style.left = '0';
            sidebar.style.top = '60px';
            sidebar.style.bottom = '0';
            sidebar.style.width = '250px';
            sidebar.style.zIndex = '1000';
            console.log('✅ Sidebar fixed');
        } else {
            console.warn('⚠️ Sidebar not found');
        }
    }
    
    function fixSections() {
        const sections = [
            'dashboard-section',
            'search-section',
            'assets-section',
            'admin-section',
            'settings-section'
        ];
        
        sections.forEach(sectionId => {
            const section = document.getElementById(sectionId);
            if (section) {
                // Remove any hiding styles
                section.style.removeProperty('display');
                section.style.removeProperty('visibility');
                section.style.removeProperty('opacity');
                
                // Ensure it has the content-section class
                if (!section.classList.contains('content-section')) {
                    section.classList.add('content-section');
                }
                
                // Hide by default (will show active one later)
                if (!section.classList.contains('active')) {
                    section.style.display = 'none';
                }
                
                console.log(`✅ Section prepared: ${sectionId}`);
            } else {
                console.warn(`⚠️ Section not found: ${sectionId}`);
            }
        });
    }
    
    function setupNavigation() {
        // Set up navigation click handlers
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            // Remove any existing listeners
            item.replaceWith(item.cloneNode(true));
        });
        
        // Re-select and add new listeners
        const newNavItems = document.querySelectorAll('.nav-item');
        newNavItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const section = this.dataset.section;
                if (section) {
                    console.log(`Navigation clicked: ${section}`);
                    showSection(section);
                }
            });
        });
        
        console.log(`✅ Navigation setup for ${newNavItems.length} items`);
    }
    
    // Also override app.showSection if it exists
    const checkApp = setInterval(() => {
        if (window.app && window.app.showSection) {
            const originalShowSection = window.app.showSection;
            window.app.showSection = function(section) {
                console.log('🔧 Intercepted app.showSection:', section);
                window.showSection(section);
                try {
                    originalShowSection.call(this, section);
                } catch(e) {
                    console.log('Original showSection failed, but fixed version worked');
                }
            };
            clearInterval(checkApp);
            console.log('✅ App showSection overridden');
        }
    }, 100);
    
    // Stop checking after 5 seconds
    setTimeout(() => {
        clearInterval(checkApp);
    }, 5000);
})();
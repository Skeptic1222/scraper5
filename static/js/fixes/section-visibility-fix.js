// Section Visibility Fix - Ensures sections are found and displayed
(function() {
    'use strict';
    
    console.log('🔧 Section Visibility Fix starting...');
    
    // Wait for DOM
    function waitForDOM(callback) {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', callback);
        } else {
            callback();
        }
    }
    
    waitForDOM(function() {
        console.log('🔍 Looking for sections...');
        
        // Find all sections
        const sections = {
            dashboard: document.getElementById('dashboard-section'),
            search: document.getElementById('search-section'),
            assets: document.getElementById('assets-section'),
            admin: document.getElementById('admin-section'),
            settings: document.getElementById('settings-section')
        };
        
        // Report what we found
        for (const [name, element] of Object.entries(sections)) {
            if (element) {
                console.log(`✅ Found section: ${name}-section`);
                // Ensure the section has proper classes
                element.classList.add('content-section');
                // Hide all sections initially except dashboard
                if (name === 'dashboard') {
                    element.style.display = 'block';
                    element.classList.add('active');
                } else {
                    element.style.display = 'none';
                    element.classList.remove('active');
                }
            } else {
                console.warn(`⚠️ Section not found: ${name}-section`);
            }
        }
        
        // Find sidebar
        const sidebar = document.querySelector('.sidebar') || document.getElementById('sidebar');
        if (sidebar) {
            console.log('✅ Sidebar found');
            sidebar.style.display = 'flex';
            sidebar.style.visibility = 'visible';
            sidebar.style.opacity = '1';
        } else {
            console.warn('⚠️ Sidebar not found');
        }
        
        // Global section switching function
        window.switchToSection = function(sectionName) {
            console.log(`Switching to section: ${sectionName}`);
            
            // Hide all sections
            for (const [name, element] of Object.entries(sections)) {
                if (element) {
                    element.style.display = 'none';
                    element.classList.remove('active');
                }
            }
            
            // Show requested section
            if (sections[sectionName]) {
                sections[sectionName].style.display = 'block';
                sections[sectionName].classList.add('active');
                console.log(`✅ Section ${sectionName} is now active`);
            }
            
            // Update navigation
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach(item => {
                item.classList.remove('active');
                if (item.dataset.section === sectionName) {
                    item.classList.add('active');
                }
            });
        };
        
        // Override showSection if it exists
        if (typeof window.showSection === 'function') {
            const originalShowSection = window.showSection;
            window.showSection = function(sectionName) {
                console.log(`Intercepted showSection: ${sectionName}`);
                window.switchToSection(sectionName);
                try {
                    originalShowSection(sectionName);
                } catch (e) {
                    console.log('Original showSection failed, but switchToSection worked');
                }
            };
        } else {
            window.showSection = window.switchToSection;
        }
        
        // Set up navigation clicks
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const section = this.dataset.section;
                if (section) {
                    window.switchToSection(section);
                }
            });
        });
        
        console.log('✅ Section Visibility Fix complete');
    });
    
    // Monitor for changes
    const observer = new MutationObserver(() => {
        const dashboardSection = document.getElementById('dashboard-section');
        if (dashboardSection && dashboardSection.style.display === 'none' && !document.querySelector('.content-section.active')) {
            console.log('🔧 Re-showing dashboard section');
            dashboardSection.style.display = 'block';
            dashboardSection.classList.add('active');
        }
    });
    
    // Start observing when DOM is ready
    waitForDOM(() => {
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class']
        });
    });
})();
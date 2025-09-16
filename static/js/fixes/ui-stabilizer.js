// UI Stabilizer - Simple and effective UI fix
(function() {
    'use strict';
    
    console.log('🚀 UI Stabilizer loading...');
    
    // Wait for DOM to be ready
    function domReady(fn) {
        if (document.readyState != 'loading'){
            fn();
        } else {
            document.addEventListener('DOMContentLoaded', fn);
        }
    }
    
    domReady(function() {
        console.log('✅ DOM Ready - Stabilizing UI');
        
        // 1. Ensure all sections exist and are properly styled
        const sections = [
            'dashboard-section',
            'search-section', 
            'assets-section',
            'admin-section',
            'settings-section'
        ];
        
        sections.forEach((sectionId, index) => {
            const section = document.getElementById(sectionId);
            if (section) {
                section.style.display = index === 0 ? 'block' : 'none'; // Show dashboard by default
                section.style.visibility = 'visible';
                section.style.opacity = '1';
                console.log(`✅ Section stabilized: ${sectionId}`);
            }
        });
        
        // 2. Ensure sidebar is visible
        const sidebar = document.querySelector('.sidebar') || document.getElementById('sidebar');
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
            sidebar.style.backgroundColor = 'var(--sidebar-bg, #f8f9fa)';
            console.log('✅ Sidebar stabilized');
        }
        
        // 3. Simple section switching
        window.switchSection = function(sectionName) {
            console.log(`Switching to section: ${sectionName}`);
            
            // Hide all sections
            sections.forEach(sectionId => {
                const section = document.getElementById(sectionId);
                if (section) {
                    section.style.display = 'none';
                }
            });
            
            // Show requested section
            const targetSection = document.getElementById(`${sectionName}-section`);
            if (targetSection) {
                targetSection.style.display = 'block';
                targetSection.style.visibility = 'visible';
                targetSection.style.opacity = '1';
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
        
        // 4. Set up navigation
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.onclick = function(e) {
                e.preventDefault();
                const section = this.dataset.section;
                if (section) {
                    switchSection(section);
                }
                return false;
            };
        });
        
        // 5. Ensure main content area is properly positioned
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.style.marginLeft = '250px';
            mainContent.style.paddingTop = '20px';
        }
        
        // 6. Keep UI stable
        setInterval(() => {
            // Keep sidebar visible
            const sidebar = document.querySelector('.sidebar');
            if (sidebar && (sidebar.style.display === 'none' || !sidebar.style.display)) {
                sidebar.style.display = 'flex';
            }
            
            // Keep active section visible
            const activeSection = document.querySelector('.content-section.active') || 
                                 document.getElementById('dashboard-section');
            if (activeSection && activeSection.style.display === 'none') {
                activeSection.style.display = 'block';
            }
        }, 1000);
        
        console.log('✅ UI Stabilizer complete');
    });
})();
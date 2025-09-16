/**
 * Enhanced Navigation System
 * Ensures sidebar navigation works consistently across all pages
 */

(function() {
    'use strict';
    
    console.log('🚀 Enhanced Navigation System initializing...');
    
    // Wait for DOM and app to be ready
    function initEnhancedNavigation() {
        // Ensure sidebar is visible
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.style.display = 'block';
            sidebar.style.visibility = 'visible';
            sidebar.style.opacity = '1';
        }
        
        // Get all navigation items
        const navItems = document.querySelectorAll('.nav-item[data-section]');
        const sections = document.querySelectorAll('.content-section');
        
        // Function to show a specific section
        function showSection(sectionName) {
            console.log(`📍 Navigating to section: ${sectionName}`);
            
            // Hide all sections
            sections.forEach(section => {
                section.classList.remove('active');
                section.style.display = 'none';
            });
            
            // Show the selected section
            const targetSection = document.getElementById(`${sectionName}-section`);
            if (targetSection) {
                targetSection.classList.add('active');
                targetSection.style.display = 'block';
                console.log(`✅ Section ${sectionName} is now visible`);
            } else {
                console.warn(`⚠️ Section ${sectionName}-section not found`);
            }
            
            // Update active nav item
            navItems.forEach(item => {
                item.classList.remove('active');
                if (item.dataset.section === sectionName) {
                    item.classList.add('active');
                }
            });
            
            // Store current section in localStorage
            localStorage.setItem('currentSection', sectionName);
            
            // Update URL hash without triggering scroll
            if (history.replaceState) {
                history.replaceState(null, null, `#${sectionName}`);
            }
        }
        
        // Add click handlers to navigation items
        navItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const section = this.dataset.section;
                if (section) {
                    showSection(section);
                    
                    // If app exists, notify it
                    if (window.app && typeof window.app.showSection === 'function') {
                        window.app.showSection(section);
                    }
                }
            });
        });
        
        // Handle navigation from other sources (like buttons)
        document.addEventListener('click', function(e) {
            const target = e.target.closest('[data-section]');
            if (target && !target.classList.contains('nav-item')) {
                const section = target.dataset.section;
                if (section) {
                    showSection(section);
                }
            }
        });
        
        // Restore last section or show default
        function restoreSection() {
            const hash = window.location.hash.slice(1);
            const savedSection = localStorage.getItem('currentSection');
            const defaultSection = 'dashboard';
            
            let sectionToShow = hash || savedSection || defaultSection;
            
            // Verify section exists
            const sectionElement = document.getElementById(`${sectionToShow}-section`);
            if (!sectionElement) {
                sectionToShow = defaultSection;
            }
            
            showSection(sectionToShow);
        }
        
        // Handle browser back/forward
        window.addEventListener('hashchange', function() {
            const section = window.location.hash.slice(1);
            if (section) {
                showSection(section);
            }
        });
        
        // Mobile menu toggle
        function setupMobileMenu() {
            // Create mobile menu button if it doesn't exist
            let mobileToggle = document.querySelector('.mobile-menu-toggle');
            if (!mobileToggle && window.innerWidth <= 768) {
                mobileToggle = document.createElement('button');
                mobileToggle.className = 'mobile-menu-toggle';
                mobileToggle.innerHTML = '<i class="fas fa-bars"></i>';
                mobileToggle.setAttribute('aria-label', 'Toggle navigation menu');
                document.body.appendChild(mobileToggle);
                
                mobileToggle.addEventListener('click', function() {
                    const sidebar = document.querySelector('.sidebar');
                    if (sidebar) {
                        sidebar.classList.toggle('mobile-open');
                    }
                });
            }
            
            // Close mobile menu when clicking on nav item
            if (window.innerWidth <= 768) {
                navItems.forEach(item => {
                    item.addEventListener('click', function() {
                        const sidebar = document.querySelector('.sidebar');
                        if (sidebar) {
                            sidebar.classList.remove('mobile-open');
                        }
                    });
                });
            }
        }
        
        // Performance optimization: Debounce resize events
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(setupMobileMenu, 250);
        });
        
        // Initialize mobile menu
        setupMobileMenu();
        
        // Restore section
        restoreSection();
        
        // Make navigation functions globally available
        window.enhancedNavigation = {
            showSection: showSection,
            getCurrentSection: function() {
                const activeSection = document.querySelector('.content-section.active');
                return activeSection ? activeSection.id.replace('-section', '') : null;
            },
            refreshNavigation: function() {
                restoreSection();
            }
        };
        
        console.log('✅ Enhanced Navigation System ready');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEnhancedNavigation);
    } else {
        // DOM is already loaded
        setTimeout(initEnhancedNavigation, 100);
    }
    
    // Also initialize when app is ready
    window.addEventListener('load', function() {
        setTimeout(initEnhancedNavigation, 500);
    });
})();
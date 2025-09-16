/**
 * Force Sidebar Position Fix
 * Ensures sidebar stays in correct position at all times
 */

(function() {
    'use strict';
    
    console.log('🔧 Force Sidebar Position Fix initializing...');
    
    // Function to force sidebar position
    function forceSidebarPosition() {
        const sidebar = document.querySelector('.sidebar');
        const navbar = document.querySelector('.navbar');
        const mainContent = document.querySelector('#main-content, .content-area');
        
        if (sidebar) {
            // Remove any inline styles that might interfere
            sidebar.removeAttribute('style');
            
            // Force correct positioning
            sidebar.style.cssText = `
                position: fixed !important;
                top: 60px !important;
                left: 0 !important;
                bottom: 0 !important;
                width: 260px !important;
                height: calc(100vh - 60px) !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                background: #ffffff !important;
                border-right: 1px solid #e5e7eb !important;
                z-index: 9999 !important;
                display: block !important;
                visibility: visible !important;
                opacity: 1 !important;
                transform: none !important;
                margin: 0 !important;
                padding: 0 !important;
            `;
            
            console.log('✅ Sidebar position forced to fixed');
        }
        
        if (navbar) {
            // Ensure navbar is fixed at top
            navbar.style.cssText = `
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                width: 100% !important;
                height: 60px !important;
                z-index: 10000 !important;
            `;
        }
        
        if (mainContent) {
            // Ensure content area respects sidebar
            mainContent.style.cssText = `
                margin-left: 260px !important;
                width: calc(100% - 260px) !important;
                min-height: calc(100vh - 60px) !important;
                padding: 24px !important;
                position: relative !important;
            `;
        }
        
        // Ensure body has correct padding
        document.body.style.paddingTop = '60px';
        document.body.style.margin = '0';
        document.body.style.overflowX = 'hidden';
    }
    
    // Function to fix dashboard section specifically
    function fixDashboardSection() {
        const dashboardSection = document.querySelector('#dashboard-section');
        if (dashboardSection && dashboardSection.classList.contains('active')) {
            // Remove any problematic styles
            dashboardSection.style.position = 'relative';
            dashboardSection.style.transform = 'none';
            dashboardSection.style.marginTop = '0';
            dashboardSection.style.paddingTop = '0';
            
            // Ensure it doesn't affect sidebar
            const allChildren = dashboardSection.querySelectorAll('*');
            allChildren.forEach(child => {
                const styles = window.getComputedStyle(child);
                if (styles.position === 'fixed' || styles.position === 'absolute') {
                    if (!child.classList.contains('sidebar') && !child.classList.contains('navbar')) {
                        child.style.position = 'relative';
                    }
                }
            });
            
            console.log('✅ Dashboard section layout fixed');
        }
    }
    
    // Monitor for section changes
    function monitorSectionChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                    if (mutation.target.classList && mutation.target.classList.contains('active')) {
                        console.log('🔄 Section changed, reapplying fixes...');
                        forceSidebarPosition();
                        fixDashboardSection();
                    }
                }
            });
        });
        
        // Observe all content sections
        document.querySelectorAll('.content-section').forEach(section => {
            observer.observe(section, { attributes: true });
        });
    }
    
    // Override any function that might change sidebar position
    function interceptNavigationFunctions() {
        // Intercept showSection if it exists
        if (window.app && window.app.showSection) {
            const originalShowSection = window.app.showSection;
            window.app.showSection = function(section) {
                const result = originalShowSection.apply(this, arguments);
                setTimeout(() => {
                    forceSidebarPosition();
                    fixDashboardSection();
                }, 50);
                return result;
            };
        }
        
        // Intercept any global showSection function
        if (window.showSection) {
            const originalShowSection = window.showSection;
            window.showSection = function(section) {
                const result = originalShowSection.apply(this, arguments);
                setTimeout(() => {
                    forceSidebarPosition();
                    fixDashboardSection();
                }, 50);
                return result;
            };
        }
    }
    
    // Initialize fixes
    function initialize() {
        forceSidebarPosition();
        fixDashboardSection();
        monitorSectionChanges();
        interceptNavigationFunctions();
        
        // Reapply fixes periodically in case something changes
        setInterval(() => {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                const computedStyle = window.getComputedStyle(sidebar);
                if (computedStyle.position !== 'fixed' || computedStyle.top !== '60px') {
                    console.log('⚠️ Sidebar position changed, reapplying fix...');
                    forceSidebarPosition();
                }
            }
        }, 1000);
        
        console.log('✅ Force Sidebar Position Fix active');
    }
    
    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Also run after window load
    window.addEventListener('load', () => {
        setTimeout(initialize, 100);
    });
    
    // Handle navigation clicks
    document.addEventListener('click', (e) => {
        if (e.target.closest('.nav-item[data-section]')) {
            setTimeout(() => {
                forceSidebarPosition();
                fixDashboardSection();
            }, 100);
        }
    });
    
    // Export for debugging
    window.forceSidebarFix = {
        forceSidebarPosition,
        fixDashboardSection
    };
})();
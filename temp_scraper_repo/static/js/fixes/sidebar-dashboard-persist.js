/**
 * Sidebar and Dashboard Persistence Fix
 * Ensures sidebar and dashboard content remain visible after page load
 */

(function() {
    'use strict';
    
    console.log('🛡️ Sidebar/Dashboard Persistence Fix loading...');
    
    // Override the showSection method to prevent hiding sidebar and dashboard
    function patchShowSection() {
        // Store original showSection if it exists
        const originalShowSection = window.MediaScraperApp?.prototype?.showSection || 
                                   window.app?.showSection || 
                                   window.showSection;
        
        // Create enhanced showSection that preserves sidebar
        const enhancedShowSection = function(sectionName) {
            console.log(`🔄 Enhanced showSection called for: ${sectionName}`);
            
            // Ensure sidebar stays visible
            const sidebar = document.querySelector('.sidebar, #sidebar, aside.sidebar');
            if (sidebar) {
                sidebar.style.display = 'block';
                sidebar.style.visibility = 'visible';
                sidebar.style.opacity = '1';
                sidebar.classList.remove('hidden', 'd-none', 'collapsed');
            }
            
            // Call original if it exists
            if (originalShowSection && typeof originalShowSection === 'function') {
                // Use call/apply to maintain proper context
                const result = originalShowSection.call(this, sectionName);
                
                // Re-ensure sidebar visibility after original call
                if (sidebar) {
                    sidebar.style.display = 'block';
                    sidebar.style.visibility = 'visible';
                    sidebar.style.opacity = '1';
                }
                
                return result;
            } else {
                // Fallback implementation if no original exists
                const sections = document.querySelectorAll('.content-section');
                sections.forEach(section => {
                    section.classList.remove('active');
                    section.style.display = 'none';
                });
                
                const targetSection = document.getElementById(`${sectionName}-section`);
                if (targetSection) {
                    targetSection.classList.add('active');
                    targetSection.style.display = 'block';
                    targetSection.style.visibility = 'visible';
                    targetSection.style.opacity = '1';
                }
            }
            
            // Ensure dashboard content is visible if dashboard is selected
            if (sectionName === 'dashboard') {
                const dashboardSection = document.getElementById('dashboard-section');
                if (dashboardSection) {
                    dashboardSection.style.display = 'block';
                    dashboardSection.style.visibility = 'visible';
                    dashboardSection.style.opacity = '1';
                    
                    // Also ensure all dashboard child elements are visible
                    const dashboardContent = dashboardSection.querySelectorAll('.dashboard-content, .enhanced-stats-grid, .dashboard-container');
                    dashboardContent.forEach(el => {
                        el.style.display = '';
                        el.style.visibility = 'visible';
                        el.style.opacity = '1';
                    });
                }
            }
        };
        
        // Apply the patch to all possible locations
        if (window.MediaScraperApp?.prototype) {
            window.MediaScraperApp.prototype.showSection = enhancedShowSection;
        }
        if (window.app) {
            window.app.showSection = enhancedShowSection;
        }
        window.showSection = enhancedShowSection;
        
        // Also create aliases
        window.navigateToSection = enhancedShowSection;
        window.switchSection = enhancedShowSection;
    }
    
    // Force sidebar and content visibility periodically
    function enforceSidebarVisibility() {
        const sidebar = document.querySelector('.sidebar, #sidebar, aside.sidebar');
        if (sidebar) {
            sidebar.style.display = 'block';
            sidebar.style.visibility = 'visible';
            sidebar.style.opacity = '1';
            sidebar.style.position = 'sticky';
            sidebar.style.top = '60px';
            sidebar.style.left = '0';
            sidebar.style.width = '260px';
            sidebar.style.height = 'calc(100vh - 60px)';
            sidebar.style.zIndex = '1000';
            sidebar.classList.remove('hidden', 'd-none', 'collapsed');
        }
        
        // Also ensure active content section is visible
        const activeSection = document.querySelector('.content-section.active');
        if (activeSection) {
            activeSection.style.display = 'block';
            activeSection.style.visibility = 'visible';
            activeSection.style.opacity = '1';
        }
    }
    
    // Apply fixes when DOM is ready
    function applyFixes() {
        console.log('🔧 Applying sidebar/dashboard persistence fixes...');
        
        // Patch showSection
        patchShowSection();
        
        // Force initial visibility
        enforceSidebarVisibility();
        
        // Set dashboard as default if no section is active
        const hasActiveSection = document.querySelector('.content-section.active');
        if (!hasActiveSection) {
            const dashboardSection = document.getElementById('dashboard-section');
            if (dashboardSection) {
                dashboardSection.classList.add('active');
                dashboardSection.style.display = 'block';
                dashboardSection.style.visibility = 'visible';
                dashboardSection.style.opacity = '1';
            }
        }
        
        // Monitor for changes that might hide sidebar
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && 
                    (mutation.attributeName === 'style' || 
                     mutation.attributeName === 'class')) {
                    
                    const target = mutation.target;
                    if (target.matches && target.matches('.sidebar, #sidebar, aside.sidebar')) {
                        const style = window.getComputedStyle(target);
                        if (style.display === 'none' || 
                            style.visibility === 'hidden' || 
                            parseFloat(style.opacity) < 1) {
                            console.log('⚠️ Sidebar was hidden, restoring visibility...');
                            enforceSidebarVisibility();
                        }
                    }
                }
            });
        });
        
        // Start observing
        const sidebar = document.querySelector('.sidebar, #sidebar, aside.sidebar');
        if (sidebar) {
            observer.observe(sidebar, {
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        }
        
        console.log('✅ Sidebar/dashboard persistence fixes applied');
    }
    
    // Wait for app initialization
    let appCheckInterval = setInterval(() => {
        if (window.app || window.MediaScraperApp) {
            clearInterval(appCheckInterval);
            applyFixes();
            
            // Also apply fixes after a delay to catch late initializations
            setTimeout(applyFixes, 500);
            setTimeout(applyFixes, 1000);
            setTimeout(applyFixes, 2000);
        }
    }, 100);
    
    // Apply fixes on various events
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', applyFixes);
    } else {
        applyFixes();
    }
    
    // Also apply on window load
    window.addEventListener('load', () => {
        setTimeout(applyFixes, 100);
    });
    
    // Periodic enforcement (every 3 seconds)
    setInterval(enforceSidebarVisibility, 3000);
    
})();
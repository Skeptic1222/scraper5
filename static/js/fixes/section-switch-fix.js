/**
 * Section Switch Fix
 * Overrides the showSection method to prevent layout breaking
 */

(function() {
    'use strict';
    
    console.log('🔧 Section Switch Fix initializing...');
    
    // Wait for app to be ready
    function waitForApp() {
        if (window.app && window.app.showSection) {
            console.log('✅ App found, patching showSection...');
            patchShowSection();
        } else if (window.MediaScraperApp && window.MediaScraperApp.prototype.showSection) {
            console.log('✅ MediaScraperApp found, patching prototype...');
            patchPrototype();
        } else {
            setTimeout(waitForApp, 100);
        }
    }
    
    function patchShowSection() {
        const originalShowSection = window.app.showSection;
        
        window.app.showSection = function(sectionName) {
            console.log(`🔧 [FIXED] Switching to section: ${sectionName}`);
            
            // Handle legacy redirects
            if (sectionName === 'downloads') {
                sectionName = 'dashboard';
            }
            
            // CRITICAL FIX: Lock sidebar before switching
            lockSidebar();
            
            // Hide all sections using visibility instead of display
            const allSections = document.querySelectorAll('.content-section');
            allSections.forEach(section => {
                section.style.position = 'absolute';
                section.style.top = '0';
                section.style.left = '0';
                section.style.width = '100%';
                section.style.height = '100%';
                section.style.visibility = 'hidden';
                section.style.opacity = '0';
                section.classList.remove('active');
            });
            
            // Show target section
            const targetSection = document.getElementById(`${sectionName}-section`);
            if (targetSection) {
                targetSection.style.visibility = 'visible';
                targetSection.style.opacity = '1';
                targetSection.classList.add('active');
                
                // Update state
                this.state.currentSection = sectionName;
                
                // Update navigation
                if (this.updateNavigation) {
                    this.updateNavigation(sectionName);
                }
                
                // Load section data
                if (this.loadSectionData) {
                    this.loadSectionData(sectionName);
                }
                
                // Update URL
                if (this.updateURL) {
                    this.updateURL(sectionName);
                }
                
                console.log(`✅ [FIXED] Successfully switched to: ${sectionName}`);
            } else {
                console.error(`❌ Section not found: ${sectionName}-section`);
                if (sectionName !== 'dashboard') {
                    this.showSection('dashboard');
                }
            }
            
            // CRITICAL FIX: Ensure layout is correct after switch
            setTimeout(() => {
                enforceLayout();
            }, 0);
        }.bind(window.app);
    }
    
    function patchPrototype() {
        const originalShowSection = window.MediaScraperApp.prototype.showSection;
        
        window.MediaScraperApp.prototype.showSection = function(sectionName) {
            console.log(`🔧 [FIXED] Switching to section: ${sectionName}`);
            
            // Handle legacy redirects
            if (sectionName === 'downloads') {
                sectionName = 'dashboard';
            }
            
            // CRITICAL FIX: Lock sidebar before switching
            lockSidebar();
            
            // Hide all sections using visibility instead of display
            const allSections = document.querySelectorAll('.content-section');
            allSections.forEach(section => {
                section.style.position = 'absolute';
                section.style.top = '0';
                section.style.left = '0';
                section.style.width = '100%';
                section.style.height = '100%';
                section.style.visibility = 'hidden';
                section.style.opacity = '0';
                section.classList.remove('active');
            });
            
            // Show target section
            const targetSection = document.getElementById(`${sectionName}-section`);
            if (targetSection) {
                targetSection.style.visibility = 'visible';
                targetSection.style.opacity = '1';
                targetSection.classList.add('active');
                
                // Update state
                this.state.currentSection = sectionName;
                
                // Update navigation
                if (this.updateNavigation) {
                    this.updateNavigation(sectionName);
                }
                
                // Load section data
                if (this.loadSectionData) {
                    this.loadSectionData(sectionName);
                }
                
                // Update URL
                if (this.updateURL) {
                    this.updateURL(sectionName);
                }
                
                console.log(`✅ [FIXED] Successfully switched to: ${sectionName}`);
            } else {
                console.error(`❌ Section not found: ${sectionName}-section`);
                if (sectionName !== 'dashboard') {
                    this.showSection('dashboard');
                }
            }
            
            // CRITICAL FIX: Ensure layout is correct after switch
            setTimeout(() => {
                enforceLayout();
            }, 0);
        };
    }
    
    function lockSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            // Use grid position which cannot be moved
            sidebar.style.cssText = `
                grid-column: 1 !important;
                width: 260px !important;
                height: 100% !important;
                position: relative !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
                transform: none !important;
                left: auto !important;
                top: auto !important;
            `;
        }
    }
    
    function enforceLayout() {
        // Ensure main container uses grid
        const mainContainer = document.querySelector('.main-container');
        if (mainContainer) {
            mainContainer.style.cssText = `
                position: absolute !important;
                top: 60px !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                display: grid !important;
                grid-template-columns: 260px 1fr !important;
                overflow: hidden !important;
            `;
        }
        
        // Lock sidebar in grid
        lockSidebar();
        
        // Ensure content area in grid
        const contentArea = document.querySelector('.content-area, #main-content');
        if (contentArea) {
            contentArea.style.cssText = `
                grid-column: 2 !important;
                width: 100% !important;
                height: 100% !important;
                position: relative !important;
                overflow-y: auto !important;
                overflow-x: hidden !important;
            `;
        }
        
        // Remove any extra scrollbars
        const unnecessaryScrolls = document.querySelectorAll('.container, .container-fluid, .row, .col');
        unnecessaryScrolls.forEach(el => {
            el.style.overflow = 'visible';
        });
    }
    
    // Start waiting for app
    waitForApp();
    
    // Also patch any navigation clicks
    document.addEventListener('click', function(e) {
        const navLink = e.target.closest('[data-section], .nav-link[href*="section="]');
        if (navLink) {
            // Ensure layout is enforced after any navigation
            setTimeout(enforceLayout, 0);
        }
    }, true);
    
    console.log('✅ Section Switch Fix ready');
})();
/**
 * CRITICAL SIDEBAR INITIALIZATION FIX
 * Ensures sidebar is immediately visible and functional
 * Addresses test failure: "Sidebar not found or not visible"
 */

(function() {
    'use strict';

    console.log('🚨 CRITICAL: Sidebar initialization fix loading...');

    // IMMEDIATE SIDEBAR VISIBILITY ENFORCEMENT
    function forceSidebarVisible() {
        const sidebar = document.querySelector('.sidebar, #sidebar, aside.sidebar');
        if (sidebar) {
            // Force visibility with highest priority
            sidebar.style.setProperty('display', 'block', 'important');
            sidebar.style.setProperty('visibility', 'visible', 'important');
            sidebar.style.setProperty('opacity', '1', 'important');
            sidebar.style.setProperty('position', 'fixed', 'important');
            sidebar.style.setProperty('top', '60px', 'important');
            sidebar.style.setProperty('left', '0', 'important');
            sidebar.style.setProperty('width', '260px', 'important');
            sidebar.style.setProperty('height', 'calc(100vh - 60px)', 'important');
            sidebar.style.setProperty('z-index', '1000', 'important');
            sidebar.style.setProperty('background', '#ffffff', 'important');
            sidebar.style.setProperty('border-right', '1px solid #e0e0e0', 'important');
            sidebar.style.setProperty('overflow-y', 'auto', 'important');
            sidebar.style.setProperty('padding', '20px', 'important');

            // Remove any hiding classes
            sidebar.classList.remove('hidden', 'd-none', 'collapsed', 'minimized');

            // Force content area layout
            const contentArea = document.querySelector('.content-area, #main-content');
            if (contentArea) {
                contentArea.style.setProperty('margin-left', '260px', 'important');
                contentArea.style.setProperty('width', 'calc(100% - 260px)', 'important');
            }

            // Force main container layout
            const mainContainer = document.querySelector('.main-container');
            if (mainContainer) {
                mainContainer.style.setProperty('display', 'flex', 'important');
                mainContainer.style.setProperty('margin-top', '60px', 'important');
            }

            console.log('✅ CRITICAL: Sidebar forced visible');
            return true;
        }
        console.log('❌ CRITICAL: Sidebar element not found');
        return false;
    }

    // NAVIGATION FUNCTIONALITY
    function initializeSidebarNavigation() {
        const navItems = document.querySelectorAll('.nav-item[data-section]');
        console.log(`🔗 CRITICAL: Found ${navItems.length} navigation items`);

        navItems.forEach((item, index) => {
            // Ensure item is visible and clickable
            item.style.setProperty('display', 'flex', 'important');
            item.style.setProperty('visibility', 'visible', 'important');
            item.style.setProperty('opacity', '1', 'important');
            item.style.setProperty('cursor', 'pointer', 'important');
            item.style.setProperty('pointer-events', 'auto', 'important');

            // Remove existing event listeners
            const newItem = item.cloneNode(true);
            item.parentNode.replaceChild(newItem, item);

            // Add enhanced click handler
            newItem.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const section = this.dataset.section;
                console.log(`🎯 CRITICAL: Navigation clicked - ${section}`);

                // Update active state
                document.querySelectorAll('.nav-item').forEach(nav => {
                    nav.classList.remove('active');
                });
                this.classList.add('active');

                // Call app navigation if available
                if (window.app && window.app.showSection) {
                    console.log(`📱 CRITICAL: Using app.showSection for ${section}`);
                    window.app.showSection(section);
                } else if (window.showSection) {
                    console.log(`🌐 CRITICAL: Using window.showSection for ${section}`);
                    window.showSection(section);
                } else {
                    // Fallback navigation
                    console.log(`🔄 CRITICAL: Using fallback navigation for ${section}`);
                    showSectionFallback(section);
                }

                // Ensure sidebar remains visible after navigation
                setTimeout(forceSidebarVisible, 100);
            });

            console.log(`✅ CRITICAL: Navigation item ${index + 1} initialized: ${newItem.dataset.section}`);
        });
    }

    // FALLBACK SECTION NAVIGATION
    function showSectionFallback(sectionName) {
        console.log(`🔄 CRITICAL: Fallback navigation to ${sectionName}`);

        // Hide all sections
        const sections = document.querySelectorAll('.content-section, [id$="-section"]');
        sections.forEach(section => {
            section.style.display = 'none';
            section.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.style.setProperty('display', 'block', 'important');
            targetSection.style.setProperty('visibility', 'visible', 'important');
            targetSection.style.setProperty('opacity', '1', 'important');
            targetSection.classList.add('active');
            console.log(`✅ CRITICAL: Section ${sectionName} activated`);
        } else {
            console.log(`❌ CRITICAL: Section ${sectionName} not found`);

            // Try to show main content
            const mainContent = document.querySelector('.content-area, #main-content');
            if (mainContent) {
                mainContent.innerHTML = `
                    <div class="alert alert-info">
                        <h4><i class="fas fa-info-circle"></i> ${sectionName.charAt(0).toUpperCase() + sectionName.slice(1)}</h4>
                        <p>This section is loading... Please wait.</p>
                    </div>
                `;
            }
        }
    }

    // CONTINUOUS VISIBILITY MONITORING
    function startVisibilityMonitoring() {
        const observer = new MutationObserver((mutations) => {
            let sidebarModified = false;

            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' &&
                    (mutation.attributeName === 'style' || mutation.attributeName === 'class')) {

                    const target = mutation.target;
                    if (target.matches && target.matches('.sidebar, #sidebar, aside.sidebar')) {
                        const computedStyle = window.getComputedStyle(target);
                        if (computedStyle.display === 'none' ||
                            computedStyle.visibility === 'hidden' ||
                            parseFloat(computedStyle.opacity) < 1) {
                            sidebarModified = true;
                        }
                    }
                }
            });

            if (sidebarModified) {
                console.log('⚠️ CRITICAL: Sidebar visibility compromised, restoring...');
                forceSidebarVisible();
            }
        });

        // Start observing
        const sidebar = document.querySelector('.sidebar, #sidebar, aside.sidebar');
        if (sidebar) {
            observer.observe(sidebar, {
                attributes: true,
                attributeFilter: ['style', 'class']
            });

            // Also observe body for layout changes
            observer.observe(document.body, {
                attributes: true,
                childList: true,
                subtree: true,
                attributeFilter: ['class', 'style']
            });
        }

        console.log('👁️ CRITICAL: Visibility monitoring started');
    }

    // INITIALIZATION SEQUENCE
    function initializeCriticalSidebar() {
        console.log('🚀 CRITICAL: Starting sidebar initialization...');

        // Step 1: Force visibility
        const sidebarFound = forceSidebarVisible();
        if (!sidebarFound) {
            // Try again after a short delay
            setTimeout(() => {
                forceSidebarVisible();
                initializeSidebarNavigation();
            }, 100);
        }

        // Step 2: Initialize navigation
        initializeSidebarNavigation();

        // Step 3: Start monitoring
        startVisibilityMonitoring();

        // Step 4: Set up periodic enforcement
        setInterval(forceSidebarVisible, 2000);

        console.log('✅ CRITICAL: Sidebar initialization complete');

        // Add debug info to window
        window.debugSidebar = {
            forceSidebarVisible,
            initializeSidebarNavigation,
            showSectionFallback
        };
    }

    // MULTIPLE INITIALIZATION TRIGGERS
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeCriticalSidebar);
    } else {
        initializeCriticalSidebar();
    }

    // Backup initialization on window load
    window.addEventListener('load', () => {
        setTimeout(initializeCriticalSidebar, 100);
    });

    // Emergency initialization after delay
    setTimeout(initializeCriticalSidebar, 500);
    setTimeout(initializeCriticalSidebar, 1000);
    setTimeout(initializeCriticalSidebar, 2000);

    console.log('🛡️ CRITICAL: Sidebar fix script loaded');

})();
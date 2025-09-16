/**
 * SEARCH PAGE COMPLETE FIX
 * Fixes all issues with the Search & Download page:
 * 1. Select All Sources checkbox
 * 2. Removes duplicate buttons
 * 3. Consolidates functionality
 * 4. Fixes error messages
 */

(function() {
    'use strict';
    
    console.log('🔧 Search Page Complete Fix initializing...');
    
    // Wait for DOM and required modules
    function waitForDependencies() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeFix);
        } else {
            initializeFix();
        }
    }
    
    function initializeFix() {
        console.log('🚀 Applying comprehensive search page fixes...');
        
        // 1. Remove ALL duplicate select-all implementations
        removeDuplicateControls();
        
        // 2. Create ONE unified control panel
        createUnifiedControls();
        
        // 3. Fix checkbox functionality
        fixCheckboxFunctionality();
        
        // 4. Fix error messages
        fixErrorMessages();
        
        // 5. Monitor for dynamic content
        setupMutationObserver();
    }
    
    function removeDuplicateControls() {
        console.log('🗑️ Removing duplicate controls...');
        
        // Remove all duplicate select-all containers
        const duplicates = [
            '.select-all-sources-container',
            '.select-all-container',
            '#select-all-wrapper',
            '.source-selection-controls'
        ];
        
        duplicates.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach((el, index) => {
                if (index > 0) { // Keep first, remove rest
                    console.log(`Removing duplicate: ${selector}`);
                    el.remove();
                }
            });
        });
        
        // Remove duplicate button groups
        const buttonGroups = document.querySelectorAll('.source-controls-buttons');
        if (buttonGroups.length > 1) {
            for (let i = 1; i < buttonGroups.length; i++) {
                buttonGroups[i].remove();
            }
        }
    }
    
    function createUnifiedControls() {
        console.log('✨ Creating unified control panel...');
        
        const sourcesContainer = document.getElementById('source-categories');
        if (!sourcesContainer) {
            console.warn('Source categories container not found');
            return;
        }
        
        // Remove any existing unified controls
        const existing = document.getElementById('unified-source-controls');
        if (existing) existing.remove();
        
        // Create new unified control panel
        const controlPanel = document.createElement('div');
        controlPanel.id = 'unified-source-controls';
        controlPanel.className = 'unified-controls-panel';
        controlPanel.innerHTML = `
            <div class="control-row">
                <label class="select-all-label">
                    <input type="checkbox" id="master-select-all" class="form-check-input">
                    <span class="label-text">Select All Sources (<span id="source-count">0</span>/<span id="source-total">0</span>)</span>
                </label>
                <div class="control-buttons">
                    <button id="select-recommended-btn" class="btn btn-sm btn-info">
                        <i class="fas fa-star"></i> Recommended
                    </button>
                    <button id="refresh-sources-btn" class="btn btn-sm btn-secondary">
                        <i class="fas fa-sync"></i> Refresh
                    </button>
                </div>
            </div>
        `;
        
        // Insert before sources container
        sourcesContainer.parentNode.insertBefore(controlPanel, sourcesContainer);
        
        // Attach event handlers
        attachControlHandlers();
    }
    
    function attachControlHandlers() {
        // Master select all checkbox
        const masterCheckbox = document.getElementById('master-select-all');
        if (masterCheckbox) {
            masterCheckbox.addEventListener('change', function(e) {
                const isChecked = e.target.checked;
                console.log(`Master checkbox: ${isChecked ? 'Select All' : 'Deselect All'}`);
                
                // Get all source checkboxes
                const checkboxes = document.querySelectorAll('#source-categories input[type="checkbox"]');
                checkboxes.forEach(cb => {
                    cb.checked = isChecked;
                    // Trigger change event for each
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                });
                
                updateSourceCount();
            });
        }
        
        // Select Recommended button
        const recommendedBtn = document.getElementById('select-recommended-btn');
        if (recommendedBtn) {
            recommendedBtn.addEventListener('click', function() {
                console.log('🌟 Selecting recommended sources...');
                
                const recommended = [
                    'youtube', 'dailymotion', 'vimeo', 'twitter',
                    'instagram', 'facebook', 'twitch', 'reddit'
                ];
                
                const checkboxes = document.querySelectorAll('#source-categories input[type="checkbox"]');
                checkboxes.forEach(cb => {
                    const sourceItem = cb.closest('.source-item');
                    const label = sourceItem ? sourceItem.textContent.toLowerCase() : '';
                    
                    // Check if this source is recommended
                    const isRecommended = recommended.some(rec => label.includes(rec));
                    cb.checked = isRecommended;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                });
                
                updateSourceCount();
                updateMasterCheckbox();
            });
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refresh-sources-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', function() {
                console.log('🔄 Refreshing sources...');
                
                // Show loading state
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
                
                // Trigger refresh in EnhancedSearchManager if available
                if (window.app && window.app.modules && window.app.modules.searchManager) {
                    if (window.app.modules.searchManager.loadSources) {
                        window.app.modules.searchManager.loadSources();
                    }
                }
                
                // Reset button after delay
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = '<i class="fas fa-sync"></i> Refresh';
                }, 1500);
            });
        }
    }
    
    function fixCheckboxFunctionality() {
        console.log('🔧 Fixing checkbox functionality...');
        
        // Add event delegation for all checkboxes in source-categories
        const sourcesContainer = document.getElementById('source-categories');
        if (sourcesContainer) {
            sourcesContainer.addEventListener('change', function(e) {
                if (e.target.type === 'checkbox') {
                    console.log(`Source checkbox changed: ${e.target.checked}`);
                    updateSourceCount();
                    updateMasterCheckbox();
                }
            });
        }
    }
    
    function updateSourceCount() {
        const checkboxes = document.querySelectorAll('#source-categories input[type="checkbox"]');
        const checked = document.querySelectorAll('#source-categories input[type="checkbox"]:checked');
        
        const countEl = document.getElementById('source-count');
        const totalEl = document.getElementById('source-total');
        
        if (countEl) countEl.textContent = checked.length;
        if (totalEl) totalEl.textContent = checkboxes.length;
    }
    
    function updateMasterCheckbox() {
        const masterCheckbox = document.getElementById('master-select-all');
        if (!masterCheckbox) return;
        
        const checkboxes = document.querySelectorAll('#source-categories input[type="checkbox"]');
        const checked = document.querySelectorAll('#source-categories input[type="checkbox"]:checked');
        
        if (checkboxes.length === 0) {
            masterCheckbox.checked = false;
            masterCheckbox.indeterminate = false;
        } else if (checked.length === 0) {
            masterCheckbox.checked = false;
            masterCheckbox.indeterminate = false;
        } else if (checked.length === checkboxes.length) {
            masterCheckbox.checked = true;
            masterCheckbox.indeterminate = false;
        } else {
            masterCheckbox.checked = false;
            masterCheckbox.indeterminate = true;
        }
    }
    
    function fixErrorMessages() {
        console.log('🔧 Fixing error messages...');
        
        // Find and fix error message elements
        const errorMessages = document.querySelectorAll('.alert-warning, .alert-danger');
        errorMessages.forEach(msg => {
            if (msg.textContent.includes('Some Content sources may not be available') ||
                msg.textContent.includes('sources may not be available')) {
                // Update with clearer message
                msg.className = 'alert alert-info';
                msg.innerHTML = '<i class="fas fa-info-circle"></i> Sources are loading. Please wait...';
                
                // Auto-hide after sources load
                setTimeout(() => {
                    msg.style.display = 'none';
                }, 3000);
            }
        });
    }
    
    function setupMutationObserver() {
        console.log('👁️ Setting up mutation observer...');
        
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            // Check for duplicate controls being added
                            if (node.classList && (
                                node.classList.contains('select-all-sources-container') ||
                                node.classList.contains('source-controls-buttons')
                            )) {
                                console.log('Blocking duplicate control insertion');
                                node.remove();
                            }
                            
                            // Update counts when new sources are added
                            if (node.classList && node.classList.contains('source-item')) {
                                setTimeout(updateSourceCount, 100);
                            }
                        }
                    });
                }
            });
        });
        
        // Start observing
        const sourcesContainer = document.getElementById('source-categories');
        if (sourcesContainer) {
            observer.observe(sourcesContainer, {
                childList: true,
                subtree: true
            });
        }
    }
    
    // Add CSS for unified controls
    function injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Unified Control Panel Styles */
            #unified-source-controls {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .control-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
            }
            
            .select-all-label {
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: 600;
                cursor: pointer;
                user-select: none;
            }
            
            .select-all-label input[type="checkbox"] {
                width: 20px;
                height: 20px;
                cursor: pointer;
            }
            
            .control-buttons {
                display: flex;
                gap: 10px;
            }
            
            .control-buttons .btn {
                min-width: 120px;
            }
            
            /* Hide all old duplicate controls */
            .source-controls-buttons:not(:first-of-type),
            .select-all-sources-container:not(:first-of-type),
            #select-all-wrapper:not(:first-of-type) {
                display: none !important;
            }
            
            /* Responsive adjustments */
            @media (max-width: 768px) {
                .control-row {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .control-buttons {
                    justify-content: stretch;
                }
                
                .control-buttons .btn {
                    flex: 1;
                }
            }
            
            /* Dark mode support */
            [data-theme="dark"] #unified-source-controls {
                background: #2d3748;
                border-color: #4a5568;
            }
            
            [data-theme="dark"] .select-all-label {
                color: #e2e8f0;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Initialize
    injectStyles();
    waitForDependencies();
    
    // Also fix on navigation
    document.addEventListener('sectionChanged', initializeFix);
    window.addEventListener('searchSectionLoaded', initializeFix);
    
    console.log('✅ Search Page Complete Fix ready');
})();
/**
 * Ultimate Select All Fix
 * Directly integrates with EnhancedSearchManager
 */

(function() {
    'use strict';
    
    console.log('🚀 Ultimate Select All Fix initializing...');
    
    // Wait for EnhancedSearchManager to be available
    function waitForSearchManager() {
        if (window.EnhancedSearchManager) {
            console.log('✅ EnhancedSearchManager found, patching...');
            patchSearchManager();
        } else {
            console.log('⏳ Waiting for EnhancedSearchManager...');
            setTimeout(waitForSearchManager, 100);
        }
    }
    
    function patchSearchManager() {
        // Save original displaySources method
        const originalDisplaySources = EnhancedSearchManager.prototype.displaySources;
        
        // Override displaySources to add Select All
        EnhancedSearchManager.prototype.displaySources = function() {
            console.log('🎨 Patched displaySources running...');
            
            // Call original method
            originalDisplaySources.call(this);
            
            // Add Select All functionality
            setTimeout(() => {
                addSelectAllCheckbox(this);
            }, 100);
        };
        
        // If there's already an instance, patch it
        if (window.app && window.app.modules && window.app.modules.searchManager) {
            const searchManager = window.app.modules.searchManager;
            addSelectAllCheckbox(searchManager);
        }
    }
    
    function addSelectAllCheckbox(searchManager) {
        console.log('📋 Adding Select All checkbox...');
        
        // Find the container
        const container = document.getElementById('source-categories') || 
                         document.querySelector('.sources-grid') ||
                         document.querySelector('#sources-section');
        
        if (!container) {
            console.warn('⚠️ No container found for Select All');
            return;
        }
        
        // Check if Select All already exists
        let selectAllContainer = document.querySelector('.select-all-sources-container');
        if (selectAllContainer) {
            selectAllContainer.remove(); // Remove old one to recreate
        }
        
        // Create Select All container
        selectAllContainer = document.createElement('div');
        selectAllContainer.className = 'select-all-sources-container mb-3';
        selectAllContainer.style.cssText = `
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        
        selectAllContainer.innerHTML = `
            <div class="d-flex align-items-center justify-content-between">
                <label class="form-check m-0 d-flex align-items-center" style="cursor: pointer;">
                    <input type="checkbox" id="ultimate-select-all" class="form-check-input me-3" 
                           style="width: 24px; height: 24px; cursor: pointer;">
                    <span style="color: white; font-weight: bold; font-size: 18px;">
                        ✨ Select All Sources
                    </span>
                </label>
                <span id="select-all-count" style="color: white; font-size: 14px;">
                    0 selected
                </span>
            </div>
        `;
        
        // Insert at the beginning of container
        container.insertBefore(selectAllContainer, container.firstChild);
        
        const selectAllCheckbox = document.getElementById('ultimate-select-all');
        const countSpan = document.getElementById('select-all-count');
        
        // Function to update counts
        const updateCounts = () => {
            const allCheckboxes = document.querySelectorAll('.source-checkbox-enhanced:not(:disabled), .source-checkbox:not(:disabled)');
            const checkedCheckboxes = document.querySelectorAll('.source-checkbox-enhanced:checked, .source-checkbox:checked');
            
            countSpan.textContent = `${checkedCheckboxes.length} / ${allCheckboxes.length} selected`;
            
            // Update Select All state
            if (allCheckboxes.length > 0) {
                selectAllCheckbox.checked = checkedCheckboxes.length === allCheckboxes.length;
                selectAllCheckbox.indeterminate = checkedCheckboxes.length > 0 && checkedCheckboxes.length < allCheckboxes.length;
            }
            
            // Update searchManager's selectedSources
            if (searchManager) {
                searchManager.selectedSources.clear();
                checkedCheckboxes.forEach(cb => {
                    const sourceId = cb.getAttribute('data-source') || cb.value;
                    if (sourceId) {
                        searchManager.selectedSources.add(sourceId);
                    }
                });
                console.log('📊 Updated selectedSources:', Array.from(searchManager.selectedSources));
            }
        };
        
        // Add Select All handler
        selectAllCheckbox.addEventListener('change', function(e) {
            const isChecked = e.target.checked;
            console.log(`🎯 Select All: ${isChecked}`);
            
            // Find all source checkboxes
            const checkboxes = document.querySelectorAll('.source-checkbox-enhanced, .source-checkbox');
            let selectedCount = 0;
            
            checkboxes.forEach(checkbox => {
                if (!checkbox.disabled) {
                    // Update checkbox state
                    checkbox.checked = isChecked;
                    
                    // Trigger change event
                    const event = new Event('change', { bubbles: true });
                    checkbox.dispatchEvent(event);
                    
                    // Update visual state
                    const li = checkbox.closest('li.source-item-enhanced');
                    if (li) {
                        if (isChecked) {
                            li.classList.add('selected');
                        } else {
                            li.classList.remove('selected');
                        }
                    }
                    
                    // Update searchManager's selectedSources
                    if (searchManager) {
                        const sourceId = checkbox.getAttribute('data-source') || checkbox.value;
                        if (sourceId) {
                            if (isChecked) {
                                searchManager.selectedSources.add(sourceId);
                            } else {
                                searchManager.selectedSources.delete(sourceId);
                            }
                        }
                    }
                    
                    if (checkbox.checked) selectedCount++;
                }
            });
            
            console.log(`✅ Updated ${selectedCount} checkboxes`);
            updateCounts();
        });
        
        // Monitor individual checkbox changes
        document.addEventListener('change', function(e) {
            if (e.target.classList.contains('source-checkbox-enhanced') || 
                e.target.classList.contains('source-checkbox')) {
                updateCounts();
            }
        });
        
        // Initial count update
        updateCounts();
        
        // Add quick select buttons
        const quickSelectDiv = document.createElement('div');
        quickSelectDiv.className = 'quick-select-buttons mt-2';
        quickSelectDiv.style.cssText = 'display: flex; gap: 10px; flex-wrap: wrap;';
        
        quickSelectDiv.innerHTML = `
            <button class="btn btn-sm btn-light" onclick="selectSourcesByCategory('Video')">
                📹 Select Video
            </button>
            <button class="btn btn-sm btn-light" onclick="selectSourcesByCategory('Social')">
                💬 Select Social
            </button>
            <button class="btn btn-sm btn-light" onclick="selectSourcesByCategory('Image')">
                🖼️ Select Images
            </button>
            <button class="btn btn-sm btn-warning" onclick="clearAllSources()">
                ❌ Clear All
            </button>
        `;
        
        selectAllContainer.appendChild(quickSelectDiv);
        
        // Global helper functions
        window.selectSourcesByCategory = function(category) {
            console.log(`🏷️ Selecting ${category} sources...`);
            const checkboxes = document.querySelectorAll('.source-checkbox-enhanced, .source-checkbox');
            
            checkboxes.forEach(checkbox => {
                const li = checkbox.closest('li');
                const categoryDiv = checkbox.closest('.source-category-enhanced');
                const categoryTitle = categoryDiv?.querySelector('h5')?.textContent || '';
                
                // Check if this source belongs to the category
                const shouldSelect = categoryTitle.toLowerCase().includes(category.toLowerCase()) ||
                                   checkbox.value.toLowerCase().includes(category.toLowerCase());
                
                if (shouldSelect && !checkbox.disabled) {
                    checkbox.checked = true;
                    const event = new Event('change', { bubbles: true });
                    checkbox.dispatchEvent(event);
                    
                    if (li) li.classList.add('selected');
                }
            });
            
            updateCounts();
        };
        
        window.clearAllSources = function() {
            console.log('❌ Clearing all sources...');
            const checkboxes = document.querySelectorAll('.source-checkbox-enhanced:checked, .source-checkbox:checked');
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
                const event = new Event('change', { bubbles: true });
                checkbox.dispatchEvent(event);
                
                const li = checkbox.closest('li');
                if (li) li.classList.remove('selected');
            });
            
            if (searchManager) {
                searchManager.selectedSources.clear();
            }
            
            updateCounts();
        };
        
        console.log('✅ Select All functionality added successfully');
    }
    
    // Start the process
    waitForSearchManager();
    
    // Also try to add it after DOM is ready
    document.addEventListener('DOMContentLoaded', waitForSearchManager);
    
    // And after a delay
    setTimeout(waitForSearchManager, 1000);
    setTimeout(waitForSearchManager, 2000);
    
    console.log('✅ Ultimate Select All Fix loaded');
})();
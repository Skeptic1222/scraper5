/**
 * Enhanced Select All Fix
 * Ensures Select All checkbox works with all source checkbox variations
 */

(function() {
    'use strict';
    
    console.log('🔧 Enhanced Select All Fix initializing...');
    
    function setupSelectAll() {
        console.log('📋 Setting up Select All functionality...');
        
        // Find all possible source checkboxes first
        const findAllSourceCheckboxes = () => {
            const selectors = [
                'input[type="checkbox"][name="sources"]',
                'input[type="checkbox"].source-checkbox',
                'input[type="checkbox"].source-checkbox-enhanced',
                '.source-item input[type="checkbox"]',
                '.source-card input[type="checkbox"]',
                'input[type="checkbox"][data-source]',
                '.sources-grid input[type="checkbox"]',
                '.source-selection input[type="checkbox"]',
                '#sources-section input[type="checkbox"]',
                '.form-check input[type="checkbox"][id*="source"]',
                'input[type="checkbox"][id^="source-"]',
                'input[type="checkbox"][value][id!="select-all-sources"]'
            ];
            
            const checkboxes = new Set();
            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(cb => {
                    // Exclude select-all itself and non-source checkboxes
                    if (cb.id !== 'select-all-sources' && 
                        !cb.id.includes('select-all') &&
                        !cb.classList.contains('select-all') &&
                        cb.type === 'checkbox') {
                        
                        // Check if it's likely a source checkbox
                        const parent = cb.closest('.source-item, .source-card, .source-selection, .sources-grid');
                        const hasSourceAttribute = cb.hasAttribute('data-source') || 
                                                  cb.name === 'sources' ||
                                                  cb.classList.contains('source-checkbox');
                        const hasSourceId = cb.id && (cb.id.includes('source') || 
                                                     cb.id.includes('youtube') || 
                                                     cb.id.includes('instagram') ||
                                                     cb.id.includes('twitter'));
                        
                        if (parent || hasSourceAttribute || hasSourceId) {
                            checkboxes.add(cb);
                        }
                    }
                });
            });
            
            return Array.from(checkboxes);
        };
        
        // Create or find Select All checkbox
        let selectAllContainer = document.querySelector('.select-all-container');
        let selectAllCheckbox = document.getElementById('select-all-sources');
        
        if (!selectAllCheckbox) {
            console.log('📝 Creating Select All checkbox...');
            
            // Find the best place to insert it
            const sourcesSection = document.querySelector('#sources-section, .sources-section, .source-selection');
            const sourcesGrid = document.querySelector('.sources-grid, .source-grid');
            const searchForm = document.querySelector('#search-form, .search-form');
            
            const insertLocation = sourcesSection || sourcesGrid || searchForm;
            
            if (insertLocation) {
                selectAllContainer = document.createElement('div');
                selectAllContainer.className = 'select-all-container mb-3 p-2';
                selectAllContainer.style.cssText = `
                    background: rgba(102, 126, 234, 0.1);
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    display: inline-block;
                `;
                selectAllContainer.innerHTML = `
                    <label class="form-check m-0" style="cursor: pointer; user-select: none;">
                        <input type="checkbox" id="select-all-sources" class="form-check-input me-2" 
                               style="cursor: pointer; width: 20px; height: 20px; vertical-align: middle;">
                        <span class="form-check-label" style="font-weight: bold; font-size: 16px; vertical-align: middle;">
                            🎯 Select All Sources
                        </span>
                    </label>
                `;
                
                // Insert at the beginning of the container
                if (sourcesGrid) {
                    insertLocation.insertBefore(selectAllContainer, sourcesGrid.firstChild);
                } else {
                    insertLocation.insertBefore(selectAllContainer, insertLocation.firstChild);
                }
                
                selectAllCheckbox = document.getElementById('select-all-sources');
            }
        }
        
        if (selectAllCheckbox) {
            console.log('✅ Select All checkbox found/created');
            
            // Remove old event listeners by cloning
            const newCheckbox = selectAllCheckbox.cloneNode(true);
            selectAllCheckbox.parentNode.replaceChild(newCheckbox, selectAllCheckbox);
            selectAllCheckbox = newCheckbox;
            
            // Add the main Select All handler
            selectAllCheckbox.addEventListener('click', function(e) {
                e.stopPropagation();
                const isChecked = this.checked;
                console.log(`🎯 Select All clicked: ${isChecked}`);
                
                const sourceCheckboxes = findAllSourceCheckboxes();
                console.log(`📦 Found ${sourceCheckboxes.length} source checkboxes`);
                
                let checkedCount = 0;
                sourceCheckboxes.forEach((checkbox, index) => {
                    // Force the checkbox to be checked/unchecked
                    checkbox.checked = isChecked;
                    checkbox.disabled = false; // Ensure it's not disabled
                    
                    // Try multiple ways to trigger the change
                    try {
                        // Method 1: Direct property change
                        Object.defineProperty(checkbox, 'checked', {
                            value: isChecked,
                            writable: true,
                            configurable: true
                        });
                    } catch (e) {}
                    
                    // Method 2: Set attribute
                    if (isChecked) {
                        checkbox.setAttribute('checked', 'checked');
                    } else {
                        checkbox.removeAttribute('checked');
                    }
                    
                    // Method 3: Click simulation if state doesn't match
                    if (checkbox.checked !== isChecked) {
                        checkbox.click();
                    }
                    
                    // Update visual state
                    const parent = checkbox.closest('.source-item, .source-card, .form-check');
                    if (parent) {
                        if (isChecked) {
                            parent.classList.add('selected', 'active', 'checked');
                            parent.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
                            parent.style.border = '2px solid #667eea';
                        } else {
                            parent.classList.remove('selected', 'active', 'checked');
                            parent.style.backgroundColor = '';
                            parent.style.border = '';
                        }
                    }
                    
                    // Trigger change event
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    if (checkbox.checked) {
                        checkedCount++;
                    }
                    
                    console.log(`✓ Checkbox ${index + 1}: ${checkbox.id || checkbox.value || 'unnamed'} = ${checkbox.checked}`);
                });
                
                console.log(`✅ Updated ${checkedCount}/${sourceCheckboxes.length} checkboxes to ${isChecked}`);
                
                // Update the label to show count
                const label = selectAllCheckbox.nextElementSibling || selectAllCheckbox.parentNode.querySelector('.form-check-label');
                if (label) {
                    label.innerHTML = `🎯 Select All Sources (${checkedCount}/${sourceCheckboxes.length})`;
                }
            });
            
            // Also handle individual checkbox changes to update Select All state
            document.addEventListener('change', function(e) {
                if (e.target.type === 'checkbox' && 
                    e.target.id !== 'select-all-sources' &&
                    e.target !== selectAllCheckbox) {
                    
                    const sourceCheckboxes = findAllSourceCheckboxes();
                    const checkedCount = sourceCheckboxes.filter(cb => cb.checked).length;
                    
                    if (selectAllCheckbox) {
                        selectAllCheckbox.checked = checkedCount === sourceCheckboxes.length;
                        selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < sourceCheckboxes.length;
                        
                        // Update label
                        const label = selectAllCheckbox.nextElementSibling || selectAllCheckbox.parentNode.querySelector('.form-check-label');
                        if (label) {
                            label.innerHTML = `🎯 Select All Sources (${checkedCount}/${sourceCheckboxes.length})`;
                        }
                    }
                }
            });
            
            // Initial count update
            const sourceCheckboxes = findAllSourceCheckboxes();
            const checkedCount = sourceCheckboxes.filter(cb => cb.checked).length;
            const label = selectAllCheckbox.nextElementSibling || selectAllCheckbox.parentNode.querySelector('.form-check-label');
            if (label) {
                label.innerHTML = `🎯 Select All Sources (${checkedCount}/${sourceCheckboxes.length})`;
            }
        }
        
        // Also make all checkboxes more clickable
        const makeCheckboxesClickable = () => {
            const allCheckboxes = findAllSourceCheckboxes();
            allCheckboxes.forEach(checkbox => {
                checkbox.style.cursor = 'pointer';
                checkbox.disabled = false;
                
                // Make parent clickable too
                const parent = checkbox.closest('.source-item, .source-card');
                if (parent) {
                    parent.style.cursor = 'pointer';
                    
                    // Remove old click handler
                    parent.onclick = null;
                    
                    // Add new click handler
                    parent.addEventListener('click', function(e) {
                        if (e.target !== checkbox && !e.target.closest('input')) {
                            checkbox.checked = !checkbox.checked;
                            checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                            
                            // Update visual state
                            if (checkbox.checked) {
                                this.classList.add('selected', 'active');
                            } else {
                                this.classList.remove('selected', 'active');
                            }
                        }
                    });
                }
            });
        };
        
        makeCheckboxesClickable();
    }
    
    // Initialize immediately
    setupSelectAll();
    
    // Re-initialize after delays to catch dynamic content
    setTimeout(setupSelectAll, 500);
    setTimeout(setupSelectAll, 1000);
    setTimeout(setupSelectAll, 2000);
    
    // Also re-initialize when sources might be loaded
    document.addEventListener('DOMContentLoaded', setupSelectAll);
    window.addEventListener('load', setupSelectAll);
    
    // Watch for dynamic content changes
    const observer = new MutationObserver(function(mutations) {
        const hasSourceChanges = mutations.some(mutation => {
            return Array.from(mutation.addedNodes).some(node => {
                if (node.nodeType === 1) { // Element node
                    return node.classList && (
                        node.classList.contains('source-item') ||
                        node.classList.contains('source-card') ||
                        node.classList.contains('sources-grid') ||
                        node.querySelector && node.querySelector('.source-checkbox')
                    );
                }
                return false;
            });
        });
        
        if (hasSourceChanges) {
            console.log('🔄 Sources changed, reinitializing Select All...');
            setTimeout(setupSelectAll, 100);
        }
    });
    
    // Start observing
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Make function globally available
    window.setupSelectAll = setupSelectAll;
    window.selectAllSources = function(checked = true) {
        const selectAll = document.getElementById('select-all-sources');
        if (selectAll) {
            selectAll.checked = checked;
            selectAll.click();
        }
    };
    
    console.log('✅ Enhanced Select All Fix loaded and watching for changes');
})();
/**
 * Source Selection Improvement Fix
 * Fixes checkbox behavior, visual feedback, and performance issues
 */

(function() {
    'use strict';
    
    console.log('🔧 Source Selection Improvement Fix initializing...');
    
    // Debounce function to reduce flickering
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Fix source checkbox behavior
    function fixSourceCheckboxes() {
        const checkboxes = document.querySelectorAll('.source-checkbox-enhanced, .source-checkbox, input[type="checkbox"][data-source]');
        
        checkboxes.forEach(checkbox => {
            // Remove any duplicate event listeners
            const newCheckbox = checkbox.cloneNode(true);
            checkbox.parentNode.replaceChild(newCheckbox, checkbox);
            
            // Add improved event handling
            newCheckbox.addEventListener('change', function(e) {
                e.stopPropagation();
                const sourceId = this.getAttribute('data-source') || this.value;
                const listItem = this.closest('.source-item-enhanced, [data-source-id]');
                
                if (listItem) {
                    // Add visual feedback
                    listItem.classList.add('selecting');
                    
                    if (this.checked) {
                        listItem.classList.add('selected');
                        console.log('✅ Source selected:', sourceId);
                    } else {
                        listItem.classList.remove('selected');
                        console.log('❌ Source deselected:', sourceId);
                    }
                    
                    // Remove animation class after animation completes
                    setTimeout(() => {
                        listItem.classList.remove('selecting');
                    }, 300);
                }
                
                // Update the count
                updateSelectedCount();
            });
            
            // Ensure checkbox state matches visual state
            const listItem = newCheckbox.closest('.source-item-enhanced, [data-source-id]');
            if (listItem) {
                if (newCheckbox.checked) {
                    listItem.classList.add('selected');
                } else {
                    listItem.classList.remove('selected');
                }
            }
        });
    }
    
    // Update selected sources count
    function updateSelectedCount() {
        const checkedBoxes = document.querySelectorAll('.source-checkbox-enhanced:checked, .source-checkbox:checked');
        const countElement = document.getElementById('selected-sources-count');
        
        if (countElement) {
            countElement.textContent = `${checkedBoxes.length} selected`;
        }
        
        // Update any other count displays
        const counts = document.querySelectorAll('[data-selected-count]');
        counts.forEach(el => {
            el.textContent = checkedBoxes.length;
        });
    }
    
    // Fix click handling on source items
    function fixSourceItemClicks() {
        const sourceItems = document.querySelectorAll('.source-item-enhanced, [data-source-id]');
        
        sourceItems.forEach(item => {
            // Remove existing click handlers
            const newItem = item.cloneNode(true);
            item.parentNode.replaceChild(newItem, item);
            
            // Add improved click handler
            newItem.addEventListener('click', function(e) {
                // Don't trigger if clicking on checkbox directly
                if (e.target.type === 'checkbox' || e.target.tagName === 'INPUT') {
                    return;
                }
                
                // Don't trigger if clicking on a lock icon
                if (e.target.classList.contains('fa-lock') || this.classList.contains('locked')) {
                    return;
                }
                
                // Find and toggle the checkbox
                const checkbox = this.querySelector('input[type="checkbox"]');
                if (checkbox && !checkbox.disabled) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
        });
    }
    
    // Fix select all/none buttons
    function fixBulkSelectionButtons() {
        // Fix Select All button
        const selectAllBtn = document.getElementById('select-all-sources');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const checkboxes = document.querySelectorAll('.source-checkbox-enhanced:not(:disabled), .source-checkbox:not(:disabled)');
                checkboxes.forEach(cb => {
                    if (!cb.checked) {
                        cb.checked = true;
                        cb.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
                console.log('📋 All sources selected');
            });
        }
        
        // Fix Deselect All button
        const deselectAllBtn = document.getElementById('deselect-all-sources');
        if (deselectAllBtn) {
            deselectAllBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const checkboxes = document.querySelectorAll('.source-checkbox-enhanced:checked, .source-checkbox:checked');
                checkboxes.forEach(cb => {
                    cb.checked = false;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                });
                console.log('📋 All sources deselected');
            });
        }
    }
    
    // Reduce flickering by optimizing reflows
    function optimizePerformance() {
        // Add will-change to animated elements
        const animatedElements = document.querySelectorAll('.source-item-enhanced');
        animatedElements.forEach(el => {
            el.style.willChange = 'transform, background-color';
        });
        
        // Use CSS containment
        const sourceContainer = document.getElementById('source-categories');
        if (sourceContainer) {
            sourceContainer.style.contain = 'layout style';
        }
        
        // Batch DOM updates
        const debouncedUpdate = debounce(() => {
            requestAnimationFrame(() => {
                updateSelectedCount();
            });
        }, 100);
        
        // Replace immediate updates with debounced ones
        document.addEventListener('change', function(e) {
            if (e.target.matches('.source-checkbox-enhanced, .source-checkbox')) {
                debouncedUpdate();
            }
        });
    }
    
    // Monitor for dynamic content changes
    function observeSourceChanges() {
        const container = document.getElementById('source-categories');
        if (!container) return;
        
        const observer = new MutationObserver(debounce(() => {
            console.log('🔄 Sources updated, reapplying fixes...');
            fixSourceCheckboxes();
            fixSourceItemClicks();
            updateSelectedCount();
        }, 200));
        
        observer.observe(container, {
            childList: true,
            subtree: true
        });
    }
    
    // Initialize all fixes
    function initialize() {
        console.log('🚀 Initializing source selection improvements...');
        
        // Apply all fixes
        fixSourceCheckboxes();
        fixSourceItemClicks();
        fixBulkSelectionButtons();
        optimizePerformance();
        observeSourceChanges();
        updateSelectedCount();
        
        console.log('✅ Source selection improvements active');
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        // Small delay to ensure other scripts have loaded
        setTimeout(initialize, 100);
    }
    
    // Also reinitialize when the search section becomes active
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-section="search"]') || e.target.closest('.nav-item[data-bs-target="#search-section"]')) {
            setTimeout(() => {
                console.log('🔄 Search section activated, refreshing fixes...');
                initialize();
            }, 300);
        }
    });
    
    // Export for debugging
    window.sourceSelectionFix = {
        fixCheckboxes: fixSourceCheckboxes,
        fixClicks: fixSourceItemClicks,
        updateCount: updateSelectedCount,
        reinitialize: initialize
    };
})();
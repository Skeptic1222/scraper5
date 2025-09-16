/**
 * Button Functionality Fix
 * Fixes Select Recommended, Select All, and other button issues
 */

(function() {
    'use strict';
    
    console.log('🔧 Button Functionality Fix initializing...');
    
    // Fix button event handlers
    function fixButtonHandlers() {
        // Select Recommended Sources button
        const selectRecommendedBtn = document.getElementById('select-recommended-sources');
        if (selectRecommendedBtn) {
            // Remove old handlers
            const newBtn = selectRecommendedBtn.cloneNode(true);
            selectRecommendedBtn.parentNode.replaceChild(newBtn, selectRecommendedBtn);
            
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('📋 Selecting recommended sources...');
                
                // Clear all first
                const allCheckboxes = document.querySelectorAll('.source-checkbox-enhanced, .source-checkbox, input[type="checkbox"][data-source]');
                allCheckboxes.forEach(cb => {
                    cb.checked = false;
                    const listItem = cb.closest('.source-item-enhanced, [data-source-id]');
                    if (listItem) {
                        listItem.classList.remove('selected');
                    }
                });
                
                // Select recommended sources
                const recommendedSources = [
                    'google images', 'google_images', 'googleimages',
                    'bing images', 'bing_images', 'bingimages',
                    'youtube', 'reddit', 'pinterest',
                    'unsplash', 'pexels', 'pixabay'
                ];
                
                let selectedCount = 0;
                recommendedSources.forEach(sourceId => {
                    const checkbox = document.querySelector(
                        `input[data-source="${sourceId}"], ` +
                        `input[value="${sourceId}"], ` +
                        `#source-${sourceId.replace(/\s+/g, '_')}`
                    );
                    
                    if (checkbox && !checkbox.disabled) {
                        checkbox.checked = true;
                        checkbox.dispatchEvent(new Event('change', { bubbles: true }));
                        selectedCount++;
                        
                        // Update visual state
                        const listItem = checkbox.closest('.source-item-enhanced, [data-source-id]');
                        if (listItem) {
                            listItem.classList.add('selected');
                        }
                    }
                });
                
                console.log(`✅ Selected ${selectedCount} recommended sources`);
                updateSelectedCount();
                
                // Show feedback
                showToast(`Selected ${selectedCount} recommended sources`, 'success');
            });
        }
        
        // Select All Sources button
        const selectAllBtn = document.getElementById('select-all-sources');
        if (selectAllBtn) {
            // Remove old handlers
            const newBtn = selectAllBtn.cloneNode(true);
            selectAllBtn.parentNode.replaceChild(newBtn, selectAllBtn);
            
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('📋 Selecting all sources...');
                
                const checkboxes = document.querySelectorAll(
                    '.source-checkbox-enhanced:not(:disabled), ' +
                    '.source-checkbox:not(:disabled), ' +
                    'input[type="checkbox"][data-source]:not(:disabled)'
                );
                
                let selectedCount = 0;
                checkboxes.forEach(cb => {
                    if (!cb.checked) {
                        cb.checked = true;
                        cb.dispatchEvent(new Event('change', { bubbles: true }));
                        selectedCount++;
                        
                        // Update visual state
                        const listItem = cb.closest('.source-item-enhanced, [data-source-id]');
                        if (listItem) {
                            listItem.classList.add('selected');
                        }
                    }
                });
                
                console.log(`✅ Selected ${selectedCount} sources`);
                updateSelectedCount();
                
                // Show feedback
                showToast(`Selected all ${checkboxes.length} available sources`, 'success');
            });
        }
        
        // Deselect All Sources button
        const deselectAllBtn = document.getElementById('deselect-all-sources');
        if (deselectAllBtn) {
            // Remove old handlers
            const newBtn = deselectAllBtn.cloneNode(true);
            deselectAllBtn.parentNode.replaceChild(newBtn, deselectAllBtn);
            
            newBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('📋 Deselecting all sources...');
                
                const checkboxes = document.querySelectorAll(
                    '.source-checkbox-enhanced:checked, ' +
                    '.source-checkbox:checked, ' +
                    'input[type="checkbox"][data-source]:checked'
                );
                
                checkboxes.forEach(cb => {
                    cb.checked = false;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // Update visual state
                    const listItem = cb.closest('.source-item-enhanced, [data-source-id]');
                    if (listItem) {
                        listItem.classList.remove('selected');
                    }
                });
                
                console.log('✅ Deselected all sources');
                updateSelectedCount();
                
                // Show feedback
                showToast('All sources deselected', 'info');
            });
        }
    }
    
    // Update selected count display
    function updateSelectedCount() {
        const checkedBoxes = document.querySelectorAll(
            '.source-checkbox-enhanced:checked, ' +
            '.source-checkbox:checked, ' +
            'input[type="checkbox"][data-source]:checked'
        );
        
        const countElement = document.getElementById('selected-sources-count');
        if (countElement) {
            countElement.textContent = `${checkedBoxes.length} selected`;
        }
        
        // Update any other count displays
        const countBadges = document.querySelectorAll('[data-selected-count]');
        countBadges.forEach(badge => {
            badge.textContent = checkedBoxes.length;
        });
        
        // Update the main select all checkbox if exists
        const selectAllCheckbox = document.getElementById('select-all-sources-checkbox');
        if (selectAllCheckbox) {
            const totalCheckboxes = document.querySelectorAll(
                '.source-checkbox-enhanced, .source-checkbox, input[type="checkbox"][data-source]'
            ).length;
            
            selectAllCheckbox.checked = checkedBoxes.length === totalCheckboxes && totalCheckboxes > 0;
            selectAllCheckbox.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < totalCheckboxes;
        }
    }
    
    // Show toast notification
    function showToast(message, type = 'info') {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.custom-toast');
        existingToasts.forEach(toast => toast.remove());
        
        const toast = document.createElement('div');
        toast.className = `custom-toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 70px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease;
            font-size: 14px;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    // Add CSS for toast animations
    function addToastStyles() {
        if (!document.getElementById('toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Initialize
    function initialize() {
        console.log('🚀 Initializing button functionality fixes...');
        
        addToastStyles();
        fixButtonHandlers();
        updateSelectedCount();
        
        // Monitor for dynamic content changes
        const observer = new MutationObserver(() => {
            fixButtonHandlers();
            updateSelectedCount();
        });
        
        const sourceContainer = document.getElementById('source-categories');
        if (sourceContainer) {
            observer.observe(sourceContainer, {
                childList: true,
                subtree: true
            });
        }
        
        console.log('✅ Button functionality fixes active');
    }
    
    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        setTimeout(initialize, 100);
    }
    
    // Re-initialize when search section becomes active
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-section="search"]') || 
            e.target.closest('.nav-item[href="#search"]')) {
            setTimeout(initialize, 300);
        }
    });
    
    // Export for debugging
    window.buttonFix = {
        fixHandlers: fixButtonHandlers,
        updateCount: updateSelectedCount,
        reinitialize: initialize
    };
})();
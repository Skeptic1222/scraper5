/**
 * Sources Selection Fix
 * Fixes the sources checkbox selection issues
 */

document.addEventListener('DOMContentLoaded', function() {
    // Fix source checkbox selection
    function fixSourceCheckboxes() {
        // Find all source checkboxes
        const sourceCheckboxes = document.querySelectorAll('.source-checkbox, .source-checkbox-enhanced, input[type="checkbox"][name="sources"], input[type="checkbox"][data-source]');
        
        sourceCheckboxes.forEach(checkbox => {
            // Remove any disabled state
            checkbox.disabled = false;
            checkbox.removeAttribute('disabled');
            
            // Ensure proper styling
            checkbox.style.cursor = 'pointer';
            checkbox.style.pointerEvents = 'auto';
            
            // Fix parent container if it exists
            const parent = checkbox.closest('.source-item, .source-card');
            if (parent) {
                parent.style.pointerEvents = 'auto';
                parent.style.opacity = '1';
            }
            
            // Add click handler if missing
            if (!checkbox.hasAttribute('data-fixed')) {
                checkbox.setAttribute('data-fixed', 'true');
                
                // Remove existing event listeners
                const newCheckbox = checkbox.cloneNode(true);
                checkbox.parentNode.replaceChild(newCheckbox, checkbox);
                
                // Add new clean event listener
                newCheckbox.addEventListener('click', function(e) {
                    e.stopPropagation();
                    
                    // Toggle checked state
                    this.checked = !this.checked;
                    
                    // Update UI
                    updateSourceSelection();
                    
                    // Trigger change event
                    const event = new Event('change', { bubbles: true });
                    this.dispatchEvent(event);
                });
                
                // Also handle label clicks
                const label = document.querySelector(`label[for="${newCheckbox.id}"]`);
                if (label) {
                    label.style.cursor = 'pointer';
                    label.addEventListener('click', function(e) {
                        e.preventDefault();
                        newCheckbox.click();
                    });
                }
            }
        });
    }
    
    // Update source selection count
    function updateSourceSelection() {
        const checkedSources = document.querySelectorAll('.source-checkbox:checked, .source-checkbox-enhanced:checked, input[type="checkbox"][name="sources"]:checked');
        const countElement = document.getElementById('selected-sources-count');
        
        if (countElement) {
            countElement.textContent = `${checkedSources.length} selected`;
            
            // Update badge style based on count
            if (checkedSources.length > 0) {
                countElement.classList.remove('bg-secondary');
                countElement.classList.add('bg-primary');
            } else {
                countElement.classList.remove('bg-primary');
                countElement.classList.add('bg-secondary');
            }
        }
    }
    
    // Fix source control buttons
    function setupSourceControlButtons() {
        // Select All button
        const selectAllBtn = document.getElementById('select-all-sources');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const checkboxes = document.querySelectorAll('.source-checkbox, .source-checkbox-enhanced, input[type="checkbox"][name="sources"]');
                checkboxes.forEach(cb => {
                    cb.checked = true;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                });
                updateSourceSelection();
            });
        }
        
        // Deselect All button
        const deselectAllBtn = document.getElementById('deselect-all-sources');
        if (deselectAllBtn) {
            deselectAllBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const checkboxes = document.querySelectorAll('.source-checkbox, .source-checkbox-enhanced, input[type="checkbox"][name="sources"]');
                checkboxes.forEach(cb => {
                    cb.checked = false;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                });
                updateSourceSelection();
            });
        }
        
        // Select Recommended button
        const selectRecommendedBtn = document.getElementById('select-recommended-sources');
        if (selectRecommendedBtn) {
            selectRecommendedBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const recommendedSources = ['youtube', 'instagram', 'twitter', 'tiktok', 'reddit'];
                const checkboxes = document.querySelectorAll('.source-checkbox, .source-checkbox-enhanced, input[type="checkbox"][name="sources"]');
                
                checkboxes.forEach(cb => {
                    const sourceName = cb.value || cb.dataset.source || cb.id;
                    cb.checked = recommendedSources.some(src => sourceName.toLowerCase().includes(src));
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                });
                updateSourceSelection();
            });
        }
        
        // Select Free Sources button
        const selectFreeBtn = document.getElementById('select-free-sources');
        if (selectFreeBtn) {
            selectFreeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const checkboxes = document.querySelectorAll('.source-checkbox, .source-checkbox-enhanced, input[type="checkbox"][name="sources"]');
                
                checkboxes.forEach(cb => {
                    const parent = cb.closest('.source-item, .source-card');
                    const isPremium = parent && (parent.classList.contains('premium') || parent.querySelector('.badge-premium, .fa-crown'));
                    cb.checked = !isPremium;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                });
                updateSourceSelection();
            });
        }
        
        // Select Premium Sources button
        const selectPremiumBtn = document.getElementById('select-premium-sources');
        if (selectPremiumBtn) {
            selectPremiumBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const checkboxes = document.querySelectorAll('.source-checkbox, .source-checkbox-enhanced, input[type="checkbox"][name="sources"]');
                
                checkboxes.forEach(cb => {
                    const parent = cb.closest('.source-item, .source-card');
                    const isPremium = parent && (parent.classList.contains('premium') || parent.querySelector('.badge-premium, .fa-crown'));
                    cb.checked = isPremium;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                });
                updateSourceSelection();
            });
        }
    }
    
    // Initialize fixes
    fixSourceCheckboxes();
    setupSourceControlButtons();
    updateSourceSelection();
    
    // Re-apply fixes when DOM changes (for dynamically loaded content)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                fixSourceCheckboxes();
                updateSourceSelection();
            }
        });
    });
    
    // Observe source containers
    const sourceContainers = document.querySelectorAll('#source-categories, #nsfw-sources-container, .sources-grid');
    sourceContainers.forEach(container => {
        if (container) {
            observer.observe(container, { childList: true, subtree: true });
        }
    });
    
    // Also fix on window load
    window.addEventListener('load', function() {
        setTimeout(fixSourceCheckboxes, 100);
        setTimeout(updateSourceSelection, 150);
    });
});

// Export for use in other modules
window.fixSourceSelection = function() {
    const event = new Event('DOMContentLoaded');
    document.dispatchEvent(event);
};
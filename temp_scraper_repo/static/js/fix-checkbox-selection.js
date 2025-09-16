/**
 * Fix Checkbox Selection
 * Handles checkbox selection for bulk operations in asset management
 */

(function() {
    'use strict';

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initCheckboxHandlers();
    });

    function initCheckboxHandlers() {
        // Handle select all checkbox
        const selectAllCheckbox = document.getElementById('select-all-assets');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', handleSelectAll);
        }

        // Handle individual asset checkboxes
        const assetCheckboxes = document.querySelectorAll('.asset-checkbox');
        assetCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', handleIndividualSelect);
        });

        // Initialize bulk action buttons
        initBulkActions();
    }

    function handleSelectAll(event) {
        const isChecked = event.target.checked;
        const assetCheckboxes = document.querySelectorAll('.asset-checkbox');
        
        assetCheckboxes.forEach(checkbox => {
            checkbox.checked = isChecked;
            // Trigger change event for each checkbox
            const changeEvent = new Event('change', { bubbles: true });
            checkbox.dispatchEvent(changeEvent);
        });

        updateBulkActionsVisibility();
    }

    function handleIndividualSelect() {
        const assetCheckboxes = document.querySelectorAll('.asset-checkbox');
        const selectAllCheckbox = document.getElementById('select-all-assets');
        
        if (selectAllCheckbox) {
            const checkedCount = document.querySelectorAll('.asset-checkbox:checked').length;
            const totalCount = assetCheckboxes.length;
            
            // Update select all checkbox state
            if (checkedCount === 0) {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = false;
            } else if (checkedCount === totalCount) {
                selectAllCheckbox.checked = true;
                selectAllCheckbox.indeterminate = false;
            } else {
                selectAllCheckbox.checked = false;
                selectAllCheckbox.indeterminate = true;
            }
        }

        updateBulkActionsVisibility();
    }

    function updateBulkActionsVisibility() {
        const checkedCount = document.querySelectorAll('.asset-checkbox:checked').length;
        const bulkActionsContainer = document.getElementById('bulk-actions');
        
        if (bulkActionsContainer) {
            if (checkedCount > 0) {
                bulkActionsContainer.style.display = 'block';
                // Update selected count display
                const countDisplay = bulkActionsContainer.querySelector('.selected-count');
                if (countDisplay) {
                    countDisplay.textContent = `${checkedCount} selected`;
                }
            } else {
                bulkActionsContainer.style.display = 'none';
            }
        }
    }

    function initBulkActions() {
        // Delete selected button
        const deleteSelectedBtn = document.getElementById('delete-selected-btn');
        if (deleteSelectedBtn) {
            deleteSelectedBtn.addEventListener('click', handleBulkDelete);
        }

        // Download selected button
        const downloadSelectedBtn = document.getElementById('download-selected-btn');
        if (downloadSelectedBtn) {
            downloadSelectedBtn.addEventListener('click', handleBulkDownload);
        }
    }

    function handleBulkDelete() {
        const selectedIds = getSelectedAssetIds();
        if (selectedIds.length === 0) return;

        if (confirm(`Are you sure you want to delete ${selectedIds.length} selected assets?`)) {
            // Trigger delete event for asset manager to handle
            const event = new CustomEvent('bulkDelete', { 
                detail: { assetIds: selectedIds }
            });
            document.dispatchEvent(event);
        }
    }

    function handleBulkDownload() {
        const selectedIds = getSelectedAssetIds();
        if (selectedIds.length === 0) return;

        // Trigger download event for asset manager to handle
        const event = new CustomEvent('bulkDownload', { 
            detail: { assetIds: selectedIds }
        });
        document.dispatchEvent(event);
    }

    function getSelectedAssetIds() {
        const checkedBoxes = document.querySelectorAll('.asset-checkbox:checked');
        return Array.from(checkedBoxes).map(checkbox => checkbox.dataset.assetId).filter(id => id);
    }

    // Re-initialize after dynamic content loads
    document.addEventListener('assetsLoaded', function() {
        initCheckboxHandlers();
    });

    // Export functions for external use
    window.CheckboxSelection = {
        init: initCheckboxHandlers,
        getSelectedIds: getSelectedAssetIds,
        clearSelection: function() {
            const selectAllCheckbox = document.getElementById('select-all-assets');
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = false;
                handleSelectAll({ target: selectAllCheckbox });
            }
        }
    };
})();
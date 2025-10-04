/**
 * Asset Selection and Bulk Delete Module
 * Handles checkbox selection and bulk operations for assets
 */

(function() {
    'use strict';

    // Selection tracking
    let selectedAssets = new Set();

    /**
     * Update UI based on current selection
     */
    function updateSelectionUI() {
        const deleteBtn = document.getElementById('delete-selected-btn');
        const countSpan = document.getElementById('selected-count');
        const statusSpan = document.getElementById('selection-status');
        const selectAllBtn = document.getElementById('select-all-btn');
        const deselectAllBtn = document.getElementById('deselect-all-btn');

        // Update delete button - always visible, but disabled when nothing selected
        if (deleteBtn) {
            deleteBtn.disabled = selectedAssets.size === 0;
            if (countSpan) {
                countSpan.textContent = selectedAssets.size;
                // Update badge color based on selection
                countSpan.className = selectedAssets.size > 0 ?
                    'badge bg-warning text-dark ms-1' :
                    'badge bg-light text-dark ms-1';
            }
        }

        // Update selection status
        if (statusSpan) {
            statusSpan.textContent = selectedAssets.size > 0 ? `${selectedAssets.size} selected` : '';
        }

        // Update select/deselect buttons
        const checkboxes = document.querySelectorAll('.asset-checkbox');
        const hasAssets = checkboxes.length > 0;
        const allChecked = selectedAssets.size === checkboxes.length && hasAssets;

        if (selectAllBtn) {
            selectAllBtn.disabled = !hasAssets || allChecked;
        }

        if (deselectAllBtn) {
            deselectAllBtn.disabled = !hasAssets || selectedAssets.size === 0;
        }
    }

    /**
     * Handle checkbox state changes
     */
    function handleCheckboxChange(event) {
        if (!event.target.classList.contains('asset-checkbox')) {
            return;
        }

        const assetId = event.target.dataset.assetId;
        if (!assetId) {
            console.warn('Checkbox missing asset ID');
            return;
        }

        // Get the asset card for visual feedback
        const assetCard = event.target.closest('.asset-card');

        if (event.target.checked) {
            selectedAssets.add(assetId);
            console.log(`Selected asset ${assetId}`);

            // Add visual highlight
            if (assetCard) {
                assetCard.style.transition = 'box-shadow 0.3s ease, border-color 0.3s ease';
                assetCard.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.5)';
                assetCard.style.borderColor = '#3b82f6';
            }
        } else {
            selectedAssets.delete(assetId);
            console.log(`Deselected asset ${assetId}`);

            // Remove visual highlight
            if (assetCard) {
                assetCard.style.transition = 'box-shadow 0.3s ease, border-color 0.3s ease';
                assetCard.style.boxShadow = '';
                assetCard.style.borderColor = '';
            }
        }

        updateSelectionUI();
    }

    /**
     * Select all assets
     */
    function selectAll() {
        const checkboxes = document.querySelectorAll('.asset-checkbox');
        if (checkboxes.length === 0) {
            console.warn('No asset checkboxes found');
            return;
        }

        const selectAllBtn = document.getElementById('select-all-btn');

        // Add visual feedback - button press effect
        if (selectAllBtn) {
            selectAllBtn.style.transform = 'scale(0.95)';
            selectAllBtn.classList.add('btn-success');
            selectAllBtn.classList.remove('btn-primary');
            setTimeout(() => {
                selectAllBtn.style.transform = 'scale(1)';
            }, 150);
        }

        checkboxes.forEach(cb => {
            cb.checked = true;
            const assetId = cb.dataset.assetId;
            if (assetId) {
                selectedAssets.add(assetId);
            }

            // Add visual highlight to asset cards
            const assetCard = cb.closest('.asset-card');
            if (assetCard) {
                assetCard.style.transition = 'box-shadow 0.3s ease, border-color 0.3s ease';
                assetCard.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.5)';
                assetCard.style.borderColor = '#3b82f6';
            }
        });

        console.log(`Selected all ${checkboxes.length} assets`);

        // Set global flag for bulk download to bypass limits
        window.selectAllWasUsed = true;

        updateSelectionUI();
    }

    /**
     * Deselect all assets
     */
    function deselectAll() {
        const checkboxes = document.querySelectorAll('.asset-checkbox');
        const deselectAllBtn = document.getElementById('deselect-all-btn');

        // Add visual feedback - button press effect
        if (deselectAllBtn) {
            deselectAllBtn.style.transform = 'scale(0.95)';
            deselectAllBtn.classList.add('btn-secondary');
            deselectAllBtn.classList.remove('btn-outline-secondary');
            setTimeout(() => {
                deselectAllBtn.style.transform = 'scale(1)';
                deselectAllBtn.classList.remove('btn-secondary');
                deselectAllBtn.classList.add('btn-outline-secondary');
            }, 150);
        }

        checkboxes.forEach(cb => {
            cb.checked = false;
            const assetId = cb.dataset.assetId;
            if (assetId) {
                selectedAssets.delete(assetId);
            }

            // Remove visual highlight from asset cards
            const assetCard = cb.closest('.asset-card');
            if (assetCard) {
                assetCard.style.transition = 'box-shadow 0.3s ease, border-color 0.3s ease';
                assetCard.style.boxShadow = '';
                assetCard.style.borderColor = '';
            }
        });

        selectedAssets.clear(); // Ensure set is completely cleared
        console.log('Deselected all assets');

        // Reset global flag for bulk download
        window.selectAllWasUsed = false;

        // Reset select all button appearance
        const selectAllBtn = document.getElementById('select-all-btn');
        if (selectAllBtn) {
            selectAllBtn.classList.remove('btn-success');
            selectAllBtn.classList.add('btn-primary');
        }

        updateSelectionUI();
    }

    /**
     * Delete selected assets with confirmation
     */
    async function deleteSelectedAssets() {
        if (selectedAssets.size === 0) {
            alert('⚠️ No assets selected. Please select assets to delete.');
            return;
        }

        const assetCount = selectedAssets.size;
        const confirmed = confirm(
            `⚠️ Are you sure you want to delete ${assetCount} asset(s)?\n\n` +
            `This will permanently delete the files and cannot be undone.`
        );

        if (!confirmed) {
            console.log('Bulk delete cancelled by user');
            return;
        }

        try {
            // Show loading state
            const deleteBtn = document.getElementById('delete-selected-btn');
            if (deleteBtn) {
                deleteBtn.disabled = true;
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
            }

            // CRITICAL: Use /scraper prefix (no ports!)
            const apiUrl = `${window.APP_BASE || '/scraper'}/api/assets/bulk-delete`;
            console.log(`Deleting ${assetCount} assets via ${apiUrl}`);

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    asset_ids: Array.from(selectedAssets)
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                const deletedCount = result.deleted_count || result.deleted || selectedAssets.size;

                console.log(`✅ Successfully deleted ${deletedCount} assets`);

                // Remove deleted assets from DOM (try multiple selectors for compatibility)
                selectedAssets.forEach(id => {
                    const assetCard = document.querySelector(`.asset-card[data-asset-id="${id}"]`) ||
                                    document.querySelector(`.asset-item[data-asset-id="${id}"]`) ||
                                    document.querySelector(`[data-asset-id="${id}"]`);
                    if (assetCard) {
                        assetCard.style.transition = 'opacity 0.3s ease';
                        assetCard.style.opacity = '0';
                        setTimeout(() => assetCard.remove(), 300);
                    }
                });

                // Clear selection
                selectedAssets.clear();
                updateSelectionUI();

                alert(`✅ Successfully deleted ${deletedCount} asset(s)`);

                // Reload assets if function is available
                if (typeof window.loadAssets === 'function') {
                    setTimeout(() => window.loadAssets(), 500);
                } else if (typeof window.WorkingAssetSystem !== 'undefined') {
                    setTimeout(() => window.WorkingAssetSystem.loadAssets(), 500);
                }

                // CRITICAL FIX: Refresh dashboard to update asset count
                refreshDashboardAfterDeletion();
            } else {
                throw new Error(result.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error deleting assets:', error);
            alert(`❌ Error deleting assets: ${error.message}`);
        } finally {
            // Restore delete button
            const deleteBtn = document.getElementById('delete-selected-btn');
            if (deleteBtn) {
                deleteBtn.disabled = false;
                deleteBtn.innerHTML = `<i class="fas fa-trash"></i> Delete Selected (<span id="selected-count">${selectedAssets.size}</span>)`;
            }
        }
    }

    /**
     * Delete ALL assets with double confirmation
     */
    async function deleteAllAssets() {
        // First confirmation
        const firstConfirm = confirm(
            `⚠️ WARNING: DELETE ALL ASSETS\n\n` +
            `This will permanently delete ALL downloaded assets from the system.\n\n` +
            `This action CANNOT be undone!\n\n` +
            `Are you sure you want to continue?`
        );

        if (!firstConfirm) {
            console.log('Delete all assets cancelled (first confirmation)');
            return;
        }

        // Second confirmation
        const secondConfirm = confirm(
            `🚨 FINAL WARNING 🚨\n\n` +
            `You are about to delete ALL assets permanently.\n\n` +
            `Click OK to DELETE EVERYTHING or Cancel to abort.`
        );

        if (!secondConfirm) {
            console.log('Delete all assets cancelled (second confirmation)');
            return;
        }

        try {
            // Show loading state
            const deleteAllBtn = document.getElementById('delete-all-assets-btn');
            if (deleteAllBtn) {
                deleteAllBtn.disabled = true;
                deleteAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting All Assets...';
            }

            // Get all asset IDs
            const checkboxes = document.querySelectorAll('.asset-checkbox');
            const allAssetIds = Array.from(checkboxes).map(cb => cb.dataset.assetId).filter(id => id);

            if (allAssetIds.length === 0) {
                alert('ℹ️ No assets found to delete.');
                return;
            }

            // CRITICAL: Use /scraper prefix (no ports!)
            const apiUrl = `${window.APP_BASE || '/scraper'}/api/assets/bulk-delete`;
            console.log(`Deleting ALL ${allAssetIds.length} assets via ${apiUrl}`);

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    asset_ids: allAssetIds
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (result.success) {
                const deletedCount = result.deleted_count || result.deleted || allAssetIds.length;
                console.log(`✅ Successfully deleted ALL ${deletedCount} assets`);

                // Clear selection
                selectedAssets.clear();
                updateSelectionUI();

                alert(`✅ Successfully deleted ALL ${deletedCount} asset(s)!\n\nYour library is now empty.`);

                // Reload assets
                if (typeof window.loadAssets === 'function') {
                    setTimeout(() => window.loadAssets(), 500);
                } else if (typeof window.WorkingAssetSystem !== 'undefined') {
                    setTimeout(() => window.WorkingAssetSystem.loadAssets(), 500);
                } else if (window.assetLibrary && window.assetLibrary.loadAssets) {
                    setTimeout(() => window.assetLibrary.loadAssets(), 500);
                }

                // CRITICAL FIX: Refresh dashboard to update asset count
                refreshDashboardAfterDeletion();
            } else {
                throw new Error(result.error || 'Unknown error occurred');
            }
        } catch (error) {
            console.error('Error deleting all assets:', error);
            alert(`❌ Error deleting assets: ${error.message}`);
        } finally {
            // Restore button
            const deleteAllBtn = document.getElementById('delete-all-assets-btn');
            if (deleteAllBtn) {
                deleteAllBtn.disabled = false;
                deleteAllBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Delete All Assets';
            }
        }
    }

    /**
     * Refresh dashboard asset count after deletion
     * This fixes the stale count issue reported by user
     */
    function refreshDashboardAfterDeletion() {
        console.log('🔄 Refreshing dashboard after deletion...');

        // Method 1: Use global dashboard refresh if available
        if (window.downloadDashboard && window.downloadDashboard.refresh) {
            console.log('✅ Using downloadDashboard.refresh()');
            window.downloadDashboard.refresh();
            return;
        }

        // Method 2: Fetch and update dashboard stats manually
        const apiUrl = `${window.APP_BASE || '/scraper'}/api/dashboard-stats`;

        fetch(apiUrl, {
            credentials: 'include'
        })
            .then(response => response.json())
            .then(data => {
                if (data && data.stats) {
                    // Update total assets count in dashboard
                    const totalAssetsElement = document.getElementById('dashboard-total-assets');
                    if (totalAssetsElement) {
                        totalAssetsElement.textContent = data.stats.total_assets;
                        console.log(`✅ Dashboard updated: ${data.stats.total_assets} assets`);
                    }

                    // Also update active downloads and queue if elements exist
                    const activeDownloadsElement = document.getElementById('dashboard-active-downloads');
                    if (activeDownloadsElement && data.stats.pending_jobs !== undefined) {
                        activeDownloadsElement.textContent = data.stats.pending_jobs;
                    }

                    const queueLengthElement = document.getElementById('dashboard-queue-length');
                    if (queueLengthElement && data.stats.pending_jobs !== undefined) {
                        queueLengthElement.textContent = data.stats.pending_jobs;
                    }
                } else {
                    console.warn('⚠️ No stats data in dashboard response');
                }
            })
            .catch(error => {
                console.error('❌ Error refreshing dashboard:', error);
            });
    }

    /**
     * Render an asset card with selection checkbox
     */
    function createAssetCard(asset) {
        const assetDiv = document.createElement('div');
        assetDiv.className = 'asset-item';
        assetDiv.dataset.assetId = asset.id;
        assetDiv.dataset.fileType = asset.file_type || asset.type || 'unknown';

        // Checkbox (top-right)
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'asset-checkbox';
        checkbox.dataset.assetId = asset.id;

        // File type badge (top-left)
        const badge = document.createElement('div');
        badge.className = `file-type-badge ${asset.file_type || asset.type || 'unknown'}`;
        const icon = asset.file_type === 'video' || asset.type === 'video' ? 'video' : 'image';
        badge.innerHTML = `
            <i class="fas fa-${icon}"></i>
            ${(asset.file_type || asset.type || 'unknown').toUpperCase()}
        `;

        // Thumbnail
        const img = document.createElement('img');
        const thumbnailUrl = `${window.APP_BASE || '/scraper'}/api/media/${asset.id}/thumbnail`;
        img.src = thumbnailUrl;
        img.alt = asset.filename || 'Asset';
        img.onerror = function() {
            this.src = `${window.APP_BASE || '/scraper'}/static/img/placeholder.png`;
        };

        // File info
        const fileInfo = document.createElement('div');
        fileInfo.className = 'file-info';

        const filename = asset.filename || asset.name || 'unknown';
        const extension = filename.includes('.') ? filename.split('.').pop() : 'file';

        fileInfo.innerHTML = `<span class="file-ext">.${extension}</span>`;

        // Assemble card
        assetDiv.appendChild(checkbox);
        assetDiv.appendChild(badge);
        assetDiv.appendChild(img);
        assetDiv.appendChild(fileInfo);

        return assetDiv;
    }

    /**
     * Initialize the module
     */
    function init() {
        console.log('🎯 Asset Selection Module Initialized');

        // Set up event delegation for checkboxes
        document.addEventListener('change', handleCheckboxChange);

        // Set up select all button
        const selectAllBtn = document.getElementById('select-all-btn');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', selectAll);
        }

        // Set up deselect all button
        const deselectAllBtn = document.getElementById('deselect-all-btn');
        if (deselectAllBtn) {
            deselectAllBtn.addEventListener('click', deselectAll);
        }

        // Set up delete selected button
        const deleteBtn = document.getElementById('delete-selected-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', deleteSelectedAssets);
        }

        // Set up delete all assets button (in Settings)
        const deleteAllBtn = document.getElementById('delete-all-assets-btn');
        if (deleteAllBtn) {
            deleteAllBtn.addEventListener('click', deleteAllAssets);
        }

        // Initial UI update
        updateSelectionUI();

        // Set up observer to update UI when assets are loaded/rendered
        const assetsGrid = document.getElementById('assets-grid') || document.getElementById('asset-grid');
        if (assetsGrid) {
            const observer = new MutationObserver(() => {
                // Update UI whenever the assets grid changes
                updateSelectionUI();
            });
            observer.observe(assetsGrid, { childList: true, subtree: true });
        }

        // Also update UI periodically for robustness
        setInterval(updateSelectionUI, 1000);

        // Expose functions globally for integration
        window.AssetSelection = {
            createAssetCard,
            updateSelectionUI,
            clearSelection: () => {
                selectedAssets.clear();
                document.querySelectorAll('.asset-checkbox').forEach(cb => cb.checked = false);
                updateSelectionUI();
            },
            getSelectedCount: () => selectedAssets.size,
            getSelectedIds: () => Array.from(selectedAssets)
        };

        console.log('✅ Asset Selection ready');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

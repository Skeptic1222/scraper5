/**
 * Enhanced Search UI Manager
 * Handles source display and search functionality with improved UI
 */
class EnhancedSearchUI {
    constructor() {
        this.sources = {};
        this.selectedSources = new Set();
        this.init();
    }

    async init() {
        await this.loadSources();
        this.setupEventListeners();
        this.setupSafeSearchToggle();
    }

    async loadSources() {
        try {
            const togglePrimary = document.getElementById('safe-search-toggle');
            const toggleAlt = document.getElementById('safe-search');
            const safeSearch = (togglePrimary && typeof togglePrimary.checked === 'boolean')
                ? togglePrimary.checked
                : (toggleAlt && typeof toggleAlt.checked === 'boolean' ? toggleAlt.checked : false);
            const response = await fetch((window.APP_BASE || '/scraper') + `/api/sources?safe_search=${safeSearch}`);
            const data = await response.json();
            
            if (data.success !== false && data.sources) {
                // Transform the flat array into categorized structure
                this.sources = this.transformSourceData(data.sources);
                this.displaySources(data.capabilities || {});
            }
        } catch (error) {
            console.error('Failed to load sources:', error);
            this.showError('Failed to load content sources');
        }
    }

    transformSourceData(sourcesArray) {
        console.log('[SearchUI] transformSourceData called with:', sourcesArray);
        const categorized = {};

        // If sources is an array of category objects
        if (Array.isArray(sourcesArray)) {
            console.log('[SearchUI] Processing', sourcesArray.length, 'category objects');
            sourcesArray.forEach(categoryObj => {
                if (categoryObj.category && categoryObj.sources) {
                    console.log('[SearchUI] Category:', categoryObj.category, 'has', categoryObj.sources.length, 'sources');

                    // Skip "All" category as it's redundant
                    if (categoryObj.category === 'All') {
                        console.log('[SearchUI] Skipping "All" category');
                        return;
                    }

                    // Use the category name from the API response directly
                    const categoryName = categoryObj.category;
                    if (!categorized[categoryName]) {
                        categorized[categoryName] = [];
                    }

                    // Add all sources from this category
                    categoryObj.sources.forEach(source => {
                        categorized[categoryName].push({
                            id: source.id,
                            name: source.name,
                            enabled: source.enabled !== false, // Enable premium for now
                            premium: !!source.subscription_required,
                            nsfw: source.nsfw || false,
                            implemented: !!source.implemented
                        });
                    });
                }
            });
        }

        console.log('[SearchUI] Final categorized data:', categorized);
        console.log('[SearchUI] Total categories:', Object.keys(categorized).length);
        console.log('[SearchUI] Total sources:', Object.values(categorized).reduce((sum, arr) => sum + arr.length, 0));
        return categorized;
    }

    getCategoryDisplayName(category) {
        const categoryMap = {
            'search': 'Search Engines',
            'photos': 'Stock Photos',
            'social': 'Social Media',
            'video': 'Video Platforms',
            'art': 'Art Platforms',
            'news': 'News Media',
            'shopping': 'E-Commerce',
            'entertainment': 'Entertainment',
            'academic': 'Academic',
            'tech': 'Tech Forums',
            'adult': 'Adult Content'
        };
        return categoryMap[category] || category;
    }

    displaySources(capabilities = {}) {
        const container = document.getElementById('source-categories');
        if (!container) return;

        container.innerHTML = '';

        // Create categories
        Object.entries(this.sources).forEach(([category, sources]) => {
            const categoryDiv = this.createCategoryCard(category, sources);
            container.appendChild(categoryDiv);
        });

        // Update source count
        this.updateSourceCount();

        // Setup adult-only mode handler
        const adultOnlyToggle = document.getElementById('adult-only-mode');
        if (adultOnlyToggle) {
            adultOnlyToggle.addEventListener('change', () => this.handleAdultOnlyMode());
        }
    }

    updateSafeSearchPill() {
        const pill = document.getElementById('safe-search-pill');
        const t1 = document.getElementById('safe-search-toggle');
        const t2 = document.getElementById('safe-search');
        const enabled = t1 ? t1.checked : (t2 ? t2.checked : false);
        if (pill) {
            pill.textContent = `Safe Search: ${enabled ? 'ON' : 'OFF'}`;
            pill.className = `badge ${enabled ? 'bg-success' : 'bg-danger'}`;
        }
    }

    toggleSafeSearch() {
        const t1 = document.getElementById('safe-search-toggle');
        const t2 = document.getElementById('safe-search');
        const current = t1 ? t1.checked : (t2 ? t2.checked : false);
        const next = !current;
        if (t1) t1.checked = next;
        if (t2) t2.checked = next;
        this.updateSafeSearchPill();
        // Reload sources to reflect new safe search state
        this.loadSources();
    }

    createCategoryCard(category, sources) {
        const card = document.createElement('div');
        card.style.cssText = `
            background: white;
            border-radius: 8px;
            margin-bottom: 15px;
            border: 1px solid #dee2e6;
            overflow: hidden;
        `;

        // Category header
        const header = document.createElement('div');
        const isAdult = category === 'Adult Content';
        header.style.cssText = `
            background: ${isAdult ? 'linear-gradient(135deg, #ffe6e6 0%, #ffcccc 100%)' : '#f8f9fa'};
            padding: 12px 16px;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            align-items: center;
            justify-content: space-between;
        `;
        header.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2em;">${this.getCategoryIcon(category)}</span>
                <strong style="font-size: 0.95rem;">${category}</strong>
                <span class="badge bg-secondary">${sources.length}</span>
            </div>
            <button type="button" class="btn btn-sm btn-outline-primary select-all-category-btn" data-category="${category}" style="font-size: 0.75rem; padding: 2px 8px;">
                <i class="fas fa-check-square"></i> Select All
            </button>
        `;

        // Add click handler for select-all button
        const selectAllBtn = header.querySelector('button');
        selectAllBtn.addEventListener('click', () => this.selectAllInCategory(category, selectAllBtn));

        // Source grid
        const grid = document.createElement('div');
        grid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 8px;
            padding: 12px;
        `;

        sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.style.cssText = `
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 6px 10px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background: white;
                cursor: pointer;
                transition: all 0.15s ease;
                ${source.nsfw ? 'border-left: 3px solid #dc3545;' : ''}
            `;
            sourceItem.dataset.sourceId = source.id;

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'source-checkbox';
            checkbox.id = `source-${source.id}`;
            checkbox.value = source.id;
            checkbox.dataset.sourceId = source.id;
            checkbox.dataset.nsfw = source.nsfw ? 'true' : 'false';
            checkbox.style.cssText = 'flex-shrink: 0; cursor: pointer;';

            // Handle click on entire item
            sourceItem.addEventListener('click', (e) => {
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change'));
                }
            });

            sourceItem.addEventListener('mouseenter', () => {
                sourceItem.style.background = '#f8f9fa';
                sourceItem.style.borderColor = '#0d6efd';
            });

            sourceItem.addEventListener('mouseleave', () => {
                if (!checkbox.checked) {
                    sourceItem.style.background = 'white';
                    sourceItem.style.borderColor = '#dee2e6';
                }
            });

            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    sourceItem.style.background = '#e7f1ff';
                    sourceItem.style.borderColor = '#0d6efd';
                } else {
                    sourceItem.style.background = 'white';
                    sourceItem.style.borderColor = '#dee2e6';
                }
                this.updateSourceCount();
            });

            const sourceName = document.createElement('span');
            sourceName.style.cssText = `
                flex: 1;
                font-size: 0.85rem;
                font-weight: 500;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            `;
            sourceName.textContent = `${source.nsfw ? '🔞 ' : ''}${source.name}`;
            sourceName.title = source.name;

            const badges = document.createElement('div');
            badges.style.cssText = 'display: flex; gap: 4px; flex-shrink: 0;';
            // Show implementation status badge
            if (typeof source.implemented !== 'undefined') {
                const badge = document.createElement('span');
                badge.className = source.implemented ? 'badge bg-success' : 'badge bg-danger';
                badge.style.fontSize = '0.65rem';
                badge.textContent = source.implemented ? 'Working' : 'Pending';
                badges.appendChild(badge);
            }
            if (source.premium) {
                const badge = document.createElement('span');
                badge.className = 'badge bg-warning';
                badge.style.fontSize = '0.65rem';
                badge.textContent = 'Premium';
                badges.appendChild(badge);
            }

            sourceItem.appendChild(checkbox);
            sourceItem.appendChild(sourceName);
            if (badges.children.length > 0) {
                sourceItem.appendChild(badges);
            }

            grid.appendChild(sourceItem);
        });

        card.appendChild(header);
        card.appendChild(grid);

        return card;
    }

    getCategoryIcon(category) {
        const icons = {
            'Search Engines': '🔍',
            'Stock Photos': '📸',
            'Social Media': '📱',
            'Video Platforms': '🎥',
            'Art Platforms': '🎨',
            'News Media': '📰',
            'E-Commerce': '🛍️',
            'Entertainment': '🎮',
            'Academic': '📚',
            'Tech Forums': '💻',
            'Adult Content': '🔞'
        };
        return icons[category] || '📁';
    }

    selectAllInCategory(category, buttonElement) {
        const sources = this.sources[category];
        if (!sources || sources.length === 0) return;

        // Check if all sources in this category are currently selected
        const allSelected = sources.every(source => {
            const checkbox = document.getElementById(`source-${source.id}`);
            return checkbox && checkbox.checked;
        });

        if (allSelected) {
            // Deselect all sources in category
            sources.forEach(source => {
                const checkbox = document.getElementById(`source-${source.id}`);
                if (checkbox) {
                    checkbox.checked = false;
                    checkbox.dispatchEvent(new Event('change'));
                    this.selectedSources.delete(source.id);
                }
            });

            // Update button text to "Select All"
            if (buttonElement) {
                buttonElement.innerHTML = '<i class="fas fa-check-square"></i> Select All';
            }
        } else {
            // Select all sources in category
            sources.forEach(source => {
                const checkbox = document.getElementById(`source-${source.id}`);
                if (checkbox) {
                    checkbox.checked = true;
                    checkbox.dispatchEvent(new Event('change'));
                    this.selectedSources.add(source.id);
                }
            });

            // Update button text to "Deselect All"
            if (buttonElement) {
                buttonElement.innerHTML = '<i class="fas fa-times-square"></i> Deselect All';
            }
        }

        this.updateSelectedCount();
    }

    selectOnlyInCategory(category) {
        // Deselect all
        const all = document.querySelectorAll('.source-checkbox');
        all.forEach(cb => cb.checked = false);
        this.selectedSources.clear();

        // Select only this category
        const sources = this.sources[category] || [];
        sources.forEach(source => {
            const checkbox = document.getElementById(`source-${source.id}`);
            if (checkbox) {
                checkbox.checked = true;
                this.selectedSources.add(source.id);
            }
        });
        this.updateSelectedCount();
    }

    selectOnlySource(sourceId) {
        // Deselect all
        const all = document.querySelectorAll('.source-checkbox');
        all.forEach(cb => cb.checked = false);
        this.selectedSources.clear();

        // Select just the requested source
        const cb = document.getElementById(`source-${sourceId}`);
        if (cb) {
            cb.checked = true;
            this.selectedSources.add(sourceId);
        }
        this.updateSelectedCount();
    }

    setupEventListeners() {
        // Handle checkbox changes
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('source-checkbox')) {
                if (e.target.checked) {
                    this.selectedSources.add(e.target.dataset.sourceId);
                } else {
                    this.selectedSources.delete(e.target.dataset.sourceId);
                }
                this.updateSelectedCount();
                this.updateCategoryButtonStates();
            }
        });

        // Select all/none buttons
        const selectAllBtn = document.getElementById('select-all-sources');
        if (selectAllBtn) {
            selectAllBtn.onclick = () => this.selectAll();
        }

        const selectNoneBtn = document.getElementById('deselect-all-sources');
        if (selectNoneBtn) {
            selectNoneBtn.onclick = () => this.selectNone();
        }
    }

    setupSafeSearchToggle() {
        const safeSearchToggle = document.getElementById('safe-search-toggle');
        if (safeSearchToggle) {
            safeSearchToggle.addEventListener('change', async () => {
                console.log('Safe search toggled:', safeSearchToggle.checked);
                await this.loadSources();
            });
        }
    }

    selectAll() {
        // Select ALL checkboxes including premium sources
        document.querySelectorAll('.source-checkbox').forEach(cb => {
            cb.checked = true;
            this.selectedSources.add(cb.dataset.sourceId);
        });
        this.updateSelectedCount();
    }

    selectNone() {
        document.querySelectorAll('.source-checkbox').forEach(cb => {
            cb.checked = false;
        });
        this.selectedSources.clear();
        this.updateSelectedCount();
    }

    updateSelectedCount() {
        const countElement = document.getElementById('selected-sources-count');
        if (countElement) {
            countElement.textContent = `${this.selectedSources.size} selected`;
        }
    }

    getSelectedSources() {
        return Array.from(this.selectedSources);
    }

    updateSourceCount() {
        const checkboxes = document.querySelectorAll('.source-checkbox');
        const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
        const countElement = document.getElementById('selected-sources-count');
        if (countElement) {
            countElement.textContent = `${checkedCount} selected`;
        }
    }

    updateCategoryButtonStates() {
        // Update all category buttons to reflect current selection state
        document.querySelectorAll('.select-all-category-btn').forEach(button => {
            const category = button.dataset.category;
            const sources = this.sources[category];

            if (!sources || sources.length === 0) return;

            // Check if all sources in this category are selected
            const allSelected = sources.every(source => {
                const checkbox = document.getElementById(`source-${source.id}`);
                return checkbox && checkbox.checked;
            });

            // Update button text based on selection state
            if (allSelected) {
                button.innerHTML = '<i class="fas fa-times-square"></i> Deselect All';
            } else {
                button.innerHTML = '<i class="fas fa-check-square"></i> Select All';
            }
        });
    }

    handleAdultOnlyMode() {
        const adultOnlyToggle = document.getElementById('adult-only-mode');
        const safeSearchToggle = document.getElementById('safe-search');
        const adultOnlyMode = adultOnlyToggle && adultOnlyToggle.checked;

        if (adultOnlyMode) {
            // Turn off safe search when adult-only is enabled
            if (safeSearchToggle) {
                safeSearchToggle.checked = false;
            }

            // Deselect all sources
            document.querySelectorAll('.source-checkbox').forEach(cb => {
                cb.checked = false;
                cb.dispatchEvent(new Event('change')); // Trigger change event for visual update
            });

            // Sources that support adult content (explicitly or via safe search toggle)
            const adultCapableSources = [
                // Explicit adult sources
                'pornhub', 'xvideos', 'xhamster', 'xnxx', 'redtube', 'youporn',
                'motherless', 'spankbang', 'eporner', 'txxx',
                // Non-adult sources with adult content when safe search is off
                'reddit', 'google', 'bing', 'duckduckgo', 'yandex',
                'twitter', 'pinterest', 'tumblr', 'imgur', 'deviantart',
                'flickr', 'giphy', 'tenor'
            ];

            // Select adult-capable sources
            document.querySelectorAll('.source-checkbox').forEach(cb => {
                const sourceId = cb.dataset.sourceId;
                const isAdultCapable = adultCapableSources.some(s => sourceId.toLowerCase().includes(s));
                const isExplicitAdult = cb.dataset.nsfw === 'true';

                if (isAdultCapable || isExplicitAdult) {
                    cb.checked = true;
                    cb.dispatchEvent(new Event('change')); // Trigger change event for visual update
                }
            });
        }

        this.updateSourceCount();
    }

    showError(message) {
        const container = document.getElementById('source-categories');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </div>
            `;
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Avoid double-render if EnhancedSearchManager is present
    if (!window.EnhancedSearchManager) {
        window.searchUI = new EnhancedSearchUI();
    }
});

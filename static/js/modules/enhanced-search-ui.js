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
    }

    async loadSources() {
        try {
            const response = await fetch('/api/sources');
            const data = await response.json();
            
            if (data.success !== false && data.sources) {
                // Transform the flat array into categorized structure
                this.sources = this.transformSourceData(data.sources);
                this.displaySources();
            }
        } catch (error) {
            console.error('Failed to load sources:', error);
            this.showError('Failed to load content sources');
        }
    }

    transformSourceData(sourcesArray) {
        const categorized = {};
        
        // If sources is an array of category objects
        if (Array.isArray(sourcesArray)) {
            sourcesArray.forEach(categoryObj => {
                if (categoryObj.category && categoryObj.sources) {
                    // Skip "All" category as it's redundant
                    if (categoryObj.category === 'All') return;
                    
                    // Group sources by their actual category
                    categoryObj.sources.forEach(source => {
                        const category = this.getCategoryDisplayName(source.category);
                        if (!categorized[category]) {
                            categorized[category] = [];
                        }
                        categorized[category].push({
                            id: source.id,
                            name: source.name,
                            enabled: !source.subscription_required,
                            nsfw: source.nsfw || false
                        });
                    });
                }
            });
        }
        
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

    displaySources() {
        const container = document.getElementById('source-categories');
        if (!container) return;

        container.innerHTML = '';
        
        // Create a beautiful grid layout
        const grid = document.createElement('div');
        grid.className = 'source-grid';
        grid.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;';
        
        Object.entries(this.sources).forEach(([category, sources]) => {
            const categoryCard = this.createCategoryCard(category, sources);
            grid.appendChild(categoryCard);
        });
        
        container.appendChild(grid);
        
        // Update source count
        const totalSources = Object.values(this.sources).reduce((sum, sources) => sum + sources.length, 0);
        const countElement = document.getElementById('source-count');
        if (countElement) {
            countElement.textContent = `(${totalSources} sources)`;
        }
    }

    createCategoryCard(category, sources) {
        const card = document.createElement('div');
        card.className = 'category-card';
        card.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        `;
        
        // Category header
        const header = document.createElement('div');
        header.style.cssText = 'margin-bottom: 15px; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px;';
        header.innerHTML = `
            <h5 style="margin: 0; color: #333; font-size: 1.1rem; font-weight: 600;">
                ${this.getCategoryIcon(category)} ${category}
                <span style="float: right; font-size: 0.85rem; color: #666;">${sources.length} sources</span>
            </h5>
        `;
        
        // Source checkboxes
        const sourceList = document.createElement('div');
        sourceList.style.cssText = 'max-height: 200px; overflow-y: auto;';
        
        sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'form-check';
            sourceItem.style.cssText = 'padding: 8px 0;';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'form-check-input source-checkbox';
            checkbox.id = `source-${source.id}`;
            checkbox.dataset.sourceId = source.id;
            checkbox.disabled = !source.enabled;
            
            const label = document.createElement('label');
            label.className = 'form-check-label';
            label.htmlFor = `source-${source.id}`;
            label.style.cssText = `cursor: pointer; color: ${source.enabled ? '#333' : '#999'};`;
            label.innerHTML = `
                ${source.name}
                ${source.nsfw ? '<span class="badge bg-warning ms-1">NSFW</span>' : ''}
                ${!source.enabled ? '<span class="badge bg-secondary ms-1">Premium</span>' : ''}
            `;
            
            sourceItem.appendChild(checkbox);
            sourceItem.appendChild(label);
            sourceList.appendChild(sourceItem);
        });
        
        card.appendChild(header);
        card.appendChild(sourceList);
        
        // Add select all button
        const selectAllBtn = document.createElement('button');
        selectAllBtn.className = 'btn btn-sm btn-outline-primary mt-2';
        selectAllBtn.textContent = 'Select All';
        selectAllBtn.onclick = () => this.selectAllInCategory(category);
        card.appendChild(selectAllBtn);
        
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

    selectAllInCategory(category) {
        const sources = this.sources[category];
        sources.forEach(source => {
            if (source.enabled) {
                const checkbox = document.getElementById(`source-${source.id}`);
                if (checkbox) {
                    checkbox.checked = true;
                    this.selectedSources.add(source.id);
                }
            }
        });
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

    selectAll() {
        document.querySelectorAll('.source-checkbox:not(:disabled)').forEach(cb => {
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
    window.searchUI = new EnhancedSearchUI();
});
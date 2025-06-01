/**
 * ============================================================================
 * MEDIA VIEWER MODULE
 * ============================================================================
 * 
 * Handles media viewing, navigation, and controls
 */

class MediaViewer {
    constructor() {
        this.modal = null;
        this.currentIndex = 0;
        this.mediaList = [];
        this.isFullscreen = false;
    }

    /**
     * Initialize media viewer
     */
    init() {
        this.modal = document.getElementById('media-viewer-modal');
        if (!this.modal) return;

        this.setupEventListeners();
        this.setupKeyboardControls();
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Navigation buttons
        const prevBtn = this.modal.querySelector('.media-prev');
        const nextBtn = this.modal.querySelector('.media-next');
        
        if (prevBtn) prevBtn.addEventListener('click', () => this.previousMedia());
        if (nextBtn) nextBtn.addEventListener('click', () => this.nextMedia());

        // Action buttons
        const fullscreenBtn = document.getElementById('media-fullscreen-btn');
        const downloadBtn = document.getElementById('media-download-btn');
        const deleteBtn = document.getElementById('media-delete-btn');
        const infoBtn = document.getElementById('media-info-btn');

        if (fullscreenBtn) fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        if (downloadBtn) downloadBtn.addEventListener('click', () => this.downloadCurrentMedia());
        if (deleteBtn) deleteBtn.addEventListener('click', () => this.deleteCurrentMedia());
        if (infoBtn) infoBtn.addEventListener('click', () => this.toggleInfoPanel());
    }

    /**
     * Set up keyboard controls
     */
    setupKeyboardControls() {
        document.addEventListener('keydown', (event) => {
            if (!this.modal || !this.modal.classList.contains('show')) return;

            switch (event.key) {
                case 'ArrowLeft':
                    event.preventDefault();
                    this.previousMedia();
                    break;
                case 'ArrowRight':
                    event.preventDefault();
                    this.nextMedia();
                    break;
                case 'Escape':
                    if (this.isFullscreen) {
                        this.exitFullscreen();
                    }
                    break;
                case 'f':
                case 'F':
                    event.preventDefault();
                    this.toggleFullscreen();
                    break;
            }
        });
    }

    /**
     * Show media viewer with media list
     */
    showMedia(mediaList, startIndex = 0) {
        this.mediaList = mediaList;
        this.currentIndex = startIndex;
        
        if (this.modal) {
            const modal = new bootstrap.Modal(this.modal);
            modal.show();
            this.displayCurrentMedia();
        }
    }

    /**
     * Display current media
     */
    displayCurrentMedia() {
        if (!this.mediaList.length) return;

        const media = this.mediaList[this.currentIndex];
        const container = document.getElementById('media-container');
        const loading = document.getElementById('media-loading');

        if (!container || !loading) return;

        // Show loading
        loading.classList.remove('d-none');
        container.classList.add('d-none');

        // Update counter
        this.updateCounter();

        // Create media element
        let mediaElement;
        if (Helpers.isImage(media.filename)) {
            mediaElement = document.createElement('img');
            mediaElement.src = media.url || media.path;
            mediaElement.alt = media.filename;
        } else if (Helpers.isVideo(media.filename)) {
            mediaElement = document.createElement('video');
            mediaElement.src = media.url || media.path;
            mediaElement.controls = true;
            mediaElement.autoplay = false;
        } else {
            // Unsupported media type
            container.innerHTML = '<div class="text-center text-muted"><i class="fas fa-file fa-3x mb-3"></i><br>Unsupported media type</div>';
            loading.classList.add('d-none');
            container.classList.remove('d-none');
            return;
        }

        // Handle load event
        mediaElement.addEventListener('load', () => {
            loading.classList.add('d-none');
            container.classList.remove('d-none');
        });

        mediaElement.addEventListener('loadeddata', () => {
            loading.classList.add('d-none');
            container.classList.remove('d-none');
        });

        // Handle error
        mediaElement.addEventListener('error', () => {
            container.innerHTML = '<div class="text-center text-danger"><i class="fas fa-exclamation-triangle fa-3x mb-3"></i><br>Failed to load media</div>';
            loading.classList.add('d-none');
            container.classList.remove('d-none');
        });

        // Clear container and add media
        container.innerHTML = '';
        container.appendChild(mediaElement);
    }

    /**
     * Navigate to previous media
     */
    previousMedia() {
        if (this.mediaList.length <= 1) return;
        
        this.currentIndex = this.currentIndex > 0 ? 
            this.currentIndex - 1 : 
            this.mediaList.length - 1;
        
        this.displayCurrentMedia();
    }

    /**
     * Navigate to next media
     */
    nextMedia() {
        if (this.mediaList.length <= 1) return;
        
        this.currentIndex = this.currentIndex < this.mediaList.length - 1 ? 
            this.currentIndex + 1 : 
            0;
        
        this.displayCurrentMedia();
    }

    /**
     * Update media counter display
     */
    updateCounter() {
        const currentElement = document.getElementById('current-media-index');
        const totalElement = document.getElementById('total-media-count');
        
        if (currentElement) currentElement.textContent = this.currentIndex + 1;
        if (totalElement) totalElement.textContent = this.mediaList.length;
    }

    /**
     * Toggle fullscreen mode
     */
    toggleFullscreen() {
        if (this.isFullscreen) {
            this.exitFullscreen();
        } else {
            this.enterFullscreen();
        }
    }

    /**
     * Enter fullscreen mode
     */
    enterFullscreen() {
        if (this.modal) {
            this.modal.classList.add('media-viewer-fullscreen');
            this.isFullscreen = true;
            
            const icon = document.querySelector('#media-fullscreen-btn i');
            if (icon) {
                icon.className = 'fas fa-compress';
            }
        }
    }

    /**
     * Exit fullscreen mode
     */
    exitFullscreen() {
        if (this.modal) {
            this.modal.classList.remove('media-viewer-fullscreen');
            this.isFullscreen = false;
            
            const icon = document.querySelector('#media-fullscreen-btn i');
            if (icon) {
                icon.className = 'fas fa-expand';
            }
        }
    }

    /**
     * Toggle info panel
     */
    toggleInfoPanel() {
        const panel = document.getElementById('media-info-panel');
        if (panel) {
            panel.classList.toggle('show');
            this.updateInfoPanel();
        }
    }

    /**
     * Update info panel content
     */
    updateInfoPanel() {
        if (!this.mediaList.length) return;
        
        const media = this.mediaList[this.currentIndex];
        const content = document.querySelector('.info-panel-content');
        
        if (content) {
            content.innerHTML = `
                <div class="mb-3">
                    <strong>Filename:</strong><br>
                    ${SecurityUtils.escapeHTML(media.filename)}
                </div>
                <div class="mb-3">
                    <strong>Type:</strong><br>
                    ${Helpers.isImage(media.filename) ? 'Image' : 'Video'}
                </div>
                <div class="mb-3">
                    <strong>Size:</strong><br>
                    ${media.size ? Helpers.formatFileSize(media.size) : 'Unknown'}
                </div>
                <div class="mb-3">
                    <strong>Date:</strong><br>
                    ${media.created_at ? Helpers.formatDate(media.created_at) : 'Unknown'}
                </div>
            `;
        }
    }

    /**
     * Download current media
     */
    downloadCurrentMedia() {
        if (!this.mediaList.length) return;
        
        const media = this.mediaList[this.currentIndex];
        if (media.url || media.path) {
            Helpers.downloadFile(media.url || media.path, media.filename);
        }
    }

    /**
     * Delete current media
     */
    async deleteCurrentMedia() {
        if (!this.mediaList.length) return;
        
        const media = this.mediaList[this.currentIndex];
        const confirmed = confirm(`Are you sure you want to delete "${media.filename}"?`);
        
        if (confirmed) {
            try {
                // Make delete request
                await apiClient.delete(`/api/assets/${media.id}`);
                
                // Remove from current list
                this.mediaList.splice(this.currentIndex, 1);
                
                if (this.mediaList.length === 0) {
                    // Close viewer if no more media
                    const modal = bootstrap.Modal.getInstance(this.modal);
                    modal.hide();
                } else {
                    // Adjust index if needed
                    if (this.currentIndex >= this.mediaList.length) {
                        this.currentIndex = this.mediaList.length - 1;
                    }
                    this.displayCurrentMedia();
                }
                
                // Trigger refresh of assets
                if (window.mediaScraperApp && window.mediaScraperApp.modules.assetManager) {
                    window.mediaScraperApp.modules.assetManager.loadAssets();
                }
                
            } catch (error) {
                console.error('Delete failed:', error);
                alert('Failed to delete media. Please try again.');
            }
        }
    }
}

// Export to global scope
window.MediaViewer = MediaViewer;

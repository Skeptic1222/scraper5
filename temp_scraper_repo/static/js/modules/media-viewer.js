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
        this.fullscreenMode = 0; // 0: normal, 1: fullscreen, 2: fullscreen-stretched
        this.currentVideoElement = null;
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
                // Navigation controls
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    event.preventDefault();
                    this.previousMedia();
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    event.preventDefault();
                    this.nextMedia();
                    break;
                
                // Fullscreen mode controls
                case 'ArrowUp':
                case 'w':
                case 'W':
                    event.preventDefault();
                    this.cycleFullscreenMode(true);
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    event.preventDefault();
                    this.cycleFullscreenMode(false);
                    break;
                
                // Toggle fullscreen
                case 'f':
                case 'F':
                    event.preventDefault();
                    this.toggleFullscreen();
                    break;
                
                // Video controls
                case ' ':
                    event.preventDefault();
                    this.toggleVideoPlayPause();
                    break;
                case 'm':
                case 'M':
                    event.preventDefault();
                    this.toggleVideoMute();
                    break;
                
                // Close controls
                case 'Escape':
                    event.preventDefault();
                    this.closeViewer();
                    break;
                
                // Navigation to first/last
                case 'Home':
                    event.preventDefault();
                    this.goToFirst();
                    break;
                case 'End':
                    event.preventDefault();
                    this.goToLast();
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
            mediaElement.className = 'media-viewer-image';
            this.currentVideoElement = null;
        } else if (Helpers.isVideo(media.filename)) {
            mediaElement = document.createElement('video');
            mediaElement.src = media.url || media.path;
            mediaElement.controls = true;
            mediaElement.autoplay = false;
            mediaElement.className = 'media-viewer-video';
            this.currentVideoElement = mediaElement;
        } else {
            // Unsupported media type
            container.innerHTML = '<div class="text-center text-muted"><i class="fas fa-file fa-3x mb-3"></i><br>Unsupported media type</div>';
            loading.classList.add('d-none');
            container.classList.remove('d-none');
            this.currentVideoElement = null;
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

    /**
     * Cycle through fullscreen modes
     */
    cycleFullscreenMode(forward = true) {
        if (forward) {
            this.fullscreenMode = (this.fullscreenMode + 1) % 3;
        } else {
            this.fullscreenMode = this.fullscreenMode === 0 ? 2 : this.fullscreenMode - 1;
        }
        
        this.applyFullscreenMode();
    }

    /**
     * Apply current fullscreen mode
     */
    applyFullscreenMode() {
        if (!this.modal) return;

        // Remove all fullscreen classes
        this.modal.classList.remove('media-viewer-normal', 'media-viewer-fullscreen', 'media-viewer-fullscreen-stretched');
        
        // Apply current mode
        switch (this.fullscreenMode) {
            case 0:
                this.modal.classList.add('media-viewer-normal');
                this.isFullscreen = false;
                break;
            case 1:
                this.modal.classList.add('media-viewer-fullscreen');
                this.isFullscreen = true;
                break;
            case 2:
                this.modal.classList.add('media-viewer-fullscreen-stretched');
                this.isFullscreen = true;
                break;
        }

        // Update fullscreen button icon
        const icon = document.querySelector('#media-fullscreen-btn i');
        if (icon) {
            switch (this.fullscreenMode) {
                case 0:
                    icon.className = 'fas fa-expand';
                    break;
                case 1:
                    icon.className = 'fas fa-compress';
                    break;
                case 2:
                    icon.className = 'fas fa-expand-arrows-alt';
                    break;
            }
        }
    }

    /**
     * Toggle video play/pause
     */
    toggleVideoPlayPause() {
        if (this.currentVideoElement) {
            if (this.currentVideoElement.paused) {
                this.currentVideoElement.play();
            } else {
                this.currentVideoElement.pause();
            }
        }
    }

    /**
     * Toggle video mute
     */
    toggleVideoMute() {
        if (this.currentVideoElement) {
            this.currentVideoElement.muted = !this.currentVideoElement.muted;
        }
    }

    /**
     * Close viewer
     */
    closeViewer() {
        if (this.modal) {
            const modal = bootstrap.Modal.getInstance(this.modal);
            if (modal) {
                modal.hide();
            }
        }
        this.cleanup();
    }

    /**
     * Go to first media
     */
    goToFirst() {
        if (this.mediaList.length > 0) {
            this.currentIndex = 0;
            this.displayCurrentMedia();
        }
    }

    /**
     * Go to last media
     */
    goToLast() {
        if (this.mediaList.length > 0) {
            this.currentIndex = this.mediaList.length - 1;
            this.displayCurrentMedia();
        }
    }

    /**
     * Cleanup when closing viewer
     */
    cleanup() {
        if (this.currentVideoElement) {
            this.currentVideoElement.pause();
            this.currentVideoElement.currentTime = 0;
            this.currentVideoElement = null;
        }
        this.fullscreenMode = 0;
        this.isFullscreen = false;
    }
}

// Export to global scope
window.MediaViewer = MediaViewer;

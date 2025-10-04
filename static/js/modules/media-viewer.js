/**
 * Enhanced Media Viewer with keyboard controls and multiple view modes
 */
class MediaViewer {
    constructor() {
        this.currentAssets = [];
        this.currentIndex = 0;
        this.viewMode = 'normal'; // normal, fullscreen, fullscreen-stretched
        this.isOpen = false;
        this.mediaElement = null;
        this.overlay = null;
        this.container = null;
        
        this.createViewerElements();
        this.setupEventListeners();
    }
    
    createViewerElements() {
        const viewerHTML = `
            <div id="media-viewer-overlay" class="media-viewer-overlay">
                <div class="media-viewer-container">
                    <div class="media-viewer-header">
                        <span class="media-info"></span>
                        <div class="viewer-controls">
                            <button class="viewer-btn" id="viewer-fullscreen" title="Fullscreen (W/↑)">
                                <i class="fas fa-expand"></i>
                            </button>
                            <button class="viewer-btn" id="viewer-close" title="Close (ESC/S/↓)">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="media-viewer-content">
                        <button class="nav-btn nav-prev" id="viewer-prev" title="Previous (A/←)">
                            <i class="fas fa-chevron-left"></i>
                        </button>
                        
                        <div class="media-container" id="media-container"></div>
                        
                        <button class="nav-btn nav-next" id="viewer-next" title="Next (D/→)">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                    
                    <div class="media-viewer-footer">
                        <span class="media-counter"></span>
                        <div class="media-controls">
                            <span id="viewer-mode-indicator">Normal View</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing viewer if present
        const existingViewer = document.getElementById('media-viewer-overlay');
        if (existingViewer) {
            existingViewer.remove();
        }
        
        document.body.insertAdjacentHTML('beforeend', viewerHTML);
        this.overlay = document.getElementById('media-viewer-overlay');
        this.container = document.querySelector('.media-viewer-container');
    }
    
    setupEventListeners() {
        // Close button
        document.getElementById('viewer-close').addEventListener('click', () => this.close());
        
        // Navigation buttons
        document.getElementById('viewer-prev').addEventListener('click', () => this.previous());
        document.getElementById('viewer-next').addEventListener('click', () => this.next());
        
        // Fullscreen button
        document.getElementById('viewer-fullscreen').addEventListener('click', () => this.toggleFullscreen());
        
        // Overlay click to close
        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => this.handleKeypress(e));
    }
    
    handleKeypress(e) {
        if (!this.isOpen) return;
        
        switch(e.key) {
            case 'Escape':
                this.close();
                break;
            case 'ArrowLeft':
            case 'a':
            case 'A':
                e.preventDefault();
                this.previous();
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                e.preventDefault();
                this.next();
                break;
            case 'ArrowUp':
            case 'w':
            case 'W':
                e.preventDefault();
                this.increaseViewMode();
                break;
            case 'ArrowDown':
            case 's':
            case 'S':
                e.preventDefault();
                this.decreaseViewMode();
                break;
            case ' ':
            case 'Enter':
                e.preventDefault();
                this.togglePlayPause();
                break;
        }
    }
    
    open(assets, index = 0) {
        if (!assets || assets.length === 0) return;
        
        this.currentAssets = assets;
        this.currentIndex = index;
        this.isOpen = true;
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        this.loadMedia();
    }
    
    close() {
        this.isOpen = false;
        this.overlay.classList.remove('active');
        document.body.style.overflow = '';
        this.viewMode = 'normal';
        this.container.classList.remove('fullscreen', 'fullscreen-stretched');
        
        // Clean up media element
        if (this.mediaElement) {
            if (this.mediaElement.tagName === 'VIDEO') {
                this.mediaElement.pause();
                this.mediaElement.src = '';
            }
            this.mediaElement = null;
        }
        
        // Clear container
        const mediaContainer = document.getElementById('media-container');
        if (mediaContainer) {
            mediaContainer.innerHTML = '';
        }
    }
    
    loadMedia() {
        const asset = this.currentAssets[this.currentIndex];
        const mediaContainer = document.getElementById('media-container');
        
        // Clear previous content
        mediaContainer.innerHTML = '';
        
        // Determine media type from file_type field
        const fileType = (asset.file_type || asset.type || '').toLowerCase();
        const isImage = fileType.includes('image') || 
                       fileType.includes('jpeg') || 
                       fileType.includes('jpg') || 
                       fileType.includes('png') || 
                       fileType.includes('gif') || 
                       fileType.includes('webp');
        
        const isVideo = fileType.includes('video') || 
                       fileType.includes('mp4') || 
                       fileType.includes('webm') || 
                       fileType.includes('ogg');
        
        const mediaUrl = asset.url || `/serve/${asset.id}`;
        
        if (isImage) {
            const img = document.createElement('img');
            img.src = mediaUrl;
            img.alt = asset.filename || 'Image';
            img.className = 'viewer-media';
            img.onerror = () => {
                img.src = '/static/images/image-error.png';
                img.alt = 'Error loading image';
            };
            mediaContainer.appendChild(img);
            this.mediaElement = img;
        } else if (isVideo) {
            const video = document.createElement('video');
            video.src = mediaUrl;
            video.controls = true;
            video.autoplay = true;
            video.preload = 'metadata';  // Better performance
            video.playsInline = true;  // Mobile support
            video.className = 'viewer-media';

            // Add loading state
            video.addEventListener('loadstart', () => {
                mediaContainer.classList.add('loading');
            });

            video.addEventListener('canplay', () => {
                mediaContainer.classList.remove('loading');
            });

            // Improved error handling
            video.onerror = () => {
                mediaContainer.innerHTML = `
                    <div class="file-preview error">
                        <i class="fas fa-exclamation-triangle fa-5x"></i>
                        <p>Error loading video</p>
                        <p class="text-muted small">Try downloading the file instead</p>
                        <a href="${mediaUrl}" download class="btn btn-primary mt-3">
                            <i class="fas fa-download"></i> Download Video
                        </a>
                    </div>
                `;
            };

            mediaContainer.appendChild(video);
            this.mediaElement = video;
        } else {
            // Fallback for other file types
            const div = document.createElement('div');
            div.className = 'file-preview';
            div.innerHTML = `
                <i class="fas fa-file fa-5x"></i>
                <p>${asset.filename || 'File'}</p>
                <a href="${mediaUrl}" target="_blank" class="btn btn-primary mt-3">
                    <i class="fas fa-download"></i> Download
                </a>
            `;
            mediaContainer.appendChild(div);
        }
        
        // Update info
        this.updateInfo();
    }
    
    updateInfo() {
        const asset = this.currentAssets[this.currentIndex];
        const infoElement = document.querySelector('.media-info');
        const counterElement = document.querySelector('.media-counter');
        const modeIndicator = document.getElementById('viewer-mode-indicator');
        
        if (infoElement) {
            infoElement.textContent = asset.filename || 'Unknown';
        }
        
        if (counterElement) {
            counterElement.textContent = `${this.currentIndex + 1} / ${this.currentAssets.length}`;
        }
        
        if (modeIndicator) {
            const modeText = {
                'normal': 'Normal View',
                'fullscreen': 'Fullscreen',
                'fullscreen-stretched': 'Fullscreen Stretched'
            };
            modeIndicator.textContent = modeText[this.viewMode];
        }
    }
    
    next() {
        if (this.currentIndex < this.currentAssets.length - 1) {
            this.currentIndex++;
        } else {
            // Loop to beginning
            this.currentIndex = 0;
        }
        this.loadMedia();
    }
    
    previous() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
        } else {
            // Loop to end
            this.currentIndex = this.currentAssets.length - 1;
        }
        this.loadMedia();
    }
    
    togglePlayPause() {
        if (this.mediaElement && this.mediaElement.tagName === 'VIDEO') {
            if (this.mediaElement.paused) {
                this.mediaElement.play();
            } else {
                this.mediaElement.pause();
            }
        } else if (!this.mediaElement || this.mediaElement.tagName === 'IMG') {
            // For images, open in fullscreen
            if (this.viewMode === 'normal') {
                this.increaseViewMode();
            }
        }
    }
    
    increaseViewMode() {
        if (this.viewMode === 'normal') {
            this.viewMode = 'fullscreen';
            this.container.classList.add('fullscreen');
            this.container.classList.remove('fullscreen-stretched');
        } else if (this.viewMode === 'fullscreen') {
            this.viewMode = 'fullscreen-stretched';
            this.container.classList.add('fullscreen-stretched');
        }
        this.updateInfo();
    }
    
    decreaseViewMode() {
        if (this.viewMode === 'fullscreen-stretched') {
            this.viewMode = 'fullscreen';
            this.container.classList.remove('fullscreen-stretched');
            this.updateInfo();
        } else if (this.viewMode === 'fullscreen') {
            this.viewMode = 'normal';
            this.container.classList.remove('fullscreen', 'fullscreen-stretched');
            this.updateInfo();
        } else if (this.viewMode === 'normal') {
            this.close();
        }
    }
    
    toggleFullscreen() {
        if (this.viewMode === 'normal') {
            this.increaseViewMode();
        } else {
            this.viewMode = 'normal';
            this.container.classList.remove('fullscreen', 'fullscreen-stretched');
            this.updateInfo();
        }
    }
}

// Initialize global media viewer
window.mediaViewer = new MediaViewer();
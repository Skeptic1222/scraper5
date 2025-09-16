#!/usr/bin/env python3
"""
Manual fixes for remaining issues
"""

import re

def apply_manual_fixes():
    """Apply manual fixes to index.html"""
    
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix sources section with proper grid layout
    sources_html = '''
    <!-- Sources Section -->
    <div id="sources-section" class="content-section" style="display: none;">
        <div class="container-fluid">
            <h2 class="mb-4">Available Sources</h2>
            
            <!-- Sources Grid -->
            <div class="sources-grid">
                <div class="source-card" data-source="instagram">
                    <div class="source-header">
                        <div class="source-icon">
                            <i class="fas fa-check-circle text-success"></i>
                        </div>
                        <h5 class="source-title">Instagram</h5>
                    </div>
                    <div class="source-body">
                        <p class="source-description">Download photos and videos from Instagram</p>
                        <div class="source-stats">
                            <span class="stat-item">
                                <i class="fas fa-image"></i> 10M+ items
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-star"></i> High Quality
                            </span>
                        </div>
                    </div>
                    <div class="source-footer">
                        <button class="btn btn-primary btn-sm w-100" onclick="browseSource('instagram')">
                            <i class="fas fa-folder-open"></i> Browse
                        </button>
                    </div>
                </div>
                
                <div class="source-card" data-source="twitter">
                    <div class="source-header">
                        <div class="source-icon">
                            <i class="fas fa-check-circle text-success"></i>
                        </div>
                        <h5 class="source-title">Twitter/X</h5>
                    </div>
                    <div class="source-body">
                        <p class="source-description">Download media from Twitter/X posts</p>
                        <div class="source-stats">
                            <span class="stat-item">
                                <i class="fas fa-image"></i> 5M+ items
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-star"></i> HD Quality
                            </span>
                        </div>
                    </div>
                    <div class="source-footer">
                        <button class="btn btn-primary btn-sm w-100" onclick="browseSource('twitter')">
                            <i class="fas fa-folder-open"></i> Browse
                        </button>
                    </div>
                </div>
                
                <div class="source-card" data-source="tiktok">
                    <div class="source-header">
                        <div class="source-icon">
                            <i class="fas fa-lock text-warning"></i>
                        </div>
                        <h5 class="source-title">TikTok</h5>
                    </div>
                    <div class="source-body">
                        <p class="source-description">Download TikTok videos without watermark</p>
                        <div class="source-stats">
                            <span class="stat-item">
                                <i class="fas fa-video"></i> 20M+ videos
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-star"></i> Premium
                            </span>
                        </div>
                    </div>
                    <div class="source-footer">
                        <button class="btn btn-warning btn-sm w-100" onclick="showSubscription()">
                            <i class="fas fa-crown"></i> Premium Only
                        </button>
                    </div>
                </div>
                
                <div class="source-card" data-source="youtube">
                    <div class="source-header">
                        <div class="source-icon">
                            <i class="fas fa-lock text-warning"></i>
                        </div>
                        <h5 class="source-title">YouTube</h5>
                    </div>
                    <div class="source-body">
                        <p class="source-description">Download YouTube videos in multiple formats</p>
                        <div class="source-stats">
                            <span class="stat-item">
                                <i class="fas fa-video"></i> Unlimited
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-star"></i> 4K Support
                            </span>
                        </div>
                    </div>
                    <div class="source-footer">
                        <button class="btn btn-warning btn-sm w-100" onclick="showSubscription()">
                            <i class="fas fa-crown"></i> Premium Only
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    # Replace sources section
    sources_pattern = r'<div id="sources-section"[^>]*>.*?</div>\s*(?=<div id="downloads-section")'
    content = re.sub(sources_pattern, sources_html, content, flags=re.DOTALL)
    
    # 2. Add additional CSS fixes
    additional_css = '''
        /* Additional fixes for reported issues */
        
        /* Fix navbar brand for dark mode */
        .navbar-brand {
            color: var(--bs-navbar-color) !important;
            transition: color 0.3s ease;
        }
        
        .dark-mode .navbar-brand {
            color: #ffffff !important;
        }
        
        /* Fix user dropdown visibility */
        .user-dropdown {
            display: none !important;
        }
        
        .user-menu:hover .user-dropdown {
            display: block !important;
        }
        
        /* Video thumbnail consistency */
        .asset-card {
            position: relative;
            overflow: hidden;
        }
        
        .asset-card img,
        .asset-card video {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background-color: #f0f0f0;
        }
        
        .dark-mode .asset-card img,
        .dark-mode .asset-card video {
            background-color: #2a2a2a;
        }
        
        /* Video hover preview */
        .asset-card video.preview {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 200px;
            object-fit: cover;
            display: none;
            z-index: 2;
        }
        
        .asset-card:hover video.preview {
            display: block;
        }
        
        /* System status spacing */
        .system-status {
            padding: 30px;
            margin-bottom: 40px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            margin-top: 25px;
        }
        
        .status-item {
            padding: 20px;
            background: rgba(0, 123, 255, 0.1);
            border-radius: 10px;
            text-align: center;
            transition: transform 0.2s ease;
        }
        
        .status-item:hover {
            transform: translateY(-2px);
        }
        
        .dark-mode .status-item {
            background: rgba(255, 255, 255, 0.1);
        }
    '''
    
    # Insert additional CSS
    content = content.replace('</style>', additional_css + '\n    </style>')
    
    # 3. Add JavaScript for video preview and sign out
    additional_js = '''
        // Fix sign out functionality
        function signOut() {
            if (confirm('Are you sure you want to sign out?')) {
                window.location.href = '/logout';
            }
        }
        
        // Video preview on hover
        function initVideoPreview() {
            document.querySelectorAll('.asset-card').forEach(card => {
                const thumbnail = card.querySelector('img');
                const videoSrc = thumbnail?.dataset.videoSrc;
                
                if (videoSrc && thumbnail) {
                    // Create preview video element
                    const video = document.createElement('video');
                    video.className = 'preview';
                    video.src = videoSrc;
                    video.muted = true;
                    video.loop = true;
                    video.preload = 'metadata';
                    
                    card.appendChild(video);
                    
                    // Play on hover
                    card.addEventListener('mouseenter', () => {
                        video.play().catch(e => console.log('Autoplay prevented'));
                    });
                    
                    card.addEventListener('mouseleave', () => {
                        video.pause();
                        video.currentTime = 0;
                    });
                }
            });
        }
        
        // Initialize on page load and after loading assets
        document.addEventListener('DOMContentLoaded', initVideoPreview);
        
        // Enhanced image viewer with WASD support
        const imageViewer = {
            currentIndex: 0,
            images: [],
            
            init() {
                document.addEventListener('keydown', (e) => {
                    if (!this.isOpen()) return;
                    
                    switch(e.key.toLowerCase()) {
                        case 'arrowleft':
                        case 'a':
                            this.previous();
                            break;
                        case 'arrowright':
                        case 'd':
                            this.next();
                            break;
                        case 'arrowup':
                        case 'w':
                            this.zoomIn();
                            break;
                        case 'arrowdown':
                        case 's':
                            this.zoomOut();
                            break;
                        case 'escape':
                            this.close();
                            break;
                    }
                });
            },
            
            open(index) {
                this.currentIndex = index;
                const viewer = document.getElementById('imageViewer');
                if (viewer) {
                    viewer.classList.add('active');
                    this.updateImage();
                }
            },
            
            close() {
                const viewer = document.getElementById('imageViewer');
                if (viewer) {
                    viewer.classList.remove('active');
                }
            },
            
            isOpen() {
                const viewer = document.getElementById('imageViewer');
                return viewer && viewer.classList.contains('active');
            },
            
            next() {
                this.currentIndex = (this.currentIndex + 1) % this.images.length;
                this.updateImage();
            },
            
            previous() {
                this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
                this.updateImage();
            },
            
            updateImage() {
                const img = document.getElementById('viewerImage');
                if (img && this.images[this.currentIndex]) {
                    img.src = this.images[this.currentIndex];
                }
            },
            
            zoomIn() {
                const img = document.getElementById('viewerImage');
                if (img) {
                    const scale = parseFloat(img.style.transform.replace('scale(', '').replace(')', '') || '1');
                    img.style.transform = `scale(${Math.min(scale + 0.1, 3)})`;
                }
            },
            
            zoomOut() {
                const img = document.getElementById('viewerImage');
                if (img) {
                    const scale = parseFloat(img.style.transform.replace('scale(', '').replace(')', '') || '1');
                    img.style.transform = `scale(${Math.max(scale - 0.1, 0.5)})`;
                }
            }
        };
        
        // Initialize image viewer
        imageViewer.init();
    '''
    
    # Insert additional JS
    content = content.replace('</script>', additional_js + '\n    </script>')
    
    # 4. Fix system status HTML
    status_html = '''
            <div class="system-status">
                <h4>System Status</h4>
                <div class="status-grid">
                    <div class="status-item">
                        <span class="status-value">12</span>
                        <span class="status-label">Active Downloads</span>
                    </div>
                    <div class="status-item">
                        <span class="status-value">1,234</span>
                        <span class="status-label">Total Users</span>
                    </div>
                    <div class="status-item">
                        <span class="status-value">45.6 GB</span>
                        <span class="status-label">Storage Used</span>
                    </div>
                    <div class="status-item">
                        <span class="status-value">98.5%</span>
                        <span class="status-label">System Health</span>
                    </div>
                </div>
            </div>
    '''
    
    # Replace system status
    status_pattern = r'<div class="system-status[^"]*">.*?</div>\s*</div>'
    content = re.sub(status_pattern, status_html, content, flags=re.DOTALL)
    
    # Write back
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Applied all manual fixes successfully!")

if __name__ == '__main__':
    apply_manual_fixes() 
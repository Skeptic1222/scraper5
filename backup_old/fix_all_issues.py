#!/usr/bin/env python3
"""
Fix all reported issues in the scraper application
"""

import re
import os

def fix_index_html():
    """Fix all issues in index.html"""
    
    # Read the current index.html
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix download URL
    content = content.replace(
        'link.href = `/downloads/${encodeURIComponent(assetId)}`;',
        'link.href = `/api/media/${assetId}/download`;'
    )
    
    # 2. Fix sources display - find and replace the sources section
    sources_pattern = r'(<div id="sources-section"[^>]*>)(.*?)(<div id="downloads-section")'
    sources_replacement = r'''\1
        <div class="container-fluid">
            <h2 class="mb-4">Available Sources</h2>
            
            <!-- Sources Grid -->
            <div class="sources-grid">
                {% for source in sources %}
                <div class="source-card" data-source="{{ source.name }}">
                    <div class="source-header">
                        <div class="source-icon">
                            {% if source.is_premium %}
                                <i class="fas fa-lock text-warning"></i>
                            {% else %}
                                <i class="fas fa-check-circle text-success"></i>
                            {% endif %}
                        </div>
                        <h5 class="source-title">{{ source.display_name }}</h5>
                    </div>
                    <div class="source-body">
                        <p class="source-description">{{ source.description }}</p>
                        <div class="source-stats">
                            <span class="stat-item">
                                <i class="fas fa-image"></i> {{ source.media_count }} items
                            </span>
                            <span class="stat-item">
                                <i class="fas fa-star"></i> {{ source.quality }}
                            </span>
                        </div>
                    </div>
                    <div class="source-footer">
                        {% if source.is_premium and not user_info.is_premium %}
                            <button class="btn btn-warning btn-sm w-100" onclick="showSubscription()">
                                <i class="fas fa-crown"></i> Premium Only
                            </button>
                        {% else %}
                            <button class="btn btn-primary btn-sm w-100" onclick="browseSource('{{ source.name }}')">
                                <i class="fas fa-folder-open"></i> Browse
                            </button>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    \3'''
    content = re.sub(sources_pattern, sources_replacement, content, flags=re.DOTALL)
    
    # 3. Add CSS for sources grid
    css_addition = '''
        /* Sources Grid Layout */
        .sources-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .source-card {
            background: var(--bs-body-bg);
            border: 1px solid var(--bs-border-color);
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .source-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .source-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .source-icon {
            font-size: 24px;
            margin-right: 10px;
        }
        
        .source-title {
            margin: 0;
            font-size: 18px;
            font-weight: 600;
        }
        
        .source-description {
            color: var(--bs-secondary-color);
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        .source-stats {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 13px;
            color: var(--bs-secondary-color);
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        /* System Status Improvements */
        .system-status {
            background: var(--bs-body-bg);
            border: 1px solid var(--bs-border-color);
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 30px;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .status-item {
            background: var(--bs-gray-100);
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }
        
        .dark-mode .status-item {
            background: var(--bs-gray-800);
        }
        
        .status-value {
            font-size: 24px;
            font-weight: bold;
            color: var(--bs-primary);
            display: block;
            margin-bottom: 5px;
        }
        
        .status-label {
            font-size: 14px;
            color: var(--bs-secondary-color);
        }
        
        /* Video Thumbnail Fixes */
        .asset-card img,
        .asset-card video {
            width: 100%;
            height: 200px;
            object-fit: cover;
            background: var(--bs-gray-200);
        }
        
        .dark-mode .asset-card img,
        .dark-mode .asset-card video {
            background: var(--bs-gray-700);
        }
        
        /* Video Hover Autoplay */
        .asset-card:hover video {
            display: block;
        }
        
        .asset-card:hover img.video-thumbnail {
            display: none;
        }
        
        /* Title Dark Mode Fix */
        .navbar-brand {
            color: var(--bs-navbar-brand-color) !important;
        }
        
        /* Sign Out Button Fix */
        .user-menu {
            position: relative;
        }
        
        .user-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            background: var(--bs-body-bg);
            border: 1px solid var(--bs-border-color);
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            min-width: 200px;
            z-index: 1000;
            display: none;
        }
        
        .user-menu:hover .user-dropdown,
        .user-dropdown:hover {
            display: block;
        }
        
        /* Image Viewer Improvements */
        .image-viewer {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.95);
            z-index: 9999;
            display: none;
            align-items: center;
            justify-content: center;
        }
        
        .image-viewer.active {
            display: flex;
        }
        
        .viewer-content {
            max-width: 90%;
            max-height: 90%;
            position: relative;
        }
        
        .viewer-controls {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.8);
            padding: 10px 20px;
            border-radius: 30px;
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .viewer-nav {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(0,0,0,0.8);
            color: white;
            border: none;
            padding: 20px;
            cursor: pointer;
            font-size: 24px;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        
        .viewer-nav:hover {
            background: rgba(0,0,0,0.9);
        }
        
        .viewer-nav.prev {
            left: 20px;
        }
        
        .viewer-nav.next {
            right: 20px;
        }
        
        .viewer-close {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            border: none;
            padding: 10px 15px;
            cursor: pointer;
            font-size: 20px;
            border-radius: 4px;
        }
    '''
    
    # Insert CSS before closing style tag
    content = content.replace('</style>', css_addition + '\n    </style>')
    
    # 4. Fix system status display
    status_pattern = r'(<div class="system-status[^"]*">)(.*?)(<h4>System Status</h4>)(.*?)(</div>\s*</div>)'
    status_replacement = r'''\1
                <h4>System Status</h4>
                <div class="status-grid">
                    <div class="status-item">
                        <span class="status-value">{{ system_stats.active_downloads }}</span>
                        <span class="status-label">Active Downloads</span>
                    </div>
                    <div class="status-item">
                        <span class="status-value">{{ system_stats.total_users }}</span>
                        <span class="status-label">Total Users</span>
                    </div>
                    <div class="status-item">
                        <span class="status-value">{{ system_stats.storage_used }}</span>
                        <span class="status-label">Storage Used</span>
                    </div>
                    <div class="status-item">
                        <span class="status-value">{{ system_stats.api_calls }}</span>
                        <span class="status-label">API Calls Today</span>
                    </div>
                </div>\5'''
    content = re.sub(status_pattern, status_replacement, content, flags=re.DOTALL)
    
    # 5. Add video autoplay on hover functionality
    js_addition = '''
        // Video autoplay on hover
        document.addEventListener('DOMContentLoaded', function() {
            const assetCards = document.querySelectorAll('.asset-card');
            
            assetCards.forEach(card => {
                const video = card.querySelector('video');
                const thumbnail = card.querySelector('img.video-thumbnail');
                
                if (video && thumbnail) {
                    // Hide video by default
                    video.style.display = 'none';
                    
                    card.addEventListener('mouseenter', function() {
                        thumbnail.style.display = 'none';
                        video.style.display = 'block';
                        video.play().catch(e => console.log('Autoplay prevented:', e));
                    });
                    
                    card.addEventListener('mouseleave', function() {
                        video.pause();
                        video.currentTime = 0;
                        video.style.display = 'none';
                        thumbnail.style.display = 'block';
                    });
                }
            });
        });
        
        // Enhanced keyboard navigation for image viewer
        let currentImageIndex = 0;
        let viewerImages = [];
        
        function openImageViewer(index) {
            currentImageIndex = index;
            const viewer = document.getElementById('imageViewer');
            const img = document.getElementById('viewerImage');
            
            if (viewer && img && viewerImages[index]) {
                img.src = viewerImages[index].src;
                viewer.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        }
        
        function closeImageViewer() {
            const viewer = document.getElementById('imageViewer');
            if (viewer) {
                viewer.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
        
        function navigateViewer(direction) {
            if (direction === 'next') {
                currentImageIndex = (currentImageIndex + 1) % viewerImages.length;
            } else {
                currentImageIndex = (currentImageIndex - 1 + viewerImages.length) % viewerImages.length;
            }
            openImageViewer(currentImageIndex);
        }
        
        // Keyboard controls
        document.addEventListener('keydown', function(e) {
            const viewer = document.getElementById('imageViewer');
            if (!viewer || !viewer.classList.contains('active')) return;
            
            switch(e.key) {
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    navigateViewer('prev');
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    navigateViewer('next');
                    break;
                case 'ArrowUp':
                case 'w':
                case 'W':
                    // Zoom in
                    const img = document.getElementById('viewerImage');
                    if (img) {
                        const currentScale = parseFloat(img.style.transform.replace('scale(', '').replace(')', '') || '1');
                        img.style.transform = `scale(${Math.min(currentScale + 0.1, 3)})`;
                    }
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    // Zoom out
                    const img2 = document.getElementById('viewerImage');
                    if (img2) {
                        const currentScale = parseFloat(img2.style.transform.replace('scale(', '').replace(')', '') || '1');
                        img2.style.transform = `scale(${Math.max(currentScale - 0.1, 0.5)})`;
                    }
                    break;
                case 'Escape':
                    closeImageViewer();
                    break;
            }
        });
    '''
    
    # Insert JS before closing script tag
    content = content.replace('</script>', js_addition + '\n    </script>')
    
    # 6. Add image viewer HTML
    viewer_html = '''
    <!-- Enhanced Image Viewer -->
    <div id="imageViewer" class="image-viewer">
        <button class="viewer-close" onclick="closeImageViewer()">
            <i class="fas fa-times"></i>
        </button>
        <button class="viewer-nav prev" onclick="navigateViewer('prev')">
            <i class="fas fa-chevron-left"></i>
        </button>
        <button class="viewer-nav next" onclick="navigateViewer('next')">
            <i class="fas fa-chevron-right"></i>
        </button>
        <div class="viewer-content">
            <img id="viewerImage" src="" alt="Viewing image">
            <div class="viewer-controls">
                <span class="text-white">Use Arrow Keys or WASD to navigate • ESC to close</span>
            </div>
        </div>
    </div>
    '''
    
    # Insert viewer HTML before closing body tag
    content = content.replace('</body>', viewer_html + '\n</body>')
    
    # 7. Fix sign out functionality
    signout_fix = '''
        function signOut() {
            if (confirm('Are you sure you want to sign out?')) {
                window.location.href = '/logout';
            }
        }
    '''
    
    # Add signOut function if not exists
    if 'function signOut()' not in content:
        content = content.replace('</script>', signout_fix + '\n    </script>')
    
    # Write the fixed content back
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed all issues in index.html")

def fix_app_py():
    """Fix subscription and download endpoints in app.py"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add missing download endpoint if not exists
    if '@app.route(\'/api/media/<path:media_id>/download\')' not in content:
        download_endpoint = '''
@app.route('/api/media/<path:media_id>/download')
@login_required
def download_media(media_id):
    """Download a media file"""
    try:
        # Check user credits
        if current_user.credits <= 0:
            return jsonify({'error': 'Insufficient credits'}), 403
        
        # Get the media file path
        media_path = os.path.join(app.config['UPLOAD_FOLDER'], media_id)
        
        if not os.path.exists(media_path):
            return jsonify({'error': 'Media not found'}), 404
        
        # Deduct credit
        current_user.credits -= 1
        db.session.commit()
        
        # Send file
        return send_file(media_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500
'''
        
        # Insert before the last route or at the end
        content = content.replace('if __name__ == \'__main__\':', download_endpoint + '\n\nif __name__ == \'__main__\':')
    
    # Fix subscription endpoint
    subscription_fix = '''
@app.route('/api/subscription/status')
@login_required
def subscription_status():
    """Get user subscription status"""
    return jsonify({
        'success': True,
        'is_premium': current_user.is_premium,
        'credits': current_user.credits,
        'daily_downloads': current_user.daily_downloads,
        'max_daily_downloads': 25 if not current_user.is_premium else 999999
    })

@app.route('/api/subscription/upgrade', methods=['POST'])
@login_required
def upgrade_subscription():
    """Upgrade to premium (placeholder)"""
    # This is a placeholder - implement payment processing
    return jsonify({
        'success': False,
        'message': 'Payment processing coming soon!'
    })
'''
    
    if '@app.route(\'/api/subscription/status\')' not in content:
        content = content.replace('if __name__ == \'__main__\':', subscription_fix + '\n\nif __name__ == \'__main__\':')
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed app.py endpoints")

if __name__ == '__main__':
    print("🔧 Fixing all reported issues...")
    fix_index_html()
    fix_app_py()
    print("✨ All fixes applied successfully!") 
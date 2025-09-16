/**
 * App Updates - Additional functionality for MediaScraperApp
 * Handles admin features, sign-in bonus, theme fixes, and more
 */

// Admin Management Module
class AdminManager {
    constructor(app) {
        this.app = app;
        this.isAdmin = false;
        this.init();
    }
    
    async init() {
        // Check if current user is admin
        const userInfo = await this.app.getUserInfo();
        this.isAdmin = userInfo?.user?.is_admin || false;
        
        if (this.isAdmin) {
            this.setupAdminUI();
        }
    }
    
    setupAdminUI() {
        // Add admin badge to navbar
        const userDropdown = document.getElementById('user-dropdown');
        if (userDropdown) {
            const adminBadge = document.createElement('span');
            adminBadge.className = 'badge bg-danger ms-2';
            adminBadge.textContent = 'ADMIN';
            userDropdown.appendChild(adminBadge);
        }
    }
    
    async loadUsers() {
        try {
            const response = await fetch('/api/admin/users', {
                headers: {
                    'X-CSRFToken': this.app.getCSRFToken()
                }
            });
            
            if (!response.ok) throw new Error('Failed to load users');
            
            const data = await response.json();
            this.displayUsers(data.users);
        } catch (error) {
            console.error('Error loading users:', error);
            this.app.showError('Failed to load users');
        }
    }
    
    displayUsers(users) {
        const container = document.getElementById('admin-users-list');
        if (!container) return;
        
        const html = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Credits</th>
                        <th>Plan</th>
                        <th>Last Active</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>
                                <div>
                                    <strong>${user.name || 'No name'}</strong><br>
                                    <small class="text-muted">${user.email}</small>
                                </div>
                            </td>
                            <td>
                                <span class="badge bg-primary">${user.credits}</span>
                            </td>
                            <td>
                                <span class="badge bg-${this.getPlanColor(user.subscription_plan)}">
                                    ${user.subscription_plan}
                                </span>
                            </td>
                            <td>
                                <small>${this.formatDate(user.last_login || user.created_at)}</small>
                            </td>
                            <td>
                                <div class="btn-group btn-group-sm">
                                    <button class="btn btn-success" onclick="adminManager.showCreditDialog(${user.id}, '${user.email}')">
                                        <i class="fas fa-coins"></i> Credits
                                    </button>
                                    <button class="btn btn-primary" onclick="adminManager.showUserDetails(${user.id})">
                                        <i class="fas fa-info-circle"></i> Details
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        container.innerHTML = html;
    }
    
    getPlanColor(plan) {
        const colors = {
            'trial': 'secondary',
            'basic': 'info',
            'pro': 'primary',
            'ultra': 'danger'
        };
        return colors[plan] || 'secondary';
    }
    
    formatDate(dateStr) {
        if (!dateStr) return 'Never';
        const date = new Date(dateStr);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
    
    async showCreditDialog(userId, userEmail) {
        const action = await this.app.showPrompt(`
            <div class="credit-dialog">
                <h5>Manage Credits for ${userEmail}</h5>
                <div class="form-group mt-3">
                    <label>Action:</label>
                    <select class="form-select" id="credit-action">
                        <option value="add">Add Credits</option>
                        <option value="subtract">Subtract Credits</option>
                    </select>
                </div>
                <div class="form-group mt-3">
                    <label>Amount:</label>
                    <input type="number" class="form-control" id="credit-amount" min="1" value="50">
                </div>
            </div>
        `, 'Update Credits');
        
        if (action) {
            const creditAction = document.getElementById('credit-action').value;
            const amount = parseInt(document.getElementById('credit-amount').value);
            
            if (amount > 0) {
                await this.updateUserCredits(userId, creditAction, amount);
            }
        }
    }
    
    async updateUserCredits(userId, action, amount) {
        try {
            const response = await fetch(`/api/admin/user/${userId}/credits`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.app.getCSRFToken()
                },
                body: JSON.stringify({ action, amount })
            });
            
            if (!response.ok) throw new Error('Failed to update credits');
            
            const data = await response.json();
            this.app.showSuccess(data.message);
            
            // Reload users
            this.loadUsers();
        } catch (error) {
            console.error('Error updating credits:', error);
            this.app.showError('Failed to update credits');
        }
    }
}

// Sign-in Bonus Handler
class SignInBonusHandler {
    constructor(app) {
        this.app = app;
        this.init();
    }
    
    async init() {
        // Check if user is eligible for sign-in bonus
        const userInfo = await this.app.getUserInfo();
        if (userInfo?.user && !userInfo.user.signin_bonus_claimed) {
            this.showSignInBonusBanner();
        }
    }
    
    showSignInBonusBanner() {
        // Create banner
        const banner = document.createElement('div');
        banner.className = 'signin-bonus-banner';
        banner.innerHTML = `
            <i class="fas fa-gift"></i>
            Welcome! Sign in to receive 50 FREE credits!
            <button class="btn btn-sm btn-light ms-3" onclick="signInBonusHandler.claimBonus()">
                Claim Now
            </button>
        `;
        
        // Insert after navbar
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.parentNode.insertBefore(banner, navbar.nextSibling);
        }
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            banner.style.animation = 'slideUp 0.3s ease-out forwards';
            setTimeout(() => banner.remove(), 300);
        }, 10000);
    }
    
    async claimBonus() {
        try {
            const response = await fetch('/api/claim-signin-bonus', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.app.getCSRFToken()
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to claim bonus');
            }
            
            const data = await response.json();
            this.app.showSuccess(data.message);
            
            // Update credits display
            this.app.updateCreditsDisplay(data.new_credits);
            
            // Remove banner
            const banner = document.querySelector('.signin-bonus-banner');
            if (banner) banner.remove();
            
        } catch (error) {
            console.error('Error claiming bonus:', error);
            this.app.showError(error.message);
        }
    }
}

// Google Avatar Color Helper
function getGoogleAvatarColor(initials) {
    // Simple hash function to consistently assign colors
    const colors = ['blue', 'red', 'yellow', 'green'];
    let hash = 0;
    for (let i = 0; i < initials.length; i++) {
        hash += initials.charCodeAt(i);
    }
    return colors[hash % colors.length];
}

// Theme Fix
function fixThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    if (themeToggle && themeIcon) {
        // Remove any existing listeners
        const newToggle = themeToggle.cloneNode(true);
        themeToggle.parentNode.replaceChild(newToggle, themeToggle);
        
        // Add working listener
        newToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update icon
            const icon = document.getElementById('theme-icon');
            if (icon) {
                icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
            
            // Show feedback
            if (window.mediaScraperApp) {
                window.mediaScraperApp.showSuccess(`Switched to ${newTheme} theme`);
            }
        });
    }
}

// Assets Display Fix
function fixAssetsDisplay() {
    const originalLoadAssets = window.mediaScraperApp?.modules?.assetManager?.loadAssets;
    
    if (originalLoadAssets) {
        window.mediaScraperApp.modules.assetManager.loadAssets = async function(filter = 'all') {
            // Call original method
            await originalLoadAssets.call(this, filter);
            
            // Ensure videos and images are properly displayed
            const assets = document.querySelectorAll('.asset-item');
            assets.forEach(asset => {
                const isVideo = asset.dataset.type === 'video';
                if (isVideo) {
                    // Ensure video thumbnails are visible
                    const video = asset.querySelector('video');
                    if (video) {
                        video.setAttribute('controls', '');
                        video.setAttribute('preload', 'metadata');
                    }
                }
            });
        };
    }
}

// AI Assistant Dialog Fix
function fixAIAssistant() {
    // Check if AI assistant is properly initialized
    const toggleBtn = document.getElementById('ai-assistant-toggle');
    const chatWindow = document.getElementById('ai-chat-window');
    
    if (toggleBtn && chatWindow) {
        // Check if Enhanced AI Assistant is loaded
        if (window.enhancedAIAssistant) {
            console.log('✅ Enhanced AI Assistant already initialized');
            return;
        }
        
        // Fallback simple toggle if Enhanced AI Assistant isn't loaded
        if (!toggleBtn.onclick && !toggleBtn.hasAttribute('data-click-handler')) {
            toggleBtn.setAttribute('data-click-handler', 'true');
            toggleBtn.addEventListener('click', function() {
                if (chatWindow.style.display === 'none' || !chatWindow.style.display) {
                    chatWindow.style.display = 'flex';
                    // Focus input
                    const input = document.getElementById('ai-chat-input');
                    if (input) {
                        setTimeout(() => input.focus(), 100);
                    }
                    console.log('✅ AI Assistant opened (fallback)');
                } else {
                    chatWindow.style.display = 'none';
                    console.log('✅ AI Assistant closed (fallback)');
                }
            });
            console.log('✅ AI Assistant fallback toggle initialized');
        }
    } else {
        console.log('⚠️ AI Assistant elements not found:', {
            toggleBtn: !!toggleBtn,
            chatWindow: !!chatWindow
        });
    }
}

// Download Credit Usage
function setupCreditUsage() {
    // Override search start to check credits
    const originalStartSearch = window.mediaScraperApp?.startComprehensiveSearch;
    
    if (originalStartSearch) {
        window.mediaScraperApp.startComprehensiveSearch = async function(...args) {
            // Check if user has credits
            const userInfo = await this.getUserInfo();
            if (userInfo?.user && userInfo.user.credits <= 0 && !userInfo.user.is_subscribed) {
                this.showError('You have no credits remaining. Please upgrade to continue.');
                return;
            }
            
            // Call original method
            const result = await originalStartSearch.apply(this, args);
            
            // Update credits display after search
            if (result && userInfo?.user) {
                setTimeout(() => this.updateCreditsDisplay(), 2000);
            }
            
            return result;
        };
    }
}

// Initialize all updates when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Wait for main app
    function initializeUpdates() {
        if (window.mediaScraperApp) {
            // Initialize modules
            window.adminManager = new AdminManager(window.mediaScraperApp);
            window.signInBonusHandler = new SignInBonusHandler(window.mediaScraperApp);
            
            // Apply fixes
            fixThemeToggle();
            fixAssetsDisplay();
            fixAIAssistant();
            setupCreditUsage();
            
            // Update Google avatar colors
            const avatarBadge = document.querySelector('.user-avatar-badge');
            if (avatarBadge) {
                const initials = avatarBadge.textContent.trim();
                const color = getGoogleAvatarColor(initials);
                avatarBadge.setAttribute('data-color', color);
                console.log('✅ Avatar badge color set to:', color, 'for initials:', initials);
                
                // Also add a class for additional styling
                avatarBadge.classList.add('google-colors-applied');
            } else {
                console.log('⚠️ Avatar badge element not found');
            }
            
            console.log('✅ App updates initialized');
        } else {
            setTimeout(initializeUpdates, 100);
        }
    }
    
    initializeUpdates();
});

// Add helper methods to main app
if (window.mediaScraperApp) {
    // Get user info
    window.mediaScraperApp.getUserInfo = async function() {
        try {
            const response = await fetch('/api/user/info', {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.error('Error getting user info:', error);
            return null;
        }
    };
    
    // Update credits display
    window.mediaScraperApp.updateCreditsDisplay = function(credits) {
        const elements = document.querySelectorAll('#credits-count, #user-credits-count, .credits-count');
        elements.forEach(el => {
            if (el) el.textContent = credits || '0';
        });
    };
    
    // Show prompt dialog
    window.mediaScraperApp.showPrompt = function(html, title = 'Input Required') {
        return new Promise((resolve) => {
            // Create modal
            const modal = document.createElement('div');
            modal.className = 'modal fade show';
            modal.style.display = 'block';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${html}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="modal-confirm">Confirm</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Handle confirm
            modal.querySelector('#modal-confirm').addEventListener('click', () => {
                resolve(true);
                modal.remove();
            });
            
            // Handle cancel
            modal.querySelectorAll('[data-bs-dismiss="modal"]').forEach(btn => {
                btn.addEventListener('click', () => {
                    resolve(false);
                    modal.remove();
                });
            });
        });
    };
}
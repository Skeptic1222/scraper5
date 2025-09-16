/**
 * ============================================================================
 * AI ASSISTANT MODULE - Integration Bridge
 * ============================================================================
 * 
 * This module ensures the AI Assistant toggle button works properly
 * The main AI Assistant implementation is in the HTML component
 */

class AIAssistantModule {
    constructor(app) {
        this.app = app;
        this.isInitialized = false;
    }

    /**
     * Initialize the AI assistant module
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🔗 Initializing AI Assistant Module Bridge...');
        
        // Wait for the main AI assistant to be available
        this.waitForAIAssistant();
        
        this.isInitialized = true;
        console.log('✅ AI Assistant Module Bridge initialized');
    }

    /**
     * Wait for the main AI assistant to be initialized
     */
    waitForAIAssistant() {
        let attempts = 0;
        const maxAttempts = 30; // 15 seconds total
        
        const checkInterval = setInterval(() => {
            attempts++;
            const toggleButton = document.getElementById('ai-assistant-toggle');
            const aiAssistant = window.enhancedAIAssistant;
            
            console.log(`🔍 AI Assistant check attempt ${attempts}: Button=${!!toggleButton}, Assistant=${!!aiAssistant}`);
            
            if (toggleButton && aiAssistant) {
                console.log('🤖 AI Assistant detected and linked');
                
                // Add additional event listeners if needed
                this.setupAdditionalFeatures();
                
                clearInterval(checkInterval);
                return;
            }
            
            // If we have the button but not the assistant, try to help initialization
            if (toggleButton && !aiAssistant && attempts > 10) {
                console.log('🔧 Attempting to trigger AI assistant initialization...');
                
                // Try to call the global initialization function if it exists
                if (typeof initializeAIAssistant === 'function') {
                    try {
                        initializeAIAssistant();
                    } catch (error) {
                        console.warn('🔧 Manual initialization call failed:', error);
                    }
                }
            }
            
            // Clear interval after max attempts but ensure fallback functionality
            if (attempts >= maxAttempts) {
                console.warn('⚠️ AI Assistant initialization timeout - ensuring fallback functionality');
                console.log('Available elements:', {
                    toggleButton: !!document.getElementById('ai-assistant-toggle'),
                    chatWindow: !!document.getElementById('ai-chat-window'),
                    mediaScraperApp: !!window.mediaScraperApp,
                    enhancedAIAssistant: !!window.enhancedAIAssistant
                });
                
                // Ensure we have fallback functionality
                this.setupAdditionalFeatures();
                
                clearInterval(checkInterval);
            }
        }, 500);
    }
    
    /**
     * Manually initialize AI assistant if automatic initialization fails
     */
    initializeAIAssistantManually() {
        try {
            // Check if the EnhancedAIAssistant class is available in the global scope
            if (typeof EnhancedAIAssistant !== 'undefined' && window.mediaScraperApp) {
                console.log('🔧 Manual initialization of AI Assistant...');
                window.enhancedAIAssistant = new EnhancedAIAssistant(window.mediaScraperApp);
                console.log('✅ AI Assistant manually initialized');
            } else {
                console.warn('⚠️ EnhancedAIAssistant class not found or mediaScraperApp not ready');
            }
        } catch (error) {
            console.error('❌ Manual AI Assistant initialization failed:', error);
        }
    }

    /**
     * Setup additional features for the AI assistant
     */
    setupAdditionalFeatures() {
        // Add theme-aware styling updates
        document.addEventListener('theme-changed', () => {
            this.updateAIAssistantTheme();
        });
        
        // Add keyboard shortcut for AI assistant
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + A to toggle AI assistant
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'A') {
                e.preventDefault();
                this.toggleAIAssistant();
            }
        });
        
        // Add fallback toggle functionality
        this.addFallbackToggle();
    }
    
    /**
     * Add fallback toggle functionality if main AI assistant fails
     */
    addFallbackToggle() {
        const toggleButton = document.getElementById('ai-assistant-toggle');
        const chatWindow = document.getElementById('ai-chat-window');
        
        if (toggleButton && chatWindow) {
            // Add simple toggle functionality as backup
            const fallbackToggle = () => {
                console.log('🔘 AI Assistant toggle clicked (with fallback)');
                
                if (window.enhancedAIAssistant && window.enhancedAIAssistant.toggle) {
                    // Use main AI assistant if available
                    window.enhancedAIAssistant.toggle();
                } else {
                    // Use simple fallback toggle
                    const isVisible = chatWindow.style.display !== 'none';
                    
                    if (isVisible) {
                        chatWindow.style.display = 'none';
                        console.log('🤖 AI Assistant closed (fallback)');
                    } else {
                        chatWindow.style.display = 'flex';
                        console.log('🤖 AI Assistant opened (fallback)');
                        
                        // Focus input if available
                        const chatInput = document.getElementById('ai-chat-input');
                        if (chatInput) {
                            setTimeout(() => chatInput.focus(), 100);
                        }
                    }
                }
            };
            
            // Add event listener (don't remove existing ones)
            toggleButton.addEventListener('click', fallbackToggle);
            
            console.log('✅ Fallback toggle functionality added');
        } else {
            console.warn('⚠️ Could not add fallback toggle - missing elements');
        }
    }

    /**
     * Toggle the AI assistant
     */
    toggleAIAssistant() {
        const toggleButton = document.getElementById('ai-assistant-toggle');
        if (toggleButton) {
            toggleButton.click();
        }
    }

    /**
     * Update AI assistant theme
     */
    updateAIAssistantTheme() {
        const theme = document.documentElement.getAttribute('data-theme') || 'light';
        console.log(`🎨 AI Assistant theme updated to: ${theme}`);
        
        // The CSS handles theme switching automatically via data-theme attribute
        // No additional JavaScript needed for styling
    }

    /**
     * Show AI assistant if it's hidden
     */
    showAIAssistant() {
        const aiAssistant = window.enhancedAIAssistant;
        if (aiAssistant && !aiAssistant.isOpen) {
            aiAssistant.open();
        }
    }

    /**
     * Hide AI assistant if it's open
     */
    hideAIAssistant() {
        const aiAssistant = window.enhancedAIAssistant;
        if (aiAssistant && aiAssistant.isOpen) {
            aiAssistant.close();
        }
    }

    /**
     * Send a message to the AI assistant programmatically
     */
    sendMessage(message) {
        const aiAssistant = window.enhancedAIAssistant;
        if (aiAssistant) {
            // Show the assistant first
            this.showAIAssistant();
            
            // Wait a moment for it to open, then set the message
            setTimeout(() => {
                const chatInput = document.getElementById('ai-chat-input');
                if (chatInput) {
                    chatInput.value = message;
                    chatInput.dispatchEvent(new Event('input'));
                }
            }, 300);
        }
    }
}

// Export globally
window.AIAssistantModule = AIAssistantModule;
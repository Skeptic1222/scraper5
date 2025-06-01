/**
 * ============================================================================
 * ENHANCED AI ASSISTANT - GPT-4 Powered
 * ============================================================================
 * 
 * Intelligent search term generation and customer service assistant
 */

class EnhancedAIAssistant {
    constructor(app) {
        this.app = app;
        this.apiKey = localStorage.getItem('openai_api_key') || '';
        this.conversationHistory = [];
        this.isInitialized = false;
        this.isTyping = false;
        
        // System prompts for different use cases
        this.systemPrompts = {
            searchAssistant: `You are an AI assistant specialized in helping users generate effective search terms for a media scraping platform. Your role is to:

1. SEARCH TERM OPTIMIZATION:
   - Analyze user queries and suggest better, more specific search terms
   - Suggest alternative keywords that might yield better results
   - Help avoid overly broad terms that cause too many false positives
   - Recommend trending or popular variations of search terms

2. PLATFORM GUIDANCE:
   - Help users understand which content sources work best for different types of content
   - Suggest optimal search strategies for images vs videos
   - Provide tips for better search results

3. TROUBLESHOOTING:
   - Help diagnose common search issues
   - Suggest solutions for download problems
   - Guide users through feature usage

Always be concise, helpful, and focused on improving search effectiveness. If asked about search terms, provide 3-5 specific, actionable suggestions.`,

            customerService: `You are a customer service AI for Enhanced Media Scraper, a comprehensive media downloading platform. You can help with:

PLATFORM FEATURES:
- 78+ content sources (social media, search engines, stock photos, etc.)
- Image and video downloading capabilities
- Database-driven asset management
- User account and credit system
- Safe search and content filtering

SUBSCRIPTION PLANS:
- Free Plan: Basic features, limited sources, 50 downloads/month
- Premium Plan: $9.99/month, all sources, unlimited downloads, priority support
- Enterprise Plan: $29.99/month, API access, bulk features, dedicated support

COMMON ISSUES:
- Downloads not working: Usually network or source-specific issues
- Assets not showing: Database sync or UI refresh needed
- Source access: Some sources require Premium subscription
- Account limits: Free users have monthly download limits

Always be helpful, professional, and provide accurate information about features and pricing.`
        };
        
        this.currentMode = 'general'; // general, search, customerService
    }

    /**
     * Initialize the AI assistant
     */
    async init() {
        if (this.isInitialized) return;
        
        console.log('🤖 Initializing Enhanced AI Assistant...');
        
        this.setupEventListeners();
        this.loadConversationHistory();
        this.checkApiKey();
        this.showWelcomeMessage();
        
        this.isInitialized = true;
        console.log('✅ Enhanced AI Assistant initialized');
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Chat input handling
        const chatInput = document.getElementById('ai-chat-input');
        const sendButton = document.getElementById('ai-send-button');
        const clearButton = document.getElementById('ai-clear-chat');
        const apiKeyInput = document.getElementById('ai-api-key');

        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });

            chatInput.addEventListener('input', () => {
                this.updateSendButtonState();
            });
        }

        if (sendButton) {
            sendButton.addEventListener('click', () => {
                this.handleSendMessage();
            });
        }

        if (clearButton) {
            clearButton.addEventListener('click', () => {
                this.clearConversation();
            });
        }

        if (apiKeyInput) {
            apiKeyInput.value = this.apiKey;
            apiKeyInput.addEventListener('input', (e) => {
                this.apiKey = e.target.value.trim();
                localStorage.setItem('openai_api_key', this.apiKey);
                this.updateSendButtonState();
                this.toggleApiKeySection();
            });
        }
    }

    /**
     * Check and handle API key
     */
    checkApiKey() {
        const apiKeySection = document.getElementById('ai-api-key-section');
        if (!this.apiKey && apiKeySection) {
            apiKeySection.style.display = 'block';
        }
        this.updateSendButtonState();
    }

    /**
     * Toggle API key section visibility
     */
    toggleApiKeySection() {
        const apiKeySection = document.getElementById('ai-api-key-section');
        if (apiKeySection) {
            apiKeySection.style.display = this.apiKey ? 'none' : 'block';
        }
    }

    /**
     * Update send button state
     */
    updateSendButtonState() {
        const sendButton = document.getElementById('ai-send-button');
        const chatInput = document.getElementById('ai-chat-input');
        
        if (sendButton && chatInput) {
            const hasApiKey = !!this.apiKey;
            const hasMessage = !!chatInput.value.trim();
            sendButton.disabled = !hasApiKey || !hasMessage || this.isTyping;
        }
    }

    /**
     * Show welcome message
     */
    showWelcomeMessage() {
        if (this.conversationHistory.length === 0) {
            this.addMessage('ai', 
                `👋 Hi! I'm your AI assistant for Enhanced Media Scraper. I can help you with:

🔍 **Smart Search Terms** - I'll analyze your queries and suggest better, more specific search terms that reduce false positives

🛠️ **Troubleshooting** - Get help with downloads, sources, and platform features  

💡 **Customer Service** - Questions about subscription plans, features, and account management

What would you like help with today?`, 
                false
            );
        }
    }

    /**
     * Handle sending a message
     */
    async handleSendMessage() {
        const chatInput = document.getElementById('ai-chat-input');
        if (!chatInput || !chatInput.value.trim() || !this.apiKey) return;

        const message = chatInput.value.trim();
        chatInput.value = '';
        chatInput.style.height = 'auto';
        this.updateSendButtonState();

        // Add user message
        this.addMessage('user', message);

        // Determine conversation mode based on message content
        this.analyzeMessageIntent(message);

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Get AI response
            const response = await this.getAIResponse(message);
            this.hideTypingIndicator();
            this.addMessage('ai', response);
            
            // Save conversation
            this.saveConversationHistory();
            
        } catch (error) {
            this.hideTypingIndicator();
            console.error('AI Assistant error:', error);
            this.addMessage('ai', 
                '❌ Sorry, I encountered an error. Please check your API key and try again. ' +
                'If the problem persists, it might be a temporary service issue.'
            );
        }
    }

    /**
     * Analyze message intent to determine conversation mode
     */
    analyzeMessageIntent(message) {
        const searchKeywords = ['search', 'find', 'look for', 'download', 'terms', 'keywords', 'query'];
        const serviceKeywords = ['subscription', 'plan', 'pricing', 'account', 'features', 'upgrade', 'credit'];
        
        const lowerMessage = message.toLowerCase();
        
        if (searchKeywords.some(keyword => lowerMessage.includes(keyword))) {
            this.currentMode = 'search';
        } else if (serviceKeywords.some(keyword => lowerMessage.includes(keyword))) {
            this.currentMode = 'customerService';
        } else {
            this.currentMode = 'general';
        }
    }

    /**
     * Get AI response from OpenAI API
     */
    async getAIResponse(message) {
        const systemPrompt = this.getSystemPrompt();
        
        // Prepare conversation context
        const messages = [
            { role: 'system', content: systemPrompt },
            ...this.conversationHistory.slice(-10).map(msg => ({
                role: msg.type === 'user' ? 'user' : 'assistant',
                content: msg.content
            })),
            { role: 'user', content: message }
        ];

        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-4',
                messages: messages,
                max_tokens: 500,
                temperature: 0.7,
                presence_penalty: 0.1,
                frequency_penalty: 0.1
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error?.message || `HTTP ${response.status}`);
        }

        const data = await response.json();
        return data.choices[0]?.message?.content || 'No response generated.';
    }

    /**
     * Get appropriate system prompt based on current mode
     */
    getSystemPrompt() {
        switch (this.currentMode) {
            case 'search':
                return this.systemPrompts.searchAssistant;
            case 'customerService':
                return this.systemPrompts.customerService;
            default:
                return `You are a helpful AI assistant for Enhanced Media Scraper. Provide concise, accurate help with search optimization, troubleshooting, and platform features. Be friendly and professional.`;
        }
    }

    /**
     * Add message to chat
     */
    addMessage(type, content, timestamp = true) {
        const messagesContainer = document.getElementById('ai-chat-messages');
        if (!messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = `chat-message ${type}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = this.formatMessage(content);

        contentDiv.appendChild(messageText);

        if (timestamp) {
            const timestampDiv = document.createElement('div');
            timestampDiv.className = 'message-timestamp';
            timestampDiv.textContent = new Date().toLocaleTimeString();
            contentDiv.appendChild(timestampDiv);
        }

        if (type === 'user') {
            messageElement.appendChild(contentDiv);
            messageElement.appendChild(avatar);
        } else {
            messageElement.appendChild(avatar);
            messageElement.appendChild(contentDiv);
        }

        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Add to conversation history
        this.conversationHistory.push({
            type,
            content,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Format message content (basic markdown support)
     */
    formatMessage(content) {
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/```(.*?)```/gs, '<code>$1</code>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        this.isTyping = true;
        this.updateSendButtonState();
        
        const messagesContainer = document.getElementById('ai-chat-messages');
        if (!messagesContainer) return;

        const typingElement = document.createElement('div');
        typingElement.className = 'chat-message ai-message typing-indicator';
        typingElement.id = 'typing-indicator';
        
        typingElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;

        messagesContainer.appendChild(typingElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        this.isTyping = false;
        this.updateSendButtonState();
        
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            typingElement.remove();
        }
    }

    /**
     * Clear conversation
     */
    clearConversation() {
        if (confirm('Clear conversation history?')) {
            this.conversationHistory = [];
            const messagesContainer = document.getElementById('ai-chat-messages');
            if (messagesContainer) {
                messagesContainer.innerHTML = '';
            }
            localStorage.removeItem('ai_conversation_history');
            this.showWelcomeMessage();
        }
    }

    /**
     * Save conversation history
     */
    saveConversationHistory() {
        try {
            // Keep only last 50 messages to avoid storage bloat
            const historyToSave = this.conversationHistory.slice(-50);
            localStorage.setItem('ai_conversation_history', JSON.stringify(historyToSave));
        } catch (error) {
            console.warn('Failed to save conversation history:', error);
        }
    }

    /**
     * Load conversation history
     */
    loadConversationHistory() {
        try {
            const saved = localStorage.getItem('ai_conversation_history');
            if (saved) {
                this.conversationHistory = JSON.parse(saved);
                
                // Restore conversation in UI
                const messagesContainer = document.getElementById('ai-chat-messages');
                if (messagesContainer && this.conversationHistory.length > 0) {
                    messagesContainer.innerHTML = '';
                    this.conversationHistory.forEach(msg => {
                        this.addMessage(msg.type, msg.content, false);
                    });
                }
            }
        } catch (error) {
            console.warn('Failed to load conversation history:', error);
            this.conversationHistory = [];
        }
    }

    /**
     * Get smart search suggestions for a query
     */
    async getSearchSuggestions(query) {
        if (!this.apiKey) {
            return {
                suggestions: [query],
                explanation: 'API key required for smart suggestions'
            };
        }

        try {
            const response = await this.getAIResponse(
                `Please analyze this search query and provide 3-5 improved search terms that would be more specific and yield better results with fewer false positives: "${query}"\n\nFormat your response as:\n1. [term] - [brief explanation]\n2. [term] - [brief explanation]\netc.`
            );

            return {
                suggestions: this.parseSearchSuggestions(response),
                explanation: response
            };
        } catch (error) {
            console.error('Failed to get search suggestions:', error);
            return {
                suggestions: [query],
                explanation: 'Failed to get AI suggestions'
            };
        }
    }

    /**
     * Parse search suggestions from AI response
     */
    parseSearchSuggestions(response) {
        const suggestions = [];
        const lines = response.split('\n');
        
        for (const line of lines) {
            const match = line.match(/^\d+\.\s*([^-]+)/);
            if (match) {
                suggestions.push(match[1].trim());
            }
        }
        
        return suggestions.length > 0 ? suggestions : [response];
    }

    /**
     * Quick help for specific topics
     */
    showQuickHelp(topic) {
        const helpMessages = {
            search: `🔍 **Search Tips:**
• Use specific keywords instead of generic terms
• Add context like "high quality", "4k", "professional"  
• Try brand names or specific styles
• Use quotes for exact phrases
• Combine multiple related terms`,

            downloads: `📥 **Download Issues:**
• Check your internet connection
• Verify the source is accessible
• Try refreshing the page
• Clear browser cache if needed
• Some sources may require premium access`,

            sources: `📋 **Content Sources:**
• **Free sources:** Bing Images, Imgur, Reddit
• **Premium sources:** Instagram, Pinterest, TikTok
• **Stock photos:** Unsplash, Pexels, Pixabay
• **Adult content:** Requires premium + 18+ verification`,

            account: `👤 **Account & Billing:**
• **Free Plan:** 50 downloads/month, basic sources
• **Premium Plan:** $9.99/month, unlimited downloads
• **Enterprise:** $29.99/month, API access
• Credits refresh monthly on your billing date`
        };

        const message = helpMessages[topic] || 'Topic not found. Ask me anything!';
        this.addMessage('ai', message);
    }
}

// Export globally
window.EnhancedAIAssistant = EnhancedAIAssistant; 
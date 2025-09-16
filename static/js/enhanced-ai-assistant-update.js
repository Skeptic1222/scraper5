/**
 * Enhanced AI Assistant Update - User-Based Access for MAX Subscribers
 * This code should be included after the main AI assistant to add the new functionality
 */

// Override the callEnhancedAI method to support user-based access
if (window.enhancedAIAssistant) {
    const originalCallEnhancedAI = window.enhancedAIAssistant.callEnhancedAI;
    
    window.enhancedAIAssistant.checkAIAccess = async function() {
        try {
            const response = await fetch('/api/ai-assistant/status', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-OpenAI-API-Key': this.apiKey || ''
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                return data;
            }
        } catch (error) {
            console.error('Failed to check AI access:', error);
        }
        
        return {
            has_access: false,
            requires_api_key: true,
            message: 'AI Assistant unavailable'
        };
    };
    
    window.enhancedAIAssistant.callEnhancedAI = async function(userMessage) {
        try {
            // Check access status first
            const accessStatus = await this.checkAIAccess();
            
            // If user doesn't have access, show upgrade prompt
            if (!accessStatus.has_access) {
                if (accessStatus.requires_upgrade) {
                    return `🔒 ${accessStatus.message}\n\n` +
                           `🎯 Upgrade to MAX subscription for unlimited AI assistance without needing an API key!\n` +
                           `<a href="${accessStatus.upgrade_url || '/subscription/plans'}" class="ai-upgrade-link">View Plans</a>\n\n` +
                           `💡 Or provide your own OpenAI API key in settings.`;
                }
                return accessStatus.message || 'AI Assistant requires an API key or MAX subscription.';
            }
            
            // Call the AI assistant API
            const response = await fetch('/api/ai-assistant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    api_key: this.apiKey, // Send API key if available
                    context: this.userContext
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // If it's a subscription-based access, show a badge
                if (data.access_type === 'subscription') {
                    return `${data.response}\n\n<small class="ai-access-badge">✨ MAX Subscriber AI Access</small>`;
                }
                
                return data.response || data.message || 'I received your message but had trouble generating a response.';
            } else {
                const errorData = await response.json();
                
                // Handle specific error cases
                if (errorData.requires_upgrade) {
                    return `🔒 ${errorData.error}\n\n` +
                           `🎯 Upgrade to MAX subscription for unlimited AI assistance!\n` +
                           `<a href="${errorData.upgrade_url || '/subscription/plans'}" class="ai-upgrade-link">View Plans</a>`;
                }
                
                // Fallback to local AI response
                console.warn('AI API not available, using local responses');
                return await this.getAIResponse(userMessage);
            }
        } catch (error) {
            console.warn('AI API error:', error);
            // Fallback to local AI response
            return await this.getAIResponse(userMessage);
        }
    };
    
    // Update the initialization to show access status
    const originalInit = window.enhancedAIAssistant.init;
    window.enhancedAIAssistant.init = async function() {
        // Call original init
        originalInit.call(this);
        
        // Check and display access status
        try {
            const accessStatus = await this.checkAIAccess();
            const statusElement = document.getElementById('ai-status');
            
            if (statusElement) {
                if (accessStatus.has_access) {
                    if (accessStatus.access_type === 'subscription') {
                        statusElement.textContent = '✨ MAX AI - Ready';
                        statusElement.style.color = '#ffd700';
                    } else {
                        statusElement.textContent = '🔑 API Key - Ready';
                        statusElement.style.color = '#90EE90';
                    }
                } else {
                    statusElement.textContent = '🔒 Upgrade Required';
                    statusElement.style.color = '#ff6b6b';
                }
            }
        } catch (error) {
            console.error('Failed to check AI status:', error);
        }
    };
}

// Add styles for the upgrade link and badge
const style = document.createElement('style');
style.textContent = `
    .ai-upgrade-link {
        display: inline-block;
        margin-top: 8px;
        padding: 6px 16px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-decoration: none;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
        transition: transform 0.2s ease;
    }
    
    .ai-upgrade-link:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .ai-access-badge {
        display: inline-block;
        padding: 2px 8px;
        background: linear-gradient(135deg, #ffd700 0%, #ffed4b 100%);
        color: #333;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-top: 8px;
    }
`;
document.head.appendChild(style);

console.log('✅ Enhanced AI Assistant updated with user-based access support');
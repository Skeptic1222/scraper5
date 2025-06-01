"""
OpenAI API Integration for AI Assistant
Handles AI-powered search optimization and content recommendations
"""

import os
import json
import openai
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from functools import wraps
import logging

# Set up OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Create AI API blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ai_enabled_required(f):
    """Decorator to check if AI features are enabled"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not os.getenv('OPENAI_API_KEY'):
            return jsonify({
                'success': False,
                'error': 'AI features not configured'
            }), 503
        return f(*args, **kwargs)
    return decorated_function

@ai_bp.route('/status')
@login_required
def ai_status():
    """Check if AI services are available"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        available = bool(api_key and len(api_key) > 20)
        
        return jsonify({
            'success': True,
            'available': available,
            'features': {
                'search_optimization': available,
                'chat_assistant': available,
                'content_recommendations': available
            }
        })
    except Exception as e:
        logger.error(f"AI status check failed: {e}")
        return jsonify({
            'success': False,
            'available': False,
            'error': str(e)
        }), 500

@ai_bp.route('/optimize-search', methods=['POST'])
@login_required
@ai_enabled_required
def optimize_search():
    """Optimize search query and recommend sources using AI"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        smart_filters = data.get('smartFilters', {})
        available_sources = data.get('availableSources', [])
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'No search query provided'
            }), 400
        
        # Prepare context for AI
        context = f"""
        You are an expert content discovery assistant. Help optimize this search request:

        User Query: "{query}"
        Smart Filters: {json.dumps(smart_filters)}
        Available Sources: {[s.get('name', '') for s in available_sources if not s.get('locked')]}

        Please provide:
        1. An optimized search query that will yield better results
        2. Recommended sources from the available list that are best for this type of content
        3. Any additional search tips

        Respond in JSON format:
        {{
            "optimizedQuery": "improved query here",
            "recommendedSources": ["source1", "source2"],
            "searchTips": ["tip1", "tip2"],
            "confidence": 0.85
        }}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant specialized in content discovery and search optimization. Always respond with valid JSON."},
                {"role": "user", "content": context}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        try:
            recommendations = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            recommendations = {
                "optimizedQuery": query,
                "recommendedSources": [s.get('name', '') for s in available_sources[:5] if not s.get('locked')],
                "searchTips": ["Try different keywords", "Use specific terms"],
                "confidence": 0.5
            }
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Search optimization failed: {e}")
        return jsonify({
            'success': False,
            'error': 'AI optimization failed',
            'details': str(e)
        }), 500

@ai_bp.route('/optimize-query', methods=['POST'])
@login_required
@ai_enabled_required
def optimize_query():
    """Optimize just the search query using AI"""
    try:
        data = request.get_json()
        original_query = data.get('query', '')
        
        if not original_query:
            return jsonify({
                'success': False,
                'error': 'No query provided'
            }), 400
        
        context = f"""
        Improve this search query to find better content results:
        Original: "{original_query}"
        
        Please:
        1. Make it more specific and effective
        2. Add relevant keywords
        3. Fix any spelling or grammar issues
        4. Optimize for content discovery
        
        Respond with JSON:
        {{
            "optimizedQuery": "improved query",
            "suggestions": ["suggestion1", "suggestion2"],
            "score": 0.85
        }}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at optimizing search queries for content discovery. Always respond with valid JSON."},
                {"role": "user", "content": context}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        try:
            result = json.loads(ai_response)
        except json.JSONDecodeError:
            result = {
                "optimizedQuery": original_query,
                "suggestions": ["Try adding more specific keywords"],
                "score": 0.5
            }
        
        return jsonify({
            'success': True,
            'optimizedQuery': result.get('optimizedQuery', original_query),
            'suggestions': result.get('suggestions', []),
            'score': result.get('score', 0.5)
        })
        
    except Exception as e:
        logger.error(f"Query optimization failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Query optimization failed',
            'details': str(e)
        }), 500

@ai_bp.route('/chat', methods=['POST'])
@login_required
@ai_enabled_required
def ai_chat():
    """Chat with AI assistant for search help"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        history = data.get('history', [])
        context = data.get('context', {})
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        # Build conversation context
        system_prompt = f"""
        You are a helpful AI assistant for a media discovery platform. Help users find content by:
        - Understanding what they're looking for
        - Suggesting better search terms
        - Recommending appropriate content sources
        - Providing tips for better results
        
        Current context:
        - User's current search: "{context.get('currentQuery', 'None')}"
        - Selected sources: {context.get('selectedSources', [])}
        - Smart filters: {context.get('smartFilters', {})}
        
        Be conversational, helpful, and specific. If you suggest changes, explain why.
        """
        
        # Build message history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history
        for entry in history[-5:]:  # Last 5 exchanges
            messages.append({"role": "user", "content": entry.get('user', '')})
            messages.append({"role": "assistant", "content": entry.get('ai', '')})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=800,
            temperature=0.8
        )
        
        ai_reply = response.choices[0].message.content
        
        # Extract any actionable suggestions
        suggestions = None
        if any(keyword in message.lower() for keyword in ['search for', 'find', 'looking for', 'want']):
            # Try to extract search suggestions
            suggestions = extract_search_suggestions(ai_reply, context)
        
        return jsonify({
            'success': True,
            'reply': ai_reply,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"AI chat failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Chat failed',
            'details': str(e)
        }), 500

def extract_search_suggestions(ai_reply, context):
    """Extract actionable suggestions from AI reply"""
    try:
        # Simple extraction of suggestions
        suggestions = {}
        
        # Look for query suggestions in the reply
        reply_lower = ai_reply.lower()
        if 'search for' in reply_lower or 'try searching' in reply_lower:
            # Extract quoted terms as potential queries
            import re
            quotes = re.findall(r'"([^"]*)"', ai_reply)
            if quotes:
                suggestions['query'] = quotes[0]
        
        return suggestions if suggestions else None
        
    except Exception as e:
        logger.error(f"Failed to extract suggestions: {e}")
        return None

@ai_bp.route('/content-recommendations', methods=['POST'])
@login_required
@ai_enabled_required
def content_recommendations():
    """Get AI recommendations for content discovery"""
    try:
        data = request.get_json()
        user_preferences = data.get('preferences', {})
        search_history = data.get('searchHistory', [])
        
        context = f"""
        Based on this user's preferences and search history, recommend content types and sources:
        
        Preferences: {json.dumps(user_preferences)}
        Recent searches: {search_history[-10:]}
        
        Provide recommendations in JSON format:
        {{
            "recommendedCategories": ["category1", "category2"],
            "suggestedQueries": ["query1", "query2"],
            "tips": ["tip1", "tip2"]
        }}
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a content discovery expert. Provide helpful recommendations based on user behavior."},
                {"role": "user", "content": context}
            ],
            max_tokens=600,
            temperature=0.6
        )
        
        ai_response = response.choices[0].message.content
        
        try:
            recommendations = json.loads(ai_response)
        except json.JSONDecodeError:
            recommendations = {
                "recommendedCategories": ["Popular Content"],
                "suggestedQueries": ["trending topics"],
                "tips": ["Try specific keywords for better results"]
            }
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
        
    except Exception as e:
        logger.error(f"Content recommendations failed: {e}")
        return jsonify({
            'success': False,
            'error': 'Recommendations failed',
            'details': str(e)
        }), 500

# Export the blueprint
__all__ = ['ai_bp'] 
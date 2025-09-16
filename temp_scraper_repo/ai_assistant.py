"""
AI Assistant module using OpenAI GPT-4
Handles intelligent search optimization and user assistance
"""

import json
import os
import re
from typing import Any, Dict, List

from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

class AIAssistant:
    """AI Assistant for search optimization and user help"""

    def __init__(self):
        self.system_prompt = """You are an AI assistant for a media scraping application.
Your role is to help users optimize their searches, recommend the best sources,
and provide guidance on using the application effectively.

Key capabilities:
- Optimize search queries for better results
- Recommend appropriate sources based on content type
- Filter out low-quality or fake content
- Provide usage tips and best practices
- Help with subscription and feature questions

Always be helpful, concise, and focus on getting users the best results."""

    def generate_response(self, message: str, context: Dict[str, Any],
                         history: List[Dict[str, str]], user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI response using OpenAI GPT-4"""
        try:
            # Build conversation history
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add recent history
            for hist in history[-5:]:  # Last 5 messages
                role = "user" if hist.get("sender") == "user" else "assistant"
                messages.append({"role": role, "content": hist.get("message", "")})

            # Add current message
            messages.append({"role": "user", "content": message})

            # Add context about user and current search
            context_prompt = f"\nUser context: {json.dumps(user_info, indent=2)}\nSearch context: {json.dumps(context, indent=2)}"
            messages.append({"role": "system", "content": context_prompt})

            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            ai_message = response.choices[0].message.content

            # Parse response for special commands
            return self._parse_ai_response(ai_message, message, context)

        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback to rule-based response
            return self._generate_fallback_response(message, context, user_info)

    def optimize_query(self, query: str, search_type: str, filters: Dict[str, bool]) -> Dict[str, Any]:
        """Optimize search query using AI"""
        try:
            prompt = f"""Optimize this search query for better results:
Query: {query}
Search type: {search_type}
Filters: {json.dumps(filters)}

Provide:
1. An optimized query that will yield better results
2. Explanation of changes
3. Additional search tips

Format response as JSON with keys: optimized_query, explanation, tips"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a search optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )

            # Parse JSON response
            try:
                result = json.loads(response.choices[0].message.content)
                return {
                    'query': result.get('optimized_query', query),
                    'score': 85,
                    'suggestions': result.get('tips', []),
                    'explanation': result.get('explanation', 'Query optimized for better results')
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'query': query + " HD high quality -fake -repost",
                    'score': 75,
                    'suggestions': ['Added quality filters', 'Excluded common spam terms'],
                    'explanation': 'Basic optimization applied'
                }

        except Exception as e:
            print(f"Query optimization error: {e}")
            return self._basic_query_optimization(query, filters)

    def _parse_ai_response(self, ai_message: str, user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        response = {
            'message': ai_message,
            'suggestions': [],
            'sources': [],
            'optimized_query': None,
            'optimization_score': 0,
            'actions': []
        }

        # Extract search query if mentioned
        query_match = re.search(r'search for[:\s]*"([^"]+)"', ai_message, re.IGNORECASE)
        if query_match:
            response['optimized_query'] = query_match.group(1)
            response['optimization_score'] = 85

        # Extract source recommendations
        sources_match = re.search(r'sources?[:\s]*([\w\s,]+)', ai_message, re.IGNORECASE)
        if sources_match:
            sources = [s.strip() for s in sources_match.group(1).split(',')]
            response['sources'] = sources[:5]  # Limit to 5 sources

        # Add contextual actions
        if 'search' in user_message.lower():
            response['actions'].append({
                'label': 'Apply Suggestions',
                'icon': 'fa-magic',
                'onclick': 'optimizeSearchQuery()'
            })

        if 'subscription' in user_message.lower() or 'upgrade' in user_message.lower():
            response['actions'].append({
                'label': 'View Plans',
                'icon': 'fa-crown',
                'onclick': "window.location.href='/subscription/plans'"
            })

        return response

    def _generate_fallback_response(self, message: str, context: Dict[str, Any],
                                   user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response without OpenAI"""
        message_lower = message.lower()

        # Search-related queries
        if any(word in message_lower for word in ['search', 'find', 'download']):
            return {
                'message': "I'll help you optimize your search. Try adding specific keywords and using filters to exclude low-quality content. What type of content are you looking for?",
                'suggestions': [
                    "Be specific with keywords",
                    "Use filters to exclude fakes",
                    "Try multiple sources"
                ],
                'optimization_score': 70
            }

        # Help queries
        elif any(word in message_lower for word in ['help', 'how to', 'guide']):
            return {
                'message': "I can help you with:\n• Search optimization\n• Source selection\n• Download management\n• Account settings\n\nWhat would you like help with?",
                'suggestions': ["Ask about specific features", "Learn search tips"],
                'actions': []
            }

        # Default
        else:
            return {
                'message': "I'm here to help you get the best search results. Feel free to ask about search tips, source recommendations, or any features!",
                'suggestions': ["Try asking about search optimization"],
                'actions': []
            }

    def _basic_query_optimization(self, query: str, filters: Dict[str, bool]) -> Dict[str, Any]:
        """Basic query optimization without AI"""
        optimized = query
        suggestions = []

        # Apply filter-based optimizations
        if filters.get('exclude_fakes'):
            optimized += ' -fake -repost -stolen'
            suggestions.append('Excluding fake content')

        if filters.get('high_quality'):
            optimized += ' HD HQ "high quality"'
            suggestions.append('Filtering for high quality')

        if filters.get('verified_sources'):
            optimized += ' verified official'
            suggestions.append('Prioritizing verified sources')

        if filters.get('recent_only'):
            optimized += ' 2024 recent new'
            suggestions.append('Focusing on recent content')

        return {
            'query': optimized.strip(),
            'score': 70,
            'suggestions': suggestions,
            'explanation': 'Basic optimization applied based on your filters'
        }

# Create singleton instance
ai_assistant = AIAssistant()

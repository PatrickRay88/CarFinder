"""Conversational agent for car shopping assistance."""
from typing import Dict, List, Any, Optional
import json
import requests
from dataclasses import dataclass

@dataclass
class ConversationState:
    """State of the conversation."""
    user_preferences: Dict[str, Any]
    clarified_needs: Dict[str, Any]
    search_performed: bool
    recommendations_shown: bool
    conversation_history: List[Dict[str, str]]

class ConversationAgent:
    """AI agent for conversational car shopping."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ollama_host = config.get('ollama_host', 'http://localhost:11434')
        self.model_name = config.get('ollama_model', 'llama3.1')
    
    def process_message(self, user_message: str, conversation_state: ConversationState) -> Dict[str, Any]:
        """Process user message and return response with actions."""
        
        # Add user message to history
        conversation_state.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Determine conversation phase and generate appropriate response
        response = self._generate_response(user_message, conversation_state)
        
        # Add AI response to history
        conversation_state.conversation_history.append({
            'role': 'assistant', 
            'content': response['message']
        })
        
        return response
    
    def _generate_response(self, user_message: str, state: ConversationState) -> Dict[str, Any]:
        """Generate contextual response based on conversation state."""
        
        # Create system prompt based on conversation phase
        system_prompt = self._create_system_prompt(state)
        
        # Prepare conversation context
        context = self._prepare_context(user_message, state)
        
        # Call Ollama for response generation
        try:
            ai_response = self._call_ollama(system_prompt, context)
            parsed_response = self._parse_ai_response(ai_response, state)
            return parsed_response
        except Exception as e:
            # Fallback to rule-based response
            return self._fallback_response(user_message, state)
    
    def _create_system_prompt(self, state: ConversationState) -> str:
        """Create system prompt based on conversation phase."""
        
        base_prompt = """
You are a helpful car shopping assistant. Your goal is to understand the user's car needs and preferences, then help them find the perfect vehicle.

Key areas to explore:
- Budget range
- Vehicle type (sedan, SUV, truck, etc.)
- Primary use (commuting, family, adventure, etc.)
- Fuel efficiency preferences
- Must-have features
- Safety priorities
- Brand preferences or concerns

Always be conversational, friendly, and ask clarifying questions to better understand their needs.
"""
        
        if not state.user_preferences:
            base_prompt += "\nThe user is just starting - help them think through what kind of car would work best for them."
        elif not state.clarified_needs:
            base_prompt += "\nYou have some initial preferences. Now dig deeper into their specific needs and priorities."
        elif not state.search_performed:
            base_prompt += "\nYou understand their needs well. Suggest it's time to search for vehicles matching their criteria."
        else:
            base_prompt += "\nYou've shown them results. Help them understand the recommendations and next steps."
        
        return base_prompt
    
    def _prepare_context(self, user_message: str, state: ConversationState) -> str:
        """Prepare conversation context for the AI."""
        
        context_parts = []
        
        # Add conversation history (last 6 messages to stay within limits)
        history = state.conversation_history[-6:] if len(state.conversation_history) > 6 else state.conversation_history
        
        if history:
            context_parts.append("Previous conversation:")
            for msg in history:
                role = "User" if msg['role'] == 'user' else "Assistant"
                context_parts.append(f"{role}: {msg['content']}")
        
        # Add current preferences
        if state.user_preferences:
            context_parts.append(f"\nCurrent user preferences: {json.dumps(state.user_preferences, indent=2)}")
        
        # Add current message
        context_parts.append(f"\nUser's current message: {user_message}")
        
        # Add instructions
        context_parts.append("\nProvide a helpful response and indicate if you need to perform any actions (search, clarify, recommend).")
        
        return "\n".join(context_parts)
    
    def _call_ollama(self, system_prompt: str, context: str) -> str:
        """Call Ollama API for response generation."""
        
        prompt = f"System: {system_prompt}\n\n{context}\n\nAssistant:"
        
        response = requests.post(
            f"{self.ollama_host}/api/generate",
            json={
                'model': self.model_name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': 500
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    
    def _parse_ai_response(self, ai_response: str, state: ConversationState) -> Dict[str, Any]:
        """Parse AI response and extract actions."""
        
        # For now, simple parsing - in production could be more sophisticated
        response = {
            'message': ai_response.strip(),
            'actions': [],
            'extracted_preferences': {}
        }
        
        # Simple keyword extraction for preferences
        message_lower = ai_response.lower()
        
        # Extract budget mentions
        import re
        budget_matches = re.findall(r'\$([0-9,]+)', ai_response)
        if budget_matches:
            try:
                budget = int(budget_matches[0].replace(',', ''))
                response['extracted_preferences']['budget_max'] = budget
            except ValueError:
                pass
        
        # Extract vehicle type mentions
        vehicle_types = ['sedan', 'suv', 'truck', 'coupe', 'hatchback', 'wagon']
        for vtype in vehicle_types:
            if vtype in message_lower:
                response['extracted_preferences']['vehicle_type'] = vtype
                break
        
        # Determine if search should be triggered
        search_triggers = ['search', 'find', 'show me', 'look for', 'ready to see']
        if any(trigger in message_lower for trigger in search_triggers):
            if state.user_preferences:
                response['actions'].append('trigger_search')
        
        return response
    
    def _fallback_response(self, user_message: str, state: ConversationState) -> Dict[str, Any]:
        """Fallback response when Ollama is unavailable."""
        
        message_lower = user_message.lower()
        
        # Budget-related responses
        if any(word in message_lower for word in ['budget', 'price', 'cost', 'afford']):
            return {
                'message': "Great! Understanding your budget is important. What's the maximum you'd like to spend on a car? This helps me find options that won't strain your finances.",
                'actions': [],
                'extracted_preferences': {}
            }
        
        # Vehicle type responses
        elif any(word in message_lower for word in ['suv', 'sedan', 'truck', 'car type']):
            return {
                'message': "Perfect! Vehicle type is a key decision. Are you looking for something practical for daily commuting, spacious for family needs, or maybe something for outdoor adventures?",
                'actions': [],
                'extracted_preferences': {}
            }
        
        # Fuel efficiency
        elif any(word in message_lower for word in ['gas', 'fuel', 'mpg', 'economy', 'efficient']):
            return {
                'message': "Fuel efficiency is definitely worth considering, especially with gas prices! How important is getting good gas mileage to you? Are you interested in hybrid or electric options?",
                'actions': [],
                'extracted_preferences': {}
            }
        
        # Features
        elif any(word in message_lower for word in ['features', 'options', 'tech', 'safety']):
            return {
                'message': "Features can really make a difference in your daily driving experience! What features are most important to you? Things like backup cameras, heated seats, navigation, or advanced safety features?",
                'actions': [],
                'extracted_preferences': {}
            }
        
        # Search request
        elif any(word in message_lower for word in ['search', 'find', 'show', 'ready', 'look']):
            if state.user_preferences:
                return {
                    'message': "Absolutely! Let me search for vehicles that match your preferences. I'll find options that fit your criteria and rank them based on what matters most to you.",
                    'actions': ['trigger_search'],
                    'extracted_preferences': {}
                }
            else:
                return {
                    'message': "I'd love to help you search! First, let me understand what you're looking for. What's your budget range and what type of vehicle interests you most?",
                    'actions': [],
                    'extracted_preferences': {}
                }
        
        # Generic response
        else:
            if not state.user_preferences:
                return {
                    'message': "Hi! I'm here to help you find the perfect car. To get started, could you tell me about your budget and what kind of driving you do most? For example, daily commuting, weekend trips, or family hauling?",
                    'actions': [],
                    'extracted_preferences': {}
                }
            else:
                return {
                    'message': "I understand! Based on what you've told me, I'm getting a good picture of what you need. Is there anything else important to you that we haven't discussed yet?",
                    'actions': [],
                    'extracted_preferences': {}
                }
    
    def extract_preferences_from_conversation(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract structured preferences from conversation history."""
        
        preferences = {}
        
        # Combine all user messages
        user_text = " ".join([
            msg['content'] for msg in conversation_history 
            if msg['role'] == 'user'
        ]).lower()
        
        # Extract budget
        import re
        budget_matches = re.findall(r'\$([0-9,]+)', user_text)
        if budget_matches:
            try:
                budget = int(budget_matches[-1].replace(',', ''))  # Take the last mentioned
                preferences['budget_max'] = budget
            except ValueError:
                pass
        
        # Extract make preferences
        makes = ['toyota', 'honda', 'ford', 'chevrolet', 'bmw', 'mercedes', 'audi']
        for make in makes:
            if make in user_text:
                preferences['make'] = make.title()
                break
        
        # Extract fuel type preferences
        if any(word in user_text for word in ['hybrid', 'electric', 'ev']):
            if 'electric' in user_text or 'ev' in user_text:
                preferences['fuel_type'] = 'Electric'
            else:
                preferences['fuel_type'] = 'Hybrid'
        
        # Extract features
        features = []
        feature_keywords = {
            'backup camera': ['backup camera', 'rear camera', 'rearview camera'],
            'navigation': ['navigation', 'nav', 'gps'],
            'heated seats': ['heated seats', 'seat warmers'],
            'sunroof': ['sunroof', 'moonroof'],
            'bluetooth': ['bluetooth', 'wireless'],
            'all-wheel drive': ['awd', 'all-wheel', '4wd', 'four-wheel']
        }
        
        for feature, keywords in feature_keywords.items():
            if any(keyword in user_text for keyword in keywords):
                features.append(feature)
        
        if features:
            preferences['desired_features'] = features
        
        return preferences
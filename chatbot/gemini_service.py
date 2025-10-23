try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from django.conf import settings
import re

# Configure Gemini AI if available
if GEMINI_AVAILABLE:
    genai.configure(api_key="AIzaSyDvdiDXyHt7oUYQ1xe2zPjL_f_pK-HE5W0")

class GeminiChatService:
    def __init__(self):
        if GEMINI_AVAILABLE and genai is not None:
            try:
                self.model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception as e:
                (f"Failed to initialize Gemini: {e}")
                self.model = None
        else:
            self.model = None
        self.context = """
        You are a helpful assistant for Triple G BuildHub, a construction management platform. 
        
        IMPORTANT GUIDELINES:
        - Only discuss topics related to construction, building, project management, or Triple G BuildHub services
        - Do NOT provide any sensitive project information, user data, or specific project details
        - Keep responses professional and helpful
        - If asked about topics outside construction/building, politely redirect to construction-related topics
        - Do not provide personal information about users or specific project statuses
        - Focus on general construction advice, services, and platform features
       

        Triple G BuildHub offers:
        - Construction project management
        - Communication tools for construction teams
        - Project tracking and milestone management
        - Document management for construction projects
        - Team collaboration features
        
        If users ask about scheduling calls or appointments, guide them to use the contact form or scheduling options.
        You can also engage in casual conversation that is appropriate.
        """
    
    def get_response(self, user_message):
        # Fallback if Gemini is not available
        if not GEMINI_AVAILABLE or not self.model:
            return self._get_fallback_response(user_message)
        
        try:
            # Check if message is construction-related
            if not self._is_construction_related(user_message):
                return "I'm here to help with construction and building-related questions about Triple G BuildHub. How can I assist you with your construction project needs?"
            
            # Generate response with context
            prompt = f"{self.context}\n\nUser: {user_message}\nAssistant:"
            response = self.model.generate_content(prompt)
            
            # Filter response to ensure it's appropriate
            if response.text and self._is_appropriate_response(response.text):
                return response.text
            else:
                return "I'm sorry, I can only help with construction and building-related questions. How can I assist you with your project needs?"
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._get_fallback_response(user_message)
    
    def _is_construction_related(self, message):
        """Check if message is related to construction/building topics"""
        construction_keywords = [
            'build', 'construction', 'project', 'contractor', 'architect', 'engineer',
            'foundation', 'concrete', 'steel', 'material', 'blueprint', 'design',
            'permit', 'inspection', 'safety', 'site', 'management', 'schedule',
            'milestone', 'budget', 'cost', 'estimate', 'planning', 'renovation',
            'repair', 'maintenance', 'structure', 'building', 'house', 'commercial',
            'residential', 'infrastructure', 'triple g', 'buildhub', 'team',
            'communication', 'document', 'tracking', 'collaboration', 'platform',
            'service', 'help', 'support', 'contact', 'appointment', 'meeting',
            'hello', 'hi', 'thanks', 'thank you', 'how', 'what', 'when', 'where'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in construction_keywords)
    
    def _is_appropriate_response(self, response):
        """Check if response is appropriate and doesn't contain sensitive info"""
        # Check for patterns that might indicate sensitive information
        sensitive_patterns = [
            r'\$[\d,]+',  # Dollar amounts
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
            r'\b\d{1,5}\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr)\b',  # Addresses
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return False
        
        return True
    
    def _get_fallback_response(self, user_message):
        """Fallback responses when Gemini is not available"""
        fallback_responses = {
            'hello': "Hello! Welcome to Triple G BuildHub. How can I assist you with your construction project today?",
            'help': "I'm here to help with construction and building-related questions. You can ask about our services, project management, or schedule a call with our team.",
            'services': "Triple G BuildHub offers construction project management, team communication tools, document management, and project tracking services.",
            'contact': "You can contact our team through the contact form or schedule a callback. How would you like to proceed?",
            'default': "Thank you for your message. For detailed assistance with your construction project needs, please contact our support team or schedule a call."
        }
        
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return fallback_responses['hello']
        elif any(word in message_lower for word in ['help', 'assist', 'support']):
            return fallback_responses['help']
        elif any(word in message_lower for word in ['service', 'what do you do', 'about']):
            return fallback_responses['services']
        elif any(word in message_lower for word in ['contact', 'call', 'phone']):
            return fallback_responses['contact']
        else:
            return fallback_responses['default']

# Global instance
gemini_service = GeminiChatService()
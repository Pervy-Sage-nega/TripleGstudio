from .models import ChatbotIntent

def detect_intent(message_text):
    """Detect intent from message text using keyword matching"""
    intents = ChatbotIntent.objects.filter(is_active=True)
    best_intent = None
    best_score = 0
    
    for intent in intents:
        score = intent.match_keywords(message_text)
        if score > best_score:
            best_score = score
            best_intent = intent
    
    return best_intent, best_score

def generate_response(intent, user=None, context=None):
    """Generate response based on intent and context"""
    if not intent:
        return "I'm sorry, I didn't understand that. Can you please rephrase?"
    
    return intent.get_response(context)
from django.contrib.auth.models import User
from .models import Conversation, ChatbotIntent, ChatMessage
from site_diary.models import Project
import uuid

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
    
    response = intent.get_response(context)
    
    # Replace placeholders with user data
    if user and user.is_authenticated:
        response = response.replace('{user_name}', user.first_name or user.username)
    
    return response

def get_user_context(user):
    """Gather user context for personalization"""
    if not user or not user.is_authenticated:
        return {}
    
    context = {
        'name': user.first_name or user.username,
        'email': user.email,
    }
    
    # Add project info if available
    projects = Project.objects.filter(client=user)[:3]
    context['projects'] = [{'name': p.name, 'status': p.status} for p in projects]
    
    return context

def get_project_info(user):
    """Get user's project information"""
    if not user or not user.is_authenticated:
        return []
    
    projects = Project.objects.filter(client=user)
    return [{
        'name': project.name,
        'status': project.status,
        'progress': getattr(project, 'progress_percentage', 0),
    } for project in projects]

def get_or_create_conversation(user=None, session_id=None):
    """Get existing or create new conversation"""
    if user and user.is_authenticated:
        conversation, created = Conversation.objects.get_or_create(
            user=user,
            status='active',
            defaults={'session_id': uuid.uuid4()}
        )
    else:
        if not session_id:
            session_id = uuid.uuid4()
        conversation, created = Conversation.objects.get_or_create(
            session_id=session_id,
            status='active'
        )
    
    return conversation

def generate_session_id():
    """Generate UUID for anonymous users"""
    return str(uuid.uuid4())

def format_message_for_api(message):
    """Convert ChatMessage to JSON-serializable dict"""
    return {
        'id': message.id,
        'sender_type': message.sender_type,
        'message_text': message.message_text,
        'intent': message.intent,
        'created_at': message.created_at.isoformat(),
    }

def format_conversation_for_api(conversation):
    """Convert Conversation to JSON-serializable dict"""
    return {
        'id': conversation.id,
        'user': conversation.user.username if conversation.user else None,
        'session_id': str(conversation.session_id),
        'started_at': conversation.started_at.isoformat(),
        'last_message_at': conversation.last_message_at.isoformat(),
        'status': conversation.status,
        'message_count': conversation.get_message_count(),
    }
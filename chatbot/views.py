from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from admin_side.decorators import require_admin_role
from core.models import ContactMessage
from site_diary.models import Project
from .models import Conversation, ChatMessage, ChatbotIntent, ChatFeedback
from .utils import detect_intent, generate_response, get_or_create_conversation, format_message_for_api, format_conversation_for_api, get_project_info
from django.db.models import Count
import json
import uuid

def chatbot(request):
    return render(request, 'chatbot/chatbot.html')

@require_admin_role
def adminmessagecenter(request):
    # Get all contact messages ordered by creation date
    messages = ContactMessage.objects.all().order_by('-created_at')
    
    # Get status counts
    status_counts = ContactMessage.objects.values('status').annotate(count=Count('status'))
    status_dict = {item['status']: item['count'] for item in status_counts}
    
    # Prepare status counts with defaults
    new_count = status_dict.get('new', 0)
    read_count = status_dict.get('read', 0)
    reviewed_count = status_dict.get('reviewed', 0)
    archived_count = status_dict.get('archived', 0)
    
    context = {
        'contact_messages': messages,
        'new_count': new_count,
        'read_count': read_count,
        'reviewed_count': reviewed_count,
        'archived_count': archived_count,
        'total_count': messages.count(),
    }
    
    return render(request, 'admin/adminmessagecenter.html', context)

@csrf_exempt
@require_http_methods(['POST'])
def send_message(request):
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        session_id = data.get('session_id')
        
        if not message_text:
            return JsonResponse({'success': False, 'error': 'Message is required'})
        
        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                conversation = get_or_create_conversation(request.user if request.user.is_authenticated else None, session_id)
        else:
            conversation = get_or_create_conversation(request.user if request.user.is_authenticated else None, session_id)
        
        # Save user message
        user_message = ChatMessage.objects.create(
            conversation=conversation,
            sender_type='user',
            message_text=message_text
        )
        
        # Detect intent and generate response
        intent, confidence = detect_intent(message_text)
        response_text = generate_response(intent, request.user if request.user.is_authenticated else None)
        
        # Save bot message
        bot_message = ChatMessage.objects.create(
            conversation=conversation,
            sender_type='bot',
            message_text=response_text,
            intent=intent.name if intent else None,
            confidence_score=confidence
        )
        
        return JsonResponse({
            'success': True,
            'response': response_text,
            'conversation_id': conversation.id,
            'session_id': str(conversation.session_id)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(['GET'])
def get_conversation_history(request):
    try:
        conversation_id = request.GET.get('conversation_id')
        session_id = request.GET.get('session_id')
        
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Conversation not found'})
        elif session_id:
            try:
                conversation = Conversation.objects.get(session_id=session_id)
            except Conversation.DoesNotExist:
                return JsonResponse({'success': True, 'messages': []})
        else:
            return JsonResponse({'success': True, 'messages': []})
        
        # Verify user owns the conversation
        if request.user.is_authenticated and conversation.user != request.user:
            return JsonResponse({'success': False, 'error': 'Access denied'})
        
        messages = conversation.chatmessage_set.all()
        message_list = [format_message_for_api(msg) for msg in messages]
        
        return JsonResponse({
            'success': True,
            'messages': message_list,
            'conversation_id': conversation.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(['GET'])
def get_project_status(request):
    try:
        projects = get_project_info(request.user)
        return JsonResponse({
            'success': True,
            'projects': projects
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(['POST'])
def submit_feedback(request):
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        rating = data.get('rating')
        feedback_text = data.get('feedback_text', '')
        
        try:
            message = ChatMessage.objects.get(id=message_id)
        except ChatMessage.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Message not found'})
        
        ChatFeedback.objects.create(
            message=message,
            rating=rating,
            feedback_text=feedback_text
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(['POST'])
def create_contact_from_chat(request):
    try:
        data = json.loads(request.body)
        
        ContactMessage.objects.create(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone', ''),
            subject=data.get('subject'),
            message=data.get('message'),
            status='new'
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_admin_role
@require_http_methods(['GET'])
def admin_get_conversations(request):
    try:
        conversations = Conversation.objects.all()
        conversation_list = [format_conversation_for_api(conv) for conv in conversations]
        
        return JsonResponse({
            'success': True,
            'conversations': conversation_list
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_admin_role
@require_http_methods(['GET'])
def admin_get_conversation_messages(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        messages = conversation.chatmessage_set.all()
        message_list = [format_message_for_api(msg) for msg in messages]
        
        return JsonResponse({
            'success': True,
            'messages': message_list
        })
        
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_admin_role
@csrf_exempt
@require_http_methods(['POST'])
def admin_close_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        conversation.status = 'closed'
        conversation.save()
        
        return JsonResponse({'success': True})
        
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_admin_role
@csrf_exempt
@require_http_methods(['POST'])
def admin_archive_conversation(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        conversation.status = 'archived'
        conversation.save()
        
        return JsonResponse({'success': True})
        
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


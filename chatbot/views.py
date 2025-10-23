from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from admin_side.decorators import require_admin_role
from core.models import ContactMessage
from site_diary.models import Project
from .models import ChatbotMessage
from .gemini_service import gemini_service
from django.db.models import Count
import json
import uuid

def chatbot(request):
    return render(request, 'chatbot/chatbot.html')

@require_admin_role
def adminmessagecenter(request):
    # Get all chatbot messages ordered by creation date
    messages = ChatbotMessage.objects.all().order_by('-created_at')
    
    # Count messages by status
    new_count = messages.filter(status='new').count()
    read_count = messages.filter(status='read').count()
    reviewed_count = messages.filter(status='reviewed').count()
    archived_count = messages.filter(status='archived').count()
    
    context = {
        'chatbot_messages': messages,
        'total_count': messages.count(),
        'new_count': new_count,
        'read_count': read_count,
        'reviewed_count': reviewed_count,
        'archived_count': archived_count,
    }
    
    return render(request, 'admin/adminmessagecenter.html', context)

@csrf_exempt
@require_http_methods(['POST'])
def create_contact_from_chat(request):
    try:
        data = json.loads(request.body)
        
        ChatbotMessage.objects.create(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone', ''),
            message=data.get('message')
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})











@require_admin_role
@require_http_methods(['POST'])
def update_message_status(request):
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        status = data.get('status')
        
        if status not in ['new', 'read', 'reviewed', 'archived']:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
        message = ChatbotMessage.objects.get(id=message_id)
        message.status = status
        message.save()
        
        return JsonResponse({'success': True})
    except ChatbotMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_admin_role
@require_http_methods(['POST'])
def delete_message(request):
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        
        message = ChatbotMessage.objects.get(id=message_id)
        message.delete()
        
        return JsonResponse({'success': True})
    except ChatbotMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})







@csrf_exempt
@require_http_methods(['POST'])
def chat_with_gemini(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({'success': False, 'error': 'No message provided'})
        
        # Get response from Gemini service
        bot_response = gemini_service.get_response(user_message)
        
        return JsonResponse({
            'success': True,
            'response': bot_response
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e),
            'response': "I'm here to help with construction and building-related questions. How can I assist you?"
        })




from django.shortcuts import render
from admin_side.decorators import require_admin_role
from core.models import ContactMessage
from django.db.models import Count

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


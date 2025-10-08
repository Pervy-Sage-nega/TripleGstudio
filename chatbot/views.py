from django.shortcuts import render
from admin_side.decorators import require_admin_role

def chatbot(request):
    return render(request, 'chatbot/chatbot.html')

@require_admin_role
def adminmessagecenter(request):
    return render(request, 'admin/adminmessagecenter.html')


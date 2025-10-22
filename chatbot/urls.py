from django.urls import path
from . import views

urlpatterns = [
    path('adminmessagecenter/', views.adminmessagecenter, name='adminmessagecenter'),
    path('', views.chatbot, name='chatbot'),
    
    # API endpoints
    path('api/send-message/', views.send_message, name='send_message'),
    path('api/conversation-history/', views.get_conversation_history, name='get_conversation_history'),
    path('api/project-status/', views.get_project_status, name='get_project_status'),
    path('api/submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('api/create-contact/', views.create_contact_from_chat, name='create_contact_from_chat'),
    
    # Admin API endpoints
    path('api/admin/conversations/', views.admin_get_conversations, name='admin_get_conversations'),
    path('api/admin/conversation/<int:conversation_id>/messages/', views.admin_get_conversation_messages, name='admin_get_conversation_messages'),
    path('api/admin/conversation/<int:conversation_id>/close/', views.admin_close_conversation, name='admin_close_conversation'),
    path('api/admin/conversation/<int:conversation_id>/archive/', views.admin_archive_conversation, name='admin_archive_conversation'),
]
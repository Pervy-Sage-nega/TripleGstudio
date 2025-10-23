from django.urls import path
from . import views

urlpatterns = [
    path('adminmessagecenter/', views.adminmessagecenter, name='adminmessagecenter'),
    path('', views.chatbot, name='chatbot'),
    
    # API endpoints
    path('api/create-contact/', views.create_contact_from_chat, name='create_contact_from_chat'),
    path('api/chat/', views.chat_with_gemini, name='chat_with_gemini'),
    
    # Admin API endpoints
    path('api/admin/update-message-status/', views.update_message_status, name='update_message_status'),
    path('api/admin/delete-message/', views.delete_message, name='delete_message'),
]
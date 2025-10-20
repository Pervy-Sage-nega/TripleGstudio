from django.urls import path
from . import views

urlpatterns = [
    path('adminmessagecenter/', views.adminmessagecenter, name='adminmessagecenter'),
    path('', views.chatbot, name='chatbot'),
]
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import json

class Conversation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('archived', 'Archived'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.UUIDField(default=uuid.uuid4, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-last_message_at']
    
    def is_anonymous(self):
        return self.user is None
    
    def get_message_count(self):
        return self.chatmessage_set.count()
    
    def close_conversation(self):
        self.status = 'closed'
        self.save()

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message_text = models.TextField()
    intent = models.CharField(max_length=100, null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def is_from_user(self):
        return self.sender_type == 'user'
    
    def is_from_bot(self):
        return self.sender_type == 'bot'

class ChatbotIntent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    keywords = models.JSONField(default=list)
    response_template = models.TextField()
    requires_auth = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority']
    
    def match_keywords(self, message):
        message_lower = message.lower()
        matches = sum(1 for keyword in self.keywords if keyword.lower() in message_lower)
        return matches / len(self.keywords) if self.keywords else 0
    
    def get_response(self, context=None):
        return self.response_template

class ChatFeedback(models.Model):
    RATING_CHOICES = [
        ('thumbs_up', 'Thumbs Up'),
        ('thumbs_down', 'Thumbs Down'),
    ]
    
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    feedback_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

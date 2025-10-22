from django.contrib import admin
from .models import Conversation, ChatMessage, ChatbotIntent, ChatFeedback

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('sender_type', 'message_text', 'intent', 'created_at')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'started_at', 'last_message_at', 'status', 'get_message_count')
    list_filter = ('status', 'started_at')
    search_fields = ('user__username', 'user__email', 'session_id')
    readonly_fields = ('started_at', 'last_message_at')
    inlines = [ChatMessageInline]
    actions = ['close_conversations', 'archive_conversations']
    
    def close_conversations(self, request, queryset):
        queryset.update(status='closed')
    close_conversations.short_description = "Close selected conversations"
    
    def archive_conversations(self, request, queryset):
        queryset.update(status='archived')
    archive_conversations.short_description = "Archive selected conversations"

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender_type', 'truncated_message', 'intent', 'created_at')
    list_filter = ('sender_type', 'intent', 'created_at')
    search_fields = ('message_text', 'conversation__user__username')
    readonly_fields = ('created_at',)
    
    def truncated_message(self, obj):
        return obj.message_text[:50] + '...' if len(obj.message_text) > 50 else obj.message_text
    truncated_message.short_description = 'Message'

@admin.register(ChatbotIntent)
class ChatbotIntentAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'is_active', 'requires_auth', 'created_at')
    list_filter = ('is_active', 'requires_auth')
    search_fields = ('name', 'description')
    list_editable = ('priority', 'is_active')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description')
        }),
        ('Keywords & Response', {
            'fields': ('keywords', 'response_template')
        }),
        ('Settings', {
            'fields': ('requires_auth', 'priority', 'is_active')
        }),
    )

@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('feedback_text', 'message__message_text')
    readonly_fields = ('created_at',)

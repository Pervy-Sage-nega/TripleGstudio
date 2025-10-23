from django.contrib import admin
from .models import ChatbotMessage

@admin.register(ChatbotMessage)
class ChatbotMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False  # Prevent manual addition

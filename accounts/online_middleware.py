from django.utils.deprecation import MiddlewareMixin
from .activity_tracker import UserActivityTracker

class OnlineStatusMiddleware(MiddlewareMixin):
    """Middleware to track user online status"""
    
    def process_request(self, request):
        """Mark authenticated users as online on each request"""
        if request.user.is_authenticated:
            UserActivityTracker.mark_user_online(request.user)
        return None
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from django.core.cache import cache

class UserActivityTracker:
    """Track user online status using cache for better performance"""
    
    ONLINE_THRESHOLD = 5  # minutes
    CACHE_TIMEOUT = 300   # 5 minutes in seconds
    
    @classmethod
    def mark_user_online(cls, user):
        """Mark user as online"""
        if user.is_authenticated:
            cache_key = f"user_online_{user.id}"
            cache.set(cache_key, timezone.now().isoformat(), cls.CACHE_TIMEOUT)
    
    @classmethod
    def is_user_online(cls, user):
        """Check if user is online"""
        if not user.is_authenticated:
            return False
            
        cache_key = f"user_online_{user.id}"
        last_activity = cache.get(cache_key)
        
        if not last_activity:
            return False
            
        try:
            last_activity_time = timezone.datetime.fromisoformat(last_activity)
            if timezone.is_naive(last_activity_time):
                last_activity_time = timezone.make_aware(last_activity_time)
            
            cutoff_time = timezone.now() - timedelta(minutes=cls.ONLINE_THRESHOLD)
            return last_activity_time > cutoff_time
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def get_online_users(cls):
        """Get list of online user IDs"""
        online_users = []
        # This is a simplified version - in production you might want to use Redis pattern matching
        return online_users
    
    @classmethod
    def mark_user_offline(cls, user):
        """Explicitly mark user as offline"""
        if user.is_authenticated:
            cache_key = f"user_online_{user.id}"
            cache.delete(cache_key)
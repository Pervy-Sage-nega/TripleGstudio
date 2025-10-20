"""
Blog Analytics System for Triple G Blog
Tracks views, engagement, and provides insights
"""

from django.db import models
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Q
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json


class BlogAnalytics(models.Model):
    """Blog analytics tracking model"""
    
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('post_view', 'Post View'),
        ('search', 'Search'),
        ('category_view', 'Category View'),
        ('tag_view', 'Tag View'),
        ('social_share', 'Social Share'),
        ('newsletter_signup', 'Newsletter Signup'),
        ('comment_post', 'Comment Posted'),
    ]
    
    DEVICE_TYPES = [
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('unknown', 'Unknown'),
    ]
    
    # Event details
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Device and browser info
    user_agent = models.TextField(blank=True)
    device_type = models.CharField(max_length=10, choices=DEVICE_TYPES, default='unknown')
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    
    # Content information
    blog_post = models.ForeignKey('BlogPost', on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ForeignKey('Tag', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Additional data
    referrer = models.URLField(blank=True)
    search_query = models.CharField(max_length=200, blank=True)
    social_platform = models.CharField(max_length=50, blank=True)
    
    # Engagement metrics
    time_on_page = models.PositiveIntegerField(null=True, blank=True)  # seconds
    scroll_depth = models.PositiveIntegerField(null=True, blank=True)  # percentage
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Blog Analytics'
        verbose_name_plural = 'Blog Analytics'
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['blog_post', 'timestamp']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class AnalyticsManager:
    """Manager class for blog analytics operations"""
    
    @staticmethod
    def track_event(event_type, request, **kwargs):
        """Track an analytics event"""
        try:
            # Extract device and browser info
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device_type = AnalyticsManager.get_device_type(user_agent)
            browser = AnalyticsManager.get_browser(user_agent)
            os = AnalyticsManager.get_os(user_agent)
            
            # Get session ID
            session_id = request.session.session_key or ''
            
            # Get IP address
            ip_address = AnalyticsManager.get_client_ip(request)
            
            # Get referrer
            referrer = request.META.get('HTTP_REFERER', '')
            
            # Create analytics record
            analytics = BlogAnalytics.objects.create(
                event_type=event_type,
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=device_type,
                browser=browser,
                os=os,
                referrer=referrer,
                **kwargs
            )
            
            return analytics
            
        except Exception as e:
            print(f"Error tracking analytics event: {e}")
            return None
    
    @staticmethod
    def get_device_type(user_agent):
        """Determine device type from user agent"""
        user_agent = user_agent.lower()
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return 'tablet'
        elif 'mozilla' in user_agent or 'chrome' in user_agent or 'safari' in user_agent:
            return 'desktop'
        return 'unknown'
    
    @staticmethod
    def get_browser(user_agent):
        """Extract browser from user agent"""
        user_agent = user_agent.lower()
        if 'chrome' in user_agent:
            return 'Chrome'
        elif 'firefox' in user_agent:
            return 'Firefox'
        elif 'safari' in user_agent and 'chrome' not in user_agent:
            return 'Safari'
        elif 'edge' in user_agent:
            return 'Edge'
        elif 'opera' in user_agent:
            return 'Opera'
        return 'Unknown'
    
    @staticmethod
    def get_os(user_agent):
        """Extract OS from user agent"""
        user_agent = user_agent.lower()
        if 'windows' in user_agent:
            return 'Windows'
        elif 'mac' in user_agent:
            return 'macOS'
        elif 'linux' in user_agent:
            return 'Linux'
        elif 'android' in user_agent:
            return 'Android'
        elif 'ios' in user_agent or 'iphone' in user_agent or 'ipad' in user_agent:
            return 'iOS'
        return 'Unknown'
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_dashboard_data(days=30):
        """Get analytics dashboard data"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Base queryset
        analytics = BlogAnalytics.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        # Total views
        total_views = analytics.filter(event_type='post_view').count()
        
        # Unique visitors (by session)
        unique_visitors = analytics.values('session_id').distinct().count()
        
        # Popular posts
        popular_posts = analytics.filter(
            event_type='post_view',
            blog_post__isnull=False
        ).values(
            'blog_post__title',
            'blog_post__slug'
        ).annotate(
            views=Count('id')
        ).order_by('-views')[:10]
        
        # Device breakdown
        device_stats = analytics.values('device_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Browser breakdown
        browser_stats = analytics.values('browser').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Daily views for chart
        daily_views = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            views = analytics.filter(
                event_type='post_view',
                timestamp__date=date.date()
            ).count()
            daily_views.append({
                'date': date.strftime('%Y-%m-%d'),
                'views': views
            })
        
        # Top search queries
        top_searches = analytics.filter(
            event_type='search',
            search_query__isnull=False
        ).exclude(
            search_query=''
        ).values('search_query').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Social shares
        social_shares = analytics.filter(
            event_type='social_share'
        ).values('social_platform').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average time on page
        avg_time_on_page = analytics.filter(
            time_on_page__isnull=False
        ).aggregate(
            avg_time=Avg('time_on_page')
        )['avg_time'] or 0
        
        # Bounce rate (sessions with only one page view)
        total_sessions = analytics.values('session_id').distinct().count()
        single_page_sessions = analytics.values('session_id').annotate(
            page_count=Count('id')
        ).filter(page_count=1).count()
        
        bounce_rate = (single_page_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        return {
            'total_views': total_views,
            'unique_visitors': unique_visitors,
            'popular_posts': list(popular_posts),
            'device_stats': list(device_stats),
            'browser_stats': list(browser_stats),
            'daily_views': daily_views,
            'top_searches': list(top_searches),
            'social_shares': list(social_shares),
            'avg_time_on_page': round(avg_time_on_page, 2),
            'bounce_rate': round(bounce_rate, 2),
            'date_range': {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        }
    
    @staticmethod
    def get_post_analytics(blog_post, days=30):
        """Get analytics for a specific blog post"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        analytics = BlogAnalytics.objects.filter(
            blog_post=blog_post,
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        # Total views
        total_views = analytics.filter(event_type='post_view').count()
        
        # Unique visitors
        unique_visitors = analytics.filter(
            event_type='post_view'
        ).values('session_id').distinct().count()
        
        # Daily views
        daily_views = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            views = analytics.filter(
                event_type='post_view',
                timestamp__date=date.date()
            ).count()
            daily_views.append({
                'date': date.strftime('%Y-%m-%d'),
                'views': views
            })
        
        # Social shares
        social_shares = analytics.filter(
            event_type='social_share'
        ).values('social_platform').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average engagement
        avg_time_on_page = analytics.filter(
            time_on_page__isnull=False
        ).aggregate(avg_time=Avg('time_on_page'))['avg_time'] or 0
        
        avg_scroll_depth = analytics.filter(
            scroll_depth__isnull=False
        ).aggregate(avg_scroll=Avg('scroll_depth'))['avg_scroll'] or 0
        
        return {
            'total_views': total_views,
            'unique_visitors': unique_visitors,
            'daily_views': daily_views,
            'social_shares': list(social_shares),
            'avg_time_on_page': round(avg_time_on_page, 2),
            'avg_scroll_depth': round(avg_scroll_depth, 2),
        }

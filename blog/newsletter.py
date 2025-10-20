"""
Newsletter subscription system for the Triple G Blog
"""

from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid


class NewsletterSubscriber(models.Model):
    """Newsletter subscriber model"""
    
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_date = models.DateTimeField(auto_now_add=True)
    unsubscribed_date = models.DateTimeField(null=True, blank=True)
    confirmation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_confirmed = models.BooleanField(default=False)
    
    # Subscription preferences
    weekly_digest = models.BooleanField(default=True)
    new_posts = models.BooleanField(default=True)
    featured_posts = models.BooleanField(default=True)
    
    # Analytics
    open_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    last_opened = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-subscribed_date']
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
    
    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
    
    def unsubscribe(self):
        """Unsubscribe the user"""
        self.is_active = False
        self.unsubscribed_date = timezone.now()
        self.save()
    
    def confirm_subscription(self):
        """Confirm the subscription"""
        self.is_confirmed = True
        self.save()


class NewsletterCampaign(models.Model):
    """Newsletter campaign model"""
    
    CAMPAIGN_TYPES = [
        ('weekly_digest', 'Weekly Digest'),
        ('new_post', 'New Post Notification'),
        ('featured_post', 'Featured Post'),
        ('custom', 'Custom Campaign'),
    ]
    
    CAMPAIGN_STATUS = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES, default='custom')
    status = models.CharField(max_length=20, choices=CAMPAIGN_STATUS, default='draft')
    
    # Scheduling
    created_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    
    # Analytics
    total_sent = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    
    # Related blog post (for new post notifications)
    blog_post = models.ForeignKey('BlogPost', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_date']
        verbose_name = 'Newsletter Campaign'
        verbose_name_plural = 'Newsletter Campaigns'
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def open_rate(self):
        """Calculate open rate percentage"""
        if self.total_sent == 0:
            return 0
        return round((self.total_opened / self.total_sent) * 100, 2)
    
    @property
    def click_rate(self):
        """Calculate click rate percentage"""
        if self.total_sent == 0:
            return 0
        return round((self.total_clicked / self.total_sent) * 100, 2)


class NewsletterAnalytics(models.Model):
    """Newsletter analytics tracking"""
    
    ACTION_TYPES = [
        ('open', 'Email Opened'),
        ('click', 'Link Clicked'),
        ('unsubscribe', 'Unsubscribed'),
    ]
    
    subscriber = models.ForeignKey(NewsletterSubscriber, on_delete=models.CASCADE)
    campaign = models.ForeignKey(NewsletterCampaign, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Newsletter Analytics'
        verbose_name_plural = 'Newsletter Analytics'
    
    def __str__(self):
        return f"{self.subscriber.email} - {self.get_action_type_display()}"

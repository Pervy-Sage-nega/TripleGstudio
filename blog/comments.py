"""
Comment system for the Triple G Blog
Includes moderation, threading, and spam protection
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import EmailValidator
from django.urls import reverse
from django.utils.html import strip_tags
import uuid


class Comment(models.Model):
    """Blog comment model with moderation support"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Moderation'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('spam', 'Spam'),
    ]
    
    # Content
    blog_post = models.ForeignKey('BlogPost', on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    
    # Author information
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField(validators=[EmailValidator()])
    author_website = models.URLField(blank=True)
    
    # Threading support
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Moderation
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_comments')
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderation_note = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Spam detection
    spam_score = models.FloatField(default=0.0)
    is_spam = models.BooleanField(default=False)
    
    # Engagement
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['blog_post', 'status', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.blog_post.title}"
    
    def get_absolute_url(self):
        return f"{self.blog_post.get_absolute_url()}#comment-{self.id}"
    
    @property
    def is_reply(self):
        return self.parent is not None
    
    @property
    def reply_count(self):
        return self.replies.filter(status='approved').count()
    
    def approve(self, moderator=None):
        """Approve the comment"""
        self.status = 'approved'
        self.moderated_by = moderator
        self.moderated_at = timezone.now()
        self.save()
    
    def reject(self, moderator=None, note=''):
        """Reject the comment"""
        self.status = 'rejected'
        self.moderated_by = moderator
        self.moderated_at = timezone.now()
        self.moderation_note = note
        self.save()
    
    def mark_as_spam(self, moderator=None):
        """Mark comment as spam"""
        self.status = 'spam'
        self.is_spam = True
        self.moderated_by = moderator
        self.moderated_at = timezone.now()
        self.save()


class CommentLike(models.Model):
    """Comment like/dislike tracking"""
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_like = models.BooleanField()  # True for like, False for dislike
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user', 'ip_address']
        verbose_name = 'Comment Like'
        verbose_name_plural = 'Comment Likes'
    
    def __str__(self):
        action = "liked" if self.is_like else "disliked"
        return f"Comment {action} by {self.user or self.ip_address}"


class CommentModerationRule(models.Model):
    """Automatic comment moderation rules"""
    
    RULE_TYPES = [
        ('keyword', 'Keyword Filter'),
        ('email_domain', 'Email Domain Filter'),
        ('ip_address', 'IP Address Filter'),
        ('length', 'Content Length'),
        ('links', 'Link Count'),
        ('caps', 'Excessive Caps'),
    ]
    
    ACTION_CHOICES = [
        ('approve', 'Auto Approve'),
        ('reject', 'Auto Reject'),
        ('spam', 'Mark as Spam'),
        ('hold', 'Hold for Review'),
    ]
    
    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    pattern = models.TextField(help_text="Pattern to match (keywords, domains, etc.)")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Comment Moderation Rule'
        verbose_name_plural = 'Comment Moderation Rules'
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class CommentManager:
    """Manager for comment operations"""
    
    @staticmethod
    def create_comment(blog_post, content, author_name, author_email, 
                      author_website='', parent=None, user=None, request=None):
        """Create a new comment with automatic moderation"""
        
        # Clean content
        content = strip_tags(content).strip()
        
        # Create comment
        comment = Comment(
            blog_post=blog_post,
            content=content,
            author_name=author_name,
            author_email=author_email,
            author_website=author_website,
            parent=parent,
            author=user
        )
        
        # Add request metadata if available
        if request:
            comment.ip_address = CommentManager.get_client_ip(request)
            comment.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Run spam detection
        comment.spam_score = CommentManager.calculate_spam_score(comment)
        comment.is_spam = comment.spam_score > 0.7
        
        # Apply moderation rules
        comment.status = CommentManager.apply_moderation_rules(comment)
        
        comment.save()
        
        # Send notifications if approved
        if comment.status == 'approved':
            CommentManager.send_notifications(comment)
        
        return comment
    
    @staticmethod
    def calculate_spam_score(comment):
        """Calculate spam score for a comment"""
        score = 0.0
        content = comment.content.lower()
        
        # Check for spam indicators
        spam_keywords = ['viagra', 'casino', 'lottery', 'winner', 'congratulations', 
                        'click here', 'free money', 'make money fast']
        
        for keyword in spam_keywords:
            if keyword in content:
                score += 0.3
        
        # Check for excessive links
        link_count = content.count('http')
        if link_count > 2:
            score += 0.4
        
        # Check for excessive caps
        caps_ratio = sum(1 for c in comment.content if c.isupper()) / len(comment.content)
        if caps_ratio > 0.5:
            score += 0.3
        
        # Check content length
        if len(content) < 10:
            score += 0.2
        elif len(content) > 500:
            score += 0.1
        
        return min(score, 1.0)
    
    @staticmethod
    def apply_moderation_rules(comment):
        """Apply automatic moderation rules"""
        rules = CommentModerationRule.objects.filter(is_active=True)
        
        for rule in rules:
            if CommentManager.rule_matches(comment, rule):
                if rule.action == 'approve':
                    return 'approved'
                elif rule.action == 'reject':
                    return 'rejected'
                elif rule.action == 'spam':
                    comment.is_spam = True
                    return 'spam'
                elif rule.action == 'hold':
                    return 'pending'
        
        # Default moderation based on spam score
        if comment.is_spam or comment.spam_score > 0.7:
            return 'spam'
        elif comment.spam_score > 0.5:
            return 'pending'
        else:
            return 'approved'  # Auto-approve low-risk comments
    
    @staticmethod
    def rule_matches(comment, rule):
        """Check if a comment matches a moderation rule"""
        content = comment.content.lower()
        pattern = rule.pattern.lower()
        
        if rule.rule_type == 'keyword':
            keywords = [k.strip() for k in pattern.split(',')]
            return any(keyword in content for keyword in keywords)
        
        elif rule.rule_type == 'email_domain':
            domains = [d.strip() for d in pattern.split(',')]
            email_domain = comment.author_email.split('@')[1].lower()
            return email_domain in domains
        
        elif rule.rule_type == 'length':
            min_length, max_length = map(int, pattern.split(','))
            return not (min_length <= len(comment.content) <= max_length)
        
        elif rule.rule_type == 'links':
            max_links = int(pattern)
            link_count = comment.content.lower().count('http')
            return link_count > max_links
        
        elif rule.rule_type == 'caps':
            max_caps_ratio = float(pattern)
            caps_ratio = sum(1 for c in comment.content if c.isupper()) / len(comment.content)
            return caps_ratio > max_caps_ratio
        
        return False
    
    @staticmethod
    def send_notifications(comment):
        """Send notifications for new comments"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        try:
            # Notify blog post author
            if comment.blog_post.author.email:
                subject = f"New comment on your post: {comment.blog_post.title}"
                message = f"""
                A new comment has been posted on your blog post "{comment.blog_post.title}".
                
                Comment by: {comment.author_name}
                Content: {comment.content[:200]}...
                
                View comment: {comment.get_absolute_url()}
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[comment.blog_post.author.email],
                    fail_silently=True
                )
            
            # Notify parent comment author if it's a reply
            if comment.parent and comment.parent.author_email:
                subject = f"Reply to your comment on: {comment.blog_post.title}"
                message = f"""
                Someone replied to your comment on "{comment.blog_post.title}".
                
                Reply by: {comment.author_name}
                Content: {comment.content[:200]}...
                
                View reply: {comment.get_absolute_url()}
                """
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[comment.parent.author_email],
                    fail_silently=True
                )
                
        except Exception as e:
            print(f"Error sending comment notification: {e}")
    
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
    def get_comment_tree(blog_post):
        """Get hierarchical comment tree for a blog post"""
        comments = Comment.objects.filter(
            blog_post=blog_post,
            status__in=['approved', 'pending']  # Show both approved and pending for now
        ).select_related('author').order_by('created_at')
        
        # Build comment tree
        comment_dict = {}
        root_comments = []
        
        for comment in comments:
            comment_dict[comment.id] = comment
            comment.replies_list = []
            
            if comment.parent_id:
                if comment.parent_id in comment_dict:
                    comment_dict[comment.parent_id].replies_list.append(comment)
            else:
                root_comments.append(comment)
        
        return root_comments

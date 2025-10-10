from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from PIL import Image
import os

# Create your models here.

class Category(models.Model):
    """Blog post categories for organizing content"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Brief description of this category")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code for UI styling")
    icon = models.CharField(max_length=50, default="fas fa-folder", help_text="FontAwesome icon class")
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category_list', kwargs={'slug': self.slug})
    
    def get_post_count(self):
        """Get count of published posts - use annotation in queries for better performance"""
        return self.blog_posts.filter(status='published').count()


class Tag(models.Model):
    """Tags for blog posts to enable flexible categorization"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    usage_count = models.IntegerField(default=0, help_text="Number of times this tag has been used")
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Blog Tag"
        verbose_name_plural = "Blog Tags"
        ordering = ['-usage_count', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:tag_list', kwargs={'slug': self.slug})


class BlogPost(models.Model):
    """Main blog post model with comprehensive features"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Blog post title")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(help_text="Main blog content (supports HTML)")
    excerpt = models.TextField(max_length=500, blank=True, help_text="Brief summary for previews")
    
    # Media
    featured_image = models.ImageField(
        upload_to='blog/featured_images/', 
        blank=True, 
        null=True,
        help_text="Main image for the blog post"
    )
    featured_image_alt = models.CharField(
        max_length=200, 
        blank=True, 
        help_text="Alt text for featured image (accessibility)"
    )
    
    # Relationships
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='blog_posts')
    
    # Status and Features
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False, help_text="Show in featured section")
    
    # Rejection tracking
    rejection_reason = models.TextField(blank=True, null=True, help_text="Admin's reason for rejection")
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rejected_posts', help_text="Admin who rejected this post")
    rejected_at = models.DateTimeField(null=True, blank=True, help_text="When this post was rejected")
    
    # SEO Fields
    seo_meta_title = models.CharField(max_length=60, blank=True, help_text="SEO title (max 60 chars)")
    seo_meta_description = models.TextField(max_length=160, blank=True, help_text="SEO description (max 160 chars)")
    
    # Content Enhancement
    enable_toc = models.BooleanField(default=True, help_text="Enable table of contents generation")
    reading_time = models.PositiveIntegerField(blank=True, null=True, help_text="Estimated reading time in minutes")
    
    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, null=True)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ['-published_date', '-created_date']
        indexes = [
            models.Index(fields=['status', 'published_date']),
            models.Index(fields=['featured', 'status']),
            models.Index(fields=['category', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Set published date when status changes to published
        if self.status == 'published' and not self.published_date:
            self.published_date = timezone.now()
        
        # Auto-generate SEO fields if empty
        if not self.seo_meta_title:
            self.seo_meta_title = self.title[:60]
        
        if not self.seo_meta_description and self.excerpt:
            self.seo_meta_description = self.excerpt[:160]
        
        # Auto-calculate reading time
        if self.content and not self.reading_time:
            self.reading_time = self.calculate_reading_time()
        
        super().save(*args, **kwargs)
    
    def calculate_reading_time(self):
        """Calculate estimated reading time based on word count"""
        if not self.content:
            return 1
        
        # Remove HTML tags and count words
        import re
        text = re.sub(r'<[^>]+>', '', self.content)
        word_count = len(text.split())
        
        # Average reading speed: 200 words per minute
        reading_time = max(1, round(word_count / 200))
        return reading_time
        
        # Update tag usage counts
        for tag in self.tags.all():
            tag.usage_count = tag.blog_posts.filter(status='published').count()
            tag.save()
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:blog_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return self.status == 'published' and self.published_date
    
    @property
    def reading_time(self):
        """Estimate reading time based on word count (average 200 words per minute)"""
        word_count = len(self.content.split())
        minutes = max(1, round(word_count / 200))
        return minutes
    
    def increment_view_count(self):
        """Increment view count for analytics"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def get_related_posts(self, limit=3):
        """Get related posts based on category and tags"""
        related = BlogPost.objects.filter(
            status='published'
        ).exclude(id=self.id).distinct()
        
        # Prioritize posts from same category
        if self.category:
            related = related.filter(category=self.category)
        
        # If not enough posts, include posts with similar tags
        if related.count() < limit and self.tags.exists():
            tag_related = BlogPost.objects.filter(
                tags__in=self.tags.all(),
                status='published'
            ).exclude(id=self.id).distinct()
            
            # Use union instead of | operator to avoid query combination issues
            related = related.union(tag_related)
        
        return related[:limit]


class Comment(models.Model):
    """Blog comment model with moderation support"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Moderation'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('spam', 'Spam'),
    ]
    
    # Content
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    
    # Author information
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
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



class BlogImage(models.Model):
    """Additional images for blog posts (gallery)"""
    blog_post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='blog/gallery/')
    caption = models.CharField(max_length=200, blank=True, help_text="Image caption")
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alt text for accessibility")
    order = models.IntegerField(default=0, help_text="Display order")
    
    # Image metadata (auto-populated)
    width = models.PositiveIntegerField(blank=True, null=True, help_text="Image width in pixels")
    height = models.PositiveIntegerField(blank=True, null=True, help_text="Image height in pixels")
    file_size = models.PositiveIntegerField(blank=True, null=True, help_text="File size in bytes")
    uploaded_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        verbose_name = "Blog Image"
        verbose_name_plural = "Blog Images"
        ordering = ['order', 'id']
    
    def save(self, *args, **kwargs):
        """Auto-populate image metadata"""
        if self.image and not self.width:
            try:
                from PIL import Image
                with Image.open(self.image) as img:
                    self.width, self.height = img.size
                
                # Get file size
                self.image.seek(0, 2)  # Seek to end
                self.file_size = self.image.tell()
                self.image.seek(0)  # Reset to beginning
            except Exception:
                pass  # Fail silently if image processing fails
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Image for {self.blog_post.title}"

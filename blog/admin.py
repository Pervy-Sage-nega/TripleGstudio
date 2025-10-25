from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import BlogPost, Category, Tag, BlogImage
from .newsletter import NewsletterSubscriber, NewsletterCampaign, NewsletterAnalytics

# Register your models here.

class BlogImageInline(admin.TabularInline):
    """Inline admin for blog gallery images"""
    model = BlogImage
    extra = 1
    fields = ('image', 'caption', 'alt_text', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for blog categories"""
    list_display = ('name', 'slug', 'post_count', 'color_preview', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_date',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display Settings', {
            'fields': ('color', 'icon')
        }),
        ('Statistics', {
            'fields': ('created_date',),
            'classes': ('collapse',)
        })
    )
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div>',
            obj.color
        )
    color_preview.short_description = "Color"
    
    def post_count(self, obj):
        count = obj.get_post_count()
        if count > 0:
            url = reverse('admin:blog_blogpost_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} posts</a>', url, count)
        return "0 posts"
    post_count.short_description = "Published Posts"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for blog tags"""
    list_display = ('name', 'slug', 'usage_count', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('usage_count', 'created_date')
    ordering = ('-usage_count', 'name')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Admin interface for blog posts"""
    list_display = (
        'title', 'author', 'category', 'status', 'featured', 
        'view_count', 'published_date', 'created_date'
    )
    list_filter = (
        'status', 'featured', 'category', 'tags', 
        'created_date', 'published_date', 'author'
    )
    search_fields = ('title', 'content', 'excerpt', 'seo_meta_title')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = (
        'view_count', 'created_date', 'updated_date', 
        'reading_time', 'featured_image_preview'
    )
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('Content', {
            'fields': ('content', 'excerpt')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_preview'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('status', 'featured', 'published_date')
        }),
        ('SEO Optimization', {
            'fields': ('seo_meta_title', 'seo_meta_description'),
            'classes': ('collapse',)
        }),
        ('Analytics & Timestamps', {
            'fields': (
                'view_count', 'reading_time', 
                'created_date', 'updated_date'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [BlogImageInline]
    
    actions = ['make_published', 'make_draft', 'make_featured', 'remove_featured']
    
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />',
                obj.featured_image.url
            )
        return "No featured image"
    featured_image_preview.short_description = "Featured Image Preview"
    
    def reading_time(self, obj):
        return f"{obj.reading_time} min read"
    reading_time.short_description = "Reading Time"
    
    def make_published(self, request, queryset):
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} posts were successfully published.')
    make_published.short_description = "Mark selected posts as published"
    
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} posts were moved to draft.')
    make_draft.short_description = "Mark selected posts as draft"
    
    def make_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} posts were marked as featured.')
    make_featured.short_description = "Mark selected posts as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f'{updated} posts were removed from featured.')
    remove_featured.short_description = "Remove featured status from selected posts"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category').prefetch_related('tags')


@admin.register(BlogImage)
class BlogImageAdmin(admin.ModelAdmin):
    """Admin interface for blog images"""
    list_display = ('blog_post', 'image_preview', 'caption', 'order')
    list_filter = ('blog_post__category', 'blog_post__status')
    search_fields = ('blog_post__title', 'caption', 'alt_text')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"



@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'is_confirmed', 'subscribed_date', 'open_count', 'click_count')
    list_filter = ('is_active', 'is_confirmed', 'weekly_digest', 'new_posts', 'featured_posts', 'subscribed_date')
    search_fields = ('email', 'name')
    readonly_fields = ('confirmation_token', 'subscribed_date', 'unsubscribed_date', 'open_count', 'click_count', 'last_opened')


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'campaign_type', 'status', 'scheduled_date', 'sent_date', 'total_sent', 'open_rate', 'click_rate')
    list_filter = ('campaign_type', 'status', 'created_date', 'scheduled_date')
    search_fields = ('title', 'subject', 'content')
    readonly_fields = ('created_date', 'sent_date', 'total_sent', 'total_opened', 'total_clicked', 'open_rate', 'click_rate')


@admin.register(NewsletterAnalytics)
class NewsletterAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'campaign', 'action_type', 'timestamp', 'ip_address')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('subscriber__email', 'campaign__title')
    readonly_fields = ('subscriber', 'campaign', 'action_type', 'timestamp', 'ip_address', 'user_agent')

"""
Sitemap configuration for the Triple G Blog System
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, Category


class BlogPostSitemap(Sitemap):
    """Sitemap for blog posts"""
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return BlogPost.objects.filter(status='published').select_related('category')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class BlogCategorySitemap(Sitemap):
    """Sitemap for blog categories"""
    changefreq = "monthly"
    priority = 0.6
    
    def items(self):
        return Category.objects.filter(blogpost__status='published').distinct()
    
    def lastmod(self, obj):
        # Get the latest blog post in this category
        latest_post = BlogPost.objects.filter(
            category=obj, 
            status='published'
        ).order_by('-updated_at').first()
        return latest_post.updated_at if latest_post else obj.created_at
    
    def location(self, obj):
        return reverse('blog:category_list', args=[obj.slug])


class StaticBlogSitemap(Sitemap):
    """Sitemap for static blog pages"""
    changefreq = "daily"
    priority = 0.9
    
    def items(self):
        return ['blog:blog_list']
    
    def location(self, item):
        return reverse(item)
    
    def lastmod(self, obj):
        # Get the latest blog post date
        latest_post = BlogPost.objects.filter(status='published').order_by('-updated_at').first()
        return latest_post.updated_at if latest_post else None

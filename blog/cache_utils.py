"""
Caching utilities for the Triple G Blog System
Implements intelligent caching strategies for better performance
"""

from django.core.cache import cache
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import hashlib
import json


class BlogCacheManager:
    """Manages caching for blog-related data"""
    
    # Cache timeouts (in seconds)
    CACHE_TIMEOUTS = {
        'blog_post': 3600,  # 1 hour
        'blog_list': 1800,  # 30 minutes
        'categories': 7200,  # 2 hours
        'tags': 7200,  # 2 hours
        'popular_posts': 3600,  # 1 hour
        'recent_posts': 1800,  # 30 minutes
        'featured_posts': 3600,  # 1 hour
        'search_results': 900,  # 15 minutes
        'analytics': 1800,  # 30 minutes
    }
    
    @staticmethod
    def get_cache_key(prefix, *args, **kwargs):
        """Generate a cache key"""
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)
        
        # Add kwargs to key
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(hashlib.md5(
                json.dumps(sorted_kwargs, sort_keys=True).encode()
            ).hexdigest()[:8])
        
        return ':'.join(key_parts)
    
    @staticmethod
    def cache_blog_post(blog_post):
        """Cache a blog post"""
        cache_key = BlogCacheManager.get_cache_key('blog_post', blog_post.slug)
        cache.set(
            cache_key, 
            blog_post, 
            BlogCacheManager.CACHE_TIMEOUTS['blog_post']
        )
        return cache_key
    
    @staticmethod
    def get_cached_blog_post(slug):
        """Get cached blog post"""
        cache_key = BlogCacheManager.get_cache_key('blog_post', slug)
        return cache.get(cache_key)
    
    @staticmethod
    def cache_blog_list(posts, filters=None):
        """Cache blog list with filters"""
        cache_key = BlogCacheManager.get_cache_key('blog_list', **filters or {})
        cache.set(
            cache_key,
            posts,
            BlogCacheManager.CACHE_TIMEOUTS['blog_list']
        )
        return cache_key
    
    @staticmethod
    def get_cached_blog_list(filters=None):
        """Get cached blog list"""
        cache_key = BlogCacheManager.get_cache_key('blog_list', **filters or {})
        return cache.get(cache_key)
    
    @staticmethod
    def cache_categories():
        """Cache categories with post counts"""
        from .models import Category
        
        categories = Category.objects.annotate(
            post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
        ).filter(post_count__gt=0).order_by('name')
        
        cache_key = BlogCacheManager.get_cache_key('categories')
        cache.set(
            cache_key,
            list(categories),
            BlogCacheManager.CACHE_TIMEOUTS['categories']
        )
        return list(categories)
    
    @staticmethod
    def get_cached_categories():
        """Get cached categories"""
        cache_key = BlogCacheManager.get_cache_key('categories')
        categories = cache.get(cache_key)
        
        if categories is None:
            categories = BlogCacheManager.cache_categories()
        
        return categories
    
    @staticmethod
    def cache_popular_tags():
        """Cache popular tags"""
        from .models import Tag
        
        tags = Tag.objects.annotate(
            post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
        ).filter(post_count__gt=0).order_by('-post_count')[:20]
        
        cache_key = BlogCacheManager.get_cache_key('tags')
        cache.set(
            cache_key,
            list(tags),
            BlogCacheManager.CACHE_TIMEOUTS['tags']
        )
        return list(tags)
    
    @staticmethod
    def get_cached_popular_tags():
        """Get cached popular tags"""
        cache_key = BlogCacheManager.get_cache_key('tags')
        tags = cache.get(cache_key)
        
        if tags is None:
            tags = BlogCacheManager.cache_popular_tags()
        
        return tags
    
    @staticmethod
    def cache_popular_posts(limit=5):
        """Cache popular posts"""
        from .models import BlogPost
        
        posts = BlogPost.objects.filter(
            status='published'
        ).order_by('-view_count', '-published_date')[:limit]
        
        cache_key = BlogCacheManager.get_cache_key('popular_posts', limit)
        cache.set(
            cache_key,
            list(posts),
            BlogCacheManager.CACHE_TIMEOUTS['popular_posts']
        )
        return list(posts)
    
    @staticmethod
    def get_cached_popular_posts(limit=5):
        """Get cached popular posts"""
        cache_key = BlogCacheManager.get_cache_key('popular_posts', limit)
        posts = cache.get(cache_key)
        
        if posts is None:
            posts = BlogCacheManager.cache_popular_posts(limit)
        
        return posts
    
    @staticmethod
    def cache_recent_posts(limit=5):
        """Cache recent posts"""
        from .models import BlogPost
        
        posts = BlogPost.objects.filter(
            status='published'
        ).order_by('-published_date')[:limit]
        
        cache_key = BlogCacheManager.get_cache_key('recent_posts', limit)
        cache.set(
            cache_key,
            list(posts),
            BlogCacheManager.CACHE_TIMEOUTS['recent_posts']
        )
        return list(posts)
    
    @staticmethod
    def get_cached_recent_posts(limit=5):
        """Get cached recent posts"""
        cache_key = BlogCacheManager.get_cache_key('recent_posts', limit)
        posts = cache.get(cache_key)
        
        if posts is None:
            posts = BlogCacheManager.cache_recent_posts(limit)
        
        return posts
    
    @staticmethod
    def cache_featured_posts(limit=3):
        """Cache featured posts"""
        from .models import BlogPost
        
        posts = BlogPost.objects.filter(
            status='published',
            featured=True
        ).order_by('-published_date')[:limit]
        
        cache_key = BlogCacheManager.get_cache_key('featured_posts', limit)
        cache.set(
            cache_key,
            list(posts),
            BlogCacheManager.CACHE_TIMEOUTS['featured_posts']
        )
        return list(posts)
    
    @staticmethod
    def get_cached_featured_posts(limit=3):
        """Get cached featured posts"""
        cache_key = BlogCacheManager.get_cache_key('featured_posts', limit)
        posts = cache.get(cache_key)
        
        if posts is None:
            posts = BlogCacheManager.cache_featured_posts(limit)
        
        return posts
    
    @staticmethod
    def cache_search_results(query, results):
        """Cache search results"""
        cache_key = BlogCacheManager.get_cache_key('search', query)
        cache.set(
            cache_key,
            results,
            BlogCacheManager.CACHE_TIMEOUTS['search_results']
        )
        return cache_key
    
    @staticmethod
    def get_cached_search_results(query):
        """Get cached search results"""
        cache_key = BlogCacheManager.get_cache_key('search', query)
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_blog_caches():
        """Invalidate all blog-related caches"""
        cache_patterns = [
            'blog_post:*',
            'blog_list:*',
            'categories',
            'tags',
            'popular_posts:*',
            'recent_posts:*',
            'featured_posts:*',
            'search:*',
        ]
        
        # Note: This is a simplified version
        # In production, you might want to use cache versioning
        # or a more sophisticated cache invalidation strategy
        for pattern in cache_patterns:
            try:
                cache.delete_pattern(pattern)
            except AttributeError:
                # Fallback for cache backends that don't support delete_pattern
                pass
    
    @staticmethod
    def warm_cache():
        """Warm up the cache with commonly accessed data"""
        # Cache categories
        BlogCacheManager.cache_categories()
        
        # Cache popular tags
        BlogCacheManager.cache_popular_tags()
        
        # Cache popular posts
        BlogCacheManager.cache_popular_posts()
        
        # Cache recent posts
        BlogCacheManager.cache_recent_posts()
        
        # Cache featured posts
        BlogCacheManager.cache_featured_posts()


class LazyLoadManager:
    """Manages lazy loading for images and content"""
    
    @staticmethod
    def process_content_for_lazy_loading(content):
        """Process HTML content to add lazy loading attributes"""
        import re
        
        # Add lazy loading to images
        img_pattern = r'<img([^>]*?)src="([^"]*)"([^>]*?)>'
        
        def replace_img(match):
            before_src = match.group(1)
            src_url = match.group(2)
            after_src = match.group(3)
            
            # Don't add lazy loading to small images or data URLs
            if src_url.startswith('data:') or 'lazy' in before_src + after_src:
                return match.group(0)
            
            return f'<img{before_src}src="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 1 1\'%3E%3C/svg%3E" data-src="{src_url}" class="lazy"{after_src}>'
        
        return re.sub(img_pattern, replace_img, content)
    
    @staticmethod
    def generate_placeholder_image(width=800, height=400, text="Loading..."):
        """Generate a placeholder image SVG"""
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
            <rect width="100%" height="100%" fill="#f0f0f0"/>
            <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#999" font-family="Arial, sans-serif" font-size="16">{text}</text>
        </svg>'''
        
        import base64
        return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"


class PerformanceMiddleware:
    """Middleware for performance optimizations"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Add performance headers
        response = self.get_response(request)
        
        # Add caching headers for static content
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
        
        # Add compression hint
        if 'gzip' not in response.get('Content-Encoding', ''):
            response['Vary'] = 'Accept-Encoding'
        
        return response

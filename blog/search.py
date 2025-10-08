"""
Enhanced search system for the Triple G Blog
Provides intelligent search with suggestions and filters
"""

from django.db.models import Q, Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from .models import BlogPost, Category, Tag
from .cache_utils import BlogCacheManager
import re


class BlogSearchEngine:
    """Advanced search engine for blog posts"""
    
    def __init__(self):
        self.cache_manager = BlogCacheManager()
    
    def search(self, query, filters=None, page=1, per_page=12):
        """
        Perform advanced search with filters
        
        Args:
            query (str): Search query
            filters (dict): Search filters (category, tags, date_range, etc.)
            page (int): Page number
            per_page (int): Results per page
        
        Returns:
            dict: Search results with metadata
        """
        if not query or not query.strip():
            return self._empty_results()
        
        query = query.strip()
        filters = filters or {}
        
        # Check cache first
        cache_key = f"{query}_{hash(str(filters))}_{page}_{per_page}"
        cached_results = self.cache_manager.get_cached_search_results(cache_key)
        if cached_results:
            return cached_results
        
        # Build base queryset
        queryset = BlogPost.objects.filter(status='published')
        
        # Apply search
        if hasattr(BlogPost, 'search_vector'):
            # Use PostgreSQL full-text search if available
            search_query = SearchQuery(query)
            queryset = queryset.annotate(
                search=SearchVector('title', 'content', 'excerpt'),
                rank=SearchRank('search', search_query)
            ).filter(search=search_query).order_by('-rank', '-published_date')
        else:
            # Fallback to basic search
            queryset = self._basic_search(queryset, query)
        
        # Apply filters
        queryset = self._apply_filters(queryset, filters)
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Paginate results
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Prepare results
        results = {
            'query': query,
            'results': list(page_obj.object_list),
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'suggestions': self._get_search_suggestions(query),
            'filters_applied': filters,
            'related_categories': self._get_related_categories(query),
            'related_tags': self._get_related_tags(query),
        }
        
        # Cache results
        self.cache_manager.cache_search_results(cache_key, results)
        
        return results
    
    def _basic_search(self, queryset, query):
        """Basic search implementation"""
        search_terms = query.split()
        
        # Build Q objects for each term
        q_objects = Q()
        for term in search_terms:
            q_objects |= (
                Q(title__icontains=term) |
                Q(content__icontains=term) |
                Q(excerpt__icontains=term) |
                Q(seo_meta_title__icontains=term) |
                Q(seo_meta_description__icontains=term) |
                Q(category__name__icontains=term) |
                Q(tags__name__icontains=term)
            )
        
        return queryset.filter(q_objects).distinct().order_by('-published_date')
    
    def _apply_filters(self, queryset, filters):
        """Apply search filters"""
        # Category filter
        if filters.get('category'):
            try:
                category = Category.objects.get(slug=filters['category'])
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                pass
        
        # Tags filter
        if filters.get('tags'):
            tag_slugs = filters['tags'] if isinstance(filters['tags'], list) else [filters['tags']]
            queryset = queryset.filter(tags__slug__in=tag_slugs)
        
        # Date range filter
        if filters.get('date_from'):
            queryset = queryset.filter(published_date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(published_date__lte=filters['date_to'])
        
        # Author filter
        if filters.get('author'):
            queryset = queryset.filter(author__username=filters['author'])
        
        # Featured filter
        if filters.get('featured'):
            queryset = queryset.filter(featured=True)
        
        # Sort order
        sort_by = filters.get('sort', 'relevance')
        if sort_by == 'date_desc':
            queryset = queryset.order_by('-published_date')
        elif sort_by == 'date_asc':
            queryset = queryset.order_by('published_date')
        elif sort_by == 'title':
            queryset = queryset.order_by('title')
        elif sort_by == 'views':
            queryset = queryset.order_by('-view_count')
        
        return queryset
    
    def _get_search_suggestions(self, query):
        """Get search suggestions based on query"""
        suggestions = []
        
        # Get similar titles
        similar_posts = BlogPost.objects.filter(
            status='published',
            title__icontains=query
        ).values_list('title', flat=True)[:5]
        
        suggestions.extend(similar_posts)
        
        # Get related categories
        related_categories = Category.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:3]
        
        suggestions.extend(related_categories)
        
        # Get related tags
        related_tags = Tag.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:3]
        
        suggestions.extend(related_tags)
        
        return list(set(suggestions))[:8]  # Remove duplicates and limit
    
    def _get_related_categories(self, query):
        """Get categories related to search query"""
        return Category.objects.filter(
            Q(name__icontains=query) |
            Q(blog_posts__title__icontains=query) |
            Q(blog_posts__content__icontains=query)
        ).annotate(
            post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
        ).filter(post_count__gt=0).distinct()[:5]
    
    def _get_related_tags(self, query):
        """Get tags related to search query"""
        return Tag.objects.filter(
            Q(name__icontains=query) |
            Q(blog_posts__title__icontains=query) |
            Q(blog_posts__content__icontains=query)
        ).annotate(
            post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
        ).filter(post_count__gt=0).distinct()[:8]
    
    def _empty_results(self):
        """Return empty search results"""
        return {
            'query': '',
            'results': [],
            'total_count': 0,
            'page': 1,
            'per_page': 12,
            'total_pages': 0,
            'has_next': False,
            'has_previous': False,
            'suggestions': [],
            'filters_applied': {},
            'related_categories': [],
            'related_tags': [],
        }
    
    def get_autocomplete_suggestions(self, query, limit=10):
        """Get autocomplete suggestions for search input"""
        if not query or len(query) < 2:
            return []
        
        suggestions = []
        
        # Blog post titles
        post_titles = BlogPost.objects.filter(
            status='published',
            title__icontains=query
        ).values_list('title', flat=True)[:limit//2]
        
        suggestions.extend([{'text': title, 'type': 'post'} for title in post_titles])
        
        # Categories
        categories = Category.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:3]
        
        suggestions.extend([{'text': cat, 'type': 'category'} for cat in categories])
        
        # Tags
        tags = Tag.objects.filter(
            name__icontains=query
        ).values_list('name', flat=True)[:3]
        
        suggestions.extend([{'text': tag, 'type': 'tag'} for tag in tags])
        
        return suggestions[:limit]
    
    def get_trending_searches(self, limit=10):
        """Get trending search queries"""
        # This would typically come from analytics data
        # For now, return popular categories and tags
        
        trending = []
        
        # Popular categories
        popular_categories = Category.objects.annotate(
            post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
        ).filter(post_count__gt=0).order_by('-post_count')[:limit//2]
        
        trending.extend([{'text': cat.name, 'type': 'category'} for cat in popular_categories])
        
        # Popular tags
        popular_tags = Tag.objects.annotate(
            post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
        ).filter(post_count__gt=0).order_by('-post_count')[:limit//2]
        
        trending.extend([{'text': tag.name, 'type': 'tag'} for tag in popular_tags])
        
        return trending[:limit]


class SearchAnalytics:
    """Analytics for search functionality"""
    
    @staticmethod
    def track_search(query, results_count, user=None, session_id=None):
        """Track search query and results"""
        from .analytics import AnalyticsManager
        
        # This would integrate with the analytics system
        # to track search queries and their effectiveness
        pass
    
    @staticmethod
    def get_popular_searches(days=30, limit=10):
        """Get popular search queries"""
        from .analytics import BlogAnalytics
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        return BlogAnalytics.objects.filter(
            event_type='search',
            timestamp__gte=start_date,
            search_query__isnull=False
        ).exclude(
            search_query=''
        ).values('search_query').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
    
    @staticmethod
    def get_search_conversion_rate(query):
        """Get conversion rate for a search query (clicks after search)"""
        # This would calculate how often users click on results
        # after performing a specific search
        pass

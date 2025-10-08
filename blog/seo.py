"""
SEO utilities for the Triple G Blog System
Handles structured data, meta tags, and SEO optimization
"""

import json
from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator


class SEOManager:
    """Manages SEO-related functionality for blog posts"""
    
    @staticmethod
    def generate_structured_data(blog_post, request):
        """Generate JSON-LD structured data for a blog post"""
        
        # Get absolute URL
        absolute_url = request.build_absolute_uri(blog_post.get_absolute_url())
        
        # Get author information
        author_name = blog_post.author.get_full_name() or blog_post.author.username
        
        # Get featured image URL
        featured_image = None
        if blog_post.featured_image:
            featured_image = request.build_absolute_uri(blog_post.featured_image.url)
        
        # Basic article structure
        structured_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": blog_post.title,
            "description": blog_post.excerpt or Truncator(strip_tags(blog_post.content)).words(30),
            "url": absolute_url,
            "datePublished": blog_post.published_date.isoformat() if blog_post.published_date else blog_post.created_date.isoformat(),
            "dateModified": blog_post.updated_date.isoformat(),
            "author": {
                "@type": "Person",
                "name": author_name
            },
            "publisher": {
                "@type": "Organization",
                "name": "Triple G BuildHub",
                "logo": {
                    "@type": "ImageObject",
                    "url": request.build_absolute_uri(settings.STATIC_URL + "images/logo.png")
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": absolute_url
            }
        }
        
        # Add featured image if available
        if featured_image:
            structured_data["image"] = {
                "@type": "ImageObject",
                "url": featured_image,
                "width": 1200,
                "height": 630
            }
        
        # Add category if available
        if blog_post.category:
            structured_data["articleSection"] = blog_post.category.name
        
        # Add tags if available
        if blog_post.tags.exists():
            structured_data["keywords"] = [tag.name for tag in blog_post.tags.all()]
        
        # Add reading time
        if hasattr(blog_post, 'reading_time') and blog_post.reading_time:
            structured_data["timeRequired"] = f"PT{blog_post.reading_time}M"
        
        return json.dumps(structured_data, indent=2)
    
    @staticmethod
    def generate_breadcrumb_data(blog_post, request):
        """Generate breadcrumb structured data"""
        
        breadcrumb_data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": request.build_absolute_uri(reverse('core:index'))
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Blog",
                    "item": request.build_absolute_uri(reverse('blog:blog_list'))
                }
            ]
        }
        
        # Add category if available
        if blog_post.category:
            breadcrumb_data["itemListElement"].append({
                "@type": "ListItem",
                "position": 3,
                "name": blog_post.category.name,
                "item": request.build_absolute_uri(reverse('blog:category_list', args=[blog_post.category.slug]))
            })
            
            breadcrumb_data["itemListElement"].append({
                "@type": "ListItem",
                "position": 4,
                "name": blog_post.title,
                "item": request.build_absolute_uri(blog_post.get_absolute_url())
            })
        else:
            breadcrumb_data["itemListElement"].append({
                "@type": "ListItem",
                "position": 3,
                "name": blog_post.title,
                "item": request.build_absolute_uri(blog_post.get_absolute_url())
            })
        
        return json.dumps(breadcrumb_data, indent=2)
    
    @staticmethod
    def generate_meta_tags(blog_post, request):
        """Generate meta tags for a blog post"""
        
        # Get absolute URL
        absolute_url = request.build_absolute_uri(blog_post.get_absolute_url())
        
        # Get description
        description = blog_post.seo_meta_description or blog_post.excerpt
        if not description:
            description = Truncator(strip_tags(blog_post.content)).words(25)
        
        # Get featured image
        featured_image = None
        if blog_post.featured_image:
            featured_image = request.build_absolute_uri(blog_post.featured_image.url)
        
        # Get author name
        author_name = blog_post.author.get_full_name() or blog_post.author.username
        
        meta_tags = {
            'title': blog_post.seo_meta_title or blog_post.title,
            'description': description,
            'canonical_url': absolute_url,
            'og_title': blog_post.title,
            'og_description': description,
            'og_url': absolute_url,
            'og_type': 'article',
            'og_site_name': 'Triple G BuildHub',
            'og_image': featured_image,
            'twitter_card': 'summary_large_image',
            'twitter_title': blog_post.title,
            'twitter_description': description,
            'twitter_image': featured_image,
            'article_author': author_name,
            'article_published_time': blog_post.published_date.isoformat() if blog_post.published_date else blog_post.created_date.isoformat(),
            'article_modified_time': blog_post.updated_date.isoformat(),
        }
        
        # Add category
        if blog_post.category:
            meta_tags['article_section'] = blog_post.category.name
        
        # Add tags
        if blog_post.tags.exists():
            meta_tags['article_tags'] = [tag.name for tag in blog_post.tags.all()]
        
        return meta_tags


class SitemapGenerator:
    """Generates sitemap data for blog posts"""
    
    @staticmethod
    def get_blog_urls():
        """Get all blog URLs for sitemap"""
        from .models import BlogPost
        
        urls = []
        
        # Get all published blog posts
        blog_posts = BlogPost.objects.filter(status='published').select_related('category')
        
        for post in blog_posts:
            urls.append({
                'location': post.get_absolute_url(),
                'lastmod': post.updated_date,
                'changefreq': 'weekly',
                'priority': 0.8
            })
        
        # Add blog list page
        urls.append({
            'location': reverse('blog:blog_list'),
            'lastmod': blog_posts.first().updated_date if blog_posts.exists() else None,
            'changefreq': 'daily',
            'priority': 0.9
        })
        
        return urls

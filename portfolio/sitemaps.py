"""
Sitemap configuration for Triple G Portfolio System
Generates XML sitemaps for search engine crawling
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project, Category


class ProjectSitemap(Sitemap):
    """Sitemap for individual project pages"""
    changefreq = "monthly"
    priority = 0.8
    
    def items(self):
        """Return all projects for sitemap"""
        return Project.objects.all().select_related('category')
    
    def lastmod(self, obj):
        """Return last modification date"""
        return obj.updated_at
    
    def priority(self, obj):
        """Dynamic priority based on project status and featured flag"""
        priority = 0.8
        
        # Higher priority for completed projects
        if obj.status == 'completed':
            priority += 0.1
            
        # Higher priority for featured projects
        if obj.featured:
            priority += 0.1
            
        return min(priority, 1.0)  # Cap at 1.0
    
    def changefreq(self, obj):
        """Dynamic change frequency based on project status"""
        if obj.status == 'completed':
            return 'monthly'
        elif obj.status == 'ongoing':
            return 'weekly'
        else:  # planned
            return 'weekly'


class ProjectCategorySitemap(Sitemap):
    """Sitemap for project category pages"""
    changefreq = "weekly"
    priority = 0.7
    
    def items(self):
        """Return all categories that have projects"""
        return Category.objects.filter(projects__isnull=False).distinct()
    
    def location(self, obj):
        """Return category filter URL"""
        return reverse('portfolio:project_list') + f"?category={obj.slug}"
    
    def lastmod(self, obj):
        """Return last modification date of most recent project in category"""
        latest_project = obj.projects.order_by('-updated_at').first()
        return latest_project.updated_at if latest_project else None


class PortfolioStaticSitemap(Sitemap):
    """Sitemap for static portfolio pages"""
    changefreq = "weekly"
    priority = 0.9
    
    def items(self):
        """Return static portfolio URLs"""
        return ['portfolio:project_list']
    
    def location(self, item):
        """Return URL for static pages"""
        return reverse(item)


# Sitemap registry for easy import
portfolio_sitemaps = {
    'projects': ProjectSitemap,
    'categories': ProjectCategorySitemap,
    'portfolio': PortfolioStaticSitemap,
}

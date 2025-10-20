"""
SEO utilities for the Triple G Portfolio System
Handles structured data, meta tags, and SEO optimization for projects
"""

import json
from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator


class PortfolioSEOManager:
    """Manages SEO-related functionality for portfolio projects"""
    
    @staticmethod
    def generate_structured_data(project, request):
        """Generate JSON-LD structured data for a project"""
        
        # Get absolute URL
        absolute_url = request.build_absolute_uri(project.get_absolute_url())
        
        # Get featured image URL
        featured_image = None
        if project.hero_image:
            featured_image = request.build_absolute_uri(project.hero_image.url)
        
        # Basic creative work structure for architecture projects
        structured_data = {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "@id": absolute_url,
            "name": project.title,
            "description": project.seo_meta_description or Truncator(strip_tags(project.description)).words(30),
            "url": absolute_url,
            "dateCreated": project.created_at.isoformat(),
            "dateModified": project.updated_at.isoformat(),
            "creator": {
                "@type": "Organization",
                "name": "Triple G Studio Design",
                "url": request.build_absolute_uri(reverse('core:index'))
            },
            "publisher": {
                "@type": "Organization",
                "name": "Triple G Studio Design",
                "logo": {
                    "@type": "ImageObject",
                    "url": request.build_absolute_uri(settings.STATIC_URL + "images/logo.png")
                }
            },
            "genre": project.category.name if project.category else "Architecture",
            "locationCreated": {
                "@type": "Place",
                "name": project.location
            },
            "additionalProperty": [
                {
                    "@type": "PropertyValue",
                    "name": "Project Status",
                    "value": project.get_status_display()
                },
                {
                    "@type": "PropertyValue", 
                    "name": "Size",
                    "value": project.size
                },
                {
                    "@type": "PropertyValue",
                    "name": "Duration", 
                    "value": project.duration
                },
                {
                    "@type": "PropertyValue",
                    "name": "Lead Architect",
                    "value": project.lead_architect
                },
                {
                    "@type": "PropertyValue",
                    "name": "Completion Year",
                    "value": str(project.year)
                }
            ]
        }
        
        # Add featured image if available
        if featured_image:
            structured_data["image"] = {
                "@type": "ImageObject",
                "url": featured_image,
                "width": 1200,
                "height": 630,
                "caption": project.hero_image_alt or f"{project.title} - Hero Image"
            }
        
        # Add completion date if project is completed
        if project.status == 'completed':
            structured_data["dateCompleted"] = project.completion_date.isoformat()
        
        return json.dumps(structured_data, indent=2)
    
    @staticmethod
    def generate_breadcrumb_data(project, request):
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
                    "name": "Portfolio",
                    "item": request.build_absolute_uri(reverse('portfolio:project_list'))
                }
            ]
        }
        
        # Add category if available
        if project.category:
            breadcrumb_data["itemListElement"].append({
                "@type": "ListItem",
                "position": 3,
                "name": project.category.name,
                "item": request.build_absolute_uri(reverse('portfolio:project_list') + f"?category={project.category.slug}")
            })
            
            breadcrumb_data["itemListElement"].append({
                "@type": "ListItem",
                "position": 4,
                "name": project.title,
                "item": request.build_absolute_uri(project.get_absolute_url())
            })
        else:
            breadcrumb_data["itemListElement"].append({
                "@type": "ListItem",
                "position": 3,
                "name": project.title,
                "item": request.build_absolute_uri(project.get_absolute_url())
            })
        
        return json.dumps(breadcrumb_data, indent=2)
    
    @staticmethod
    def generate_meta_tags(project, request):
        """Generate meta tags for a project"""
        
        # Get absolute URL
        absolute_url = request.build_absolute_uri(project.get_absolute_url())
        
        # Get description
        description = project.seo_meta_description
        if not description:
            description = Truncator(strip_tags(project.description)).words(25)
        
        # Get featured image
        featured_image = None
        if project.hero_image:
            featured_image = request.build_absolute_uri(project.hero_image.url)
        
        # Generate SEO-optimized title
        seo_title = project.seo_meta_title or f"{project.title} - {project.category.name if project.category else 'Architecture Project'} | Triple G Studio"
        
        meta_tags = {
            'title': seo_title,
            'description': description,
            'canonical_url': absolute_url,
            'og_title': project.title,
            'og_description': description,
            'og_url': absolute_url,
            'og_type': 'website',
            'og_site_name': 'Triple G Studio Design',
            'og_image': featured_image,
            'twitter_card': 'summary_large_image',
            'twitter_title': project.title,
            'twitter_description': description,
            'twitter_image': featured_image,
            'project_location': project.location,
            'project_year': str(project.year),
            'project_status': project.get_status_display(),
            'project_category': project.category.name if project.category else None,
            'project_architect': project.lead_architect,
        }
        
        # Add project-specific keywords
        keywords = [
            project.title,
            project.category.name if project.category else 'architecture',
            project.location,
            'Triple G Studio',
            'architecture',
            'design',
            'construction',
            str(project.year)
        ]
        
        # Add project stats as keywords
        if hasattr(project, 'stats'):
            for stat in project.stats.all():
                keywords.append(stat.label.lower())
        
        meta_tags['keywords'] = ', '.join(filter(None, keywords))
        
        return meta_tags

    @staticmethod
    def generate_organization_data(request):
        """Generate organization structured data for Triple G Studio"""
        
        organization_data = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Triple G Studio Design",
            "url": request.build_absolute_uri(reverse('core:index')),
            "logo": request.build_absolute_uri(settings.STATIC_URL + "images/logo.png"),
            "description": "Professional architecture and construction services specializing in residential and commercial projects.",
            "foundingDate": "2020",
            "serviceArea": {
                "@type": "Place",
                "name": "Philippines"
            },
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": "Architecture Services",
                "itemListElement": [
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service",
                            "name": "Residential Architecture",
                            "description": "Custom home design and construction"
                        }
                    },
                    {
                        "@type": "Offer", 
                        "itemOffered": {
                            "@type": "Service",
                            "name": "Commercial Architecture",
                            "description": "Office buildings and commercial spaces"
                        }
                    },
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service", 
                            "name": "Interior Design",
                            "description": "Complete interior design solutions"
                        }
                    }
                ]
            },
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "Customer Service",
                "url": request.build_absolute_uri(reverse('core:contact'))
            }
        }
        
        return json.dumps(organization_data, indent=2)


class PortfolioSitemapGenerator:
    """Generates sitemap data for portfolio projects"""
    
    @staticmethod
    def get_portfolio_urls():
        """Get all portfolio URLs for sitemap"""
        from .models import Project, Category
        
        urls = []
        
        # Get all projects
        projects = Project.objects.all().select_related('category')
        
        for project in projects:
            # Higher priority for completed and featured projects
            priority = 0.9 if project.featured else 0.8
            if project.status == 'completed':
                priority += 0.1
            
            urls.append({
                'location': project.get_absolute_url(),
                'lastmod': project.updated_at,
                'changefreq': 'monthly' if project.status == 'completed' else 'weekly',
                'priority': min(priority, 1.0)  # Cap at 1.0
            })
        
        # Add portfolio list page
        urls.append({
            'location': reverse('portfolio:project_list'),
            'lastmod': projects.first().updated_at if projects.exists() else None,
            'changefreq': 'weekly',
            'priority': 0.9
        })
        
        # Add category pages
        categories = Category.objects.all()
        for category in categories:
            urls.append({
                'location': reverse('portfolio:project_list') + f"?category={category.slug}",
                'lastmod': projects.filter(category=category).first().updated_at if projects.filter(category=category).exists() else None,
                'changefreq': 'weekly',
                'priority': 0.7
            })
        
        return urls

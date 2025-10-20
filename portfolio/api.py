from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Project, Category
import json


@require_http_methods(["GET"])
def project_list_api(request):
    """API endpoint for project list with filtering"""
    try:
        # Get filter parameters
        year_filter = request.GET.get('year', 'all')
        category_filter = request.GET.get('category', 'all')
        search_query = request.GET.get('search', '').strip()
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 12))
        
        # Start with published projects only (exclude drafts)
        projects = Project.objects.select_related('category').exclude(status='draft')
        
        # Apply filters
        if year_filter != 'all':
            try:
                year = int(year_filter)
                projects = projects.filter(year=year)
            except (ValueError, TypeError):
                pass
        
        if category_filter != 'all':
            if category_filter == 'featured':
                projects = projects.filter(featured=True)
            else:
                projects = projects.filter(category__slug=category_filter)
        
        if search_query:
            projects = projects.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(lead_architect__icontains=search_query)
            )
        
        # Order and paginate
        projects = projects.order_by('-featured', '-completion_date', '-created_at')
        paginator = Paginator(projects, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize projects
        projects_data = []
        for project in page_obj:
            project_data = {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'category': {
                    'name': project.category.name,
                    'slug': project.category.slug
                },
                'year': project.year,
                'location': project.location,
                'size': project.size,
                'duration': project.duration,
                'completion_date': project.completion_date.isoformat(),
                'lead_architect': project.lead_architect,
                'status': project.status,
                'status_display': project.get_status_display(),
                'featured': project.featured,
                'hero_image': project.hero_image.url if project.hero_image else None,
                'url': f'/portfolio/{project.id}/',
            }
            projects_data.append(project_data)
        
        return JsonResponse({
            'success': True,
            'projects': projects_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_projects': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def project_detail_api(request, project_id):
    """API endpoint for project detail"""
    try:
        project = Project.objects.select_related('category').prefetch_related(
            'images', 'stats', 'timeline'
        ).exclude(status='draft').get(id=project_id)
        
        # Serialize project with all related data
        project_data = {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'category': {
                'name': project.category.name,
                'slug': project.category.slug
            },
            'year': project.year,
            'location': project.location,
            'size': project.size,
            'duration': project.duration,
            'completion_date': project.completion_date.isoformat(),
            'lead_architect': project.lead_architect,
            'status': project.status,
            'status_display': project.get_status_display(),
            'featured': project.featured,
            'hero_image': project.hero_image.url if project.hero_image else None,
            'video': project.video.url if project.video else None,
            'images': [
                {
                    'id': img.id,
                    'image': img.image.url,
                    'alt_text': img.alt_text,
                    'order': img.order
                }
                for img in project.images.all()
            ],
            'stats': [
                {
                    'id': stat.id,
                    'label': stat.label,
                    'value': stat.value,
                    'order': stat.order
                }
                for stat in project.stats.all()
            ],
            'timeline': [
                {
                    'id': timeline.id,
                    'title': timeline.title,
                    'date': timeline.date.isoformat(),
                    'description': timeline.description,
                    'completed': timeline.completed,
                    'order': timeline.order
                }
                for timeline in project.timeline.all()
            ]
        }
        
        return JsonResponse({
            'success': True,
            'project': project_data
        })
        
    except Project.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def categories_api(request):
    """API endpoint for categories"""
    try:
        categories = Category.objects.all().order_by('name')
        categories_data = [
            {
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'project_count': cat.projects.exclude(status='draft').count()
            }
            for cat in categories
        ]
        
        return JsonResponse({
            'success': True,
            'categories': categories_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

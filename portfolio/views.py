from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
from .models import Project, Category, ProjectImage, ProjectStat, ProjectTimeline
from accounts.decorators import require_admin_role, allow_public_access

# Create your views here.

@require_admin_role
def projectmanagement(request):
    """Admin project management view"""
    # Get all projects with related data for admin management
    projects = Project.objects.select_related('category').prefetch_related(
        'images', 'stats', 'timeline'
    ).order_by('-created_at')
    
    # Get statistics for dashboard
    total_projects = projects.count()
    completed_projects = projects.filter(status='completed').count()
    ongoing_projects = projects.filter(status='ongoing').count()
    planned_projects = projects.filter(status='planned').count()
    featured_projects = projects.filter(featured=True).count()
    
    # Get categories for filtering
    categories = Category.objects.all().order_by('name')
    
    context = {
        'projects': projects,
        'categories': categories,
        'total_projects': total_projects,
        'completed_projects': completed_projects,
        'ongoing_projects': ongoing_projects,
        'planned_projects': planned_projects,
        'featured_projects': featured_projects,
    }
    
    return render(request, 'admin/projectmanagement.html', context)


@allow_public_access
def project_list(request):
    """Display list of projects with filtering and pagination"""
    # Get filter parameters
    year_filter = request.GET.get('year', 'all')
    category_filter = request.GET.get('category', 'all')
    search_query = request.GET.get('search', '').strip()
    
    # Start with all projects, optimizing queries
    projects = Project.objects.select_related('category').prefetch_related('images')
    
    # Apply filters
    if year_filter != 'all':
        try:
            year = int(year_filter)
            projects = projects.filter(year=year)
        except (ValueError, TypeError):
            pass  # Invalid year, ignore filter
    
    if category_filter != 'all':
        if category_filter == 'featured':
            projects = projects.filter(featured=True)
        else:
            projects = projects.filter(category__slug=category_filter)
    
    # Apply search
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(lead_architect__icontains=search_query)
        )
    
    # Order projects
    projects = projects.order_by('-featured', '-completion_date', '-created_at')
    
    # Pagination
    paginator = Paginator(projects, 12)  # Show 12 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for the template
    categories = Category.objects.all().order_by('name')
    years = Project.objects.values_list('year', flat=True).distinct().order_by('-year')
    
    context = {
        'page_obj': page_obj,
        'projects': page_obj,  # For template compatibility
        'categories': categories,
        'years': years,
        'current_year': year_filter,
        'current_category': category_filter,
        'search_query': search_query,
        'total_projects': paginator.count,
    }
    return render(request, 'portfolio/project-list.html', context)

@allow_public_access
def project_detail(request, project_id):
    """Display detailed view of a single project"""
    # Get project with all related data in optimized queries
    project = get_object_or_404(
        Project.objects.select_related('category').prefetch_related(
            'images', 'stats', 'timeline'
        ),
        id=project_id
    )
    
    # Get related projects (same category, excluding current)
    related_projects = Project.objects.filter(
        category=project.category
    ).exclude(id=project.id).select_related('category')[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects,
        'project_images': project.images.all(),
        'project_stats': project.stats.all(),
        'project_timeline': project.timeline.all(),
    }
    
    return render(request, 'portfolio/project-detail.html', context)


@require_admin_role
@require_http_methods(["POST"])
def create_project(request):
    """Create a new project with milestones"""
    try:
        with transaction.atomic():
            # Create the main project
            project = Project.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                category_id=request.POST.get('category'),
                year=int(request.POST.get('year')),
                location=request.POST.get('location'),
                size=request.POST.get('size'),
                duration=request.POST.get('duration'),
                completion_date=request.POST.get('completion_date'),
                lead_architect=request.POST.get('lead_architect'),
                status=request.POST.get('status', 'planned'),
                featured=request.POST.get('featured') == 'on',
            )
            
            # Handle hero image upload
            if request.FILES.get('hero_image'):
                project.hero_image = request.FILES['hero_image']
            
            # Handle video upload
            if request.FILES.get('video'):
                project.video = request.FILES['video']
            
            # Save project with uploaded files
            project.save()
            
            # Handle gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for i, image in enumerate(gallery_images):
                ProjectImage.objects.create(
                    project=project,
                    image=image,
                    alt_text=f"{project.title} - Image {i+1}",
                    order=i
                )
            
            # Handle milestones
            milestone_titles = request.POST.getlist('milestone_title[]')
            milestone_dates = request.POST.getlist('milestone_date[]')
            milestone_descriptions = request.POST.getlist('milestone_description[]')
            
            for i, (title, date, description) in enumerate(zip(milestone_titles, milestone_dates, milestone_descriptions)):
                if title and date:  # Only create if title and date are provided
                    ProjectTimeline.objects.create(
                        project=project,
                        title=title,
                        date=date,
                        description=description or '',
                        order=i
                    )
            
            messages.success(request, f'Project "{project.title}" created successfully!')
            return redirect('portfolio:projectmanagement')
            
    except Exception as e:
        messages.error(request, f'Error creating project: {str(e)}')
        return redirect('portfolio:projectmanagement')


@require_admin_role
@require_http_methods(["POST"])
def edit_project(request, project_id):
    """Edit an existing project"""
    try:
        project = get_object_or_404(Project, id=project_id)
        
        with transaction.atomic():
            # Update project fields
            project.title = request.POST.get('title')
            project.description = request.POST.get('description')
            project.category_id = request.POST.get('category')
            project.year = int(request.POST.get('year'))
            project.location = request.POST.get('location')
            project.size = request.POST.get('size')
            project.duration = request.POST.get('duration')
            project.completion_date = request.POST.get('completion_date')
            project.lead_architect = request.POST.get('lead_architect')
            project.status = request.POST.get('status', 'planned')
            project.featured = request.POST.get('featured') == 'on'
            
            # Handle hero image upload
            if request.FILES.get('hero_image'):
                project.hero_image = request.FILES['hero_image']
            
            # Handle video upload
            if request.FILES.get('video'):
                project.video = request.FILES['video']
            
            project.save()
            
            # Update milestones (clear and recreate for simplicity)
            project.timeline.all().delete()
            
            milestone_titles = request.POST.getlist('milestone_title[]')
            milestone_dates = request.POST.getlist('milestone_date[]')
            milestone_descriptions = request.POST.getlist('milestone_description[]')
            
            for i, (title, date, description) in enumerate(zip(milestone_titles, milestone_dates, milestone_descriptions)):
                if title and date:
                    ProjectTimeline.objects.create(
                        project=project,
                        title=title,
                        date=date,
                        description=description or '',
                        order=i
                    )
            
            messages.success(request, f'Project "{project.title}" updated successfully!')
            return redirect('portfolio:projectmanagement')
            
    except Exception as e:
        messages.error(request, f'Error updating project: {str(e)}')
        return redirect('portfolio:projectmanagement')


@require_admin_role
@require_http_methods(["POST"])
def delete_project(request, project_id):
    """Delete a project"""
    try:
        project = get_object_or_404(Project, id=project_id)
        project_title = project.title
        project.delete()
        messages.success(request, f'Project "{project_title}" deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting project: {str(e)}')
    
    return redirect('portfolio:projectmanagement')


@require_admin_role
def get_project_data(request, project_id):
    """Get project data for editing (AJAX endpoint)"""
    try:
        project = get_object_or_404(
            Project.objects.prefetch_related('timeline'),
            id=project_id
        )
        
        data = {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'category': project.category.id,
            'year': project.year,
            'location': project.location,
            'size': project.size,
            'duration': project.duration,
            'completion_date': project.completion_date.strftime('%Y-%m-%d'),
            'lead_architect': project.lead_architect,
            'status': project.status,
            'featured': project.featured,
            'milestones': [
                {
                    'title': milestone.title,
                    'date': milestone.date.strftime('%Y-%m-%d'),
                    'description': milestone.description
                }
                for milestone in project.timeline.all()
            ]
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_admin_role
@require_http_methods(["POST"])
def save_draft(request):
    """Save project as draft"""
    try:
        # For now, just save as regular project with 'planned' status
        # You can extend this to have a separate draft system
        return create_project(request)
    except Exception as e:
        messages.error(request, f'Error saving draft: {str(e)}')
        return redirect('portfolio:projectmanagement')


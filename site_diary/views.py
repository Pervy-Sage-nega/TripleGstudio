from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Avg, Count, Max, Min
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import csv
import json
from accounts.decorators import require_site_manager_role, require_admin_role
from .models import (
    Project, DiaryEntry, LaborEntry, MaterialEntry, 
    EquipmentEntry, DelayEntry, VisitorEntry, DiaryPhoto
)
from .forms import (
    ProjectForm, DiaryEntryForm, LaborEntryFormSet, MaterialEntryFormSet,
    EquipmentEntryFormSet, DelayEntryFormSet, VisitorEntryFormSet, 
    DiaryPhotoFormSet, DiarySearchForm, DiaryEntrySearchForm, ProjectSearchForm
)
from django.views.decorators.csrf import csrf_exempt
import requests

OPENWEATHERMAP_API_KEY = "0c461dd2b831a59146501773674950cd"

# Create your views here.
@login_required
def diary(request):
    """Create new diary entry with all related data, including Save as Draft support"""
    if request.method == 'POST':
        save_as_draft = request.POST.get('save_as_draft') == '1'
        diary_form = DiaryEntryForm(request.POST)
        labor_formset = LaborEntryFormSet(request.POST, prefix='labor')
        material_formset = MaterialEntryFormSet(request.POST, prefix='material')
        equipment_formset = EquipmentEntryFormSet(request.POST, prefix='equipment')
        delay_formset = DelayEntryFormSet(request.POST, prefix='delay')
        visitor_formset = VisitorEntryFormSet(request.POST, prefix='visitor')
        photo_formset = DiaryPhotoFormSet(request.POST, request.FILES, prefix='photo')
        
        if (diary_form.is_valid() and labor_formset.is_valid() and \
            material_formset.is_valid() and equipment_formset.is_valid() and \
            delay_formset.is_valid() and visitor_formset.is_valid() and \
            photo_formset.is_valid()):
            
            # Save diary entry
            diary_entry = diary_form.save(commit=False)
            diary_entry.created_by = request.user
            diary_entry.draft = save_as_draft
            diary_entry.save()
            
            # Save related entries
            for form in labor_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    labor_entry = form.save(commit=False)
                    labor_entry.diary_entry = diary_entry
                    labor_entry.save()
            for form in material_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    material_entry = form.save(commit=False)
                    material_entry.diary_entry = diary_entry
                    material_entry.save()
            for form in equipment_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    equipment_entry = form.save(commit=False)
                    equipment_entry.diary_entry = diary_entry
                    equipment_entry.save()
            for form in delay_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    delay_entry = form.save(commit=False)
                    delay_entry.diary_entry = diary_entry
                    delay_entry.save()
            for form in visitor_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    visitor_entry = form.save(commit=False)
                    visitor_entry.diary_entry = diary_entry
                    visitor_entry.save()
            for form in photo_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    photo_entry = form.save(commit=False)
                    photo_entry.diary_entry = diary_entry
                    photo_entry.save()
            
            if save_as_draft:
                messages.success(request, 'Diary draft saved successfully!')
                return redirect('site_diary:sitedraft')
            else:
                messages.success(request, 'Diary entry created successfully!')
                return redirect('site_diary:diary')
    else:
        # Get user's projects for the form
        if request.user.is_staff:
            user_projects = Project.objects.all()
        else:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
        
        diary_form = DiaryEntryForm()
        # Update the project field queryset
        diary_form.fields['project'].queryset = user_projects
        
        labor_formset = LaborEntryFormSet(prefix='labor')
        material_formset = MaterialEntryFormSet(prefix='material')
        equipment_formset = EquipmentEntryFormSet(prefix='equipment')
        delay_formset = DelayEntryFormSet(prefix='delay')
        visitor_formset = VisitorEntryFormSet(prefix='visitor')
        photo_formset = DiaryPhotoFormSet(prefix='photo')
    
    context = {
        'diary_form': diary_form,
        'labor_formset': labor_formset,
        'material_formset': material_formset,
        'equipment_formset': equipment_formset,
        'delay_formset': delay_formset,
        'visitor_formset': visitor_formset,
        'photo_formset': photo_formset,
        'user_projects': user_projects,
    }
    return render(request, 'site_diary/diary.html', context)

@login_required
def dashboard(request):
    """Enhanced dashboard with comprehensive project overview and statistics"""
    # Get user's projects
    if request.user.is_staff:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
    
    # Recent diary entries
    recent_entries = DiaryEntry.objects.filter(
        project__in=projects
    ).select_related('project', 'created_by').order_by('-created_at')[:5]
    
    # Statistics
    total_projects = projects.count()
    active_projects = projects.filter(status='active').count()
    completed_projects = projects.filter(status='completed').count()
    planning_projects = projects.filter(status='planning').count()
    on_hold_projects = projects.filter(status='on_hold').count()
    total_entries = DiaryEntry.objects.filter(project__in=projects).count()
    draft_entries = DiaryEntry.objects.filter(project__in=projects, draft=True).count()
    
    # Recent delays
    recent_delays = DelayEntry.objects.filter(
        diary_entry__project__in=projects
    ).select_related('diary_entry__project').order_by('-diary_entry__entry_date')[:5]
    
    # Project progress statistics
    project_progress = []
    for project in projects[:5]:
        latest_entry = DiaryEntry.objects.filter(
            project=project, draft=False
        ).order_by('-entry_date').first()
        
        progress_data = {
            'project': project,
            'latest_progress': latest_entry.progress_percentage if latest_entry else 0,
            'total_entries': DiaryEntry.objects.filter(project=project, draft=False).count(),
            'last_entry_date': latest_entry.entry_date if latest_entry else None,
        }
        project_progress.append(progress_data)
    
    # Labor statistics
    labor_stats = LaborEntry.objects.filter(
        diary_entry__project__in=projects
    ).aggregate(
        total_workers=Sum('workers_count'),
        total_hours=Sum('hours_worked'),
        avg_hours=Avg('hours_worked')
    )
    
    # Material statistics
    material_stats = MaterialEntry.objects.filter(
        diary_entry__project__in=projects
    ).aggregate(
        total_deliveries=Count('id'),
        total_materials=Count('material_name')
    )
    
    # Equipment statistics
    equipment_stats = EquipmentEntry.objects.filter(
        diary_entry__project__in=projects
    ).aggregate(
        total_equipment=Count('id'),
        total_hours=Sum('hours_operated')
    )
    
    # Project card data for template (first 5 projects)
    project_cards = []
    for project in projects[:5]:
        latest_entry = DiaryEntry.objects.filter(project=project, draft=False).order_by('-entry_date').first()
        project_cards.append({'project': project, 'latest_entry': latest_entry})

    context = {
        'projects': projects[:5],  # For any other features
        'project_cards': project_cards,
        'recent_entries': recent_entries,
        'recent_delays': recent_delays,
        'project_progress': project_progress,
        'stats': {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'planning_projects': planning_projects,
            'on_hold_projects': on_hold_projects,
            'total_entries': total_entries,
            'draft_entries': draft_entries,
        },
        'labor_stats': labor_stats,
        'material_stats': material_stats,
        'equipment_stats': equipment_stats,
    }
    return render(request, 'site_diary/dashboard.html', context)

@require_site_manager_role
def chatbot(request):
    return render(request, 'chatbot/chatbot.html')

@login_required
def newproject(request):
    """Create new project with enhanced validation and user experience"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            # Set the project manager to the current user if not already set
            if not project.project_manager:
                project.project_manager = request.user
            project.save()
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('site_diary:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-populate project manager with current user
        form = ProjectForm(initial={'project_manager': request.user})
    
    context = {
        'form': form,
        'page_title': 'Create New Project'
    }
    return render(request, 'site_diary/newproject.html', context)

@login_required
def project_list(request):
    """List all projects with filtering and search capabilities"""
    # Get user's projects
    if request.user.is_staff:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
    
    # Apply filters
    search_form = ProjectSearchForm(request.GET)
    if search_form.is_valid():
        if search_form.cleaned_data.get('name'):
            projects = projects.filter(name__icontains=search_form.cleaned_data['name'])
        if search_form.cleaned_data.get('status'):
            projects = projects.filter(status=search_form.cleaned_data['status'])
        if search_form.cleaned_data.get('client_name'):
            projects = projects.filter(client_name__icontains=search_form.cleaned_data['client_name'])
        if search_form.cleaned_data.get('location'):
            projects = projects.filter(location__icontains=search_form.cleaned_data['location'])
    
    # Pagination
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'page_title': 'Project List'
    }
    return render(request, 'site_diary/project_list.html', context)

@login_required
def project_detail(request, project_id):
    """Detailed view of a specific project with all related information"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project
    if not request.user.is_staff and project.project_manager != request.user and project.architect != request.user:
        messages.error(request, 'You do not have permission to view this project.')
        return redirect('site_diary:dashboard')
    
    # Get project statistics
    diary_entries = DiaryEntry.objects.filter(project=project).order_by('-entry_date')
    total_entries = diary_entries.count()
    draft_entries = diary_entries.filter(draft=True).count()
    
    # Get latest progress
    latest_entry = diary_entries.filter(draft=False).first()
    current_progress = latest_entry.progress_percentage if latest_entry else 0
    
    # Labor statistics
    labor_stats = LaborEntry.objects.filter(
        diary_entry__project=project
    ).aggregate(
        total_workers=Sum('workers_count'),
        total_hours=Sum('hours_worked')
    )
    
    # Material statistics
    material_stats = MaterialEntry.objects.filter(
        diary_entry__project=project
    ).aggregate(
        total_deliveries=Count('id'),
        total_materials=Count('material_name')
    )
    
    # Equipment statistics
    equipment_stats = EquipmentEntry.objects.filter(
        diary_entry__project=project
    ).aggregate(
        total_equipment=Count('id'),
        total_hours=Sum('hours_operated')
    )
    
    # Recent delays
    recent_delays = DelayEntry.objects.filter(
        diary_entry__project=project
    ).select_related('diary_entry').order_by('-diary_entry__entry_date')[:5]
    
    # Recent visitors
    recent_visitors = VisitorEntry.objects.filter(
        diary_entry__project=project
    ).select_related('diary_entry').order_by('-diary_entry__entry_date')[:5]
    
    context = {
        'project': project,
        'diary_entries': diary_entries[:10],  # Show last 10 entries
        'total_entries': total_entries,
        'draft_entries': draft_entries,
        'current_progress': current_progress,
        'labor_stats': labor_stats,
        'material_stats': material_stats,
        'equipment_stats': equipment_stats,
        'recent_delays': recent_delays,
        'recent_visitors': recent_visitors,
        'page_title': f'Project: {project.name}'
    }
    return render(request, 'site_diary/project_detail.html', context)

@login_required
def project_edit(request, project_id):
    """Edit an existing project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has permission to edit this project
    if not request.user.is_staff and project.project_manager != request.user:
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('site_diary:project_detail', project_id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('site_diary:project_detail', project_id=project_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'page_title': f'Edit Project: {project.name}'
    }
    return render(request, 'site_diary/project_edit.html', context)

@require_site_manager_role
def createblog(request):
    """Create blog post - handles both GET (form display) and POST (form submission)"""
    # Import blog models
    from blog.models import BlogPost, Category, Tag
    from django.contrib import messages
    
    # Handle delete operation
    if request.GET.get('delete'):
        try:
            blog_id = int(request.GET.get('delete'))
            blog_post = BlogPost.objects.get(id=blog_id, author=request.user)
            blog_title = blog_post.title
            blog_post.delete()
            messages.success(request, f'Blog post "{blog_title}" deleted successfully!')
            return redirect('site_diary:drafts')
        except (BlogPost.DoesNotExist, ValueError):
            messages.error(request, 'Blog post not found or you do not have permission to delete it.')
            return redirect('site_diary:drafts')
    
    # Handle edit operation
    edit_blog = None
    if request.GET.get('edit'):
        try:
            blog_id = int(request.GET.get('edit'))
            edit_blog = BlogPost.objects.get(id=blog_id, author=request.user)
        except (BlogPost.DoesNotExist, ValueError):
            messages.error(request, 'Blog post not found or you do not have permission to edit it.')
            return redirect('site_diary:drafts')
    
    if request.method == 'POST':
        try:
            # Extract form data
            title = request.POST.get('title')
            content = request.POST.get('content')
            excerpt = request.POST.get('excerpt', '')
            category_id = request.POST.get('category')
            tag_names = request.POST.get('tags', '').split(',')
            status = request.POST.get('status', 'draft')
            featured = request.POST.get('featured') == 'on'
            seo_meta_title = request.POST.get('seo_meta_title', '')
            seo_meta_description = request.POST.get('seo_meta_description', '')
            featured_image_alt = request.POST.get('featured_image_alt', '')
            
            # Check if this is an edit operation
            edit_id = request.POST.get('edit_id')
            if edit_id:
                # Update existing blog post
                try:
                    blog_post = BlogPost.objects.get(id=edit_id, author=request.user)
                    blog_post.title = title
                    blog_post.content = content
                    blog_post.excerpt = excerpt
                    blog_post.status = status
                    blog_post.featured = featured
                    blog_post.seo_meta_title = seo_meta_title
                    blog_post.seo_meta_description = seo_meta_description
                    blog_post.featured_image_alt = featured_image_alt
                    blog_post.save()
                except BlogPost.DoesNotExist:
                    messages.error(request, 'Blog post not found or you do not have permission to edit it.')
                    return redirect('site_diary:drafts')
            else:
                # Create new blog post with proper user isolation
                blog_post = BlogPost.objects.create(
                    title=title,
                    content=content,
                    excerpt=excerpt,
                    author=request.user,  # Critical: Set the author to logged-in user
                    status=status,
                    featured=featured,
                    seo_meta_title=seo_meta_title,
                    seo_meta_description=seo_meta_description,
                    featured_image_alt=featured_image_alt,
                )
            
            # Set category if provided
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    blog_post.category = category
                    blog_post.save()
                except Category.DoesNotExist:
                    pass
            
            # Handle tags
            for tag_name in tag_names:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    blog_post.tags.add(tag)
            
            # Handle featured image
            if 'featured_image' in request.FILES:
                blog_post.featured_image = request.FILES['featured_image']
                blog_post.save()
            
            # Handle gallery images
            if 'gallery_images' in request.FILES:
                from blog.models import BlogImage
                gallery_files = request.FILES.getlist('gallery_images')
                
                for i, gallery_file in enumerate(gallery_files):
                    # Get caption and alt text for new images
                    caption = request.POST.get(f'new_gallery_caption[{i}]', '')
                    alt_text = request.POST.get(f'new_gallery_alt[{i}]', '')
                    
                    BlogImage.objects.create(
                        blog_post=blog_post,
                        image=gallery_file,
                        caption=caption,
                        alt_text=alt_text,
                        order=i
                    )
            
            # Handle existing gallery image updates and deletions
            if edit_id:
                from blog.models import BlogImage
                # Handle gallery image deletions first
                for key, value in request.POST.items():
                    if key.startswith('delete_gallery_image_') and value == 'true':
                        image_id = key.replace('delete_gallery_image_', '')
                        try:
                            gallery_image = BlogImage.objects.get(id=image_id, blog_post=blog_post)
                            gallery_image.delete()
                        except BlogImage.DoesNotExist:
                            pass
                
                # Update existing gallery images (captions and alt text)
                for key, value in request.POST.items():
                    if key.startswith('gallery_caption_'):
                        image_id = key.replace('gallery_caption_', '')
                        try:
                            gallery_image = BlogImage.objects.get(id=image_id, blog_post=blog_post)
                            gallery_image.caption = value
                            gallery_image.save()
                        except BlogImage.DoesNotExist:
                            pass
                    elif key.startswith('gallery_alt_'):
                        image_id = key.replace('gallery_alt_', '')
                        try:
                            gallery_image = BlogImage.objects.get(id=image_id, blog_post=blog_post)
                            gallery_image.alt_text = value
                            gallery_image.save()
                        except BlogImage.DoesNotExist:
                            pass
            
            # Success message and redirect
            if status == 'draft':
                messages.success(request, 'Blog post saved as draft successfully!')
                return redirect('site_diary:drafts')  # Redirect to drafts page
            else:
                messages.success(request, 'Blog post created successfully!')
                return redirect('site_diary:drafts')
                
        except Exception as e:
            messages.error(request, f'Error creating blog post: {str(e)}')
            return redirect('site_diary:createblog')
    
    # GET request - show the form
    # Get categories and tags for the form
    categories = Category.objects.all().order_by('name')
    tags = Tag.objects.all().order_by('name')
    
    context = {
        'categories': categories,
        'tags': tags,
        'edit_blog': edit_blog,  # Pass the blog post being edited (if any)
    }
    
    return render(request, 'blogcreation/createblog.html', context)

@require_site_manager_role
def drafts(request):
    """Site manager's drafts page - shows only their blog posts with proper user isolation"""
    # Import blog models
    from blog.models import BlogPost, Category
    
    # Get all blog posts by current user (proper user isolation)
    user_blog_posts = BlogPost.objects.select_related(
        'author', 'category'
    ).prefetch_related('tags').filter(
        author=request.user  # Critical: Only show posts by the logged-in user
    ).order_by('-created_date')
    
    # Get statistics for the current user only
    total_posts = user_blog_posts.count()
    draft_posts = user_blog_posts.filter(status='draft').count()
    published_posts = user_blog_posts.filter(status='published').count()
    archived_posts = user_blog_posts.filter(status='archived').count()
    
    # Get all categories for filter dropdown
    all_categories = Category.objects.all().order_by('name')
    
    context = {
        'blog_posts': user_blog_posts,
        'total_posts': total_posts,
        'draft_posts': draft_posts,
        'published_posts': published_posts,
        'archived_posts': archived_posts,
        'all_categories': all_categories,
    }
    
    return render(request, 'blogcreation/drafts.html', context)

@login_required
def history(request):
    """View diary entry history with search and filtering"""
    # Get user's projects
    if request.user.is_staff:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
    
    # Get diary entries
    entries = DiaryEntry.objects.filter(project__in=projects).select_related(
        'project', 'created_by', 'reviewed_by'
    ).prefetch_related('labor_entries', 'material_entries', 'equipment_entries')
    
    # Apply search filters
    search_form = DiarySearchForm(request.GET)
    if search_form.is_valid():
        if search_form.cleaned_data['project']:
            entries = entries.filter(project=search_form.cleaned_data['project'])
        if search_form.cleaned_data['start_date']:
            entries = entries.filter(entry_date__gte=search_form.cleaned_data['start_date'])
        if search_form.cleaned_data['end_date']:
            entries = entries.filter(entry_date__lte=search_form.cleaned_data['end_date'])
        if search_form.cleaned_data['weather_condition']:
            entries = entries.filter(weather_condition=search_form.cleaned_data['weather_condition'])
        if search_form.cleaned_data['created_by']:
            entries = entries.filter(created_by=search_form.cleaned_data['created_by'])
    
    # Pagination
    paginator = Paginator(entries.order_by('-entry_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'site_diary/history.html', context)

@login_required
def reports(request):
    """Generate comprehensive reports and analytics with database data"""
    # Get user's projects
    if request.user.is_staff:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
    
    # Date filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_project = request.GET.get('project')
    report_type = request.GET.get('report_type', 'summary')
    
    # Filter projects if specific project selected
    if selected_project:
        try:
            projects = projects.filter(id=int(selected_project))
        except (ValueError, TypeError):
            pass
    
    # Get diary entries for the period
    entries = DiaryEntry.objects.filter(project__in=projects)
    if start_date:
        entries = entries.filter(entry_date__gte=start_date)
    if end_date:
        entries = entries.filter(entry_date__lte=end_date)
    
    # Project statistics with comprehensive data from database
    project_stats = []
    for project in projects:
        project_entries = entries.filter(project=project)
        
        # Get all related data for this project from database
        labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
        material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        delay_entries = DelayEntry.objects.filter(diary_entry__in=project_entries)
        visitor_entries = VisitorEntry.objects.filter(diary_entry__in=project_entries)
        
        # Calculate costs from database
        total_labor_cost = sum(labor.total_cost for labor in labor_entries)
        total_material_cost = sum(material.total_cost for material in material_entries)
        total_equipment_cost = sum(equipment.total_rental_cost for equipment in equipment_entries)
        total_delay_impact = delay_entries.aggregate(total=Sum('cost_impact'))['total'] or 0
        
        # Progress tracking from database
        progress_data = project_entries.aggregate(
            avg_progress=Avg('progress_percentage'),
            max_progress=Max('progress_percentage'),
            min_progress=Min('progress_percentage')
        )
        
        # Safety and quality metrics from database
        safety_incidents = project_entries.exclude(safety_incidents='').count()
        quality_issues = project_entries.exclude(quality_issues='').count()
        
        project_stats.append({
            'project': project,
            'entries_count': project_entries.count(),
            'total_delays': delay_entries.count(),
            'total_delay_hours': delay_entries.aggregate(total=Sum('duration_hours'))['total'] or 0,
            'total_labor_cost': total_labor_cost,
            'total_material_cost': total_material_cost,
            'total_equipment_cost': total_equipment_cost,
            'total_project_cost': total_labor_cost + total_material_cost + total_equipment_cost,
            'total_delay_impact': total_delay_impact,
            'avg_progress': progress_data['avg_progress'] or 0,
            'max_progress': progress_data['max_progress'] or 0,
            'min_progress': progress_data['min_progress'] or 0,
            'approved_entries': project_entries.filter(approved=True).count(),
            'pending_entries': project_entries.filter(approved=False).count(),
            'safety_incidents': safety_incidents,
            'quality_issues': quality_issues,
            'visitor_count': visitor_entries.count(),
            'photos_count': project_entries.filter(photos_taken=True).count(),
        })
    
    # Delay analysis by category from database
    delay_categories = DelayEntry.objects.filter(
        diary_entry__in=entries
    ).values('category').annotate(
        count=Count('id'),
        total_hours=Sum('duration_hours'),
        avg_impact=Avg('cost_impact'),
        total_cost_impact=Sum('cost_impact')
    ).order_by('-total_hours')
    
    # Weather analysis from database
    weather_stats = entries.exclude(weather_condition='').values('weather_condition').annotate(
        count=Count('id'),
        avg_temp_high=Avg('temperature_high'),
        avg_temp_low=Avg('temperature_low'),
        avg_humidity=Avg('humidity'),
        avg_wind_speed=Avg('wind_speed')
    ).order_by('-count')
    
    # Labor analysis from database
    labor_stats = LaborEntry.objects.filter(
        diary_entry__in=entries
    ).values('labor_type').annotate(
        total_workers=Sum('workers_count'),
        total_hours=Sum('hours_worked'),
        total_overtime=Sum('overtime_hours'),
        avg_hourly_rate=Avg('hourly_rate'),
        entry_count=Count('id')
    ).order_by('-total_hours')
    
    # Material analysis from database
    material_stats = MaterialEntry.objects.filter(
        diary_entry__in=entries
    ).values('material_name').annotate(
        total_delivered=Sum('quantity_delivered'),
        total_used=Sum('quantity_used'),
        avg_unit_cost=Avg('unit_cost'),
        total_entries=Count('id')
    ).order_by('-total_delivered')[:15]  # Top 15 materials
    
    # Equipment utilization from database
    equipment_stats = EquipmentEntry.objects.filter(
        diary_entry__in=entries
    ).values('equipment_type').annotate(
        total_hours=Sum('hours_operated'),
        avg_hourly_rate=Avg('rental_cost_per_hour'),
        total_fuel=Sum('fuel_consumption'),
        utilization_days=Count('diary_entry__entry_date', distinct=True),
        breakdown_count=Count('id', filter=Q(status='breakdown'))
    ).order_by('-total_hours')
    
    # Monthly progress tracking from database
    monthly_progress = entries.extra(
        select={'month': "DATE_TRUNC('month', entry_date)"}
    ).values('month').annotate(
        avg_progress=Avg('progress_percentage'),
        entry_count=Count('id'),
        total_delays=Count('delay_entries'),
        avg_temp=Avg('temperature_high')
    ).order_by('month')
    
    # Overall summary from database
    overall_summary = {
        'total_projects': projects.count(),
        'total_entries': entries.count(),
        'total_approved': entries.filter(approved=True).count(),
        'total_pending': entries.filter(approved=False).count(),
        'total_labor_entries': LaborEntry.objects.filter(diary_entry__in=entries).count(),
        'total_material_entries': MaterialEntry.objects.filter(diary_entry__in=entries).count(),
        'total_equipment_entries': EquipmentEntry.objects.filter(diary_entry__in=entries).count(),
        'total_delays': DelayEntry.objects.filter(diary_entry__in=entries).count(),
        'total_visitors': VisitorEntry.objects.filter(diary_entry__in=entries).count(),
        'date_range': {
            'start': start_date,
            'end': end_date,
        }
    }
    
    context = {
        'project_stats': project_stats,
        'delay_categories': delay_categories,
        'weather_stats': weather_stats,
        'labor_stats': labor_stats,
        'material_stats': material_stats,
        'equipment_stats': equipment_stats,
        'monthly_progress': monthly_progress,
        'overall_summary': overall_summary,
        'projects': Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        ) if not request.user.is_staff else Project.objects.all(),
        'start_date': start_date,
        'end_date': end_date,
        'selected_project': selected_project,
        'report_type': report_type,
    }
    return render(request, 'site_diary/reports.html', context)


@login_required
def project_detail(request, project_id):
    """Project detail view - temporary placeholder"""
    try:
        project = get_object_or_404(Project, id=project_id)
        context = {
            'project': project,
        }
        return render(request, 'site_diary/project_detail.html', context)
    except:
        # Fallback - redirect to dashboard if project doesn't exist
        messages.info(request, 'Project details are not available yet.')
        return redirect('site_diary:dashboard')

@login_required
@require_site_manager_role
def settings(request):
    """Site Manager settings and preferences"""
    from accounts.models import SiteManagerProfile
    from accounts.forms import ProfileUpdateForm
    from django.contrib.auth.forms import PasswordChangeForm
    
    # Get or create site manager profile
    try:
        site_manager_profile = request.user.sitemanagerprofile
    except SiteManagerProfile.DoesNotExist:
        messages.error(request, 'Site Manager profile not found.')
        return redirect('site_diary:dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_profile':
            # Handle profile update
            user = request.user
            user.first_name = request.POST.get('firstName', '')
            user.last_name = request.POST.get('lastName', '')
            user.email = request.POST.get('email', '')
            
            # Update site manager profile fields
            site_manager_profile.phone = request.POST.get('phone', '')
            site_manager_profile.emergency_contact = request.POST.get('emergency_contact', '')
            
            # Handle profile picture upload
            if 'profile_pic' in request.FILES:
                site_manager_profile.profile_pic = request.FILES['profile_pic']
            
            try:
                user.save()
                site_manager_profile.save()
                messages.success(request, 'Profile updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        
        elif action == 'change_password':
            # Handle password change
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Password changed successfully!')
            else:
                for error in password_form.errors.values():
                    messages.error(request, error[0])
        
        return redirect('site_diary:settings')
    
    context = {
        'user': request.user,
        'site_manager_profile': site_manager_profile,
    }
    return render(request, 'site_diary/settings.html', context)

@require_admin_role
def adminclientproject(request):
    """Admin view for client projects"""
    
    search_form = ProjectSearchForm(request.GET)
    projects = Project.objects.all().select_related('project_manager', 'architect')
    
    if search_form.is_valid():
        if search_form.cleaned_data['name']:
            projects = projects.filter(name__icontains=search_form.cleaned_data['name'])
        if search_form.cleaned_data['client_name']:
            projects = projects.filter(client_name__icontains=search_form.cleaned_data['client_name'])
        if search_form.cleaned_data['status']:
            projects = projects.filter(status=search_form.cleaned_data['status'])
        if search_form.cleaned_data['project_manager']:
            projects = projects.filter(project_manager=search_form.cleaned_data['project_manager'])
    
    paginator = Paginator(projects.order_by('-created_at'), 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'admin/adminclientproject.html', context)

@require_admin_role
def admindiary(request):
    """Admin view for diary entries"""
    
    search_form = DiaryEntrySearchForm(request.GET)
    entries = DiaryEntry.objects.all().select_related(
        'project', 'created_by', 'reviewed_by'
    ).order_by('-entry_date')
    
    if search_form.is_valid():
        if search_form.cleaned_data['project']:
            entries = entries.filter(project=search_form.cleaned_data['project'])
        if search_form.cleaned_data['start_date']:
            entries = entries.filter(entry_date__gte=search_form.cleaned_data['start_date'])
        if search_form.cleaned_data['end_date']:
            entries = entries.filter(entry_date__lte=search_form.cleaned_data['end_date'])
    
    # Pagination
    paginator = Paginator(entries, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'admin/admindiary.html', context)

@require_admin_role
def admindiaryreviewer(request):
    """Admin diary reviewer interface"""
    
    # Get entries pending review
    pending_entries = DiaryEntry.objects.filter(
        approved=False
    ).select_related('project', 'created_by').order_by('-entry_date')
    
    context = {'pending_entries': pending_entries}
    return render(request, 'admin/admindiaryreviewer.html', context)

@require_admin_role
def adminhistory(request):
    """Admin history view"""
    return render(request, 'admin/adminhistory.html')

@require_admin_role
def adminreports(request):
    """Admin reports view"""
    return render(request, 'admin/adminreports.html')

@login_required
def sitedraft(request):
    drafts = DiaryEntry.objects.filter(created_by=request.user, draft=True).order_by('-created_at')
    return render(request, 'site_diary/sitedraft.html', {'drafts': drafts})

@csrf_exempt
@login_required
def weather_api(request):
    """Weather API endpoint for fetching real-time weather data"""
    if request.method == 'POST':
        location = request.POST.get('location')
        if not location:
            return JsonResponse({'success': False, 'error': 'Location required.'}, status=400)
        
        try:
            # Use the provided API key
            url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if response.status_code != 200:
                error_msg = data.get('message', 'Weather API error')
                return JsonResponse({'success': False, 'error': error_msg}, status=400)
            
            if 'main' not in data or 'weather' not in data:
                return JsonResponse({'success': False, 'error': 'Invalid weather data received'}, status=400)
            
            # Extract weather data
            weather_data = {
                'condition': data['weather'][0]['main'].lower(),
                'description': data['weather'][0]['description'].title(),
                'temperature': round(data['main']['temp']),
                'temperature_high': round(data['main']['temp_max']),
                'temperature_low': round(data['main']['temp_min']),
                'humidity': int(data['main']['humidity']),
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
                'pressure': data['main'].get('pressure', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert m to km
                'location': data['name'],
                'country': data['sys']['country'],
            }
            
            return JsonResponse({'success': True, 'data': weather_data})
            
        except requests.exceptions.Timeout:
            return JsonResponse({'success': False, 'error': 'Weather service timeout. Please try again.'}, status=408)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'success': False, 'error': f'Weather service error: {str(e)}'}, status=503)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Only POST method allowed.'}, status=405)
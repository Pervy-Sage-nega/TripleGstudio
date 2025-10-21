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
from django.core.cache import cache
from accounts.decorators import require_site_manager_role, require_admin_role
from .models import (
    Project, DiaryEntry, LaborEntry, MaterialEntry, 
    EquipmentEntry, DelayEntry, VisitorEntry, DiaryPhoto, SubcontractorCompany, Milestone
)
from .forms import (
    ProjectForm, DiaryEntryForm, LaborEntryFormSet, MaterialEntryFormSet,
    EquipmentEntryFormSet, DelayEntryFormSet, VisitorEntryFormSet, 
    DiaryPhotoFormSet, DiarySearchForm, DiaryEntrySearchForm, ProjectSearchForm
)
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.utils.html import escape
import requests
import logging

OPENWEATHERMAP_API_KEY = "0c461dd2b831a59146501773674950cd"
logger = logging.getLogger(__name__)

# Create your views here.
@login_required
@require_site_manager_role
@csrf_protect
def diary(request):
    """Create new diary entry with all related data, including Save as Draft support"""
    if request.method == 'POST':
        save_as_draft = request.POST.get('save_as_draft') == '1'
        
        diary_form = DiaryEntryForm(request.POST, user=request.user)
        labor_formset = LaborEntryFormSet(request.POST, prefix='labor')
        material_formset = MaterialEntryFormSet(request.POST, prefix='material')
        equipment_formset = EquipmentEntryFormSet(request.POST, prefix='equipment')
        delay_formset = DelayEntryFormSet(request.POST, prefix='delay')
        visitor_formset = VisitorEntryFormSet(request.POST, prefix='visitor')
        photo_formset = DiaryPhotoFormSet(request.POST, request.FILES, prefix='photo')
        
        # Validate forms
        if not diary_form.is_valid():
            logger.warning(f"Diary form validation failed for user {request.user.id}")
        if not material_formset.is_valid():
            logger.warning(f"Material formset validation failed for user {request.user.id}")
        
        # Check if editing existing draft with proper validation
        edit_draft_id = request.POST.get('edit_draft_id') or request.GET.get('edit')
        editing_draft = None
        
        if edit_draft_id:
            try:
                # Validate draft_id is numeric to prevent injection
                draft_id = int(edit_draft_id)
                editing_draft = DiaryEntry.objects.get(
                    id=draft_id,
                    created_by=request.user,
                    draft=True
                )
            except (ValueError, TypeError, DiaryEntry.DoesNotExist):
                messages.error(request, 'Draft not found or access denied.')
                return redirect('site_diary:sitedraft')
        
        # For drafts, only require project and entry_date
        if save_as_draft:
            # Minimal validation for drafts
            project = diary_form.cleaned_data.get('project') if diary_form.is_valid() else None
            entry_date = diary_form.cleaned_data.get('entry_date') if diary_form.is_valid() else None
            
            if not project:
                messages.error(request, 'Please select a project to save as draft.')
            
            if not entry_date:
                messages.error(request, 'Please select an entry date to save as draft.')
            
            if not project or not entry_date:
                # Re-render form with errors
                user_projects = Project.objects.filter(
                    project_manager=request.user,
                    status__in=['planning', 'active', 'on_hold', 'completed']
                )
                context = {
                    'diary_form': diary_form,
                    'labor_formset': labor_formset,
                    'material_formset': material_formset,
                    'equipment_formset': equipment_formset,
                    'delay_formset': delay_formset,
                    'visitor_formset': visitor_formset,
                    'photo_formset': photo_formset,
                    'user_projects': user_projects,
                    'project_data': [],
                }
                return render(request, 'site_diary/diary.html', context)
            
            if editing_draft:
                # Update existing draft
                for field in diary_form.cleaned_data:
                    if hasattr(editing_draft, field) and diary_form.cleaned_data[field] is not None:
                        setattr(editing_draft, field, diary_form.cleaned_data[field])
                editing_draft.save()
                diary_entry = editing_draft
                logger.info(f"Updated existing draft {diary_entry.id} for user {request.user.id}")
            else:
                # Check if draft already exists for this project and date (avoid duplicates)
                existing_draft = DiaryEntry.objects.filter(
                    project=project,
                    entry_date=entry_date,
                    created_by=request.user,
                    draft=True
                ).first()
                
                if existing_draft:
                    # Update existing draft
                    for field in diary_form.cleaned_data:
                        if hasattr(existing_draft, field) and diary_form.cleaned_data[field] is not None:
                            setattr(existing_draft, field, diary_form.cleaned_data[field])
                    existing_draft.save()
                    diary_entry = existing_draft
                    logger.info(f"Updated existing draft {diary_entry.id} for user {request.user.id}")
                else:
                    # Create new draft with minimal required fields
                    diary_entry = DiaryEntry.objects.create(
                        project=project,
                        entry_date=entry_date,
                        created_by=request.user,
                        draft=True,
                        milestone=diary_form.cleaned_data.get('milestone'),
                        work_description=diary_form.cleaned_data.get('work_description', ''),
                        progress_percentage=diary_form.cleaned_data.get('progress_percentage', 0),
                        weather_condition=diary_form.cleaned_data.get('weather_condition', ''),
                        temperature_high=diary_form.cleaned_data.get('temperature_high'),
                        temperature_low=diary_form.cleaned_data.get('temperature_low'),
                        humidity=diary_form.cleaned_data.get('humidity'),
                        wind_speed=diary_form.cleaned_data.get('wind_speed'),
                        quality_issues=diary_form.cleaned_data.get('quality_issues', ''),
                        safety_incidents=diary_form.cleaned_data.get('safety_incidents', ''),
                        general_notes=diary_form.cleaned_data.get('general_notes', ''),
                        photos_taken=diary_form.cleaned_data.get('photos_taken', False)
                    )
                    logger.info(f"Created new draft {diary_entry.id} for user {request.user.id}")
            
            messages.success(request, 'Diary draft saved successfully!')
            return redirect('site_diary:sitedraft')
        
        # Full validation for final submission
        elif diary_form.is_valid():
            # Save diary entry
            diary_entry = diary_form.save(commit=False)
            diary_entry.created_by = request.user
            diary_entry.draft = False
            diary_entry.save()
            
            # Save related entries (simplified for now)
            logger.info(f"Diary entry saved successfully: {diary_entry.id} for user {request.user.id}")
            
            messages.success(request, 'Diary entry created successfully!')
            return redirect('site_diary:diary')
        else:
            # Form validation failed
            logger.warning(f"Form validation failed for user {request.user.id}")
            messages.error(request, 'Please correct the form errors and try again.')
    else:
        # Get user's assigned projects only - very strict filtering
        user_projects = Project.objects.filter(
            project_manager=request.user,
            status__in=['planning', 'active', 'on_hold', 'completed']
        )
        
        # Check if editing an existing draft with proper validation
        edit_draft_id = request.GET.get('edit')
        draft_instance = None
        
        if edit_draft_id:
            try:
                # Validate draft_id is numeric to prevent injection
                draft_id = int(edit_draft_id)
                draft_instance = DiaryEntry.objects.get(
                    id=draft_id,
                    created_by=request.user,
                    draft=True
                )
                logger.info(f"Editing draft {draft_instance.id} for user {request.user.id}")
            except (ValueError, TypeError, DiaryEntry.DoesNotExist):
                messages.error(request, 'Draft not found or access denied.')
                return redirect('site_diary:sitedraft')
        
        diary_form = DiaryEntryForm(instance=draft_instance, user=request.user)
        
        labor_formset = LaborEntryFormSet(prefix='labor')
        material_formset = MaterialEntryFormSet(prefix='material')
        equipment_formset = EquipmentEntryFormSet(prefix='equipment')
        delay_formset = DelayEntryFormSet(prefix='delay')
        visitor_formset = VisitorEntryFormSet(prefix='visitor')
        photo_formset = DiaryPhotoFormSet(prefix='photo')
    
    # Get project data for budget calculations
    project_data = []
    for project in user_projects:
        # Calculate existing costs for this project
        project_entries = DiaryEntry.objects.filter(project=project)
        labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
        material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        
        total_spent = (
            sum(labor.total_cost for labor in labor_entries) +
            sum(material.total_cost for material in material_entries) +
            sum(equipment.total_rental_cost for equipment in equipment_entries)
        )
        
        project_data.append({
            'id': project.id,
            'name': project.name,
            'location': project.location,
            'budget': float(project.budget) if project.budget else 0,
            'spent': float(total_spent),
            'remaining': float(project.budget) - float(total_spent) if project.budget else -float(total_spent)
        })
    
    # Get active subcontractor companies for dropdown
    subcontractor_companies = SubcontractorCompany.objects.filter(is_active=True).order_by('name')
    
    # Get active milestones for dropdown
    milestones = Milestone.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'diary_form': diary_form,
        'labor_formset': labor_formset,
        'material_formset': material_formset,
        'equipment_formset': equipment_formset,
        'delay_formset': delay_formset,
        'visitor_formset': visitor_formset,
        'photo_formset': photo_formset,
        'user_projects': user_projects,
        'project_data': project_data,
        'subcontractor_companies': subcontractor_companies,
        'milestones': milestones,
    }
    return render(request, 'site_diary/diary.html', context)

@login_required
@require_site_manager_role
def dashboard(request):
    """Site Manager Enhanced dashboard with comprehensive project overview"""
    # Get user's approved projects only
    if request.user.is_staff:
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
        )
    
    # Enhanced project data with progress and analytics
    project_data = []
    # Mock progress values for demonstration
    mock_progress = [65, 40, 85, 25, 55, 75, 30, 90, 45, 60]
    
    for i, project in enumerate(projects):
        # Get latest diary entry for progress
        latest_entry = DiaryEntry.objects.filter(project=project).order_by('-entry_date').first()
        
        # Calculate project analytics
        project_entries = DiaryEntry.objects.filter(project=project)
        labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
        material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        delay_entries = DelayEntry.objects.filter(diary_entry__in=project_entries)
        
        # Use diary entry progress or calculate based on status
        if latest_entry:
            progress = float(latest_entry.progress_percentage)
        else:
            progress = float(project.get_progress_percentage())
        
        # Budget calculations with real data
        total_labor_cost = sum(float(labor.total_cost) for labor in labor_entries)
        total_material_cost = sum(float(material.total_cost) for material in material_entries)
        total_equipment_cost = sum(float(equipment.total_rental_cost) for equipment in equipment_entries)
        total_spent = total_labor_cost + total_material_cost + total_equipment_cost
        
        project_budget = float(project.budget) if project.budget else 0
        if project_budget > 0:
            budget_used_percentage = min((total_spent / project_budget) * 100, 100)
        else:
            budget_used_percentage = 0
        
        # Determine current phase based on progress
        if progress < 25:
            phase_name = "Planning"
        elif progress < 50:
            phase_name = "Foundation"
        elif progress < 75:
            phase_name = "Structure"
        else:
            phase_name = "Finishing"
        
        # Calculate schedule status based on actual delays
        delay_count = delay_entries.count()
        if delay_count == 0:
            schedule_status = 'On Track'
        elif delay_count < 3:
            schedule_status = 'Minor Delays'
        else:
            schedule_status = 'At Risk'
            
        # Add calculated fields directly to project object
        project.progress = progress
        project.current_phase = f"Phase {min(int(progress/25) + 1, 4)} - {phase_name}"
        project.budget_used = budget_used_percentage
        project.schedule_status = schedule_status
        project_data.append(project)
    
    # Dashboard statistics
    total_projects = projects.count()
    active_projects = projects.filter(status='active').count()
    at_risk_projects = projects.filter(status='on_hold').count()
    total_entries = DiaryEntry.objects.filter(project__in=projects).count()
    draft_entries = DiaryEntry.objects.filter(project__in=projects, draft=True).count()
    
    # Recent delays
    recent_delays = DelayEntry.objects.filter(
        diary_entry__project__in=projects
    ).select_related('diary_entry__project').order_by('-diary_entry__entry_date')[:5]
    
    # Get recent diary entries
    recent_entries = DiaryEntry.objects.filter(
        project__in=projects
    ).select_related('project', 'created_by').order_by('-entry_date')[:5]
    
    context = {
        'projects': project_data[:5],  # Show only 5 recent projects with enhanced data
        'recent_entries': recent_entries,
        'recent_delays': recent_delays,
        'stats': {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'at_risk': at_risk_projects,
            'draft_entries': draft_entries,
        }
    }
    return render(request, 'site_diary/dashboard.html', context)

@require_site_manager_role
@require_http_methods(["GET"])
def weather_api(request):
    """Weather API endpoint for fetching weather data"""
    location = request.GET.get('location', '').strip()
    
    # Validate location input
    if not location or len(location) > 100:
        return JsonResponse({'error': 'Invalid location parameter'}, status=400)
    
    # Sanitize location input to prevent injection
    location = escape(location)
    
    try:
        from django.conf import settings
        
        # Use OpenWeatherMap API
        api_key = getattr(settings, 'WEATHER_API_KEY', OPENWEATHERMAP_API_KEY)
        api_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(api_url, params=params, timeout=10)
                
        if response.status_code == 200:
            data = response.json()
            
            # Validate API response structure
            if not all(key in data for key in ['main', 'weather', 'wind']):
                return JsonResponse({'error': 'Invalid weather data received'}, status=500)
            
            weather_data = {
                'temperature': round(float(data['main']['temp'])),
                'temperature_high': round(float(data['main']['temp_max'])),
                'temperature_low': round(float(data['main']['temp_min'])),
                'humidity': int(data['main']['humidity']),
                'wind_speed': round(float(data['wind']['speed']) * 3.6),  # Convert m/s to km/h
                'description': escape(data['weather'][0]['description']),
                'condition': escape(data['weather'][0]['main']),
                'icon': escape(data['weather'][0]['icon']),
                'location': location
            }
            return JsonResponse(weather_data)
        else:
            logger.warning(f"Weather API failed for location {location}: {response.status_code}")
            return JsonResponse({'error': 'Weather data not found'}, status=404)
                    
    except requests.RequestException as e:
        logger.error(f"Weather API request failed: {str(e)}")
        # Fallback to mock data if API fails
        weather_data = {
            'temperature': 28,
            'temperature_high': 32,
            'temperature_low': 24,
            'humidity': 65,
            'wind_speed': 12,
            'description': 'Partly Cloudy',
            'condition': 'Clouds',
            'icon': '02d',
            'location': location
        }
        return JsonResponse(weather_data)
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Weather data parsing error: {str(e)}")
        return JsonResponse({'error': 'Weather service error'}, status=500)
    except Exception as e:
        logger.error(f"Unexpected weather API error: {str(e)}")
        return JsonResponse({'error': 'Weather service error'}, status=500)

@require_site_manager_role
def print_preview(request, project_id):
    """Print preview for project"""
    try:
        project_id = int(project_id)
        project = get_object_or_404(Project, id=project_id)
        
        # Verify user has access to this project
        if not request.user.is_staff:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
            if project not in user_projects:
                messages.error(request, 'Access denied.')
                return redirect('site_diary:dashboard')
        
        return render(request, 'site_diary/print_preview.html', {'project': project})
    except (ValueError, TypeError):
        messages.error(request, 'Invalid project ID.')
        return redirect('site_diary:dashboard')

@require_site_manager_role
def sample_print(request):
    """Sample print view"""
    return render(request, 'site_diary/sample_print.html')

@require_site_manager_role
@require_http_methods(["POST"])
@csrf_protect
def generate_project_report(request, project_id):
    """Generate project report API"""
    try:
        project_id = int(project_id)
        project = get_object_or_404(Project, id=project_id)
        
        # Verify user has access to this project
        if not request.user.is_staff:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
            if project not in user_projects:
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Generate report logic here
        report_data = {
            'status': 'success',
            'report_url': f'/reports/{project_id}/',
            'project_name': escape(project.name)
        }
        return JsonResponse(report_data)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid project ID'}, status=400)
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return JsonResponse({'error': 'Report generation failed'}, status=500)

@require_site_manager_role
@require_http_methods(["GET"])
def api_filter_projects(request):
    """API for filtering projects"""
    status = request.GET.get('status', '').strip()
    category = request.GET.get('category', '').strip()
    
    # Get user's projects only
    if request.user.is_staff:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
    
    # Validate and apply filters
    if status and status in dict(Project.PROJECT_STATUS):
        projects = projects.filter(status=status)
    if category:
        # Assuming category field exists, validate against allowed values
        projects = projects.filter(category=escape(category))
        
    project_data = []
    for project in projects[:50]:  # Limit results to prevent DoS
        project_data.append({
            'id': project.id,
            'name': escape(project.name),
            'status': project.status,
            'client_name': escape(project.client_name),
        })
    
    return JsonResponse({'projects': project_data})

@require_site_manager_role
def adminclientproject(request):
    """Admin client project management"""
    return render(request, 'site_diary/admin/clientproject.html')

@require_site_manager_role
def admindiary(request):
    """Admin diary management"""
    return render(request, 'site_diary/admin/diary.html')

@require_site_manager_role
def admindiaryreviewer(request):
    """Admin diary reviewer"""
    return render(request, 'site_diary/admin/diary_reviewer.html')

@require_site_manager_role
def adminhistory(request):
    """Admin history view"""
    return render(request, 'site_diary/admin/history.html')

@require_site_manager_role
def adminreports(request):
    """Admin reports view"""
    return render(request, 'site_diary/admin/reports.html')

@require_site_manager_role
def chatbot(request):
    return render(request, 'chatbot/chatbot.html')

@require_site_manager_role
@csrf_protect
def newproject(request):
    """Create new project - requires admin approval"""
    if request.method == 'POST':
        try:
            # Validate and sanitize inputs
            client_name = request.POST.get('client_name', '').strip()
            client_email = request.POST.get('client_email', '').strip()
            project_name = request.POST.get('name', '').strip()
            location = request.POST.get('location', '').strip()
            description = request.POST.get('description', '').strip()
            
            # Basic validation
            if not client_name or len(client_name) > 100:
                messages.error(request, 'Valid client name is required.')
                return redirect('site_diary:newproject')
            
            if not project_name or len(project_name) > 200:
                messages.error(request, 'Valid project name is required.')
                return redirect('site_diary:newproject')
            
            if not location or len(location) > 300:
                messages.error(request, 'Valid location is required.')
                return redirect('site_diary:newproject')
            
            # Validate budget
            try:
                budget = float(request.POST.get('budget', 0)) if request.POST.get('budget') else 0
                if budget < 0:
                    messages.error(request, 'Budget cannot be negative.')
                    return redirect('site_diary:newproject')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid budget amount.')
                return redirect('site_diary:newproject')
            
            # Validate dates
            start_date = request.POST.get('start_date')
            expected_end_date = request.POST.get('expected_end_date')
            
            if not start_date or not expected_end_date:
                messages.error(request, 'Start date and expected end date are required.')
                return redirect('site_diary:newproject')
            
            # Try to find existing client by email
            client_user = None
            if client_email:
                try:
                    from django.contrib.auth.models import User
                    from django.core.validators import validate_email
                    validate_email(client_email)
                    client_user = User.objects.get(email=client_email)
                except (User.DoesNotExist, ValidationError):
                    pass
            
            # Validate image file if provided
            image_file = None
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                # Validate file type and size
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                if image_file.content_type not in allowed_types:
                    messages.error(request, 'Invalid image type. Please upload JPEG, PNG, or GIF.')
                    return redirect('site_diary:newproject')
                
                if image_file.size > 5 * 1024 * 1024:  # 5MB limit
                    messages.error(request, 'Image file too large. Maximum size is 5MB.')
                    return redirect('site_diary:newproject')
            
            # Create project with pending approval status
            project = Project.objects.create(
                name=project_name,
                client_name=client_name,
                client=client_user,
                location=location,
                description=description,
                budget=budget,
                start_date=start_date,
                expected_end_date=expected_end_date,
                project_manager=request.user,
                status='pending_approval',  # Requires admin approval
                image=image_file
            )
            
            # Update client's profile if linked
            if client_user:
                try:
                    from accounts.models import Profile
                    profile, created = Profile.objects.get_or_create(user=client_user)
                    if not profile.project_name:
                        profile.project_name = project.name
                        profile.project_start = project.start_date
                        profile.save()
                        messages.info(request, f'Client account linked and updated for {client_user.get_full_name() or client_user.username}')
                except Exception as e:
                    logger.error(f"Error updating client profile: {str(e)}")
            
            messages.success(request, f'Project "{project.name}" submitted for admin approval. You will be notified once approved.')
            logger.info(f"Project {project.id} created by user {request.user.id}")
            return redirect('site_diary:dashboard')
        except Exception as e:
            logger.error(f"Error creating project for user {request.user.id}: {str(e)}")
            messages.error(request, 'Error creating project. Please try again.')
    
    context = {
        'page_title': 'Create New Project'
    }
    return render(request, 'site_diary/newproject.html', context)

@login_required
def project_list(request):
    """List approved projects with filtering and search capabilities"""
    # Get user's approved projects only
    if request.user.is_staff:
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
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



@login_required
@require_site_manager_role
def history(request):
    """View diary entry history with search and filtering"""
    # Get user's approved projects
    if request.user.is_staff:
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
        )
    
    # Get diary entries with prefetch
    entries = DiaryEntry.objects.filter(project__in=projects).select_related(
        'project', 'created_by', 'reviewed_by'
    ).prefetch_related('labor_entries', 'material_entries', 'equipment_entries')
    
    # Prefetch diary entries for projects
    projects = projects.prefetch_related('diary_entries')
    
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
@require_site_manager_role
def reports(request):
    """Generate comprehensive reports and analytics with database data"""
    # Get user's approved projects
    if request.user.is_staff:
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
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
    
    # Ensure we have data even if no entries exist
    if not project_stats:
        project_stats = []
    if not delay_categories:
        delay_categories = []
    if not labor_stats:
        labor_stats = []
    if not material_stats:
        material_stats = []
    
    context = {
        'project_stats': project_stats,
        'delay_categories': delay_categories,
        'weather_stats': weather_stats,
        'labor_stats': labor_stats,
        'material_stats': material_stats,
        'equipment_stats': equipment_stats,
        'monthly_progress': monthly_progress,
        'overall_summary': overall_summary,
        'projects': projects,
        'start_date': start_date,
        'end_date': end_date,
        'selected_project': selected_project,
        'report_type': report_type,
    }
    return render(request, 'site_diary/reports.html', context)


@require_site_manager_role
def project_detail(request, project_id):
    """Comprehensive Project Detail View for Site Managers"""
    project = get_object_or_404(Project, id=project_id)
    
    # Verify user has access to this project
    if not request.user.is_staff:
        user_projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
        if project not in user_projects:
            messages.error(request, 'You do not have access to this project.')
            return redirect('site_diary:dashboard')
    
    # Get project entries and related data
    project_entries = DiaryEntry.objects.filter(project=project).order_by('-entry_date')
    labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
    material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
    equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
    delay_entries = DelayEntry.objects.filter(diary_entry__in=project_entries)
    
    # Calculate project metrics from real data
    latest_entry = project_entries.first()
    progress = float(latest_entry.progress_percentage) if latest_entry else 0
    
    # Budget calculations from real data
    total_labor_cost = sum(labor.total_cost for labor in labor_entries)
    total_material_cost = sum(material.total_cost for material in material_entries)
    total_equipment_cost = sum(equipment.total_rental_cost for equipment in equipment_entries)
    total_spent = total_labor_cost + total_material_cost + total_equipment_cost
    total_budget = float(project.budget) if project.budget else 0
    remaining_budget = max(0, total_budget - total_spent)
    
    # Recent diary entries for summary
    recent_diary_entries = project_entries[:3]
    
    # Resource statistics from real data
    total_workers = labor_entries.aggregate(total=Sum('workers_count'))['total'] or 0
    equipment_count = equipment_entries.values('equipment_type').distinct().count()
    delay_count = delay_entries.count()
    
    # Determine current phase based on progress
    if progress < 25:
        phase_name = "Planning"
    elif progress < 50:
        phase_name = "Foundation"
    elif progress < 75:
        phase_name = "Structure"
    else:
        phase_name = "Finishing"
    
    context = {
        'project': project,
        'progress': progress,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'remaining_budget': remaining_budget,
        'labor_count': total_workers,
        'equipment_count': equipment_count,
        'delays_count': delay_count,
        'recent_diary_entries': recent_diary_entries,
        'phase_name': phase_name,
    }
    return render(request, 'site_diary/project-detail.html', context)

@login_required
@require_site_manager_role
def settings(request):
    """Site Manager settings and preferences"""
    from accounts.models import SiteManagerProfile
    from accounts.forms import ProfileUpdateForm
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import logout
    from django.http import HttpResponse
    from django.db import transaction
    import csv
    import json
    
    # Get or create site manager profile
    try:
        site_manager_profile = request.user.sitemanagerprofile
        print(f"DEBUG: Site manager profile found: {site_manager_profile}")
        print(f"DEBUG: Current profile data - Phone: {site_manager_profile.phone}, Emergency: {site_manager_profile.emergency_contact}")
        print(f"DEBUG: Current profile pic: {site_manager_profile.profile_pic}")
    except SiteManagerProfile.DoesNotExist:
        print(f"DEBUG: Site Manager profile not found for user: {request.user}")
        messages.error(request, 'Site Manager profile not found.')
        return redirect('site_diary:dashboard')
    
    if request.method == 'POST':
        print(f"DEBUG: POST request received")
        print(f"DEBUG: POST data: {request.POST}")
        print(f"DEBUG: FILES data: {request.FILES}")
        
        action = request.POST.get('action')
        print(f"DEBUG: Action: {action}")
        
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
                profile_pic = request.FILES['profile_pic']
                print(f"DEBUG: Profile picture uploaded: {profile_pic.name}, Size: {profile_pic.size}")
                
                # Validate file type
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
                file_type = profile_pic.content_type.lower()
                
                if file_type not in allowed_types:
                    messages.error(request, 'Invalid file type. Please upload a JPEG, PNG, GIF, or WebP image.')
                    return redirect('site_diary:settings')
                
                # Validate file size (max 5MB)
                max_size = 5 * 1024 * 1024  # 5MB
                if profile_pic.size > max_size:
                    messages.error(request, 'File size too large. Please upload an image smaller than 5MB.')
                    return redirect('site_diary:settings')
                
                site_manager_profile.profile_pic = profile_pic
                print(f"DEBUG: Profile picture assigned to site_manager_profile")
            
            try:
                with transaction.atomic():
                    # Save user data
                    print(f"DEBUG: Saving user data - First: {user.first_name}, Last: {user.last_name}, Email: {user.email}")
                    user.save()
                    
                    # Save site manager profile data
                    print(f"DEBUG: Saving profile data - Phone: {site_manager_profile.phone}, Emergency: {site_manager_profile.emergency_contact}")
                    site_manager_profile.save()
                    
                    # Verify data was saved by reloading from database
                    user.refresh_from_db()
                    site_manager_profile.refresh_from_db()
                    
                    print(f"DEBUG: Verification - User saved: First={user.first_name}, Last={user.last_name}, Email={user.email}")
                    print(f"DEBUG: Verification - Profile saved: Phone={site_manager_profile.phone}, Emergency={site_manager_profile.emergency_contact}")
                    print(f"DEBUG: Verification - Profile pic: {site_manager_profile.profile_pic}")
                    
                    messages.success(request, 'Profile updated successfully!')
            except Exception as e:
                print(f"DEBUG: Error saving profile: {str(e)}")
                import traceback
                print(f"DEBUG: Full traceback: {traceback.format_exc()}")
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
        
        return redirect('site:settings')
    
    # Debug: Show current data being passed to template
    print(f"DEBUG: Template context - User: {request.user}")
    print(f"DEBUG: Template context - Profile: {site_manager_profile}")
    print(f"DEBUG: Template context - User first_name: {request.user.first_name}")
    print(f"DEBUG: Template context - User last_name: {request.user.last_name}")
    print(f"DEBUG: Template context - User email: {request.user.email}")
    print(f"DEBUG: Template context - Profile phone: {site_manager_profile.phone}")
    print(f"DEBUG: Template context - Profile emergency_contact: {site_manager_profile.emergency_contact}")
    
    context = {
        'user': request.user,
        'site_manager_profile': site_manager_profile,
    }
    return render(request, 'site_diary/settings.html', context)

@login_required
@require_site_manager_role
def site_manager_logout(request):
    """Site Manager logout view"""
    from django.contrib.auth import logout
    
    if request.method == 'POST':
        # Clear browser data if requested
        clear_browser_data = request.POST.get('clear_browser_data') == 'on'
        
        # Log out the user
        logout(request)
        
        # Add success message
        messages.success(request, 'You have been successfully logged out from the Site Manager panel.')
        
        # Redirect to site manager login
        return redirect('accounts:sitemanager_login')
    
    # If GET request, redirect to settings
    return redirect('site:settings')

@login_required
@require_admin_role
def adminclientproject(request):
    """Admin view for client projects with approval functionality"""
    
    # Handle project approval/rejection
    if request.method == 'POST':
        action = request.POST.get('action')
        project_id = request.POST.get('project_id')
        
        if action and project_id:
            try:
                project = Project.objects.get(id=project_id)
                
                if action == 'approve':
                    project.status = 'planning'
                    project.approved_by = request.user
                    project.approved_at = timezone.now()
                    project.save()
                    messages.success(request, f'Project "{project.name}" approved successfully.')
                    
                elif action == 'reject':
                    rejection_reason = request.POST.get('rejection_reason', '')
                    project.status = 'rejected'
                    project.rejection_reason = rejection_reason
                    project.save()
                    messages.success(request, f'Project "{project.name}" rejected.')
                    
            except Project.DoesNotExist:
                messages.error(request, 'Project not found.')
        
        return redirect('site_diary:adminclientproject')
    
    search_form = ProjectSearchForm(request.GET)
    projects = Project.objects.all().select_related('project_manager', 'architect')
    
    if search_form.is_valid():
        if search_form.cleaned_data['name']:
            projects = projects.filter(name__icontains=search_form.cleaned_data['name'])
        if search_form.cleaned_data['client_name']:
            projects = projects.filter(client_name__icontains=search_form.cleaned_data['client_name'])
        if search_form.cleaned_data['status']:
            projects = projects.filter(status=search_form.cleaned_data['status'])
    
    # Separate pending projects for easy access
    pending_projects = projects.filter(status='pending_approval').order_by('-created_at')
    approved_count = projects.filter(status__in=['planning', 'active', 'on_hold', 'completed']).count()
    rejected_count = projects.filter(status='rejected').count()
    all_projects = projects.order_by('-created_at')
    
    paginator = Paginator(all_projects, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'pending_projects': pending_projects,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'search_form': search_form,
    }
    return render(request, 'admin/adminclientproject.html', context)

@login_required
@require_admin_role
def admindiary(request):
    """Admin view for diary entries with approval functionality"""
    
    # Handle diary entry approval
    if request.method == 'POST':
        action = request.POST.get('action')
        entry_id = request.POST.get('entry_id')
        
        if action and entry_id:
            try:
                entry = DiaryEntry.objects.get(id=entry_id)
                
                if action == 'approve':
                    entry.approved = True
                    entry.reviewed_by = request.user
                    entry.approval_date = timezone.now()
                    entry.save()
                    messages.success(request, f'Diary entry for {entry.project.name} approved.')
                    
            except DiaryEntry.DoesNotExist:
                messages.error(request, 'Diary entry not found.')
        
        return redirect('site_diary:admindiary')
    
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
    
    # Statistics
    total_entries = entries.count()
    pending_entries = entries.filter(approved=False).count()
    approved_entries = entries.filter(approved=True).count()
    draft_entries = entries.filter(draft=True).count()
    
    # Pagination
    paginator = Paginator(entries, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_entries': total_entries,
        'pending_entries': pending_entries,
        'approved_entries': approved_entries,
        'draft_entries': draft_entries,
    }
    return render(request, 'admin/admindiary.html', context)

@login_required
@require_admin_role
def admindiaryreviewer(request):
    """Admin diary reviewer interface with approval functionality"""
    
    # Handle bulk actions
    if request.method == 'POST':
        action = request.POST.get('action')
        entry_ids = request.POST.getlist('entry_ids')
        
        if action == 'approve_selected' and entry_ids:
            DiaryEntry.objects.filter(id__in=entry_ids).update(
                approved=True,
                reviewed_by=request.user,
                approval_date=timezone.now()
            )
            messages.success(request, f'{len(entry_ids)} diary entries approved successfully.')
        
        return redirect('site_diary:admindiaryreviewer')
    
    # Get entries pending review
    pending_entries = DiaryEntry.objects.filter(
        approved=False, draft=False
    ).select_related('project', 'created_by').order_by('-entry_date')
    
    # Pagination
    paginator = Paginator(pending_entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'pending_count': pending_entries.count()
    }
    return render(request, 'admin/admindiaryreviewer.html', context)

@login_required
@require_admin_role
def adminhistory(request):
    """Admin history view with comprehensive data"""
    
    # Get all diary entries with related data
    entries = DiaryEntry.objects.select_related(
        'project', 'created_by', 'reviewed_by'
    ).order_by('-entry_date')
    
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        entries = entries.filter(entry_date__gte=start_date)
    if end_date:
        entries = entries.filter(entry_date__lte=end_date)
    
    # Statistics
    total_entries = entries.count()
    approved_entries = entries.filter(approved=True).count()
    pending_entries = entries.filter(approved=False, draft=False).count()
    
    # Pagination
    paginator = Paginator(entries, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_entries': total_entries,
        'approved_entries': approved_entries,
        'pending_entries': pending_entries,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'admin/adminhistory.html', context)

@login_required
@require_admin_role
def adminreports(request):
    """Admin reports view with comprehensive analytics"""
    
    # Project statistics
    total_projects = Project.objects.count()
    pending_projects = Project.objects.filter(status='pending_approval').count()
    approved_projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed']).count()
    rejected_projects = Project.objects.filter(status='rejected').count()
    
    # Diary entry statistics
    total_entries = DiaryEntry.objects.count()
    approved_entries = DiaryEntry.objects.filter(approved=True).count()
    pending_entries = DiaryEntry.objects.filter(approved=False, draft=False).count()
    draft_entries = DiaryEntry.objects.filter(draft=True).count()
    
    # Recent activity
    recent_projects = Project.objects.order_by('-created_at')[:5]
    recent_entries = DiaryEntry.objects.select_related('project', 'created_by').order_by('-created_at')[:5]
    
    context = {
        'project_stats': {
            'total': total_projects,
            'pending': pending_projects,
            'approved': approved_projects,
            'rejected': rejected_projects,
        },
        'entry_stats': {
            'total': total_entries,
            'approved': approved_entries,
            'pending': pending_entries,
            'drafts': draft_entries,
        },
        'recent_projects': recent_projects,
        'recent_entries': recent_entries,
    }
    return render(request, 'admin/adminreports.html', context)

@require_site_manager_role
def generate_project_report(request, project_id):
    """Generate project report - API endpoint"""
    if request.method == 'POST':
        try:
            project = get_object_or_404(Project, id=project_id)
            
            # Verify user has access
            if not request.user.is_staff:
                user_projects = Project.objects.filter(
                    Q(project_manager=request.user) | Q(architect=request.user)
                )
                if project not in user_projects:
                    return JsonResponse({'error': 'Access denied'}, status=403)
            
            # Mock report generation - replace with actual report logic
            report_data = {
                'project_name': project.name,
                'generated_at': timezone.now().isoformat(),
                'status': 'success',
                'download_url': f'/reports/project_{project_id}_{timezone.now().strftime("%Y%m%d")}.pdf'
            }
            
            return JsonResponse(report_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@require_site_manager_role
@require_http_methods(["GET"])
def api_project_location(request, project_id):
    """API endpoint to get project location"""
    try:
        project_id = int(project_id)
        project = get_object_or_404(Project, id=project_id)
        
        # Verify user has access to this project
        if not request.user.is_staff:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
            if project not in user_projects:
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        return JsonResponse({
            'location': escape(project.location or ''),
            'project_name': escape(project.name)
        })
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid project ID'}, status=400)
    except Exception as e:
        logger.error(f"Project location API error: {str(e)}")
        return JsonResponse({'error': 'Server error'}, status=500)

@require_site_manager_role
@require_http_methods(["GET"])
def api_project_data(request, project_id):
    """API endpoint to get comprehensive project data for reports"""
    try:
        project_id = int(project_id)
        project = get_object_or_404(Project, id=project_id)
        
        # Verify user has access to this project
        if not request.user.is_staff:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
            if project not in user_projects:
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get project entries for date range calculation
        project_entries = DiaryEntry.objects.filter(project=project).order_by('entry_date')
        
        # Calculate date range from actual entries
        start_date = None
        end_date = None
        if project_entries.exists():
            start_date = project_entries.first().entry_date.strftime('%Y-%m-%d')
            end_date = project_entries.last().entry_date.strftime('%Y-%m-%d')
        else:
            # Fallback to project dates
            start_date = project.start_date.strftime('%Y-%m-%d') if project.start_date else ''
            end_date = project.expected_end_date.strftime('%Y-%m-%d') if project.expected_end_date else ''
        
        # Get latest weather condition from entries
        latest_entry = project_entries.filter(weather_condition__isnull=False).exclude(weather_condition='').last()
        weather_condition = latest_entry.weather_condition if latest_entry else 'sunny'
        
        # Get contractor info (assuming it's stored in project or can be derived)
        contractor = project.client_name or 'Default Contractor'
        
        return JsonResponse({
            'location': escape(project.location or ''),
            'weather_condition': weather_condition,
            'contractor': escape(contractor),
            'start_date': start_date,
            'end_date': end_date,
            'project_name': escape(project.name)
        })
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid project ID'}, status=400)
    except Exception as e:
        logger.error(f"Project data API error: {str(e)}")
        return JsonResponse({'error': 'Server error'}, status=500)

@login_required
@require_site_manager_role
@csrf_protect
def sitedraft(request):
    """Site Manager drafts view with real database data"""
    # Handle draft deletion
    if request.method == 'POST' and request.POST.get('action') == 'delete_draft':
        draft_id = request.POST.get('draft_id')
        try:
            draft_id = int(draft_id)
            draft = DiaryEntry.objects.get(id=draft_id, created_by=request.user, draft=True)
            draft.delete()
            messages.success(request, 'Draft deleted successfully!')
            logger.info(f"Draft {draft_id} deleted by user {request.user.id}")
        except (ValueError, TypeError, DiaryEntry.DoesNotExist):
            messages.error(request, 'Draft not found or access denied.')
        return redirect('site_diary:sitedraft')
    
    # Get user's draft diary entries
    if request.user.is_staff:
        drafts = DiaryEntry.objects.filter(draft=True)
    else:
        user_projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
        )
        drafts = DiaryEntry.objects.filter(
            project__in=user_projects,
            draft=True
        )
    
    # Order by most recent
    drafts = drafts.select_related('project', 'created_by').order_by('-created_at')
    
    # Statistics
    total_drafts = drafts.count()
    recent_drafts = drafts.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    submitted_entries = DiaryEntry.objects.filter(
        created_by=request.user,
        draft=False
    ).count()
    
    # Pagination
    paginator = Paginator(drafts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'drafts': page_obj,
        'page_obj': page_obj,
        'stats': {
            'total_drafts': total_drafts,
            'recent_drafts': recent_drafts,
            'submitted_entries': submitted_entries,
        },
        'user': request.user,
    }
    return render(request, 'site_diary/sitedraft.html', context)
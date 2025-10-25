from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseForbidden, JsonResponse
from accounts.models import Profile
from accounts.forms import ProfileUpdateForm
from accounts.decorators import allow_public_access, require_public_role
from portfolio.models import Project, Category
from site_diary.models import Project as SiteDiaryProject
from chatbot.models import ChatbotMessage

@allow_public_access
def home(request):
    # Get published projects with related data for homepage (exclude drafts)
    projects = Project.objects.select_related('category').prefetch_related('images').exclude(status='draft').order_by('-featured', '-completion_date')
    
    # Get categories for filters
    categories = Category.objects.all().order_by('name')
    
    # Get unique years for year filter (exclude drafts)
    years = Project.objects.exclude(status='draft').values_list('year', flat=True).distinct().order_by('-year')
    
    # Get recent projects (first 6 for carousel)
    recent_projects = projects[:6]
    
    context = {
        'projects': projects,
        'categories': categories,
        'years': years,
        'recent_projects': recent_projects,
    }
    
    return render(request, 'core/home.html', context)

@allow_public_access
def about(request):
    return render(request, 'core/aboutus.html')

@allow_public_access
def contact(request):
    if request.method == 'POST':
        # Extract form data
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Basic validation
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'core/contacts.html')
        
        # Create contact message using chatbot model
        try:
            contact_msg = ChatbotMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=f"{subject}: {message}"
            )
            messages.success(request, 'Message sent successfully! We will get back to you soon.')
            return redirect('core:contact')
        except Exception as e:
            messages.error(request, 'Failed to send message. Please try again.')
            return render(request, 'core/contacts.html')
    
    return render(request, 'core/contacts.html')

@allow_public_access
def project(request):
    return render(request, 'core/project.html')

@allow_public_access
def terms(request):
    return render(request, 'core/terms.html')

@require_public_role
@login_required
def clientdashboard(request):
    """
    Client Dashboard View - Shows project dashboard for users with assigned projects
    """
    current_user = request.user
    
    try:
        profile = Profile.objects.get(user=current_user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=current_user, role='client')
    
    # Ensure users with projects have client role
    if not profile.role or profile.role == 'guest':
        profile.role = 'client'
        profile.save()
    
    # Allow access to dashboard even without project for design viewing
    # if not profile.project_name:
    #     messages.info(request, 'No project assigned yet. Please contact us to get started.')
    #     return redirect('core:usersettings')
    
    # Get client's approved projects from site_diary
    client_projects = SiteDiaryProject.objects.filter(client=current_user, approved_by__isnull=False).order_by('-created_at')
    
    # If no projects found by client field, try to find by client_name
    if not client_projects.exists():
        user_full_name = current_user.get_full_name()
        if user_full_name:
            client_projects = SiteDiaryProject.objects.filter(client_name__icontains=user_full_name, approved_by__isnull=False).order_by('-created_at')
            print(f"[DEBUG] Found {client_projects.count()} projects by name matching: {user_full_name}")
        else:
            client_projects = SiteDiaryProject.objects.filter(client_name__icontains=current_user.username, approved_by__isnull=False).order_by('-created_at')
            print(f"[DEBUG] Found {client_projects.count()} projects by username matching: {current_user.username}")
    
    # Calculate project statistics
    total_projects = client_projects.count()
    active_projects = client_projects.filter(status='active').count()
    completed_projects = client_projects.filter(status='completed').count()
    planning_projects = client_projects.filter(status='planning').count()
    
    # Debug: Print profile data
    print(f"[DEBUG] Current user: {current_user.username} (ID: {current_user.id})")
    print(f"[DEBUG] User email: {current_user.email}")
    print(f"[DEBUG] User full name: {current_user.get_full_name()}")
    print(f"[DEBUG] Profile data: role={profile.role}, phone={profile.phone}")
    print(f"[DEBUG] Project: name={profile.project_name}, start={profile.project_start}")
    print(f"[DEBUG] Architect: {profile.assigned_architect}")
    print(f"[DEBUG] Client projects found: {total_projects}")
    
    # Debug: Print all projects to see what's available
    all_projects = SiteDiaryProject.objects.all()
    print(f"[DEBUG] Total projects in database: {all_projects.count()}")
    for proj in all_projects:
        print(f"[DEBUG] Project: {proj.name}, Client: {proj.client}, Client Name: {proj.client_name}")
    
    print(f"[DEBUG] Final client projects: {total_projects}")
    for proj in client_projects:
        print(f"[DEBUG] Final project: {proj.name}, Status: {proj.status}, Client: {proj.client}")
    
    context = {
        'user': current_user,
        'profile': profile,
        'user_full_name': current_user.get_full_name() or current_user.username,
        'user_email': current_user.email,
        'profile_role': profile.role.title() if profile.role else 'Client',
        'client_projects': client_projects,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
        'planning_projects': planning_projects,
    }
    
    return render(request, 'core/clientdashboard.html', context)

@require_public_role
@login_required
def client_project_detail(request, project_id):
    """
    Client Project Detail View - Shows detailed project information for clients
    """
    current_user = request.user
    
    # Get the approved project and ensure it belongs to the current user
    try:
        project = SiteDiaryProject.objects.get(id=project_id, client=current_user, approved_by__isnull=False)
    except SiteDiaryProject.DoesNotExist:
        # Try to find by client_name if client field is not set
        user_full_name = current_user.get_full_name()
        if user_full_name:
            try:
                project = SiteDiaryProject.objects.get(id=project_id, client_name__icontains=user_full_name, approved_by__isnull=False)
            except SiteDiaryProject.DoesNotExist:
                messages.error(request, 'Project not found or access denied.')
                return redirect('core:clientdashboard')
        else:
            messages.error(request, 'Project not found or access denied.')
            return redirect('core:clientdashboard')
    
    # Get diary entries for this project
    diary_entries = project.diary_entries.filter(draft=False).order_by('-entry_date')[:10]
    
    # Calculate budget used from all diary entries
    from decimal import Decimal
    budget_used = Decimal('0')
    all_entries = project.diary_entries.filter(draft=False)
    
    for entry in all_entries:
        # Sum material costs
        for material in entry.material_entries.all():
            budget_used += material.total_cost
        # Sum labor costs
        for labor in entry.labor_entries.all():
            budget_used += labor.total_cost
        # Sum equipment costs
        for equipment in entry.equipment_entries.all():
            budget_used += equipment.total_rental_cost
        # Sum subcontractor costs
        for subcontractor in entry.subcontractor_entries.all():
            budget_used += subcontractor.daily_cost
        # Sum delay cost impacts
        for delay in entry.delay_entries.all():
            if delay.cost_impact:
                budget_used += delay.cost_impact
    
    budget_remaining = project.budget - budget_used if project.budget else Decimal('0')
    budget_percentage = (budget_used / project.budget * 100) if project.budget and project.budget > 0 else 0
    
    # Get latest weather data from most recent diary entry
    latest_entry = project.diary_entries.filter(draft=False, weather_condition__isnull=False).order_by('-entry_date').first()
    
    # Get all milestones with their completion status
    from site_diary.models import Milestone
    milestones = Milestone.objects.filter(is_active=True).order_by('order')
    
    # Get milestone progress from diary entries
    milestone_progress = {}
    current_milestone = None
    current_milestone_progress = 0
    completed_phases = 0
    total_phases = milestones.count()
    
    for milestone in milestones:
        latest_entry_for_milestone = project.diary_entries.filter(draft=False, milestone=milestone).order_by('-entry_date').first()
        if latest_entry_for_milestone:
            milestone_progress[milestone.id] = latest_entry_for_milestone.progress_percentage
            if latest_entry_for_milestone.progress_percentage == 100:
                completed_phases += 1
            elif latest_entry_for_milestone.progress_percentage < 100 and not current_milestone:
                current_milestone = milestone
                current_milestone_progress = latest_entry_for_milestone.progress_percentage
    
    context = {
        'project': project,
        'user': current_user,
        'diary_entries': diary_entries,
        'budget_used': budget_used,
        'budget_remaining': budget_remaining,
        'budget_percentage': budget_percentage,
        'latest_weather': latest_entry,
        'milestones': milestones,
        'milestone_progress': milestone_progress,
        'current_milestone': current_milestone,
        'current_milestone_progress': current_milestone_progress,
        'completed_phases': completed_phases,
        'total_phases': total_phases,
    }
    
    return render(request, 'core/client_project_detail.html', context)

@require_public_role
@login_required
@never_cache
@csrf_protect
@transaction.atomic
def usersettings(request):
    """
    User Settings View - Ensures each user only sees and edits their own data
    Security: Uses request.user for all queries, never accepts user ID from request
    """
    # Debug: Print current user info
    print(f"[DEBUG] USERSETTINGS - Current user: {request.user.username} (ID: {request.user.id})")
    
    # SECURITY: Always use request.user - never trust user input for user identification
    current_user = request.user
    
    # Get or create profile for the CURRENT USER ONLY
    try:
        profile = Profile.objects.select_for_update().get(user=current_user)
        print(f"[DEBUG] USERSETTINGS - Found existing profile for user: {current_user.username}")
    except Profile.DoesNotExist:
        # Create profile if it doesn't exist (signal should handle this, but fallback)
        profile = Profile.objects.create(user=current_user, role='client')
        print(f"[DEBUG] USERSETTINGS - Created new profile for user: {current_user.username}")
    
    # Ensure users accessing settings have client role if they don't have a role set
    if not profile.role or profile.role == 'guest':
        profile.role = 'client'
        profile.save()
        print(f"[DEBUG] USERSETTINGS - Updated role to client for user: {current_user.username}")
    
    # SECURITY CHECK: Verify profile belongs to current user
    if profile.user != current_user:
        print(f"[SECURITY ERROR] Profile user mismatch! Profile belongs to {profile.user}, current user is {current_user}")
        messages.error(request, 'Security error: Profile access denied.')
        return redirect('core:home')
    
    print(f"[DEBUG] USERSETTINGS - Profile verified for user: {profile.user.username} (Profile ID: {profile.id})")
    print(f"[DEBUG] USERSETTINGS - Profile data: phone={profile.phone}, architect={profile.assigned_architect}, project={profile.project_name}")
    
    if request.method == 'POST':
        # SECURITY: Pass current_user explicitly to form
        form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=profile, 
            user=current_user
        )
        
        if form.is_valid():
            # SECURITY: Double-check user ownership before saving
            if profile.user != current_user:
                print(f"[SECURITY ERROR] Attempted to save profile for wrong user!")
                messages.error(request, 'Security error: Unauthorized profile update.')
                return redirect('core:usersettings')
            
            try:
                # Save with explicit user parameter
                with transaction.atomic():
                    updated_profile = form.save(user=current_user)
                    print(f"[DEBUG] USERSETTINGS - Profile updated for user: {updated_profile.user.username}")
                    print(f"[DEBUG] USERSETTINGS - Updated data: {current_user.first_name} {current_user.last_name}, {updated_profile.phone}, {updated_profile.assigned_architect}")
                    
                    # Success message with user's name
                    user_name = current_user.get_full_name() or current_user.username
                    messages.success(request, f'🎉 Profile updated successfully, {user_name}! Your changes have been saved.')
                    
                return redirect('core:usersettings')
                
            except Exception as e:
                print(f"[ERROR] USERSETTINGS - Failed to save profile: {str(e)}")
                messages.error(request, f'Failed to update profile: {str(e)}')
                
        else:
            messages.error(request, 'Please correct the errors below.')
            print(f"[DEBUG] USERSETTINGS - Form errors: {form.errors}")
            # Add specific field errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        # GET request - initialize form with current user's data
        initial_data = {
            'first_name': current_user.first_name or '',
            'last_name': current_user.last_name or '',
            'email': current_user.email or '',
            'phone': profile.phone or '',
            'assigned_architect': profile.assigned_architect or '',
            'project_name': profile.project_name or '',
            'project_start': profile.project_start or '',
        }
        
        print(f"[DEBUG] USERSETTINGS - Initial form data: {initial_data}")
        form = ProfileUpdateForm(instance=profile, user=current_user, initial=initial_data)
    
    # Get client's approved projects for display
    client_projects = SiteDiaryProject.objects.filter(client=current_user, approved_by__isnull=False).order_by('-created_at')
    if not client_projects.exists():
        user_full_name = current_user.get_full_name()
        if user_full_name:
            client_projects = SiteDiaryProject.objects.filter(client_name__icontains=user_full_name, approved_by__isnull=False).order_by('-created_at')
        else:
            client_projects = SiteDiaryProject.objects.filter(client_name__icontains=current_user.username, approved_by__isnull=False).order_by('-created_at')
    
    # SECURITY: Only pass current user's data to template
    context = {
        'profile': profile,
        'form': form,
        'user': current_user,  # Explicitly pass current user
        'user_full_name': current_user.get_full_name() or current_user.username,
        'user_email': current_user.email,
        'profile_role': profile.role.title() if profile.role else 'Client',
        'client_projects': client_projects,
        # Additional user-specific data
        'account_created': current_user.date_joined.strftime('%B %d, %Y') if current_user.date_joined else 'Unknown',
        'last_login': current_user.last_login.strftime('%B %d, %Y at %I:%M %p') if current_user.last_login else 'Never',
        'account_status': 'Active' if current_user.is_active else 'Inactive',
        'user_id': current_user.id,
    }
    
    print(f"[DEBUG] USERSETTINGS - Rendering template for user: {current_user.username}")
    
    # Add cache-busting timestamp
    import time
    context['cache_buster'] = int(time.time())
    
    response = render(request, 'core/usersettings.html', context)
    
    # Add headers to prevent caching
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response

def login(request):
    return render(request, 'core/login.html')

def permission_denied_view(request, exception=None):
    """
    Custom 401 Unauthorized error handler.
    Redirects users to client login when they try to access admin/site manager areas.
    """
    return render(request, 'page error/401.html', status=401)

def admin_permission_denied_view(request, exception=None):
    """
    Custom 401 Unauthorized error handler for admin areas.
    Shows admin-specific error page when site managers or unauthorized users try to access admin areas.
    """
    return render(request, 'page error/401_2.html', status=401)
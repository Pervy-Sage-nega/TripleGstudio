from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseForbidden
from accounts.models import Profile
from accounts.forms import ProfileUpdateForm
from accounts.decorators import allow_public_access, require_public_role
from portfolio.models import Project, Category

@allow_public_access
def home(request):
    # Get projects with related data for homepage
    projects = Project.objects.select_related('category').prefetch_related('images').order_by('-featured', '-completion_date')
    
    # Get categories for filters
    categories = Category.objects.all().order_by('name')
    
    # Get unique years for year filter
    years = Project.objects.values_list('year', flat=True).distinct().order_by('-year')
    
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
    return render(request, 'core/contacts.html')

@allow_public_access
def project(request):
    return render(request, 'core/project.html')

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
        profile = Profile.objects.create(user=current_user, role='customer')
    
    # Allow access to dashboard even without project for design viewing
    # if not profile.project_name:
    #     messages.info(request, 'No project assigned yet. Please contact us to get started.')
    #     return redirect('core:usersettings')
    
    # Debug: Print profile data
    print(f"[DEBUG] Profile data: role={profile.role}, phone={profile.phone}")
    print(f"[DEBUG] Project: name={profile.project_name}, start={profile.project_start}")
    print(f"[DEBUG] Architect: {profile.assigned_architect}")
    
    context = {
        'user': current_user,
        'profile': profile,
        'user_full_name': current_user.get_full_name() or current_user.username,
        'user_email': current_user.email,
        'profile_role': profile.role.title() if profile.role else 'Customer',
    }
    
    return render(request, 'core/clientdashboard.html', context)

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
        profile = Profile.objects.create(user=current_user, role='customer')
        print(f"[DEBUG] USERSETTINGS - Created new profile for user: {current_user.username}")
    
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
    
    # SECURITY: Only pass current user's data to template
    context = {
        'profile': profile,
        'form': form,
        'user': current_user,  # Explicitly pass current user
        'user_full_name': current_user.get_full_name() or current_user.username,
        'user_email': current_user.email,
        'profile_role': profile.role.title() if profile.role else 'Customer',
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
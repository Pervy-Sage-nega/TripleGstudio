from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils import timezone
from accounts.models import AdminProfile, SiteManagerProfile, Profile, SitePersonnelRole
from django.contrib.auth.models import User
from site_diary.models import Project
from blog.models import BlogPost
from django.db.models import Count
from django.contrib.sessions.models import Session
from .decorators import require_admin_role, ajax_require_admin_role
from accounts.activity_tracker import UserActivityTracker
import json
from datetime import timedelta

@require_admin_role
def admin_home(request):
    """Admin dashboard home page"""
    from site_diary.models import DiaryEntry
    
    admin_profile = AdminProfile.objects.get(user=request.user)
    
    # Get blog statistics
    all_posts = BlogPost.objects.filter(is_deleted=False)
    total_posts = all_posts.count()
    published_posts = all_posts.filter(status='published').count()
    draft_posts = all_posts.filter(status='draft').count()
    pending_posts = all_posts.filter(status='pending').count()
    
    # Get recent blog posts
    recent_posts = BlogPost.objects.filter(is_deleted=False).order_by('-created_date')[:3]
    
    # Get recent site diary entries
    recent_diary_entries = DiaryEntry.objects.filter(draft=False).select_related('project', 'created_by').order_by('-entry_date', '-created_at')[:5]
    
    # Get pending project approvals
    pending_projects = Project.objects.filter(status='pending_approval').select_related('client', 'project_manager').order_by('-created_at')[:3]
    
    # Get recent notifications
    recent_notifications = []
    
    # New user registrations
    new_users = User.objects.filter(date_joined__gte=timezone.now() - timedelta(hours=24)).order_by('-date_joined')[:2]
    for user in new_users:
        time_diff = timezone.now() - user.date_joined
        recent_notifications.append({
            'icon': 'fa-user-plus',
            'color': '#0a6cf1',
            'message': f'New user registered: {user.username}',
            'time': time_diff
        })
    
    # Pending diary approvals
    pending_diaries = DiaryEntry.objects.filter(needs_revision=True).select_related('project').order_by('-created_at')[:2]
    for diary in pending_diaries:
        time_diff = timezone.now() - diary.created_at
        recent_notifications.append({
            'icon': 'fa-file-alt',
            'color': '#7c3aed',
            'message': f'Diary pending approval ({diary.project.name})',
            'time': time_diff
        })
    
    # Pending site manager approvals
    pending_managers = SiteManagerProfile.objects.filter(approval_status='pending').select_related('user').order_by('-created_at')[:1]
    for manager in pending_managers:
        time_diff = timezone.now() - manager.created_at
        recent_notifications.append({
            'icon': 'fa-clipboard-check',
            'color': '#f59e0b',
            'message': f'Site manager approval needed: {manager.user.get_full_name()}',
            'time': time_diff
        })
    
    # Sort by time and limit to 5
    recent_notifications.sort(key=lambda x: x['time'])
    recent_notifications = recent_notifications[:5]
    
    # Get project statistics
    total_projects = Project.objects.count()
    ongoing_projects_qs = Project.objects.exclude(status__in=['completed', 'cancelled', 'rejected'])
    ongoing_projects = ongoing_projects_qs.count()
    
    # Calculate average progress for ongoing projects
    avg_progress = 0
    if ongoing_projects > 0:
        total_progress = sum([p.get_progress_percentage() for p in ongoing_projects_qs])
        avg_progress = int(total_progress / ongoing_projects)
    
    # Get dashboard statistics
    context = {
        'total_users': User.objects.count(),
        'total_admins': AdminProfile.objects.filter(approval_status='approved').count(),
        'pending_approvals': AdminProfile.objects.filter(approval_status='pending').count(),
        'total_clients': Profile.objects.count(),
        'pending_site_managers': SiteManagerProfile.objects.filter(approval_status='pending').count(),
        'admin_profile': admin_profile,
        'user': request.user,
        # Project statistics
        'total_projects': total_projects,
        'ongoing_projects': ongoing_projects,
        'avg_progress': avg_progress,
        # Blog statistics
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'pending_posts': pending_posts,
        'recent_posts': recent_posts,
        # Site diary entries
        'recent_diary_entries': recent_diary_entries,
        # Pending projects
        'pending_projects': pending_projects,
        # Notifications
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'adminhome.html', context)

@require_admin_role
def admin_settings(request):
    """Admin settings page"""
    admin_profile = AdminProfile.objects.get(user=request.user)
    
    context = {
        'admin_profile': admin_profile,
        'user': request.user,
    }
    
    return render(request, 'adminsettings.html', context)

@require_admin_role
def security_logs(request):
    """Security logs page showing Axes failed login attempts"""
    from axes.models import AccessAttempt, AccessLog
    from django.utils import timezone
    from django.db.models import Count
    from datetime import timedelta
    
    # Get all access attempts
    access_attempts = AccessAttempt.objects.all().order_by('-attempt_time')[:100]
    access_logs = AccessLog.objects.all().order_by('-attempt_time')[:100]
    
    # Calculate statistics
    total_attempts = AccessAttempt.objects.count()
    locked_count = AccessAttempt.objects.filter(failures_since_start__gte=5).count()
    unique_ips = AccessAttempt.objects.values('ip_address').distinct().count()
    
    # Today's attempts
    today = timezone.now().date()
    today_attempts = AccessAttempt.objects.filter(
        attempt_time__date=today
    ).count()
    
    # Analytics data - Last 7 days
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    attempts_by_day = []
    for day in last_7_days:
        count = AccessAttempt.objects.filter(attempt_time__date=day).count()
        attempts_by_day.append(count)
    
    # Top IPs by attempts
    top_ips = list(AccessAttempt.objects.values('ip_address')
                   .annotate(count=Count('id'))
                   .order_by('-count')[:5])
    
    # Attempts by status
    locked = AccessAttempt.objects.filter(failures_since_start__gte=5).count()
    failed = AccessAttempt.objects.filter(failures_since_start__lt=5).count()
    
    context = {
        'access_attempts': access_attempts,
        'access_logs': access_logs,
        'total_attempts': total_attempts,
        'locked_count': locked_count,
        'unique_ips': unique_ips,
        'today_attempts': today_attempts,
        'days_labels': [day.strftime('%b %d') for day in last_7_days],
        'attempts_by_day': attempts_by_day,
        'top_ips': top_ips,
        'locked_attempts': locked,
        'failed_attempts': failed,
    }
    
    return render(request, 'security_logs.html', context)

@ajax_require_admin_role
@csrf_protect
@require_http_methods(["POST"])
def unlock_user(request):
    """Unlock a user blocked by Axes"""
    from axes.utils import reset
    
    try:
        data = json.loads(request.body)
        username = data.get('username')
        ip_address = data.get('ip_address')
        
        # Reset the lockout for this username and IP
        reset(username=username, ip_address=ip_address)
        
        return JsonResponse({'success': True, 'message': 'User unlocked successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@ajax_require_admin_role
@csrf_protect
@require_http_methods(["POST"])
def update_admin_settings(request):
    """Handle admin settings updates via AJAX"""
    admin_profile = AdminProfile.objects.get(user=request.user)
    
    data = json.loads(request.body)
    section = data.get('section')
    
    if section == 'account':
        # Update user account information
        user = request.user
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.save()
        
        return JsonResponse({'success': True, 'message': 'Account updated successfully.'})
    
    elif section == 'security':
        # Update password
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not request.user.check_password(current_password):
            return JsonResponse({'success': False, 'message': 'Current password is incorrect.'})
        
        request.user.set_password(new_password)
        request.user.save()
        
        return JsonResponse({'success': True, 'message': 'Password updated successfully.'})
    
    elif section == 'system':
        # Handle system settings (you can extend this based on your needs)
        return JsonResponse({'success': True, 'message': 'System settings updated successfully.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid section.'})

@never_cache
def admin_logout(request):
    """
    Enhanced admin logout view with proper session handling
    """
    # Check if user was actually logged in as admin
    was_admin = False
    if request.user.is_authenticated:
        try:
            admin_profile = AdminProfile.objects.get(user=request.user)
            was_admin = True
            # Mark user as offline
            UserActivityTracker.mark_user_offline(request.user)
        except AdminProfile.DoesNotExist:
            pass
    
    # Clear all session data
    if hasattr(request, 'session'):
        request.session.flush()
    
    # Logout the user
    logout(request)
    
    # Add appropriate message
    if was_admin:
        messages.success(request, 'You have been logged out successfully from the admin panel.')
    else:
        messages.info(request, 'You have been logged out.')
    
    # Redirect to admin login page
    return redirect('accounts:admin_login')

@require_admin_role
def check_session(request):
    """AJAX endpoint to check if admin session is still valid"""
    return JsonResponse({
        'success': True,
        'authenticated': True,
        'user': request.user.username,
        'role': request.user.adminprofile.get_admin_role_display(),
        'timestamp': timezone.now().isoformat()
    })

def is_user_online(user):
    """Check if user is online using the activity tracker"""
    return UserActivityTracker.is_user_online(user)

@require_admin_role
def admin_user_list(request):
    """Admin user management list view"""
    # Get all clients
    clients = User.objects.filter(profile__isnull=False).select_related('profile')
    
    # Get all site managers
    site_managers = User.objects.filter(sitemanagerprofile__isnull=False).select_related('sitemanagerprofile')
    
    users = []
    
    # Add clients to users list
    for user in clients:
        users.append({
            'user_id': user.id,
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'role': 'client',
            'role_display': 'Client',
            'status': 'active' if user.is_active else 'suspended',
            'status_display': 'Active' if user.is_active else 'Suspended',
            'date_joined': user.date_joined,
            'profile_pic': user.profile.get_profile_image_url() if hasattr(user, 'profile') else None,
            'is_online': is_user_online(user)
        })
    
    # Add site managers to users list
    for user in site_managers:
        profile = user.sitemanagerprofile
        is_locked = profile.is_account_locked()
        status = 'locked' if is_locked else profile.approval_status
        status_display = 'Locked' if is_locked else profile.get_approval_status_display()
        
        users.append({
            'user_id': user.id,
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'role': 'sitemanager',
            'role_display': 'Site Manager',
            'status': status,
            'status_display': status_display,
            'date_joined': user.date_joined,
            'profile_pic': profile.get_profile_image_url(),
            'is_online': is_user_online(user)
        })
    
    # Sort by date joined (newest first)
    users.sort(key=lambda x: x['date_joined'], reverse=True)
    
    context = {
        'users': users,
        'total_clients': clients.count(),
        'active_site_managers': SiteManagerProfile.objects.filter(approval_status='approved').count(),
        'pending_site_managers': SiteManagerProfile.objects.filter(approval_status='pending').count(),
    }
    
    return render(request, 'adminusers.html', context)

@require_admin_role
def admin_user_detail(request, user_id):
    """Admin user detail view"""
    user = get_object_or_404(User, id=user_id)
    
    # Determine user type and get profile data
    if hasattr(user, 'sitemanagerprofile'):
        # Refresh from database to get latest data
        profile_data = SiteManagerProfile.objects.select_related('site_role').get(user=user)
        user_role = 'Site Manager'
        status = profile_data.approval_status
        status_display = profile_data.get_approval_status_display()
        profile_pic = profile_data.get_profile_image_url()
        site_role = profile_data.site_role
        available_roles = SitePersonnelRole.objects.filter(is_active=True).order_by('order')
    elif hasattr(user, 'profile'):
        profile_data = user.profile
        user_role = 'Client'
        status = 'active' if user.is_active else 'inactive'
        status_display = 'Active' if user.is_active else 'Inactive'
        profile_pic = profile_data.get_profile_image_url()
        site_role = None
        available_roles = []
    else:
        profile_data = None
        user_role = 'Unknown'
        status = 'unknown'
        status_display = 'Unknown'
        profile_pic = '/static/images/default-profile.png'
        site_role = None
        available_roles = []
    
    context = {
        'user': user,
        'user_role': user_role,
        'status': status,
        'status_display': status_display,
        'profile_data': profile_data,
        'profile_pic': profile_pic,
        'site_role': site_role,
        'available_roles': available_roles,
    }
    
    return render(request, 'adminuserdetail.html', context)

@ajax_require_admin_role
@csrf_protect
@require_http_methods(["POST"])
def update_user_status(request, user_id):
    """Update user status (approve, deny, suspend, reactivate)"""
    user = get_object_or_404(User, id=user_id)
    
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if hasattr(user, 'sitemanagerprofile'):
            profile = user.sitemanagerprofile
            
            if action == 'approve':
                profile.approval_status = 'approved'
                profile.approved_by = request.user
                profile.approved_at = timezone.now()
                profile.save()
                message = f'Site Manager {user.get_full_name()} has been approved.'
                
            elif action == 'deny':
                profile.approval_status = 'denied'
                profile.save()
                message = f'Site Manager {user.get_full_name()} application has been denied.'
                
            elif action == 'suspend':
                profile.approval_status = 'suspended'
                profile.save()
                message = f'Site Manager {user.get_full_name()} has been suspended.'
                
            elif action == 'reactivate':
                profile.approval_status = 'approved'
                profile.save()
                message = f'Site Manager {user.get_full_name()} has been reactivated.'
                
            elif action == 'unlock':
                profile.account_locked_until = None
                profile.failed_login_attempts = 0
                profile.save()
                message = f'Site Manager {user.get_full_name()} account has been unlocked.'
                
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action'})
                
        elif hasattr(user, 'profile'):
            if action == 'suspend':
                user.is_active = False
                user.save()
                message = f'Client {user.get_full_name()} has been suspended.'
                
            elif action == 'reactivate':
                user.is_active = True
                user.save()
                message = f'Client {user.get_full_name()} has been reactivated.'
                
            else:
                return JsonResponse({'success': False, 'message': 'Invalid action for client'})
        else:
            return JsonResponse({'success': False, 'message': 'User profile not found'})
        
        return JsonResponse({'success': True, 'message': message})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@ajax_require_admin_role
@csrf_protect
@require_http_methods(["POST"])
def generate_employee_id(request):
    """Generate unique employee ID"""
    try:
        data = json.loads(request.body)
        user_type = data.get('user_type')
        
        if user_type == 'admin':
            emp_id = AdminProfile.generate_employee_id('TG')
        elif user_type == 'sitemanager':
            emp_id = SiteManagerProfile.generate_employee_id()
        else:
            return JsonResponse({'success': False, 'message': 'Invalid user type'})
        
        return JsonResponse({'success': True, 'employee_id': emp_id})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@ajax_require_admin_role
@require_http_methods(["GET"])
def get_users_online_status(request):
    """Get real-time online status for all users"""
    try:
        clients = User.objects.filter(profile__isnull=False).values_list('id', flat=True)
        site_managers = User.objects.filter(sitemanagerprofile__isnull=False).values_list('id', flat=True)
        
        online_status = {}
        
        for user_id in list(clients) + list(site_managers):
            try:
                user = User.objects.get(id=user_id)
                online_status[str(user_id)] = UserActivityTracker.is_user_online(user)
            except User.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'online_status': online_status,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@ajax_require_admin_role
@csrf_protect
@require_http_methods(["POST"])
def assign_site_role(request):
    """Assign site role to site manager"""
    try:
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')
        
        user = get_object_or_404(User, id=user_id)
        
        if not hasattr(user, 'sitemanagerprofile'):
            return JsonResponse({'success': False, 'message': 'User is not a site manager'})
        
        profile = user.sitemanagerprofile
        
        if role_id:
            role = get_object_or_404(SitePersonnelRole, id=role_id, is_active=True)
            profile.site_role = role
            profile.employee_id = SiteManagerProfile.generate_employee_id(role)
        else:
            profile.site_role = None
            if not profile.employee_id or not profile.employee_id.startswith('SM-'):
                profile.employee_id = SiteManagerProfile.generate_employee_id()
        
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Role assigned successfully',
            'role_name': profile.site_role.display_name if profile.site_role else 'Site Manager',
            'employee_id': profile.employee_id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_admin_role
def subcontractor_list(request):
    """List all subcontractor companies"""
    from site_diary.models import SubcontractorCompany
    companies = SubcontractorCompany.objects.all().order_by('name')
    return render(request, 'admin/subcontractors.html', {'companies': companies})

@ajax_require_admin_role
@csrf_protect
@require_http_methods(["POST"])
def subcontractor_add(request):
    """Add new subcontractor company"""
    from site_diary.models import SubcontractorCompany
    try:
        SubcontractorCompany.objects.create(
            name=request.POST.get('name'),
            company_type=request.POST.get('company_type'),
            contact_person=request.POST.get('contact_person', ''),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            license_number=request.POST.get('license_number', ''),
            is_active=request.POST.get('is_active') == 'true'
        )
        return JsonResponse({'success': True, 'message': 'Company added successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@ajax_require_admin_role
@require_http_methods(["GET"])
def subcontractor_detail(request, company_id):
    """Get subcontractor company details"""
    from site_diary.models import SubcontractorCompany
    company = get_object_or_404(SubcontractorCompany, id=company_id)
    return JsonResponse({
        'id': company.id,
        'name': company.name,
        'company_type': company.company_type,
        'contact_person': company.contact_person,
        'phone': company.phone,
        'email': company.email,
        'address': company.address,
        'license_number': company.license_number,
        'is_active': company.is_active
    })

@ajax_require_admin_role
@csrf_protect
@require_http_methods(["POST"])
def subcontractor_update(request, company_id):
    """Update subcontractor company"""
    from site_diary.models import SubcontractorCompany
    try:
        company = get_object_or_404(SubcontractorCompany, id=company_id)
        company.name = request.POST.get('name')
        company.company_type = request.POST.get('company_type')
        company.contact_person = request.POST.get('contact_person', '')
        company.phone = request.POST.get('phone', '')
        company.email = request.POST.get('email', '')
        company.address = request.POST.get('address', '')
        company.license_number = request.POST.get('license_number', '')
        company.is_active = request.POST.get('is_active') == 'true'
        company.save()
        return JsonResponse({'success': True, 'message': 'Company updated successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@ajax_require_admin_role
@csrf_protect
@require_http_methods(["POST"])
def subcontractor_delete(request, company_id):
    """Delete subcontractor company"""
    from site_diary.models import SubcontractorCompany
    try:
        company = get_object_or_404(SubcontractorCompany, id=company_id)
        company.delete()
        return JsonResponse({'success': True, 'message': 'Company deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils import timezone
from accounts.models import AdminProfile, SiteManagerProfile, Profile
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.sessions.models import Session
from .decorators import require_admin_role, ajax_require_admin_role
from accounts.activity_tracker import UserActivityTracker
import json
from datetime import timedelta

@require_admin_role
def admin_home(request):
    """Admin dashboard home page"""
    admin_profile = AdminProfile.objects.get(user=request.user)
    
    # Get dashboard statistics
    context = {
        'total_users': User.objects.count(),
        'total_admins': AdminProfile.objects.filter(approval_status='approved').count(),
        'pending_approvals': AdminProfile.objects.filter(approval_status='pending').count(),
        'total_clients': Profile.objects.count(),
        'pending_site_managers': SiteManagerProfile.objects.filter(approval_status='pending').count(),
        'admin_profile': admin_profile,
        'user': request.user,
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
            'status': 'active' if user.is_active else 'inactive',
            'status_display': 'Active' if user.is_active else 'Inactive',
            'date_joined': user.date_joined,
            'profile_pic': user.profile.get_profile_image_url() if hasattr(user, 'profile') else None,
            'is_online': is_user_online(user)
        })
    
    # Add site managers to users list
    for user in site_managers:
        users.append({
            'user_id': user.id,
            'full_name': user.get_full_name() or user.username,
            'email': user.email,
            'role': 'sitemanager',
            'role_display': 'Site Manager',
            'status': user.sitemanagerprofile.approval_status,
            'status_display': user.sitemanagerprofile.get_approval_status_display(),
            'date_joined': user.date_joined,
            'profile_pic': user.sitemanagerprofile.get_profile_image_url(),
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
        profile_data = user.sitemanagerprofile
        user_role = 'Site Manager'
        status = profile_data.approval_status
        status_display = profile_data.get_approval_status_display()
        profile_pic = profile_data.get_profile_image_url()
    elif hasattr(user, 'profile'):
        profile_data = user.profile
        user_role = 'Client'
        status = 'active' if user.is_active else 'inactive'
        status_display = 'Active' if user.is_active else 'Inactive'
        profile_pic = profile_data.get_profile_image_url()
    else:
        profile_data = None
        user_role = 'Unknown'
        status = 'unknown'
        status_display = 'Unknown'
        profile_pic = '/static/images/default-profile.png'
    
    context = {
        'user': user,
        'user_role': user_role,
        'status': status,
        'status_display': status_display,
        'profile_data': profile_data,
        'profile_pic': profile_pic,
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
            emp_id = SiteManagerProfile.generate_employee_id('SM')
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

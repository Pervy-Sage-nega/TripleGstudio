from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils import timezone
from accounts.models import AdminProfile
from django.contrib.auth.models import User
from django.db.models import Count
from .decorators import require_admin_role, ajax_require_admin_role
import json

@require_admin_role
def admin_home(request):
    """Admin dashboard home page"""
    admin_profile = AdminProfile.objects.get(user=request.user)
    
    # Get dashboard statistics
    context = {
        'total_users': User.objects.count(),
        'total_admins': AdminProfile.objects.filter(approval_status='approved').count(),
        'pending_approvals': AdminProfile.objects.filter(approval_status='pending').count(),
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
    """
    AJAX endpoint to check if admin session is still valid
    Used by JavaScript to monitor session status
    """
    return JsonResponse({
        'success': True,
        'authenticated': True,
        'user': request.user.username,
        'role': request.user.adminprofile.get_admin_role_display(),
        'timestamp': timezone.now().isoformat()
    })

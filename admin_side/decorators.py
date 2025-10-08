from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from accounts.models import AdminProfile


def require_admin_role(view_func):
    """
    Decorator that requires user to be logged in and have an approved admin profile.
    Redirects to admin login if not authenticated or not authorized.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return redirect('accounts:admin_login')
        
        # Check if user has admin profile
        try:
            admin_profile = AdminProfile.objects.get(user=request.user)
            
            # Check if admin account is approved
            if admin_profile.approval_status != 'approved':
                raise PermissionDenied('Your admin account is not approved or is suspended.')
                
            # Check if account is locked
            if admin_profile.is_account_locked():
                raise PermissionDenied('Your admin account is temporarily locked. Please try again later.')
                
        except AdminProfile.DoesNotExist:
            raise PermissionDenied('Access denied. Admin privileges required.')
        
        # If all checks pass, call the original view
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_superuser(view_func):
    """
    Decorator that requires user to be a superuser admin.
    """
    @require_admin_role
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        admin_profile = AdminProfile.objects.get(user=request.user)
        
        # Check if user is superuser or has admin role
        if not (request.user.is_superuser or admin_profile.admin_role == 'admin'):
            raise PermissionDenied('Superuser privileges required for this action.')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def ajax_require_admin_role(view_func):
    """
    Decorator for AJAX views that requires admin role.
    Returns JSON response instead of redirect.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from django.http import JsonResponse
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False, 
                'message': 'Authentication required.',
                'redirect': '/accounts/admin-auth/login/'
            }, status=401)
        
        # Check if user has admin profile
        try:
            admin_profile = AdminProfile.objects.get(user=request.user)
            
            # Check if admin account is approved
            if admin_profile.approval_status != 'approved':
                return JsonResponse({
                    'success': False, 
                    'message': 'Admin account not approved.',
                    'redirect': '/accounts/admin-auth/login/'
                }, status=403)
                
            # Check if account is locked
            if admin_profile.is_account_locked():
                return JsonResponse({
                    'success': False, 
                    'message': 'Admin account is locked.',
                    'redirect': '/accounts/admin-auth/login/'
                }, status=403)
                
        except AdminProfile.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'Admin privileges required.',
                'redirect': '/accounts/admin-auth/login/'
            }, status=403)
        
        # If all checks pass, call the original view
        return view_func(request, *args, **kwargs)
    
    return wrapper

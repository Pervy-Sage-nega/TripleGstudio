from functools import wraps
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
import re

def handle_unauthorized_access(view_func):
    """
    Decorator to handle unauthorized access attempts with custom 401 pages.
    Prevents modal conflicts by clearing messages and showing appropriate error page.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except PermissionDenied:
            # Clear any existing messages to prevent modal conflicts
            if hasattr(request, '_messages'):
                request._messages.used = True
            
            # Determine which error page to show based on URL
            path = request.path
            context = _get_error_context(request)
            
            # Admin-only areas
            admin_patterns = [r'^/admin-panel/', r'^/adminside/']
            for pattern in admin_patterns:
                if re.match(pattern, path):
                    return render(request, 'page error/401_2.html', context, status=401)
            
            # Site manager areas
            site_manager_patterns = [r'^/diary/']
            for pattern in site_manager_patterns:
                if re.match(pattern, path):
                    return render(request, 'page error/401.html', context, status=401)
            
            # Default to client-focused error page
            return render(request, 'page error/401.html', context, status=401)
    
    return wrapper

def _get_error_context(request):
    """
    Get context data for error templates based on user type and request.
    """
    context = {
        'user_type': 'anonymous',
        'is_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
    }
    
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            from accounts.models import Profile, AdminProfile
            
            # Check if user has admin profile
            if AdminProfile.objects.filter(user=request.user).exists():
                context['user_type'] = 'admin'
            # Check if user has client profile
            elif Profile.objects.filter(user=request.user).exists():
                context['user_type'] = 'client'
            else:
                context['user_type'] = 'site_manager'
                
        except Exception:
            context['user_type'] = 'unknown'
    
    return context

def require_admin_access(view_func):
    """
    Decorator that requires admin access and shows 401_2.html for unauthorized users.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            from accounts.models import AdminProfile
            
            # Check if user has admin profile
            if not AdminProfile.objects.filter(user=request.user, approval_status='approved').exists():
                # Clear messages to prevent modal conflicts
                if hasattr(request, '_messages'):
                    request._messages.used = True
                
                context = _get_error_context(request)
                return render(request, 'page error/401_2.html', context, status=401)
            
            return view_func(request, *args, **kwargs)
            
        except Exception:
            # Clear messages to prevent modal conflicts
            if hasattr(request, '_messages'):
                request._messages.used = True
            
            context = _get_error_context(request)
            return render(request, 'page error/401_2.html', context, status=401)
    
    return wrapper

def require_site_manager_access(view_func):
    """
    Decorator that requires site manager or admin access and shows 401.html for unauthorized users.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            from accounts.models import AdminProfile, Profile
            
            # Check if user has admin or site manager access
            has_admin = AdminProfile.objects.filter(user=request.user, approval_status='approved').exists()
            has_profile = Profile.objects.filter(user=request.user).exists()
            
            if not (has_admin or has_profile):
                # Clear messages to prevent modal conflicts
                if hasattr(request, '_messages'):
                    request._messages.used = True
                
                context = _get_error_context(request)
                return render(request, 'page error/401.html', context, status=401)
            
            return view_func(request, *args, **kwargs)
            
        except Exception:
            # Clear messages to prevent modal conflicts
            if hasattr(request, '_messages'):
                request._messages.used = True
            
            context = _get_error_context(request)
            return render(request, 'page error/401.html', context, status=401)
    
    return wrapper

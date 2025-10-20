"""
Access control decorators for Triple G BuildHub
Provides role-based view protection decorators.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .utils import get_user_role, log_access_violation, get_appropriate_redirect

def require_role(allowed_roles):
    """
    Decorator to require specific user roles for view access.
    
    Args:
        allowed_roles (list): List of allowed roles ('admin', 'site_manager', 'public', 'superadmin')
    
    Usage:
        @require_role(['admin', 'superadmin'])
        def admin_view(request):
            return render(request, 'admin/dashboard.html')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = get_user_role(request.user)
            
            # Check if user has required role
            if user_role not in allowed_roles:
                # Log the violation
                client_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                           request.META.get('REMOTE_ADDR', 'Unknown'))
                if client_ip and ',' in client_ip:
                    client_ip = client_ip.split(',')[0].strip()
                
                log_access_violation(
                    request.user, 
                    request.path, 
                    client_ip, 
                    f'role_violation_required_{allowed_roles}_got_{user_role}'
                )
                
                # Set appropriate error message
                if user_role == 'anonymous':
                    messages.error(request, "Please log in to access this page.")
                    return redirect('accounts:client_login')
                else:
                    messages.error(request, f"Access denied. This page requires {' or '.join(allowed_roles)} privileges.")
                    return redirect(get_appropriate_redirect(request.user))
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_admin_role(view_func):
    """
    Decorator to require admin role (admin, manager, staff - NOT supervisor).
    Blocks site managers and public users.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_role = get_user_role(request.user)
        
        if user_role not in ['admin', 'superadmin']:
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                       request.META.get('REMOTE_ADDR', 'Unknown'))
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            log_access_violation(request.user, request.path, client_ip, 'admin_access_denied')
            
            if user_role == 'site_manager':
                messages.error(request, "Site managers cannot access admin areas.")
                return redirect('site_diary:dashboard')
            elif user_role == 'public':
                messages.error(request, "This area requires admin privileges.")
                return redirect('accounts:client_login')
            else:
                messages.error(request, "Access denied.")
                return redirect('core:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def require_site_manager_role(view_func):
    """
    Decorator to require site manager role (supervisor).
    Blocks admins and public users.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_role = get_user_role(request.user)
        
        if user_role not in ['site_manager', 'superadmin']:
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                       request.META.get('REMOTE_ADDR', 'Unknown'))
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            log_access_violation(request.user, request.path, client_ip, 'site_manager_access_denied')
            
            if user_role == 'admin':
                messages.error(request, "Admin users cannot access site manager areas.")
                return redirect('portfolio:projectmanagement')
            elif user_role == 'public':
                messages.error(request, "This area requires site manager privileges.")
                return redirect('accounts:client_login')
            else:
                messages.error(request, "Access denied.")
                return redirect('core:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def require_public_role(view_func):
    """
    Decorator to require public/client role.
    Blocks admin users and site managers from accessing client areas.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_role = get_user_role(request.user)
        
        if user_role not in ['public', 'superadmin']:
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                       request.META.get('REMOTE_ADDR', 'Unknown'))
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            log_access_violation(request.user, request.path, client_ip, 'client_access_denied')
            
            if user_role == 'admin':
                messages.error(request, "Admin users cannot access client areas. Use the admin interface.")
                return redirect('portfolio:projectmanagement')
            elif user_role == 'site_manager':
                messages.error(request, "Site managers cannot access client areas.")
                return redirect('site_diary:dashboard')
            else:
                messages.error(request, "Access denied.")
                return redirect('core:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def require_superadmin_role(view_func):
    """
    Decorator to require superadmin role.
    Only Django superusers can access.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                       request.META.get('REMOTE_ADDR', 'Unknown'))
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            log_access_violation(request.user, request.path, client_ip, 'superadmin_access_denied')
            messages.error(request, "This area requires superadmin privileges.")
            return redirect(get_appropriate_redirect(request.user))
        
        return view_func(request, *args, **kwargs)
    return wrapper

def allow_public_access(view_func):
    """
    Decorator to explicitly allow public access (no authentication required).
    This is mainly for documentation purposes.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper

def block_role(blocked_roles):
    """
    Decorator to block specific roles from accessing a view.
    
    Args:
        blocked_roles (list): List of roles to block
    
    Usage:
        @block_role(['admin', 'site_manager'])
        def client_only_view(request):
            return render(request, 'client/dashboard.html')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = get_user_role(request.user)
            
            if user_role in blocked_roles:
                client_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                           request.META.get('REMOTE_ADDR', 'Unknown'))
                if client_ip and ',' in client_ip:
                    client_ip = client_ip.split(',')[0].strip()
                
                log_access_violation(
                    request.user, 
                    request.path, 
                    client_ip, 
                    f'blocked_role_{user_role}'
                )
                
                messages.error(request, f"Access denied. {user_role.title()} users cannot access this page.")
                return redirect(get_appropriate_redirect(request.user))
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def admin_or_site_manager_required(view_func):
    """
    Decorator to require either admin or site manager role.
    Useful for views that both roles should access.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_role = get_user_role(request.user)
        
        if user_role not in ['admin', 'site_manager', 'superadmin']:
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', 
                                       request.META.get('REMOTE_ADDR', 'Unknown'))
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            log_access_violation(request.user, request.path, client_ip, 'staff_access_denied')
            
            if user_role == 'public':
                messages.error(request, "This area requires admin or site manager privileges.")
                return redirect('accounts:client_login')
            else:
                messages.error(request, "Access denied.")
                return redirect('core:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def role_based_redirect(view_func):
    """
    Decorator that redirects users to their appropriate dashboard if they access a generic view.
    Useful for login success redirects.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            dashboard_url = get_appropriate_redirect(request.user)
            if dashboard_url != 'core:index':  # Don't redirect if already going to index
                return redirect(dashboard_url)
        
        return view_func(request, *args, **kwargs)
    return wrapper

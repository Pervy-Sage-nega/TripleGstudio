"""
Decorators for the Triple G Blog System
Role-based access control decorators
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden


def require_site_manager_role(view_func):
    """
    Decorator to require site manager role
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is superuser (always allowed)
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Check if user has site manager profile
        if hasattr(request.user, 'sitemanagerprofile'):
            site_manager = request.user.sitemanagerprofile
            if site_manager.approval_status == 'approved' and site_manager.can_login():
                return view_func(request, *args, **kwargs)
        
        # Check if user has admin profile (admins can also manage blogs)
        if hasattr(request.user, 'adminprofile'):
            admin_profile = request.user.adminprofile
            if admin_profile.approval_status == 'approved' and admin_profile.can_login():
                return view_func(request, *args, **kwargs)
        
        # User doesn't have permission
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('core:index')
    
    return _wrapped_view


def require_admin_role(view_func):
    """
    Decorator to require admin role (Administrator, Project Manager, or Site Supervisor)
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is superuser
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Check if user has admin profile with appropriate admin role
        if hasattr(request.user, 'adminprofile'):
            admin_profile = request.user.adminprofile
            # Allow admin, manager, supervisor, and staff roles for blog management
            allowed_roles = ['admin', 'manager', 'supervisor', 'staff']
            if (admin_profile.approval_status == 'approved' and 
                admin_profile.admin_role in allowed_roles and
                admin_profile.can_login()):
                return view_func(request, *args, **kwargs)
        
        # User doesn't have permission
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('core:index')
    
    return _wrapped_view


def allow_public_access(view_func):
    """
    Decorator to explicitly mark views as publicly accessible
    This is mainly for documentation purposes
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

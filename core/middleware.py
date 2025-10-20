from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
import re

class UnauthorizedAccessMiddleware:
    """
    Middleware to catch unauthorized access attempts to admin/site manager areas
    and redirect to the appropriate custom 401 error page.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define admin-only URL patterns (show 401_2.html)
        self.admin_only_patterns = [
            r'^/admin-panel/',                  # Admin side URLs
            r'^/adminside/',                    # Direct admin URLs
            r'^/portfolio/projectmanagement/',  # Portfolio management dashboard
            r'^/blog/blogmanagement/',          # Blog admin dashboard
            r'^/diary/adminside/',              # Diary admin routes
            r'^/admin/',                        # Django admin
        ]

        # Django admin authentication endpoints (allowed for everyone)
        self.admin_login_patterns = [
            r'^/admin/login/?$',
            r'^/admin/logout/?$',
        ]
        
        # Define site manager/diary URL patterns (show 401.html)
        self.site_manager_patterns = [
            r'^/diary/',        # Site diary URLs  
        ]
        
        # Define login pages that should not show modals when accessed after unauthorized attempts
        self.login_pages = [
            r'^/accounts/client/login/',
            r'^/accounts/admin-auth/login/',
            r'^/accounts/sitemanager/login/',
        ]
    
    def __call__(self, request):
        # Pre-check for protected URLs before processing
        if self._should_intercept_request(request):
            context = self._get_error_context(request)
            error_template = self._get_error_template_by_path(request.path)
            if error_template:
                # Clear any existing messages to prevent modal conflicts
                self._clear_messages(request)
                return render(request, error_template, context, status=401)
        
        # Since we're running before other middleware, we don't need to check for login pages here
        
        response = self.get_response(request)
        
        # Post-check for unauthorized responses
        error_template = self._get_error_template(request, response)
        if error_template:
            context = self._get_error_context(request)
            # Clear any existing messages to prevent modal conflicts
            self._clear_messages(request)
            return render(request, error_template, context, status=401)
            
        return response
    
    def _get_error_template(self, request, response):
        """
        Determine which error template to show based on the request path and user type.
        Returns the template path or None if no error handling needed.
        """
        # Check if the response is a 401 or 403 status
        if response.status_code not in [401, 403]:
            return None
            
        path = request.path
        
        # Check if trying to access admin-only areas
        for pattern in self.admin_only_patterns:
            if re.match(pattern, path):
                return 'page error/401_2.html'  # Admin-specific error page
        
        # Check if trying to access site manager areas
        for pattern in self.site_manager_patterns:
            if re.match(pattern, path):
                return 'page error/401.html'   # Client-focused error page
                
        return None
    
    def _should_intercept_request(self, request):
        """
        Check if this request should be intercepted before processing.
        Returns True if user is trying to access protected areas without proper permissions.
        """
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            path = request.path
            if self._matches_patterns(path, self.admin_login_patterns):
                return False
            # Allow anonymous users to reach Django admin login pages
            if self._matches_patterns(path, self.admin_only_patterns):
                return False
            # Block anonymous access to site manager areas
            return self._matches_patterns(path, self.site_manager_patterns)
        
        # Allow superusers to reach Django admin without interception
        if request.user.is_superuser:
            return False

        # Check if authenticated user has proper permissions
        try:
            from accounts.models import Profile, AdminProfile, SiteManagerProfile
            
            path = request.path
            
            # Check admin-only areas (excluding login/logout)
            if self._matches_patterns(path, self.admin_login_patterns):
                return False

            for pattern in self.admin_only_patterns:
                if re.match(pattern, path):
                    # Only admins can access these areas
                    return not AdminProfile.objects.filter(
                        user=request.user,
                        approval_status='approved',
                        admin_role__in=['admin', 'manager', 'supervisor', 'staff']
                    ).exists()
            
            # Check site manager areas
            for pattern in self.site_manager_patterns:
                if re.match(pattern, path):
                    # Site managers or admins can access these areas
                    has_site_manager = SiteManagerProfile.objects.filter(
                        user=request.user, 
                        approval_status='approved'
                    ).exists()
                    has_admin = AdminProfile.objects.filter(
                        user=request.user, 
                        approval_status='approved',
                        admin_role__in=['admin', 'manager', 'supervisor', 'staff']
                    ).exists()
                    return not (has_site_manager or has_admin)
                    
        except Exception:
            # If there's an error checking permissions, intercept for safety
            return self._is_protected_path(request.path)
        
        return False
    
    def _is_protected_path(self, path):
        """Check if the path matches any protected patterns."""
        all_patterns = self.admin_only_patterns + self.site_manager_patterns
        return self._matches_patterns(path, all_patterns)

    def _matches_patterns(self, path, patterns):
        """Return True if the path matches any regex in patterns."""
        return any(re.match(pattern, path) for pattern in patterns)
    
    def _get_error_template_by_path(self, path):
        """Get error template based on path only."""
        # Skip admin login/logout pages
        if self._matches_patterns(path, self.admin_login_patterns):
            return None

        # Check admin-only areas
        for pattern in self.admin_only_patterns:
            if re.match(pattern, path):
                return 'page error/401_2.html'
        
        # Check site manager areas
        for pattern in self.site_manager_patterns:
            if re.match(pattern, path):
                return 'page error/401.html'
        
        return None
    
    def _is_login_page_with_error_context(self, request):
        """
        Check if this is a login page that might have error messages from unauthorized access attempts.
        """
        path = request.path
        for pattern in self.login_pages:
            if re.match(pattern, path):
                # Check if there are messages that might be from unauthorized access
                try:
                    from django.contrib.messages import get_messages
                    storage = get_messages(request)
                    # Peek at messages without consuming them
                    messages_list = list(storage)
                    # If there are error messages about permissions, clear them
                    for message in messages_list:
                        if any(keyword in str(message).lower() for keyword in 
                               ['permission', 'access', 'denied', 'unauthorized', 'admin']):
                            return True
                except Exception:
                    pass
        return False
    
    def _clear_messages(self, request):
        """Clear Django messages to prevent modal conflicts."""
        # Since we're running before MessageMiddleware, we need to be careful
        if hasattr(request, '_messages'):
            request._messages.used = True
        
        # Also try to clear from storage if messages middleware has run
        try:
            from django.contrib.messages import get_messages
            messages = get_messages(request)
            for message in messages:
                pass  # This consumes all messages
        except Exception:
            # Messages middleware might not have run yet, which is fine
            pass
    
    def _get_error_context(self, request):
        """
        Get context data for error templates based on user type and request.
        """
        context = {
            'user_type': 'anonymous',
            'is_authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
        }
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Try to determine user type based on their profile
            try:
                from accounts.models import Profile, AdminProfile, SiteManagerProfile
                
                # Check if user has site manager profile
                if SiteManagerProfile.objects.filter(user=request.user).exists():
                    context['user_type'] = 'site_manager'
                # Check if user has admin profile
                elif AdminProfile.objects.filter(user=request.user).exists():
                    context['user_type'] = 'admin'
                # Check if user has client profile
                elif Profile.objects.filter(user=request.user).exists():
                    context['user_type'] = 'client'
                else:
                    context['user_type'] = 'unknown'
                    
            except Exception:
                context['user_type'] = 'unknown'
        
        return context
    
    def process_exception(self, request, exception):
        """
        Handle permission denied exceptions.
        """
        from django.core.exceptions import PermissionDenied
        
        if isinstance(exception, PermissionDenied):
            path = request.path
            context = self._get_error_context(request)
            
            # Clear any existing messages to prevent modal conflicts
            self._clear_messages(request)
            
            # Get appropriate error template
            error_template = self._get_error_template_by_path(path)
            if error_template:
                return render(request, error_template, context, status=401)
        
        return None

from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from accounts.models import AdminProfile


class AdminAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to ensure proper admin authentication across all admin pages.
    Redirects unauthenticated users to admin login page.
    """
    
    # Admin URL patterns that require authentication
    ADMIN_URL_PATTERNS = [
        '/admin-side/',
        '/portfolio/admin/',
        '/site-diary/admin/',
        '/blog/admin/',
        '/chatbot/admin/',
    ]
    
    # URLs that don't require authentication
    EXEMPT_URLS = [
        '/accounts/admin-auth/login/',
        '/accounts/admin-auth/register/',
        '/accounts/admin-auth/verify-otp/',
        '/accounts/admin-auth/resend-otp/',
        '/accounts/admin-auth/logout/',
        '/admin/',  # Django admin
        '/static/',
        '/media/',
    ]
    
    def process_request(self, request):
        """
        Check if the request is for an admin page and handle authentication
        """
        path = request.path
        
        # Skip if not an admin URL
        if not any(path.startswith(pattern) for pattern in self.ADMIN_URL_PATTERNS):
            return None
        
        # Skip exempt URLs
        if any(path.startswith(exempt) for exempt in self.EXEMPT_URLS):
            return None
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to access the admin panel.')
            return redirect('accounts:admin_login')
        
        # Check if user has admin profile
        try:
            admin_profile = AdminProfile.objects.get(user=request.user)
            
            # Check if admin account is approved
            if admin_profile.approval_status != 'approved':
                messages.error(request, 'Your admin account is not approved or is suspended.')
                return redirect('accounts:admin_login')
            
            # Check if account is locked
            if hasattr(admin_profile, 'is_account_locked') and admin_profile.is_account_locked():
                messages.error(request, 'Your admin account is temporarily locked. Please try again later.')
                return redirect('accounts:admin_login')
                
        except AdminProfile.DoesNotExist:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('accounts:admin_login')
        
        # If all checks pass, continue with the request
        return None
    
    def process_response(self, request, response):
        """
        Add cache control headers to admin pages to prevent caching
        """
        path = request.path
        
        # Add no-cache headers for admin pages
        if any(path.startswith(pattern) for pattern in self.ADMIN_URL_PATTERNS):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response

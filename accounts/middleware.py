"""
Role-Based Access Control Middleware for Triple G BuildHub
Handles routing users to appropriate interfaces based on their roles.
"""
import logging
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('security')

class RoleBasedAccessMiddleware(MiddlewareMixin):
    """
    Middleware to enforce role-based access control across the application.
    Routes users to appropriate interfaces and blocks unauthorized access.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process each request to enforce access control"""
        
        # Skip middleware for certain paths
        if self._should_skip_middleware(request):
            return None
            
        # Get user role information
        user_role = self._get_user_role(request.user)
        current_path = request.path
        
        # Apply access control rules
        return self._enforce_access_control(request, user_role, current_path)
    
    def _should_skip_middleware(self, request):
        """Determine if middleware should be skipped for this request"""
        skip_paths = [
            '/static/', '/media/', '/favicon.ico',
            '/accounts/client/login/', '/accounts/client/register/',
            '/accounts/admin-auth/login/', '/accounts/admin-auth/register/',
            '/accounts/client/verify-otp/', '/accounts/admin-auth/verify-otp/',
            '/accounts/client/logout/', '/accounts/admin-auth/logout/',
            '/admin/login/', '/admin/logout/',
        ]
        
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _get_user_role(self, user):
        """Determine user role based on authentication and profile"""
        if not user.is_authenticated:
            return 'anonymous'
        
        # Super Admin (Django superuser)
        if user.is_superuser:
            return 'superadmin'
        
        # Check for AdminProfile first (prioritize admin over site manager)
        if hasattr(user, 'adminprofile') and user.adminprofile.can_login():
            admin_role = user.adminprofile.admin_role
            
            # Admin (admin, manager, supervisor, staff roles)
            if admin_role in ['admin', 'manager', 'supervisor', 'staff']:
                return 'admin'
        
        # Check for SiteManagerProfile second
        if hasattr(user, 'sitemanagerprofile') and user.sitemanagerprofile.can_login():
            return 'site_manager'
        
        # Regular authenticated user (public/client)
        return 'public'
    
    def _enforce_access_control(self, request, user_role, current_path):
        """Enforce access control rules based on user role and path"""
        
        # Define access patterns for each role
        access_patterns = {
            'public': {
                'allowed': [
                    '/', '/about/', '/contact/', '/project/',
                    '/blog/', '/portfolio/',
                    '/accounts/client/', '/usersettings/', '/user/',
                ],
                'blocked': [
                    '/accounts/admin-auth/', '/adminside/', '/portfolio/projectmanagement/',
                    '/blog/blogmanagement/', '/diary/adminside/',
                ],
                'redirect_to': 'accounts:client_login'
            },
            'admin': {
                'allowed': [
                    '/', '/about/', '/contact/', '/project/', '/blog/',
                    '/accounts/admin-auth/', '/adminside/', '/portfolio/projectmanagement/',
                    '/blog/blogmanagement/', '/diary/adminside/',
                ],
                'blocked': [
                    '/accounts/client/', '/usersettings/', '/user/',
                    '/diary/dashboard/', '/diary/newproject/', '/diary/createblog/',
                ],
                'redirect_to': 'portfolio:projectmanagement'
            },
            'site_manager': {
                'allowed': [
                    '/', '/about/', '/contact/', '/project/', '/blog/',
                    '/diary/', '/chatbot/', '/site/',
                ],
                'blocked': [
                    '/accounts/client/', '/usersettings/', '/user/',
                    '/accounts/admin-auth/', '/portfolio/projectmanagement/',
                    '/blog/blogmanagement/', '/diary/adminside/',
                ],
                'redirect_to': 'site_diary:dashboard'
            },
            'superadmin': {
                'allowed': ['*'],  # Super admin can access everything
                'blocked': [],
                'redirect_to': '/admin/'
            },
            'anonymous': {
                'allowed': [
                    '/', '/about/', '/contact/', '/project/', '/blog/',
                ],
                'blocked': [
                    '/accounts/client/', '/accounts/admin-auth/',
                    '/usersettings/', '/user/', '/portfolio/projectmanagement/',
                    '/blog/blogmanagement/', '/diary/', '/adminside/',
                ],
                'redirect_to': 'accounts:client_login'
            }
        }
        
        # Get access rules for current user role
        rules = access_patterns.get(user_role, access_patterns['anonymous'])
        
        # Check if path is blocked
        if self._is_path_blocked(current_path, rules['blocked']):
            return self._handle_blocked_access(request, user_role, current_path, rules['redirect_to'])
        
        # Check if path requires authentication but user is anonymous
        if user_role == 'anonymous' and self._requires_authentication(current_path):
            return redirect('accounts:client_login')
        
        return None
    
    def _is_path_blocked(self, current_path, blocked_patterns):
        """Check if current path matches any blocked patterns"""
        return any(current_path.startswith(pattern) for pattern in blocked_patterns)
    
    def _requires_authentication(self, current_path):
        """Check if path requires authentication"""
        protected_patterns = [
            '/usersettings/', '/user/', '/portfolio/projectmanagement/',
            '/blog/blogmanagement/', '/diary/', '/adminside/',
        ]
        return any(current_path.startswith(pattern) for pattern in protected_patterns)
    
    def _handle_blocked_access(self, request, user_role, attempted_path, redirect_to):
        """Handle blocked access attempts with appropriate messaging and logging"""
        
        # Log the access violation
        if request.user.is_authenticated:
            client_ip = self._get_client_ip(request)
            logger.warning(
                f"ACCESS VIOLATION: {user_role} user '{request.user.username}' "
                f"attempted to access '{attempted_path}' from IP {client_ip}"
            )
        
        # Set appropriate error message
        error_messages = {
            'public': "You don't have permission to access admin areas.",
            'admin': "Admin users cannot access client areas. Use the admin interface.",
            'site_manager': "Site managers cannot access admin or client areas.",
            'anonymous': "Please log in to access this page."
        }
        
        if user_role == 'anonymous':
            try:
                if redirect_to.startswith('/'):
                    return redirect(redirect_to)
                else:
                    return redirect(redirect_to)
            except:
                return redirect('accounts:client_login')

        raise PermissionDenied(error_messages.get(user_role, "Access denied."))
    
    def _get_client_ip(self, request):
        """Get client IP address for logging"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip

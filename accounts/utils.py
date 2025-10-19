"""
Utility functions for role-based access control in Triple G BuildHub
"""
import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger('security')

def send_admin_approval_email(profile, approved_by_user):
    """
    Send approval email to admin/site manager based on their profile type.
    
    Args:
        profile: AdminProfile or SiteManagerProfile instance
        approved_by_user: User who approved the account
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    user = profile.user
    
    try:
        # Check if it's a SiteManagerProfile or AdminProfile with site_manager role
        if profile.__class__.__name__ == 'SiteManagerProfile' or (hasattr(profile, 'admin_role') and profile.admin_role == 'site_manager'):
            # Site Manager approval email
            subject = 'Site Manager Account Approved - Triple G BuildHub'
            login_url = 'http://127.0.0.1:8000/accounts/sitemanager/login/'
            role_features = '''- Create and manage site diaries
- Collaborate with teams and clients
- Access all construction project management tools'''
            role_title = 'Site Manager'
        else:
            # Admin approval email
            subject = 'Admin Account Approved - Triple G BuildHub'
            login_url = 'http://127.0.0.1:8000/accounts/admin-auth/login/'
            role_features = '''- Full system administration access
- Manage users and permissions
- Access all administrative features
- Oversee project management and reporting'''
            role_title = profile.get_admin_role_display() if hasattr(profile, 'get_admin_role_display') else 'Admin'
        
        message = f'''
Hello {user.first_name},

Great news! Your {role_title} account has been approved by our admin team.

You can now log in to your account and start using Triple G BuildHub's features:
{role_features}

Login URL: {login_url}

Your login credentials:
- Email: {user.email}
- Password: [Use the password you created during registration]

Welcome to Triple G BuildHub!

Best regards,
Triple G BuildHub Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
        
    except Exception as e:
        print(f"Failed to send approval email to {user.email}: {str(e)}")
        return False

def send_admin_denial_email(profile):
    """
    Send denial email to admin/site manager based on their profile type.
    
    Args:
        profile: AdminProfile or SiteManagerProfile instance
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    user = profile.user
    
    try:
        if profile.__class__.__name__ == 'SiteManagerProfile' or (hasattr(profile, 'admin_role') and profile.admin_role == 'site_manager'):
            subject = 'Site Manager Account Application Update - Triple G BuildHub'
            role_title = 'Site Manager'
        else:
            subject = 'Admin Account Application Update - Triple G BuildHub'
            role_title = profile.get_admin_role_display() if hasattr(profile, 'get_admin_role_display') else 'Admin'
        
        message = f'''
Hello {user.first_name},

Thank you for your interest in becoming a {role_title} with Triple G BuildHub.

After reviewing your application, we are unable to approve your account at this time. This could be due to various reasons such as incomplete information or current capacity limitations.

If you believe this is an error or would like to reapply in the future, please contact our support team.

Thank you for your understanding.

Best regards,
Triple G BuildHub Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
        
    except Exception as e:
        print(f"Failed to send denial email to {user.email}: {str(e)}")
        return False

def send_admin_suspension_email(profile):
    """
    Send suspension email to admin/site manager based on their profile type.
    
    Args:
        profile: AdminProfile or SiteManagerProfile instance
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    user = profile.user
    
    try:
        if profile.__class__.__name__ == 'SiteManagerProfile' or (hasattr(profile, 'admin_role') and profile.admin_role == 'site_manager'):
            subject = 'Site Manager Account Suspended - Triple G BuildHub'
            role_title = 'Site Manager'
        else:
            subject = 'Admin Account Suspended - Triple G BuildHub'
            role_title = profile.get_admin_role_display() if hasattr(profile, 'get_admin_role_display') else 'Admin'
        
        message = f'''
Hello {user.first_name},

We are writing to inform you that your {role_title} account with Triple G BuildHub has been suspended.

This action may have been taken due to:
- Violation of terms of service
- Security concerns
- Administrative review requirements

Your account access has been temporarily disabled. If you believe this is an error or would like to appeal this decision, please contact our support team immediately.

Contact Support: support@tripleg.com

Best regards,
Triple G BuildHub Team
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
        
    except Exception as e:
        print(f"Failed to send suspension email to {user.email}: {str(e)}")
        return False

def get_user_role(user):
    """
    Determine user role based on authentication and profile.
    
    Returns:
        str: One of 'anonymous', 'public', 'admin', 'site_manager', 'superadmin'
    """
    if not user.is_authenticated:
        return 'anonymous'
    
    # Super Admin (Django superuser)
    if user.is_superuser:
        return 'superadmin'
    
    # Check for SiteManagerProfile first
    if hasattr(user, 'sitemanagerprofile') and user.sitemanagerprofile.can_login():
        return 'site_manager'
    
    # Check for AdminProfile
    if hasattr(user, 'adminprofile') and user.adminprofile.can_login():
        admin_role = user.adminprofile.admin_role
        
        # Admin (admin, manager, staff roles) - no longer includes site_manager
        if admin_role in ['admin', 'manager', 'staff']:
            return 'admin'
    
    # Regular authenticated user (public/client)
    return 'public'

def get_user_dashboard_url(user):
    """
    Get the appropriate dashboard URL for a user based on their role.
    
    Args:
        user: Django User instance
        
    Returns:
        str: URL name or path for user's dashboard
    """
    role = get_user_role(user)
    
    dashboard_urls = {
        'superadmin': '/admin/',
        'admin': 'admin_side:admin_home',
        'site_manager': 'site_diary:dashboard',  # Fixed: Site managers go to site diary dashboard
        'public': 'core:index',  # Client dashboard - redirect to home page with modal
        'anonymous': 'accounts:client_login'
    }
    
    return dashboard_urls.get(role, 'core:index')

def get_user_login_url(user_type='client'):
    """
    Get the appropriate login URL based on user type.
    
    Args:
        user_type (str): 'client', 'admin', or 'superadmin'
        
    Returns:
        str: URL name for login page
    """
    login_urls = {
        'client': 'accounts:client_login',
        'admin': 'accounts:admin_login',
        'superadmin': '/admin/login/',
    }
    
    return login_urls.get(user_type, 'accounts:client_login')

def can_access_path(user, path):
    """
    Check if a user can access a specific path based on their role.
    
    Args:
        user: Django User instance
        path (str): URL path to check
        
    Returns:
        bool: True if user can access the path, False otherwise
    """
    role = get_user_role(user)
    
    # Define access patterns for each role
    access_patterns = {
        'superadmin': {
            'allowed': ['*'],  # Can access everything
            'blocked': []
        },
        'admin': {
            'allowed': [
                '/', '/about/', '/contact/', '/project/', '/blog/',
                '/accounts/admin-auth/', '/portfolio/projectmanagement/',
                '/blog/blogmanagement/', '/diary/adminside/',
            ],
            'blocked': [
                '/accounts/client/', '/usersettings/', '/user/',
                '/diary/dashboard/', '/diary/newproject/', '/diary/createblog/',
            ]
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
            ]
        },
        'public': {
            'allowed': [
                '/', '/about/', '/contact/', '/project/',
                '/blog/', '/portfolio/',
                '/accounts/client/', '/usersettings/', '/user/',
            ],
            'blocked': [
                '/accounts/admin-auth/', '/adminside/', '/portfolio/projectmanagement/',
                '/blog/blogmanagement/', '/diary/adminside/',
            ]
        },
        'anonymous': {
            'allowed': [
                '/', '/about/', '/contact/', '/project/', '/blog/',
            ],
            'blocked': [
                '/accounts/client/', '/accounts/admin-auth/',
                '/usersettings/', '/user/', '/portfolio/projectmanagement/',
                '/blog/blogmanagement/', '/diary/', '/adminside/',
            ]
        }
    }
    
    rules = access_patterns.get(role, access_patterns['anonymous'])
    
    # Check if superadmin (can access everything)
    if '*' in rules['allowed']:
        return True
    
    # Check if path is explicitly blocked
    if any(path.startswith(blocked) for blocked in rules['blocked']):
        return False
    
    # Check if path is explicitly allowed
    if any(path.startswith(allowed) for allowed in rules['allowed']):
        return True
    
    # Default: block access for protected paths
    protected_patterns = [
        '/usersettings/', '/user/', '/portfolio/projectmanagement/',
        '/blog/blogmanagement/', '/diary/', '/adminside/',
    ]
    
    if any(path.startswith(pattern) for pattern in protected_patterns):
        return False
    
    # Allow access to public paths by default
    return True

def log_access_violation(user, attempted_path, client_ip, violation_type='unauthorized_access'):
    """
    Log access violations for security monitoring.
    
    Args:
        user: Django User instance
        attempted_path (str): Path user tried to access
        client_ip (str): Client IP address
        violation_type (str): Type of violation
    """
    role = get_user_role(user)
    
    if user.is_authenticated:
        logger.warning(
            f"SECURITY VIOLATION [{violation_type}]: "
            f"{role} user '{user.username}' (ID: {user.id}) "
            f"attempted to access '{attempted_path}' from IP {client_ip}"
        )
    else:
        logger.warning(
            f"SECURITY VIOLATION [{violation_type}]: "
            f"Anonymous user attempted to access '{attempted_path}' from IP {client_ip}"
        )

def get_appropriate_redirect(user, requested_path=None):
    """
    Get appropriate redirect URL for a user based on their role and context.
    
    Args:
        user: Django User instance
        requested_path (str, optional): Path user was trying to access
        
    Returns:
        str: Redirect URL or URL name
    """
    role = get_user_role(user)
    
    # If user is trying to access a path they can't access, redirect to their dashboard
    if requested_path and not can_access_path(user, requested_path):
        return get_user_dashboard_url(user)
    
    # Default redirects based on role
    default_redirects = {
        'superadmin': '/admin/',
        'admin': 'admin_side:admin_home',
        'site_manager': 'site_diary:dashboard',  # Fixed: Site managers go to site diary dashboard
        'public': 'core:usersettings',  # Client dashboard
        'anonymous': 'accounts:client_login'
    }
    
    return default_redirects.get(role, 'core:index')

def is_admin_user(user):
    """Check if user is an admin (not site manager or public user)"""
    return get_user_role(user) == 'admin'

def is_site_manager(user):
    """Check if user is a site manager"""
    return get_user_role(user) == 'site_manager'

def is_public_user(user):
    """Check if user is a public/client user"""
    return get_user_role(user) == 'public'

def is_superadmin(user):
    """Check if user is a superadmin"""
    return get_user_role(user) == 'superadmin'

def get_user_interface_template(user):
    """
    Get the appropriate base template for a user's interface.
    
    Args:
        user: Django User instance
        
    Returns:
        str: Template path for user's interface
    """
    role = get_user_role(user)
    
    templates = {
        'superadmin': 'admin/base.html',  # Django admin template
        'admin': 'admin-nav-footer-template/base.html',
        'site_manager': 'site_diary/navtemplate/layout.html',
        'public': 'layout.html',
        'anonymous': 'layout.html'
    }
    
    return templates.get(role, 'layout.html')

def get_navigation_context(user):
    """
    Get navigation context data for templates based on user role.
    
    Args:
        user: Django User instance
        
    Returns:
        dict: Context data for navigation
    """
    role = get_user_role(user)
    
    context = {
        'user_role': role,
        'is_admin': is_admin_user(user),
        'is_site_manager': is_site_manager(user),
        'is_public_user': is_public_user(user),
        'is_superadmin': is_superadmin(user),
        'dashboard_url': get_user_dashboard_url(user),
        'interface_template': get_user_interface_template(user)
    }
    
    return context

"""
Context processors for role-based access control in Triple G BuildHub
Provides role information to all templates automatically.
"""
from .utils import get_user_role, get_user_dashboard_url, get_navigation_context

def role_context(request):
    """
    Context processor to add user role information to all templates.
    This makes role-based template logic easier to implement.
    
    Usage in templates:
        {% if user_role == 'admin' %}
            <!-- Admin-specific content -->
        {% elif user_role == 'site_manager' %}
            <!-- Site manager-specific content -->
        {% elif user_role == 'public' %}
            <!-- Client-specific content -->
        {% endif %}
    """
    if not hasattr(request, 'user'):
        return {}
    
    # Get comprehensive navigation context
    context = get_navigation_context(request.user)
    
    # Add additional template-specific context
    context.update({
        'user_dashboard_url': get_user_dashboard_url(request.user),
        'can_access_admin': context['is_admin'] or context['is_superadmin'],
        'can_access_site_manager': context['is_site_manager'] or context['is_superadmin'],
        'can_access_client': context['is_public_user'] or context['is_superadmin'],
        'show_admin_nav': context['is_admin'],
        'show_site_manager_nav': context['is_site_manager'],
        'show_public_nav': context['is_public_user'] or not request.user.is_authenticated,
    })
    
    return context

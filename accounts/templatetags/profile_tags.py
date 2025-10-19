from django import template
from django.templatetags.static import static
from site_diary.models import Project as SiteDiaryProject

register = template.Library()

@register.simple_tag
def profile_image_url(user):
    """
    Get the profile image URL for any user type or return default image.
    Works with Profile, AdminProfile, SiteManagerProfile, and SuperAdminProfile.
    """
    default_image = static('images/default-profile.png')
    
    if not user or not user.is_authenticated:
        return default_image
    
    # Check for regular Profile
    if hasattr(user, 'profile') and user.profile:
        return user.profile.get_profile_image_url()
    
    # Check for AdminProfile
    if hasattr(user, 'adminprofile') and user.adminprofile:
        return user.adminprofile.get_profile_image_url()
    
    # Check for SiteManagerProfile
    if hasattr(user, 'sitemanagerprofile') and user.sitemanagerprofile:
        return user.sitemanagerprofile.get_profile_image_url()
    
    # Check for SuperAdminProfile
    if hasattr(user, 'superadminprofile') and user.superadminprofile:
        return user.superadminprofile.get_profile_image_url()
    
    return default_image

@register.simple_tag
def get_user_profile(user):
    """
    Get the appropriate profile object for the user.
    Returns the profile object or None if no profile exists.
    """
    if not user or not user.is_authenticated:
        return None
    
    # Check for regular Profile
    if hasattr(user, 'profile'):
        return user.profile
    
    # Check for AdminProfile
    if hasattr(user, 'adminprofile'):
        return user.adminprofile
    
    # Check for SiteManagerProfile
    if hasattr(user, 'sitemanagerprofile'):
        return user.sitemanagerprofile
    
    # Check for SuperAdminProfile
    if hasattr(user, 'superadminprofile'):
        return user.superadminprofile
    
    return None

@register.filter
def has_projects(user):
    """Check if user has any assigned projects"""
    if not user or not user.is_authenticated:
        return False
    
    # Check if user has projects assigned directly
    if SiteDiaryProject.objects.filter(client=user).exists():
        return True
    
    # Check if user has projects by name matching
    user_full_name = user.get_full_name()
    if user_full_name:
        if SiteDiaryProject.objects.filter(client_name__icontains=user_full_name).exists():
            return True
    
    # Check by username
    if SiteDiaryProject.objects.filter(client_name__icontains=user.username).exists():
        return True
    
    return False

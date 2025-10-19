from django import template
from site_diary.models import Project as SiteDiaryProject

register = template.Library()

@register.filter
def has_projects(user):
    """Check if user has any assigned projects"""
    if not user.is_authenticated:
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
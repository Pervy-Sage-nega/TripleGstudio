from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from portfolio.models import Project

register = template.Library()


@register.simple_tag
def get_featured_projects(limit=3):
    """Get featured projects for display"""
    return Project.objects.filter(featured=True).select_related('category')[:limit]


@register.simple_tag
def get_recent_projects(limit=6):
    """Get recent projects for display"""
    return Project.objects.select_related('category').order_by('-completion_date', '-created_at')[:limit]


@register.filter
def status_badge_class(status):
    """Return CSS class for project status badge"""
    status_classes = {
        'planned': 'status-planned',
        'ongoing': 'status-ongoing', 
        'completed': 'status-completed'
    }
    return status_classes.get(status, 'status-default')


@register.filter
def truncate_description(description, words=20):
    """Truncate description to specified number of words"""
    word_list = description.split()
    if len(word_list) > words:
        return ' '.join(word_list[:words]) + '...'
    return description


@register.inclusion_tag('portfolio/partials/project_card.html')
def render_project_card(project, show_featured_badge=True):
    """Render a project card component"""
    return {
        'project': project,
        'show_featured_badge': show_featured_badge,
    }


@register.simple_tag
def project_image_url(project, fallback='images/image1.jpg'):
    """Get project image URL with fallback"""
    if project.hero_image:
        return project.hero_image.url
    elif project.images.exists():
        return project.images.first().image.url
    else:
        return f'/static/{fallback}'


@register.filter
def format_project_year(year):
    """Format project year for display"""
    return f"Year {year}"


@register.simple_tag
def get_project_stats_count(project):
    """Get count of project statistics"""
    return project.stats.count()


@register.simple_tag
def get_project_timeline_progress(project):
    """Calculate timeline completion percentage"""
    total_items = project.timeline.count()
    if total_items == 0:
        return 100 if project.status == 'completed' else 0
    
    completed_items = project.timeline.filter(completed=True).count()
    return int((completed_items / total_items) * 100)

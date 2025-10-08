from django import template

register = template.Library()

@register.filter
def status_class(status):
    """
    Convert blog post status to CSS class for styling
    draft -> pending (yellow/warning)
    published -> published (green/success)
    archived -> archived (gray/secondary)
    """
    status_map = {
        'draft': 'draft',
        'published': 'published',
        'archived': 'archived',
    }
    return status_map.get(status, 'draft')

@register.filter
def status_display(status):
    """
    Convert blog post status to display text
    """
    display_map = {
        'draft': 'Draft',
        'published': 'Published',
        'archived': 'Archived',
    }
    return display_map.get(status, status.title())

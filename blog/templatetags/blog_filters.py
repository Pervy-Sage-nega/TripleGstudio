from django import template
import html

register = template.Library()

@register.filter
def unescape_html(value):
    """Unescape HTML entities in the given value."""
    if value:
        return html.unescape(value)
    return value
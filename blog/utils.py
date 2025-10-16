import bleach
import re
from django.core.exceptions import ValidationError

# Allowed HTML tags for blog content
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'a', 'img', 'code', 'pre'
]

# Allowed attributes for HTML tags
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
}

def sanitize_content(content):
    """Sanitize HTML content to prevent XSS attacks"""
    if not content:
        return content
    
    return bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)

def contains_suspicious_content(content):
    """Check for suspicious patterns in content"""
    if not content:
        return False
    
    suspicious_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'onclick=',
        r'onerror=',
        r'onload=',
        r'data:text/html',
        r'vbscript:',
        r'expression\(',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def validate_image(image):
    """Validate uploaded image files"""
    from PIL import Image
    import os
    
    # Check file size (max 5MB)
    if image.size > 5 * 1024 * 1024:
        raise ValidationError("Image file too large (max 5MB)")
    
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError("Invalid file type")
    
    # Verify it's actually an image
    try:
        img = Image.open(image)
        img.verify()
    except:
        raise ValidationError("Invalid image file")
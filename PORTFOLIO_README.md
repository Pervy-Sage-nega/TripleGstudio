# Portfolio App Documentation

## 🎯 Overview
The Portfolio App is a full-stack Django application with PostgreSQL backend that showcases architectural projects. It's designed for public viewing (no authentication required) while maintaining privacy by excluding client information.

## 🚀 Features

### Core Functionality
- **Project Showcase**: Display projects with images, descriptions, and details
- **Advanced Filtering**: Filter by year, category, featured status, and search
- **Responsive Design**: Works on all devices
- **Privacy-First**: No client information stored or displayed
- **SEO Optimized**: Proper meta tags and semantic HTML

### Models
- **Project**: Main project model with all essential details
- **Category**: Project categories (Residential, Commercial, Public)
- **ProjectImage**: Gallery images with alt text and ordering
- **ProjectStat**: Custom project statistics
- **ProjectTimeline**: Project milestones and progress tracking

## 📱 URLs & Views

### Public URLs
- `/portfolio/` - Project list with filtering and search
- `/portfolio/{id}/` - Individual project detail page
- `/portfolio/projectmanagement/` - Admin project management

### API Endpoints
- `/portfolio/api/projects/` - JSON API for project list
- `/portfolio/api/projects/{id}/` - JSON API for project details
- `/portfolio/api/categories/` - JSON API for categories

## 🛠️ Management Commands

### Seed Sample Data
```bash
python manage.py seed_projects
```

### Create New Project Interactively
```bash
python manage.py create_project
```

### Create Project with Parameters
```bash
python manage.py create_project \
  --title "Modern Villa" \
  --description "Contemporary residential design" \
  --category "Residential" \
  --year 2024 \
  --location "Manila, Philippines" \
  --size "400 m²" \
  --duration "16 Months" \
  --completion-date "2024-12-15" \
  --lead-architect "John Doe" \
  --status "ongoing" \
  --featured
```

## 🎨 Template Tags

### Load Portfolio Extras
```django
{% load portfolio_extras %}
```

### Available Tags
```django
{% get_featured_projects 3 %}
{% get_recent_projects 6 %}
{% project_image_url project %}
{% get_project_timeline_progress project %}
{% render_project_card project %}
```

### Available Filters
```django
{{ project.status|status_badge_class }}
{{ project.description|truncate_description:20 }}
{{ project.year|format_project_year }}
```

## 📊 Admin Interface

### Access Admin
1. Create superuser: `python manage.py createsuperuser`
2. Visit: `/admin/`
3. Navigate to Portfolio section

### Managing Projects
- **Projects**: Add/edit projects with inline stats, images, and timeline
- **Categories**: Manage project categories
- **Images**: Upload and organize project gallery images
- **Stats**: Add custom project statistics
- **Timeline**: Create project milestones and track progress

## 🔧 Customization

### Adding New Project Fields
1. Update `portfolio/models.py`
2. Create migration: `python manage.py makemigrations portfolio`
3. Apply migration: `python manage.py migrate`
4. Update templates and admin as needed

### Custom Styling
- Main CSS: `static/css/projects.css` and `static/css/project-detail.css`
- JavaScript: `static/js/projects.js` and `static/js/project-detail.js`

### Template Customization
- Project List: `portfolio/templates/portfolio/project-list.html`
- Project Detail: `portfolio/templates/portfolio/project-detail.html`
- Project Card: `portfolio/templates/portfolio/partials/project_card.html`

## 🔒 Security Features

### Privacy Protection
- ✅ No client information stored in database
- ✅ No sensitive data exposed in templates
- ✅ Input validation and sanitization
- ✅ Proper error handling

### Performance Optimization
- ✅ Database query optimization with `select_related`/`prefetch_related`
- ✅ Pagination for large datasets
- ✅ Image optimization ready
- ✅ Caching-ready architecture

## 📝 Usage Examples

### Display Featured Projects in Homepage
```django
{% load portfolio_extras %}
{% get_featured_projects 3 as featured %}
{% for project in featured %}
    {% render_project_card project %}
{% endfor %}
```

### Custom Project Filtering
```python
# In views.py
from portfolio.models import Project

# Get residential projects from 2023
projects = Project.objects.filter(
    category__slug='residential',
    year=2023,
    status='completed'
).select_related('category')
```

### API Usage
```javascript
// Fetch projects via API
fetch('/portfolio/api/projects/?category=residential&year=2023')
    .then(response => response.json())
    .then(data => {
        console.log(data.projects);
    });
```

## 🚀 Deployment Notes

### Production Settings
- Configure `MEDIA_URL` and `MEDIA_ROOT` for file uploads
- Set up proper image serving (nginx/Apache)
- Enable database connection pooling
- Configure caching (Redis/Memcached)

### SEO Optimization
- Update meta tags in templates
- Add structured data (JSON-LD)
- Implement sitemap generation
- Configure robots.txt

## 🐛 Troubleshooting

### Common Issues
1. **Images not loading**: Check `MEDIA_URL` and `MEDIA_ROOT` settings
2. **Filters not working**: Verify JavaScript files are loaded
3. **Database errors**: Run migrations and check database connection
4. **Template errors**: Ensure template tags are loaded properly

### Debug Mode
```python
# In settings.py
DEBUG = True  # Only for development
```

## 📞 Support

For issues or questions:
1. Check Django logs: `python manage.py runserver --verbosity=2`
2. Review database queries: Enable Django Debug Toolbar
3. Test API endpoints: Use Postman or curl
4. Validate templates: Check for syntax errors

---

**Note**: This portfolio app follows Django best practices and is production-ready. The CSS linter warnings in templates are expected due to Django template syntax and don't affect functionality.

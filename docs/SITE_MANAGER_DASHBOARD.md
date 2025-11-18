# Site Manager Dashboard - Triple G BuildHub

## Overview
The Site Manager Dashboard provides comprehensive project management capabilities for construction site managers and architects.

## Features

### 🏗️ **Dashboard Overview**
- **Multi-project grid view** with real-time project cards
- **Performance analytics** for each project (budget usage, schedule adherence)
- **Dynamic statistics** showing active projects, on-schedule count, at-risk projects
- **Search and filtering** by project name, category, and status

### 📊 **Project Detail View**
- **Comprehensive project information** with client details and timeline
- **Progress tracking** with circular progress indicators and milestone visualization
- **Budget monitoring** with pie charts and financial breakdown
- **Site diary integration** showing recent entries and quick access
- **Resource management** displaying labor count, equipment, and delays
- **Document management** with file upload, download, and preview capabilities

### 🔧 **Interactive Features**
- **Real-time filtering** without page reload
- **Report generation** with API integration
- **Responsive design** for desktop, tablet, and mobile
- **Notification system** for user feedback
- **Timeline modal** for detailed project milestones

## Usage

### Getting Started
1. **Access Dashboard**: Navigate to `/site/dashboard/`
2. **View Projects**: Browse project cards with progress and analytics
3. **Filter Projects**: Use category, status, and search filters
4. **Project Details**: Click "View Details" for comprehensive project information

### Creating Sample Data
Run the management command to create sample projects:
```bash
python manage.py create_sample_projects
```

### API Endpoints
- **Report Generation**: `POST /site/api/generate-report/<project_id>/`
- **Project Filtering**: `GET /site/api/filter-projects/`

## File Structure
```
site_diary/
├── templates/site_diary/
│   ├── dashboard.html          # Main dashboard
│   └── project-detail.html     # Project detail view
├── static/
│   ├── css/sitecss/
│   │   ├── dashboard.css       # Dashboard styles
│   │   └── siteproject-detail.css  # Project detail styles
│   └── js/sitejs/
│       ├── sitemanager-dashboard.js  # Dashboard functionality
│       └── project-detail.js   # Project detail functionality
├── views.py                    # Django views
├── urls.py                     # URL patterns
└── management/commands/
    └── create_sample_projects.py  # Sample data generator
```

## Technical Implementation

### Backend (Django)
- **Enhanced views** with comprehensive project analytics
- **API endpoints** for AJAX functionality
- **User access control** with proper permissions
- **Database optimization** with select_related and prefetch_related

### Frontend (JavaScript/CSS)
- **Vanilla JavaScript** for filtering and search
- **CSS Grid/Flexbox** for responsive layouts
- **Smooth animations** and transitions
- **CSRF protection** for API calls

### Security
- **Login required** decorators
- **Role-based access control**
- **CSRF token validation**
- **User isolation** for project access

## Future Enhancements
- Real-time notifications with WebSockets
- Advanced reporting with charts and graphs
- File upload with drag-and-drop
- Calendar integration for project scheduling
- Mobile app companion

## Dependencies
- Django 4.x+
- Font Awesome 6.4.0
- Modern browser with ES6 support
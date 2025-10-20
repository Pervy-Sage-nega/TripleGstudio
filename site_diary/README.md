# Site Diary App - Complete Construction Management System

A comprehensive Django application for managing construction site diary entries, tracking project progress, labor, materials, equipment, delays, and generating detailed reports with full CRUD operations.

## Features

### Core Functionality
- **Project Management**: Create and manage construction projects with client details, budgets, and timelines
- **Daily Diary Entries**: Record daily work progress, weather conditions, and project updates with approval workflow
- **Labor Tracking**: Track workers, hours, costs, and productivity by trade with overtime calculations
- **Material Management**: Monitor material deliveries, usage, costs, and storage locations
- **Equipment Logging**: Record equipment usage, maintenance, rental costs, and fuel consumption
- **Delay Documentation**: Track and categorize project delays with cost impact analysis
- **Visitor Management**: Log site visitors, purposes, and safety briefings
- **Photo Documentation**: Attach multiple photos to diary entries for visual records

### Advanced Features
- **Entry Management**: View, edit, and delete diary entries with permission controls
- **Draft System**: Save entries as drafts before approval with enhanced search and pagination
- **Comprehensive Reports**: Generate detailed analytics with database-driven insights
- **Export Functionality**: Export reports to CSV format (summary, delays, labor, materials)
- **Real-time Statistics**: Dashboard with project progress, costs, and performance metrics

### User Roles & Permissions
- **Admin Users**: Full access to all projects and administrative functions
- **Project Managers**: Access to assigned projects and team management
- **Architects**: Access to projects they're assigned to with review capabilities
- **Regular Users**: Limited access based on project assignments

### Reports & Analytics
- **Project Statistics**: Progress tracking, cost analysis, and performance metrics
- **Delay Analysis**: Categorized delays with duration and cost impact
- **Weather Reports**: Weather condition analysis and impact on work
- **Labor Analytics**: Worker productivity, overtime, and cost analysis
- **Material Reports**: Usage tracking, delivery monitoring, and cost analysis
- **Equipment Utilization**: Operating hours, fuel consumption, and breakdown tracking
- **Monthly Progress**: Time-based progress tracking and trend analysis

## Models

### Core Models
- **Project**: Main project information and metadata
- **DiaryEntry**: Daily diary entries with weather, progress, and notes
- **LaborEntry**: Labor tracking with costs and productivity
- **MaterialEntry**: Material deliveries and usage tracking
- **EquipmentEntry**: Equipment usage and maintenance logs
- **DelayEntry**: Delay documentation with impact analysis
- **VisitorEntry**: Site visitor logs
- **DiaryPhoto**: Photo attachments for diary entries

## Setup Instructions

### 1. Database Migration
```bash
python manage.py makemigrations site_diary
python manage.py migrate
```

### 2. Create Sample Data (Optional)
```bash
python manage.py setup_sample_data
```

This creates:
- Sample users (admin, project manager, architect)
- Sample projects
- Sample diary entries with related data

### 3. Create Superuser (if not using sample data)
```bash
python manage.py createsuperuser
```

## Usage

### Creating Projects
1. Navigate to `/site_diary/newproject/`
2. Fill in project details including client, budget, and timeline
3. Assign project manager and architect

### Daily Diary Entries
1. Go to `/site_diary/` (main diary entry page)
2. Select project and date
3. Fill in weather conditions and work description
4. Add labor, material, equipment, delay, and visitor entries as needed
5. Upload photos if available
6. Submit for review/approval

### Viewing and Managing Entries
- `/site_diary/history/` - View all diary entries with advanced search and filtering
- `/site_diary/entry/<id>/` - View complete diary entry details
- `/site_diary/entry/<id>/edit/` - Edit existing diary entries (with permissions)
- `/site_diary/entry/<id>/delete/` - Delete draft entries (authorized users only)
- `/site_diary/sitedraft/` - View and manage draft entries with search and pagination

### Reports and Analytics
- `/site_diary/reports/` - Generate comprehensive project reports and analytics
- `/site_diary/export/reports/` - Export reports to CSV (summary, delays, labor, materials)
- `/site_diary/dashboard/` - Overview dashboard with project statistics

### Admin Functions
- `/site_diary/admin/clientproject/` - Manage all projects
- `/site_diary/admin/clientdiary/` - View all diary entries
- `/site_diary/admin/reports/` - Administrative reports and analytics

## API Endpoints

- `POST /site_diary/api/approve-entry/<entry_id>/` - Approve diary entry
- `GET /site_diary/api/project-details/<project_id>/` - Get project details

## Export Functionality

The application supports exporting reports in CSV format:

### Export Types
- **Summary Report**: Project overview with costs, progress, and statistics
- **Delays Report**: Detailed delay analysis with categories and impact
- **Labor Report**: Worker productivity, hours, and cost analysis  
- **Materials Report**: Material usage, deliveries, and cost tracking

### Export Usage
```
GET /site_diary/export/reports/?type=summary&start_date=2024-01-01&end_date=2024-12-31&project=1
```

Parameters:
- `type`: summary, delays, labor, materials
- `start_date`: Filter from date (YYYY-MM-DD)
- `end_date`: Filter to date (YYYY-MM-DD)
- `project`: Specific project ID (optional)

## Forms and Validation

The app includes comprehensive form validation for:
- Required fields validation
- Numeric range validation (percentages, temperatures)
- Date consistency checks
- User permission validation

## Admin Interface

All models are registered in Django admin with:
- List views with filtering and search
- Inline editing for related models
- Organized fieldsets for better UX
- Custom display fields and methods

## File Structure

```
site_diary/
├── models.py          # Database models
├── forms.py           # Django forms and formsets
├── views.py           # View functions and logic
├── urls.py            # URL routing
├── admin.py           # Admin interface configuration
├── utils.py           # Utility functions
├── management/
│   └── commands/
│       └── setup_sample_data.py  # Sample data creation
└── templates/         # HTML templates (existing)
```

## Dependencies

The app uses standard Django functionality and requires:
- Django (configured in main project)
- PIL/Pillow (for image handling)
- PostgreSQL (configured in settings)

## Testing

After setup, test the functionality by:
1. Creating a new project
2. Adding daily diary entries
3. Testing different user roles and permissions
4. Generating reports
5. Using the admin interface

## Notes

- All monetary values are stored as DecimalField for precision
- Images are uploaded to `media/diary_photos/YYYY/MM/DD/`
- The app integrates with the existing user authentication system
- Permissions are role-based with staff/non-staff distinctions

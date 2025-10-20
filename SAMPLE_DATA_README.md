# Sample Data Creator for Triple G Site Diary

This script creates comprehensive sample data for the Site Diary system, automatically assigning projects to the currently logged-in user account.

## Features

- **Automatic User Detection**: Finds the most recently logged-in staff user
- **Comprehensive Project Data**: Creates 6 diverse projects with detailed information
- **Complete Diary Entries**: Generates 30 days of realistic diary entries
- **Related Data**: Includes labor, materials, equipment, delays, and visitor entries
- **Dashboard Compatible**: All data works with the dashboard templates

## Quick Start

### Method 1: Using the Test Script (Recommended)
```bash
cd /path/to/TripleG
python test_sample_data.py
```

### Method 2: Using Django Management Command
```bash
# Create data for the most recently logged-in staff user
python manage.py create_sample_data

# Create data for a specific user
python manage.py create_sample_data --user-email your-email@example.com

# Clear existing projects first
python manage.py create_sample_data --clear-existing
```

## What Gets Created

### Projects (6 total)
1. **Metro Plaza Tower** - Commercial (42-story mixed-use)
2. **Seaside Resort Complex** - Commercial (Luxury resort)
3. **Green Valley Subdivision** - Residential (150 house units)
4. **Industrial Park Phase 1** - Industrial (Manufacturing facilities)
5. **Heritage Mall Renovation** - Commercial (Completed project)
6. **Riverside Bridge Construction** - Infrastructure (4-lane bridge)

### Diary Entries
- **30 days** of entries (excluding weekends)
- **Realistic weather data** (temperature, humidity, wind)
- **Work descriptions** and progress tracking
- **Photo documentation** flags

### Related Data for Each Entry
- **Labor Entries**: Different worker types with hours and rates
- **Material Entries**: Construction materials with quantities and costs
- **Equipment Entries**: Heavy machinery with operating hours
- **Delay Entries**: Realistic delays with impact levels (30% chance)
- **Visitor Entries**: Site visitors and inspections (20% chance)

## Project Details Include

- **Progress Tracking**: Realistic progress percentages
- **Budget Management**: Budget usage and cost tracking
- **Schedule Status**: On Track, Minor Delays, Completed Early
- **Project Phases**: Current milestone and phase descriptions
- **Categories**: Commercial, Residential, Industrial, Infrastructure
- **Locations**: Various Philippine locations
- **Client Information**: Realistic client names and companies

## Requirements

- Django project with Site Diary app installed
- At least one staff user account
- Database properly configured and migrated

## Troubleshooting

### No Staff Users Found
```bash
# Create a superuser first
python manage.py createsuperuser
```

### Database Errors
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### Permission Errors
Make sure your user account has `is_staff=True` and appropriate permissions.

## Data Structure

The sample data follows the Site Diary models:
- `Project` - Main project information
- `DiaryEntry` - Daily site diary entries
- `LaborEntry` - Worker information and hours
- `MaterialEntry` - Materials delivered and used
- `EquipmentEntry` - Equipment usage and costs
- `DelayEntry` - Project delays and issues
- `VisitorEntry` - Site visitors and inspections

## Customization

You can modify the sample data by editing:
- `site_diary/management/commands/create_sample_data.py`
- Update project details, locations, or data ranges
- Adjust the probability of delays and visitors
- Modify material types, equipment, or labor categories

## Clean Up

To remove sample data:
```bash
python manage.py create_sample_data --clear-existing
```

This will delete all projects for the specified user before creating new ones.
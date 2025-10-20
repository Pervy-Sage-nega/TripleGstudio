from django.db import models
from django.contrib.auth.models import User
from .models import Project, DiaryEntry

def get_user_projects(user):
    """Get projects accessible by a user"""
    if user.is_staff:
        return Project.objects.all()
    else:
        return Project.objects.filter(
            models.Q(project_manager=user) | models.Q(architect=user)
        )

def get_project_statistics(project):
    """Get comprehensive statistics for a project"""
    diary_entries = project.diary_entries.all()
    
    stats = {
        'total_entries': diary_entries.count(),
        'approved_entries': diary_entries.filter(approved=True).count(),
        'pending_entries': diary_entries.filter(approved=False).count(),
        'avg_progress': diary_entries.aggregate(
            avg=models.Avg('progress_percentage')
        )['avg'] or 0,
        'total_labor_cost': 0,
        'total_material_cost': 0,
        'total_equipment_cost': 0,
        'total_delay_hours': 0,
        'weather_breakdown': {},
    }
    
    # Calculate costs and delays
    for entry in diary_entries:
        # Labor costs
        for labor in entry.labor_entries.all():
            stats['total_labor_cost'] += labor.total_cost
        
        # Material costs
        for material in entry.material_entries.all():
            stats['total_material_cost'] += material.total_cost
        
        # Equipment costs
        for equipment in entry.equipment_entries.all():
            stats['total_equipment_cost'] += equipment.total_rental_cost
        
        # Delay hours
        for delay in entry.delay_entries.all():
            stats['total_delay_hours'] += delay.duration_hours
        
        # Weather breakdown
        if entry.weather_condition:
            if entry.weather_condition in stats['weather_breakdown']:
                stats['weather_breakdown'][entry.weather_condition] += 1
            else:
                stats['weather_breakdown'][entry.weather_condition] = 1
    
    stats['total_project_cost'] = (
        stats['total_labor_cost'] + 
        stats['total_material_cost'] + 
        stats['total_equipment_cost']
    )
    
    return stats

def validate_diary_entry_data(data):
    """Validate diary entry data before saving"""
    errors = []
    
    # Check required fields
    required_fields = ['project', 'entry_date', 'work_description']
    for field in required_fields:
        if not data.get(field):
            errors.append(f'{field} is required')
    
    # Validate percentage fields
    if data.get('progress_percentage'):
        if not (0 <= float(data['progress_percentage']) <= 100):
            errors.append('Progress percentage must be between 0 and 100')
    
    if data.get('humidity'):
        if not (0 <= int(data['humidity']) <= 100):
            errors.append('Humidity must be between 0 and 100')
    
    # Validate temperature range
    if data.get('temperature_high') and data.get('temperature_low'):
        if int(data['temperature_high']) < int(data['temperature_low']):
            errors.append('High temperature cannot be lower than low temperature')
    
    return errors

def generate_diary_report(project, start_date=None, end_date=None):
    """Generate a comprehensive diary report for a project"""
    entries = project.diary_entries.all()
    
    if start_date:
        entries = entries.filter(entry_date__gte=start_date)
    if end_date:
        entries = entries.filter(entry_date__lte=end_date)
    
    report = {
        'project': project,
        'period': {
            'start': start_date,
            'end': end_date,
        },
        'summary': {
            'total_entries': entries.count(),
            'work_days': entries.values('entry_date').distinct().count(),
            'weather_delays': entries.filter(
                delay_entries__category='weather'
            ).count(),
            'safety_incidents': entries.exclude(safety_incidents='').count(),
            'quality_issues': entries.exclude(quality_issues='').count(),
        },
        'progress': {
            'start_progress': entries.order_by('entry_date').first().progress_percentage if entries.exists() else 0,
            'end_progress': entries.order_by('-entry_date').first().progress_percentage if entries.exists() else 0,
        },
        'costs': get_project_statistics(project),
        'entries': entries.order_by('entry_date')
    }
    
    if report['progress']['start_progress'] and report['progress']['end_progress']:
        report['progress']['total_progress'] = (
            report['progress']['end_progress'] - report['progress']['start_progress']
        )
    
    return report

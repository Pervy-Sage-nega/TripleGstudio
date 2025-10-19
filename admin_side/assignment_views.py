from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from site_diary.models import Project
from .decorators import require_admin_role

@require_admin_role
def assign_project(request):
    """Assign site manager to project"""
    if request.method == 'POST':
        site_manager_id = request.POST.get('site_manager')
        project_id = request.POST.get('project')
        role = request.POST.get('role')
        
        try:
            site_manager = User.objects.get(id=site_manager_id)
            project = Project.objects.get(id=project_id)
            
            if role == 'project_manager':
                project.project_manager = site_manager
            elif role == 'architect':
                project.architect = site_manager
            
            project.save()
            messages.success(request, f'Successfully assigned {site_manager.get_full_name()} to {project.name}')
            
        except (User.DoesNotExist, Project.DoesNotExist):
            messages.error(request, 'Invalid user or project selected')
        
        return redirect('admin_side:assign_project')
    
    # Get site managers and projects
    site_managers = User.objects.filter(
        sitemanagerprofile__isnull=False,
        sitemanagerprofile__approval_status='approved'
    )
    projects = Project.objects.all()
    
    # Get current assignments
    current_assignments = []
    for project in projects:
        if project.project_manager:
            current_assignments.append({
                'id': f'pm_{project.id}',
                'project': project,
                'user': project.project_manager,
                'role': 'project_manager'
            })
        if project.architect:
            current_assignments.append({
                'id': f'arch_{project.id}',
                'project': project,
                'user': project.architect,
                'role': 'architect'
            })
    
    context = {
        'site_managers': site_managers,
        'projects': projects,
        'current_assignments': current_assignments
    }
    return render(request, 'assign_project.html', context)

@require_admin_role
def remove_assignment(request, assignment_id):
    """Remove site manager assignment from project"""
    try:
        role_type, project_id = assignment_id.split('_')
        project = Project.objects.get(id=project_id)
        
        if role_type == 'pm':
            project.project_manager = None
        elif role_type == 'arch':
            project.architect = None
        
        project.save()
        messages.success(request, 'Assignment removed successfully')
        
    except (Project.DoesNotExist, ValueError):
        messages.error(request, 'Invalid assignment')
    
    return redirect('admin_side:assign_project')
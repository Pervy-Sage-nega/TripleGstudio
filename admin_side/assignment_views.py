from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from site_diary.models import Project
from accounts.models import SitePersonnelRole
from .models import ProjectAssignment
from .decorators import require_admin_role
from django.http import JsonResponse
import json

@require_admin_role
def assign_project(request):
    """Assign multiple users to project"""
    if request.method == 'POST':
        if request.content_type == 'application/json':
            # Handle AJAX request for multiple assignments
            data = json.loads(request.body)
            project_id = data.get('project_id')
            assignments = data.get('assignments', [])
            
            try:
                project = Project.objects.get(id=project_id)
                success_count = 0
                
                for assignment in assignments:
                    user_id = assignment.get('user_id')
                    role = assignment.get('role')
                    
                    if user_id and role:
                        user = User.objects.get(id=user_id)
                        assignment_obj, created = ProjectAssignment.objects.get_or_create(
                            project=project,
                            user=user,
                            role=role,
                            defaults={'assigned_by': request.user}
                        )
                        if created:
                            success_count += 1
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully assigned {success_count} users to {project.name}'
                })
                
            except (User.DoesNotExist, Project.DoesNotExist) as e:
                return JsonResponse({'success': False, 'message': str(e)})
        else:
            # Handle single assignment form submission
            user_id = request.POST.get('user')
            project_id = request.POST.get('project')
            role = request.POST.get('role')
            
            try:
                user = User.objects.get(id=user_id)
                project = Project.objects.get(id=project_id)
                
                assignment, created = ProjectAssignment.objects.get_or_create(
                    project=project,
                    user=user,
                    role=role,
                    defaults={'assigned_by': request.user}
                )
                
                if created:
                    messages.success(request, f'Successfully assigned {user.get_full_name()} as {assignment.get_role_display()} to {project.name}')
                else:
                    messages.info(request, f'{user.get_full_name()} is already assigned as {assignment.get_role_display()} to {project.name}')
                
            except (User.DoesNotExist, Project.DoesNotExist):
                messages.error(request, 'Invalid user or project selected')
        
        return redirect('admin_side:assign_project')
    
    # Get site managers and projects
    site_managers = User.objects.filter(
        sitemanagerprofile__isnull=False,
        sitemanagerprofile__approval_status='approved'
    )
    projects = Project.objects.all()
    
    # Get current assignments using the new model
    current_assignments = ProjectAssignment.objects.filter(is_active=True).select_related('project', 'user')
    
    # Get site personnel roles from database
    personnel_roles = SitePersonnelRole.objects.filter(is_active=True).order_by('order')
    
    # Prepare data for JavaScript
    site_managers_json = [{
        'id': manager.id,
        'name': manager.get_full_name(),
        'username': manager.username
    } for manager in site_managers]
    
    role_choices_json = [{
        'value': role.name,
        'display': role.display_name
    } for role in personnel_roles]
    
    context = {
        'site_managers': site_managers,
        'projects': projects,
        'current_assignments': current_assignments,
        'personnel_roles': personnel_roles,
        'site_managers_json': site_managers_json,
        'role_choices_json': role_choices_json
    }
    return render(request, 'assign_project.html', context)

@require_admin_role
def remove_assignment(request, assignment_id):
    """Remove user assignment from project"""
    try:
        assignment = ProjectAssignment.objects.get(id=assignment_id)
        user_name = assignment.user.get_full_name()
        role = assignment.get_role_display()
        project_name = assignment.project.name
        
        assignment.delete()
        messages.success(request, f'Successfully removed {user_name} as {role} from {project_name}')
        
    except ProjectAssignment.DoesNotExist:
        messages.error(request, 'Assignment not found')
    
    return redirect('admin_side:assign_project')
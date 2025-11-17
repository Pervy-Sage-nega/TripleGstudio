from django.core.management.base import BaseCommand
from admin_side.models import ProjectAssignment
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check project assignments for debugging'
    
    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?', type=str, help='Username to check assignments for')

    def handle(self, *args, **options):
        self.stdout.write('=== PROJECT ASSIGNMENTS DEBUG ===')
        
        # Check all assignments
        assignments = ProjectAssignment.objects.all()
        self.stdout.write(f'Total assignments: {assignments.count()}')
        
        for assignment in assignments:
            self.stdout.write(f'- User: {assignment.user.username} ({assignment.user.get_full_name()})')
            self.stdout.write(f'  Project: {assignment.project.name}')
            self.stdout.write(f'  Role: {assignment.role}')
            self.stdout.write(f'  Active: {assignment.is_active}')
            self.stdout.write(f'  Assigned by: {assignment.assigned_by.username}')
            self.stdout.write('---')
        
        # Check specific user if provided
        username = options.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                user_assignments = ProjectAssignment.objects.filter(user=user, is_active=True)
                self.stdout.write(f'\nAssignments for {username}:')
                for assignment in user_assignments:
                    self.stdout.write(f'- {assignment.project.name} as {assignment.role}')
            except User.DoesNotExist:
                self.stdout.write(f'User {username} not found')
        
        # Also check projects that should be visible
        self.stdout.write('\n=== PROJECTS BY STATUS ===')
        from site_diary.models import Project
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])
        self.stdout.write(f'Total active projects: {projects.count()}')
        for project in projects:
            self.stdout.write(f'- {project.name} (ID: {project.id}, Status: {project.status})')
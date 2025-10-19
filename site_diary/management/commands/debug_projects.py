from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from site_diary.models import Project
from django.db.models import Q

class Command(BaseCommand):
    help = 'Debug project visibility issues'

    def handle(self, *args, **options):
        self.stdout.write('=== Project Debug Information ===')
        
        # Show all users
        self.stdout.write('\nAll Users:')
        for user in User.objects.all():
            self.stdout.write(f'- {user.username} (ID: {user.id}, Staff: {user.is_staff})')
        
        # Show all projects
        self.stdout.write('\nAll Projects:')
        for project in Project.objects.all():
            self.stdout.write(f'- {project.name} (Manager: {project.project_manager.username}, Status: {project.status})')
        
        # Test project visibility for each user
        self.stdout.write('\nProject Visibility by User:')
        for user in User.objects.all():
            if user.is_staff:
                projects = Project.objects.all()
            else:
                projects = Project.objects.filter(
                    Q(project_manager=user) | Q(architect=user)
                )
            
            self.stdout.write(f'\n{user.username} (Staff: {user.is_staff}):')
            self.stdout.write(f'  Can see {projects.count()} projects:')
            for project in projects:
                self.stdout.write(f'    - {project.name}')
        
        self.stdout.write('\n=== End Debug Information ===')

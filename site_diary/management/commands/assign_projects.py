from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from site_diary.models import Project

class Command(BaseCommand):
    help = 'Assign projects to a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to assign projects to')
        parser.add_argument('--make-staff', action='store_true', help='Make user a staff member')
        parser.add_argument('--assign-all', action='store_true', help='Assign all projects to user as manager')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" not found'))
            return
        
        self.stdout.write(f'Found user: {user.username} (Staff: {user.is_staff})')
        
        if options['make_staff']:
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Made {user.username} a staff user'))
        
        if options['assign_all']:
            projects = Project.objects.all()
            for project in projects:
                project.project_manager = user
                project.save()
            self.stdout.write(self.style.SUCCESS(f'Assigned {projects.count()} projects to {user.username} as manager'))
        
        # Show current project visibility
        if user.is_staff:
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(
                project_manager=user
            ) | Project.objects.filter(
                architect=user
            )
        
        self.stdout.write(f'\n{user.username} can now see {projects.count()} projects:')
        for project in projects:
            self.stdout.write(f'  - {project.name}')

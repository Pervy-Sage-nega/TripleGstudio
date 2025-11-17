from django.core.management.base import BaseCommand
from site_diary.models import Project

class Command(BaseCommand):
    help = 'Check all projects and their status'

    def handle(self, *args, **options):
        self.stdout.write('=== ALL PROJECTS ===')
        
        projects = Project.objects.all().order_by('id')
        self.stdout.write(f'Total projects: {projects.count()}')
        
        for project in projects:
            self.stdout.write(f'ID: {project.id} | Name: {project.name} | Status: {project.status} | Manager: {project.project_manager.username if project.project_manager else "None"}')
        
        self.stdout.write('\n=== PROJECTS BY STATUS ===')
        statuses = ['pending_approval', 'planning', 'active', 'on_hold', 'completed', 'cancelled', 'rejected']
        for status in statuses:
            count = Project.objects.filter(status=status).count()
            if count > 0:
                self.stdout.write(f'{status}: {count}')
                for project in Project.objects.filter(status=status):
                    self.stdout.write(f'  - {project.name} (ID: {project.id})')
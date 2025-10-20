from django.core.management.base import BaseCommand
from site_diary.models import Project

class Command(BaseCommand):
    help = 'Clean up duplicate test projects'

    def handle(self, *args, **options):
        # Remove duplicate test projects
        test_projects = Project.objects.filter(name='test-project')
        count = test_projects.count()
        test_projects.delete()
        
        # Remove test weather project
        weather_projects = Project.objects.filter(name='Test Weather Project')
        weather_count = weather_projects.count()
        weather_projects.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Removed {count} test projects and {weather_count} weather test projects')
        )
        
        # Show remaining projects
        remaining = Project.objects.all()
        self.stdout.write(
            self.style.SUCCESS(f'Remaining projects: {remaining.count()}')
        )
        for project in remaining:
            self.stdout.write(f'- {project.name} ({project.client_name})')
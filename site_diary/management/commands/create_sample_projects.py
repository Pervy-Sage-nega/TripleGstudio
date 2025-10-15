from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from site_diary.models import Project
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample projects for testing'

    def handle(self, *args, **options):
        # Get or create a user for the project manager
        user, created = User.objects.get_or_create(
            username='sitemanager',
            defaults={
                'email': 'sitemanager@example.com',
                'first_name': 'Site',
                'last_name': 'Manager',
                'is_staff': True
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f'Created user: {user.username}')
        
        # Create sample projects
        projects_data = [
            {
                'name': 'Riverside Commercial Complex',
                'description': 'A modern commercial complex with retail and office spaces',
                'client_name': 'Riverside Development Corp',
                'location': 'Downtown Riverside District',
                'budget': Decimal('2500000.00'),
                'status': 'active'
            },
            {
                'name': 'Green Valley Residential',
                'description': 'Sustainable residential development with 50 units',
                'client_name': 'Green Valley Holdings',
                'location': 'Green Valley Subdivision',
                'budget': Decimal('1800000.00'),
                'status': 'active'
            },
            {
                'name': 'Industrial Park Phase 1',
                'description': 'First phase of industrial park development',
                'client_name': 'Industrial Solutions Inc',
                'location': 'North Industrial Zone',
                'budget': Decimal('3200000.00'),
                'status': 'planning'
            }
        ]
        
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                name=project_data['name'],
                defaults={
                    'description': project_data['description'],
                    'client_name': project_data['client_name'],
                    'project_manager': user,
                    'location': project_data['location'],
                    'start_date': date.today(),
                    'expected_end_date': date.today() + timedelta(days=365),
                    'budget': project_data['budget'],
                    'status': project_data['status']
                }
            )
            
            if created:
                self.stdout.write(f'Created project: {project.name}')
            else:
                self.stdout.write(f'Project already exists: {project.name}')
        
        self.stdout.write(self.style.SUCCESS('Sample projects created successfully!'))
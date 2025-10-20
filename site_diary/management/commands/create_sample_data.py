from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date
from decimal import Decimal
from site_diary.models import Project

class Command(BaseCommand):
    help = 'Create sample data for dashboard and project detail'

    def add_arguments(self, parser):
        parser.add_argument('--user-email', type=str, help='Email of the user to create projects for')
        parser.add_argument('--clear-existing', action='store_true', help='Clear existing projects before creating new ones')

    def handle(self, *args, **options):
        user_email = options.get('user_email')
        
        if user_email:
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User with email {user_email} not found.'))
                return
        else:
            user = User.objects.filter(is_staff=True, is_active=True).order_by('-last_login').first()
            if not user:
                self.stdout.write(self.style.ERROR('No active staff user found. Please specify --user-email'))
                return

        self.stdout.write(f'Creating sample data for user: {user.email}')

        if options['clear_existing']:
            Project.objects.filter(project_manager=user).delete()
            self.stdout.write(self.style.WARNING('Cleared existing projects'))

        projects_data = [
            {
                'name': 'Metro Plaza Tower',
                'client_name': 'Metro Development Corp',
                'location': 'Central Business District, Manila',
                'status': 'active',
                'description': '42-story mixed-use tower with commercial and residential units. Premium office spaces and luxury condominiums.',
                'budget': Decimal('850000000.00'),
                'start_date': date(2024, 2, 1),
                'expected_end_date': date(2025, 8, 15),
                'architect': user
            },
            {
                'name': 'Seaside Resort Complex',
                'client_name': 'Coastal Properties Inc',
                'location': 'Boracay Island, Aklan',
                'status': 'active',
                'description': 'Luxury resort with 200 rooms, spa, conference facilities, and beachfront amenities.',
                'budget': Decimal('450000000.00'),
                'start_date': date(2024, 1, 15),
                'expected_end_date': date(2025, 6, 30),
                'architect': user
            },
            {
                'name': 'Green Valley Subdivision',
                'client_name': 'Valley Homes Development',
                'location': 'Antipolo, Rizal',
                'status': 'active',
                'description': 'Eco-friendly residential subdivision with 150 house units, parks, and community facilities.',
                'budget': Decimal('320000000.00'),
                'start_date': date(2024, 3, 1),
                'expected_end_date': date(2025, 12, 20),
                'architect': user
            },
            {
                'name': 'Industrial Park Phase 1',
                'client_name': 'Philippine Industrial Corp',
                'location': 'Laguna Technopark, Sta. Rosa',
                'status': 'planning',
                'description': 'Manufacturing facilities and warehouse complex with modern logistics infrastructure.',
                'budget': Decimal('680000000.00'),
                'start_date': date(2024, 6, 1),
                'expected_end_date': date(2026, 3, 15),
                'architect': user
            },
            {
                'name': 'Heritage Mall Renovation',
                'client_name': 'Heritage Properties',
                'location': 'Makati City',
                'status': 'completed',
                'description': 'Complete renovation of 5-story shopping mall with modern retail spaces and food court.',
                'budget': Decimal('180000000.00'),
                'start_date': date(2023, 8, 1),
                'expected_end_date': date(2024, 2, 28),
                'actual_end_date': date(2024, 2, 15),
                'architect': user
            },
            {
                'name': 'Riverside Bridge Construction',
                'client_name': 'Department of Public Works',
                'location': 'Marikina River, Metro Manila',
                'status': 'active',
                'description': 'Four-lane concrete bridge with pedestrian walkways and bike lanes.',
                'budget': Decimal('280000000.00'),
                'start_date': date(2024, 4, 1),
                'expected_end_date': date(2025, 10, 30),
                'architect': user
            }
        ]

        created_count = 0
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                name=project_data['name'],
                project_manager=user,
                defaults=project_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✓ Created project: {project.name}')

        self.stdout.write(self.style.SUCCESS(f'Sample data creation completed! Created {created_count} projects.'))
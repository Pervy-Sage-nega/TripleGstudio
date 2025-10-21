from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from site_diary.models import Project, DiaryEntry, Milestone
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create test diary entries for admindiaryreviewer'

    def handle(self, *args, **options):
        # Get or create test users
        user1, created = User.objects.get_or_create(
            username='testmanager1',
            defaults={
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'john@example.com'
            }
        )
        
        user2, created = User.objects.get_or_create(
            username='testmanager2',
            defaults={
                'first_name': 'Emily',
                'last_name': 'Rodriguez',
                'email': 'emily@example.com'
            }
        )

        # Get or create test projects
        project1, created = Project.objects.get_or_create(
            name='Central Business District Tower',
            defaults={
                'client_name': 'ABC Corporation',
                'project_manager': user1,
                'location': 'Manila, Philippines',
                'start_date': date.today() - timedelta(days=30),
                'expected_end_date': date.today() + timedelta(days=180),
                'budget': Decimal('5000000.00'),
                'status': 'active'
            }
        )

        project2, created = Project.objects.get_or_create(
            name='Tech Innovation Campus',
            defaults={
                'client_name': 'Tech Corp',
                'project_manager': user2,
                'location': 'Quezon City, Philippines',
                'start_date': date.today() - timedelta(days=45),
                'expected_end_date': date.today() + timedelta(days=200),
                'budget': Decimal('8000000.00'),
                'status': 'active'
            }
        )

        # Get or create milestones
        milestone1, created = Milestone.objects.get_or_create(
            name='Structural Framework',
            defaults={'order': 2, 'description': 'Building structural framework'}
        )
        
        milestone2, created = Milestone.objects.get_or_create(
            name='Exterior Facade',
            defaults={'order': 3, 'description': 'Exterior facade work'}
        )

        # Create test diary entries
        entries_data = [
            {
                'project': project1,
                'created_by': user1,
                'entry_date': date.today() - timedelta(days=2),
                'work_description': 'Continued concrete pouring for foundation',
                'progress_percentage': Decimal('35.5'),
                'milestone': milestone1,
                'approved': False,
                'weather_condition': 'sunny'
            },
            {
                'project': project2,
                'created_by': user2,
                'entry_date': date.today() - timedelta(days=1),
                'work_description': 'Steel frame installation on 3rd floor',
                'progress_percentage': Decimal('42.0'),
                'milestone': milestone2,
                'approved': True,
                'weather_condition': 'cloudy'
            },
            {
                'project': project1,
                'created_by': user1,
                'entry_date': date.today(),
                'work_description': 'Electrical wiring installation',
                'progress_percentage': Decimal('38.0'),
                'milestone': milestone1,
                'approved': False,
                'weather_condition': 'rainy'
            }
        ]

        for entry_data in entries_data:
            DiaryEntry.objects.get_or_create(
                project=entry_data['project'],
                entry_date=entry_data['entry_date'],
                defaults=entry_data
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully created test diary entries')
        )
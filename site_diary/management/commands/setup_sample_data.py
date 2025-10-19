from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from site_diary.models import (
    Project, DiaryEntry, LaborEntry, MaterialEntry, 
    EquipmentEntry, DelayEntry, VisitorEntry, DiaryPhoto
)

class Command(BaseCommand):
    help = 'Set up sample data for site diary testing'

    def handle(self, *args, **options):
        self.stdout.write('Setting up sample data for site diary...')
        
        # Create sample users if they don't exist
        self.create_sample_users()
        
        # Create sample projects
        self.create_sample_projects()
        
        # Create sample diary entries
        self.create_sample_diary_entries()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def create_sample_users(self):
        """Create sample users for testing"""
        users_data = [
            {
                'username': 'site_manager',
                'email': 'sitemanager@tripleg.com',
                'first_name': 'John',
                'last_name': 'Manager',
                'is_staff': True,
            },
            {
                'username': 'architect_user',
                'email': 'architect@tripleg.com',
                'first_name': 'Sarah',
                'last_name': 'Architect',
                'is_staff': False,
            },
            {
                'username': 'project_manager',
                'email': 'pm@tripleg.com',
                'first_name': 'Mike',
                'last_name': 'ProjectManager',
                'is_staff': True,
            }
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults=user_data
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f'Created user: {user.username}')
            else:
                self.stdout.write(f'User already exists: {user.username}')

    def create_sample_projects(self):
        """Create sample projects"""
        projects_data = [
            {
                'name': 'River View Residences',
                'description': 'Luxury residential complex with river views',
                'client_name': 'River View Development Corp',
                'location': 'Manila, Philippines',
                'start_date': date(2024, 1, 15),
                'expected_end_date': date(2024, 12, 31),
                'budget': Decimal('50000000.00'),
                'status': 'active',
            },
            {
                'name': 'Central Business District Tower',
                'description': 'Commercial office tower in CBD',
                'client_name': 'CBD Properties Inc',
                'location': 'Makati, Philippines',
                'start_date': date(2024, 3, 1),
                'expected_end_date': date(2025, 6, 30),
                'budget': Decimal('75000000.00'),
                'status': 'active',
            },
            {
                'name': 'Highway Bridge Expansion',
                'description': 'Bridge expansion project for traffic relief',
                'client_name': 'Department of Public Works',
                'location': 'Quezon City, Philippines',
                'start_date': date(2023, 10, 1),
                'expected_end_date': date(2024, 8, 31),
                'budget': Decimal('30000000.00'),
                'status': 'active',
            }
        ]
        
        # Get users for project assignment
        site_manager = User.objects.get(username='site_manager')
        architect = User.objects.get(username='architect_user')
        project_manager = User.objects.get(username='project_manager')
        
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                name=project_data['name'],
                defaults={
                    **project_data,
                    'project_manager': project_manager,
                    'architect': architect,
                }
            )
            if created:
                self.stdout.write(f'Created project: {project.name}')
            else:
                self.stdout.write(f'Project already exists: {project.name}')

    def create_sample_diary_entries(self):
        """Create sample diary entries with related data"""
        # Get projects and users
        river_view = Project.objects.get(name='River View Residences')
        cbd_tower = Project.objects.get(name='Central Business District Tower')
        site_manager = User.objects.get(username='site_manager')
        
        # Create diary entries for the last 7 days
        for i in range(7):
            entry_date = date.today() - timedelta(days=i)
            
            # Create diary entry
            diary_entry = DiaryEntry.objects.create(
                project=river_view if i % 2 == 0 else cbd_tower,
                entry_date=entry_date,
                created_by=site_manager,
                weather_condition='sunny' if i % 3 == 0 else 'cloudy',
                temperature_high=32 + (i % 5),
                temperature_low=25 + (i % 3),
                humidity=60 + (i % 20),
                wind_speed=Decimal('5.5') + Decimal(str(i % 3)),
                work_description=f'Work performed on day {i+1}: Foundation work, concrete pouring, and site preparation.',
                progress_percentage=Decimal('15.0') + Decimal(str(i * 2)),
                quality_issues='' if i % 4 != 0 else 'Minor concrete cracking observed in section B',
                safety_incidents='' if i % 5 != 0 else 'Near miss incident with crane operation',
                general_notes=f'General notes for day {i+1}. Site conditions were good.',
                photos_taken=i % 2 == 0,
                draft=False,
                approved=True,
            )
            
            # Create labor entries
            LaborEntry.objects.create(
                diary_entry=diary_entry,
                labor_type='skilled',
                trade_description='Concrete Workers',
                workers_count=8,
                hours_worked=Decimal('8.0'),
                hourly_rate=Decimal('15.00'),
                overtime_hours=Decimal('2.0'),
                work_area='Foundation Area',
                notes='Worked on foundation concrete pouring'
            )
            
            LaborEntry.objects.create(
                diary_entry=diary_entry,
                labor_type='supervisor',
                trade_description='Site Supervisor',
                workers_count=2,
                hours_worked=Decimal('8.0'),
                hourly_rate=Decimal('25.00'),
                overtime_hours=Decimal('0.0'),
                work_area='Entire Site',
                notes='Supervised all activities'
            )
            
            # Create material entries
            MaterialEntry.objects.create(
                diary_entry=diary_entry,
                material_name='Ready-mix Concrete',
                quantity_delivered=Decimal('15.0'),
                quantity_used=Decimal('12.0'),
                unit='m3',
                unit_cost=Decimal('4500.00'),
                supplier='ABC Concrete Supply',
                quality_check=True,
                storage_location='Site Storage Area',
                notes='Good quality concrete delivered on time'
            )
            
            # Create equipment entries
            EquipmentEntry.objects.create(
                diary_entry=diary_entry,
                equipment_name='Excavator CAT 320',
                equipment_type='Excavator',
                operator_name='Juan Dela Cruz',
                hours_operated=Decimal('6.0'),
                fuel_consumption=Decimal('45.0'),
                status='operational',
                rental_cost_per_hour=Decimal('800.00'),
                work_area='Foundation Area',
            )
            
            # Create delay entries (occasionally)
            if i % 3 == 0:
                DelayEntry.objects.create(
                    diary_entry=diary_entry,
                    category='weather',
                    description='Heavy rain caused work stoppage',
                    duration_hours=Decimal('2.0'),
                    impact_level='medium',
                    affected_activities='Concrete pouring and excavation work',
                    mitigation_actions='Workers sheltered in site office, resumed work after rain stopped',
                    responsible_party='Weather conditions',
                    cost_impact=Decimal('5000.00')
                )
            
            # Create visitor entries (occasionally)
            if i % 4 == 0:
                VisitorEntry.objects.create(
                    diary_entry=diary_entry,
                    visitor_name='Maria Santos',
                    company='Quality Assurance Inc',
                    visitor_type='inspector',
                    arrival_time='09:00',
                    departure_time='11:30',
                    purpose_of_visit='Quality inspection of foundation work',
                    areas_visited='Foundation Area, Storage Area',
                    accompanied_by='Site Supervisor',
                    notes='Inspection passed with minor recommendations'
                )
            
            self.stdout.write(f'Created diary entry for {entry_date}')
        
        self.stdout.write('Sample data creation completed!')
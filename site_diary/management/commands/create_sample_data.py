from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random
from site_diary.models import (
    Project, DiaryEntry, LaborEntry, MaterialEntry, 
    EquipmentEntry, DelayEntry, VisitorEntry
)

class Command(BaseCommand):
    help = 'Create comprehensive sample data for the logged-in user account'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Email of the user to create projects for',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing projects before creating new ones',
        )

    def handle(self, *args, **options):
        # Get user - either from argument or find active staff user
        user_email = options.get('user_email')
        
        if user_email:
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with email {user_email} not found.')
                )
                return
        else:
            # Find the most recently active staff user
            user = User.objects.filter(is_staff=True, is_active=True).order_by('-last_login').first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('No active staff user found. Please specify --user-email')
                )
                return

        self.stdout.write(f'Creating sample data for user: {user.email}')

        # Clear existing data if requested
        if options['clear_existing']:
            Project.objects.filter(project_manager=user).delete()
            self.stdout.write(self.style.WARNING('Cleared existing projects'))

        # Create sample projects
        self.create_projects(user)
        
        # Create diary entries for projects
        self.create_diary_entries(user)
        
        self.stdout.write(
            self.style.SUCCESS('Sample data creation completed successfully!')
        )

    def create_projects(self, user):
        """Create sample projects for the user"""
        projects_data = [
            {
                'name': 'Metro Plaza Tower',
                'client_name': 'Metro Development Corp',
                'location': 'Central Business District, Manila',
                'status': 'active',
                'description': '42-story mixed-use tower with commercial and residential units. Features premium office spaces, luxury condominiums, and retail establishments.',
                'budget': Decimal('850000000.00'),
                'start_date': date(2024, 2, 1),
                'expected_end_date': date(2025, 8, 15),
                'architect': user,
                'category': 'commercial',
                'current_phase': 'Structural Framework - Floor 15 construction in progress',
                'progress': 35,
                'budget_used': 42,
                'schedule_status': 'On Track',
                'size': '85,000 sqm'
            },
            {
                'name': 'Seaside Resort Complex',
                'client_name': 'Coastal Properties Inc',
                'location': 'Boracay Island, Aklan',
                'status': 'active',
                'description': 'Luxury resort with 200 rooms, spa, conference facilities, and beachfront amenities. Eco-friendly design with sustainable materials.',
                'budget': Decimal('450000000.00'),
                'start_date': date(2024, 1, 15),
                'expected_end_date': date(2025, 6, 30),
                'architect': user,
                'category': 'commercial',
                'current_phase': 'Interior & Exterior Finishing - Guest rooms and common areas',
                'progress': 68,
                'budget_used': 58,
                'schedule_status': 'On Track',
                'size': '45,000 sqm'
            },
            {
                'name': 'Green Valley Subdivision',
                'client_name': 'Valley Homes Development',
                'location': 'Antipolo, Rizal',
                'status': 'active',
                'description': 'Eco-friendly residential subdivision with 150 house units, parks, and community facilities. Solar-powered streetlights and rainwater harvesting.',
                'budget': Decimal('320000000.00'),
                'start_date': date(2024, 3, 1),
                'expected_end_date': date(2025, 12, 20),
                'architect': user,
                'category': 'residential',
                'current_phase': 'Foundation Work - Phase 2 housing units',
                'progress': 28,
                'budget_used': 31,
                'schedule_status': 'Minor Delays',
                'size': '25 hectares'
            },
            {
                'name': 'Industrial Park Phase 1',
                'client_name': 'Philippine Industrial Corp',
                'location': 'Laguna Technopark, Sta. Rosa',
                'status': 'planning',
                'description': 'Manufacturing facilities and warehouse complex with modern logistics infrastructure. Green building certified design.',
                'budget': Decimal('680000000.00'),
                'start_date': date(2024, 6, 1),
                'expected_end_date': date(2026, 3, 15),
                'architect': user,
                'category': 'industrial',
                'current_phase': 'Planning & Design - Permit applications in progress',
                'progress': 15,
                'budget_used': 8,
                'schedule_status': 'On Track',
                'size': '120,000 sqm'
            },
            {
                'name': 'Heritage Mall Renovation',
                'client_name': 'Heritage Properties',
                'location': 'Makati City',
                'status': 'completed',
                'description': 'Complete renovation of 5-story shopping mall with modern retail spaces, food court, and entertainment facilities.',
                'budget': Decimal('180000000.00'),
                'start_date': date(2023, 8, 1),
                'expected_end_date': date(2024, 2, 28),
                'actual_end_date': date(2024, 2, 15),
                'architect': user,
                'category': 'commercial',
                'current_phase': 'Project Completion - Handover completed',
                'progress': 100,
                'budget_used': 96,
                'schedule_status': 'Completed Early',
                'size': '32,000 sqm'
            },
            {
                'name': 'Riverside Bridge Construction',
                'client_name': 'Department of Public Works',
                'location': 'Marikina River, Metro Manila',
                'status': 'active',
                'description': 'Four-lane concrete bridge with pedestrian walkways and bike lanes. Seismic-resistant design with modern lighting.',
                'budget': Decimal('280000000.00'),
                'start_date': date(2024, 4, 1),
                'expected_end_date': date(2025, 10, 30),
                'architect': user,
                'category': 'infrastructure',
                'current_phase': 'Foundation Work - Pier construction ongoing',
                'progress': 22,
                'budget_used': 18,
                'schedule_status': 'On Track',
                'size': '450 meters'
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
            else:
                self.stdout.write(f'- Project already exists: {project.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Projects created: {created_count}')
        )

    def create_diary_entries(self, user):
        """Create sample diary entries for active projects"""
        active_projects = Project.objects.filter(
            project_manager=user, 
            status__in=['active', 'planning']
        )
        
        if not active_projects.exists():
            self.stdout.write(self.style.WARNING('No active projects found for diary entries'))
            return

        entry_count = 0
        
        # Create entries for the last 30 days
        for i in range(30):
            entry_date = date.today() - timedelta(days=i)
            
            # Skip weekends for some realism
            if entry_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue
                
            # Create entries for random projects (not all projects every day)
            selected_projects = random.sample(
                list(active_projects), 
                min(random.randint(1, 3), len(active_projects))
            )
            
            for project in selected_projects:
                # Skip if entry already exists
                if DiaryEntry.objects.filter(project=project, entry_date=entry_date).exists():
                    continue
                    
                diary_entry = self.create_single_diary_entry(project, entry_date, user)
                if diary_entry:
                    entry_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Diary entries created: {entry_count}')
        )

    def create_single_diary_entry(self, project, entry_date, user):
        """Create a single diary entry with related data"""
        weather_conditions = ['sunny', 'cloudy', 'rainy', 'windy']
        
        diary_entry = DiaryEntry.objects.create(
            project=project,
            entry_date=entry_date,
            created_by=user,
            weather_condition=random.choice(weather_conditions),
            temperature_high=random.randint(24, 35),
            temperature_low=random.randint(18, 28),
            humidity=random.randint(45, 85),
            wind_speed=Decimal(str(random.uniform(5, 25))),
            work_description=self.get_random_work_description(),
            progress_percentage=Decimal(str(random.uniform(0, 100))),
            general_notes=self.get_random_notes(),
            photos_taken=random.choice([True, False])
        )

        # Add labor entries
        self.create_labor_entries(diary_entry)
        
        # Add material entries
        self.create_material_entries(diary_entry)
        
        # Add equipment entries
        self.create_equipment_entries(diary_entry)
        
        # Occasionally add delays
        if random.random() < 0.3:  # 30% chance of delays
            self.create_delay_entries(diary_entry)
            
        # Occasionally add visitors
        if random.random() < 0.2:  # 20% chance of visitors
            self.create_visitor_entries(diary_entry)

        return diary_entry

    def create_labor_entries(self, diary_entry):
        """Create labor entries for a diary entry"""
        labor_types = [
            ('skilled', 'Carpenter', 15),
            ('skilled', 'Electrician', 8),
            ('skilled', 'Plumber', 6),
            ('unskilled', 'General Labor', 25),
            ('supervisor', 'Site Supervisor', 2),
            ('engineer', 'Site Engineer', 1)
        ]
        
        selected_labor = random.sample(labor_types, random.randint(2, 4))
        
        for labor_type, trade, base_count in selected_labor:
            LaborEntry.objects.create(
                diary_entry=diary_entry,
                labor_type=labor_type,
                trade_description=trade,
                workers_count=random.randint(1, base_count),
                hours_worked=Decimal(str(random.uniform(6, 10))),
                hourly_rate=Decimal(str(random.uniform(300, 800))),
                overtime_hours=Decimal(str(random.uniform(0, 3))),
                work_area=random.choice(['Foundation', 'Structure', 'Finishing', 'MEP'])
            )

    def create_material_entries(self, diary_entry):
        """Create material entries for a diary entry"""
        materials = [
            ('Concrete', 'm3', 15, 4500),
            ('Steel Rebar', 'kg', 2500, 45),
            ('Cement', 'bags', 150, 280),
            ('Sand', 'm3', 8, 1200),
            ('Gravel', 'm3', 12, 1500),
            ('Hollow Blocks', 'pcs', 500, 12)
        ]
        
        selected_materials = random.sample(materials, random.randint(2, 4))
        
        for material_name, unit, base_qty, unit_cost in selected_materials:
            quantity = random.randint(1, base_qty)
            MaterialEntry.objects.create(
                diary_entry=diary_entry,
                material_name=material_name,
                quantity_delivered=Decimal(str(quantity)),
                quantity_used=Decimal(str(random.randint(0, quantity))),
                unit=unit,
                unit_cost=Decimal(str(unit_cost)),
                supplier=f'{material_name} Suppliers Inc.',
                quality_check=True
            )

    def create_equipment_entries(self, diary_entry):
        """Create equipment entries for a diary entry"""
        equipment_list = [
            ('Excavator CAT 320', 'Excavator', 2500),
            ('Tower Crane', 'Crane', 8000),
            ('Concrete Mixer', 'Mixer', 1200),
            ('Dump Truck', 'Truck', 3500),
            ('Bulldozer', 'Bulldozer', 4000)
        ]
        
        selected_equipment = random.sample(equipment_list, random.randint(1, 3))
        
        for equipment_name, equipment_type, rental_cost in selected_equipment:
            EquipmentEntry.objects.create(
                diary_entry=diary_entry,
                equipment_name=equipment_name,
                equipment_type=equipment_type,
                operator_name=f'Operator {random.randint(1, 20)}',
                hours_operated=Decimal(str(random.uniform(4, 10))),
                fuel_consumption=Decimal(str(random.uniform(20, 80))),
                status='operational',
                rental_cost_per_hour=Decimal(str(rental_cost))
            )

    def create_delay_entries(self, diary_entry):
        """Create delay entries for a diary entry"""
        delay_categories = ['weather', 'material', 'equipment', 'labor']
        
        DelayEntry.objects.create(
            diary_entry=diary_entry,
            category=random.choice(delay_categories),
            description=self.get_random_delay_description(),
            duration_hours=Decimal(str(random.uniform(0.5, 4))),
            impact_level=random.choice(['low', 'medium', 'high']),
            affected_activities='Construction activities affected by delay',
            mitigation_actions='Implemented alternative work schedule'
        )

    def create_visitor_entries(self, diary_entry):
        """Create visitor entries for a diary entry"""
        visitor_types = ['client', 'inspector', 'consultant', 'supplier']
        
        VisitorEntry.objects.create(
            diary_entry=diary_entry,
            visitor_name=f'Visitor {random.randint(1, 100)}',
            company=f'Company {random.randint(1, 50)} Inc.',
            visitor_type=random.choice(visitor_types),
            arrival_time=timezone.now().time(),
            purpose_of_visit='Site inspection and progress review',
            areas_visited='Construction site and office'
        )

    def get_random_work_description(self):
        """Generate random work description"""
        descriptions = [
            "Continued concrete pouring for foundation work. Completed rebar installation for columns.",
            "Structural steel installation progressed on schedule. Quality inspections passed.",
            "Electrical rough-in work completed on floors 1-3. Plumbing installation ongoing.",
            "Exterior wall construction advanced. Window installation began on lower floors.",
            "Interior finishing work started. Painting and tiling in progress.",
            "MEP systems installation continued. Fire safety systems testing completed."
        ]
        return random.choice(descriptions)

    def get_random_notes(self):
        """Generate random general notes"""
        notes = [
            "Weather conditions favorable for construction activities.",
            "All safety protocols followed. No incidents reported.",
            "Material deliveries on schedule. Quality checks passed.",
            "Good progress made today. Team coordination excellent.",
            "Minor adjustments made to work schedule due to weather.",
            "Client visit scheduled for tomorrow. Site preparation ongoing."
        ]
        return random.choice(notes)

    def get_random_delay_description(self):
        """Generate random delay description"""
        descriptions = [
            "Material delivery delayed due to traffic conditions.",
            "Equipment breakdown required immediate maintenance.",
            "Weather conditions prevented outdoor work activities.",
            "Waiting for client approval on design changes.",
            "Labor shortage due to holiday season.",
            "Permit approval process taking longer than expected."
        ]
        return random.choice(descriptions)bor_type=labor_type,
                trade_description=trade,
                workers_count=random.randint(1, base_count),
                hours_worked=Decimal(str(random.uniform(6, 10))),
                hourly_rate=Decimal(str(random.uniform(300, 800))),
                overtime_hours=Decimal(str(random.uniform(0, 3))),
                work_area=random.choice(['Foundation', 'Structure', 'Finishing', 'MEP'])
            )

    def create_material_entries(self, diary_entry):
        """Create material entries for a diary entry"""
        materials = [
            ('Concrete', 'm3', 15, 4500),
            ('Steel Rebar', 'kg', 2500, 45),
            ('Cement', 'bags', 150, 280),
            ('Sand', 'm3', 8, 1200),
            ('Gravel', 'm3', 12, 1500),
            ('Hollow Blocks', 'pcs', 500, 12)
        ]
        
        selected_materials = random.sample(materials, random.randint(2, 4))
        
        for material_name, unit, base_qty, unit_cost in selected_materials:
            quantity = random.randint(1, base_qty)
            MaterialEntry.objects.create(
                diary_entry=diary_entry,
                material_name=material_name,
                quantity_delivered=Decimal(str(quantity)),
                quantity_used=Decimal(str(random.randint(0, quantity))),
                unit=unit,
                unit_cost=Decimal(str(unit_cost)),
                supplier=f'{material_name} Suppliers Inc.',
                quality_check=True
            )

    def create_equipment_entries(self, diary_entry):
        """Create equipment entries for a diary entry"""
        equipment_list = [
            ('Excavator CAT 320', 'Excavator', 2500),
            ('Tower Crane', 'Crane', 8000),
            ('Concrete Mixer', 'Mixer', 1200),
            ('Dump Truck', 'Truck', 3500),
            ('Bulldozer', 'Bulldozer', 4000)
        ]
        
        selected_equipment = random.sample(equipment_list, random.randint(1, 3))
        
        for equipment_name, equipment_type, rental_cost in selected_equipment:
            EquipmentEntry.objects.create(
                diary_entry=diary_entry,
                equipment_name=equipment_name,
                equipment_type=equipment_type,
                operator_name=f'Operator {random.randint(1, 20)}',
                hours_operated=Decimal(str(random.uniform(4, 10))),
                fuel_consumption=Decimal(str(random.uniform(20, 80))),
                status='operational',
                rental_cost_per_hour=Decimal(str(rental_cost))
            )

    def create_delay_entries(self, diary_entry):
        """Create delay entries for a diary entry"""
        delay_categories = ['weather', 'material', 'equipment', 'labor']
        
        DelayEntry.objects.create(
            diary_entry=diary_entry,
            category=random.choice(delay_categories),
            description=self.get_random_delay_description(),
            duration_hours=Decimal(str(random.uniform(0.5, 4))),
            impact_level=random.choice(['low', 'medium', 'high']),
            affected_activities='Construction activities affected by delay',
            mitigation_actions='Implemented alternative work schedule'
        )

    def create_visitor_entries(self, diary_entry):
        """Create visitor entries for a diary entry"""
        visitor_types = ['client', 'inspector', 'consultant', 'supplier']
        
        VisitorEntry.objects.create(
            diary_entry=diary_entry,
            visitor_name=f'Visitor {random.randint(1, 100)}',
            company=f'Company {random.randint(1, 50)} Inc.',
            visitor_type=random.choice(visitor_types),
            arrival_time=timezone.now().time(),
            purpose_of_visit='Site inspection and progress review',
            areas_visited='Construction site and office'
        )

    def get_random_work_description(self):
        """Generate random work description"""
        descriptions = [
            "Continued concrete pouring for foundation work. Completed rebar installation for columns.",
            "Structural steel installation progressed on schedule. Quality inspections passed.",
            "Electrical rough-in work completed on floors 1-3. Plumbing installation ongoing.",
            "Exterior wall construction advanced. Window installation began on lower floors.",
            "Interior finishing work started. Painting and tiling in progress.",
            "MEP systems installation continued. Fire safety systems testing completed."
        ]
        return random.choice(descriptions)

    def get_random_notes(self):
        """Generate random general notes"""
        notes = [
            "Weather conditions favorable for construction activities.",
            "All safety protocols followed. No incidents reported.",
            "Material deliveries on schedule. Quality checks passed.",
            "Good progress made today. Team coordination excellent.",
            "Minor adjustments made to work schedule due to weather.",
            "Client visit scheduled for tomorrow. Site preparation ongoing."
        ]
        return random.choice(notes)

    def get_random_delay_description(self):
        """Generate random delay description"""
        descriptions = [
            "Material delivery delayed due to traffic conditions.",
            "Equipment breakdown required immediate maintenance.",
            "Weather conditions prevented outdoor work activities.",
            "Waiting for client approval on design changes.",
            "Labor shortage due to holiday season.",
            "Permit approval process taking longer than expected."
        ]
        return random.choice(descriptions)
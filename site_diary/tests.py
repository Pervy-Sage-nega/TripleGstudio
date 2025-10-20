from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    Project, DiaryEntry, LaborEntry, MaterialEntry, 
    EquipmentEntry, DelayEntry, VisitorEntry, DiaryPhoto
)
from .utils import (
    get_user_projects, get_project_statistics, 
    validate_diary_entry_data, generate_diary_report
)


class UtilsTestCase(TestCase):
    """Test cases for utility functions in utils.py"""
    
    def setUp(self):
        """Set up test data"""
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.project_manager = User.objects.create_user(
            username='pm_test',
            email='pm@test.com',
            password='testpass123',
            is_staff=True
        )
        
        self.architect = User.objects.create_user(
            username='arch_test',
            email='arch@test.com',
            password='testpass123',
            is_staff=False
        )
        
        self.regular_user = User.objects.create_user(
            username='user_test',
            email='user@test.com',
            password='testpass123',
            is_staff=False
        )
        
        # Create test projects
        self.project1 = Project.objects.create(
            name='Test Project 1',
            description='First test project',
            client_name='Test Client 1',
            project_manager=self.project_manager,
            architect=self.architect,
            location='Test Location 1',
            start_date=date.today() - timedelta(days=30),
            expected_end_date=date.today() + timedelta(days=300),
            budget=Decimal('1000000.00'),
            status='active'
        )
        
        self.project2 = Project.objects.create(
            name='Test Project 2',
            description='Second test project',
            client_name='Test Client 2',
            project_manager=self.project_manager,
            location='Test Location 2',
            start_date=date.today() - timedelta(days=15),
            expected_end_date=date.today() + timedelta(days=200),
            budget=Decimal('500000.00'),
            status='planning'
        )
        
        # Create test diary entries
        self.diary_entry1 = DiaryEntry.objects.create(
            project=self.project1,
            entry_date=date.today() - timedelta(days=1),
            created_by=self.project_manager,
            weather_condition='sunny',
            temperature_high=25,
            temperature_low=15,
            humidity=60,
            wind_speed=Decimal('10.5'),
            work_description='Foundation work completed',
            progress_percentage=Decimal('25.50'),
            approved=True
        )
        
        self.diary_entry2 = DiaryEntry.objects.create(
            project=self.project1,
            entry_date=date.today(),
            created_by=self.architect,
            weather_condition='cloudy',
            temperature_high=22,
            temperature_low=12,
            work_description='Structural work in progress',
            progress_percentage=Decimal('30.00'),
            approved=False
        )
        
        # Create related entries for testing statistics
        self.labor_entry = LaborEntry.objects.create(
            diary_entry=self.diary_entry1,
            labor_type='skilled',
            trade_description='Concrete Workers',
            workers_count=5,
            hours_worked=Decimal('8.0'),
            hourly_rate=Decimal('25.00'),
            overtime_hours=Decimal('2.0')
        )
        
        self.material_entry = MaterialEntry.objects.create(
            diary_entry=self.diary_entry1,
            material_name='Concrete',
            quantity_delivered=Decimal('10.0'),
            quantity_used=Decimal('8.0'),
            unit='m3',
            unit_cost=Decimal('100.00')
        )
        
        self.equipment_entry = EquipmentEntry.objects.create(
            diary_entry=self.diary_entry1,
            equipment_name='Excavator',
            equipment_type='Heavy Machinery',
            hours_operated=Decimal('6.0'),
            rental_cost_per_hour=Decimal('50.00')
        )
        
        self.delay_entry = DelayEntry.objects.create(
            diary_entry=self.diary_entry1,
            category='weather',
            description='Rain delay',
            duration_hours=Decimal('3.0'),
            impact_level='medium'
        )

    def test_get_user_projects_admin(self):
        """Test get_user_projects for admin user"""
        projects = get_user_projects(self.admin_user)
        self.assertEqual(projects.count(), 2)
        self.assertIn(self.project1, projects)
        self.assertIn(self.project2, projects)

    def test_get_user_projects_project_manager(self):
        """Test get_user_projects for project manager"""
        projects = get_user_projects(self.project_manager)
        self.assertEqual(projects.count(), 2)
        self.assertIn(self.project1, projects)
        self.assertIn(self.project2, projects)

    def test_get_user_projects_architect(self):
        """Test get_user_projects for architect"""
        projects = get_user_projects(self.architect)
        self.assertEqual(projects.count(), 1)
        self.assertIn(self.project1, projects)
        self.assertNotIn(self.project2, projects)

    def test_get_user_projects_regular_user(self):
        """Test get_user_projects for regular user with no assignments"""
        projects = get_user_projects(self.regular_user)
        self.assertEqual(projects.count(), 0)

    def test_get_project_statistics_basic(self):
        """Test basic project statistics calculation"""
        stats = get_project_statistics(self.project1)
        
        # Check basic counts
        self.assertEqual(stats['total_entries'], 2)
        self.assertEqual(stats['approved_entries'], 1)
        self.assertEqual(stats['pending_entries'], 1)
        
        # Check average progress
        expected_avg = (Decimal('25.50') + Decimal('30.00')) / 2
        self.assertEqual(stats['avg_progress'], expected_avg)

    def test_get_project_statistics_costs(self):
        """Test cost calculations in project statistics"""
        stats = get_project_statistics(self.project1)
        
        # Labor cost: (8 * 25 * 5) + (2 * 25 * 1.5 * 5) = 1000 + 375 = 1375
        expected_labor_cost = Decimal('1375.00')
        self.assertEqual(stats['total_labor_cost'], expected_labor_cost)
        
        # Material cost: 10 * 100 = 1000
        expected_material_cost = Decimal('1000.00')
        self.assertEqual(stats['total_material_cost'], expected_material_cost)
        
        # Equipment cost: 6 * 50 = 300
        expected_equipment_cost = Decimal('300.00')
        self.assertEqual(stats['total_equipment_cost'], expected_equipment_cost)
        
        # Total project cost
        expected_total = expected_labor_cost + expected_material_cost + expected_equipment_cost
        self.assertEqual(stats['total_project_cost'], expected_total)

    def test_get_project_statistics_delays(self):
        """Test delay calculations in project statistics"""
        stats = get_project_statistics(self.project1)
        self.assertEqual(stats['total_delay_hours'], Decimal('3.0'))

    def test_get_project_statistics_weather(self):
        """Test weather breakdown in project statistics"""
        stats = get_project_statistics(self.project1)
        expected_weather = {'sunny': 1, 'cloudy': 1}
        self.assertEqual(stats['weather_breakdown'], expected_weather)

    def test_get_project_statistics_empty_project(self):
        """Test project statistics for project with no entries"""
        stats = get_project_statistics(self.project2)
        
        self.assertEqual(stats['total_entries'], 0)
        self.assertEqual(stats['approved_entries'], 0)
        self.assertEqual(stats['pending_entries'], 0)
        self.assertEqual(stats['avg_progress'], 0)
        self.assertEqual(stats['total_labor_cost'], 0)
        self.assertEqual(stats['total_material_cost'], 0)
        self.assertEqual(stats['total_equipment_cost'], 0)
        self.assertEqual(stats['total_delay_hours'], 0)
        self.assertEqual(stats['weather_breakdown'], {})

    def test_validate_diary_entry_data_valid(self):
        """Test validation with valid diary entry data"""
        valid_data = {
            'project': self.project1,
            'entry_date': date.today(),
            'work_description': 'Valid work description',
            'progress_percentage': '50.0',
            'humidity': '70',
            'temperature_high': '25',
            'temperature_low': '15'
        }
        
        errors = validate_diary_entry_data(valid_data)
        self.assertEqual(len(errors), 0)

    def test_validate_diary_entry_data_missing_required(self):
        """Test validation with missing required fields"""
        invalid_data = {
            'entry_date': date.today(),
            # Missing project and work_description
        }
        
        errors = validate_diary_entry_data(invalid_data)
        self.assertIn('project is required', errors)
        self.assertIn('work_description is required', errors)

    def test_validate_diary_entry_data_invalid_percentage(self):
        """Test validation with invalid percentage values"""
        invalid_data = {
            'project': self.project1,
            'entry_date': date.today(),
            'work_description': 'Test description',
            'progress_percentage': '150.0',  # Invalid: > 100
            'humidity': '110'  # Invalid: > 100
        }
        
        errors = validate_diary_entry_data(invalid_data)
        self.assertIn('Progress percentage must be between 0 and 100', errors)
        self.assertIn('Humidity must be between 0 and 100', errors)

    def test_validate_diary_entry_data_invalid_temperature(self):
        """Test validation with invalid temperature range"""
        invalid_data = {
            'project': self.project1,
            'entry_date': date.today(),
            'work_description': 'Test description',
            'temperature_high': '10',  # Lower than low temp
            'temperature_low': '20'
        }
        
        errors = validate_diary_entry_data(invalid_data)
        self.assertIn('High temperature cannot be lower than low temperature', errors)

    def test_generate_diary_report_basic(self):
        """Test basic diary report generation"""
        report = generate_diary_report(self.project1)
        
        self.assertEqual(report['project'], self.project1)
        self.assertEqual(report['summary']['total_entries'], 2)
        self.assertEqual(report['summary']['work_days'], 2)
        self.assertEqual(report['summary']['weather_delays'], 1)
        self.assertEqual(report['summary']['safety_incidents'], 0)
        self.assertEqual(report['summary']['quality_issues'], 0)

    def test_generate_diary_report_with_date_range(self):
        """Test diary report generation with date filtering"""
        start_date = date.today() - timedelta(days=1)
        end_date = date.today() - timedelta(days=1)
        
        report = generate_diary_report(self.project1, start_date, end_date)
        
        self.assertEqual(report['period']['start'], start_date)
        self.assertEqual(report['period']['end'], end_date)
        self.assertEqual(report['summary']['total_entries'], 1)  # Only one entry in range

    def test_generate_diary_report_progress_calculation(self):
        """Test progress calculation in diary report"""
        report = generate_diary_report(self.project1)
        
        # First entry has 25.50%, second has 30.00%
        self.assertEqual(report['progress']['start_progress'], Decimal('25.50'))
        self.assertEqual(report['progress']['end_progress'], Decimal('30.00'))
        self.assertEqual(report['progress']['total_progress'], Decimal('4.50'))

    def test_generate_diary_report_empty_project(self):
        """Test diary report generation for project with no entries"""
        report = generate_diary_report(self.project2)
        
        self.assertEqual(report['project'], self.project2)
        self.assertEqual(report['summary']['total_entries'], 0)
        self.assertEqual(report['summary']['work_days'], 0)
        self.assertEqual(report['progress']['start_progress'], 0)
        self.assertEqual(report['progress']['end_progress'], 0)

    def test_generate_diary_report_entries_ordering(self):
        """Test that diary report entries are properly ordered by date"""
        report = generate_diary_report(self.project1)
        entries = list(report['entries'])
        
        self.assertEqual(len(entries), 2)
        # Should be ordered by entry_date (ascending)
        self.assertTrue(entries[0].entry_date <= entries[1].entry_date)

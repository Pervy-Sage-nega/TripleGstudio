from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from datetime import date, datetime
from unittest.mock import patch, MagicMock
from accounts.models import AdminProfile
from .models import Category, Project, ProjectImage, ProjectStat, ProjectTimeline
import json
import tempfile
import os


class PortfolioModelsTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Test Category')
        self.project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=self.category,
            year=2024,
            location='Test Location',
            size='100 m²',
            duration='6 Months',
            completion_date=date(2024, 12, 31),
            lead_architect='Test Architect',
            status='planned',
            featured=True
        )

    def test_category_creation(self):
        """Test category model creation"""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.slug, 'test-category')

    def test_project_creation(self):
        """Test project model creation"""
        self.assertEqual(self.project.title, 'Test Project')
        self.assertEqual(self.project.category, self.category)
        self.assertTrue(self.project.featured)
        self.assertEqual(str(self.project), 'Test Project (2024)')

    def test_project_absolute_url(self):
        """Test project get_absolute_url method"""
        expected_url = f'/portfolio/{self.project.id}/'
        self.assertEqual(self.project.get_absolute_url(), expected_url)

    def test_project_stats(self):
        """Test project stats relationship"""
        stat = ProjectStat.objects.create(
            project=self.project,
            label='Test Stat',
            value='Test Value',
            order=1
        )
        self.assertEqual(self.project.stats.count(), 1)
        self.assertEqual(stat.project, self.project)

    def test_project_timeline(self):
        """Test project timeline relationship"""
        timeline = ProjectTimeline.objects.create(
            project=self.project,
            title='Test Milestone',
            date=date(2024, 6, 1),
            description='Test milestone description',
            completed=True,
            order=1
        )
        self.assertEqual(self.project.timeline.count(), 1)
        self.assertEqual(timeline.project, self.project)
        self.assertEqual(str(timeline), 'Test Project - Test Milestone (2024-06-01)')

    def test_project_image_creation(self):
        """Test project image relationship"""
        image = ProjectImage.objects.create(
            project=self.project,
            image='test_image.jpg',
            alt_text='Test Image Alt Text',
            order=1
        )
        self.assertEqual(self.project.images.count(), 1)
        self.assertEqual(image.project, self.project)
        self.assertEqual(image.alt_text, 'Test Image Alt Text')


class PortfolioViewsTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.category = Category.objects.create(name='Test Category')
        self.project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=self.category,
            year=2024,
            location='Test Location',
            size='100 m²',
            duration='6 Months',
            completion_date=date(2024, 12, 31),
            lead_architect='Test Architect',
            status='completed',
            featured=True
        )

    def test_project_list_view(self):
        """Test project list view"""
        url = reverse('portfolio:project_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'Our Projects')

    def test_project_detail_view(self):
        """Test project detail view"""
        url = reverse('portfolio:project_detail', kwargs={'project_id': self.project.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'Test description')

    def test_project_detail_not_found(self):
        """Test project detail view with non-existent project"""
        url = reverse('portfolio:project_detail', kwargs={'project_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_project_list_filtering(self):
        """Test project list filtering"""
        # Test year filter
        url = reverse('portfolio:project_list')
        response = self.client.get(url, {'year': '2024'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

        # Test category filter
        response = self.client.get(url, {'category': 'test-category'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

        # Test featured filter
        response = self.client.get(url, {'category': 'featured'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

        # Test search
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_list_empty_results(self):
        """Test project list with no matching results"""
        url = reverse('portfolio:project_list')
        response = self.client.get(url, {'search': 'NonExistentProject'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Projects Found')


class PortfolioAdminTest(TestCase):
    def setUp(self):
        """Set up test data for admin tests"""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()
        
        # Create admin profile
        self.admin_profile = AdminProfile.objects.create(
            user=self.admin_user,
            admin_role='admin',
            approval_status='approved'
        )
        
        self.category = Category.objects.create(name='Test Category')
        self.project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=self.category,
            year=2024,
            location='Test Location',
            size='100 m²',
            duration='6 Months',
            completion_date=date(2024, 12, 31),
            lead_architect='Test Architect',
            status='planned',
            featured=False
        )

    def test_project_management_view_requires_admin(self):
        """Test that project management view requires admin access"""
        url = reverse('portfolio:projectmanagement')
        
        # Test without login
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test with admin login
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Project Portfolio Management')

    def test_create_project_view(self):
        """Test project creation via admin interface"""
        self.client.login(username='admin', password='testpass123')
        
        # Create a simple image file for testing
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        
        project_data = {
            'title': 'New Test Project',
            'description': 'New test description',
            'category': self.category.id,
            'year': 2024,
            'location': 'New Test Location',
            'size': '200 m²',
            'duration': '8 Months',
            'completion_date': '2024-12-31',
            'lead_architect': 'New Test Architect',
            'status': 'ongoing',
            'featured': 'on',
            'hero_image': image,
            'milestone_title[]': ['Foundation', 'Structure'],
            'milestone_date[]': ['2024-03-01', '2024-06-01'],
            'milestone_description[]': ['Foundation work', 'Structure work']
        }
        
        url = reverse('portfolio:create_project')
        response = self.client.post(url, project_data)
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check if project was created
        new_project = Project.objects.get(title='New Test Project')
        self.assertEqual(new_project.status, 'ongoing')
        self.assertTrue(new_project.featured)
        self.assertEqual(new_project.timeline.count(), 2)

    def test_edit_project_view(self):
        """Test project editing via admin interface"""
        self.client.login(username='admin', password='testpass123')
        
        project_data = {
            'title': 'Updated Test Project',
            'description': 'Updated description',
            'category': self.category.id,
            'year': 2024,
            'location': 'Updated Location',
            'size': '150 m²',
            'duration': '7 Months',
            'completion_date': '2024-11-30',
            'lead_architect': 'Updated Architect',
            'status': 'completed',
            'milestone_title[]': ['Updated Milestone'],
            'milestone_date[]': ['2024-05-01'],
            'milestone_description[]': ['Updated milestone description']
        }
        
        url = reverse('portfolio:edit_project', kwargs={'project_id': self.project.id})
        response = self.client.post(url, project_data)
        
        # Should redirect after successful update
        self.assertEqual(response.status_code, 302)
        
        # Check if project was updated
        updated_project = Project.objects.get(id=self.project.id)
        self.assertEqual(updated_project.title, 'Updated Test Project')
        self.assertEqual(updated_project.status, 'completed')

    def test_delete_project_view(self):
        """Test project deletion via admin interface"""
        self.client.login(username='admin', password='testpass123')
        
        project_id = self.project.id
        url = reverse('portfolio:delete_project', kwargs={'project_id': project_id})
        response = self.client.post(url)
        
        # Should redirect after successful deletion
        self.assertEqual(response.status_code, 302)
        
        # Check if project was deleted
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=project_id)

    def test_get_project_data_ajax(self):
        """Test AJAX endpoint for getting project data"""
        self.client.login(username='admin', password='testpass123')
        
        # Add timeline to project
        ProjectTimeline.objects.create(
            project=self.project,
            title='Test Milestone',
            date=date(2024, 6, 1),
            description='Test description',
            order=1
        )
        
        url = reverse('portfolio:get_project_data', kwargs={'project_id': self.project.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['title'], 'Test Project')
        self.assertEqual(data['status'], 'planned')
        self.assertEqual(len(data['milestones']), 1)
        self.assertEqual(data['milestones'][0]['title'], 'Test Milestone')


class PortfolioModelValidationTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(name='Test Category')

    def test_category_slug_auto_generation(self):
        """Test that category slug is automatically generated"""
        category = Category.objects.create(name='Test Category With Spaces')
        self.assertEqual(category.slug, 'test-category-with-spaces')

    def test_category_unique_constraint(self):
        """Test that category names must be unique"""
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Test Category')  # Same name as in setUp

    def test_project_year_validation(self):
        """Test project year validation"""
        # Valid year should work
        project = Project(
            title='Test Project',
            description='Test description',
            category=self.category,
            year=2024,
            location='Test Location',
            size='100 m²',
            duration='6 Months',
            completion_date=date(2024, 12, 31),
            lead_architect='Test Architect',
            status='planned'
        )
        project.full_clean()  # Should not raise ValidationError

    def test_project_status_choices(self):
        """Test project status choices"""
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=self.category,
            year=2024,
            location='Test Location',
            size='100 m²',
            duration='6 Months',
            completion_date=date(2024, 12, 31),
            lead_architect='Test Architect',
            status='invalid_status'  # This should be allowed at model level
        )
        # Django doesn't enforce choices at the database level by default
        self.assertEqual(project.status, 'invalid_status')

    def test_project_image_relationship(self):
        """Test project image relationship"""
        project = Project.objects.create(
            title='Test Project',
            description='Test description',
            category=self.category,
            year=2024,
            location='Test Location',
            size='100 m²',
            duration='6 Months',
            completion_date=date(2024, 12, 31),
            lead_architect='Test Architect',
            status='planned'
        )
        
        # Create test image
        image = ProjectImage.objects.create(
            project=project,
            image='test_image.jpg',
            alt_text='Test image',
            order=1
        )
        
        self.assertEqual(project.images.count(), 1)
        self.assertEqual(image.project, project)
        self.assertEqual(str(image), 'Test Project - Image {}'.format(image.id))


class PortfolioIntegrationTest(TransactionTestCase):
    """Integration tests for the portfolio system"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()
        
        # Create admin profile
        self.admin_profile = AdminProfile.objects.create(
            user=self.admin_user,
            admin_role='admin',
            approval_status='approved'
        )
        
        self.category = Category.objects.create(name='Residential')

    def test_full_project_lifecycle(self):
        """Test complete project lifecycle from creation to deletion"""
        self.client.login(username='admin', password='testpass123')
        
        # 1. Create project
        project_data = {
            'title': 'Integration Test Project',
            'description': 'Full lifecycle test',
            'category': self.category.id,
            'year': 2024,
            'location': 'Test City',
            'size': '300 m²',
            'duration': '12 Months',
            'completion_date': '2024-12-31',
            'lead_architect': 'Test Architect',
            'status': 'planned',
            'milestone_title[]': ['Planning', 'Construction', 'Completion'],
            'milestone_date[]': ['2024-01-01', '2024-06-01', '2024-12-31'],
            'milestone_description[]': ['Planning phase', 'Construction phase', 'Project completion']
        }
        
        create_url = reverse('portfolio:create_project')
        response = self.client.post(create_url, project_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify project was created
        project = Project.objects.get(title='Integration Test Project')
        self.assertEqual(project.timeline.count(), 3)
        
        # 2. Test public project list view
        list_url = reverse('portfolio:project_list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Project')
        
        # 3. Test public project detail view
        detail_url = reverse('portfolio:project_detail', kwargs={'project_id': project.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Integration Test Project')
        self.assertContains(response, 'Full lifecycle test')
        
        # 4. Edit project
        edit_data = project_data.copy()
        edit_data['title'] = 'Updated Integration Test Project'
        edit_data['status'] = 'ongoing'
        
        edit_url = reverse('portfolio:edit_project', kwargs={'project_id': project.id})
        response = self.client.post(edit_url, edit_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify project was updated
        project.refresh_from_db()
        self.assertEqual(project.title, 'Updated Integration Test Project')
        self.assertEqual(project.status, 'ongoing')
        
        # 5. Delete project
        delete_url = reverse('portfolio:delete_project', kwargs={'project_id': project.id})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        
        # Verify project was deleted
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=project.id)

    def test_project_filtering_and_search(self):
        """Test project filtering and search functionality"""
        # Create multiple projects for testing
        commercial_category = Category.objects.create(name='Commercial')
        
        projects_data = [
            {
                'title': 'Residential Villa',
                'category': self.category,
                'year': 2023,
                'location': 'Manila',
                'featured': True
            },
            {
                'title': 'Office Building',
                'category': commercial_category,
                'year': 2024,
                'location': 'Cebu',
                'featured': False
            },
            {
                'title': 'Shopping Mall',
                'category': commercial_category,
                'year': 2024,
                'location': 'Davao',
                'featured': True
            }
        ]
        
        for data in projects_data:
            Project.objects.create(
                title=data['title'],
                description=f"Description for {data['title']}",
                category=data['category'],
                year=data['year'],
                location=data['location'],
                size='100 m²',
                duration='6 Months',
                completion_date=date(2024, 12, 31),
                lead_architect='Test Architect',
                status='completed',
                featured=data['featured']
            )
        
        list_url = reverse('portfolio:project_list')
        
        # Test year filter
        response = self.client.get(list_url, {'year': '2024'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Office Building')
        self.assertContains(response, 'Shopping Mall')
        self.assertNotContains(response, 'Residential Villa')
        
        # Test category filter
        response = self.client.get(list_url, {'category': 'commercial'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Office Building')
        self.assertContains(response, 'Shopping Mall')
        self.assertNotContains(response, 'Residential Villa')
        
        # Test featured filter
        response = self.client.get(list_url, {'category': 'featured'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Residential Villa')
        self.assertContains(response, 'Shopping Mall')
        self.assertNotContains(response, 'Office Building')
        
        # Test search
        response = self.client.get(list_url, {'search': 'Villa'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Residential Villa')
        self.assertNotContains(response, 'Office Building')
        self.assertNotContains(response, 'Shopping Mall')
        
        # Test location search
        response = self.client.get(list_url, {'search': 'Manila'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Residential Villa')
        
        # Test combined filters
        response = self.client.get(list_url, {'year': '2024', 'category': 'commercial'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Office Building')
        self.assertContains(response, 'Shopping Mall')
        self.assertNotContains(response, 'Residential Villa')

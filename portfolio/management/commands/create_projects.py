from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portfolio.models import Category, Project, ProjectImage, ProjectStat
from datetime import date
import os
import shutil
from django.conf import settings
from django.core.files import File


class Command(BaseCommand):
    help = 'Create portfolio projects from project documents'

    def handle(self, *args, **options):
        try:
            # Get the creator user
            creator = User.objects.get(email='sensitivity161@gmail.com')
            
            # Get or create categories
            try:
                residential_cat = Category.objects.get(slug='residential')
            except Category.DoesNotExist:
                residential_cat = Category.objects.create(name='Residential')
            
            try:
                commercial_cat = Category.objects.get(slug='commercial')
            except Category.DoesNotExist:
                commercial_cat = Category.objects.create(name='Commercial')
            
            try:
                interior_cat = Category.objects.get(slug='interior-design')
            except Category.DoesNotExist:
                interior_cat = Category.objects.create(name='Interior Design')
            
            # Project data based on the documents
            projects_data = [
                {
                    'title': '4-Storey Dormitel',
                    'description': 'A modern 4-storey dormitory and hotel complex designed for student accommodation and short-term stays. Features contemporary architecture with efficient space utilization and modern amenities.',
                    'category': commercial_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '2,500 m²',
                    'duration': '18 Months',
                    'completion_date': date(2024, 12, 15),
                    'lead_architect': 'Triple G Studio',
                    'status': 'completed',
                    'featured': True,
                },
                {
                    'title': 'A-Frame Residential Project',
                    'description': 'Innovative A-frame residential design combining traditional architectural elements with modern living requirements. Features sustainable materials and energy-efficient design.',
                    'category': residential_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '180 m²',
                    'duration': '12 Months',
                    'completion_date': date(2024, 10, 30),
                    'lead_architect': 'Triple G Studio',
                    'status': 'completed',
                    'featured': True,
                },
                {
                    'title': 'House 23',
                    'description': 'Contemporary single-family residence featuring open-plan living spaces, large windows for natural light, and seamless indoor-outdoor integration.',
                    'category': residential_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '220 m²',
                    'duration': '10 Months',
                    'completion_date': date(2024, 8, 20),
                    'lead_architect': 'Triple G Studio',
                    'status': 'completed',
                    'featured': False,
                },
                {
                    'title': 'House 27',
                    'description': 'Modern family home with emphasis on natural materials and sustainable design principles. Features spacious living areas and private outdoor spaces.',
                    'category': residential_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '250 m²',
                    'duration': '11 Months',
                    'completion_date': date(2024, 9, 15),
                    'lead_architect': 'Triple G Studio',
                    'status': 'completed',
                    'featured': False,
                },
                {
                    'title': 'House 33',
                    'description': 'Elegant residential design showcasing modern architectural elements with traditional Filipino influences. Optimized for tropical climate conditions.',
                    'category': residential_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '280 m²',
                    'duration': '13 Months',
                    'completion_date': date(2024, 11, 10),
                    'lead_architect': 'Triple G Studio',
                    'status': 'completed',
                    'featured': True,
                },
                {
                    'title': 'Interior Design and Fitout',
                    'description': 'Comprehensive interior design and fitout project featuring modern aesthetics, functional layouts, and premium finishes for residential and commercial spaces.',
                    'category': interior_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '500 m²',
                    'duration': '8 Months',
                    'completion_date': date(2024, 7, 25),
                    'lead_architect': 'Triple G Studio',
                    'status': 'completed',
                    'featured': True,
                },
                {
                    'title': 'Metrotowne',
                    'description': 'Mixed-use development project combining residential, commercial, and retail spaces in an urban setting. Features sustainable design and community-focused amenities.',
                    'category': commercial_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '5,000 m²',
                    'duration': '24 Months',
                    'completion_date': date(2025, 6, 30),
                    'lead_architect': 'Triple G Studio',
                    'status': 'ongoing',
                    'featured': True,
                },
                {
                    'title': 'Pellucid Reverence',
                    'description': 'Architectural masterpiece emphasizing transparency, light, and spatial flow. Features innovative use of glass and steel with sustainable design elements.',
                    'category': residential_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '320 m²',
                    'duration': '14 Months',
                    'completion_date': date(2024, 12, 5),
                    'lead_architect': 'Triple G Studio',
                    'status': 'completed',
                    'featured': True,
                },
                {
                    'title': 'Project Libertad',
                    'description': 'Freedom-inspired architectural design promoting open spaces, natural ventilation, and connection with nature. Sustainable and eco-friendly approach.',
                    'category': residential_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '290 m²',
                    'duration': '12 Months',
                    'completion_date': date(2024, 10, 15),
                    'lead_architect': 'Triple G Studio',
                    'status': 'completed',
                    'featured': False,
                },
                {
                    'title': 'Project Purple',
                    'description': 'Bold and innovative residential design featuring unique color schemes and contemporary architectural elements. Emphasis on creative expression and functionality.',
                    'category': residential_cat,
                    'year': 2024,
                    'location': 'Philippines',
                    'size': '260 m²',
                    'duration': '11 Months',
                    'completion_date': date(2024, 9, 30),
                    'lead_architect': 'Triple G Studio',
                    'status': 'completed',
                    'featured': False,
                },
            ]
            
            # Folder mapping
            folder_mapping = {
                '4-Storey Dormitel': '4-Storey Dormetil',
                'A-Frame Residential Project': 'A-Frame Residential Project',
                'House 23': 'House 23',
                'House 27': 'House 27',
                'House 33': 'House 33',
                'Interior Design and Fitout': 'Interior Design and Fitout',
                'Metrotowne': 'Metrotowne',
                'Pellucid Reverence': 'Pellucid Reverence',
                'Project Libertad': 'Project Libertad',
                'Project Purple': 'Project Purple',
            }
            
            created_count = 0
            for project_data in projects_data:
                project, created = Project.objects.get_or_create(
                    title=project_data['title'],
                    defaults=project_data
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"Created project: {project.title}")
                    
                    # Add images from sitepost folder
                    folder_name = folder_mapping.get(project.title)
                    if folder_name:
                        folder_path = os.path.join(settings.BASE_DIR, 'sitepost', folder_name)
                        if os.path.exists(folder_path):
                            image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                            
                            for i, image_file in enumerate(image_files):
                                src_path = os.path.join(folder_path, image_file)
                                dest_path = f'portfolio/projects/{folder_name}_{image_file}'
                                media_dest = os.path.join(settings.MEDIA_ROOT, dest_path)
                                os.makedirs(os.path.dirname(media_dest), exist_ok=True)
                                shutil.copy2(src_path, media_dest)
                                
                                ProjectImage.objects.create(
                                    project=project,
                                    image=dest_path,
                                    alt_text=f'{project.title} - Image {i+1}',
                                    order=i
                                )
                            
                            self.stdout.write(f"  Added {len(image_files)} images")
                    
                    # Add some basic stats for each project
                    ProjectStat.objects.get_or_create(
                        project=project,
                        label='Total Area',
                        defaults={'value': project_data['size'], 'order': 1}
                    )
                    ProjectStat.objects.get_or_create(
                        project=project,
                        label='Duration',
                        defaults={'value': project_data['duration'], 'order': 2}
                    )
                    ProjectStat.objects.get_or_create(
                        project=project,
                        label='Status',
                        defaults={'value': project_data['status'].title(), 'order': 3}
                    )
                else:
                    self.stdout.write(f"Project already exists: {project.title}")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully processed {len(projects_data)} projects. '
                    f'Created {created_count} new projects.'
                )
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('User sensitivity161@gmail.com not found. Please create the admin user first.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating projects: {str(e)}')
            )
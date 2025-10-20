from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date
from portfolio.models import Category, Project, ProjectImage, ProjectStat, ProjectTimeline


class Command(BaseCommand):
    help = 'Seed the database with sample project data'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Seeding project data...')
        
        # Create categories
        categories = {
            'residential': Category.objects.get_or_create(name='Residential')[0],
            'commercial': Category.objects.get_or_create(name='Commercial')[0],
            'public': Category.objects.get_or_create(name='Public')[0],
        }
        
        # Sample project data based on the JavaScript projects
        projects_data = [
            {
                'title': 'Modern Residential Home',
                'description': 'Contemporary design with sustainable materials and energy-efficient features for a family of four. This project combines modern aesthetics with functional living spaces, utilizing natural light and ventilation to create a comfortable and environmentally friendly home.',
                'category': categories['residential'],
                'year': 2023,
                'location': 'Manila, Philippines',
                'size': '350 m²',
                'duration': '14 Months',
                'completion_date': date(2023, 8, 15),
                'lead_architect': 'Maria Gonzalez',
                'status': 'completed',
                'featured': True,
                'stats': [
                    {'label': 'Total Area', 'value': '350 m²', 'order': 1},
                    {'label': 'Floors', 'value': '2', 'order': 2},
                    {'label': 'Bedrooms', 'value': '4', 'order': 3},
                    {'label': 'Bathrooms', 'value': '3', 'order': 4},
                ],
                'timeline': [
                    {'title': 'Planning & Design', 'date': date(2022, 10, 1), 'description': 'Initial concept development, client consultations, and finalization of architectural plans.', 'completed': True, 'order': 1},
                    {'title': 'Foundation & Structural Work', 'date': date(2022, 12, 1), 'description': 'Excavation, foundation pouring, and structural framework completion.', 'completed': True, 'order': 2},
                    {'title': 'Enclosure & Utilities', 'date': date(2023, 2, 1), 'description': 'Exterior walls, roofing, windows, and installation of plumbing and electrical systems.', 'completed': True, 'order': 3},
                    {'title': 'Interior Construction', 'date': date(2023, 5, 1), 'description': 'Interior walls, flooring, cabinetry, and fixture installation.', 'completed': True, 'order': 4},
                    {'title': 'Finishing & Handover', 'date': date(2023, 8, 15), 'description': 'Final touches, quality inspections, and project handover.', 'completed': True, 'order': 5},
                ]
            },
            {
                'title': 'Corporate Office Building',
                'description': 'Open-concept workspace design with collaborative areas and natural lighting throughout. Features sustainable building materials and energy-efficient systems.',
                'category': categories['commercial'],
                'year': 2022,
                'location': 'Makati, Philippines',
                'size': '1200 m²',
                'duration': '18 Months',
                'completion_date': date(2022, 11, 30),
                'lead_architect': 'Carlos Rivera',
                'status': 'completed',
                'featured': True,
                'stats': [
                    {'label': 'Total Area', 'value': '1200 m²', 'order': 1},
                    {'label': 'Floors', 'value': '5', 'order': 2},
                    {'label': 'Workstations', 'value': '120', 'order': 3},
                    {'label': 'Meeting Rooms', 'value': '8', 'order': 4},
                ],
                'timeline': [
                    {'title': 'Design Development', 'date': date(2021, 6, 1), 'description': 'Workspace planning and architectural design development.', 'completed': True, 'order': 1},
                    {'title': 'Construction Phase 1', 'date': date(2021, 9, 1), 'description': 'Structural modifications and core systems installation.', 'completed': True, 'order': 2},
                    {'title': 'Interior Fit-out', 'date': date(2022, 3, 1), 'description': 'Interior construction and technology infrastructure.', 'completed': True, 'order': 3},
                    {'title': 'Final Completion', 'date': date(2022, 11, 30), 'description': 'Final inspections and client handover.', 'completed': True, 'order': 4},
                ]
            },
            {
                'title': 'Public Library Renovation',
                'description': 'Modernization of a historic library building while preserving its architectural heritage. Enhanced accessibility and modern learning spaces.',
                'category': categories['public'],
                'year': 2021,
                'location': 'Quezon City, Philippines',
                'size': '800 m²',
                'duration': '12 Months',
                'completion_date': date(2021, 9, 15),
                'lead_architect': 'Ana Santos',
                'status': 'completed',
                'featured': True,
                'stats': [
                    {'label': 'Total Area', 'value': '800 m²', 'order': 1},
                    {'label': 'Reading Seats', 'value': '150', 'order': 2},
                    {'label': 'Study Rooms', 'value': '6', 'order': 3},
                    {'label': 'Computer Stations', 'value': '20', 'order': 4},
                ],
                'timeline': [
                    {'title': 'Heritage Assessment', 'date': date(2020, 10, 1), 'description': 'Historical building assessment and preservation planning.', 'completed': True, 'order': 1},
                    {'title': 'Renovation Phase 1', 'date': date(2021, 1, 1), 'description': 'Structural repairs and accessibility improvements.', 'completed': True, 'order': 2},
                    {'title': 'Interior Modernization', 'date': date(2021, 5, 1), 'description': 'Modern library systems and furniture installation.', 'completed': True, 'order': 3},
                    {'title': 'Grand Reopening', 'date': date(2021, 9, 15), 'description': 'Final inspections and public reopening ceremony.', 'completed': True, 'order': 4},
                ]
            },
            {
                'title': 'Luxury Apartment Complex',
                'description': 'High-end residential complex with premium amenities and stunning city views. Features rooftop gardens and smart home technology.',
                'category': categories['residential'],
                'year': 2023,
                'location': 'Bonifacio Global City, Philippines',
                'size': '2500 m²',
                'duration': '24 Months',
                'completion_date': date(2023, 12, 1),
                'lead_architect': 'Miguel Torres',
                'status': 'completed',
                'featured': False,
                'stats': [
                    {'label': 'Total Area', 'value': '2500 m²', 'order': 1},
                    {'label': 'Units', 'value': '24', 'order': 2},
                    {'label': 'Floors', 'value': '8', 'order': 3},
                    {'label': 'Parking Spaces', 'value': '30', 'order': 4},
                ],
                'timeline': [
                    {'title': 'Project Planning', 'date': date(2022, 1, 1), 'description': 'Site analysis and luxury residential design planning.', 'completed': True, 'order': 1},
                    {'title': 'Construction Start', 'date': date(2022, 4, 1), 'description': 'Foundation work and structural construction begins.', 'completed': True, 'order': 2},
                    {'title': 'Amenities Installation', 'date': date(2023, 6, 1), 'description': 'Premium amenities and smart home systems installation.', 'completed': True, 'order': 3},
                    {'title': 'Project Completion', 'date': date(2023, 12, 1), 'description': 'Final unit handovers and amenity completion.', 'completed': True, 'order': 4},
                ]
            },
            {
                'title': 'Beachfront Restaurant',
                'description': 'Coastal dining experience with panoramic ocean views and sustainable design. Features natural materials and open-air dining areas.',
                'category': categories['commercial'],
                'year': 2022,
                'location': 'Boracay, Philippines',
                'size': '400 m²',
                'duration': '10 Months',
                'completion_date': date(2022, 7, 20),
                'lead_architect': 'Isabella Cruz',
                'status': 'completed',
                'featured': False,
                'stats': [
                    {'label': 'Total Area', 'value': '400 m²', 'order': 1},
                    {'label': 'Seating Capacity', 'value': '80', 'order': 2},
                    {'label': 'Kitchen Area', 'value': '100 m²', 'order': 3},
                    {'label': 'Outdoor Seating', 'value': '50', 'order': 4},
                ],
                'timeline': [
                    {'title': 'Coastal Design Planning', 'date': date(2021, 9, 1), 'description': 'Environmental impact assessment and coastal design planning.', 'completed': True, 'order': 1},
                    {'title': 'Foundation & Structure', 'date': date(2021, 12, 1), 'description': 'Specialized coastal foundation and weather-resistant structure.', 'completed': True, 'order': 2},
                    {'title': 'Interior & Kitchen', 'date': date(2022, 4, 1), 'description': 'Commercial kitchen and dining area construction.', 'completed': True, 'order': 3},
                    {'title': 'Grand Opening', 'date': date(2022, 7, 20), 'description': 'Final preparations and restaurant grand opening.', 'completed': True, 'order': 4},
                ]
            },
            {
                'title': 'Urban Park Design',
                'description': 'Community green space with recreational areas, walking paths, and native landscaping. Promotes environmental sustainability and community wellness.',
                'category': categories['public'],
                'year': 2021,
                'location': 'Pasig City, Philippines',
                'size': '5000 m²',
                'duration': '8 Months',
                'completion_date': date(2021, 6, 30),
                'lead_architect': 'Roberto Mendoza',
                'status': 'completed',
                'featured': False,
                'stats': [
                    {'label': 'Total Area', 'value': '5000 m²', 'order': 1},
                    {'label': 'Walking Paths', 'value': '2 km', 'order': 2},
                    {'label': 'Native Trees', 'value': '150', 'order': 3},
                    {'label': 'Recreation Areas', 'value': '4', 'order': 4},
                ],
                'timeline': [
                    {'title': 'Landscape Planning', 'date': date(2020, 11, 1), 'description': 'Community consultation and landscape design development.', 'completed': True, 'order': 1},
                    {'title': 'Site Preparation', 'date': date(2021, 1, 1), 'description': 'Site clearing and soil preparation for landscaping.', 'completed': True, 'order': 2},
                    {'title': 'Infrastructure Installation', 'date': date(2021, 3, 1), 'description': 'Pathways, lighting, and recreational facility installation.', 'completed': True, 'order': 3},
                    {'title': 'Park Opening', 'date': date(2021, 6, 30), 'description': 'Final landscaping and public park opening ceremony.', 'completed': True, 'order': 4},
                ]
            }
        ]
        
        # Create projects with related data
        for project_data in projects_data:
            # Extract related data
            stats_data = project_data.pop('stats', [])
            timeline_data = project_data.pop('timeline', [])
            
            # Create or get project
            project, created = Project.objects.get_or_create(
                title=project_data['title'],
                defaults=project_data
            )
            
            if created:
                self.stdout.write(f'Created project: {project.title}')
                
                # Create stats
                for stat_data in stats_data:
                    ProjectStat.objects.create(project=project, **stat_data)
                
                # Create timeline
                for timeline_item in timeline_data:
                    ProjectTimeline.objects.create(project=project, **timeline_item)
            else:
                self.stdout.write(f'Project already exists: {project.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded {len(projects_data)} projects with categories, stats, and timelines!'
            )
        )

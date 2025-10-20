from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from datetime import datetime, date
from portfolio.models import Category, Project


class Command(BaseCommand):
    help = 'Create a new project interactively'

    def add_arguments(self, parser):
        parser.add_argument('--title', type=str, help='Project title')
        parser.add_argument('--description', type=str, help='Project description')
        parser.add_argument('--category', type=str, help='Category name')
        parser.add_argument('--year', type=int, help='Project year')
        parser.add_argument('--location', type=str, help='Project location')
        parser.add_argument('--size', type=str, help='Project size (e.g., 350 m²)')
        parser.add_argument('--duration', type=str, help='Project duration (e.g., 14 Months)')
        parser.add_argument('--completion-date', type=str, help='Completion date (YYYY-MM-DD)')
        parser.add_argument('--lead-architect', type=str, help='Lead architect name')
        parser.add_argument('--status', type=str, choices=['planned', 'ongoing', 'completed'], 
                          default='planned', help='Project status')
        parser.add_argument('--featured', action='store_true', help='Mark as featured project')

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            # Get or create category
            if options['category']:
                category_name = options['category']
            else:
                category_name = input('Enter category name (Residential/Commercial/Public): ')
            
            category, created = Category.objects.get_or_create(name=category_name)
            if created:
                self.stdout.write(f'Created new category: {category.name}')

            # Collect project data
            project_data = {}
            
            # Required fields
            project_data['title'] = options['title'] or input('Enter project title: ')
            project_data['description'] = options['description'] or input('Enter project description: ')
            project_data['category'] = category
            project_data['year'] = options['year'] or int(input('Enter project year: '))
            project_data['location'] = options['location'] or input('Enter project location: ')
            project_data['size'] = options['size'] or input('Enter project size (e.g., 350 m²): ')
            project_data['duration'] = options['duration'] or input('Enter project duration (e.g., 14 Months): ')
            
            # Handle completion date
            if options['completion_date']:
                project_data['completion_date'] = datetime.strptime(options['completion_date'], '%Y-%m-%d').date()
            else:
                date_str = input('Enter completion date (YYYY-MM-DD): ')
                project_data['completion_date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            project_data['lead_architect'] = options['lead_architect'] or input('Enter lead architect name: ')
            project_data['status'] = options['status'] or input('Enter status (planned/ongoing/completed) [planned]: ') or 'planned'
            project_data['featured'] = options['featured'] or input('Featured project? (y/N): ').lower().startswith('y')

            # Create project
            project = Project.objects.create(**project_data)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created project: {project.title} (ID: {project.id})'
                )
            )
            
            # Provide next steps
            self.stdout.write('\nNext steps:')
            self.stdout.write(f'- Add images via Django admin: /admin/portfolio/project/{project.id}/change/')
            self.stdout.write(f'- View project: /portfolio/{project.id}/')
            self.stdout.write('- Add project stats and timeline items via admin interface')

        except ValueError as e:
            raise CommandError(f'Invalid input: {e}')
        except Exception as e:
            raise CommandError(f'Error creating project: {e}')

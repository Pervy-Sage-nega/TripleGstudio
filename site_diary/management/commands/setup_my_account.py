from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from site_diary.models import Project

class Command(BaseCommand):
    help = 'Setup projects for rideouts200221@gmail.com and remove sample user'

    def handle(self, *args, **options):
        # Get your user account
        try:
            user = User.objects.get(email='rideouts200221@gmail.com')
            user.is_staff = True  # Make sure you have staff access
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Found and updated user: {user.email}')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('User rideouts200221@gmail.com not found.')
            )
            return

        # Remove sample sitemanager user if exists
        try:
            sample_user = User.objects.get(username='sitemanager')
            # Transfer projects to your account
            Project.objects.filter(project_manager=sample_user).update(project_manager=user)
            sample_user.delete()
            self.stdout.write(
                self.style.SUCCESS('Removed sample sitemanager user and transferred projects')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Sample sitemanager user not found')
            )

        # Sample projects data for your account
        projects_data = [
            {
                'name': 'Harbor Tower',
                'client_name': 'Skyline Developments Ltd.',
                'location': 'Downtown Harbor District',
                'status': 'active',
                'description': 'Luxury commercial building with 35 floors, featuring premium office spaces and retail outlets.'
            },
            {
                'name': 'Riverfront Promenade',
                'client_name': 'City Council',
                'location': 'Riverside Park Area',
                'status': 'active',
                'description': 'Public infrastructure project featuring walkways, parks, and recreational areas along the river.'
            },
            {
                'name': 'Oakridge Residences',
                'client_name': 'Oakridge Properties',
                'location': 'Oakridge Suburb',
                'status': 'active',
                'description': 'Luxury residential complex with 120 units, featuring modern amenities and green spaces.'
            }
        ]
        
        created_count = 0
        for project_data in projects_data:
            project, created = Project.objects.get_or_create(
                name=project_data['name'],
                defaults={
                    'client_name': project_data['client_name'],
                    'location': project_data['location'],
                    'status': project_data['status'],
                    'project_manager': user,
                    'description': project_data['description'],
                    'budget': 2500000.00,
                    'start_date': '2024-01-15',
                    'expected_end_date': '2024-12-20'
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created project: {project.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Setup complete! Created {created_count} projects for {user.email}')
        )
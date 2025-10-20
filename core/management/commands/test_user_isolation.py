from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Test user data isolation by creating test users and profiles'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Testing user data isolation...'))
        
        # Create test users
        users_data = [
            {'username': 'testuser1@example.com', 'email': 'testuser1@example.com', 'first_name': 'Test', 'last_name': 'User1'},
            {'username': 'testuser2@example.com', 'email': 'testuser2@example.com', 'first_name': 'Test', 'last_name': 'User2'},
            {'username': 'testuser3@example.com', 'email': 'testuser3@example.com', 'first_name': 'Test', 'last_name': 'User3'},
        ]
        
        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.stdout.write(f'Created user: {user.username}')
            else:
                self.stdout.write(f'User already exists: {user.username}')
            
            created_users.append(user)
        
        # Create unique profiles for each user
        profile_data = [
            {'phone': '123-456-7890', 'assigned_architect': 'Architect A', 'project_name': 'Project Alpha'},
            {'phone': '098-765-4321', 'assigned_architect': 'Architect B', 'project_name': 'Project Beta'},
            {'phone': '555-123-4567', 'assigned_architect': 'Architect C', 'project_name': 'Project Gamma'},
        ]
        
        for i, user in enumerate(created_users):
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'customer',
                    'phone': profile_data[i]['phone'],
                    'assigned_architect': profile_data[i]['assigned_architect'],
                    'project_name': profile_data[i]['project_name'],
                }
            )
            if created:
                self.stdout.write(f'Created profile for {user.username}: {profile_data[i]}')
            else:
                # Update existing profile with test data
                profile.phone = profile_data[i]['phone']
                profile.assigned_architect = profile_data[i]['assigned_architect']
                profile.project_name = profile_data[i]['project_name']
                profile.save()
                self.stdout.write(f'Updated profile for {user.username}: {profile_data[i]}')
        
        # Verify data isolation
        self.stdout.write(self.style.SUCCESS('\n=== USER DATA ISOLATION TEST ==='))
        for user in created_users:
            try:
                profile = user.profile
                self.stdout.write(f'User: {user.username} ({user.get_full_name()})')
                self.stdout.write(f'  Email: {user.email}')
                self.stdout.write(f'  Phone: {profile.phone}')
                self.stdout.write(f'  Architect: {profile.assigned_architect}')
                self.stdout.write(f'  Project: {profile.project_name}')
                self.stdout.write(f'  Profile ID: {profile.id}')
                self.stdout.write('---')
            except Profile.DoesNotExist:
                self.stdout.write(f'ERROR: No profile for user {user.username}')
        
        self.stdout.write(self.style.SUCCESS(
            '\n✅ Test complete! Each user should have unique data.\n'
            'You can now log in as any of these users to test the user settings page:\n'
            '  - testuser1@example.com (password: testpass123)\n'
            '  - testuser2@example.com (password: testpass123)\n'
            '  - testuser3@example.com (password: testpass123)'
        ))

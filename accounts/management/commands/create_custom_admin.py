from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import AdminProfile
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create a custom admin account with specified credentials'

    def handle(self, *args, **options):
        email = 'triplegotp@gmail.com'
        password = 'Ernesto!@#'
        
        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'User with email {email} already exists')
                )
                return
            
            # Create the user (using email as username)
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name='Custom',
                last_name='Admin',
                is_staff=True,
                is_active=True
            )
            
            # Create AdminProfile with approved status
            admin_profile = AdminProfile.objects.create(
                user=user,
                admin_role='admin',
                approval_status='approved',
                department='Administration',
                employee_id=AdminProfile.generate_employee_id(),
                email_verified=True,
                email_verified_at=timezone.now(),
                approved_at=timezone.now(),
                hire_date=timezone.now().date()
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created custom admin account:\n'
                    f'Email: {email}\n'
                    f'Employee ID: {admin_profile.employee_id}\n'
                    f'Status: {admin_profile.approval_status}\n'
                    f'Role: {admin_profile.get_admin_role_display()}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin account: {str(e)}')
            )
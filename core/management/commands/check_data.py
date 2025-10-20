from django.core.management.base import BaseCommand
from core.models import ContactMessage
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check data in the database'

    def handle(self, *args, **options):
        # Check ContactMessage data
        contacts = ContactMessage.objects.all()
        self.stdout.write(f"ContactMessage records: {contacts.count()}")
        
        for contact in contacts:
            self.stdout.write(f"- {contact.name} ({contact.email}) - {contact.status}")
        
        # Check User data
        users = User.objects.all()
        self.stdout.write(f"\nUser records: {users.count()}")
        
        for user in users:
            self.stdout.write(f"- {user.username} ({user.email})")
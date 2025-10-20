from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Test database connection and show database info'

    def handle(self, *args, **options):
        try:
            # Test connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            
            # Get database info
            db_config = settings.DATABASES['default']
            
            self.stdout.write(self.style.SUCCESS('Database connection successful'))
            self.stdout.write(f"Database Engine: {db_config.get('ENGINE', 'Unknown')}")
            
            if os.getenv('DATABASE_URL'):
                self.stdout.write(f"Database: PostgreSQL (Render Cloud)")
                self.stdout.write(f"DATABASE_URL: {os.getenv('DATABASE_URL')[:50]}...")
            else:
                self.stdout.write(f"Database: SQLite (Local)")
                self.stdout.write(f"Database File: {db_config.get('NAME', 'Unknown')}")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Database connection failed: {str(e)}')
            )
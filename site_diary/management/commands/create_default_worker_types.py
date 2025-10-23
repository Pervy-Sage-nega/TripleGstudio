from django.core.management.base import BaseCommand
from site_diary.models import WorkerType

class Command(BaseCommand):
    help = 'Create default worker types'

    def handle(self, *args, **options):
        default_worker_types = [
            {'name': 'Supervisor', 'description': 'Site supervisor', 'default_daily_rate': 800, 'order': 1},
            {'name': 'Skilled Labor', 'description': 'Skilled construction workers', 'default_daily_rate': 600, 'order': 2},
            {'name': 'Unskilled Labor', 'description': 'General laborers', 'default_daily_rate': 400, 'order': 3},
            {'name': 'Subcontractor', 'description': 'External contractors', 'default_daily_rate': 700, 'order': 4},
        ]

        for worker_data in default_worker_types:
            worker_type, created = WorkerType.objects.get_or_create(
                name=worker_data['name'],
                defaults=worker_data
            )
            if created:
                self.stdout.write(f"Created worker type: {worker_type.name}")
            else:
                self.stdout.write(f"Worker type already exists: {worker_type.name}")

        self.stdout.write(self.style.SUCCESS('Default worker types created successfully!'))
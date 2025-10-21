from django.core.management.base import BaseCommand
from site_diary.models import Milestone

class Command(BaseCommand):
    help = 'Create default milestone phases for Triple G projects'

    def handle(self, *args, **options):
        milestones = [
            {'name': 'Planning & Design', 'description': 'Initial project planning, design development, and permit acquisition', 'order': 1},
            {'name': 'Site Preparation', 'description': 'Site clearing, excavation, and preparation work', 'order': 2},
            {'name': 'Foundation Work', 'description': 'Foundation excavation, reinforcement, and concrete pouring', 'order': 3},
            {'name': 'Structural Framework', 'description': 'Structural steel/concrete work, columns, beams, and slabs', 'order': 4},
            {'name': 'Roofing & Envelope', 'description': 'Roof installation and building envelope completion', 'order': 5},
            {'name': 'MEP Installation', 'description': 'Mechanical, Electrical, and Plumbing systems installation', 'order': 6},
            {'name': 'Interior Finishing', 'description': 'Interior walls, flooring, painting, and fixtures', 'order': 7},
            {'name': 'Exterior Finishing', 'description': 'Exterior cladding, landscaping, and site improvements', 'order': 8},
            {'name': 'Final Inspection', 'description': 'Punch list completion and final inspections', 'order': 9},
            {'name': 'Project Handover', 'description': 'Project completion and handover to client', 'order': 10},
        ]

        created_count = 0
        for milestone_data in milestones:
            milestone, created = Milestone.objects.get_or_create(
                name=milestone_data['name'],
                defaults={
                    'description': milestone_data['description'],
                    'order': milestone_data['order'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created milestone: {milestone.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Milestone already exists: {milestone.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new milestones')
        )
from django.core.management.base import BaseCommand
from site_diary.models import SubcontractorCompany

class Command(BaseCommand):
    help = 'Create sample subcontractor companies'

    def handle(self, *args, **options):
        companies = [
            {'name': 'ABC Electrical Services', 'company_type': 'electrical', 'contact_person': 'John Smith', 'phone': '09123456789'},
            {'name': 'Metro Plumbing Solutions', 'company_type': 'plumbing', 'contact_person': 'Maria Santos', 'phone': '09234567890'},
            {'name': 'Cool Air HVAC', 'company_type': 'hvac', 'contact_person': 'Robert Cruz', 'phone': '09345678901'},
            {'name': 'Prime Roofing Contractors', 'company_type': 'roofing', 'contact_person': 'Ana Garcia', 'phone': '09456789012'},
            {'name': 'Elite Flooring Specialists', 'company_type': 'flooring', 'contact_person': 'Carlos Reyes', 'phone': '09567890123'},
            {'name': 'Perfect Paint Solutions', 'company_type': 'painting', 'contact_person': 'Lisa Tan', 'phone': '09678901234'},
            {'name': 'Solid Concrete Works', 'company_type': 'concrete', 'contact_person': 'Miguel Torres', 'phone': '09789012345'},
            {'name': 'Steel Masters Inc.', 'company_type': 'steel', 'contact_person': 'David Lee', 'phone': '09890123456'},
        ]

        for company_data in companies:
            company, created = SubcontractorCompany.objects.get_or_create(
                name=company_data['name'],
                defaults=company_data
            )
            if created:
                self.stdout.write(f'Created: {company.name}')
            else:
                self.stdout.write(f'Already exists: {company.name}')

        self.stdout.write(self.style.SUCCESS('Sample subcontractor companies created successfully!'))
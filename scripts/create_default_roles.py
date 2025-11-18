"""
Script to create default site personnel roles.
Run this after migration: python manage.py shell < create_default_roles.py
"""
from accounts.models import SitePersonnelRole

default_roles = [
    {
        'name': 'architect',
        'display_name': 'Architect',
        'employee_id_prefix': 'AR',
        'description': 'Site Architect - Responsible for design oversight and technical specifications',
        'order': 1
    },
    {
        'name': 'engineer',
        'display_name': 'Engineer',
        'employee_id_prefix': 'EN',
        'description': 'Site Engineer - Handles technical implementation and quality control',
        'order': 2
    },
    {
        'name': 'foreman',
        'display_name': 'Foreman',
        'employee_id_prefix': 'FM',
        'description': 'Site Foreman - Supervises construction workers and daily operations',
        'order': 3
    },
    {
        'name': 'supervisor',
        'display_name': 'Supervisor',
        'employee_id_prefix': 'SV',
        'description': 'Site Supervisor - Oversees site activities and safety compliance',
        'order': 4
    },
]

for role_data in default_roles:
    role, created = SitePersonnelRole.objects.get_or_create(
        name=role_data['name'],
        defaults=role_data
    )
    if created:
        print(f"✓ Created role: {role.display_name} ({role.employee_id_prefix})")
    else:
        print(f"- Role already exists: {role.display_name}")

print("\nDefault roles setup complete!")

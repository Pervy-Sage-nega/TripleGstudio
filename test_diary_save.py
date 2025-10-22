#!/usr/bin/env python
"""
Test script to verify diary entry data saving
Run this from the Django project root: python test_diary_save.py
"""

import os
import sys

# Setup Django first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from site_diary.models import Project, DiaryEntry, MaterialEntry, EquipmentEntry, LaborEntry

def test_diary_save():
    print("=== Testing Diary Entry Save ===")
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'is_staff': True}
    )
    if created:
        user.set_password('testpass')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")
    
    # Get or create test project
    from datetime import date
    project, created = Project.objects.get_or_create(
        name='Test Project',
        defaults={
            'client_name': 'Test Client',
            'location': 'Test Location',
            'project_manager': user,
            'status': 'active',
            'budget': 1000000,
            'start_date': date.today(),
            'expected_end_date': date.today()
        }
    )
    if created:
        print(f"Created test project: {project.name}")
    else:
        print(f"Using existing project: {project.name}")
    
    # Create test client
    client = Client()
    client.force_login(user)
    
    # Test data
    test_data = {
        'project': project.id,
        'entry_date': '2024-10-22',
        'work_description': 'Test work description',
        'progress_percentage': 50,
        'weather_condition': 'sunny',
        'temperature_high': 30,
        'temperature_low': 20,
        'humidity': 65,
        'wind_speed': 10,
        
        # Formset management forms
        'material-TOTAL_FORMS': '2',
        'material-INITIAL_FORMS': '0',
        'material-MIN_NUM_FORMS': '0',
        'material-MAX_NUM_FORMS': '1000',
        
        'equipment-TOTAL_FORMS': '1',
        'equipment-INITIAL_FORMS': '0',
        'equipment-MIN_NUM_FORMS': '0',
        'equipment-MAX_NUM_FORMS': '1000',
        
        'labor-TOTAL_FORMS': '1',
        'labor-INITIAL_FORMS': '0',
        'labor-MIN_NUM_FORMS': '0',
        'labor-MAX_NUM_FORMS': '1000',
        
        # Material data
        'material-0-material_name': 'Cement',
        'material-0-quantity_delivered': '100',
        'material-0-unit': 'bags',
        'material-0-unit_cost': '500',
        'material-0-total_cost': '50000',
        
        'material-1-material_name': 'Steel Bars',
        'material-1-quantity_delivered': '50',
        'material-1-unit': 'pcs',
        'material-1-unit_cost': '1000',
        'material-1-total_cost': '50000',
        
        # Equipment data
        'equipment-0-equipment_type': 'Excavator',
        'equipment-0-hours_operated': '8',
        'equipment-0-rental_cost_per_hour': '2000',
        'equipment-0-total_rental_cost': '16000',
        
        # Labor data
        'labor-0-labor_type': 'Skilled',
        'labor-0-workers_count': '5',
        'labor-0-hours_worked': '8',
        'labor-0-hourly_rate': '500',
        'labor-0-total_cost': '20000',
    }
    
    print("\nSubmitting test diary entry...")
    response = client.post('/diary/diary/', data=test_data)
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 302:
        print(f"Redirected to: {response.url}")
    
    # Check if diary entry was created
    diary_entries = DiaryEntry.objects.filter(
        project=project,
        entry_date='2024-10-22',
        created_by=user
    ).order_by('-created_at')
    
    if diary_entries.exists():
        entry = diary_entries.first()
        print(f"\n✓ Diary entry created: ID {entry.id}")
        
        # Check materials
        materials = MaterialEntry.objects.filter(diary_entry=entry)
        print(f"✓ Materials saved: {materials.count()}")
        for material in materials:
            print(f"  - {material.material_name}: {material.quantity_delivered} {material.unit} @ ₱{material.unit_cost} = ₱{material.total_cost}")
        
        # Check equipment
        equipment = EquipmentEntry.objects.filter(diary_entry=entry)
        print(f"✓ Equipment saved: {equipment.count()}")
        for equip in equipment:
            print(f"  - {equip.equipment_type}: {equip.hours_operated} hours @ ₱{equip.rental_cost_per_hour}/hr = ₱{equip.total_rental_cost}")
        
        # Check labor
        labor = LaborEntry.objects.filter(diary_entry=entry)
        print(f"✓ Labor saved: {labor.count()}")
        for lab in labor:
            print(f"  - {lab.labor_type}: {lab.workers_count} workers × {lab.hours_worked} hours @ ₱{lab.hourly_rate}/hr = ₱{lab.total_cost}")
        
        total_cost = (
            sum(m.total_cost for m in materials) +
            sum(e.total_rental_cost for e in equipment) +
            sum(l.total_cost for l in labor)
        )
        print(f"\nTotal entry cost: ₱{total_cost:,.2f}")
        
        if materials.count() > 0 and equipment.count() > 0 and labor.count() > 0:
            print("\n🎉 SUCCESS: All data saved correctly!")
            return True
        else:
            print("\n❌ FAILED: Some data not saved")
            return False
    else:
        print("\n❌ FAILED: No diary entry created")
        return False

if __name__ == '__main__':
    success = test_diary_save()
    sys.exit(0 if success else 1)
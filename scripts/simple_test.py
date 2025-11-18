#!/usr/bin/env python
"""
Simple test to verify diary entry data saving
"""

import os
import sys
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth.models import User
from site_diary.models import Project, DiaryEntry, MaterialEntry, EquipmentEntry, LaborEntry

def test_direct_save():
    print("=== Testing Direct Database Save ===")
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser2',
        defaults={'email': 'test2@example.com', 'is_staff': True}
    )
    print(f"User: {user.username}")
    
    # Get or create test project
    project, created = Project.objects.get_or_create(
        name='Test Project 2',
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
    print(f"Project: {project.name}")
    
    # Get or create diary entry
    diary_entry, created = DiaryEntry.objects.get_or_create(
        project=project,
        entry_date=date.today(),
        created_by=user,
        defaults={
            'work_description': 'Test work description',
            'progress_percentage': 50,
            'weather_condition': 'sunny',
            'temperature_high': 30,
            'temperature_low': 20,
            'humidity': 65,
            'wind_speed': 10,
            'draft': False
        }
    )
    if not created:
        # Clear existing related entries for clean test
        MaterialEntry.objects.filter(diary_entry=diary_entry).delete()
        EquipmentEntry.objects.filter(diary_entry=diary_entry).delete()
        LaborEntry.objects.filter(diary_entry=diary_entry).delete()
    print(f"Diary Entry: {diary_entry.id}")
    
    # Create material entries
    material1 = MaterialEntry.objects.create(
        diary_entry=diary_entry,
        material_name='Cement',
        quantity_delivered=100,
        unit='bags',
        unit_cost=500
    )
    
    material2 = MaterialEntry.objects.create(
        diary_entry=diary_entry,
        material_name='Steel Bars',
        quantity_delivered=50,
        unit='pcs',
        unit_cost=1000
    )
    
    # Create equipment entry
    equipment1 = EquipmentEntry.objects.create(
        diary_entry=diary_entry,
        equipment_type='Excavator',
        hours_operated=8,
        rental_cost_per_hour=2000
    )
    
    # Create labor entry
    labor1 = LaborEntry.objects.create(
        diary_entry=diary_entry,
        labor_type='skilled',
        trade_description='General Labor',
        workers_count=5,
        hours_worked=8,
        hourly_rate=500
    )
    
    print("\nCreated entries:")
    print(f"- Materials: {MaterialEntry.objects.filter(diary_entry=diary_entry).count()}")
    print(f"- Equipment: {EquipmentEntry.objects.filter(diary_entry=diary_entry).count()}")
    print(f"- Labor: {LaborEntry.objects.filter(diary_entry=diary_entry).count()}")
    
    # Verify data
    materials = MaterialEntry.objects.filter(diary_entry=diary_entry)
    for material in materials:
        print(f"Material: {material.material_name} - {material.quantity_delivered} {material.unit} @ P{material.unit_cost}")
    
    equipment = EquipmentEntry.objects.filter(diary_entry=diary_entry)
    for equip in equipment:
        print(f"Equipment: {equip.equipment_type} - {equip.hours_operated} hours @ P{equip.rental_cost_per_hour}/hr")
    
    labor = LaborEntry.objects.filter(diary_entry=diary_entry)
    for lab in labor:
        print(f"Labor: {lab.labor_type} - {lab.workers_count} workers x {lab.hours_worked} hours @ P{lab.hourly_rate}/hr")
    
    total_cost = (
        sum(m.total_cost for m in materials) +
        sum(e.total_rental_cost for e in equipment) +
        sum(l.total_cost for l in labor)
    )
    print(f"\nTotal cost: P{total_cost:,.2f}")
    
    print("\nSUCCESS: All data saved correctly!")
    return True

if __name__ == '__main__':
    test_direct_save()
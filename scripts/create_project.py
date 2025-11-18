#!/usr/bin/env python
"""
Script to create a new project from command line
Usage: python create_project.py
"""

import os
import sys
from datetime import date, datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth.models import User
from site_diary.models import Project

def create_project():
    print("=== Create New Project ===")
    
    # Get project details
    name = input("Project Name: ").strip()
    if not name:
        print("Error: Project name is required")
        return False
    
    client_name = input("Client Name: ").strip()
    if not client_name:
        print("Error: Client name is required")
        return False
    
    location = input("Project Location: ").strip()
    if not location:
        print("Error: Location is required")
        return False
    
    # Get project manager
    print("\nAvailable Site Managers:")
    managers = User.objects.filter(is_staff=True)
    for i, manager in enumerate(managers, 1):
        print(f"{i}. {manager.get_full_name() or manager.username}")
    
    try:
        manager_choice = int(input("Select Project Manager (number): ")) - 1
        project_manager = managers[manager_choice]
    except (ValueError, IndexError):
        print("Error: Invalid selection")
        return False
    
    # Get dates
    start_date_str = input("Start Date (YYYY-MM-DD): ").strip()
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Error: Invalid date format")
        return False
    
    end_date_str = input("Expected End Date (YYYY-MM-DD): ").strip()
    try:
        expected_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        print("Error: Invalid date format")
        return False
    
    if expected_end_date <= start_date:
        print("Error: End date must be after start date")
        return False
    
    # Get budget
    try:
        budget = float(input("Budget (₱): ").strip())
        if budget <= 0:
            print("Error: Budget must be positive")
            return False
    except ValueError:
        print("Error: Invalid budget amount")
        return False
    
    # Optional fields
    description = input("Description (optional): ").strip()
    
    # Create project
    try:
        project = Project.objects.create(
            name=name,
            client_name=client_name,
            location=location,
            project_manager=project_manager,
            start_date=start_date,
            expected_end_date=expected_end_date,
            budget=budget,
            description=description,
            status='active'
        )
        
        print(f"\n✓ Project created successfully!")
        print(f"  ID: {project.id}")
        print(f"  Name: {project.name}")
        print(f"  Client: {project.client_name}")
        print(f"  Manager: {project.project_manager.get_full_name() or project.project_manager.username}")
        print(f"  Budget: ₱{project.budget:,.2f}")
        print(f"  Duration: {start_date} to {expected_end_date}")
        
        return True
        
    except Exception as e:
        print(f"Error creating project: {str(e)}")
        return False

if __name__ == '__main__':
    success = create_project()
    sys.exit(0 if success else 1)
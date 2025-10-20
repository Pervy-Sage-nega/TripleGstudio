#!/usr/bin/env python
"""
Test script to create sample data for the logged-in user
Run this from the Django project root directory
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TripleG.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command

def main():
    print("=== Triple G Sample Data Creator ===")
    print()
    
    # Find active staff users
    staff_users = User.objects.filter(is_staff=True, is_active=True).order_by('-last_login')
    
    if not staff_users.exists():
        print("❌ No active staff users found!")
        print("Please create a staff user first or log in to the admin panel.")
        return
    
    print("Available staff users:")
    for i, user in enumerate(staff_users, 1):
        last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
        print(f"{i}. {user.email} (Last login: {last_login})")
    
    print()
    
    # Auto-select the most recently logged in user
    selected_user = staff_users.first()
    print(f"🎯 Auto-selected user: {selected_user.email}")
    print()
    
    # Ask for confirmation
    confirm = input("Create sample data for this user? (y/N): ").lower().strip()
    
    if confirm != 'y':
        print("❌ Operation cancelled.")
        return
    
    # Ask about clearing existing data
    clear_existing = input("Clear existing projects first? (y/N): ").lower().strip() == 'y'
    
    print()
    print("🚀 Creating sample data...")
    print("-" * 50)
    
    try:
        # Run the management command
        args = ['--user-email', selected_user.email]
        if clear_existing:
            args.append('--clear-existing')
            
        call_command('create_sample_data', *args)
        
        print("-" * 50)
        print("✅ Sample data creation completed!")
        print()
        print("You can now:")
        print("1. Log in to the site diary dashboard")
        print("2. View the created projects")
        print("3. Check diary entries and related data")
        print()
        print("🌐 Access your dashboard at: http://localhost:8000/site-diary/dashboard/")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        print("Please check your Django setup and database connection.")

if __name__ == '__main__':
    main()
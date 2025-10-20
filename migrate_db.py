#!/usr/bin/env python
"""
Simple script to migrate from PostgreSQL to SQLite using Django's dumpdata/loaddata
"""
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    print("=== Database Migration: PostgreSQL to SQLite ===")
    
    # Step 1: Create data dump from PostgreSQL (if connection works)
    print("\nStep 1: Attempting to dump data from PostgreSQL...")
    dump_success = run_command(
        "python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data_dump.json",
        "Dumping data from PostgreSQL"
    )
    
    if not dump_success:
        print("Could not dump from PostgreSQL. Creating empty local database...")
    
    # Step 2: Switch to SQLite by temporarily modifying settings
    print("\nStep 2: Setting up SQLite database...")
    
    # Create a temporary settings file for SQLite
    sqlite_settings = '''
# Temporary SQLite settings
import os
from pathlib import Path
from config.settings import *

# Override database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''
    
    with open(BASE_DIR / 'sqlite_settings.py', 'w') as f:
        f.write(sqlite_settings)
    
    # Step 3: Run migrations on SQLite
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sqlite_settings'
    run_command(
        "python manage.py migrate",
        "Running migrations on SQLite"
    )
    
    # Step 4: Load data if dump was successful
    if dump_success and os.path.exists(BASE_DIR / 'data_dump.json'):
        print("\nStep 4: Loading data into SQLite...")
        run_command(
            "python manage.py loaddata data_dump.json",
            "Loading data into SQLite"
        )
    else:
        print("\nStep 4: Creating superuser for SQLite database...")
        print("You'll need to create a superuser manually:")
        print("python manage.py createsuperuser")
    
    # Step 5: Update main settings to use SQLite
    print("\nStep 5: Updating main settings to use SQLite...")
    
    settings_file = BASE_DIR / 'config' / 'settings.py'
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Replace PostgreSQL config with SQLite
    old_db_config = '''DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'tripleg_postgre_sql'),
        'USER': os.getenv('DB_USER', 'tripleg_postgre_sql_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'r4bKPWIPB9toQ8awybGsEtjg74YTG33X'),
        'HOST': os.getenv('DB_HOST', 'dpg-d375ipur433s73eecc10-a.singapore-postgres.render.com'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}'''
    
    new_db_config = '''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}'''
    
    if old_db_config in content:
        content = content.replace(old_db_config, new_db_config)
        with open(settings_file, 'w') as f:
            f.write(content)
        print("✓ Settings updated to use SQLite")
    else:
        print("⚠ Could not automatically update settings. Please manually change database config to SQLite.")
    
    # Cleanup
    if os.path.exists(BASE_DIR / 'sqlite_settings.py'):
        os.remove(BASE_DIR / 'sqlite_settings.py')
    if os.path.exists(BASE_DIR / 'data_dump.json'):
        os.remove(BASE_DIR / 'data_dump.json')
    
    print("\n=== Migration Complete ===")
    print("Your application is now configured to use SQLite.")
    print("You can run: python manage.py runserver")

if __name__ == '__main__':
    main()
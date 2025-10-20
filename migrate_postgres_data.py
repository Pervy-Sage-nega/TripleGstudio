import os
import sys
import django
import psycopg2
import json
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Temporarily use PostgreSQL settings
os.environ['USE_POSTGRES'] = 'true'

# Update settings to use PostgreSQL for data extraction
from django.conf import settings
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'tripleg_postgre_sql',
    'USER': 'tripleg_postgre_sql_user',
    'PASSWORD': 'r4bKPWIPB9toQ8awybGsEtjg74YTG33X',
    'HOST': 'dpg-d375ipur433s73eecc10-a.singapore-postgres.render.com',
    'PORT': '5432',
    'OPTIONS': {'sslmode': 'require'},
}

django.setup()

from django.core import serializers
from django.apps import apps

def extract_data():
    """Extract all data from PostgreSQL"""
    print("Extracting data from PostgreSQL...")
    
    # Get all models
    all_models = []
    for app_config in apps.get_app_configs():
        if app_config.name in ['core', 'accounts', 'portfolio', 'site_diary', 'blog', 'admin_side']:
            all_models.extend(app_config.get_models())
    
    # Extract data
    all_objects = []
    for model in all_models:
        try:
            objects = model.objects.all()
            if objects.exists():
                print(f"Extracting {objects.count()} records from {model._meta.label}")
                all_objects.extend(objects)
        except Exception as e:
            print(f"Error extracting from {model._meta.label}: {e}")
    
    # Serialize data
    data = serializers.serialize('json', all_objects, use_natural_foreign_keys=True, use_natural_primary_keys=True)
    
    # Save to file
    with open('postgres_data.json', 'w') as f:
        f.write(data)
    
    print(f"Extracted {len(all_objects)} total objects to postgres_data.json")

def import_to_sqlite():
    """Import data to SQLite"""
    print("Switching to SQLite and importing data...")
    
    # Switch to SQLite
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    
    # Reset Django connections
    from django.db import connections
    connections.databases = settings.DATABASES
    
    # Run migrations
    from django.core.management import call_command
    call_command('migrate', verbosity=0)
    
    # Load data
    if os.path.exists('postgres_data.json'):
        try:
            call_command('loaddata', 'postgres_data.json', verbosity=2)
            print("Data imported successfully!")
        except Exception as e:
            print(f"Error importing data: {e}")
    else:
        print("No data file found to import")

if __name__ == '__main__':
    try:
        extract_data()
        import_to_sqlite()
        
        # Cleanup
        if os.path.exists('postgres_data.json'):
            os.remove('postgres_data.json')
            
        print("\nMigration complete! Your local SQLite database now has the PostgreSQL data.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
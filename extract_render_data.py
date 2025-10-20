#!/usr/bin/env python
"""
Script to extract data from Render PostgreSQL and import to local SQLite
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import psycopg2
import sqlite3
from django.core.management import call_command
from django.db import connection

# Render PostgreSQL connection details
RENDER_DB_CONFIG = {
    'host': 'dpg-d375ipur433s73eecc10-a.singapore-postgres.render.com',
    'database': 'tripleg_postgre_sql',
    'user': 'tripleg_postgre_sql_user',
    'password': 'r4bKPWIPB9toQ8awybGsEtjg74YTG33X',
    'port': '5432',
    'sslmode': 'require'
}

def extract_render_data():
    """Extract data from Render PostgreSQL database"""
    print("Connecting to Render PostgreSQL...")
    
    try:
        # Connect to Render PostgreSQL
        pg_conn = psycopg2.connect(**RENDER_DB_CONFIG)
        pg_cursor = pg_conn.cursor()
        
        # Get all table names
        pg_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in pg_cursor.fetchall()]
        print(f"Found {len(tables)} tables: {', '.join(tables)}")
        
        # Extract data from each table
        table_data = {}
        for table in tables:
            print(f"Extracting data from {table}...")
            pg_cursor.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in pg_cursor.description]
            rows = pg_cursor.fetchall()
            table_data[table] = {
                'columns': columns,
                'rows': rows
            }
            print(f"  - {len(rows)} rows extracted")
        
        pg_conn.close()
        return table_data
        
    except Exception as e:
        print(f"Error connecting to Render PostgreSQL: {e}")
        return None

def setup_local_sqlite():
    """Setup local SQLite database"""
    print("Setting up local SQLite database...")
    
    # Temporarily switch to SQLite
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    
    # Run migrations
    call_command('migrate', verbosity=0)
    print("Local SQLite database setup complete")

def import_data_to_sqlite(table_data):
    """Import extracted data to local SQLite"""
    if not table_data:
        print("No data to import")
        return
    
    print("Importing data to local SQLite...")
    
    # Connect to local SQLite
    sqlite_conn = sqlite3.connect(BASE_DIR / 'db.sqlite3')
    sqlite_cursor = sqlite_conn.cursor()
    
    for table_name, data in table_data.items():
        columns = data['columns']
        rows = data['rows']
        
        if not rows:
            print(f"  - Skipping {table_name} (no data)")
            continue
            
        print(f"  - Importing {len(rows)} rows to {table_name}")
        
        # Clear existing data
        try:
            sqlite_cursor.execute(f"DELETE FROM {table_name}")
        except sqlite3.OperationalError:
            print(f"    - Table {table_name} doesn't exist in local DB, skipping")
            continue
        
        # Insert data
        placeholders = ','.join(['?' for _ in columns])
        insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        
        try:
            sqlite_cursor.executemany(insert_sql, rows)
            sqlite_conn.commit()
            print(f"    - Successfully imported {len(rows)} rows")
        except Exception as e:
            print(f"    - Error importing to {table_name}: {e}")
            sqlite_conn.rollback()
    
    sqlite_conn.close()
    print("Data import complete")

def main():
    print("=== Render PostgreSQL to Local SQLite Migration ===")
    
    # Step 1: Extract data from Render
    table_data = extract_render_data()
    
    if not table_data:
        print("Failed to extract data from Render PostgreSQL")
        return
    
    # Step 2: Setup local SQLite
    setup_local_sqlite()
    
    # Step 3: Import data to SQLite
    import_data_to_sqlite(table_data)
    
    print("\n=== Migration Complete ===")
    print("You can now run the server with local SQLite database")
    print("Run: python manage.py runserver")

if __name__ == '__main__':
    main()
"""
Local PostgreSQL settings for TripleG
Run this to set up local PostgreSQL instead of SQLite
"""

# Add this to your settings.py to use local PostgreSQL
LOCAL_POSTGRES_CONFIG = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tripleg_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password_here',  # Change this
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Instructions:
# 1. Install PostgreSQL locally
# 2. Create database: CREATE DATABASE tripleg_db;
# 3. Update password in this file
# 4. Replace DATABASES in settings.py with LOCAL_POSTGRES_CONFIG
# 5. Run: pip install psycopg2-binary
# 6. Run: python manage.py migrate
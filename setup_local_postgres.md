# Local PostgreSQL Setup for TripleG

## 1. Install PostgreSQL
Download and install PostgreSQL from: https://www.postgresql.org/download/windows/

## 2. Create Database
```sql
-- Connect to PostgreSQL as postgres user
CREATE DATABASE tripleg_db;
CREATE USER tripleg_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE tripleg_db TO tripleg_user;
```

## 3. Install Python Package
```bash
pip install psycopg2-binary
```

## 4. Update Django Settings
In `config/settings.py`, replace the DATABASES section with:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tripleg_db',
        'USER': 'tripleg_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 5. Run Migrations
```bash
cd TripleG
python manage.py migrate
python manage.py create_custom_admin
python manage.py create_projects
python manage.py check_project_images
python manage.py add_project_covers
python manage.py create_site_manager
python manage.py create_blog_posts
```

This will fix all SQLite query issues with PostgreSQL's better query support.
# Migration Guide: Render PostgreSQL → Supabase PostgreSQL

## Overview
This guide will help you migrate your Triple G Django application from Render PostgreSQL to Supabase PostgreSQL.

## Prerequisites
- Supabase account (https://supabase.com)
- Access to current Render database
- Django project with all dependencies installed

---

## Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in:
   - **Project Name**: `tripleg-production` (or your choice)
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your users (e.g., Singapore)
4. Wait for project to be created (~2 minutes)

---

## Step 2: Get Supabase Connection Details

1. In your Supabase project dashboard, go to **Settings** → **Database**
2. Find the **Connection String** section
3. Copy the **Connection pooling** URI (recommended for Django):
   ```
   postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
4. Also note down individual connection details:
   - **Host**: `aws-0-[REGION].pooler.supabase.com`
   - **Port**: `6543` (pooler) or `5432` (direct)
   - **Database**: `postgres`
   - **User**: `postgres.[PROJECT-REF]`
   - **Password**: Your database password

---

## Step 3: Backup Current Render Database

### Option A: Using pg_dump (Recommended)

```bash
# Connect to Render database and create backup
pg_dump -h dpg-d3r8hqu3jp1c7394km30-a.singapore-postgres.render.com \
        -U tripleg_user \
        -d tripleg_db \
        -F c \
        -f tripleg_backup.dump

# Enter password when prompted: d8GpSfe5Tb5uNSPvjosneUe9h8MSLXHz
```

### Option B: Using Django dumpdata

```bash
# Backup all data to JSON
python manage.py dumpdata --natural-foreign --natural-primary \
    --exclude contenttypes --exclude auth.Permission \
    --indent 2 > tripleg_full_backup.json

# Backup specific apps
python manage.py dumpdata accounts > accounts_backup.json
python manage.py dumpdata site_diary > site_diary_backup.json
python manage.py dumpdata blog > blog_backup.json
python manage.py dumpdata portfolio > portfolio_backup.json
python manage.py dumpdata chatbot > chatbot_backup.json
python manage.py dumpdata admin_side > admin_side_backup.json
```

---

## Step 4: Update Django Settings

### Update `.env` file:

```env
# Supabase PostgreSQL Configuration
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# OR use individual variables
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.[PROJECT-REF]
DB_PASSWORD=your_supabase_password
DB_HOST=aws-0-[REGION].pooler.supabase.com
DB_PORT=6543

# Other settings remain the same
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
```

### Verify settings.py configuration:

Your current `settings.py` already supports both `DATABASE_URL` and individual variables, so no code changes needed!

```python
# This is already in your settings.py - no changes needed
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
    }
    DATABASES['default']['CONN_MAX_AGE'] = 600
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
```

---

## Step 5: Test Connection Locally

```bash
# Test connection with new Supabase credentials
python manage.py check --database default

# If successful, you'll see:
# System check identified no issues (0 silenced).
```

---

## Step 6: Run Migrations on Supabase

```bash
# Create all tables in Supabase database
python manage.py migrate

# This will create all tables for:
# - accounts (Profile, AdminProfile, SiteManagerProfile, etc.)
# - site_diary (Project, DiaryEntry, LaborEntry, MaterialEntry, etc.)
# - blog (BlogPost, Category, Tag, Comment, etc.)
# - portfolio (Project, ProjectImage, ProjectStat, etc.)
# - chatbot (ChatbotMessage)
# - admin_side (ProjectAssignment)
```

---

## Step 7: Restore Data to Supabase

### Option A: Using pg_restore (if you used pg_dump)

```bash
# Restore from dump file
pg_restore -h aws-0-[REGION].pooler.supabase.com \
           -U postgres.[PROJECT-REF] \
           -d postgres \
           -p 6543 \
           --no-owner \
           --no-acl \
           tripleg_backup.dump
```

### Option B: Using Django loaddata (if you used dumpdata)

```bash
# Load all data
python manage.py loaddata tripleg_full_backup.json

# OR load by app
python manage.py loaddata accounts_backup.json
python manage.py loaddata site_diary_backup.json
python manage.py loaddata blog_backup.json
python manage.py loaddata portfolio_backup.json
python manage.py loaddata chatbot_backup.json
python manage.py loaddata admin_side_backup.json
```

---

## Step 8: Verify Data Migration

```bash
# Check if data was migrated successfully
python manage.py shell
```

```python
# In Django shell
from django.contrib.auth.models import User
from accounts.models import Profile, SiteManagerProfile
from site_diary.models import Project, DiaryEntry
from blog.models import BlogPost
from portfolio.models import Project as PortfolioProject

# Check counts
print(f"Users: {User.objects.count()}")
print(f"Profiles: {Profile.objects.count()}")
print(f"Site Managers: {SiteManagerProfile.objects.count()}")
print(f"Projects: {Project.objects.count()}")
print(f"Diary Entries: {DiaryEntry.objects.count()}")
print(f"Blog Posts: {BlogPost.objects.count()}")
print(f"Portfolio Projects: {PortfolioProject.objects.count()}")
```

---

## Step 9: Migrate Media Files

Your media files are currently in `media/` directory. You have two options:

### Option A: Keep using local/Render storage
- No changes needed
- Files stay in `media/` directory

### Option B: Use Supabase Storage (Recommended for production)

1. In Supabase dashboard, go to **Storage**
2. Create buckets:
   - `profile-pics`
   - `project-images`
   - `blog-images`
   - `architect-gallery`
   - `diary-photos`

3. Install Supabase storage library:
```bash
pip install supabase-py
```

4. Update Django settings to use Supabase storage (optional - requires custom storage backend)

---

## Step 10: Update Production Environment Variables

If deploying to Render, Railway, or other platform:

1. Update environment variables with Supabase credentials
2. Set `DATABASE_URL` to Supabase connection string
3. Redeploy application

---

## Step 11: Performance Optimization for Supabase

Add these to your `settings.py` for better performance:

```python
# Add to DATABASES configuration
DATABASES['default']['CONN_MAX_AGE'] = 600  # Already in your settings
DATABASES['default']['CONN_HEALTH_CHECKS'] = True  # Add this
DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000'  # 30 second timeout
}
```

---

## Step 12: Enable Supabase Features (Optional)

Supabase offers additional features you can leverage:

### 1. Row Level Security (RLS)
- Go to **Authentication** → **Policies**
- Set up RLS policies for sensitive tables

### 2. Realtime Subscriptions
- Enable realtime for tables that need live updates
- Useful for chat, notifications, etc.

### 3. Database Backups
- Go to **Settings** → **Database** → **Backups**
- Supabase automatically backs up daily
- You can also create manual backups

### 4. Connection Pooling
- Already using pooler (port 6543)
- Handles up to 200 concurrent connections

---

## Troubleshooting

### Issue: Connection timeout
**Solution**: Use connection pooler (port 6543) instead of direct connection (port 5432)

### Issue: SSL certificate error
**Solution**: Ensure `sslmode: require` is in OPTIONS

### Issue: Migration fails
**Solution**: 
```bash
# Reset migrations (only if needed)
python manage.py migrate --fake-initial
```

### Issue: Data not loading
**Solution**: Check for foreign key constraints, load data in correct order:
1. Users and auth data
2. Profiles (accounts)
3. Projects (site_diary, portfolio)
4. Related data (diary entries, blog posts)

---

## Rollback Plan

If something goes wrong:

1. Keep Render database active during migration
2. Switch back by updating `DATABASE_URL` to Render credentials
3. Redeploy with old settings

---

## Post-Migration Checklist

- [ ] All tables created successfully
- [ ] All data migrated (verify counts)
- [ ] User authentication works
- [ ] File uploads work
- [ ] All features tested
- [ ] Performance is acceptable
- [ ] Backups configured
- [ ] Old Render database can be decommissioned

---

## Cost Comparison

### Render PostgreSQL
- Free tier: Limited
- Paid: $7/month (Starter)

### Supabase PostgreSQL
- Free tier: 500MB database, 2GB bandwidth
- Pro: $25/month (8GB database, 50GB bandwidth)
- Includes: Auth, Storage, Realtime, Edge Functions

---

## Support

- Supabase Docs: https://supabase.com/docs
- Supabase Discord: https://discord.supabase.com
- Django Database Docs: https://docs.djangoproject.com/en/5.2/ref/databases/

---

## Summary

Your Django app is already configured to work with any PostgreSQL database. The migration is straightforward:

1. ✅ Create Supabase project
2. ✅ Backup Render data
3. ✅ Update DATABASE_URL
4. ✅ Run migrations
5. ✅ Restore data
6. ✅ Test thoroughly

**Estimated Time**: 30-60 minutes

**Downtime**: Can be done with zero downtime using blue-green deployment

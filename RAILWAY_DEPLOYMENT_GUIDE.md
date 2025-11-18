# Railway Deployment Guide

## Quick Setup

### 1. Prepare Project

Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn tripleG.wsgi:application",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

Create `Procfile`:
```
web: gunicorn tripleG.wsgi:application
```

Update `requirements.txt`:
```txt
gunicorn
whitenoise
dj-database-url
psycopg2-binary
```

### 2. Deploy to Railway

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Django

### 3. Set Environment Variables

In Railway dashboard → Variables:

```env
DATABASE_URL=your_supabase_connection_string
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=.railway.app,your-domain.com
DISABLE_COLLECTSTATIC=1
```

### 4. Configure Static Files

Update `settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest
]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 5. Deploy

```bash
git add .
git commit -m "Railway deployment config"
git push
```

Railway auto-deploys on push.

### 6. Run Migrations

In Railway dashboard → your service → Settings:
- Update start command: `python manage.py migrate && gunicorn tripleG.wsgi:application`

Or use Railway CLI:
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

## Domain Setup

1. Railway dashboard → Settings → Domains
2. Click "Generate Domain" or add custom domain
3. Update `ALLOWED_HOSTS` with new domain

## Troubleshooting

**Build fails**: Check `requirements.txt` has all dependencies
**Static files 404**: Run `python manage.py collectstatic`
**Database error**: Verify `DATABASE_URL` in Railway variables
**App crashes**: Check logs in Railway dashboard

## Done!

Your app is live at: `https://your-app.railway.app`

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import shutil
from pathlib import Path

class Command(BaseCommand):
    help = 'Clears Django cache, session data, and Whitenoise static files cache'

    def handle(self, *args, **options):
        self.stdout.write("🧹 Starting cache cleanup...")
        
        # 1. Clear Django's cache
        self.clear_django_cache()
        
        # 2. Clear session data
        self.clear_sessions()
        
        # 3. Clear Whitenoise cache
        self.clear_whitenoise_cache()
        
        # 4. Clear browser-accessible static files
        self.clear_static_files()
        
        self.stdout.write(self.style.SUCCESS('✅ All caches cleared successfully!'))
        self.stdout.write("🔄 You may need to restart your development server and do a hard refresh (Ctrl+F5) in your browser.")

    def clear_django_cache(self):
        """Clear Django's cache framework"""
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✅ Django cache cleared'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error clearing Django cache: {str(e)}'))

    def clear_sessions(self):
        """Clear all session data"""
        try:
            from django.contrib.sessions.models import Session
            Session.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Session data cleared'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error clearing sessions: {str(e)}'))

    def clear_whitenoise_cache(self):
        """Clear Whitenoise's cache directory"""
        try:
            whitenoise_cache = Path(settings.STATIC_ROOT) / 'CACHE'
            if whitenoise_cache.exists():
                shutil.rmtree(whitenoise_cache)
                self.stdout.write(self.style.SUCCESS('✅ Whitenoise cache cleared'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Whitenoise cache directory not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error clearing Whitenoise cache: {str(e)}'))

    def clear_static_files(self):
        """Clear collected static files"""
        try:
            if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
                static_root = Path(settings.STATIC_ROOT)
                if static_root.exists():
                    # Remove all files in STATIC_ROOT
                    for item in static_root.glob('*'):
                        if item.name == '.gitkeep':  # Skip .gitkeep if it exists
                            continue
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    self.stdout.write(self.style.SUCCESS('✅ Static files cleared'))
                else:
                    self.stdout.write(self.style.WARNING('⚠️ STATIC_ROOT directory does not exist'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ STATIC_ROOT is not configured in settings'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error clearing static files: {str(e)}'))
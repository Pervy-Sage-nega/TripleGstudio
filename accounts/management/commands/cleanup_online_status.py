from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Clean up expired online status entries from cache'

    def handle(self, *args, **options):
        # This is a placeholder - in production with Redis you would use pattern matching
        # For now, the cache entries will expire automatically based on CACHE_TIMEOUT
        self.stdout.write(
            self.style.SUCCESS('Online status cleanup completed (cache entries expire automatically)')
        )
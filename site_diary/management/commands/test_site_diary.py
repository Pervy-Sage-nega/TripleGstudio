"""
Simple Django management command to test site_diary app
"""
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Test site_diary app functionality'
    
    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("SITE DIARY APP TEST")
        self.stdout.write("=" * 50)
        
        # Test URL resolution
        self.test_urls()
        
        # Test basic view access
        self.test_views()
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("TEST COMPLETE")
        self.stdout.write("=" * 50)
    
    def test_urls(self):
        self.stdout.write("\nTesting URL resolution...")
        
        urls_to_test = [
            'site_diary:dashboard',
            'site_diary:diary',
            'site_diary:newproject',
            'site_diary:project_list',
            'site_diary:history',
            'site_diary:reports'
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                self.stdout.write(f"[OK] {url_name} resolved to: {url}")
            except Exception as e:
                self.stdout.write(f"[FAIL] {url_name} failed: {e}")
    
    def test_views(self):
        self.stdout.write("\nTesting view access...")
        
        client = Client()
        
        # Test unauthenticated access
        response = client.get('/diary/dashboard/')
        self.stdout.write(f"Dashboard (unauthenticated): {response.status_code}")
        
        # Test if redirect works
        if response.status_code in [302, 403]:
            self.stdout.write("[OK] Dashboard properly protected")
        else:
            self.stdout.write("[FAIL] Dashboard security issue")
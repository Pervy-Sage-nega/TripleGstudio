#!/usr/bin/env python
"""
Test email sending functionality
"""

import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    print("=== Testing Email Configuration ===")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    try:
        result = send_mail(
            "Test Email - Triple G BuildHub",
            "This is a test email to verify email configuration.",
            settings.DEFAULT_FROM_EMAIL,
            ['rideouts199@gmail.com'],
            fail_silently=False,
        )
        print(f"\nEmail sent successfully! Result: {result}")
        return True
    except Exception as e:
        print(f"\nEmail sending failed: {str(e)}")
        return False

if __name__ == '__main__':
    test_email()
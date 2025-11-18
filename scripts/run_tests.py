#!/usr/bin/env python
"""
Test runner script for Triple G Portfolio System
Run this script to execute all tests for the portfolio app
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.test_settings')
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run specific app tests
    failures = test_runner.run_tests(["portfolio"])
    
    if failures:
        sys.exit(bool(failures))
    else:
        print("\n🎉 All tests passed successfully!")
        print("Your Triple G Portfolio System is working correctly.")

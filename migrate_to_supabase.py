"""
Migration Script: Render PostgreSQL → Supabase PostgreSQL
Usage: python migrate_to_supabase.py
"""

import os
import sys
import subprocess
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(step, message):
    print(f"\n{Colors.BLUE}[Step {step}]{Colors.END} {message}")

def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")

def print_error(message):
    print(f"{Colors.RED}✗{Colors.END} {message}")

def run_command(command, description):
    """Run a shell command and return success status"""
    print(f"  Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print_success(f"{description} completed")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed: {e.stderr}")
        return False, e.stderr

def main():
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}Triple G Migration: Render → Supabase{Colors.END}")
    print(f"{'='*60}\n")
    
    # Step 1: Check environment
    print_step(1, "Checking environment...")
    
    if not os.path.exists('manage.py'):
        print_error("manage.py not found. Run this script from project root.")
        sys.exit(1)
    
    print_success("Project root directory confirmed")
    
    # Step 2: Backup current database
    print_step(2, "Creating database backup...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_{timestamp}.json"
    
    print_warning("This will backup all data to JSON format...")
    response = input("Continue? (y/n): ")
    
    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    # Backup command
    backup_cmd = f"python manage.py dumpdata --natural-foreign --natural-primary --exclude contenttypes --exclude auth.Permission --indent 2 > {backup_file}"
    success, output = run_command(backup_cmd, "Database backup")
    
    if not success:
        print_error("Backup failed. Migration aborted.")
        sys.exit(1)
    
    print_success(f"Backup saved to: {backup_file}")
    
    # Step 3: Check Supabase credentials
    print_step(3, "Checking Supabase credentials...")
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print_warning("DATABASE_URL not found in environment")
        print("\nPlease set your Supabase DATABASE_URL:")
        print("Example: postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres")
        database_url = input("\nEnter DATABASE_URL: ").strip()
        
        if not database_url:
            print_error("DATABASE_URL is required")
            sys.exit(1)
        
        # Set environment variable for this session
        os.environ['DATABASE_URL'] = database_url
    
    if 'supabase.com' in database_url:
        print_success("Supabase connection string detected")
    else:
        print_warning("Connection string doesn't appear to be Supabase")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Step 4: Test connection
    print_step(4, "Testing database connection...")
    
    success, output = run_command("python manage.py check --database default", "Connection test")
    
    if not success:
        print_error("Cannot connect to database. Check your credentials.")
        sys.exit(1)
    
    # Step 5: Run migrations
    print_step(5, "Running migrations on Supabase...")
    
    print_warning("This will create all tables in Supabase database")
    response = input("Continue? (y/n): ")
    
    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)
    
    success, output = run_command("python manage.py migrate", "Database migrations")
    
    if not success:
        print_error("Migrations failed")
        sys.exit(1)
    
    # Step 6: Load data
    print_step(6, "Restoring data to Supabase...")
    
    print_warning(f"This will load data from: {backup_file}")
    response = input("Continue? (y/n): ")
    
    if response.lower() != 'y':
        print("Data restore skipped.")
    else:
        success, output = run_command(f"python manage.py loaddata {backup_file}", "Data restore")
        
        if not success:
            print_error("Data restore failed")
            print_warning("You may need to restore data manually")
        else:
            print_success("Data restored successfully")
    
    # Step 7: Verify migration
    print_step(7, "Verifying migration...")
    
    verify_script = """
from django.contrib.auth.models import User
from accounts.models import Profile, SiteManagerProfile
from site_diary.models import Project, DiaryEntry
from blog.models import BlogPost
from portfolio.models import Project as PortfolioProject

print(f"Users: {User.objects.count()}")
print(f"Profiles: {Profile.objects.count()}")
print(f"Site Managers: {SiteManagerProfile.objects.count()}")
print(f"Site Diary Projects: {Project.objects.count()}")
print(f"Diary Entries: {DiaryEntry.objects.count()}")
print(f"Blog Posts: {BlogPost.objects.count()}")
print(f"Portfolio Projects: {PortfolioProject.objects.count()}")
"""
    
    with open('verify_migration.py', 'w') as f:
        f.write(verify_script)
    
    success, output = run_command("python manage.py shell < verify_migration.py", "Data verification")
    
    if success:
        print("\nData counts:")
        print(output)
    
    # Cleanup
    os.remove('verify_migration.py')
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"{Colors.GREEN}Migration Complete!{Colors.END}")
    print(f"{'='*60}\n")
    
    print("Next steps:")
    print("1. Test your application thoroughly")
    print("2. Verify all features work correctly")
    print("3. Check file uploads and media")
    print("4. Update production environment variables")
    print(f"5. Keep backup file safe: {backup_file}")
    print("\nIf issues occur, restore DATABASE_URL to Render and redeploy.")
    
    print(f"\n{Colors.BLUE}Documentation:{Colors.END} See SUPABASE_MIGRATION_GUIDE.md for details")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Migration cancelled by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

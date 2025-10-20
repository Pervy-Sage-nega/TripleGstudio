from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from accounts.models import Profile, AdminProfile, SiteManagerProfile


class Command(BaseCommand):
    help = 'Clean up orphaned users and profiles'

    def add_arguments(self, parser):
        parser.add_argument('--list-only', action='store_true', help='Only list users, don\'t delete')
        parser.add_argument('--delete-all', action='store_true', help='Delete all non-superuser users')
        parser.add_argument('--delete-inactive', action='store_true', help='Delete only inactive users')
        parser.add_argument('--delete-all-except-superadmin', action='store_true', help='Delete all users except superadmin (keeps only superusers)')
        parser.add_argument('--force-delete', action='store_true', help='Force delete using raw SQL (use with caution)')
        parser.add_argument('--confirm', action='store_true', help='Confirm deletion (required for actual deletion)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== User Cleanup Tool ==='))
        
        # Get all users
        all_users = User.objects.all()
        superusers = all_users.filter(is_superuser=True)
        regular_users = all_users.filter(is_superuser=False)
        
        self.stdout.write(f"Total users in database: {all_users.count()}")
        self.stdout.write(f"Superusers: {superusers.count()}")
        self.stdout.write(f"Regular users: {regular_users.count()}")
        
        # List all users with their details
        self.stdout.write("\n=== All Users ===")
        for user in all_users:
            profile_info = self.get_profile_info(user)
            status = "ACTIVE" if user.is_active else "INACTIVE"
            user_type = "SUPERUSER" if user.is_superuser else "REGULAR"
            
            self.stdout.write(
                f"ID: {user.id} | {user.username} ({user.email}) | "
                f"{status} | {user_type} | {profile_info}"
            )
        
        if options['list_only']:
            return
            
        # Determine what to delete
        users_to_delete = []
        
        if options['delete_all']:
            users_to_delete = regular_users
            action_desc = "all non-superuser users"
        elif options['delete_inactive']:
            users_to_delete = regular_users.filter(is_active=False)
            action_desc = "inactive non-superuser users"
        elif options['delete_all_except_superadmin']:
            users_to_delete = regular_users
            action_desc = "all users except superadmin (keeping only superusers)"
        else:
            self.stdout.write(self.style.WARNING(
                "\nNo deletion action specified. Use --delete-all, --delete-inactive, or --delete-all-except-superadmin"
            ))
            return
            
        if not users_to_delete.exists():
            self.stdout.write(self.style.SUCCESS(f"No users to delete for action: {action_desc}"))
            return
            
        self.stdout.write(f"\n=== Users to be deleted ({action_desc}) ===")
        for user in users_to_delete:
            profile_info = self.get_profile_info(user)
            self.stdout.write(f"- {user.username} ({user.email}) | {profile_info}")
            
        if not options['confirm']:
            self.stdout.write(self.style.WARNING(
                f"\nWould delete {users_to_delete.count()} users. "
                "Add --confirm to actually perform the deletion."
            ))
            return
            
        # Check if force delete is requested
        if options['force_delete']:
            self.stdout.write(self.style.WARNING("⚠️  FORCE DELETE MODE - Using raw SQL"))
            return self.force_delete_users(users_to_delete)
            
        # Perform deletion
        self.stdout.write(f"\nDeleting {users_to_delete.count()} users...")
        
        deleted_count = 0
        for user in users_to_delete:
            # Use individual transactions for each user to prevent rollback cascade
            try:
                with transaction.atomic():
                    username = user.username
                    
                    # Delete associated profiles first
                    Profile.objects.filter(user=user).delete()
                    AdminProfile.objects.filter(user=user).delete()
                    SiteManagerProfile.objects.filter(user=user).delete()
                    
                    # Delete related objects that might cause foreign key issues
                    self.cleanup_user_relations(user)
                    
                    # Delete the user
                    user.delete()
                    deleted_count += 1
                    self.stdout.write(f"✓ Deleted user: {username}")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Failed to delete {user.username}: {e}"))
        self.stdout.write(self.style.SUCCESS(f"\n=== Cleanup Complete ==="))
        self.stdout.write(f"Successfully deleted {deleted_count} users")
        
        # Show final state
        remaining_users = User.objects.all()
        self.stdout.write(f"Remaining users in database: {remaining_users.count()}")

    def force_delete_users(self, users_to_delete):
        """Force delete users using raw SQL to bypass foreign key constraints"""
        from django.db import connection
        
        user_ids = list(users_to_delete.values_list('id', flat=True))
        
        if not user_ids:
            self.stdout.write("No users to delete")
            return
            
        self.stdout.write(f"Force deleting {len(user_ids)} users with IDs: {user_ids}")
        
        with connection.cursor() as cursor:
            try:
                # Delete related records first
                tables_to_clean = [
                    ('accounts_profile', 'user_id'),
                    ('accounts_adminprofile', 'user_id'), 
                    ('accounts_sitemanagerprofile', 'user_id'),
                    ('accounts_onetimepassword', 'user_id'),
                ]
                
                # Try to clean blog tables if they exist
                try:
                    cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'blog_blogpost'")
                    if cursor.fetchone():
                        tables_to_clean.append(('blog_blogpost', 'author_id'))
                except:
                    pass
                    
                try:
                    cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name = 'blog_comment'")
                    if cursor.fetchone():
                        tables_to_clean.append(('blog_comment', 'user_id'))
                except:
                    pass
                
                # Delete from related tables
                for table, column in tables_to_clean:
                    try:
                        placeholders = ','.join(['%s'] * len(user_ids))
                        cursor.execute(f"DELETE FROM {table} WHERE {column} IN ({placeholders})", user_ids)
                        deleted = cursor.rowcount
                        if deleted > 0:
                            self.stdout.write(f"✓ Deleted {deleted} records from {table}")
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Warning: Could not clean {table}: {e}"))
                
                # Finally delete users
                placeholders = ','.join(['%s'] * len(user_ids))
                cursor.execute(f"DELETE FROM auth_user WHERE id IN ({placeholders})", user_ids)
                deleted_users = cursor.rowcount
                
                self.stdout.write(self.style.SUCCESS(f"✓ Force deleted {deleted_users} users"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Force delete failed: {e}"))
                
        # Show final state
        remaining_users = User.objects.all()
        self.stdout.write(f"Remaining users in database: {remaining_users.count()}")

    def cleanup_user_relations(self, user):
        """Clean up user-related objects that might cause foreign key constraints"""
        try:
            # Clean up blog-related objects if they exist
            from django.apps import apps
            
            # Check if blog app models exist and clean them up
            if apps.is_installed('blog'):
                try:
                    BlogPost = apps.get_model('blog', 'BlogPost')
                    BlogPost.objects.filter(author=user).delete()
                except LookupError:
                    pass  # Model doesn't exist
                    
                try:
                    Comment = apps.get_model('blog', 'Comment')
                    Comment.objects.filter(user=user).delete()
                except LookupError:
                    pass  # Model doesn't exist
                    
            # Clean up site_diary related objects if they exist
            if apps.is_installed('site_diary'):
                try:
                    Project = apps.get_model('site_diary', 'Project')
                    Project.objects.filter(project_manager=user).update(project_manager=None)
                    Project.objects.filter(architect=user).update(architect=None)
                except LookupError:
                    pass
                    
                try:
                    DiaryEntry = apps.get_model('site_diary', 'DiaryEntry')
                    DiaryEntry.objects.filter(created_by=user).delete()
                except LookupError:
                    pass
                    
            # Clean up any OTP objects
            try:
                from accounts.models import OneTimePassword
                OneTimePassword.objects.filter(user=user).delete()
            except:
                pass
                
        except Exception as e:
            # If cleanup fails, log it but don't stop the deletion
            self.stdout.write(self.style.WARNING(f"Warning: Could not clean up relations for {user.username}: {e}"))

    def get_profile_info(self, user):
        """Get profile information for a user"""
        profiles = []
        
        if hasattr(user, 'profile'):
            profiles.append(f"Profile({user.profile.role})")
        if hasattr(user, 'adminprofile'):
            profiles.append(f"AdminProfile({user.adminprofile.admin_role})")
        if hasattr(user, 'sitemanagerprofile'):
            profiles.append(f"SiteManagerProfile({user.sitemanagerprofile.approval_status})")
            
        return " | ".join(profiles) if profiles else "NO PROFILE"

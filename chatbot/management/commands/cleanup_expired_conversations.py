from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from chatbot.models import Conversation

class Command(BaseCommand):
    help = 'Clean up expired chatbot conversations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours after which to consider conversations expired (default: 24)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        
        # Calculate cutoff time
        cutoff_time = timezone.now() - timedelta(hours=hours)
        
        # Find expired conversations
        expired_conversations = Conversation.objects.filter(
            last_message_at__lt=cutoff_time,
            status='active'
        )
        
        count = expired_conversations.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would mark {count} conversations as expired'
                )
            )
            for conv in expired_conversations[:10]:  # Show first 10
                self.stdout.write(f'  - Conversation {conv.id} (last activity: {conv.last_message_at})')
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            # Mark as expired instead of deleting
            expired_conversations.update(status='expired')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully marked {count} conversations as expired'
                )
            )
            
        # Also clean up very old expired conversations (delete after 30 days)
        very_old_cutoff = timezone.now() - timedelta(days=30)
        very_old_conversations = Conversation.objects.filter(
            last_message_at__lt=very_old_cutoff,
            status='expired'
        )
        
        old_count = very_old_conversations.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {old_count} very old conversations'
                )
            )
        else:
            very_old_conversations.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {old_count} very old conversations'
                )
            )
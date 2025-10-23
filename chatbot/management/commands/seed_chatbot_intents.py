from django.core.management.base import BaseCommand
from chatbot.models import ChatbotIntent

class Command(BaseCommand):
    help = 'Seed initial chatbot intents'

    def handle(self, *args, **options):
        intents_data = [
            {
                'name': 'greeting',
                'description': 'Greeting messages',
                'keywords': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
                'response_template': 'Hello! Welcome to Triple G BuildHub. How can I assist you today?',
                'priority': 10,
                'requires_auth': False,
            },
            {
                'name': 'project_status',
                'description': 'Project status inquiries',
                'keywords': ['project status', 'milestone', 'progress', 'update', 'how is my project'],
                'response_template': 'Let me check your project status...',
                'priority': 9,
                'requires_auth': True,
            },
            {
                'name': 'support',
                'description': 'Support and human contact requests',
                'keywords': ['talk to someone', 'need help', 'contact support', 'human', 'speak to agent'],
                'response_template': 'I can connect you with our support team. Would you like to leave a message?',
                'priority': 8,
                'requires_auth': False,
            },
            {
                'name': 'appointment',
                'description': 'Appointment scheduling requests',
                'keywords': ['schedule', 'appointment', 'meeting', 'call back', 'book'],
                'response_template': 'I can help you schedule an appointment. Please provide your contact information.',
                'priority': 7,
                'requires_auth': False,
            },
            {
                'name': 'faq',
                'description': 'General questions about Triple G',
                'keywords': ['what is triple g', 'faq', 'question', 'about', 'services'],
                'response_template': 'Triple G BuildHub is a construction management platform. What would you like to know?',
                'priority': 6,
                'requires_auth': False,
            },
            {
                'name': 'navigation',
                'description': 'Navigation and guidance requests',
                'keywords': ['where', 'how do i', 'find', 'locate', 'view', 'navigate'],
                'response_template': 'You can find that in your dashboard. Would you like me to guide you?',
                'priority': 5,
                'requires_auth': False,
            },
        ]

        created_count = 0
        for intent_data in intents_data:
            intent, created = ChatbotIntent.objects.get_or_create(
                name=intent_data['name'],
                defaults=intent_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created intent: {intent.name}")
            else:
                self.stdout.write(f"Intent already exists: {intent.name}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new intents')
        )
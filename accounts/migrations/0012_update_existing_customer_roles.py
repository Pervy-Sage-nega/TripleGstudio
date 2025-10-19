from django.db import migrations

def update_customer_to_client(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    Profile.objects.filter(role='customer').update(role='client')

def reverse_client_to_customer(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    Profile.objects.filter(role='client').update(role='customer')

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_update_customer_to_client'),
    ]

    operations = [
        migrations.RunPython(update_customer_to_client, reverse_client_to_customer),
    ]
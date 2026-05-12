# Generated migration for creating admin superuser

from django.db import migrations
from django.contrib.auth.models import User


def create_superuser(apps, schema_editor):
    """Create a default admin superuser if it doesn't exist."""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@mookh.com',
            password='admin123'
        )


def delete_superuser(apps, schema_editor):
    """Reverse: delete the superuser if it exists."""
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser, delete_superuser),
    ]

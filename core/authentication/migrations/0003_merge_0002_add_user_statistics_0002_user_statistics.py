"""Migration to add user statistics fields to the CustomUser model."""
from django.db import migrations


class Migration(migrations.Migration):
    """
    Migration to merge two parallel migrations that added user statistics.
    
    This migration merges '0002_add_user_statistics' and '0002_user_statistics',
    which were likely created in separate development branches.
    No new operations are performed in this migration.
    """

    dependencies = [
        ('authentication', '0002_add_user_statistics'),
        ('authentication', '0002_user_statistics'),
    ]

    operations = [
    ]

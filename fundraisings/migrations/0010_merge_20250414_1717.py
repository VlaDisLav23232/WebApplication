from django.db import migrations


class Migration(migrations.Migration):
    """
    Merge migration to resolve conflict between
    0002_ensure_default_categories and 0009_alter_fundraising_categories
    """

    dependencies = [
        ('fundraisings', '0002_ensure_default_categories'),
        ('fundraisings', '0009_alter_fundraising_categories'),
    ]

    operations = [
    ]

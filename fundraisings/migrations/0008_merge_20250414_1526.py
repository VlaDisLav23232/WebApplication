from django.db import migrations


class Migration(migrations.Migration):
    """
    Merge migration to resolve conflict
    between 0006_ensure_primary_category and 0007_add_status_field.
    """

    dependencies = [
        ('fundraisings', '0006_ensure_primary_category'),
        ('fundraisings', '0007_add_status_field'),
    ]

    operations = [
    ]

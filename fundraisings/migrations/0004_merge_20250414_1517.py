from django.db import migrations


class Migration(migrations.Migration):
    """
    Merge migration to resolve conflict between
    0003_merge_0002_add_donation_model_0002_donation and add_status_field.
    """

    dependencies = [
        ('fundraisings', '0003_merge_0002_add_donation_model_0002_donation'),
        ('fundraisings', 'add_status_field'),
    ]

    operations = [
    ]

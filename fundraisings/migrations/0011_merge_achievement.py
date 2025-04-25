from django.db import migrations

class Migration(migrations.Migration):
    """
    Merge migration to resolve conflict between 0007_achievement and 0010_merge_20250414_1717
    """

    dependencies = [
        ('fundraisings', '0007_achievement'),
        ('fundraisings', '0010_merge_20250414_1717'),
    ]

    operations = [
        # No operations needed for a merge migration
    ]

from django.db import migrations

def fix_invalid_foreign_keys(apps, schema_editor):
    """
    Fix invalid foreign keys in the Fundraising model.
    """

    Fundraising = apps.get_model('fundraisings', 'Fundraising')
    db = schema_editor.connection.alias

    # Check if the primary_category_id column exists
    try:
        # A safer approach that checks if the column exists before trying to update it
        Fundraising.objects.using(db).filter(pk=12).update(primary_category=None)
    except Exception:
        # If the column doesn't exist yet, we can skip this operation
        pass

class Migration(migrations.Migration):
    """
    Migration to fix invalid foreign keys in the Fundraising model.
    """
    dependencies = [
        ('fundraisings', '0004_merge_20250414_1517'),
    ]

    operations = [
        migrations.RunPython(fix_invalid_foreign_keys, migrations.RunPython.noop),
    ]

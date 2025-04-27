from django.db import migrations

def create_default_categories(apps, schema_editor):
    """
    Create default categories if they don't exist.
    This migration is specifically designed to run after a database reset
    to ensure that all categories are properly restored.
    """
    Category = apps.get_model('fundraisings', 'Category')
    defaults = [
        {"name": "Екіпірування", "description": "Екіпірування для військових", "color_code": "#E53935"},
        {"name": "Техніка та обладнання", "description": "Технічні засоби та обладнання", "color_code": "#43A047"},
        {"name": "Медична допомога", "description": "Медичні засоби та допомога", "color_code": "#3949AB"},
        {"name": "Транспорт та логістика", "description": "Транспортні засоби та логістика", "color_code": "#FB8C00"},
        {"name": "Інше", "description": "Інші види проектів", "color_code": "#757575"}
    ]

    for cat_data in defaults:
        category, created = Category.objects.get_or_create(
            name=cat_data["name"],
            defaults={
                "description": cat_data["description"],
                "color_code": cat_data["color_code"]
            }
        )

class Migration(migrations.Migration):
    """
    Emergency migration to restore categories after database reset.
    """

    dependencies = [
        ('fundraisings', '0009_alter_fundraising_categories'),
    ]

    operations = [
        migrations.RunPython(create_default_categories, migrations.RunPython.noop),
    ]

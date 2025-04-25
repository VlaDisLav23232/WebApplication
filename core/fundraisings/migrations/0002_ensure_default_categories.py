from django.db import migrations

def create_default_categories(apps, schema_editor):
    """
    Create default categories if they don't exist.
    """
    Category = apps.get_model('fundraisings', 'Category')
    defaults = [
        {"name": "Екіпірування", "description":\
        "Екіпірування для військових", "color_code": "#E53935"},
        {"name": "Техніка та обладнання", "description":\
        "Технічні засоби та обладнання", "color_code": "#43A047"},
        {"name": "Медична допомога", "description":\
         "Медичні засоби та допомога", "color_code": "#3949AB"},
        {"name": "Транспорт та логістика", "description":\
        "Транспортні засоби та логістика", "color_code": "#FB8C00"},
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
        if created:
            print(f"Created category: {cat_data['name']}")
        else:
            print(f"Category already exists: {cat_data['name']}")

    print("Default categories have been ensured")

def reverse_func(apps, schema_editor):
    """
    Reverse function for the migration.
    """
    # This function is intentionally left empty.
    # We don't want to remove categories on migration reversal
    pass

class Migration(migrations.Migration):
    """
    Migration to ensure default categories exist in the database.
    """

    dependencies = [
        ('fundraisings', '0001_initial'),  # Update this to match your last migration
    ]

    operations = [
        migrations.RunPython(create_default_categories, reverse_func),
    ]

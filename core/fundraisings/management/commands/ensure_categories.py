from django.core.management.base import BaseCommand
from fundraisings.models import Category

class Command(BaseCommand):
    help = 'Ensures that default categories exist in the database'

    def handle(self, *args, **kwargs):
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
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {cat_data['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Category already exists: {cat_data['name']}"))
        
        self.stdout.write(self.style.SUCCESS("Default categories have been ensured"))

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('fundraisings', '0001_initial'),  # Make sure this is the correct dependency
    ]

    operations = [
        migrations.AddField(
            model_name='fundraising',
            name='status',
            field=models.CharField(
                choices=[
                    ('active', 'Активний'),
                    ('paused', 'Призупинено'),
                    ('completed', 'Завершено'),
                    ('canceled', 'Скасовано')
                ],
                default='active',
                max_length=20
            ),
        ),
    ]

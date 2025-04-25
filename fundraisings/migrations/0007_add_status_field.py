from django.db import migrations, models

class Migration(migrations.Migration):
    """
    Migration to add a status field to the Fundraising model.
    """
    dependencies = [
        ('fundraisings', '0004_merge_20250414_1517'),
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

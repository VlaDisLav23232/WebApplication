# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundraisings', '0002_remove_fundraising_current_sum_category_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundraising',
            name='current_sum',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Зібрана сума (₴)'),
        ),
    ]

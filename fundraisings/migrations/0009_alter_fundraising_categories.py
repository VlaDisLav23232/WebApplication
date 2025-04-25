from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration to alter the categories field in the Fundraising model.
    """

    dependencies = [
        ('fundraisings', '0008_merge_20250414_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundraising',
            name='categories',
            field=models.ManyToManyField(blank=True,\
            related_name='associated_fundraisings', to='fundraisings.category'),
        ),
    ]

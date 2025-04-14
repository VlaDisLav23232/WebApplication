from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('fundraisings', '0005_fix_invalid_primary_category'),
    ]

    operations = [
        # First check if the field exists, if not, create it
        migrations.AddField(
            model_name='fundraising',
            name='primary_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_fundraisings', to='fundraisings.category'),
        ),
    ]

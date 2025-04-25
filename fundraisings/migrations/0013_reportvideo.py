import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration that adds a ReportVideo model to store videos related to reports.
    """

    dependencies = [
        ('fundraisings', '0012_alter_achievement_id_report_reportimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True,\
                        primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='report_videos/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,\
                        related_name='videos', to='fundraisings.report')),
            ],
        ),
    ]

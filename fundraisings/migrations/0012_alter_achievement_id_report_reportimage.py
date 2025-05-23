import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration that adds Report and ReportImage models to the fundraisings app.
    """
    dependencies = [
        ('fundraisings', '0011_merge_achievement'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='id',
            field=models.BigAutoField(auto_created=True,\
            primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,\
                            serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,\
                                    to=settings.AUTH_USER_MODEL)),
                ('fundraising', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,\
                                related_name='report', to='fundraisings.fundraising')),
            ],
        ),
        migrations.CreateModel(
            name='ReportImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True,\
                    primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='report_images/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,\
                    related_name='images', to='fundraisings.report')),
            ],
        ),
    ]

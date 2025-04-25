from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.utils.timezone

class Migration(migrations.Migration):
    """
    Initial migration for the Fundraising app.
    This migration creates the Fundraising and Donation models,
    along with the Category model for categorizing fundraisers.
    """
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('color_code', models.CharField(default='#5D4037', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Fundraising',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('needed_sum', models.DecimalField(decimal_places=2, max_digits=10)),
                ('current_sum', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('active', 'Активний'), ('paused', 'Призупинено'), ('completed', 'Завершено'), ('canceled', 'Скасовано')], default='active', max_length=20)),
                ('main_image', models.ImageField(blank=True, null=True, upload_to='fundraising_images/')),
                ('link_for_money', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('confirm_reporting', models.BooleanField(default=False)),
                ('categories', models.ManyToManyField(blank=True, related_name='fundraisings', to='fundraisings.category')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fundraisings', to=settings.AUTH_USER_MODEL)),
                ('primary_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_fundraisings', to='fundraisings.category')),
            ],
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('anonymous', models.BooleanField(default=False)),
                ('fundraising', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donations', to='fundraisings.fundraising')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='donations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

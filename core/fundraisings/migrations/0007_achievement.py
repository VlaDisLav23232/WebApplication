from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_add_user_statistics'),
        ('fundraisings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('achievement_type', models.CharField(choices=[('fundraising_created', 'Створено зборів'), ('fundraising_completed', 'Завершено зборів'), ('donation_amount', 'Сума донатів'), ('donation_count', 'Кількість донатів'), ('category_completed', 'Категорія завершена')], max_length=50)),
                ('level', models.IntegerField(choices=[(1, 'Бронза'), (2, 'Срібло'), (3, 'Золото')], default=1)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('icon', models.CharField(default='award', max_length=100)),
                ('color', models.CharField(default='#8D6E63', max_length=20)),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('date_earned', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='achievements', to='fundraisings.Category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='authentication.CustomUser')),
            ],
            options={
                'ordering': ['-date_earned'],
                'unique_together': {('user', 'achievement_type', 'level', 'category')},
            },
        ),
    ]

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='total_donations_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Загальна сума донатів'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='created_fundraisings_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Кількість створених зборів'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='completed_fundraisings_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Кількість закритих зборів'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='total_received_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Зібрана сума на збори'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='unique_donators_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Кількість унікальних донаторів'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='supported_fundraisings_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Кількість підтриманих зборів'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='total_donated_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Кількість грошей задоначено'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='largest_donation_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Найбільший донат'),
        ),
    ]

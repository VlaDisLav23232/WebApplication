from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration that adds donation-related fields to the CustomUser model.
    
    This migration adds three fields to track:
    - The largest donation amount made by the user
    - The count of fundraisings supported by the user
    - The total amount donated by the user across all fundraisings
    """

    dependencies = [
        ('authentication', '0005_remove_customuser_banner_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='largest_donation_amount_field',
            field=models.DecimalField(decimal_places=2,
            default=0, max_digits=10, verbose_name='Найбільший донат'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='supported_fundraisings_count_field',
            field=models.PositiveIntegerField(default=0,\
                        verbose_name='Кількість підтриманих зборів'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='total_donated_amount_field',
            field=models.DecimalField(decimal_places=2,\
                    default=0, max_digits=10, verbose_name='Сума зроблених донатів'),
        ),
    ]

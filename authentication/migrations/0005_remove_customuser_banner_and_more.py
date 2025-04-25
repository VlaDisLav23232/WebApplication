from django.db import migrations


class Migration(migrations.Migration):
    """
    Migration that removes the banner field and donation tracking fields from CustomUser.
    
    This removes several fields that were previously added, including the banner image
    and fields related to donation tracking which will be replaced in a later migration.
    """

    dependencies = [
        ('authentication', '0004_customuser_banner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='banner',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='largest_donation_amount',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='supported_fundraisings_count',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='total_donated_amount',
        ),
    ]

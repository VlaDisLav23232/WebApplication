from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migration that adds a banner field to the CustomUser model.
    
    This allows users to set a profile banner image which can be
    displayed at the top of their profile page.
    """

    dependencies = [
        ('authentication', '0003_merge_0002_add_user_statistics_0002_user_statistics'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='banner',
            field=models.ImageField(blank=True, null=True,\
                    upload_to='banners/', verbose_name='Банер профілю'),
        ),
    ]

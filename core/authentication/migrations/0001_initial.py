from django.db import migrations, models
import django.contrib.auth.models
import django.contrib.auth.validators
from django.utils import timezone


class Migration(migrations.Migration):
    """
    Initial migration for the authentication app.
    
    Creates the Category and CustomUser models with all their fields,
    relationships, and permission configurations.
    """

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True,\
                                primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100,\
                                unique=True, verbose_name='Назва категорії')),
                ('description', models.TextField(blank=True,\
                                null=True, verbose_name='Опис категорії')),
                ('icon', models.CharField(blank=True,\
                                max_length=50, null=True, verbose_name='Іконка')),
            ],
            options={
                'verbose_name': 'Категорія',
                'verbose_name_plural': 'Категорії',
            },
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=timezone.now, verbose_name='date joined')),
                ('phone', models.CharField(blank=True, max_length=15, null=True, unique=True, verbose_name='Номер телефону')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Аватар')),
                ('bio', models.TextField(blank=True, max_length=500, null=True, verbose_name='Про себе')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='Дата народження')),
                ('country', models.CharField(blank=True, max_length=100, null=True, verbose_name='Країна')),
                ('region', models.CharField(blank=True, max_length=100, null=True, verbose_name='Область/Регіон')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Населений пункт')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='Адреса')),
                ('notifications_enabled', models.BooleanField(default=True, verbose_name='Сповіщення увімкнені')),
                ('instagram', models.TextField(blank=True, null=True, verbose_name='Instagram')),
                ('facebook', models.TextField(blank=True, null=True, verbose_name='Facebook')),
                ('telegram', models.TextField(blank=True, null=True, verbose_name='Telegram')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата створення')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата оновлення')),
                ('categories', models.ManyToManyField(blank=True, related_name='users', to='authentication.category', verbose_name='Категорії')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Користувач',
                'verbose_name_plural': 'Користувачі',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]

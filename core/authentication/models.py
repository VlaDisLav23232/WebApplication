from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    # Основні контактні дані
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="Номер телефону")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")
    
    # Додаткова інформація
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="Про себе")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")
    
    # Адреса
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Країна")
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Область/Регіон")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Населений пункт")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адреса")
    # Видалено postal_code
    
    # Налаштування
    notifications_enabled = models.BooleanField(default=True, verbose_name="Сповіщення увімкнені")
    
    # Соціальні мережі
    instagram = models.CharField(max_length=100, blank=True, null=True, verbose_name="Instagram")
    facebook = models.CharField(max_length=100, blank=True, null=True, verbose_name="Facebook")
    telegram = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telegram")
    
    # Метадані
    created_at = models.DateTimeField(auto_now_add=True,  null=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True,  null=True, verbose_name="Дата оновлення")
    
    # Для відстеження категорій користувача
    # Це поле можна використовувати, якщо у вас є вибір категорій
    categories = models.ManyToManyField(
        'Category', 
        related_name='users', 
        blank=True, 
        verbose_name="Категорії"
    )
    
    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"
    
    def __str__(self):
        return str(self.username)
    
    def get_full_name(self):
        """
        Повертає повне ім'я користувача (ім'я та прізвище).
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()


class Category(models.Model):
    """
    Модель для категорій інтересів користувачів
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва категорії")
    description = models.TextField(blank=True, null=True, verbose_name="Опис категорії")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="Іконка")
    
    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
    
    def __str__(self):
        return str(self.name)
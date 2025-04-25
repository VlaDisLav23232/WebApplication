"""
Authentication models for the Dovir Web Application.

This module defines the custom user model for the authentication
system, including user profile data and statistics.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum, Max
from fundraisings.models import Donation


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Includes additional fields for user profile information, contact details,
    social media links, and statistics related to fundraising activities.
    """
    # Contact information
    phone = models.CharField(max_length=15, unique=True,\
                        null=True, blank=True, verbose_name="Номер телефону")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")

    # Additional information
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="Про себе")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")

    # Address
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Країна")
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name="Область/Регіон")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Населений пункт")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адреса")

    # Settings
    notifications_enabled = models.BooleanField(default=True, verbose_name="Сповіщення увімкнені")

    # Social media
    instagram = models.TextField(blank=True, null=True, verbose_name="Instagram")
    facebook = models.TextField(blank=True, null=True, verbose_name="Facebook")
    telegram = models.TextField(blank=True, null=True, verbose_name="Telegram")

    # User statistics
    total_donations_amount = models.DecimalField(max_digits=10,\
        decimal_places=2, default=0, verbose_name="Загальна сума донатів")
    created_fundraisings_count = models.PositiveIntegerField(default=0,\
        verbose_name="Кількість створених зборів")
    completed_fundraisings_count = models.PositiveIntegerField(default=0,\
        verbose_name="Кількість закритих зборів")
    total_received_amount = models.DecimalField(max_digits=10, decimal_places=2,\
        default=0, verbose_name="Зібрана сума на збори")
    unique_donators_count = models.PositiveIntegerField(default=0,\
        verbose_name="Кількість унікальних донаторів")

    # Supporting fields for properties
    supported_fundraisings_count_field = models.PositiveIntegerField(default=0,
                                           verbose_name="Кількість підтриманих зборів")
    total_donated_amount_field = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                 verbose_name="Сума зроблених донатів")
    largest_donation_amount_field = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                  verbose_name="Найбільший донат")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True,  null=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True,  null=True, verbose_name="Дата оновлення")

    class Meta:
        """Meta class"""
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"

    def __str__(self):
        """Return username as string representation."""
        return str(self.username)

    def get_full_name(self):
        """
        Return user's full name (first name and last name).
        
        Returns:
            str: User's full name
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    @property
    def supported_fundraisings_count(self):
        """
        Count of fundraisings the user has supported (excluding anonymous donations).
        
        Returns:
            int: Number of distinct fundraisings supported
        """
        try:
            return Donation.objects.filter(user=self,\
                    anonymous=False).values('fundraising').distinct().count()
        except:
            return self.supported_fundraisings_count_field

    @supported_fundraisings_count.setter
    def supported_fundraisings_count(self, value):
        """Set supported fundraisings count field."""
        self.supported_fundraisings_count_field = value

    @property
    def total_donated_amount(self):
        """
        Total amount the user has donated (excluding anonymous donations).
        
        Returns:
            Decimal: Total donation amount
        """
        try:
            total = Donation.objects.filter(user=self, anonymous=False).aggregate(Sum('amount'))
            return total['amount__sum'] or 0
        except:
            return self.total_donated_amount_field

    @total_donated_amount.setter
    def total_donated_amount(self, value):
        """Set total donated amount field."""
        self.total_donated_amount_field = value

    @property
    def largest_donation_amount(self):
        """
        Largest single donation made by the user (excluding anonymous donations).
        
        Returns:
            Decimal: Amount of largest donation
        """
        try:
            maximum = Donation.objects.filter(user=self, anonymous=False).aggregate(Max('amount'))
            return maximum['amount__max'] or 0
        except:
            return self.largest_donation_amount_field

    @largest_donation_amount.setter
    def largest_donation_amount(self, value):
        """Set largest donation amount field."""
        self.largest_donation_amount_field = value

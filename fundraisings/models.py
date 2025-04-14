from django.db import models
from core.authentication.models import CustomUser
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color_code = models.CharField(max_length=10, default="#5D4037")
    
    def __str__(self):
        return self.name

class Fundraising(models.Model):
    STATUS_CHOICES = (
        ('active', 'Активний'),
        ('paused', 'Призупинено'),
        ('completed', 'Завершено'),
        ('canceled', 'Скасовано'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='fundraisings')
    needed_sum = models.DecimalField(max_digits=10, decimal_places=2)
    current_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    main_image = models.ImageField(upload_to='fundraising_images/', null=True, blank=True)
    link_for_money = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirm_reporting = models.BooleanField(default=False)
    
    # Primary category for the fundraising
    primary_category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='primary_fundraisings'
    )
    
    # Additional categories
    categories = models.ManyToManyField(
        Category, 
        related_name='fundraisings', 
        blank=True
    )
    
    @property
    def progress_percentage(self):
        if self.needed_sum == 0:
            return 0
        return min(int((self.current_sum / self.needed_sum) * 100), 100)
    
    def __str__(self):
        return self.title

class Donation(models.Model):
    fundraising = models.ForeignKey(Fundraising, on_delete=models.CASCADE, related_name='donations')
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)
    anonymous = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Donation of {self.amount} to {self.fundraising.title}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Update the fundraising's current sum
            self.fundraising.current_sum += self.amount
            self.fundraising.save()

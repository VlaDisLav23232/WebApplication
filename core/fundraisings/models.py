from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color_code = models.CharField(max_length=10, default="#5D4037")
    
    @classmethod
    def get_default_categories(cls):
        """
        Returns all categories, without creating them during app initialization.
        Default categories should be created via migrations.
        """
        return cls.objects.all()
    
    @classmethod
    def get_default_category(cls):
        """Returns the 'Інше' category or first available category"""
        try:
            return cls.objects.filter(name="Інше").first() or cls.objects.first()
        except:
            # Create a fallback only if absolutely needed
            return cls.objects.create(
                name="Інше",
                description="Інші види проектів",
                color_code="#757575"
            )
    
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
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fundraisings')
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
        'Category', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='primary_fundraisings'  # Changed from 'fundraisings'
    )
    
    # Additional categories
    categories = models.ManyToManyField(
        Category, 
        related_name='associated_fundraisings',  # Changed from default which would be 'fundraisings'
        blank=True
    )
    
    @property
    def progress_percentage(self):
        if float(self.needed_sum) == 0:
            return 0
        return min(round((float(self.current_sum) / float(self.needed_sum)) * 100), 100)
    
    def add_donation(self, amount):
        """Add donation amount to current sum and return updated values"""
        if isinstance(amount, float):
            amount_decimal = Decimal(str(amount))
        else:
            amount_decimal = amount
            
        # Use update method to avoid race conditions
        from django.db.models import F
        Fundraising.objects.filter(pk=self.pk).update(
            current_sum=F('current_sum') + amount_decimal
        )
        # Refresh the object to get updated values
        self.refresh_from_db()
        
        return {
            'current_sum': self.current_sum,
            'progress_percentage': self.progress_percentage
        }
    
    def __str__(self):
        return self.title

class Donation(models.Model):
    fundraising = models.ForeignKey(Fundraising, on_delete=models.CASCADE, related_name='donations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
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
            # Use the add_donation method from Fundraising to update current_sum
            self.fundraising.add_donation(self.amount)
            
            # Update user statistics when donation is made
            try:
                # Try to import here to avoid circular imports
                from authentication.views import update_user_statistics
                if self.user:
                    update_user_statistics(self.user)
                update_user_statistics(self.fundraising.creator)
            except (ImportError, Exception):
                pass  # Skip if function not available

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

class Achievement(models.Model):
    """Model to store user achievements"""
    ACHIEVEMENT_TYPES = (
        ('fundraising_created', 'Створено зборів'),
        ('fundraising_completed', 'Завершено зборів'),
        ('donation_amount', 'Сума донатів'),
        ('donation_count', 'Кількість донатів'),
        ('category_completed', 'Категорія завершена'),
    )
    
    ACHIEVEMENT_LEVELS = (
        (1, 'Бронза'),
        (2, 'Срібло'),
        (3, 'Золото'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    level = models.IntegerField(choices=ACHIEVEMENT_LEVELS, default=1)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='achievements')
    icon = models.CharField(max_length=100, default='award')  # FontAwesome icon name
    color = models.CharField(max_length=20, default='#8D6E63')
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Value/threshold reached
    date_earned = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement_type', 'level', 'category')
        ordering = ['-date_earned']
    
    def __str__(self):
        return f"{self.title} - {self.get_level_display()} ({self.user.username})"
    
    @staticmethod
    def check_achievements(user):
        """Check and award achievements for a user"""
        from django.db.models import Sum, Count
        
        # Fundraising creation achievements
        fundraising_count = Fundraising.objects.filter(creator=user).count()
        
        if fundraising_count >= 1:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='fundraising_created',
                level=1,
                defaults={
                    'title': 'Перший крок',
                    'description': 'Створив перший збір',
                    'icon': 'flag',
                    'color': '#8D6E63',
                    'value': 1
                }
            )
        
        if fundraising_count >= 5:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='fundraising_created',
                level=2,
                defaults={
                    'title': 'Організатор',
                    'description': 'Створив 5 зборів',
                    'icon': 'flag',
                    'color': '#9E9E9E',
                    'value': 5
                }
            )
        
        if fundraising_count >= 10:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='fundraising_created',
                level=3,
                defaults={
                    'title': 'Волонтер',
                    'description': 'Створив 10 зборів',
                    'icon': 'flag',
                    'color': '#FFC107',
                    'value': 10
                }
            )
        
        # Completed fundraisings
        completed_count = Fundraising.objects.filter(creator=user, status='completed').count()
        
        if completed_count >= 1:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='fundraising_completed',
                level=1,
                defaults={
                    'title': 'Завершив справу',
                    'description': 'Успішно завершив перший збір',
                    'icon': 'check-circle',
                    'color': '#8D6E63',
                    'value': 1
                }
            )
        
        if completed_count >= 3:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='fundraising_completed',
                level=2,
                defaults={
                    'title': 'Досвідчений',
                    'description': 'Успішно завершив 3 збори',
                    'icon': 'check-circle',
                    'color': '#9E9E9E',
                    'value': 3
                }
            )
        
        if completed_count >= 5:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='fundraising_completed',
                level=3,
                defaults={
                    'title': 'Майстер зборів',
                    'description': 'Успішно завершив 5 зборів',
                    'icon': 'check-circle',
                    'color': '#FFC107',
                    'value': 5
                }
            )
        
        # Donation amount
        donation_sum = Donation.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
        
        if donation_sum >= 1000:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='donation_amount',
                level=1,
                defaults={
                    'title': 'Щедрий донатор',
                    'description': 'Зробив донатів на 1 000 ₴',
                    'icon': 'hand-holding-heart',
                    'color': '#8D6E63',
                    'value': 1000
                }
            )
        
        if donation_sum >= 5000:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='donation_amount',
                level=2,
                defaults={
                    'title': 'Меценат',
                    'description': 'Зробив донатів на 5 000 ₴',
                    'icon': 'hand-holding-heart',
                    'color': '#9E9E9E',
                    'value': 5000
                }
            )
        
        if donation_sum >= 10000:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='donation_amount',
                level=3,
                defaults={
                    'title': 'Філантроп',
                    'description': 'Зробив донатів на 10 000 ₴',
                    'icon': 'hand-holding-heart',
                    'color': '#FFC107',
                    'value': 10000
                }
            )
        
        # Category-specific completed fundraisings
        categories = Category.objects.exclude(name="Інше")
        
        for category in categories:
            category_completed = Fundraising.objects.filter(
                creator=user, 
                status='completed',
                categories=category
            ).count()
            
            if category_completed >= 1:
                icon_map = {
                    'Екіпірування': 'shield-alt',
                    'Техніка та обладнання': 'laptop',
                    'Медична допомога': 'medkit',
                    'Транспорт та логістика': 'truck',
                }
                
                achievement_title = f"Спеціаліст: {category.name}"
                
                Achievement.objects.get_or_create(
                    user=user,
                    achievement_type='category_completed',
                    level=1,
                    category=category,
                    defaults={
                        'title': achievement_title,
                        'description': f'Завершив збір у категорії "{category.name}"',
                        'icon': icon_map.get(category.name, 'star'),
                        'color': category.color_code,
                        'value': 1
                    }
                )
            
            if category_completed >= 3:
                Achievement.objects.get_or_create(
                    user=user,
                    achievement_type='category_completed',
                    level=2,
                    category=category,
                    defaults={
                        'title': f"Експерт: {category.name}",
                        'description': f'Завершив 3 збори у категорії "{category.name}"',
                        'icon': icon_map.get(category.name, 'star'),
                        'color': category.color_code,
                        'value': 3
                    }
                )
        
        # Number of donations - updated descriptions
        donation_count = Donation.objects.filter(user=user).count()
        
        if donation_count >= 5:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='donation_count',
                level=1,
                defaults={
                    'title': 'Підтримка',
                    'description': 'Зробив 5 донатів',
                    'icon': 'heart',
                    'color': '#8D6E63',
                    'value': 5
                }
            )
        
        if donation_count >= 15:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='donation_count',
                level=2,
                defaults={
                    'title': 'Постійний донатор',
                    'description': 'Зробив 15 донатів',
                    'icon': 'heart',
                    'color': '#9E9E9E',
                    'value': 15
                }
            )
        
        if donation_count >= 30:
            Achievement.objects.get_or_create(
                user=user,
                achievement_type='donation_count',
                level=3,
                defaults={
                    'title': 'Надійна підтримка',
                    'description': 'Зробив 30 донатів',
                    'icon': 'heart',
                    'color': '#FFC107',
                    'value': 30
                }
            )
        
        return Achievement.objects.filter(user=user).order_by('-level', '-date_earned')

class Report(models.Model):
    """Model for fundraising reports"""
    fundraising = models.OneToOneField(Fundraising, on_delete=models.CASCADE, related_name='report')
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report for {self.fundraising.title}"

class ReportImage(models.Model):
    """Model for report images"""
    report = models.ForeignKey(Report, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='report_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.report.title}"

class ReportVideo(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='report_videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for report {self.report.id}"

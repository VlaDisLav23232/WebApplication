from django.db import models
from authentication.models import CustomUser
from django.urls import reverse

class Fundraising(models.Model):
    title = models.CharField(max_length=255, verbose_name='Title')
    categories = models.ManyToManyField('Category', related_name='fundraisings')
    description = models.TextField(max_length=2000, verbose_name='Description')
    main_image = models.ImageField(
        upload_to='fundraising_images/',
        verbose_name="Зображення кампанії"
    )
    needed_sum = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цільова сума (₴)')
    start_date = models.DateField(verbose_name='Дата початку')
    end_date = models.DateField(verbose_name='Дата завершення')
    link_for_money = models.TextField(max_length=2000, verbose_name='Реквізити для переказу', default='Реквізити будуть додані пізніше', blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="fundraisings")
    report = models.TextField(
        max_length=5000,
        blank=True,
        null=True,
        verbose_name="Звіт по завершенню збору"
    )
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('donate', kwargs={'pk': self.pk})

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

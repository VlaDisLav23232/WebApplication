from django.contrib import admin
from .models import Fundraising, Category, Donation

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color_code')
    search_fields = ('name', 'description')
    readonly_fields = ('id',) # Make ID visible but readonly

@admin.register(Fundraising)
class FundraisingAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'needed_sum', 'current_sum', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'primary_category')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('fundraising', 'user', 'amount', 'date', 'anonymous')
    list_filter = ('anonymous', 'date')
    search_fields = ('message',)

"""
Admin configuration for the authentication app in the Dovir Web Application.

This module configures the Django admin interface for managing user accounts,
customizing the admin forms and fields displayed.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser model.
    
    Extends the default UserAdmin to include additional custom fields.
    """
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткові поля', {'fields': ('phone',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Додаткові поля', {'fields': ('phone',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

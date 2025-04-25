"""
Authentication app configuration for the Dovir Web Application.

This module configures the Django app for authentication functionality,
setting the application name and default field types.
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration class for the authentication app.
    
    Defines app name and database field configuration.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'

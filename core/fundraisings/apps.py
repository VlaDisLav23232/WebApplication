from django.apps import AppConfig

class FundraisingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fundraisings'

    def ready(self):
        """
        Remove any database access from here to avoid warnings.
        Default categories should be handled by migrations.
        """
        pass

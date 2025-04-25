from django.apps import AppConfig

class FundraisingsConfig(AppConfig):
    """
    Configuration for the Fundraisings app.
    This class is used to set up the app's name and default auto field.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fundraisings'

    def ready(self):
        """
        Remove any database access from here to avoid warnings.
        Default categories should be handled by migrations.
        """
        pass

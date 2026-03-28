from django.apps import AppConfig


class AgroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agro'
    verbose_name = '🌿 E-Shelle Agro'

    def ready(self):
        pass

from django.apps import AppConfig


class RestoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resto"
    verbose_name = "E-Shelle Resto"

    def ready(self):
        import resto.signals  # noqa

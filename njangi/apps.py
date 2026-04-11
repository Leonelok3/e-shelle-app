from django.apps import AppConfig


class NjangiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "njangi"
    verbose_name = "Njangi+"

    def ready(self):
        import njangi.signals  # noqa

from django.apps import AppConfig


class AdgenConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "adgen"
    verbose_name = "AdGen — Générateur de pubs IA"

    def ready(self):
        import adgen.signals  # noqa

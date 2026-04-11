from django.apps import AppConfig


class ImmobilierCamerounConfig(AppConfig):
    name            = "immobilier_cameroun"
    verbose_name    = "Immobilier Cameroun"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import immobilier_cameroun.signals  # noqa: F401

from django.apps import AppConfig


class AnnoncesCamConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "annonces_cam"
    verbose_name = "Annonces Cam"

    def ready(self):
        import annonces_cam.signals  # noqa

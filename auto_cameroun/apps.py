from django.apps import AppConfig


class AutoCamerounConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auto_cameroun"
    verbose_name = "Auto Cameroun"

    def ready(self):
        import auto_cameroun.signals  # noqa

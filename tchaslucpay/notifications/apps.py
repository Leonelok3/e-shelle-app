from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tchaslucpay.notifications"
    label = "tchaslucpay_notifications"
    verbose_name = "Tchaslucpay - notifications"

    def ready(self):
        from . import signals  # noqa: F401


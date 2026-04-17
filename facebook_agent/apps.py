from django.apps import AppConfig


class FacebookAgentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "facebook_agent"
    verbose_name = "Agent Facebook IA"

    def ready(self):
        pass

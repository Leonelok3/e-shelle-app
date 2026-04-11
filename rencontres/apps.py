from django.apps import AppConfig


class RencontresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rencontres'
    verbose_name = 'E-Shelle Love — Rencontres'

    def ready(self):
        import rencontres.signals  # noqa

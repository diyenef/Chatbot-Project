from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core (chat)'

    def ready(self):
        # Import signals to ensure UserProfile is created for each new User
        try:
            import core.signals  # noqa: F401
        except Exception:
            pass

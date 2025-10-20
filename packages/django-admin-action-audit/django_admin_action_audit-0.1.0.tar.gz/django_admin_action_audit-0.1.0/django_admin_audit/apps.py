from django.apps import AppConfig


class DjangoAdminAuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_admin_audit"
    verbose_name = "Django Admin Audit"

    def ready(self):
        # Import signal handlers so they are registered when the app loads.
        from . import signals  # noqa: F401
        from .snapshots import connect_signals

        connect_signals()

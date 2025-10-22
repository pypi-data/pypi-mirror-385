from django.apps import AppConfig


class LeadCaptureConfig(AppConfig):
    """Django app configuration for Lead Capture."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_lead_capture"
    verbose_name = "Lead Capture"

    def ready(self):
        """Import checks when app is ready."""
        from . import checks  # noqa: F401

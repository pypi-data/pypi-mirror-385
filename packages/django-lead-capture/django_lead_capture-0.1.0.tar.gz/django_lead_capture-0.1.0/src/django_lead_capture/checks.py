"""Django system checks for Lead Capture configuration."""

from django.core.checks import Warning, register


@register()
def check_lead_capture_config(app_configs, **kwargs):
    """Check if Lead Capture is properly configured.

    Verifies that an API key is configured for AI-powered campaign generation.
    This is a non-blocking warning - the app will still function without an API key,
    but the AI campaign wizard will not work.

    Returns:
        list: List of Django Warning objects if configuration is incomplete

    """
    from .models import LeadCaptureConfiguration

    warnings = []

    try:
        config = LeadCaptureConfiguration.get_solo()

        if not config.api_key:
            warnings.append(
                Warning(
                    "Lead Capture API key not configured",
                    hint=(
                        "Configure your LLM API key in Django Admin: "
                        "Lead Capture Configuration. AI-powered campaign "
                        "generation will not work until configured."
                    ),
                    id="django_lead_capture.W001",
                )
            )
    except Exception:  # noqa: S110
        # Database not ready yet (initial migration) or table doesn't exist
        # This is fine - checks run before migrations
        pass

    return warnings

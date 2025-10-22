import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from solo.admin import SingletonModelAdmin

from .models import ComingSoonCampaign, Lead, LeadCaptureConfiguration


def export_leads_csv(modeladmin, request, queryset):  # noqa: ARG001
    """Export selected leads to CSV."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="leads.csv"'

    writer = csv.writer(response)
    writer.writerow(["Email", "Campaign", "Source", "Created", "Verified", "IP Address"])

    for lead in queryset:
        writer.writerow(
            [
                lead.email,
                lead.campaign.title,
                lead.source,
                lead.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Yes" if lead.email_verified else "No",
                lead.ip_address or "Unknown",
            ]
        )

    return response


export_leads_csv.short_description = "Export selected leads to CSV"


@admin.register(ComingSoonCampaign)
class ComingSoonCampaignAdmin(admin.ModelAdmin):
    """Admin interface for ComingSoonCampaign."""

    list_display = [
        "title",
        "slug",
        "is_active",
        "page_views",
        "lead_count",
        "conversion_rate_display",
        "created_at",
        "preview_link",
    ]
    list_filter = ["is_active", "template_type", "created_at"]
    search_fields = ["title", "slug", "headline"]
    readonly_fields = ["slug", "page_views", "created_at", "updated_at", "lead_count", "conversion_rate"]

    fieldsets = (
        ("Basic Information", {"fields": ("title", "slug", "is_active", "template_type")}),
        (
            "Content",
            {
                "fields": (
                    "headline",
                    "subheadline",
                    "value_proposition",
                    "benefits",
                    "cta_button_text",
                    "thank_you_message",
                )
            },
        ),
        ("Configuration", {"fields": ("launch_date", "show_countdown", "show_social_proof")}),
        ("SEO", {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
        (
            "Analytics",
            {
                "fields": ("page_views", "lead_count", "conversion_rate", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
        ("Questionnaire Data", {"fields": ("questionnaire_data",), "classes": ("collapse",)}),
    )

    def lead_count(self, obj):
        """Display lead count."""
        return obj.leads.count()

    lead_count.short_description = "Total Leads"

    def conversion_rate_display(self, obj):
        """Display conversion rate with color coding."""
        rate = obj.conversion_rate
        if rate >= 20:
            color = "green"
        elif rate >= 10:
            color = "orange"
        else:
            color = "red"

        return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)

    conversion_rate_display.short_description = "Conversion Rate"

    def preview_link(self, obj):
        """Display preview link."""
        if obj.slug:
            url = reverse("lead_capture:campaign_preview", kwargs={"slug": obj.slug})
            return format_html('<a href="{}" target="_blank">Preview</a>', url)
        return "-"

    preview_link.short_description = "Preview"

    def conversion_rate(self, obj):
        """Display conversion rate."""
        return f"{obj.conversion_rate:.1f}%"

    conversion_rate.short_description = "Conversion Rate"


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    """Admin interface for Lead."""

    list_display = ["email", "campaign", "source", "email_verified", "created_at", "ip_address_short"]
    list_filter = ["email_verified", "campaign", "source", "created_at"]
    search_fields = ["email", "campaign__title"]
    readonly_fields = ["verification_token", "created_at", "verified_at", "user_agent"]
    actions = [export_leads_csv]

    fieldsets = (
        ("Lead Information", {"fields": ("email", "campaign", "email_verified", "verified_at")}),
        ("Metadata", {"fields": ("source", "referrer_url", "ip_address", "user_agent"), "classes": ("collapse",)}),
        ("Verification", {"fields": ("verification_token",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def ip_address_short(self, obj):
        """Display shortened IP address."""
        if obj.ip_address:
            return obj.ip_address[:15] + "..." if len(obj.ip_address) > 15 else obj.ip_address
        return "Unknown"

    ip_address_short.short_description = "IP Address"

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related("campaign")


@admin.register(LeadCaptureConfiguration)
class LeadCaptureConfigurationAdmin(SingletonModelAdmin):
    """Admin interface for Lead Capture Configuration singleton."""

    fieldsets = (
        (
            "LiteLLM Configuration",
            {
                "fields": ("api_key", "model_name", "api_endpoint"),
                "description": (
                    "Configure your LLM provider for AI-powered campaign generation. "
                    "The API key is required for the campaign wizard to work."
                ),
            }
        ),
    )

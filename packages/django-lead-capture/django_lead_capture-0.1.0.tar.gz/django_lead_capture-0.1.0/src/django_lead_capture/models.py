import secrets

import solo.models
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ComingSoonCampaign(models.Model):
    """Campaign model for coming soon / lead capture pages."""

    TEMPLATE_CHOICES = [
        ("minimal", "Minimal Coming Soon"),
        ("detailed", "Detailed Product Launch"),
    ]

    # Basic Info
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    title = models.CharField(max_length=200, help_text="Internal reference name")

    # AI Generation Fields
    questionnaire_data = models.JSONField(default=dict, blank=True, help_text="Stores answers from setup wizard")

    # Generated Content Fields
    headline = models.CharField(max_length=200, blank=True, default="")
    subheadline = models.TextField(blank=True, default="")
    value_proposition = models.TextField(blank=True, default="")
    benefits = models.JSONField(default=list, blank=True, help_text="List of 3-5 benefit bullet points")
    cta_button_text = models.CharField(
        max_length=50, default="Get Early Access", help_text="Call-to-action button text"
    )
    thank_you_message = models.TextField(
        blank=True,
        default="Thank you! We'll notify you when we launch.",
        help_text="Message shown after email submission",
    )

    # Configuration
    template_type = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default="minimal")
    launch_date = models.DateTimeField(blank=True, null=True, help_text="Optional launch date for countdown timer")
    show_countdown = models.BooleanField(default=True, help_text="Display countdown timer if launch_date is set")
    show_social_proof = models.BooleanField(default=True, help_text="Show lead count as social proof")

    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True, default="")
    meta_description = models.CharField(max_length=160, blank=True, default="")

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Analytics
    page_views = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Coming Soon Campaign"
        verbose_name_plural = "Coming Soon Campaigns"

    def __str__(self):  # noqa: D105
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while ComingSoonCampaign.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get the public URL for this campaign.

        Returns:
            str: Public campaign URL for lead capture

        """
        return reverse("lead_capture:campaign_detail", kwargs={"slug": self.slug})

    @property
    def conversion_count(self):
        """Return number of leads collected.

        Returns:
            int: Total number of email leads captured for this campaign

        """
        return self.leads.count()

    @property
    def conversion_rate(self):
        """Calculate conversion rate percentage.

        Computes the percentage of page visitors who submitted their email.
        Handles division by zero gracefully.

        Returns:
            float: Conversion rate as percentage (0.00 to 100.00)

        """
        if self.page_views == 0:
            return 0
        return round((self.conversion_count / self.page_views) * 100, 2)


class Lead(models.Model):
    """Lead model for capturing email addresses."""

    email = models.EmailField()
    campaign = models.ForeignKey(ComingSoonCampaign, on_delete=models.CASCADE, related_name="leads")

    # Metadata
    source = models.CharField(
        max_length=50, blank=True, default="", help_text="Traffic source (organic, twitter, facebook, etc.)"
    )
    referrer_url = models.URLField(blank=True, default="")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, default="")

    # Email verification
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, default="")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ["email", "campaign"]
        ordering = ["-created_at"]
        verbose_name = "Lead"
        verbose_name_plural = "Leads"

    def __str__(self):  # noqa: D105
        return f"{self.email} - {self.campaign.title}"

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def get_verification_url(self):
        """Get email verification URL.

        Generates a secure URL for email verification using the lead's unique token.
        Used in welcome emails to verify email addresses.

        Returns:
            str: Verification URL path (relative, not absolute)

        """
        return reverse("lead_capture:verify_email", kwargs={"token": self.verification_token})


class LeadCaptureConfiguration(solo.models.SingletonModel):
    """Configuration for Lead Capture campaigns."""

    api_key = models.CharField(
        max_length=500,
        blank=True,
        help_text="LLM API key (required for AI-powered campaign generation)"
    )

    model_name = models.CharField(
        max_length=200,
        default='gpt-4o-mini',
        help_text="LiteLLM model identifier (e.g., gpt-4, claude-3-sonnet-20240229)"
    )

    api_endpoint = models.URLField(
        blank=True,
        default='',
        help_text="Custom API endpoint (optional). Leave blank for provider defaults."
    )

    class Meta:
        verbose_name = "Lead Capture Configuration"

    def __str__(self):
        """Return configuration name."""
        return "Lead Capture Configuration"

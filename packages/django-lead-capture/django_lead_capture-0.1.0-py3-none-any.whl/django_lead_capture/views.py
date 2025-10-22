from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .emails import send_welcome_email
from .forms import CampaignEditForm, CampaignWizardForm, LeadCaptureForm
from .models import ComingSoonCampaign, Lead, LeadCaptureConfiguration
from .utils import generate_campaign_copy


@staff_member_required
def campaign_wizard(request):
    """Campaign creation wizard with AI copy generation.

    Staff-only view that guides users through creating a new lead capture campaign.
    Presents a comprehensive questionnaire, generates AI-powered copy, and creates
    a new campaign ready for editing and activation.

    Flow:
        1. Check if LLM models are configured
        2. Present questionnaire form (GET) or process submission (POST)
        3. Generate AI copy from responses using selected LLM model
        4. Create campaign with generated copy
        5. Redirect to edit page for customization

    Args:
        request: Django HttpRequest object

    Returns:
        HttpResponse: Wizard form (GET) or redirect to edit page (POST)

    Raises:
        PermissionDenied: If user is not staff member

    Templates:
        - django_lead_capture/wizard.html: Main questionnaire form
        - django_lead_capture/no_models.html: Error when no API key configured

    """
    # Check if API key is configured
    config = LeadCaptureConfiguration.get_solo()
    if not config.api_key:
        messages.error(
            request,
            "No API key configured. Please configure your LLM API key in Lead Capture Configuration to use the campaign wizard."
        )
        return render(
            request, "django_lead_capture/no_models.html",
            {"admin_url": reverse("admin:django_lead_capture_leadcaptureconfiguration_change")}
        )

    if request.method == "POST":
        form = CampaignWizardForm(request.POST)
        if form.is_valid():
            # Generate AI copy from questionnaire data
            questionnaire_data = form.cleaned_data

            generated_copy = generate_campaign_copy(questionnaire_data)

            # Create campaign with generated copy
            campaign = ComingSoonCampaign.objects.create(
                title=questionnaire_data["project_name"],
                questionnaire_data=questionnaire_data,
                headline=generated_copy.get("headline", ""),
                subheadline=generated_copy.get("subheadline", ""),
                value_proposition=generated_copy.get("value_proposition", ""),
                benefits=generated_copy.get("benefits", []),
                cta_button_text=generated_copy.get("cta_button_text", "Get Early Access"),
                thank_you_message=generated_copy.get(
                    "thank_you_message", "Thank you! We'll notify you when we launch."
                ),
                meta_title=generated_copy.get("meta_title", ""),
                meta_description=generated_copy.get("meta_description", ""),
            )

            messages.success(request, f'Campaign "{campaign.title}" created successfully!')
            return redirect("lead_capture:campaign_edit", slug=campaign.slug)
    else:
        form = CampaignWizardForm()

    return render(request, "django_lead_capture/wizard.html", {"form": form})


@staff_member_required
def campaign_edit(request, slug):
    """Edit campaign content after AI generation.

    Allows staff to customize the AI-generated copy before activating the campaign.
    Provides a form interface for editing all campaign fields including headlines,
    benefits, styling options, and SEO metadata.

    Args:
        request: Django HttpRequest object
        slug: Campaign slug identifier

    Returns:
        HttpResponse: Edit form (GET) or redirect to preview (POST)

    Raises:
        Http404: If campaign with given slug doesn't exist
        PermissionDenied: If user is not staff member

    """
    campaign = get_object_or_404(ComingSoonCampaign, slug=slug)

    if request.method == "POST":
        form = CampaignEditForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, "Campaign updated successfully!")
            return redirect("lead_capture:campaign_preview", slug=campaign.slug)
    else:
        form = CampaignEditForm(instance=campaign)

    return render(request, "django_lead_capture/edit.html", {"form": form, "campaign": campaign})


@staff_member_required
def campaign_preview(request, slug):
    """Preview campaign before making it active.

    Shows how the campaign will appear to visitors without making it live.
    Displays the landing page with current content and provides links to
    edit or activate the campaign.

    Args:
        request: Django HttpRequest object
        slug: Campaign slug identifier

    Returns:
        HttpResponse: Preview page showing campaign as visitors would see it

    Raises:
        Http404: If campaign with given slug doesn't exist
        PermissionDenied: If user is not staff member

    """
    campaign = get_object_or_404(ComingSoonCampaign, slug=slug)

    return render(
        request,
        "django_lead_capture/preview.html",
        {"campaign": campaign, "lead_count": campaign.leads.count(), "is_preview": True},
    )


def campaign_detail(request, slug):
    """Public campaign page for lead capture.

    The main landing page that visitors see when accessing a campaign URL.
    Handles email capture, tracks analytics, and provides the conversion-optimized
    experience for lead generation.

    Features:
        - Automatic page view tracking
        - Email capture with duplicate detection
        - Welcome email automation
        - Referrer and metadata tracking
        - Graceful error handling

    Args:
        request: Django HttpRequest object
        slug: Campaign slug identifier

    Returns:
        HttpResponse: Campaign landing page (GET) or redirect to thank you (POST)

    Raises:
        Http404: If campaign doesn't exist or is not active

    Note:
        Only shows active campaigns. Uses standalone template for optimal conversion.

    """
    campaign = get_object_or_404(ComingSoonCampaign, slug=slug, is_active=True)

    # Track page view
    campaign.page_views += 1
    campaign.save(update_fields=["page_views"])

    if request.method == "POST":
        form = LeadCaptureForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.campaign = campaign

            # Add metadata
            lead.referrer_url = request.META.get("HTTP_REFERER", "")
            lead.ip_address = get_client_ip(request)
            lead.user_agent = request.META.get("HTTP_USER_AGENT", "")

            # Try to save, handle duplicates gracefully
            try:
                lead.save()
                # Send welcome email
                send_welcome_email(lead)
                messages.success(request, campaign.thank_you_message)
                return redirect("lead_capture:thank_you", slug=slug)
            except Exception:
                # Email already exists for this campaign
                messages.info(request, "You're already on our list! We'll be in touch soon.")
                return redirect("lead_capture:thank_you", slug=slug)
    else:
        form = LeadCaptureForm()

    return render(
        request,
        "django_lead_capture/campaign.html",
        {
            "campaign": campaign,
            "form": form,
            "lead_count": campaign.leads.count(),
        },
    )


def thank_you(request, slug):
    """Thank you page after email submission."""
    campaign = get_object_or_404(ComingSoonCampaign, slug=slug, is_active=True)

    return render(
        request,
        "django_lead_capture/thank_you.html",
        {
            "campaign": campaign,
            "lead_count": campaign.leads.count(),
        },
    )


def verify_email(request, token):
    """Email verification endpoint."""
    try:
        lead = Lead.objects.get(verification_token=token, email_verified=False)
        lead.email_verified = True
        lead.verified_at = timezone.now()
        lead.save()

        messages.success(request, "Email verified successfully!")
        return redirect("lead_capture:campaign_detail", slug=lead.campaign.slug)
    except Lead.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect("home")


@staff_member_required
def campaign_list(request):
    """List all campaigns with analytics."""
    campaigns = ComingSoonCampaign.objects.all()

    return render(request, "django_lead_capture/list.html", {"campaigns": campaigns})


@staff_member_required
def campaign_analytics(request, slug):
    """Detailed analytics for a campaign."""
    campaign = get_object_or_404(ComingSoonCampaign, slug=slug)
    leads = campaign.leads.order_by("-created_at")

    return render(
        request,
        "django_lead_capture/analytics.html",
        {
            "campaign": campaign,
            "leads": leads,
            "total_leads": leads.count(),
            "verified_leads": leads.filter(email_verified=True).count(),
        },
    )


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")

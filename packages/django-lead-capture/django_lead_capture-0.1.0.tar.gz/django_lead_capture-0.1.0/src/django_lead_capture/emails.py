"""Email utilities for lead capture campaigns."""
# ruff: noqa: S112

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Lead


def send_welcome_email(lead: Lead) -> bool:
    """Send welcome email to new lead.

    Args:
        lead: The Lead instance to send email to

    Returns:
        bool: True if email sent successfully, False otherwise

    """
    try:
        campaign = lead.campaign

        # Build email context
        context = {
            "lead": lead,
            "campaign": campaign,
            "verification_url": lead.get_verification_url(),
            "campaign_url": campaign.get_absolute_url(),
        }

        # Render email template
        html_message = render_to_string("lead_capture/emails/welcome.html", context)
        plain_message = strip_tags(html_message)

        # Email subject
        subject = f"Welcome to {campaign.title}!"

        # Send email
        sent = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[lead.email],
            html_message=html_message,
            fail_silently=False,
        )

        return sent == 1

    except Exception:
        # Log error in production
        # Log error in production - replace with proper logging
        # print(f"Error sending welcome email to {lead.email}: {e}")
        return False


def send_launch_notification(campaign, custom_message=None) -> int:
    """Send launch notification to all leads in a campaign.

    Args:
        campaign: The ComingSoonCampaign instance
        custom_message: Optional custom message to include

    Returns:
        int: Number of emails sent successfully

    """
    leads = campaign.leads.filter(email_verified=True)
    sent_count = 0

    for lead in leads:
        try:
            context = {
                "lead": lead,
                "campaign": campaign,
                "custom_message": custom_message,
                "campaign_url": campaign.get_absolute_url(),
            }

            html_message = render_to_string("lead_capture/emails/launch_notification.html", context)
            plain_message = strip_tags(html_message)

            subject = f"🚀 {campaign.title} is now live!"

            sent = send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lead.email],
                html_message=html_message,
                fail_silently=True,  # Don't fail entire batch if one fails
            )

            if sent == 1:
                sent_count += 1

        except Exception:  # nosec B112
            # Log error in production - replace with proper logging
            # print(f"Error sending launch notification to {lead.email}: {e}")
            continue

    return sent_count


def send_campaign_update(campaign, subject_line, message_content) -> int:
    """Send update email to all verified leads in a campaign.

    Args:
        campaign: The ComingSoonCampaign instance
        subject_line: Email subject
        message_content: Email message content

    Returns:
        int: Number of emails sent successfully

    """
    leads = campaign.leads.filter(email_verified=True)
    sent_count = 0

    for lead in leads:
        try:
            context = {
                "lead": lead,
                "campaign": campaign,
                "message_content": message_content,
                "campaign_url": campaign.get_absolute_url(),
            }

            html_message = render_to_string("lead_capture/emails/campaign_update.html", context)
            plain_message = strip_tags(html_message)

            sent = send_mail(
                subject=subject_line,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[lead.email],
                html_message=html_message,
                fail_silently=True,
            )

            if sent == 1:
                sent_count += 1

        except Exception:  # nosec B112
            # Log error in production - replace with proper logging
            # print(f"Error sending update to {lead.email}: {e}")
            continue

    return sent_count

from django.urls import path

from . import views

app_name = "lead_capture"

urlpatterns = [
    # Staff-only views
    path("lead-capture/wizard/", views.campaign_wizard, name="campaign_wizard"),
    path("lead-capture/campaigns/", views.campaign_list, name="campaign_list"),
    path("lead-capture/campaigns/<slug:slug>/edit/", views.campaign_edit, name="campaign_edit"),
    path("lead-capture/campaigns/<slug:slug>/preview/", views.campaign_preview, name="campaign_preview"),
    path("lead-capture/campaigns/<slug:slug>/analytics/", views.campaign_analytics, name="campaign_analytics"),
    # Public views
    path("launch/<slug:slug>/", views.campaign_detail, name="campaign_detail"),
    path("launch/<slug:slug>/thank-you/", views.thank_you, name="thank_you"),
    path("verify/<str:token>/", views.verify_email, name="verify_email"),
]

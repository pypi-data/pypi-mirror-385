from django import forms

from .models import ComingSoonCampaign, Lead


class CampaignWizardForm(forms.Form):
    """Questionnaire form for generating AI-powered campaign copy."""

    # Basic Info
    project_name = forms.CharField(
        max_length=200, help_text="What are you launching? (e.g., 'AI Tools Directory', 'SaaS Marketing Platform')"
    )

    project_type = forms.ChoiceField(
        choices=[
            ("directory", "Directory/Marketplace"),
            ("tool", "Software Tool"),
            ("service", "Service/Consulting"),
            ("community", "Community/Platform"),
            ("course", "Course/Training"),
            ("other", "Other"),
        ],
        help_text="What type of project is this?",
    )

    target_audience = forms.CharField(
        max_length=300,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Who is your ideal user? (e.g., 'Developers building AI apps', 'Marketing teams at B2B companies')",
    )

    launch_timeframe = forms.ChoiceField(
        choices=[
            ("2weeks", "Within 2 weeks"),
            ("1month", "Within 1 month"),
            ("3months", "Within 3 months"),
            ("6months", "Within 6 months"),
            ("tbd", "To be determined"),
        ],
        help_text="When do you plan to launch?",
    )

    # Value Proposition
    main_problem_solved = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="What main problem does your project solve? (e.g., 'Finding quality AI tools is overwhelming and time-consuming')",
    )

    primary_benefit = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="What's the #1 benefit users get? (e.g., 'Save 10+ hours per week finding the right tools')",
    )

    unique_differentiator = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="What makes this unique/different? (e.g., 'First directory with real user reviews and pricing data')",
    )

    # Audience Pain Points
    current_struggle = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="What are they struggling with now? (e.g., 'Wasting time on unreliable tools')",
    )

    desired_outcome = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="What transformation do they want? (e.g., 'Confidently pick the best tools for their needs')",
    )

    # Offer Details
    signup_incentive = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="What do they get for signing up? (e.g., 'Early access + 50% launch discount')",
    )

    scarcity_element = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Any limitations? (e.g., 'First 100 users only', 'Limited beta access') - Optional",
    )

    # Optional Social Proof
    early_testimonials = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
        help_text="Any early feedback/testimonials? - Optional",
    )

    partner_logos = forms.CharField(required=False, help_text="Any partner companies/logos to mention? - Optional")

    relevant_metrics = forms.CharField(
        required=False, help_text="Any relevant numbers? (e.g., '1000+ tools evaluated', '50+ beta testers') - Optional"
    )


class LeadCaptureForm(forms.ModelForm):
    """Simple form for capturing email leads."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email address",
                "class": "form-control form-control-lg",
            }
        )
    )

    # Honeypot field for spam prevention
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Lead
        fields = ["email"]

    def clean_website(self):
        """Honeypot field - should always be empty."""
        website = self.cleaned_data.get("website")
        if website:
            raise forms.ValidationError("Spam detected.")
        return website


class CampaignEditForm(forms.ModelForm):
    """Form for editing campaign content after AI generation."""

    class Meta:
        model = ComingSoonCampaign
        fields = [
            "title",
            "headline",
            "subheadline",
            "value_proposition",
            "benefits",
            "cta_button_text",
            "thank_you_message",
            "template_type",
            "launch_date",
            "show_countdown",
            "show_social_proof",
            "meta_title",
            "meta_description",
        ]
        widgets = {
            "subheadline": forms.Textarea(attrs={"rows": 3}),
            "value_proposition": forms.Textarea(attrs={"rows": 4}),
            "benefits": forms.Textarea(attrs={"rows": 6}),
            "thank_you_message": forms.Textarea(attrs={"rows": 3}),
            "launch_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

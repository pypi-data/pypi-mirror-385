# Lead Capture Django App

A complete AI-powered lead capture system for creating professional "coming soon" pages with email collection, AI-generated copy, and seamless homepage override functionality.

## Terminology

- **Campaign**: A complete lead capture configuration with AI-generated copy and settings
- **Coming Soon Mode**: Django admin toggle that replaces homepage with campaign landing page
- **Lead**: An email address captured through a campaign form submission
- **Campaign Wizard**: Staff interface for creating campaigns with AI-assisted copy generation
- **Homepage Override**: Alternative term for Coming Soon Mode (same feature)

## Quick Start

### 1. Create Your First Campaign

**Prerequisites**: You must be logged in as a staff user

```bash
# Step 1: Login to Django admin
http://localhost:8000/admin/

# Step 2: Access campaign wizard (staff only)
http://localhost:8000/lead-capture/wizard/

# If you get 403 Forbidden error:
# - Ensure your user has is_staff=True in Django admin
# - User must have staff permissions for lead_capture app

# Step 3: Complete the workflow
# Fill out the questionnaire → Select LLM model → AI generates copy → Edit as needed
```

### 2. Enable Coming Soon Mode

```python
# In Django admin: Site Configuration (not lead_capture admin)
# 1. Go to: /admin/ → Site Configuration
# 2. Check "Coming soon mode" = True
# 3. Select your campaign in "Coming soon campaign" dropdown
# 4. Save changes
# 5. Visit homepage (/) - should now show your campaign instead of directory

# To disable: Uncheck "Coming soon mode" and save
# Note: Your leads remain in the database when switching modes
```

### 3. Collect and Manage Leads

```bash
# View analytics
/lead-capture/campaigns/<slug>/analytics/

# Export leads to CSV
# Django Admin → Leads → Select leads → Export CSV
```

## Architecture Overview

### Models (`models.py`)

#### `ComingSoonCampaign`
```python
# Core campaign model with AI-generated content
fields = [
    'title', 'slug', 'is_active',
    'headline', 'subheadline', 'value_proposition', 'benefits',
    'cta_button_text', 'thank_you_message',
    'page_views', 'conversion_rate', 'questionnaire_data'
]
```

#### `Lead`
```python
# Email captures with verification and tracking
fields = [
    'email', 'campaign', 'email_verified', 'verification_token',
    'source', 'referrer_url', 'ip_address', 'user_agent'
]
```

### Views (`views.py`)

- **`campaign_wizard`** - AI-powered campaign creation
- **`campaign_detail`** - Public lead capture page
- **`campaign_edit`** - Staff editing interface
- **`campaign_analytics`** - Performance tracking
- **`verify_email`** - Email verification handling

### AI Integration (`utils.py`)

#### `generate_campaign_copy(questionnaire_data, model_id=None)`
```python
# Generates complete landing page copy using LLM
# Returns: headline, subheadline, benefits, CTA, etc.
# Includes fallback copy if AI fails
```

#### `build_copy_generation_prompt(data)`
```python
# Constructs optimized prompt from questionnaire responses
# Focuses on conversion-oriented copy generation
```

### Email System (`emails.py`)

- **Welcome emails** with verification links
- **Launch notifications** for campaign goes live
- **Campaign updates** for ongoing communication
- Uses existing Django email configuration

## Configuration

### Required Settings

```python
# settings.py - Add these to your INSTALLED_APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ... your other apps
    'solo',  # Required for SiteConfiguration singleton pattern
    'llm_suite',  # AI integration - configure API keys in admin first
    'lead_capture',  # This app
]

# Required Django configuration
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration (must be configured for welcome emails)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'your-email@domain.com'  # Replace with actual email
SMTP_HOST = 'your-smtp-host.com'  # Configure your SMTP settings
```

### Database Migration

```bash
# Use UV commands (this project uses UV package manager)
uv run python src/manage.py makemigrations lead_capture
uv run python src/manage.py migrate
```

### URL Integration

Add lead_capture URLs to your main project:

```python
# In your main urls.py (e.g., src/myapp/urls.py or src/config/urls.py)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lead-capture/', include('lead_capture.urls')),
    # ... your other URL patterns
]
```

### LLM Setup

1. Configure API keys in Django admin: **LLM Suite → API Keys**
2. Ensure at least one API key is active
3. Test AI generation in campaign wizard

## URL Patterns

### Staff URLs (Login Required)
```python
/lead-capture/wizard/                    # Create campaign
/lead-capture/campaigns/                 # List campaigns
/lead-capture/campaigns/<slug>/edit/     # Edit campaign
/lead-capture/campaigns/<slug>/preview/  # Preview campaign
/lead-capture/campaigns/<slug>/analytics/ # View analytics
```

### Public URLs
```python
/launch/<slug>/           # Campaign landing page
/launch/<slug>/thank-you/ # Post-submission page
/verify/<token>/          # Email verification
```

### Homepage Override
```python
/  # Shows campaign when coming_soon_mode=True
/  # Shows normal site when coming_soon_mode=False
```

## API Reference

### Key Functions

#### Campaign Creation
```python
from lead_capture.utils import generate_campaign_copy

# Generate AI copy from questionnaire
copy_data = generate_campaign_copy(
    questionnaire_data={
        'project_name': 'My Startup',
        'target_audience': 'Developers',
        # ... other questionnaire fields
    },
    model_id=api_key.id  # Optional: specific LLM model
)
```

#### Email Operations
```python
from lead_capture.emails import send_welcome_email, send_launch_notification

# Send welcome email to new lead
success = send_welcome_email(lead_instance)

# Notify all leads when campaign goes live
count = send_launch_notification(campaign_instance)
```

#### Lead Management
```python
from lead_capture.models import Lead, ComingSoonCampaign

# Get campaign analytics
campaign = ComingSoonCampaign.objects.get(slug='my-campaign')
conversion_rate = campaign.conversion_rate
lead_count = campaign.leads.count()

# Export verified leads
verified_leads = campaign.leads.filter(email_verified=True)
```

## Template Structure

```
lead_capture/templates/lead_capture/
├── campaign.html         # Public landing page (standalone)
├── thank_you.html        # Post-submission page (standalone)
├── wizard.html           # Campaign creation form
├── edit.html             # Campaign editing interface
├── preview.html          # Campaign preview
├── analytics.html        # Analytics dashboard
├── list.html             # Campaign list
└── emails/
    └── welcome.html      # Welcome email template
```

### Standalone Templates

The `campaign.html` and `thank_you.html` are **standalone** HTML pages (no base template inheritance) for professional appearance and optimal conversion.

## Testing

### Unit Tests
```bash
# Use UV commands for this project
uv run python src/manage.py test lead_capture
```

### Manual Testing Workflow
1. Create campaign via wizard
2. Test AI copy generation
3. Preview campaign design
4. Submit test email
5. Verify email delivery
6. Check analytics tracking
7. Export lead data

### Integration Testing
```python
# Test coming soon mode toggle
# Note: SiteConfiguration location varies by project setup
from myapp.models import SiteConfiguration  # Adjust import based on your project
config = SiteConfiguration.get_solo()
config.coming_soon_mode = True
config.coming_soon_campaign = campaign
config.save()

# Visit homepage - should show campaign
```

## LLM Agent Instructions

### Prerequisites Validation
Before implementing, verify these conditions:
1. `llm_suite` app is in INSTALLED_APPS
2. At least one APIKey exists in Django admin with `is_active=True`
3. Email backend is configured (check DEFAULT_FROM_EMAIL setting)
4. URL patterns are included in main urls.py

### Success Criteria
Campaign creation succeeded if ALL are true:
- Campaign object created with unique slug
- AI-generated copy fields populated (headline, subheadline, benefits)
- No error messages in Django logs
- Preview URL returns 200 status code
- Email test passes (if configured)

### Failure Detection
Stop and escalate if ANY occur:
- ImportError for llm_suite models
- "No API keys available" message in wizard
- Email sending fails during testing
- Campaign wizard returns 500 error
- Permission denied (403) errors for staff users

### Command Validation
All commands in this documentation use UV package manager:
- ✅ Correct: `uv run python src/manage.py migrate`
- ❌ Wrong: `python manage.py migrate`

### Error Recovery
If campaign creation fails:
1. Check Django admin: LLM Suite → API Keys (must have active key)
2. Verify user has staff permissions
3. Check Django logs for specific error messages
4. Test email configuration separately if emails fail

## Common Use Cases

### 1. New Directory Launch
```python
# Deploy directory-builder to new domain
# Create campaign: "AI Tools Directory Coming Soon"
# Enable coming soon mode
# Collect 1000+ emails while building content
# Launch directory with instant audience
```

### 2. Feature Pre-Launch
```python
# Create campaign for new category
# Test market demand
# Build feature based on interest level
# Launch to pre-qualified audience
```

### 3. Marketing Campaigns
```python
# Create multiple campaigns for A/B testing
# Different copy for different traffic sources
# Track conversion by campaign
# Optimize based on performance
```

## Troubleshooting

### Common Issues

**No LLM models available**
```python
# Solution: Configure API key in Django admin
# LLM Suite → API Keys → Add key → Make active
```

**Email delivery failing**
```python
# Test email configuration safely
uv run python src/manage.py shell
>>> from django.conf import settings
>>> from django.core.mail import send_mail
>>> print(f"Email backend: {settings.EMAIL_BACKEND}")
>>> print(f"Default from email: {settings.DEFAULT_FROM_EMAIL}")
>>> # Only test if settings look correct:
>>> send_mail('Test Subject', 'Test message', settings.DEFAULT_FROM_EMAIL, ['test@example.com'])
```

**Coming soon mode not working**
```python
# Check SiteConfiguration in Django admin
# Ensure coming_soon_mode = True
# Ensure coming_soon_campaign is selected
# Clear browser cache
```

**AI copy generation failing**
```python
# Check API key validity
# Verify model name format (e.g., 'gpt-3.5-turbo')
# Check network connectivity
# Review litellm logs
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.getLogger('lead_capture').setLevel(logging.DEBUG)

# Check campaign status
campaign = ComingSoonCampaign.objects.get(slug='test')
print(f"Active: {campaign.is_active}")
print(f"Page views: {campaign.page_views}")
print(f"Leads: {campaign.leads.count()}")
```

## Security Considerations

- **Staff-only access** for campaign creation
- **CSRF protection** on all forms
- **Honeypot fields** for spam prevention
- **Email validation** and verification
- **Rate limiting** recommended for public pages
- **SQL injection safe** (Django ORM only)

## Performance Notes

- **Optimized queries** with select_related in admin
- **Responsive design** for fast mobile loading
- **Minimal dependencies** (Django + litellm)
- **Efficient templates** with CDN Bootstrap
- **Database indexes** on frequently queried fields

## Further Reading

- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Complete implementation guide
- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)
- [LiteLLM Documentation](https://docs.litellm.ai/) - AI integration details

---

**Version:** 1.0
**Django Version:** 4.x+
**Python Version:** 3.12+
**Dependencies:** django, litellm, solo

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-16

### Added
- Initial release of django-lead-capture
- AI-powered campaign copy generation using LiteLLM
- Campaign wizard with comprehensive questionnaire
- Lead capture with email verification
- Campaign analytics and conversion tracking
- CSV export of leads
- Email notifications (welcome, launch, campaign updates)
- Countdown timer support
- Social proof display
- Django Solo-based configuration
- Django system check for API key validation
- Bootstrap 5 templates
- Comprehensive admin interface

### Features
- Two campaign models: ComingSoonCampaign and Lead
- Configuration via Django Admin (no environment variables required)
- Support for any LiteLLM-compatible model (OpenAI, Anthropic, Groq, etc.)
- Custom API endpoint support
- Template-based fallback copy generation
- Honeypot spam prevention
- IP tracking and referrer metadata

[0.1.0]: https://github.com/heysamtexas/django-lead-capture/releases/tag/0.1.0

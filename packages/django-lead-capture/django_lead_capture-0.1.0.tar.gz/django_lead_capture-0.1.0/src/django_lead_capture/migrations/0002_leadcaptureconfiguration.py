# Generated migration for LeadCaptureConfiguration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_lead_capture', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeadCaptureConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(blank=True, help_text='LLM API key (required for AI-powered campaign generation)', max_length=500)),
                ('model_name', models.CharField(default='gpt-4o-mini', help_text='LiteLLM model identifier (e.g., gpt-4, claude-3-sonnet-20240229)', max_length=200)),
                ('api_endpoint', models.URLField(blank=True, default='', help_text='Custom API endpoint (optional). Leave blank for provider defaults.')),
            ],
            options={
                'verbose_name': 'Lead Capture Configuration',
            },
        ),
    ]

"""Utilities for lead capture functionality including AI copy generation."""
# ruff: noqa: TRY301, B904, PLW2901

import json
from typing import Any

import litellm


def get_llm_config():
    """Get LLM configuration from LeadCaptureConfiguration singleton.

    Retrieves the configured API key and model from the Django admin configuration.

    Returns:
        dict: Configuration dictionary with 'api_key', 'model', and optionally 'api_base' fields

    Raises:
        ValueError: If no API key is configured

    Example:
        >>> config = get_llm_config()
        >>> print(config['model'])  # 'gpt-4o-mini'

    """
    from .models import LeadCaptureConfiguration

    config = LeadCaptureConfiguration.get_solo()

    if not config.api_key:
        raise ValueError(
            "No API key configured. Please configure Lead Capture in Django Admin."
        )

    result = {
        "api_key": config.api_key,
        "model": config.model_name,
    }

    if config.api_endpoint:
        result["api_base"] = config.api_endpoint

    return result


def generate_campaign_copy(questionnaire_data: dict[str, Any]) -> dict[str, Any]:
    """Generate landing page copy using LLM based on questionnaire data.

    Takes structured questionnaire responses and generates professional landing page copy
    optimized for conversion. Uses AI to create headlines, value propositions, benefits,
    and call-to-action text based on the project details and target audience.

    Args:
        questionnaire_data: Dictionary containing questionnaire responses with keys:
            - project_name: Name of the project/product
            - project_type: Type (directory, tool, service, etc.)
            - target_audience: Description of ideal users
            - main_problem_solved: Core problem the project addresses
            - primary_benefit: Main benefit users get
            - unique_differentiator: What makes it unique
            - And other optional fields for social proof, timeline, etc.

    Returns:
        dict: Generated copy with keys:
            - headline: Main headline (max 60 chars)
            - subheadline: Supporting text (max 120 chars)
            - value_proposition: 2-3 sentence explanation
            - benefits: List of 3-5 benefit bullet points
            - cta_button_text: Call-to-action button text
            - thank_you_message: Post-submission message
            - meta_title: SEO page title
            - meta_description: SEO meta description

    Raises:
        ValueError: If LLM configuration fails
        Exception: Falls back to default copy if LLM generation fails

    Example:
        >>> data = {
        ...     'project_name': 'AI Tools Directory',
        ...     'target_audience': 'Developers building AI apps',
        ...     'main_problem_solved': 'Finding quality AI tools is time-consuming'
        ... }
        >>> copy = generate_campaign_copy(data)
        >>> print(copy['headline'])  # 'Coming Soon: AI Tools Directory'

    """
    llm_config = get_llm_config()

    litellm.api_key = llm_config["api_key"]

    # Build the prompt
    prompt = build_copy_generation_prompt(questionnaire_data)

    try:
        completion_params = {
            "model": llm_config["model"],
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert copywriter specializing in high-converting landing pages. You create compelling, benefit-focused copy that drives email signups. Always format your response as valid JSON with the exact keys requested.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        # Add custom API endpoint if configured
        if "api_base" in llm_config:
            completion_params["api_base"] = llm_config["api_base"]

        response = litellm.completion(**completion_params)

        # Parse the response
        response_content = response.choices[0].message.content

        try:
            # Try to parse as JSON
            generated_copy = json.loads(response_content)
        except json.JSONDecodeError:
            # If JSON parsing fails, extract content manually
            generated_copy = parse_non_json_response(response_content)

        # Validate and clean the response
        return validate_generated_copy(generated_copy, questionnaire_data)

    except Exception:
        # Fallback to default copy if LLM fails
        return generate_fallback_copy(questionnaire_data)


def build_copy_generation_prompt(data: dict[str, Any]) -> str:
    """Build the prompt for LLM copy generation.

    Creates a structured prompt that guides the LLM to generate high-converting
    landing page copy based on questionnaire responses. The prompt includes
    specific constraints and formatting requirements to ensure consistent output.

    Args:
        data: Questionnaire data dictionary containing project details,
              value proposition, audience insights, and social proof

    Returns:
        str: Formatted prompt optimized for LLM copy generation

    Example:
        >>> prompt = build_copy_generation_prompt({'project_name': 'My App'})
        >>> print(len(prompt))  # ~1500 characters

    """
    prompt = f"""
Generate compelling landing page copy for a coming soon page based on this information:

**Project Details:**
- Name: {data["project_name"]}
- Type: {data["project_type"]}
- Target Audience: {data["target_audience"]}
- Launch Timeframe: {data["launch_timeframe"]}

**Value Proposition:**
- Main Problem Solved: {data["main_problem_solved"]}
- Primary Benefit: {data["primary_benefit"]}
- Unique Differentiator: {data["unique_differentiator"]}

**Audience Insights:**
- Current Struggle: {data["current_struggle"]}
- Desired Outcome: {data["desired_outcome"]}

**Offer Details:**
- Signup Incentive: {data["signup_incentive"]}
- Scarcity Element: {data.get("scarcity_element", "N/A")}

**Social Proof (if available):**
- Early Testimonials: {data.get("early_testimonials", "N/A")}
- Partner Logos: {data.get("partner_logos", "N/A")}
- Relevant Metrics: {data.get("relevant_metrics", "N/A")}

Generate the following copy elements optimized for high conversion:

1. **Headline** (max 60 chars): Attention-grabbing, benefit-focused
2. **Subheadline** (max 120 chars): Clarify the value proposition
3. **Value Proposition** (2-3 sentences): Why this matters now
4. **Benefits** (3-5 bullet points): Specific, outcome-focused benefits
5. **CTA Button Text** (2-4 words): Action-oriented, compelling
6. **Thank You Message** (1-2 sentences): Set expectations for next steps
7. **Meta Title** (max 60 chars): SEO-optimized page title
8. **Meta Description** (max 160 chars): Search-friendly description

Format your response as JSON with these exact keys:
{{
    "headline": "Your headline here",
    "subheadline": "Your subheadline here",
    "value_proposition": "Your value proposition here",
    "benefits": ["Benefit 1", "Benefit 2", "Benefit 3", "Benefit 4"],
    "cta_button_text": "Get Early Access",
    "thank_you_message": "Thank you! We'll notify you when we launch.",
    "meta_title": "SEO title here",
    "meta_description": "SEO description here"
}}

Focus on:
- Clear, benefit-driven language
- Urgency and scarcity where appropriate
- Addressing the specific pain points mentioned
- Creating emotional connection with the target audience
- Professional but approachable tone
"""

    return prompt


def parse_non_json_response(content: str) -> dict[str, Any]:
    """Parse LLM response when JSON parsing fails.

    Provides a fallback parser for when the LLM returns malformed JSON or plain text.
    Uses pattern matching to extract key-value pairs for landing page copy elements.

    Args:
        content: Raw text response from LLM

    Returns:
        dict: Parsed copy elements (may be incomplete)

    Note:
        This is a best-effort parser. Results may vary depending on LLM output format.
        Always followed by validate_generated_copy() to ensure completeness.

    """
    # Simple fallback parsing - look for key patterns
    parsed = {}

    lines = content.split("\n")
    current_key = None
    current_value = []

    for line in lines:
        line = line.strip()
        if ":" in line and any(
            key in line.lower() for key in ["headline", "subheadline", "value", "benefit", "cta", "thank", "meta"]
        ):
            # Save previous key if exists
            if current_key:
                if "benefit" in current_key:
                    parsed[current_key] = current_value
                else:
                    parsed[current_key] = " ".join(current_value).strip()

            # Start new key
            parts = line.split(":", 1)
            if len(parts) == 2:  # noqa: PLR2004
                current_key = parts[0].lower().replace(" ", "_").replace("-", "_")
                current_value = [parts[1].strip()]
        elif current_key and line:
            current_value.append(line)

    # Save last key
    if current_key:
        if "benefit" in current_key:
            parsed[current_key] = current_value
        else:
            parsed[current_key] = " ".join(current_value).strip()

    return parsed


def validate_generated_copy(generated_copy: dict[str, Any], questionnaire_data: dict[str, Any]) -> dict[str, Any]:
    """Validate and clean the generated copy, providing fallbacks for missing fields.

    Ensures all required copy elements are present and properly formatted. Applies
    character limits, sanitizes content, and provides intelligent fallbacks using
    the original questionnaire data when LLM output is incomplete.

    Args:
        generated_copy: Raw copy from LLM (may be incomplete or malformed)
        questionnaire_data: Original questionnaire responses for fallbacks

    Returns:
        dict: Complete, validated copy ready for campaign creation

    Processing:
        - Enforces character limits (headline: 60, subheadline: 120, etc.)
        - Converts string benefits to list format
        - Provides fallbacks for missing fields
        - Generates SEO fields if not provided

    """
    validated = {}

    # Required fields with fallbacks
    validated["headline"] = generated_copy.get("headline", f"Coming Soon: {questionnaire_data['project_name']}")[:60]
    validated["subheadline"] = generated_copy.get("subheadline", questionnaire_data.get("primary_benefit", ""))[:120]
    validated["value_proposition"] = generated_copy.get(
        "value_proposition", questionnaire_data.get("main_problem_solved", "")
    )

    # Benefits - ensure it's a list
    benefits = generated_copy.get("benefits", [])
    if isinstance(benefits, str):
        # If benefits is a string, try to split it
        benefits = [b.strip() for b in benefits.replace("•", "").replace("-", "").split("\n") if b.strip()]
    validated["benefits"] = benefits[:5]  # Max 5 benefits

    validated["cta_button_text"] = generated_copy.get("cta_button_text", "Get Early Access")[:50]
    validated["thank_you_message"] = generated_copy.get(
        "thank_you_message", "Thank you! We'll notify you when we launch."
    )

    # SEO fields
    validated["meta_title"] = generated_copy.get("meta_title", validated["headline"])[:60]
    validated["meta_description"] = generated_copy.get("meta_description", validated["subheadline"])[:160]

    return validated


def generate_fallback_copy(questionnaire_data: dict[str, Any]) -> dict[str, Any]:
    """Generate fallback copy when LLM fails.

    Creates basic but professional landing page copy using template-based approach
    when AI generation fails. Ensures the campaign wizard never completely fails
    and users always get usable copy that can be manually edited.

    Args:
        questionnaire_data: Original questionnaire responses

    Returns:
        dict: Basic copy elements using questionnaire data and templates

    Example:
        >>> data = {'project_name': 'My App', 'primary_benefit': 'Save time'}
        >>> copy = generate_fallback_copy(data)
        >>> copy['headline']  # 'Coming Soon: My App'

    """
    project_name = questionnaire_data["project_name"]
    primary_benefit = questionnaire_data.get("primary_benefit", "Get early access to something amazing")

    return {
        "headline": f"Coming Soon: {project_name}",
        "subheadline": primary_benefit,
        "value_proposition": questionnaire_data.get(
            "main_problem_solved", f"{project_name} is launching soon. Be the first to know!"
        ),
        "benefits": [
            "Early access to new features",
            "Exclusive member benefits",
            "Be part of the beta community",
            "No spam, unsubscribe anytime",
        ],
        "cta_button_text": "Get Early Access",
        "thank_you_message": "Thank you! We'll notify you when we launch.",
        "meta_title": f"Coming Soon: {project_name}",
        "meta_description": f"Join the waitlist for {project_name}. {primary_benefit}",
    }

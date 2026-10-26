"""LLM integration service for MathQuest using google-genai SDK.

Enforces Rule 2 & 3: Model names and secrets strictly come from environment variables.
Model names are read from GEMINI_MODEL and GEMINI_MODEL_ALT.
Uses structured outputs with the QuestionTemplate Pydantic schema.
"""

from __future__ import annotations

import logging
import os
from google import genai
from google.genai import types

from app.schemas import QuestionTemplate

logger = logging.getLogger(__name__)


def get_model_name(use_alt: bool = False) -> str:
    """Retrieve model name strictly from environment variables.

    Raises:
        ValueError: If GEMINI_MODEL or GEMINI_MODEL_ALT is missing from the environment.
    """
    env_var = "GEMINI_MODEL_ALT" if use_alt else "GEMINI_MODEL"
    model_name = os.getenv(env_var)
    if not model_name or not model_name.strip():
        raise ValueError(
            f"Required environment variable '{env_var}' is not set. "
            "Model names must be configured strictly via environment variables, not hardcoded."
        )
    return model_name.strip()


def get_gemini_client() -> genai.Client:
    """Create and return a configured google-genai Client."""
    api_key = os.getenv("GEMINI_API_KEY")
    http_opts = types.HttpOptions(timeout=15000)
    if api_key:
        return genai.Client(api_key=api_key, http_options=http_opts)
    return genai.Client(http_options=http_opts)


def generate_question_template(
    prompt: str,
    client: genai.Client | None = None,
    model_name: str | None = None,
    use_alt_model: bool = False,
) -> QuestionTemplate:
    """Invoke Gemini API to generate a structured QuestionTemplate.

    Args:
        prompt: System and instruction prompt.
        client: Optional pre-configured genai.Client (useful for testing and dependency injection).
        model_name: Optional explicit model override. If not supplied, read from GEMINI_MODEL or GEMINI_MODEL_ALT.
        use_alt_model: If True and model_name is not provided, uses GEMINI_MODEL_ALT.

    Returns:
        Validated QuestionTemplate instance.

    Raises:
        ValueError: If model name cannot be resolved or API returns empty response.
        Exception: If network error, API failure, or response generation fails.
    """
    if os.getenv("TESTING") == "true" and client is None and not os.getenv("ENABLE_LIVE_LLM_TESTS"):
        raise ValueError("Live LLM calls disabled in testing mode; triggering fallback pipeline.")

    target_model = model_name or get_model_name(use_alt=use_alt_model)
    if client is None:
        client = get_gemini_client()

    logger.info("Invoking Gemini model '%s' for QuestionTemplate generation.", target_model)

    response = client.models.generate_content(
        model=target_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QuestionTemplate,
            temperature=0.7,
        ),
    )

    if not response or not response.text:
        raise ValueError("Gemini API returned an empty response.")

    # Validate output against Pydantic schema
    return QuestionTemplate.model_validate_json(response.text)

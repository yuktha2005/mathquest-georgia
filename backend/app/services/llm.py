"""LLM integration service for MathQuest Georgia using google-genai SDK.

Enforces Rule 4: Zero secrets in code. Reads GEMINI_API_KEY and GEMINI_MODEL
strictly from environment variables.
Uses structured outputs with the QuestionTemplate Pydantic schema.
"""

from __future__ import annotations

import logging
import os
from google import genai
from google.genai import types

from app.schemas import QuestionTemplate

logger = logging.getLogger(__name__)


def get_gemini_client() -> genai.Client:
    """Create and return a configured google-genai Client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()


def generate_question_template(
    prompt: str,
    client: genai.Client | None = None,
) -> QuestionTemplate:
    """Invoke Gemini API to generate a structured QuestionTemplate.

    Args:
        prompt: System and instruction prompt.
        client: Optional pre-configured genai.Client (useful for testing and dependency injection).

    Returns:
        Validated QuestionTemplate instance.

    Raises:
        Exception: If network error, API failure, or response generation fails.
    """
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    if client is None:
        client = get_gemini_client()

    logger.info("Invoking Gemini model '%s' for QuestionTemplate generation.", model_name)

    response = client.models.generate_content(
        model=model_name,
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

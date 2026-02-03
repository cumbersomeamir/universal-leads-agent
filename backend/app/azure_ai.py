"""
Azure AI Foundry client (OpenAI-compatible).
Uses AZURE_API_KEY and AZURE_BASE_ENDPOINT from config.
"""

from openai import AzureOpenAI

from app.config import settings


def get_client() -> AzureOpenAI | None:
    """Return Azure OpenAI client if credentials are set, else None."""
    if not settings.azure_ai_configured:
        return None
    return AzureOpenAI(
        api_key=settings.azure_api_key,
        api_version="2024-08-01-preview",
        azure_endpoint=settings.azure_base_endpoint.rstrip("/"),
    )


def is_available() -> bool:
    """Check if Azure AI Foundry is configured and usable."""
    return settings.azure_ai_configured

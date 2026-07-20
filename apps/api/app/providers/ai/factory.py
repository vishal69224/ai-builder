from app.core.config import Settings
from app.providers.ai.mock import MockAIProvider
from app.providers.ai.openai_compatible import OpenAICompatibleProvider


def get_ai_provider(settings: Settings):
    if settings.ai_mock or not settings.ai_api_key:
        return MockAIProvider()
    return OpenAICompatibleProvider(
        base_url=settings.ai_base_url,
        api_key=settings.ai_api_key,
        model=settings.ai_model,
    )

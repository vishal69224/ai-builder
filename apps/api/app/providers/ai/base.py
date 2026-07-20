from typing import Protocol

from app.providers.ai.schemas import GenerationRequest, GenerationResult


class AIProvider(Protocol):
    def generate_site(self, request: GenerationRequest) -> GenerationResult: ...

"""Generation Orchestrator — public entry facade for site generation.

Phase 2: thin delegate to GenerationEngine.
Phase 3: GenerationContext carries run identity (including queued worker runs).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.generation.context import GenerationContext
from app.generation.engine import GenerationEngine
from app.models.user import User

__all__ = ["GenerationContext", "Orchestrator"]


class Orchestrator:
    """Single public entry point for generation. Delegates to GenerationEngine."""

    def __init__(self, engine: GenerationEngine | None = None) -> None:
        self._engine = engine or GenerationEngine()

    def run(
        self,
        *,
        db: Session,
        user: User,
        prompt: str,
        project_id: UUID | None = None,
        project_name: str | None = None,
        existing_run_id: UUID | None = None,
    ) -> dict:
        ctx = GenerationContext(
            db=db,
            user=user,
            prompt=prompt,
            project_id=project_id,
            project_name=project_name,
            existing_run_id=existing_run_id,
        )
        return self._engine.run(ctx)

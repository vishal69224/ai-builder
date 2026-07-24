"""Runtime context for a single generation invocation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User

if TYPE_CHECKING:
    from app.generation.pipeline import PromptAnalysis, StructuredRequirements


@dataclass
class GenerationContext:
    """Carries identity and stage outputs for Orchestrator → Engine → agents.

    existing_run_id: when set (async worker), reuse that GenerationRun instead of
    creating a duplicate row.

    analysis / requirements: written by PromptAgent (Phase 4).
    """

    db: Session
    user: User
    prompt: str
    project_id: UUID | None = None
    project_name: str | None = None
    existing_run_id: UUID | None = None
    analysis: PromptAnalysis | None = None
    requirements: StructuredRequirements | None = None

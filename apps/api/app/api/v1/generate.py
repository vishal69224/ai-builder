from uuid import UUID

from pydantic import BaseModel, Field

from app.core.deps import get_current_user, get_db
from app.generation.analyzer.prompt_analyzer import analyze_prompt
from app.generation.analyzer.website_types import catalog_stats
from app.generation.engine import GenerationEngine
from app.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(tags=["generate"])


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1)
    project_id: UUID | None = None
    project_name: str | None = Field(default=None, max_length=200)


class AnalyzeRequest(BaseModel):
    prompt: str = Field(min_length=1)


@router.post("/generate")
def generate_project(
    payload: GenerateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Full generation pipeline: analyze → extract → plan → generate → validate → save."""
    return GenerationEngine().run(
        db=db,
        user=user,
        prompt=payload.prompt,
        project_id=payload.project_id,
        project_name=payload.project_name,
    )


@router.post("/analyze")
def analyze_only(payload: AnalyzeRequest) -> dict:
    """Prompt Analyzer only — returns structured JSON (no auth required for inspection)."""
    return analyze_prompt(payload.prompt)


@router.get("/analyze/catalog")
def analyzer_catalog() -> dict:
    return catalog_stats()

from fastapi import APIRouter

from app.ai_model.classifier import LocalWebsiteClassifier
from app.ai_model.trainer import train_and_save
from app.core.config import get_settings

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status")
def ai_status() -> dict:
    """Local AI status — no external API key required."""
    settings = get_settings()
    clf = LocalWebsiteClassifier()
    return {
        "active_provider": "local" if settings.ai_provider == "local" or not settings.ai_api_key else "openai",
        "requires_api_key": False if settings.ai_provider == "local" or not settings.ai_api_key else True,
        "description": (
            "Local trained classifier + template generation engine. "
            "Understands prompts and builds full React + Tailwind projects without OpenAI."
        ),
        "classifier": clf.status(),
        "pipeline": [
            "Prompt Analyzer (ML + rules)",
            "Requirement Extractor",
            "Project Planner",
            "Component / CSS / Route / API Generators",
            "Validation",
            "File Writer",
            "Preview Engine (npm build)",
        ],
    }


@router.post("/train")
def retrain_model() -> dict:
    """Retrain local website classifier from catalog."""
    meta = train_and_save()
    return {"ok": True, **meta}

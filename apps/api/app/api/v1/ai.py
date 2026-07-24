from fastapi import APIRouter

from app.ai_model.classifier import LocalWebsiteClassifier
from app.ai_model.trainer import train_and_save
from app.core.config import get_settings

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status")
def ai_status() -> dict:
    """Local AI status — classifier + TinyGPT hybrid."""
    settings = get_settings()
    clf = LocalWebsiteClassifier()
    tinygpt: dict = {"ok": False, "hybrid": settings.tinygpt_hybrid}
    try:
        from app.generation.ai.tinygpt_client import health

        h = health(base_url=settings.tinygpt_base_url, timeout=1.2)
        if h:
            tinygpt = {
                "ok": True,
                "hybrid": settings.tinygpt_hybrid,
                "base_url": settings.tinygpt_base_url,
                "checkpoint": h.get("checkpoint"),
                "params": h.get("params"),
                "meta": h.get("meta"),
            }
    except Exception as exc:  # noqa: BLE001
        tinygpt["error"] = str(exc)

    return {
        "active_provider": "local" if settings.ai_provider == "local" or not settings.ai_api_key else "openai",
        "requires_api_key": False if settings.ai_provider == "local" or not settings.ai_api_key else True,
        "description": (
            "Local TinyGPT (8M) hybrid + specialty generators. "
            "Understands prompts and builds full React + Tailwind projects without paid APIs."
        ),
        "classifier": clf.status(),
        "tinygpt": tinygpt,
        "pipeline": [
            "Prompt Analyzer (ML + rules)",
            "Website Planner",
            "TinyGPT hybrid (when online)",
            "Specialty generators (fashion / portfolio / …)",
            "Theme + content + images",
            "Validation",
            "Preview Engine (vite build)",
        ],
    }


@router.post("/train")
def retrain_model() -> dict:
    """Retrain local website classifier from catalog."""
    meta = train_and_save()
    return {"ok": True, **meta}

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401

logger = logging.getLogger("ai_builder")


def _ensure_local_ai_model() -> None:
    """Train local classifier on first boot if missing (no API key required)."""
    from app.ai_model.trainer import MODEL_PATH, train_and_save

    if MODEL_PATH.exists():
        logger.info("Local AI model loaded from %s", MODEL_PATH)
        return
    logger.info("Training local AI model (first run, ~10s)...")
    meta = train_and_save()
    logger.info(
        "Local AI ready: %s samples, %s website types",
        meta.get("training_samples"),
        meta.get("website_types"),
    )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    if settings.is_sqlite:
        Base.metadata.create_all(bind=engine)
    if settings.ai_provider == "local" or not settings.ai_api_key:
        _ensure_local_ai_model()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "env": settings.app_env}

    return app


app = create_app()

"""Background worker that claims queued generation runs and writes artifacts."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.generation.orchestrator import Orchestrator
from app.models.enums import GenerationStatus
from app.models.generation import GenerationRun
from app.models.project import Project
from app.models.user import User
import app.models  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("generation_worker")


def claim_next_run(db) -> GenerationRun | None:
    settings = get_settings()
    if settings.is_sqlite:
        run = db.scalar(
            select(GenerationRun)
            .where(GenerationRun.status == GenerationStatus.queued)
            .order_by(GenerationRun.created_at.asc())
            .limit(1)
        )
        if run is None:
            return None
        run.status = GenerationStatus.running
        run.started_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(run)
        return run

    # Postgres: SKIP LOCKED for safe multi-worker claiming
    from sqlalchemy import text

    result = db.execute(
        text(
            """
            SELECT id FROM generation_runs
            WHERE status = 'queued'
            ORDER BY created_at ASC
            FOR UPDATE SKIP LOCKED
            LIMIT 1
            """
        )
    )
    row = result.first()
    if row is None:
        return None
    run = db.get(GenerationRun, row[0])
    if run is None:
        return None
    run.status = GenerationStatus.running
    run.started_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run


def process_run(run_id) -> None:
    """Process a claimed run through the same Orchestrator → Engine pipeline as /generate."""
    db = SessionLocal()
    try:
        run = db.get(GenerationRun, run_id)
        if run is None:
            return
        project = db.get(Project, run.project_id)
        if project is None:
            run.status = GenerationStatus.failed
            run.error_message = "Project missing"
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        user = db.get(User, run.user_id)
        if user is None:
            run.status = GenerationStatus.failed
            run.error_message = "User missing"
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
            return

        result = Orchestrator().run(
            db=db,
            user=user,
            prompt=run.prompt,
            project_id=project.id,
            project_name=project.name,
            existing_run_id=run.id,
        )
        file_count = len(result.get("files") or [])
        logger.info("Run %s succeeded via Orchestrator (%s files)", run.id, file_count)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Run %s failed", run_id)
        db.rollback()
        run = db.get(GenerationRun, run_id)
        if run:
            detail = getattr(exc, "detail", None)
            message = str(detail) if detail is not None else str(exc)
            run.status = GenerationStatus.failed
            run.error_message = message[:4000]
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


def run_forever() -> None:
    settings = get_settings()
    if settings.is_sqlite:
        Base.metadata.create_all(bind=engine)
    logger.info(
        "Generation worker started (poll=%ss, pipeline=orchestrator, db=%s)",
        settings.worker_poll_interval_seconds,
        "sqlite" if settings.is_sqlite else "postgres",
    )
    while True:
        db = SessionLocal()
        try:
            run = claim_next_run(db)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to claim run")
            run = None
        finally:
            db.close()

        if run:
            process_run(run.id)
        else:
            time.sleep(settings.worker_poll_interval_seconds)


if __name__ == "__main__":
    run_forever()

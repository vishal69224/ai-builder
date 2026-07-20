"""Background worker that claims queued generation runs and writes artifacts."""

from __future__ import annotations

import hashlib
import logging
import time
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.domain.paths import sanitize_relative_path
from app.models.artifact import ArtifactFile
from app.models.enums import GenerationStatus
from app.models.generation import GenerationRun
from app.models.project import Project
import app.models  # noqa: F401
from app.providers.ai.factory import get_ai_provider
from app.providers.ai.schemas import FileSpec, GenerationRequest
from app.providers.storage.local import LocalArtifactStorage

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


def load_prior_files(storage: LocalArtifactStorage, project: Project) -> list[FileSpec] | None:
    if project.current_run_id is None:
        return None
    paths = storage.list_files(project.id, project.current_run_id)
    specs: list[FileSpec] = []
    for path in paths[:40]:
        try:
            content = storage.read_file(project.id, project.current_run_id, path).decode("utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        specs.append(FileSpec(path=path, content=content))
    return specs or None


def persist_files(db, storage: LocalArtifactStorage, run: GenerationRun, files: list[FileSpec]) -> None:
    storage.delete_tree(run.project_id, run.id)
    for spec in files:
        path = sanitize_relative_path(spec.path)
        data = spec.content.encode("utf-8")
        storage.write_file(run.project_id, run.id, path, data)
        digest = hashlib.sha256(data).hexdigest()
        db.add(ArtifactFile(run_id=run.id, path=path, content_hash=digest, size_bytes=len(data)))


def process_run(run_id) -> None:
    settings = get_settings()
    storage = LocalArtifactStorage(settings.artifact_root)
    provider = get_ai_provider(settings)
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

        prior = load_prior_files(storage, project)
        result = provider.generate_site(
            GenerationRequest(prompt=run.prompt, project_name=project.name, prior_files=prior)
        )
        persist_files(db, storage, run, result.files)
        run.status = GenerationStatus.succeeded
        run.finished_at = datetime.now(timezone.utc)
        run.error_message = None
        project.current_run_id = run.id
        db.commit()
        logger.info("Run %s succeeded (%s files)", run.id, len(result.files))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Run %s failed", run_id)
        db.rollback()
        run = db.get(GenerationRun, run_id)
        if run:
            run.status = GenerationStatus.failed
            run.error_message = str(exc)[:4000]
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


def run_forever() -> None:
    settings = get_settings()
    if settings.is_sqlite:
        Base.metadata.create_all(bind=engine)
    logger.info(
        "Generation worker started (poll=%ss, mock=%s, db=%s)",
        settings.worker_poll_interval_seconds,
        settings.ai_mock,
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

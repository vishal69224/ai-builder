from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.enums import GenerationStatus
from app.models.generation import GenerationRun
from app.models.project import Project
from app.models.user import User


class GenerationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def enqueue(self, user: User, project: Project, prompt: str) -> GenerationRun:
        run = GenerationRun(
            project_id=project.id,
            user_id=user.id,
            prompt=prompt.strip(),
            status=GenerationStatus.queued,
            provider="orchestrator",
            model="local-website-ai-v1",
        )
        self.db.add(run)
        self.db.flush()
        return run

    def start_for_project(self, user: User, project_id: UUID, prompt: str) -> GenerationRun:
        project = self.db.get(Project, project_id)
        if project is None or project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        run = self.enqueue(user, project, prompt)
        self.db.commit()
        self.db.refresh(run)
        return run

    def list_for_project(self, user: User, project_id: UUID) -> list[GenerationRun]:
        project = self.db.get(Project, project_id)
        if project is None or project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        stmt = (
            select(GenerationRun)
            .where(GenerationRun.project_id == project_id)
            .order_by(GenerationRun.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_owned(self, user: User, run_id: UUID) -> GenerationRun:
        run = self.db.get(GenerationRun, run_id)
        if run is None or run.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found")
        return run

    def mark_running(self, run: GenerationRun) -> None:
        run.status = GenerationStatus.running
        run.started_at = datetime.now(timezone.utc)
        self.db.commit()

    def mark_succeeded(self, run: GenerationRun) -> None:
        run.status = GenerationStatus.succeeded
        run.finished_at = datetime.now(timezone.utc)
        run.error_message = None
        project = self.db.get(Project, run.project_id)
        if project:
            project.current_run_id = run.id
        self.db.commit()

    def mark_failed(self, run: GenerationRun, message: str) -> None:
        run.status = GenerationStatus.failed
        run.finished_at = datetime.now(timezone.utc)
        run.error_message = message[:4000]
        self.db.commit()

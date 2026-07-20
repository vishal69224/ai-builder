import hashlib
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.paths import sanitize_relative_path
from app.models.artifact import ArtifactFile
from app.models.project import Project
from app.models.user import User
from app.providers.storage.local import LocalArtifactStorage


class FileService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = LocalArtifactStorage(get_settings().artifact_root)

    def _current_run(self, user: User, project_id: UUID) -> tuple[Project, UUID]:
        project = self.db.get(Project, project_id)
        if project is None or project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if project.current_run_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No generated files yet")
        return project, project.current_run_id

    def list_files(self, user: User, project_id: UUID) -> list[dict]:
        _, run_id = self._current_run(user, project_id)
        rows = self.db.scalars(select(ArtifactFile).where(ArtifactFile.run_id == run_id)).all()
        if rows:
            return [{"path": r.path, "size_bytes": r.size_bytes} for r in rows]
        return [{"path": p, "size_bytes": None} for p in self.storage.list_files(project_id, run_id)]

    def read_file(self, user: User, project_id: UUID, path: str) -> dict:
        project, run_id = self._current_run(user, project_id)
        rel = sanitize_relative_path(path)
        try:
            content = self.storage.read_file(project.id, run_id, rel).decode("utf-8")
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="File not found") from exc
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="Binary file cannot be displayed") from exc
        return {"path": rel, "content": content}

    def write_file(self, user: User, project_id: UUID, path: str, content: str) -> dict:
        project, run_id = self._current_run(user, project_id)
        rel = sanitize_relative_path(path)
        data = content.encode("utf-8")
        self.storage.write_file(project.id, run_id, rel, data)
        digest = hashlib.sha256(data).hexdigest()
        existing = self.db.scalar(
            select(ArtifactFile).where(ArtifactFile.run_id == run_id, ArtifactFile.path == rel)
        )
        if existing:
            existing.content_hash = digest
            existing.size_bytes = len(data)
        else:
            self.db.add(
                ArtifactFile(run_id=run_id, path=rel, content_hash=digest, size_bytes=len(data))
            )
        self.db.commit()
        return {"path": rel, "content": content}

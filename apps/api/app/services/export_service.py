import io
import zipfile
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.project import Project
from app.models.user import User
from app.providers.storage.local import LocalArtifactStorage


class ExportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.storage = LocalArtifactStorage(get_settings().artifact_root)

    def zip_current_run(self, user: User, project_id: UUID) -> tuple[bytes, str]:
        project = self.db.get(Project, project_id)
        if project is None or project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        if project.current_run_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No generated files yet")

        files = self.storage.list_files(project.id, project.current_run_id)
        if not files:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact tree is empty")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel in files:
                data = self.storage.read_file(project.id, project.current_run_id, rel)
                zf.writestr(rel, data)
        filename = f"{project.name.replace(' ', '-').lower() or 'project'}.zip"
        return buffer.getvalue(), filename

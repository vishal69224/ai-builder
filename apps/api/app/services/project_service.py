from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.deployment import Deployment
from app.models.enums import DeploymentStatus, ProjectStatus
from app.models.project import Project
from app.models.user import User
from app.schemas import ProjectCreate, ProjectUpdate
from app.services.generation_service import GenerationService


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_projects(self, user: User) -> list[Project]:
        stmt = (
            select(Project)
            .where(Project.user_id == user.id, Project.status != ProjectStatus.archived)
            .order_by(Project.updated_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_owned(self, user: User, project_id: UUID) -> Project:
        project = self.db.get(Project, project_id)
        if project is None or project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    def create(self, user: User, data: ProjectCreate) -> tuple[Project, object | None]:
        project = Project(
            user_id=user.id,
            name=data.name.strip(),
            description=data.description,
            status=ProjectStatus.active,
        )
        self.db.add(project)
        self.db.flush()
        self.db.add(
            Deployment(project_id=project.id, status=DeploymentStatus.not_configured)
        )
        run = None
        if data.prompt:
            run = GenerationService(self.db).enqueue(user, project, data.prompt)
        self.db.commit()
        self.db.refresh(project)
        if run is not None:
            self.db.refresh(run)
        return project, run

    def update(self, user: User, project_id: UUID, data: ProjectUpdate) -> Project:
        project = self.get_owned(user, project_id)
        if data.name is not None:
            project.name = data.name.strip()
        if data.description is not None:
            project.description = data.description
        if data.status is not None:
            try:
                project.status = ProjectStatus(data.status)
            except ValueError as exc:
                raise HTTPException(status_code=422, detail="Invalid status") from exc
        self.db.commit()
        self.db.refresh(project)
        return project

    def archive(self, user: User, project_id: UUID) -> None:
        project = self.get_owned(user, project_id)
        project.status = ProjectStatus.archived
        self.db.commit()

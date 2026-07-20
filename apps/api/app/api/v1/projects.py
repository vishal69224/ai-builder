from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas import GenerationOut, ProjectCreate, ProjectOut, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list:
    return ProjectService(db).list_projects(user)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> object:
    project, _ = ProjectService(db).create(user, payload)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> object:
    return ProjectService(db).get_owned(user, project_id)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> object:
    return ProjectService(db).update(user, project_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    ProjectService(db).archive(user, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{project_id}/generations", response_model=GenerationOut, status_code=status.HTTP_201_CREATED)
def create_generation(
    project_id: UUID,
    payload: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> object:
    from app.schemas import GenerationCreate
    from app.services.generation_service import GenerationService

    body = GenerationCreate.model_validate(payload)
    return GenerationService(db).start_for_project(user, project_id, body.prompt)


@router.get("/{project_id}/generations", response_model=list[GenerationOut])
def list_generations(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list:
    from app.services.generation_service import GenerationService

    return GenerationService(db).list_for_project(user, project_id)

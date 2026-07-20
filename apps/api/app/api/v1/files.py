from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas import FileContent, FileEntry, FileWrite, GenerationOut
from app.services.file_service import FileService
from app.services.generation_service import GenerationService

router = APIRouter(tags=["files-generations"])


@router.get("/generations/{run_id}", response_model=GenerationOut)
def get_generation(
    run_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> object:
    return GenerationService(db).get_owned(user, run_id)


@router.get("/projects/{project_id}/files", response_model=list[FileEntry])
def list_files(
    project_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list:
    return FileService(db).list_files(user, project_id)


@router.get("/projects/{project_id}/file", response_model=FileContent)
def read_file(
    project_id: UUID,
    path: str = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return FileService(db).read_file(user, project_id, path)


@router.put("/projects/{project_id}/file", response_model=FileContent)
def write_file(
    project_id: UUID,
    payload: FileWrite,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return FileService(db).write_file(user, project_id, payload.path, payload.content)

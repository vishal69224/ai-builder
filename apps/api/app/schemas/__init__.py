from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(ORMModel):
    id: UUID
    email: EmailStr
    name: str
    created_at: datetime


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    prompt: str | None = Field(default=None, min_length=1)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: str | None = None


class ProjectOut(ORMModel):
    id: UUID
    name: str
    description: str | None
    status: str
    current_run_id: UUID | None
    created_at: datetime
    updated_at: datetime


class GenerationCreate(BaseModel):
    prompt: str = Field(min_length=1)


class GenerationOut(ORMModel):
    id: UUID
    project_id: UUID
    prompt: str
    status: str
    error_message: str | None
    provider: str
    model: str
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class FileEntry(BaseModel):
    path: str
    size_bytes: int | None = None


class FileContent(BaseModel):
    path: str
    content: str


class FileWrite(BaseModel):
    path: str = Field(min_length=1, max_length=512)
    content: str

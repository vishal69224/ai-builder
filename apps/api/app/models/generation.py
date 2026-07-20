from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import GenerationStatus, enum_column

if TYPE_CHECKING:
    from app.models.artifact import ArtifactFile
    from app.models.project import Project


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[GenerationStatus] = enum_column(
        GenerationStatus,
        "generation_status",
        default=GenerationStatus.queued,
        index=True,
        nullable=False,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(64), default="openai_compatible", nullable=False)
    model: Mapped[str] = mapped_column(String(128), default="gpt-4o-mini", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    project: Mapped[Project] = relationship(
        "Project", back_populates="runs", foreign_keys=[project_id]
    )
    files: Mapped[list[ArtifactFile]] = relationship(
        "ArtifactFile", back_populates="run", cascade="all, delete-orphan"
    )

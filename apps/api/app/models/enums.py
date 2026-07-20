from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuthProvider(str, enum.Enum):
    local = "local"
    google = "google"


class ProjectStatus(str, enum.Enum):
    active = "active"
    archived = "archived"


class GenerationStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class DeploymentStatus(str, enum.Enum):
    not_configured = "not_configured"
    pending = "pending"
    live = "live"
    failed = "failed"


def enum_column(enum_cls: type[enum.Enum], name: str, **kwargs):
    # Portable across Postgres + SQLite
    return mapped_column(Enum(enum_cls, name=name, native_enum=False), **kwargs)

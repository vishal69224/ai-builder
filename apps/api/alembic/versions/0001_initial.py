"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    auth_provider = sa.Enum("local", "google", name="auth_provider")
    project_status = sa.Enum("active", "archived", name="project_status")
    generation_status = sa.Enum(
        "queued", "running", "succeeded", "failed", "cancelled", name="generation_status"
    )
    deployment_status = sa.Enum(
        "not_configured", "pending", "live", "failed", name="deployment_status"
    )

    auth_provider.create(op.get_bind(), checkfirst=True)
    project_status.create(op.get_bind(), checkfirst=True)
    generation_status.create(op.get_bind(), checkfirst=True)
    deployment_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("auth_provider", auth_provider, nullable=False),
        sa.Column("google_sub", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_sub"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", project_status, nullable=False),
        sa.Column("current_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"])

    op.create_table(
        "generation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("status", generation_status, nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_generation_runs_project_id", "generation_runs", ["project_id"])
    op.create_index("ix_generation_runs_user_id", "generation_runs", ["user_id"])
    op.create_index("ix_generation_runs_status", "generation_runs", ["status"])
    op.create_index("ix_generation_runs_created_at", "generation_runs", ["created_at"])

    op.create_foreign_key(
        "fk_projects_current_run",
        "projects",
        "generation_runs",
        ["current_run_id"],
        ["id"],
    )

    op.create_table(
        "artifact_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("generation_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("path", sa.String(512), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("run_id", "path", name="uq_artifact_run_path"),
    )
    op.create_index("ix_artifact_files_run_id", "artifact_files", ["run_id"])

    op.create_table(
        "deployments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", deployment_status, nullable=False),
        sa.Column("provider", sa.String(64), nullable=True),
        sa.Column("url", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_deployments_project_id", "deployments", ["project_id"])


def downgrade() -> None:
    op.drop_table("deployments")
    op.drop_table("artifact_files")
    op.drop_constraint("fk_projects_current_run", "projects", type_="foreignkey")
    op.drop_table("generation_runs")
    op.drop_table("projects")
    op.drop_table("users")
    sa.Enum(name="deployment_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="generation_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="project_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="auth_provider").drop(op.get_bind(), checkfirst=True)

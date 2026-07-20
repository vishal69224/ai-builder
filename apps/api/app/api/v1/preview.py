from uuid import UUID

import mimetypes
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.deps import get_current_user, get_db, get_optional_user
from app.core.security import TokenError, safe_decode_token
from app.domain.paths import sanitize_relative_path
from app.generation.preview.preview_engine import PreviewEngine
from app.models.project import Project
from app.models.user import User
from app.providers.storage.local import LocalArtifactStorage

router = APIRouter(prefix="/preview", tags=["preview"])
live_router = APIRouter(prefix="/preview-live", tags=["preview-live"])

_COOKIE_PREFIX = "preview_tok_"


def _authorize_project(
    project_id: UUID,
    db: Session,
    user: User | None,
    access_token: str | None,
    request: Request | None = None,
) -> tuple[Project, str | None]:
    token = access_token
    if not token and request is not None:
        token = request.cookies.get(f"{_COOKIE_PREFIX}{project_id}")

    resolved_user = user
    if resolved_user is None and token:
        try:
            payload = safe_decode_token(token)
            from uuid import UUID as UUIDType

            from app.models.user import User as UserModel

            resolved_user = db.get(UserModel, UUIDType(payload["sub"]))
        except (TokenError, KeyError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid token")

    if resolved_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    project = db.get(Project, project_id)
    if project is None or project.user_id != resolved_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project, token


def _fix_asset_urls(html: str, access_token: str | None) -> str:
    """Make absolute /assets paths relative; attach token so script tags can load."""
    html = html.replace('src="/assets/', 'src="./assets/')
    html = html.replace('href="/assets/', 'href="./assets/')
    if access_token:
        tok = access_token.replace('"', "")

        def _add(match: re.Match[str]) -> str:
            attr, url = match.group(1), match.group(2)
            joiner = "&" if "?" in url else "?"
            return f'{attr}="{url}{joiner}access_token={tok}"'

        html = re.sub(r'(src|href)="(\./assets/[^"]+)"', _add, html)
    return html


@router.get("/{project_id}")
@router.get("/{project_id}/{file_path:path}")
def preview_file(
    project_id: UUID,
    file_path: str = "preview.html",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    project = db.get(Project, project_id)
    if project is None or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.current_run_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No preview available")

    storage = LocalArtifactStorage(get_settings().artifact_root)
    rel = sanitize_relative_path(file_path or "preview.html")
    if not storage.exists(project.id, project.current_run_id, rel):
        for fallback in ("preview.html", "index.html"):
            if storage.exists(project.id, project.current_run_id, fallback):
                rel = fallback
                break
        else:
            raise HTTPException(status_code=404, detail="File not found")

    data = storage.read_file(project.id, project.current_run_id, rel)
    media_type = mimetypes.guess_type(rel)[0] or "application/octet-stream"
    return Response(content=data, media_type=media_type)


@live_router.get("/{project_id}")
@live_router.get("/{project_id}/{file_path:path}")
def preview_live(
    project_id: UUID,
    request: Request,
    file_path: str = "",
    access_token: str | None = Query(default=None),
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Serve built Vite dist (SDD §16 live preview after npm run build)."""
    project, token = _authorize_project(project_id, db, user, access_token, request)
    if project.current_run_id is None:
        raise HTTPException(status_code=404, detail="No preview available")

    engine = PreviewEngine()
    target = engine.resolve_live_file(project.id, project.current_run_id, file_path)
    if target is None:
        raise HTTPException(status_code=404, detail="Live preview not built yet — run generate first")

    media_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"

    # index.html needs rewritten asset URLs + auth cookie so JS/CSS can load
    if target.name == "index.html" or media_type == "text/html":
        html = target.read_text(encoding="utf-8")
        html = _fix_asset_urls(html, token)
        response = Response(content=html, media_type="text/html")
        if token:
            response.set_cookie(
                key=f"{_COOKIE_PREFIX}{project_id}",
                value=token,
                httponly=True,
                samesite="lax",
                max_age=60 * 60 * 12,
                path=f"/api/v1/preview-live/{project_id}",
            )
        return response

    return FileResponse(target, media_type=media_type)

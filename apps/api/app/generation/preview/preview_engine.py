"""SDD §16 Preview Engine — npm install, build, serve live preview."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from uuid import UUID

from app.core.config import get_settings

logger = logging.getLogger("preview_engine")


class PreviewEngine:
    def __init__(self) -> None:
        settings = get_settings()
        self.generated_root = Path(settings.generated_projects_root)
        self.build_timeout = settings.preview_build_timeout_seconds
        self.generated_root.mkdir(parents=True, exist_ok=True)

    def project_dir(self, project_id: UUID, run_id: UUID) -> Path:
        return self.generated_root / str(project_id) / str(run_id)

    def dist_dir(self, project_id: UUID, run_id: UUID) -> Path:
        return self.project_dir(project_id, run_id) / "dist"

    def sync_from_storage(self, storage_root: Path, project_id: UUID, run_id: UUID) -> Path:
        """Copy artifact tree into generated_projects for npm build."""
        src = storage_root / str(project_id) / str(run_id)
        dest = self.project_dir(project_id, run_id)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns("node_modules", "dist"))
        return dest

    def install_and_build(self, project_id: UUID, run_id: UUID) -> dict:
        """Run npm install && npm run build per SDD."""
        workdir = self.project_dir(project_id, run_id)
        if not (workdir / "package.json").exists():
            return {"ok": False, "error": "package.json not found", "preview_url": None}

        try:
            subprocess.run(
                ["npm", "install", "--prefer-offline", "--no-audit", "--no-fund"],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=self.build_timeout,
                check=True,
            )
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=self.build_timeout,
                check=True,
            )
            dist = self.dist_dir(project_id, run_id)
            ok = dist.exists() and (dist / "index.html").exists()
            return {
                "ok": ok,
                "preview_url": f"/api/v1/preview-live/{project_id}/" if ok else None,
                "mode": "built",
                "stdout": (result.stdout or "")[-500:],
            }
        except subprocess.TimeoutExpired:
            logger.warning("Preview build timed out for %s/%s", project_id, run_id)
            return {"ok": False, "error": "Build timed out", "preview_url": None}
        except subprocess.CalledProcessError as exc:
            logger.warning("Preview build failed: %s", exc.stderr or exc.stdout)
            return {
                "ok": False,
                "error": (exc.stderr or exc.stdout or str(exc))[-400:],
                "preview_url": None,
            }
        except FileNotFoundError:
            return {"ok": False, "error": "npm not found — install Node.js", "preview_url": None}

    def resolve_live_file(self, project_id: UUID, run_id: UUID, file_path: str) -> Path | None:
        dist = self.dist_dir(project_id, run_id)
        if not dist.exists():
            return None
        rel = file_path.strip("/") or "index.html"
        target = (dist / rel).resolve()
        if not str(target).startswith(str(dist.resolve())):
            return None
        if target.is_file():
            return target
        index = dist / "index.html"
        return index if index.is_file() else None

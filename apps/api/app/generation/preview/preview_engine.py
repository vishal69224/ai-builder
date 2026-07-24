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
        """Run npm install && vite build for live preview."""
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
        except subprocess.TimeoutExpired:
            logger.warning("npm install timed out for %s/%s", project_id, run_id)
            return {"ok": False, "error": "npm install timed out", "preview_url": None}
        except subprocess.CalledProcessError as exc:
            err = (exc.stderr or exc.stdout or str(exc))[-400:]
            logger.warning("npm install failed: %s", err)
            return {"ok": False, "error": err, "preview_url": None}
        except FileNotFoundError:
            return {"ok": False, "error": "npm not found — install Node.js", "preview_url": None}

        # Prefer vite build directly — generated TS often fails `tsc -b` but still ships fine
        build_cmds = [
            ["npm", "run", "build"],
            ["npx", "vite", "build"],
        ]
        last_error = ""
        for cmd in build_cmds:
            try:
                result = subprocess.run(
                    cmd,
                    cwd=workdir,
                    capture_output=True,
                    text=True,
                    timeout=self.build_timeout,
                    check=True,
                )
                dist = self.dist_dir(project_id, run_id)
                ok = dist.exists() and (dist / "index.html").exists()
                if ok:
                    return {
                        "ok": True,
                        "preview_url": f"/api/v1/preview-live/{project_id}/",
                        "mode": "built",
                        "stdout": (result.stdout or "")[-500:],
                    }
                last_error = "Build finished but dist/index.html missing"
            except subprocess.TimeoutExpired:
                last_error = "Build timed out"
                logger.warning("Preview build timed out for %s/%s via %s", project_id, run_id, cmd)
            except subprocess.CalledProcessError as exc:
                last_error = (exc.stderr or exc.stdout or str(exc))[-400:]
                logger.warning("Preview build failed via %s: %s", cmd, last_error)
            except FileNotFoundError:
                last_error = "vite/npm not found"
                break

        return {"ok": False, "error": last_error or "Build failed", "preview_url": None}

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

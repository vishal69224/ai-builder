import shutil
from pathlib import Path
from uuid import UUID

from app.domain.paths import sanitize_relative_path


class LocalArtifactStorage:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve_root(self, project_id: UUID, run_id: UUID) -> Path:
        return self.root / str(project_id) / str(run_id)

    def _safe_file(self, project_id: UUID, run_id: UUID, path: str) -> Path:
        rel = sanitize_relative_path(path)
        base = self.resolve_root(project_id, run_id).resolve()
        target = (base / rel).resolve()
        if not str(target).startswith(str(base)):
            raise ValueError("Path escapes artifact root")
        return target

    def write_file(self, project_id: UUID, run_id: UUID, path: str, content: bytes) -> None:
        target = self._safe_file(project_id, run_id, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def read_file(self, project_id: UUID, run_id: UUID, path: str) -> bytes:
        target = self._safe_file(project_id, run_id, path)
        return target.read_bytes()

    def list_files(self, project_id: UUID, run_id: UUID) -> list[str]:
        base = self.resolve_root(project_id, run_id)
        if not base.exists():
            return []
        files: list[str] = []
        for p in base.rglob("*"):
            if p.is_file():
                files.append(str(p.relative_to(base)).replace("\\", "/"))
        return sorted(files)

    def delete_tree(self, project_id: UUID, run_id: UUID) -> None:
        base = self.resolve_root(project_id, run_id)
        if base.exists():
            shutil.rmtree(base)

    def exists(self, project_id: UUID, run_id: UUID, path: str) -> bool:
        try:
            return self._safe_file(project_id, run_id, path).is_file()
        except ValueError:
            return False

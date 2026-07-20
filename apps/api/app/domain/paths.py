from pathlib import PurePosixPath


FORBIDDEN_SEGMENTS = {"", ".", ".."}


def sanitize_relative_path(path: str) -> str:
    raw = path.replace("\\", "/").strip()
    if raw.startswith("/"):
        raise ValueError("Absolute paths are not allowed")
    parts = PurePosixPath(raw).parts
    if not parts or any(p in FORBIDDEN_SEGMENTS for p in parts):
        raise ValueError(f"Invalid path: {path}")
    if any(p.startswith("/") for p in parts):
        raise ValueError(f"Invalid path: {path}")
    cleaned = str(PurePosixPath(*parts))
    if cleaned.startswith("..") or "/../" in f"/{cleaned}/":
        raise ValueError(f"Invalid path: {path}")
    return cleaned

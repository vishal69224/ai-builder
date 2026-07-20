from dataclasses import dataclass


@dataclass
class FileSpec:
    path: str
    content: str


@dataclass
class GenerationRequest:
    prompt: str
    project_name: str
    prior_files: list[FileSpec] | None = None


@dataclass
class GenerationResult:
    files: list[FileSpec]
    summary: str | None = None

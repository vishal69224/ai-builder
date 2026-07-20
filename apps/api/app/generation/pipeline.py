from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PromptAnalysis:
    website_type: str
    website_type_id: str
    confidence: float
    pages: list[str]
    components: list[str]
    theme: dict[str, Any]
    animations: list[str]
    libraries: list[str]
    icons: dict[str, Any]
    responsive: dict[str, Any]
    seo: dict[str, Any]
    framework: str = "React"
    styling: str = "Tailwind"
    color: str = "Light"
    tags: list[str] = field(default_factory=list)
    raw_prompt: str = ""
    sections: list[str] = field(default_factory=list)
    layout: str = "multi_page"  # multi_page | single_page
    brand_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StructuredRequirements:
    analysis: PromptAnalysis
    features: list[str]
    content_sections: list[str]
    cta_primary: str
    tone: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["analysis"] = self.analysis.to_dict()
        return data


@dataclass
class ProjectPlan:
    project_name: str
    routes: list[dict[str, str]]
    files: list[str]
    stack: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GeneratedFile:
    path: str
    content: str


@dataclass
class GenerationBundle:
    files: list[GeneratedFile]
    analysis: PromptAnalysis
    requirements: StructuredRequirements
    plan: ProjectPlan
    validation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "files": [{"path": f.path, "content": f.content} for f in self.files],
            "analysis": self.analysis.to_dict(),
            "requirements": self.requirements.to_dict(),
            "plan": self.plan.to_dict(),
            "validation": self.validation,
        }

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
    pages_explicit: bool = False  # True when user named specific pages / page count

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
class IntentSnapshot:
    """Thin adapter over PromptAnalysis for the v2 Website Planner (Phase 1)."""

    website_type: str
    website_type_id: str
    industry: str
    subcategory: str
    business_type: str
    target_audience: str
    brand_style: str
    design_style: str
    color_theme: str
    typography_style: str
    pages: list[str]
    sections: list[str]
    components: list[str]
    animations: list[str]
    tone: str
    product_types: list[str]
    forbidden_products: list[str]
    image_style: str
    seo_keywords: list[str]
    business_name: str
    confidence: float
    raw_prompt: str
    understanding_source: str = "rules_classifier"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WebsitePlanSection:
    id: str
    component: str
    variant: str
    props: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WebsitePlanPage:
    name: str
    path: str
    sections: list[WebsitePlanSection] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "sections": [s.to_dict() for s in self.sections],
        }


@dataclass
class WebsitePlan:
    """
    Source-of-truth plan for generation v2 (Phase 1+).
    Phase 1 only persists this artifact — legacy generators still emit the site.
    """

    version: str
    niche: str
    brand_name: str
    tagline: str
    intent: dict[str, Any]
    theme: dict[str, Any]
    typography: dict[str, Any]
    navbar: dict[str, Any]
    footer: dict[str, Any]
    hero: dict[str, Any]
    pages: list[WebsitePlanPage]
    product_types: list[str]
    forbidden_products: list[str]
    image_collections: list[str]
    animations: list[str]
    seo: dict[str, Any]
    components: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "niche": self.niche,
            "brand_name": self.brand_name,
            "tagline": self.tagline,
            "intent": self.intent,
            "theme": self.theme,
            "typography": self.typography,
            "navbar": self.navbar,
            "footer": self.footer,
            "hero": self.hero,
            "pages": [p.to_dict() for p in self.pages],
            "product_types": self.product_types,
            "forbidden_products": self.forbidden_products,
            "image_collections": self.image_collections,
            "animations": self.animations,
            "seo": self.seo,
            "components": self.components,
        }


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

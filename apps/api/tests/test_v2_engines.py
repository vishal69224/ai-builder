"""Phases 3–7 engine tests."""

from __future__ import annotations

from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
from app.generation.engines.component_engine import ComponentEngine
from app.generation.engines.content_engine import ContentEngine
from app.generation.engines.image_engine import ImageEngine
from app.generation.extractor.requirements import RequirementExtractor
from app.generation.generators.component_generator import ComponentGenerator
from app.generation.planner.project_planner import ProjectPlanner
from app.generation.planner.website_planner import WebsitePlanner
from app.generation.validation.semantic_validator import SemanticValidator
from app.generation.ai.ai_planner import AIPlanner


def _plan(prompt: str):
    analysis = PromptAnalyzer().analyze(prompt)
    requirements = RequirementExtractor().extract(analysis)
    website_plan = WebsitePlanner().plan_from_analysis(analysis, requirements=requirements)
    project_plan = ProjectPlanner().plan(requirements, website_plan.brand_name)
    return analysis, requirements, website_plan, project_plan


def test_content_clothing_excludes_sneakers():
    _, _, website_plan, _ = _plan("Create a branded clothing store")
    bag = ContentEngine().build(website_plan)
    assert bag["niche"] == "clothing"
    blob = " ".join(f"{p['name']} {p['category']}" for p in bag["products"]).lower()
    assert "sneaker" not in blob
    assert "shoe" not in blob
    assert "welcome to our website" not in bag["hero_headline"].lower()


def test_images_clothing_excludes_footwear_collections():
    _, _, website_plan, _ = _plan("Create a branded clothing store")
    images = ImageEngine().build(website_plan)
    assert "footwear" not in images["collections"]
    assert "sneakers" not in images["collections"]
    assert images["hero"]


def test_component_shells_emit_required_files():
    _, _, website_plan, _ = _plan("Create a branded clothing store")
    content = ContentEngine().build(website_plan)
    images = ImageEngine().build(website_plan)
    files = ComponentEngine().emit_shells(website_plan, content=content, images=images)
    paths = {f.path for f in files}
    assert "src/components/Navbar.tsx" in paths
    assert "src/components/Hero.tsx" in paths
    assert "src/components/Footer.tsx" in paths
    hero = next(f for f in files if f.path.endswith("Hero.tsx")).content
    assert "HeroFashion" in hero or "Velora" in hero or "Apparel" in hero


def test_niche_dispatch_clothing_not_shoes():
    _, requirements, website_plan, project_plan = _plan("Create a branded clothing store")
    files = ComponentGenerator().generate(requirements, project_plan, website_plan=website_plan)
    joined = "\n".join(f.content for f in files)
    # Fashion path uses kurta/saree style products, not sneaker Unsplash lists from footwear.py
    assert "kurta" in joined.lower() or "saree" in joined.lower() or "ProductGrid" in joined
    assert "generate_shoe_store" not in joined


def test_semantic_validator_passes_clothing():
    _, _, website_plan, project_plan = _plan("Create a branded clothing store")
    requirements = RequirementExtractor().extract(PromptAnalyzer().analyze("Create a branded clothing store"))
    files = ComponentGenerator().generate(requirements, project_plan, website_plan=website_plan)
    content = ContentEngine().build(website_plan)
    images = ImageEngine().build(website_plan)
    shells = ComponentEngine().emit_shells(website_plan, content=content, images=images)
    report = SemanticValidator().validate(
        website_plan=website_plan,
        files=list(files) + list(shells),
        content=content,
        images=images,
    )
    assert report["ok"], report["errors"]


def test_semantic_validator_fails_wrong_images():
    _, _, website_plan, _ = _plan("Create a branded clothing store")
    content = ContentEngine().build(website_plan)
    bad_images = {"niche": "clothing", "collections": ["footwear", "sneakers"], "hero": [], "products": [], "covers": []}
    report = SemanticValidator().validate(
        website_plan=website_plan,
        content=content,
        images=bad_images,
    )
    assert not report["ok"]
    assert any("footwear" in e or "collection" in e for e in report["errors"])


def test_ai_planner_noop_without_key():
    analysis, _, website_plan, _ = _plan("Create a branded clothing store")
    out = AIPlanner().maybe_enrich(analysis, website_plan)
    assert out.niche == website_plan.niche
    assert out.brand_name == website_plan.brand_name

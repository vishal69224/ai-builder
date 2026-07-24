"""Phase 1 — Website Planner unit tests (no Vite / no DB)."""

from __future__ import annotations

import json
from pathlib import Path

from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
from app.generation.extractor.requirements import RequirementExtractor
from app.generation.planner.niches import NICHES, invent_brand_name, resolve_niche
from app.generation.planner.website_planner import WebsitePlanner


def _plan(prompt: str):
    analysis = PromptAnalyzer().analyze(prompt)
    requirements = RequirementExtractor().extract(analysis)
    return WebsitePlanner().plan_from_analysis(analysis, requirements=requirements), analysis


def test_niche_registry_has_twenty_three_plus_generic():
    # 22 specialty + footwear + blog + generic extras — at least the planned set
    required = {
        "clothing",
        "footwear",
        "electronics",
        "restaurant",
        "coffee_shop",
        "bakery",
        "portfolio",
        "agency",
        "jewelry",
        "furniture",
        "medical",
        "travel",
        "gym",
        "education",
        "law_firm",
        "finance",
        "bookstore",
        "real_estate",
        "hotel",
        "photography",
        "automobile",
        "wedding",
        "salon",
        "blog",
        "generic",
    }
    assert required.issubset(set(NICHES))


def test_clothing_prompt_plans_clothing_not_footwear():
    plan, analysis = _plan("Create a branded clothing store")
    assert plan.niche == "clothing"
    assert "Sneakers" in plan.forbidden_products or "Shoes" in plan.forbidden_products
    assert "T-Shirts" in plan.product_types
    assert plan.brand_name != "Fashion Brand"
    assert plan.hero["variant"] == "HeroFashion"
    assert plan.theme["token_preset"] == "luxury_minimal"
    assert "fashion" in plan.image_collections
    assert "footwear" not in plan.image_collections
    data = plan.to_dict()
    assert data["intent"]["industry"] == "Fashion"
    assert data["pages"]
    # Analyzer may still say fashion_brand — plan niche is what matters for v2
    assert "fashion" in analysis.website_type_id or analysis.website_type_id.startswith("fashion")


def test_shoe_prompt_plans_footwear():
    plan, _ = _plan("Create a shoe store for sneakers")
    assert plan.niche == "footwear"
    assert "Sneakers" in plan.product_types
    assert "T-Shirts" in plan.forbidden_products
    assert "footwear" in plan.image_collections or "sneakers" in plan.image_collections


def test_mixed_clothing_and_shoes_prefers_explicit_keywords():
    # Both signals present — niche resolver should pick one consistently (footwear or clothing)
    niche = resolve_niche("fashion_brand", "create a branded clothing and shoe store")
    assert niche.id in {"clothing", "footwear"}


def test_seo_blog_plans_blog_niche():
    plan, _ = _plan("create SEO blog website for digital marketing tips")
    assert plan.niche == "blog"
    assert plan.brand_name  # non-empty
    assert any(p.name == "Articles" or p.name == "Home" for p in plan.pages)


def test_website_plan_schema_required_keys():
    plan, _ = _plan("Create a branded clothing store")
    data = plan.to_dict()
    schema_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "generation"
        / "planner"
        / "schemas"
        / "website_plan.schema.json"
    )
    schema = json.loads(schema_path.read_text())
    for key in schema["required"]:
        assert key in data, f"missing {key}"


def test_invent_brand_avoids_catalog_labels():
    clothing = NICHES["clothing"]
    assert invent_brand_name("Fashion Brand", clothing) == "Velora"
    assert invent_brand_name("Acme Apparel", clothing) == "Acme Apparel"


def test_plan_json_roundtrip_serializable():
    plan, _ = _plan("Build a modern coffee shop website")
    raw = json.dumps(plan.to_dict())
    loaded = json.loads(raw)
    assert loaded["niche"] == "coffee_shop"
    assert loaded["brand_name"]

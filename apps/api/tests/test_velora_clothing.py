"""VELORA / clothing vs shoe misroute regression tests."""

from __future__ import annotations

VELORA = '''Create a premium luxury fashion clothing brand website called "VELORA".

The website should exclusively sell clothing and fashion accessories.

IMPORTANT:
Do NOT generate a shoe store.
Do NOT generate sportswear.
Do NOT use sneakers, boots, sandals, football shoes, running shoes, or athletic products.
Shoes should never appear as featured or primary products.

Target Audience:
- Men
- Women
- Young Adults
- Fashion Enthusiasts

Brand Style:
Luxury, Minimal, Modern, Elegant

Create the following pages:
- Home
- Shop
- Men
- Women
- New Arrivals
- Collections
- About
- Contact

Products should include only:
- Oversized T-Shirts
- Hoodies
- Jeans
- Dresses
- Blazers

Avoid:
- Shoes
- Sneakers
- Boots
'''


def test_velora_prompt_is_clothing_not_shoes():
    from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
    from app.generation.planner.website_planner import WebsitePlanner
    from app.generation.extractor.requirements import RequirementExtractor
    from app.generation.generators.component_generator import ComponentGenerator
    from app.generation.planner.project_planner import ProjectPlanner

    analysis = PromptAnalyzer().analyze(VELORA)
    assert "shoe" not in analysis.website_type_id
    assert "sneaker" not in analysis.website_type_id
    assert "fashion" in analysis.website_type_id or "clothing" in analysis.website_type_id
    assert analysis.brand_name.upper() == "VELORA"

    reqs = RequirementExtractor().extract(analysis)
    plan = WebsitePlanner().plan_from_analysis(analysis, requirements=reqs)
    assert plan.niche == "clothing"
    assert plan.brand_name.upper() == "VELORA"

    project_plan = ProjectPlanner().plan(reqs, plan.brand_name)
    files = ComponentGenerator().generate(reqs, project_plan, website_plan=plan)
    joined = "\n".join(f.content for f in files)
    assert "photo-1542291026" not in joined  # classic sneaker hero from footwear.py
    assert "src/data/catalog.ts" in {f.path for f in files}
    assert "Oversized" in joined or "Hoodie" in joined or "Blazer" in joined
    assert "VELORA" in joined
    # Must not be shoe store copy
    assert "Steps built for momentum" not in joined
    assert "FashionHero" in joined or "StoreNavbar" in joined

def test_sanitize_removes_avoid_shoes():
    from app.generation.understanding.intent_guards import (
        explicitly_forbids_footwear,
        has_strong_clothing_intent,
        positive_footwear_intent,
        sanitize_prompt_for_matching,
    )

    assert has_strong_clothing_intent(VELORA)
    assert explicitly_forbids_footwear(VELORA)
    assert not positive_footwear_intent(VELORA)
    cleaned = sanitize_prompt_for_matching(VELORA)
    assert "sneakers" not in cleaned or "clothing" in cleaned

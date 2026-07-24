"""Video generator / SaaS casual prompt — must not dump raw prompt into hero."""

from __future__ import annotations

VIDEO_PROMPT = (
    "i want to make one attarctive video ganerator website design give me that website design full website"
)


def test_video_generator_prompt_routes_to_saas_and_builds_product_site():
    from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
    from app.generation.extractor.requirements import RequirementExtractor
    from app.generation.generators.component_generator import ComponentGenerator
    from app.generation.planner.project_planner import ProjectPlanner
    from app.generation.planner.website_planner import WebsitePlanner

    analysis = PromptAnalyzer().analyze(VIDEO_PROMPT)
    assert analysis.website_type_id in {"saas_startup", "ai_product", "landing_page"}

    reqs = RequirementExtractor().extract(analysis)
    website_plan = WebsitePlanner().plan_from_analysis(analysis, requirements=reqs)
    assert website_plan.niche == "saas"
    assert website_plan.brand_name == "LumaClip"
    assert "i want" not in website_plan.brand_name.lower()

    project_plan = ProjectPlanner().plan(reqs, website_plan.brand_name)
    files = ComponentGenerator().generate(reqs, project_plan, website_plan=website_plan)
    by_path = {f.path: f.content for f in files}

    home = by_path["src/pages/HomePage.tsx"]
    assert "ProductHero" in home
    assert "FeatureGrid" in home
    assert "PricingTable" in home
    assert "DemoWidget" in home

    hero = by_path["src/components/ProductHero.tsx"]
    assert "attarctive" not in hero.lower()
    assert "ganerator" not in hero.lower()
    assert "give me that website" not in hero.lower()
    assert "AI Video Generator" in hero or "video" in hero.lower()
    assert "LumaClip" in hero

    product = by_path["src/data/product.ts"]
    assert 'productKind = "video"' in product
    assert "Turn ideas into stunning videos" in product or "video" in product.lower()


def test_tagline_never_echoes_instruction_prompt():
    from app.generation.generators.component_generator import _tagline

    tag = _tagline(VIDEO_PROMPT, "SaaS Startup", "LumaClip")
    assert "i want" not in tag.lower()
    assert "give me" not in tag.lower()
    assert "video" in tag.lower()

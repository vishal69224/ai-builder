"""Prompt-faithful page planning — explicit page lists win over niche defaults."""

from __future__ import annotations

PROMPT = (
    "I want to create an website for a shoe brand. it has three page. "
    "home page, contact page and about page. to can see reference of a luxury "
    "shoe brand and it should be like proper ui and ux in tha."
)


def test_three_page_shoe_prompt_respects_exact_pages():
    from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
    from app.generation.extractor.requirements import RequirementExtractor
    from app.generation.generators.component_generator import ComponentGenerator
    from app.generation.planner.project_planner import ProjectPlanner
    from app.generation.planner.website_planner import WebsitePlanner

    analysis = PromptAnalyzer().analyze(PROMPT)
    assert analysis.pages_explicit is True
    assert analysis.pages == ["Home", "Contact", "About"]
    assert "Shop" not in analysis.pages
    assert "Lookbook" not in analysis.pages
    assert "And About Page" not in analysis.pages

    reqs = RequirementExtractor().extract(analysis)
    wp = WebsitePlanner().plan_from_analysis(analysis, requirements=reqs)
    page_names = [p.name for p in wp.pages]
    assert page_names == ["Home", "Contact", "About"]

    plan = ProjectPlanner().plan(reqs, wp.brand_name)
    routes = [r["page"] for r in plan.routes]
    assert routes == ["Home", "Contact", "About"]

    files = ComponentGenerator().generate(reqs, plan, website_plan=wp)
    by = {f.path: f.content for f in files}
    assert "src/pages/HomePage.tsx" in by
    assert "src/pages/AboutPage.tsx" in by
    assert "src/pages/ContactPage.tsx" in by
    assert "src/pages/ShopPage.tsx" not in by
    assert "src/pages/LookbookPage.tsx" not in by
    assert "src/components/ShoeGrid.tsx" not in by
    assert "Aero Run Pro" not in "\n".join(by.values())
    assert "And About Page" not in "\n".join(by.values())
    home = by["src/pages/HomePage.tsx"]
    assert "ShoeHero" in home
    assert "ShoeStory" in home
    assert "ShoeGrid" not in home


def test_shop_requested_still_gets_shop():
    from app.generation.analyzer.prompt_analyzer import PromptAnalyzer

    analysis = PromptAnalyzer().analyze(
        "Create a shoe brand website with Home, Shop, and Contact pages called 'Nova Step'."
    )
    assert analysis.pages_explicit is True
    assert analysis.pages == ["Home", "Shop", "Contact"]
    assert analysis.brand_name == "Nova Step"

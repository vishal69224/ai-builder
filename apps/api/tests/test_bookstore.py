"""Online bookstore prompt must not become a marketing landing page."""

from __future__ import annotations

PROMPT = (
    "i want to build online book store where user can buy and read books "
    "and search all the books and download the books pdf so make it and "
    "responsive and perfect layout ui ux"
)


def test_bookstore_prompt_builds_real_store():
    from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
    from app.generation.extractor.requirements import RequirementExtractor
    from app.generation.generators.component_generator import ComponentGenerator
    from app.generation.planner.project_planner import ProjectPlanner
    from app.generation.planner.website_planner import WebsitePlanner

    analysis = PromptAnalyzer().analyze(PROMPT)
    assert "book" in analysis.website_type_id
    assert analysis.website_type_id != "landing_page"
    assert "Marketing" not in analysis.website_type

    reqs = RequirementExtractor().extract(analysis)
    wp = WebsitePlanner().plan_from_analysis(analysis, requirements=reqs)
    assert wp.niche == "bookstore"
    page_names = [p.name for p in wp.pages]
    assert "Browse" in page_names or "Shop" in page_names
    assert "Library" in page_names or "Cart" in page_names
    assert page_names != ["Home"]

    plan = ProjectPlanner().plan(reqs, wp.brand_name)
    routes = [r["page"] for r in plan.routes]
    assert len(routes) >= 3
    assert "Home" in routes

    files = ComponentGenerator().generate(reqs, plan, website_plan=wp)
    by = {f.path: f.content for f in files}
    joined = "\n".join(by.values())

    assert "MARKETING LANDING PAGE" not in joined
    assert "src/data/catalog.ts" in by
    assert "searchBooks" in by["src/data/catalog.ts"]
    assert "BookCard" in joined
    assert "Download PDF" in joined or "download" in joined.lower()
    assert "Browse" in joined or "/browse" in joined
    assert "Library" in joined or "/library" in joined
    assert "Cart" in joined or "/cart" in joined
    assert "useBookStore" in joined

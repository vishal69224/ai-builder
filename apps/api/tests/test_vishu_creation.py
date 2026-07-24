"""Vishu Creation casual prompt — brand must not leak instructional text."""

from __future__ import annotations

VISHU = (
    "i want to create branding clothing website with an 3D view my cloth shop name is "
    "Vishu Creation so create that logo also and give me responsive website with best "
    "color combination.and here customor can sign in and sign up with his email or phone "
    "and easy to use and see our collection of branding so create that attractive website."
)


def test_vishu_brand_is_clean_not_full_prompt():
    from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
    from app.generation.extractor.requirements import RequirementExtractor
    from app.generation.generators.component_generator import ComponentGenerator
    from app.generation.generators.router_generator import RouterGenerator
    from app.generation.planner.project_planner import ProjectPlanner
    from app.generation.planner.website_planner import WebsitePlanner

    analysis = PromptAnalyzer().analyze(VISHU)
    assert analysis.brand_name == "Vishu Creation"
    assert "so create" not in analysis.brand_name.lower()
    assert "responsive" not in analysis.brand_name.lower()
    assert "Login" in analysis.pages
    assert "Register" in analysis.pages

    reqs = RequirementExtractor().extract(analysis)
    website_plan = WebsitePlanner().plan_from_analysis(analysis, requirements=reqs)
    assert website_plan.niche == "clothing"
    assert website_plan.brand_name == "Vishu Creation"

    project_plan = ProjectPlanner().plan(reqs, website_plan.brand_name)
    paths = {r["path"] for r in project_plan.routes}
    assert "/login" in paths
    assert "/register" in paths
    assert "/shop" in paths
    assert "/lookbook" in paths

    files = ComponentGenerator().generate(reqs, project_plan, website_plan=website_plan)
    by_path = {f.path: f.content for f in files}

    catalog = by_path["src/data/catalog.ts"]
    assert 'export const brandName = "Vishu Creation"' in catalog
    assert "so create that logo" not in catalog.lower()

    nav = by_path["src/components/StoreNavbar.tsx"]
    assert "BrandLogo" in nav
    assert "Vishu Creation so create" not in nav

    assert "src/components/BrandLogo.tsx" in by_path
    assert "src/pages/LoginPage.tsx" in by_path
    assert "src/pages/RegisterPage.tsx" in by_path
    assert "src/pages/LookbookPage.tsx" in by_path
    assert "email" in by_path["src/components/AuthForm.tsx"].lower()
    assert "phone" in by_path["src/components/AuthForm.tsx"].lower()

    router_files = RouterGenerator().generate(project_plan)
    app = next(f.content for f in router_files if f.path == "src/App.tsx")
    assert "LoginPage" in app
    assert "RegisterPage" in app
    assert "LookbookPage" in app
    assert 'path="/login"' in app or "path=\"/login\"" in app

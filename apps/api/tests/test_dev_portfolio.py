"""Developer portfolio generation regression tests."""

from __future__ import annotations

PROMPT = (
    "i am a flutter developer and python also so i want to make one portfolio "
    "so give me the perfect portfolio template so can edit it and make it my portfolio"
)


def test_flutter_python_prompt_routes_to_portfolio():
    from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
    from app.generation.extractor.requirements import RequirementExtractor
    from app.generation.generators.component_generator import ComponentGenerator
    from app.generation.planner.project_planner import ProjectPlanner
    from app.generation.planner.website_planner import WebsitePlanner

    analysis = PromptAnalyzer().analyze(PROMPT)
    reqs = RequirementExtractor().extract(analysis)
    plan = WebsitePlanner().plan_from_analysis(analysis, requirements=reqs)
    assert plan.niche == "portfolio"

    project_plan = ProjectPlanner().plan(reqs, plan.brand_name)
    files = ComponentGenerator().generate(reqs, project_plan, website_plan=plan)
    by_path = {f.path: f.content for f in files}

    assert "src/data/portfolio.ts" in by_path
    assert "src/components/PortfolioHero.tsx" in by_path
    assert "src/pages/HomePage.tsx" in by_path

    data = by_path["src/data/portfolio.ts"]
    assert "Flutter" in data
    assert "Python" in data
    assert "style" in data

    home = by_path["src/pages/HomePage.tsx"]
    assert "PortfolioHero" in home
    assert "ExperienceSection" in home
    assert "ProjectsSection" in home
    assert len(home) > 400


def test_portfolio_styles_differ_by_prompt():
    from app.generation.generators.dev_portfolio import pick_style

    assert pick_style("clean minimal light portfolio").id == "paper"
    assert pick_style("bold colorful modern portfolio").id == "signal"
    assert pick_style("terminal cyber portfolio").id == "terminal"
    assert pick_style("dark neon night portfolio").id == "aurora"

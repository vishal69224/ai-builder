"""Phase 2 — Theme Engine unit tests."""

from __future__ import annotations

from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
from app.generation.engines.theme_engine import THEME_PRESETS, ThemeEngine
from app.generation.extractor.requirements import RequirementExtractor
from app.generation.generators.css_generator import CssGenerator
from app.generation.planner.niches import NICHES
from app.generation.planner.website_planner import WebsitePlanner


def _clothing_plan():
    analysis = PromptAnalyzer().analyze("Create a branded clothing store")
    requirements = RequirementExtractor().extract(analysis)
    plan = WebsitePlanner().plan_from_analysis(analysis, requirements=requirements)
    return plan, requirements


def test_all_niche_presets_exist():
    missing = []
    for niche in NICHES.values():
        if niche.token_preset not in THEME_PRESETS:
            missing.append(f"{niche.id}:{niche.token_preset}")
    assert not missing, f"Missing presets: {missing}"


def test_clothing_resolves_luxury_minimal():
    plan, _ = _clothing_plan()
    tokens = ThemeEngine().resolve_from_plan(plan)
    assert tokens["id"] == "luxury_minimal"
    assert tokens["colors"]["primary"].startswith("#")
    assert tokens["colors"]["brand"] == tokens["colors"]["primary"]
    assert tokens["radius"]
    assert tokens["font"]


def test_css_variables_include_design_tokens():
    plan, _ = _clothing_plan()
    engine = ThemeEngine()
    css = engine.to_css_variables(engine.resolve_from_plan(plan))
    assert "--color-primary:" in css
    assert "--color-accent:" in css
    assert "--radius:" in css
    assert "--font-body:" in css
    assert "--brand:" in css


def test_css_generator_flag_on_uses_theme_engine():
    plan, requirements = _clothing_plan()
    files = CssGenerator().generate(requirements, website_plan=plan, use_theme_engine=True)
    css = next(f for f in files if f.path == "src/index.css").content
    assert "--color-primary:" in css
    assert "--color-accent:" in css
    assert "luxury" in css.lower() or "#111827" in css or "Luxury Minimal" in css
    assert "vite.config.ts" in {f.path for f in files}


def test_css_generator_flag_off_matches_legacy_shape():
    plan, requirements = _clothing_plan()
    files = CssGenerator().generate(requirements, website_plan=plan, use_theme_engine=False)
    css = next(f for f in files if f.path == "src/index.css").content
    assert "--brand:" in css
    assert "--style:" in css
    assert "--bg:" in css
    assert "--text:" in css
    # Phase 2 tokens should NOT appear in legacy mode
    assert "--color-accent:" not in css
    assert "--radius:" not in css


def test_tech_dark_preset_is_dark_mode():
    tokens = ThemeEngine().resolve_preset("tech_dark")
    assert tokens["mode"] == "dark"
    assert tokens["colors"]["bg"].startswith("#0")

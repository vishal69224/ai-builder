from __future__ import annotations

from typing import Any

from app.core.config import get_settings
from app.generation.pipeline import GeneratedFile, StructuredRequirements, WebsitePlan


class CssGenerator:
    """SDD §11 Styling Generator — Tailwind CSS with theme tokens.

    Phase 2: when GEN_V2_THEME=true and a WebsitePlan is provided, tokens come from
    ThemeEngine. Otherwise behavior matches the legacy generator exactly.
    """

    def generate(
        self,
        requirements: StructuredRequirements,
        *,
        website_plan: WebsitePlan | dict[str, Any] | None = None,
        use_theme_engine: bool | None = None,
    ) -> list[GeneratedFile]:
        settings = get_settings()
        enabled = settings.gen_v2_theme if use_theme_engine is None else use_theme_engine

        if enabled and website_plan is not None:
            return self._generate_from_theme_engine(website_plan, requirements)

        return self._generate_legacy(requirements)

    def _generate_legacy(self, requirements: StructuredRequirements) -> list[GeneratedFile]:
        analysis = requirements.analysis
        primary = analysis.theme.get("primary_color", "#0f172a")
        style = analysis.theme.get("style", "modern")
        prompt = (analysis.raw_prompt or "").lower()
        # Fashion / clothing should stay light-editorial by default — "luxury"
        # must not force a near-black page background (causes empty dark voids).
        fashionish = any(
            w in prompt for w in ("clothing", "fashion", "apparel", "boutique", "atelier")
        )
        portfolioish = any(
            w in prompt for w in ("portfolio", "developer", "flutter", "resume", "hire me")
        )
        saasish = any(
            w in prompt for w in ("saas", "startup", "ai video", "ai tool", "product landing")
        )
        is_dark = (not fashionish) and (
            style in {"dark", "neon"} or "dark mode" in prompt or "dark theme" in prompt
        )

        bg = "#0a0f1a" if is_dark else ("#FAFAF8" if fashionish else "#f8fafc")
        text = "#e2e8f0" if is_dark else "#0f172a"
        niche = "clothing" if fashionish else ("portfolio" if portfolioish else ("saas" if saasish else "default"))

        root_vars = (
            f"  --brand: {primary};\n"
            f"  --style: {style};\n"
            f"  --bg: {bg};\n"
            f"  --text: {text};\n"
            + self._font_vars(niche)
        )
        return self._files(root_vars, niche=niche)

    def _generate_from_theme_engine(
        self,
        website_plan: WebsitePlan | dict[str, Any],
        requirements: StructuredRequirements | None = None,
    ) -> list[GeneratedFile]:
        from app.generation.engines.theme_engine import ThemeEngine

        engine = ThemeEngine()
        tokens = engine.resolve_from_plan(website_plan)
        root_vars = engine.to_css_variables(tokens) + "\n"
        niche = getattr(website_plan, "niche", None)
        if niche is None and isinstance(website_plan, dict):
            niche = website_plan.get("niche")
        niche_key = niche if niche in {"clothing", "portfolio", "saas"} else "default"
        if niche_key == "default" and requirements is not None:
            prompt = (requirements.analysis.raw_prompt or "").lower()
            if any(w in prompt for w in ("clothing", "fashion", "apparel")):
                niche_key = "clothing"
            elif any(w in prompt for w in ("portfolio", "developer", "flutter")):
                niche_key = "portfolio"
            elif any(w in prompt for w in ("saas", "startup", "ai video")):
                niche_key = "saas"
        # Ensure display fonts exist even when theme engine omitted them
        if "--font-display" not in root_vars:
            root_vars += self._font_vars(niche_key)
        return self._files(root_vars, niche=niche_key)

    def _font_vars(self, niche: str) -> str:
        if niche == "clothing":
            return (
                '  --font-display: "Cormorant Garamond", Georgia, serif;\n'
                '  --font-body: "DM Sans", "Segoe UI", sans-serif;\n'
                "  font-family: var(--font-body);\n"
            )
        if niche == "portfolio":
            return (
                '  --font-display: "Space Grotesk", "Segoe UI", sans-serif;\n'
                '  --font-body: "DM Sans", "Segoe UI", sans-serif;\n'
                "  font-family: var(--font-body);\n"
            )
        if niche == "saas":
            return (
                '  --font-display: "Plus Jakarta Sans", "Segoe UI", sans-serif;\n'
                '  --font-body: "Plus Jakarta Sans", "Segoe UI", sans-serif;\n'
                "  font-family: var(--font-body);\n"
            )
        return '  font-family: "Segoe UI", system-ui, sans-serif;\n'

    def _font_import(self, niche: str) -> str:
        if niche == "clothing":
            return '@import url("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap");\n\n'
        if niche == "portfolio":
            return '@import url("https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap");\n\n'
        if niche == "saas":
            return '@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap");\n\n'
        return ""

    def _files(self, root_vars: str, *, niche: str = "default", fashion: bool = False) -> list[GeneratedFile]:
        if fashion:
            niche = "clothing"
        font_import = self._font_import(niche)
        serif_util = (
            ".font-serif { font-family: var(--font-display, Georgia, serif); }\n"
            "h1, h2, h3 { font-family: var(--font-display, inherit); }\n"
            if niche in {"clothing", "portfolio", "saas"}
            else ""
        )
        dark_body = (
            ".dark body {\n"
            "  --bg: #0c0a09;\n"
            "  --text: #fafaf9;\n"
            "  background: #0c0a09;\n"
            "  color: #fafaf9;\n"
            "}\n\n"
            if niche == "clothing"
            else (
                ".dark body {\n"
                "  background: var(--bg);\n"
                "  color: var(--text);\n"
                "}\n\n"
            )
        )
        return [
            GeneratedFile(
                path="src/index.css",
                content=(
                    '@import "tailwindcss";\n\n'
                    f"{font_import}"
                    ":root {\n"
                    f"{root_vars}"
                    "}\n\n"
                    "body {\n"
                    "  margin: 0;\n"
                    "  min-height: 100vh;\n"
                    "  overflow-x: hidden;\n"
                    "  background: var(--bg);\n"
                    "  color: var(--text);\n"
                    "}\n\n"
                    f"{dark_body}"
                    f"{serif_util}"
                    "@keyframes fadeUp {\n"
                    "  from { opacity: 0; transform: translateY(16px); }\n"
                    "  to { opacity: 1; transform: translateY(0); }\n"
                    "}\n"
                    "html { scroll-behavior: smooth; }\n"
                ),
            ),
            GeneratedFile(
                path="vite.config.ts",
                content=(
                    "import { defineConfig } from 'vite'\n"
                    "import react from '@vitejs/plugin-react'\n"
                    "import tailwindcss from '@tailwindcss/vite'\n\n"
                    "export default defineConfig({\n"
                    "  base: './',\n"
                    "  plugins: [react(), tailwindcss()],\n"
                    "  server: { port: 5173 },\n"
                    "})\n"
                ),
            ),
        ]

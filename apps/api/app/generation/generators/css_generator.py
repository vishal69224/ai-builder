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
            return self._generate_from_theme_engine(website_plan)

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
        is_dark = (not fashionish) and (
            style in {"dark", "neon"} or "dark mode" in prompt or "dark theme" in prompt
        )

        bg = "#0a0f1a" if is_dark else ("#FAFAF8" if fashionish else "#f8fafc")
        text = "#e2e8f0" if is_dark else "#0f172a"

        root_vars = (
            f"  --brand: {primary};\n"
            f"  --style: {style};\n"
            f"  --bg: {bg};\n"
            f"  --text: {text};\n"
            + (
                '  --font-display: "Cormorant Garamond", Georgia, serif;\n'
                '  --font-body: "DM Sans", "Segoe UI", sans-serif;\n'
                "  font-family: var(--font-body);\n"
                if fashionish
                else '  font-family: "Segoe UI", system-ui, sans-serif;\n'
            )
        )
        return self._files(root_vars, fashion=fashionish)

    def _generate_from_theme_engine(self, website_plan: WebsitePlan | dict[str, Any]) -> list[GeneratedFile]:
        from app.generation.engines.theme_engine import ThemeEngine

        engine = ThemeEngine()
        tokens = engine.resolve_from_plan(website_plan)
        root_vars = engine.to_css_variables(tokens) + "\n"
        niche = getattr(website_plan, "niche", None)
        if niche is None and isinstance(website_plan, dict):
            niche = website_plan.get("niche")
        return self._files(root_vars, fashion=niche == "clothing")

    def _files(self, root_vars: str, *, fashion: bool = False) -> list[GeneratedFile]:
        font_import = (
            '@import url("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap");\n\n'
            if fashion
            else ""
        )
        serif_util = (
            ".font-serif { font-family: var(--font-display, Georgia, serif); }\n"
            if fashion
            else ""
        )
        dark_body = (
            ".dark body {\n"
            "  --bg: #0c0a09;\n"
            "  --text: #fafaf9;\n"
            "  background: #0c0a09;\n"
            "  color: #fafaf9;\n"
            "}\n\n"
            if fashion
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

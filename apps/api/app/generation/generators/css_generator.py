from app.generation.pipeline import GeneratedFile, StructuredRequirements


class CssGenerator:
    """SDD §11 Styling Generator — Tailwind CSS with theme tokens."""

    def generate(self, requirements: StructuredRequirements) -> list[GeneratedFile]:
        analysis = requirements.analysis
        primary = analysis.theme.get("primary_color", "#0f172a")
        style = analysis.theme.get("style", "modern")
        is_dark = style in {"dark", "luxury", "neon"} or "dark" in analysis.raw_prompt.lower()

        bg = "#0a0f1a" if is_dark else "#f8fafc"
        text = "#e2e8f0" if is_dark else "#0f172a"

        return [
            GeneratedFile(
                path="src/index.css",
                content=(
                    "@import \"tailwindcss\";\n\n"
                    ":root {\n"
                    f"  --brand: {primary};\n"
                    f"  --style: {style};\n"
                    f"  --bg: {bg};\n"
                    f"  --text: {text};\n"
                    "  font-family: \"Segoe UI\", system-ui, sans-serif;\n"
                    "}\n\n"
                    "body {\n"
                    "  margin: 0;\n"
                    "  min-height: 100vh;\n"
                    "  background: var(--bg);\n"
                    "  color: var(--text);\n"
                    "}\n\n"
                    ".dark body {\n"
                    "  background: var(--bg);\n"
                    "  color: var(--text);\n"
                    "}\n\n"
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

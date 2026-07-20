from app.generation.pipeline import GeneratedFile, StructuredRequirements


class TailwindGenerator:
    def generate(self, requirements: StructuredRequirements) -> list[GeneratedFile]:
        primary = requirements.analysis.theme.get("primary_color", "#0f172a")
        style = requirements.analysis.theme.get("style", "modern")
        return [
            GeneratedFile(
                path="src/index.css",
                content=f"""@import "tailwindcss";

:root {{
  --brand: {primary};
  --style: {style};
  font-family: "Segoe UI", system-ui, sans-serif;
  color: #0f172a;
  background: #f8fafc;
}}

body {{
  margin: 0;
  min-height: 100vh;
}}
""",
            ),
            GeneratedFile(
                path="vite.config.ts",
                content="""import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
""",
            ),
        ]

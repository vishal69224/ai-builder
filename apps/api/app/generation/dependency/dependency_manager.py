from __future__ import annotations

from app.generation.pipeline import GeneratedFile, StructuredRequirements


class DependencyManager:
    """SDD §15 — install React, Router, Tailwind, Axios, Framer Motion."""

    def build_package_json(self, project_name: str, requirements: StructuredRequirements) -> GeneratedFile:
        import json
        import re

        slug = re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-") or "generated-site"
        analysis = requirements.analysis
        libs = set(analysis.libraries)

        dependencies: dict[str, str] = {
            "react": "^19.0.0",
            "react-dom": "^19.0.0",
            "react-router-dom": "^7.0.0",
            "axios": "^1.7.0",
            "lucide-react": "^0.468.0",
        }
        if "framer-motion" in libs or analysis.animations or "animation" in analysis.raw_prompt.lower():
            dependencies["framer-motion"] = "^11.0.0"

        dev_dependencies: dict[str, str] = {
            "@tailwindcss/vite": "^4.0.0",
            "@types/react": "^19.0.0",
            "@types/react-dom": "^19.0.0",
            "@vitejs/plugin-react": "^4.3.4",
            "tailwindcss": "^4.0.0",
            "typescript": "~5.7.2",
            "vite": "^6.0.0",
        }

        content = {
            "name": slug,
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc -b && vite build",
                "preview": "vite preview",
            },
            "dependencies": dependencies,
            "devDependencies": dev_dependencies,
        }
        return GeneratedFile(path="package.json", content=json.dumps(content, indent=2) + "\n")

    def list_installed(self, requirements: StructuredRequirements) -> list[str]:
        analysis = requirements.analysis
        base = ["react", "react-dom", "react-router-dom", "tailwindcss", "axios"]
        if analysis.animations:
            base.append("framer-motion")
        return base

"""AI Generation Engine — full SDD pipeline orchestrator."""

from __future__ import annotations

import hashlib
import json
import re
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.generation.analyzer.prompt_analyzer import PromptAnalyzer
from app.generation.dependency.dependency_manager import DependencyManager
from app.generation.edit.edit_mode import EditModeService
from app.generation.extractor.requirements import RequirementExtractor
from app.generation.generators.api_generator import ApiGenerator
from app.generation.generators.component_generator import ComponentGenerator
from app.generation.generators.css_generator import CssGenerator
from app.generation.generators.router_generator import RouterGenerator
from app.generation.pipeline import GeneratedFile
from app.generation.planner.folder_planner import FolderPlanner
from app.generation.planner.project_planner import ProjectPlanner
from app.generation.preview.preview_engine import PreviewEngine
from app.generation.validation.validator import GenerationValidator
from app.models.artifact import ArtifactFile
from app.models.deployment import Deployment
from app.models.enums import DeploymentStatus, GenerationStatus, ProjectStatus
from app.models.generation import GenerationRun
from app.models.project import Project
from app.models.user import User
from app.providers.storage.local import LocalArtifactStorage


class GenerationEngine:
    """
    SDD §7 Pipeline:
    Prompt → Analyzer → Requirements → Planner → Folder Planner →
    Component/CSS/Route/API Generators → Validation → File Writer → Preview
    """

    def __init__(self) -> None:
        self.analyzer = PromptAnalyzer()
        self.extractor = RequirementExtractor()
        self.planner = ProjectPlanner()
        self.folder_planner = FolderPlanner()
        self.components = ComponentGenerator()
        self.css = CssGenerator()
        self.router = RouterGenerator()
        self.api_gen = ApiGenerator()
        self.deps = DependencyManager()
        self.validator = GenerationValidator()
        self.edit_mode = EditModeService()
        self.preview = PreviewEngine()
        settings = get_settings()
        self.storage = LocalArtifactStorage(settings.artifact_root)

    def run(
        self,
        *,
        db: Session,
        user: User,
        prompt: str,
        project_id: UUID | None = None,
        project_name: str | None = None,
    ) -> dict:
        if not prompt.strip():
            raise HTTPException(status_code=422, detail="Prompt is required")

        has_existing = project_id is not None
        is_edit = self.edit_mode.is_edit_prompt(prompt, has_existing)

        # 1) Prompt Analyzer (SDD §8)
        analysis = self.analyzer.analyze(prompt)
        # Optional TinyGPT enrichment (localhost:8100) — no-op if offline
        try:
            from app.generation.ai.tinygpt_client import fetch_tagline

            tagline = fetch_tagline(prompt)
            if tagline:
                if not isinstance(analysis.seo, dict):
                    analysis.seo = {}
                analysis.seo["tagline"] = tagline
        except Exception:
            pass
        requirements = self.extractor.extract(analysis)
        preferred_name = (project_name or analysis.brand_name or analysis.website_type or "Generated Site").strip()
        project = self._resolve_project(db, user, project_id, preferred_name, analysis.website_type)
        site_title = (analysis.brand_name or project.name or preferred_name).strip()

        if is_edit and project.current_run_id:
            files = self._run_edit_mode(project, prompt)
            mode = "edit"
        else:
            files = self._run_full_pipeline(requirements, site_title)
            mode = "generate"

        plan = self.planner.plan(requirements, site_title)
        validation = self.validator.validate(files, plan)
        if not validation["ok"]:
            raise HTTPException(status_code=500, detail={"message": "Validation failed", **validation})

        run = GenerationRun(
            project_id=project.id,
            user_id=user.id,
            prompt=prompt.strip(),
            status=GenerationStatus.succeeded,
            provider="local_ai",
            model="local-website-ai-v1",
        )
        db.add(run)
        db.flush()

        self._write_files(db, project, run, files, analysis.to_dict())

        # Preview Engine (SDD §16): npm install → build → live serve
        storage_root = self.storage.root
        self.preview.sync_from_storage(storage_root, project.id, run.id)
        preview_result = self.preview.install_and_build(project.id, run.id)

        project.current_run_id = run.id
        db.commit()
        db.refresh(project)
        db.refresh(run)

        return {
            "mode": mode,
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "current_run_id": str(project.current_run_id),
            },
            "run": {
                "id": str(run.id),
                "status": str(run.status.value if hasattr(run.status, "value") else run.status),
                "prompt": run.prompt,
            },
            "analysis": analysis.to_dict(),
            "requirements": {
                "features": requirements.features,
                "content_sections": requirements.content_sections,
                "cta_primary": requirements.cta_primary,
                "tone": requirements.tone,
            },
            "plan": plan.to_dict(),
            "validation": validation,
            "preview": preview_result,
            "files": [{"path": f.path, "size_bytes": len(f.content.encode("utf-8"))} for f in files],
            "bundle_summary": {
                "file_count": len(files),
                "website_type": analysis.website_type,
                "framework": analysis.framework,
                "styling": analysis.styling,
                "color": analysis.color,
                "pages": analysis.pages,
                "components": analysis.components,
            },
        }

    def _run_full_pipeline(self, requirements, project_name: str) -> list[GeneratedFile]:
        plan = self.planner.plan(requirements, project_name)
        folder = self.folder_planner.plan(requirements, plan)

        generated: list[GeneratedFile] = []
        generated.append(self.deps.build_package_json(project_name, requirements))
        generated.extend(self._scaffold_files(project_name, requirements))
        generated.extend(self.components.generate(requirements, plan))
        generated.extend(self.css.generate(requirements))
        generated.extend(self.router.generate(plan))
        generated.extend(self.api_gen.generate(requirements))

        by_path = {f.path: f for f in generated}
        return list(by_path.values())

    def _run_edit_mode(self, project: Project, prompt: str) -> list[GeneratedFile]:
        assert project.current_run_id
        paths = self.storage.list_files(project.id, project.current_run_id)
        existing = [
            GeneratedFile(
                path=p,
                content=self.storage.read_file(project.id, project.current_run_id, p).decode("utf-8"),
            )
            for p in paths
            if not p.startswith(".builder/")
        ]
        return self.edit_mode.apply_edits(prompt, existing)

    def _scaffold_files(self, title: str, requirements) -> list[GeneratedFile]:
        analysis = requirements.analysis
        preview_title = title.replace("<", "")
        meta = _clean(analysis.seo.get("meta_description") or f"A modern {analysis.website_type} website.")
        pages = ", ".join(analysis.pages) or "Home"
        sections = ", ".join(getattr(analysis, "sections", []) or requirements.content_sections) or "Hero, Content, Contact"
        return [
            GeneratedFile(
                path="index.html",
                content=(
                    f'<!doctype html>\n<html lang="en">\n<head>\n'
                    f'  <meta charset="UTF-8" />\n'
                    f'  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
                    f'  <meta name="description" content="{meta[:160]}" />\n'
                    f'  <title>{preview_title}</title>\n'
                    f'</head>\n<body>\n  <div id="root"></div>\n'
                    f'  <script type="module" src="/src/main.tsx"></script>\n</body>\n</html>\n'
                ),
            ),
            GeneratedFile(
                path="tsconfig.json",
                content=json.dumps(
                    {
                        "compilerOptions": {
                            "target": "ES2022",
                            "lib": ["ES2022", "DOM", "DOM.Iterable"],
                            "module": "ESNext",
                            "skipLibCheck": True,
                            "moduleResolution": "bundler",
                            "jsx": "react-jsx",
                            "strict": True,
                            "noEmit": True,
                        },
                        "include": ["src"],
                    },
                    indent=2,
                )
                + "\n",
            ),
            GeneratedFile(
                path="README.md",
                content=(
                    f"# {title}\n\n"
                    f"Generated by AI Website Generator.\n\n"
                    f"- **Type:** {analysis.website_type}\n"
                    f"- **Layout:** {getattr(analysis, 'layout', 'multi_page')}\n"
                    f"- **Pages:** {pages}\n"
                    f"- **Sections:** {sections}\n"
                    f"- **Stack:** React + Vite + Tailwind + TypeScript\n"
                    f"- **Theme:** {analysis.theme.get('style', 'modern')} / {analysis.color}\n\n"
                    f"Open the **Preview** tab in the workspace for the live site.\n"
                ),
            ),
            GeneratedFile(
                path="preview.html",
                content=(
                    "<!doctype html><html><head><meta charset='utf-8'>"
                    f"<title>{preview_title}</title>"
                    "<style>body{margin:0;font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;display:grid;place-items:center;min-height:100vh}"
                    ".card{max-width:28rem;padding:2rem;border:1px solid #334155;border-radius:1rem;background:#1e293b}"
                    "h1{margin:0 0 .5rem;font-size:1.5rem}p{margin:0;color:#94a3b8;line-height:1.5}</style></head>"
                    f"<body><div class='card'><h1>{preview_title}</h1>"
                    f"<p>{analysis.website_type} · {pages}</p>"
                    "<p style='margin-top:1rem'>If you see this fallback, open live preview after generation completes.</p>"
                    "</div></body></html>\n"
                ),
            ),
        ]

    def _write_files(
        self, db: Session, project: Project, run: GenerationRun, files: list[GeneratedFile], analysis: dict
    ) -> None:
        self.storage.delete_tree(project.id, run.id)
        for spec in files:
            data = spec.content.encode("utf-8")
            self.storage.write_file(project.id, run.id, spec.path, data)
            db.add(
                ArtifactFile(
                    run_id=run.id,
                    path=spec.path,
                    content_hash=hashlib.sha256(data).hexdigest(),
                    size_bytes=len(data),
                )
            )
        self.storage.write_file(
            project.id, run.id, ".builder/analysis.json", json.dumps(analysis, indent=2).encode("utf-8")
        )

    def _resolve_project(
        self, db: Session, user: User, project_id: UUID | None, project_name: str | None, website_type: str
    ) -> Project:
        if project_id is not None:
            project = db.get(Project, project_id)
            if project is None or project.user_id != user.id:
                raise HTTPException(status_code=404, detail="Project not found")
            # Upgrade placeholder names when regenerating with a real brand
            if project_name and project.name.lower() in {"new", "untitled", "generated site", website_type.lower()}:
                project.name = project_name[:200]
            return project
        name = (project_name or website_type or "Generated Site").strip()[:200]
        project = Project(
            user_id=user.id,
            name=name,
            description=f"Generated from prompt ({website_type})",
            status=ProjectStatus.active,
        )
        db.add(project)
        db.flush()
        db.add(Deployment(project_id=project.id, status=DeploymentStatus.not_configured))
        return project


def _clean(text: str) -> str:
    return text.replace("<", "").replace(">", "").replace('"', "'")

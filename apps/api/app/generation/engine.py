"""AI Generation Engine — full SDD pipeline orchestrator."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.generation.agents.prompt_agent import PromptAgent
from app.generation.context import GenerationContext
from app.generation.dependency.dependency_manager import DependencyManager
from app.generation.edit.edit_mode import EditModeService
from app.generation.generators.api_generator import ApiGenerator
from app.generation.generators.component_generator import ComponentGenerator
from app.generation.generators.css_generator import CssGenerator
from app.generation.generators.router_generator import RouterGenerator
from app.generation.planner.folder_planner import FolderPlanner
from app.generation.planner.project_planner import ProjectPlanner
from app.generation.planner.website_planner import WebsitePlanner
from app.generation.preview.preview_engine import PreviewEngine
from app.generation.validation.validator import GenerationValidator
from app.generation.pipeline import GeneratedFile, WebsitePlan
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
    Prompt → PromptAgent → Planner → Folder Planner →
    Component/CSS/Route/API Generators → Validation → File Writer → Preview
    """

    def __init__(self) -> None:
        self.prompt_agent = PromptAgent()
        self.planner = ProjectPlanner()
        self.website_planner = WebsitePlanner()
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

    def run(self, ctx: GenerationContext) -> dict:
        db = ctx.db
        user = ctx.user
        prompt = ctx.prompt
        project_id = ctx.project_id
        project_name = ctx.project_name
        existing_run_id = ctx.existing_run_id

        if not prompt.strip():
            raise HTTPException(status_code=422, detail="Prompt is required")

        has_existing = project_id is not None
        is_edit = self.edit_mode.is_edit_prompt(prompt, has_existing)

        # Prompt understanding (Phase 4) — analyze + extract into context
        self.prompt_agent.execute(ctx)
        analysis = ctx.analysis
        requirements = ctx.requirements
        if analysis is None or requirements is None:
            raise HTTPException(status_code=500, detail="PromptAgent failed to populate context")

        preferred_name = (project_name or analysis.brand_name or analysis.website_type or "Generated Site").strip()
        project = self._resolve_project(db, user, project_id, preferred_name, analysis.website_type)
        site_title = (analysis.brand_name or project.name or preferred_name).strip()

        # Phase 1: WebsitePlan artifact (does not change template selection)
        settings = get_settings()
        website_plan: WebsitePlan | None = None
        if settings.gen_v2_planner or settings.gen_v2_theme or settings.gen_v2_components or settings.gen_v2_content or settings.gen_v2_images or settings.gen_v2_validator:
            website_plan = self.website_planner.plan_from_analysis(
                analysis,
                requirements=requirements,
                project_name=site_title,
            )
            if settings.gen_v2_ai_planner and website_plan is not None:
                try:
                    from app.generation.ai.ai_planner import AIPlanner

                    website_plan = AIPlanner().maybe_enrich(analysis, website_plan)
                except Exception:
                    pass
            # Prefer cleaned planned brand (never use raw prompt as project/logo title)
            if website_plan and website_plan.brand_name:
                planned = website_plan.brand_name.strip()
                messy = (
                    len(site_title) > 40
                    or site_title.lower() in {
                        "new",
                        "untitled",
                        "generated site",
                        analysis.website_type.lower(),
                    }
                    or any(
                        w in site_title.lower()
                        for w in ("create that", "responsive", "give me", "sign in", "so create")
                    )
                )
                if planned and (messy or planned.lower() != site_title.lower()):
                    site_title = planned
                    if messy or project.name.lower() in {
                        "new",
                        "untitled",
                        "generated site",
                        analysis.website_type.lower(),
                    } or len(project.name) > 40:
                        project.name = planned[:200]
                    analysis.brand_name = planned

        semantic_report = None
        if is_edit and project.current_run_id:
            files = self._run_edit_mode(project, prompt)
            mode = "edit"
        else:
            files, semantic_report = self._run_full_pipeline(
                requirements, site_title, website_plan=website_plan
            )
            mode = "generate"

        plan = self.planner.plan(requirements, site_title)
        validation = self.validator.validate(files, plan)
        if not validation["ok"]:
            raise HTTPException(status_code=500, detail={"message": "Validation failed", **validation})

        # Enrich WebsitePlan with resolved design tokens (Phase 2) for the artifact
        website_plan_dict = None
        if website_plan is not None:
            website_plan_dict = website_plan.to_dict()
            if settings.gen_v2_theme:
                try:
                    from app.generation.engines.theme_engine import ThemeEngine

                    tokens = ThemeEngine().resolve_from_plan(website_plan)
                    website_plan_dict["design_tokens"] = tokens
                except Exception:
                    pass
            if semantic_report is not None:
                website_plan_dict["semantic_validation"] = semantic_report
            # Persist when any v2 flag is on
            if not (
                settings.gen_v2_planner
                or settings.gen_v2_theme
                or settings.gen_v2_components
                or settings.gen_v2_content
                or settings.gen_v2_images
                or settings.gen_v2_validator
            ):
                website_plan_dict = None

        if existing_run_id is not None:
            run = db.get(GenerationRun, existing_run_id)
            if (
                run is None
                or run.user_id != user.id
                or run.project_id != project.id
            ):
                raise HTTPException(status_code=404, detail="Generation run not found")
            run.prompt = prompt.strip()
            run.status = GenerationStatus.succeeded
            run.provider = "local_ai"
            run.model = "local-website-ai-v1"
            run.error_message = None
            run.finished_at = datetime.now(timezone.utc)
        else:
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

        self._write_files(
            db,
            project,
            run,
            files,
            analysis.to_dict(),
            website_plan=website_plan_dict,
        )

        # Preview Engine (SDD §16): npm install → build → live serve
        storage_root = self.storage.root
        self.preview.sync_from_storage(storage_root, project.id, run.id)
        preview_result = self.preview.install_and_build(project.id, run.id)

        project.current_run_id = run.id
        db.commit()
        db.refresh(project)
        db.refresh(run)

        result = {
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
        if website_plan_dict is not None:
            result["website_plan"] = website_plan_dict
        if semantic_report is not None:
            result["semantic_validation"] = semantic_report
        return result

    def _run_full_pipeline(
        self,
        requirements,
        project_name: str,
        *,
        website_plan: WebsitePlan | None = None,
    ) -> tuple[list[GeneratedFile], dict | None]:
        settings = get_settings()
        plan = self.planner.plan(requirements, project_name)
        folder = self.folder_planner.plan(requirements, plan)

        content_bag = None
        image_manifest = None
        if website_plan is not None and settings.gen_v2_content:
            from app.generation.engines.content_engine import ContentEngine

            content_bag = ContentEngine().build(website_plan)
        if website_plan is not None and settings.gen_v2_images:
            from app.generation.engines.image_engine import ImageEngine

            image_manifest = ImageEngine().build(website_plan)

        generated: list[GeneratedFile] = []
        generated.append(self.deps.build_package_json(project_name, requirements))
        generated.extend(self._scaffold_files(project_name, requirements))
        generated.extend(self.components.generate(requirements, plan, website_plan=website_plan))

        if content_bag is not None:
            from app.generation.engines.content_engine import ContentEngine

            generated.append(ContentEngine().emit_data_module(content_bag))
        if image_manifest is not None:
            from app.generation.engines.image_engine import ImageEngine

            generated.append(ImageEngine().emit_data_module(image_manifest))

        if website_plan is not None and settings.gen_v2_components:
            # Specialty generators own their Navbar/Hero/Footer — don't overwrite
            niche = website_plan.niche
            if niche not in {"clothing", "footwear", "electronics", "blog", "portfolio", "saas", "bookstore"}:
                from app.generation.engines.component_engine import ComponentEngine

                shells = ComponentEngine().emit_shells(
                    website_plan, content=content_bag, images=image_manifest
                )
                generated.extend(shells)

        generated.extend(self.css.generate(requirements, website_plan=website_plan))
        generated.extend(self.router.generate(plan))
        generated.extend(self.api_gen.generate(requirements))

        by_path = {f.path: f for f in generated}
        files = list(by_path.values())

        semantic_report = None
        if website_plan is not None and settings.gen_v2_validator:
            from app.generation.validation.semantic_validator import SemanticValidator

            semantic_report = SemanticValidator().validate(
                website_plan=website_plan,
                files=files,
                content=content_bag,
                images=image_manifest,
            )
            if not semantic_report["ok"]:
                # One regenerate attempt with niche lock (re-run specialty by niche only)
                regenerated = self.components.generate(requirements, plan, website_plan=website_plan)
                if settings.gen_v2_components and website_plan.niche not in {
                    "clothing",
                    "footwear",
                    "electronics",
                    "blog",
                    "portfolio",
                    "saas",
                    "bookstore",
                }:
                    from app.generation.engines.component_engine import ComponentEngine

                    regenerated = list(regenerated) + list(
                        ComponentEngine().emit_shells(
                            website_plan, content=content_bag, images=image_manifest
                        )
                    )
                by_path.update({f.path: f for f in regenerated})
                if content_bag is not None:
                    from app.generation.engines.content_engine import ContentEngine

                    mod = ContentEngine().emit_data_module(content_bag)
                    by_path[mod.path] = mod
                if image_manifest is not None:
                    from app.generation.engines.image_engine import ImageEngine

                    mod = ImageEngine().emit_data_module(image_manifest)
                    by_path[mod.path] = mod
                files = list(by_path.values())
                semantic_report = SemanticValidator().validate(
                    website_plan=website_plan,
                    files=files,
                    content=content_bag,
                    images=image_manifest,
                )
                if not semantic_report["ok"]:
                    raise HTTPException(
                        status_code=500,
                        detail={
                            "message": "Semantic validation failed",
                            **semantic_report,
                        },
                    )

        return files, semantic_report

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
                    "<meta name='viewport' content='width=device-width, initial-scale=1'>"
                    "<style>"
                    "@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=Syne:wght@700&display=swap');"
                    "*{box-sizing:border-box}body{margin:0;font-family:'DM Sans',system-ui,sans-serif;"
                    "background:radial-gradient(circle at 10% 0%,#d4f5ef,transparent 40%),"
                    "radial-gradient(circle at 90% 10%,#ffe8d6,transparent 35%),#eef1f4;color:#0d1218;min-height:100vh}"
                    "header{display:flex;justify-content:space-between;align-items:center;padding:1.25rem 1.5rem;"
                    "border-bottom:1px solid #cfd8e3;background:rgba(255,255,255,.85);backdrop-filter:blur(8px)}"
                    "header strong{font-family:Syne,sans-serif;font-size:1.1rem}"
                    "nav{display:flex;gap:1rem;font-size:.85rem;color:#5c6b7a}"
                    "main{max-width:56rem;margin:0 auto;padding:3rem 1.5rem 4rem}"
                    "h1{font-family:Syne,sans-serif;font-size:clamp(2rem,5vw,3.25rem);line-height:1.1;margin:0}"
                    ".lead{margin:1rem 0 0;color:#5c6b7a;font-size:1.05rem;max-width:36rem;line-height:1.55}"
                    ".pills{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.5rem}"
                    ".pills span{background:#fff;border:1px solid #cfd8e3;border-radius:999px;padding:.35rem .75rem;font-size:.75rem}"
                    ".cta{display:inline-flex;margin-top:1.75rem;background:linear-gradient(135deg,#0f9f8a,#e85d04);"
                    "color:#fff;text-decoration:none;padding:.85rem 1.25rem;border-radius:999px;font-weight:600;font-size:.9rem}"
                    ".note{margin-top:2.5rem;padding:1rem 1.15rem;border-radius:1rem;background:#fff;border:1px solid #cfd8e3;"
                    "color:#5c6b7a;font-size:.85rem;line-height:1.5}"
                    "</style></head><body>"
                    f"<header><strong>{preview_title}</strong><nav><span>{analysis.website_type}</span></nav></header>"
                    f"<main><p style='font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:#0f9f8a;font-weight:700'>Preview</p>"
                    f"<h1>{preview_title}</h1>"
                    f"<p class='lead'>{meta[:180]}</p>"
                    f"<div class='pills'><span>{analysis.website_type}</span><span>Pages: {pages}</span>"
                    f"<span>Sections: {sections}</span></div>"
                    "<a class='cta' href='#'>Live React preview builds after generate</a>"
                    "<p class='note'>This is a static snapshot. After generation finishes, the Preview tab loads the full Vite site "
                    "(navbar, pages, and interactions). If you still see only this card, hit Generate again.</p>"
                    "</main></body></html>\n"
                ),
            ),
        ]

    def _write_files(
        self,
        db: Session,
        project: Project,
        run: GenerationRun,
        files: list[GeneratedFile],
        analysis: dict,
        website_plan: dict | None = None,
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
        if website_plan is not None:
            self.storage.write_file(
                project.id,
                run.id,
                ".builder/website_plan.json",
                json.dumps(website_plan, indent=2).encode("utf-8"),
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

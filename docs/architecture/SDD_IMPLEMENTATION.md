# SDD v1.0 Implementation Map

Source: [SDD-v1.0.pdf](./SDD-v1.0.pdf)

## Implemented (Phase 1–3)

| SDD Section | Feature | Implementation |
|-------------|---------|----------------|
| §4 Stack | React, Vite, Tailwind, FastAPI | `apps/web`, `apps/api` |
| §5 Architecture | User → Frontend → Backend → AI → Generator | `GenerationEngine` |
| §6 User Flow | Prompt → analyze → plan → generate → preview | `POST /api/v1/generate` |
| §7 Pipeline | Full 11-stage pipeline | `apps/api/app/generation/` |
| §8 Prompt Analyzer | Type, theme, color, framework, pages, components | `analyzer/prompt_analyzer.py` (466 types) |
| §9 Project Planner | src/components, pages, hooks, assets, services | `planner/project_planner.py` |
| §10 Component Generator | Navbar, Hero, Footer, Button, Card | `generators/component_generator.py` |
| §11 CSS Generator | Tailwind + theme tokens | `generators/css_generator.py` |
| §12 Route Generator | React Router multi-page | `generators/router_generator.py` |
| §13 Validation | JSX, imports, routes, required files | `validation/validator.py` |
| §14 File Generator | Python writes all files | `engine.py` + `ArtifactStorage` |
| §15 Dependency Manager | React, Router, Tailwind, Axios, Framer Motion | `dependency/dependency_manager.py` |
| §16 Preview Engine | npm install → npm run build → serve | `preview/preview_engine.py` |
| §17 Edit Mode | Targeted file updates | `edit/edit_mode.py` |
| §19 Folder Structure | generated_projects, templates, docs | `generated_projects/`, `docs/` |

## API Endpoints

- `POST /api/v1/generate` — full pipeline + live preview build
- `POST /api/v1/analyze` — analyzer JSON only
- `GET /api/v1/preview-live/{project_id}/` — built Vite app
- `GET /api/v1/preview/{project_id}/` — static fallback

## Future (SDD §18)

- Next.js, deploy to Vercel/Netlify, AI images, full backend generation

## Run

```bash
npm run dev:api   # Terminal 1
npm run dev       # Terminal 2
```

Requires **Node.js + npm** on the server for live preview builds.

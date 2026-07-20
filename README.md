# AI Website Builder

Lovable / Bolt / v0–style app: describe a website in natural language → get a full React + Vite + Tailwind project, live preview, edit, download.

## Local AI (no API key required)

This project includes a **built-in local AI** — you do **not** need OpenAI or any API key.

| Component | What it does |
|-----------|----------------|
| **Trained classifier** | scikit-learn model on 466 website types (5,556 training samples) |
| **Prompt analyzer** | ML + rules → type, pages, theme, components |
| **Generation engine** | Builds full React project (Navbar, Hero, Footer, pages, routes) |
| **Preview engine** | `npm install` + `npm run build` → live preview |

Check status: `GET http://localhost:8000/api/v1/ai/status`

Retrain: `cd apps/api && PYTHONPATH=. python scripts/train_local_ai.py`

## Quick start

| Layer | Choice |
|-------|--------|
| Frontend | React, Vite, Tailwind, React Router, TypeScript, Monaco |
| Backend | FastAPI, SQLAlchemy, Alembic, JWT |
| DB | PostgreSQL |
| Jobs | DB-backed worker (`FOR UPDATE SKIP LOCKED`) |
| AI | OpenAI-compatible provider + **mock mode** for local demo |
| Artifacts | Local filesystem (`ARTIFACT_ROOT`) |

Full notes: [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md)

## Quick start (local)

Uses **SQLite + rule-based generation engine** by default (no Docker/API key required).

### Terminals

```bash
# 1) API
npm run dev:api

# 2) Web (from repo root — this is the correct command)
npm run dev
```

Open http://localhost:5173 → Register → **New project** → Analyze → Generate.

> Do not run `npm run dev` expecting API — root `dev` starts the Vite web app only. Use `npm run dev:api` for the backend.

### Postgres (optional)

```bash
docker compose up -d db
# set DATABASE_URL=postgresql+psycopg://builder:builder@localhost:5432/ai_builder
cd apps/api && alembic upgrade head
```

### Real AI (optional)

In `apps/api/.env`:

```env
AI_MOCK=false
AI_API_KEY=sk-...
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
```

## API

- `POST /api/v1/auth/register` · `POST /api/v1/auth/login` · `GET /api/v1/auth/me`
- `CRUD /api/v1/projects`
- `POST/GET /api/v1/projects/{id}/generations`
- `GET /api/v1/generations/{id}`
- `GET/PUT /api/v1/projects/{id}/file`
- `GET /api/v1/projects/{id}/download`
- `GET /api/v1/preview/{id}/preview.html`
- `POST /api/v1/generate` — full AI generation pipeline
- `POST /api/v1/analyze` — Prompt Analyzer JSON only
- `GET /api/v1/analyze/catalog` — website type catalog stats
- `GET /health`

## Docker (API + worker + DB)

```bash
docker compose up --build
```

Then run the web app locally with `npm run dev` (proxies `/api` to `:8000`).

# AI Website Builder — Architecture

## Stack

- **Frontend:** React, Vite, Tailwind CSS, React Router, TypeScript
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **DB:** PostgreSQL (Redis optional later)
- **Auth:** JWT (Google OAuth later)
- **AI:** OpenAI-compatible provider abstraction

## Decisions (locked)

1. Monorepo: `apps/web`, `apps/api`
2. Async `GenerationRun` jobs via DB-backed worker (`SKIP LOCKED`)
3. Artifacts on local filesystem behind `ArtifactStorage` port
4. Preview served from API from `current_run`
5. Manual edits write into current run
6. Deploy is stub only
7. Regenerate = new `GenerationRun`

## Frontend routes

| Path | Screen |
|------|--------|
| `/login`, `/register` | Auth |
| `/` | Dashboard (projects) |
| `/projects/new` | Create + first prompt |
| `/projects/:id` | Workspace: prompt, preview, editor, history |

## API surface (`/api/v1`)

- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- `GET/POST /projects`, `GET/PATCH/DELETE /projects/{id}`
- `POST /projects/{id}/generations`, `GET /projects/{id}/generations`, `GET /generations/{id}`
- `GET/PUT /projects/{id}/files`, `GET /projects/{id}/download`
- `GET /preview/{project_id}/{path}`

## AI pipeline

1. Enqueue run → 2. Worker claims → 3. Provider returns `FileSpec[]` → 4. Validate paths → 5. Write storage → 6. Index files → 7. Set `current_run_id`

## Folder structure

See repository root (`apps/api`, `apps/web`, `docs/architecture`).

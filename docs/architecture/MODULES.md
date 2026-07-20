# Architecture — remaining modules

## Module 4 — Frontend

**Routes:** `/login`, `/register`, `/`, `/projects/new`, `/projects/:id`  
**State:** JWT in `localStorage`; AuthContext; workspace polls active runs every 1.5s  
**Workspace tabs:** Preview (`srcDoc` from authenticated fetch), Code (Monaco), History  
**Stack constraints:** React + Vite + Tailwind + React Router + TypeScript  

## Module 5 — API contracts

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/v1/auth/register` | → `{access_token}` |
| POST | `/api/v1/auth/login` | → `{access_token}` |
| GET | `/api/v1/auth/me` | Bearer required |
| GET/POST | `/api/v1/projects` | List / create (+ optional `prompt`) |
| GET/PATCH/DELETE | `/api/v1/projects/{id}` | DELETE archives |
| POST/GET | `/api/v1/projects/{id}/generations` | Enqueue / history |
| GET | `/api/v1/generations/{id}` | Poll status |
| GET | `/api/v1/projects/{id}/files` | File index |
| GET/PUT | `/api/v1/projects/{id}/file` | `?path=` / body `{path,content}` |
| GET | `/api/v1/projects/{id}/download` | ZIP |
| GET | `/api/v1/preview/{id}/{path}` | Static preview (`preview.html`) |

## Module 6 — AI pipeline

1. API creates `GenerationRun(status=queued)`  
2. Worker claims run  
3. `AIProvider.generate_site(prompt, prior_files)`  
4. Validate paths → write `ArtifactStorage` → index `ArtifactFile`  
5. `status=succeeded`, set `project.current_run_id`  
6. Mock provider ships full Vite React tree + `preview.html` for iframe  

## Module 7 — Folder structure

```
apps/api/app/{api,core,db,models,schemas,services,providers,workers,domain}
apps/web/src/{auth,lib,pages}
docs/architecture/
docker-compose.yml
```

## Module 8 — Design decisions

- SQLite default for local; Postgres via Compose/Alembic for production  
- Mock AI default; swap with `AI_MOCK=false` + key  
- Edits write into current run  
- Deploy stub only (“Deploy: later” in UI)  
- Google OAuth fields reserved on `User`  

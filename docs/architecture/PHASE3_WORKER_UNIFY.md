# Phase 3 — Worker ↔ Orchestrator Unification

**Status:** Complete  
**Behavior:** Worker jobs use the same runtime as `POST /generate`.

## Design choice: GenerationContext

`existing_run_id` is carried on `GenerationContext` (`app/generation/context.py`) rather than adding a long-lived kwarg sprawl on `GenerationEngine.run`.

- Orchestrator public kwargs unchanged for API callers (`existing_run_id` optional).
- Engine accepts a single `GenerationContext` and unpacks at the top (no business-logic move).

## Execution flow

```
API
POST /api/v1/generate
  → Orchestrator.run(...)
    → GenerationContext(existing_run_id=None)
      → GenerationEngine.run(ctx)   # creates GenerationRun

Worker
POST /api/v1/projects/{id}/generations  → queue GenerationRun
  → claim_next_run (status=running)
  → Orchestrator.run(..., existing_run_id=run.id)
    → GenerationContext(existing_run_id=run.id)
      → GenerationEngine.run(ctx)   # reuses same GenerationRun
```

One runtime pipeline. No duplicate runs for queued jobs.

## Providers

`MockAIProvider` / `OpenAICompatibleProvider` are no longer invoked by the worker.
Modules remain on disk for a later cleanup phase (not deleted in Phase 3).

## Rollback

Revert `orchestrator.py`, `context.py`, `engine.py` run entry, `generation_worker.py`, and `generation_service.py` enqueue metadata.

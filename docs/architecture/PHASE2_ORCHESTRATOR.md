# Phase 2 — Orchestrator Facade

**Date (UTC):** 2026-07-24  
**Status:** Complete  
**Behavior change:** None (delegate-only)

## What changed

| Action | Path |
|--------|------|
| Created | `apps/api/app/generation/orchestrator.py` (`Orchestrator`) |
| Wired | `apps/api/app/api/v1/generate.py` → `Orchestrator().run(...)` |
| Unchanged | `GenerationEngine`, all generators, planners, PreviewEngine, HTTP request/response shapes |

## New execution flow

```
Client
  → POST /api/v1/generate  (unchanged public API)
    → Orchestrator.run()           # Phase 2 facade (public entry)
      → GenerationEngine.run()     # existing pipeline (unchanged)
        → PromptAnalyzer → RequirementExtractor → WebsitePlanner → …
        → ComponentGenerator / CSS / Router / …
        → Validators → LocalArtifactStorage → PreviewEngine
```

Analyze endpoints are unchanged and do **not** go through Orchestrator:

```
POST /api/v1/analyze          → analyze_prompt (PromptAnalyzer)
GET  /api/v1/analyze/catalog  → catalog_stats
```

Async worker path (`GenerationService` → Mock/OpenAI provider) is **not** unified in Phase 2.

## Intent

Establish a single sync generation entry for future agent routing **without** moving responsibilities yet.

## Rollback

1. Point `generate.py` back at `GenerationEngine().run(...)`.
2. Delete `orchestrator.py`.

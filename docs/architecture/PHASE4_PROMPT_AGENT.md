# Phase 4 — PromptAgent Extraction

**Status:** Complete  
**Behavior change:** None (same analyze → enrich → extract sequence)

## Code ownership

| Unit | Before | After |
|------|--------|--------|
| `PromptAnalyzer` | Called directly by `GenerationEngine` | Called by **`PromptAgent`** (module path unchanged: `analyzer/prompt_analyzer.py`) |
| `RequirementExtractor` | Called directly by `GenerationEngine` | Called by **`PromptAgent`** (`extractor/requirements.py`) |
| TinyGPT tagline enrich | Inline in `GenerationEngine.run` | Inside **`PromptAgent.execute`** |
| New | — | `agents/prompt_agent.py`, `agents/__init__.py` |
| `GenerationContext` | Identity fields only | + `analysis`, `requirements` |

**Physical file moves:** none. Analyzer/extractor stay put so tests and `/analyze` keep stable imports. Runtime ownership moved to PromptAgent.

## New execution flow

```
Orchestrator.run(...)
  → GenerationContext
    → GenerationEngine.run(ctx)
         → PromptAgent.execute(ctx)     # analyze + tagline + extract → ctx
         → WebsitePlanner / ProjectPlanner / …
         → ComponentGenerator / …
         → Validation → Persistence → Preview
```

## Responsibilities removed from GenerationEngine

- Instantiating / calling `PromptAnalyzer`
- Instantiating / calling `RequirementExtractor`
- TinyGPT tagline enrichment on `analysis.seo`

Engine now only: `self.prompt_agent.execute(ctx)` then reads `ctx.analysis` / `ctx.requirements`.

## Unchanged

WebsitePlanner, ComponentGenerator, PreviewEngine, validation, persistence, worker, API contracts, DB models.

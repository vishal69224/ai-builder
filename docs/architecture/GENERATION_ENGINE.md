# AI Generation Engine — Backend Architecture

## Endpoint

`POST /api/v1/generate`

```json
{
  "prompt": "Build a modern coffee shop website.",
  "project_id": null,
  "project_name": "optional"
}
```

Auth: Bearer JWT.

## Pipeline

```text
User Prompt
    ↓
Prompt Analyzer          → AnalysisJSON (type, pages, components, theme, …)
    ↓
Requirement Extractor    → StructuredRequirements
    ↓
Project Planner          → FilePlan + route map
    ↓
React Generator          → App/pages/components TSX
    ↓
Tailwind Generator       → tokens + index.css + utility plan
    ↓
Router Generator         → React Router wiring
    ↓
Validation               → paths, required files, schema checks
    ↓
Save Files               → ArtifactStorage + ArtifactFile index
    ↓
Return Project           → project + run + analysis + files summary
```

## Modules (`apps/api/app/generation/`)

| Module | Responsibility |
|--------|----------------|
| `analyzer/` | Prompt → JSON analysis (hundreds of website types) |
| `extractor/` | Analysis → detailed requirements |
| `planner/` | Requirements → project/file plan |
| `generators/` | React / Tailwind / Router code emitters |
| `validation/` | Validate artifacts before save |
| `engine.py` | Orchestrates stages end-to-end |
| `pipeline.py` | Stage interfaces + result types |

## Stage contracts

Each stage is a pure-ish function / class with a clear input/output DTO so providers (rule-based vs LLM) can be swapped later.

## Status

- **Prompt Analyzer:** implemented (rule + catalog based)
- **Downstream stages:** scaffolded; wired through engine with progressive enrichment
- **Frontend for generate UI:** not in this phase

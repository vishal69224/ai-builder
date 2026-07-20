# Evaluation Spec — TinyGPT

## Per-stage gates

| Stage | Format valid | JSX parse | Structure |
|-------|--------------|-----------|-----------|
| C1 | ≥ 90% | ≥ 80% | 1 file, has `export` |
| C2 | ≥ 85% | ≥ 70% | Page path present |
| C3 | ≥ 80% | ≥ 50% | App + package.json; build ≥ 20–40% |

## Golden prompts

Store later at `ml/eval/prompts_golden.jsonl` (Phase 7).

## Regression

Do not promote checkpoint if format-valid drops >10 pts vs previous best.

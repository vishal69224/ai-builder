# Evaluation harness

```bash
cd ml && source .venv/bin/activate
PYTHONPATH=. python -m eval.run_eval c1
PYTHONPATH=. python -m eval.run_eval c2
PYTHONPATH=. python -m eval.run_eval c3
```

Gates come from `docs/ml/EVAL_SPEC.md`. Reports write to `ml/eval/report_<stage>.json`.

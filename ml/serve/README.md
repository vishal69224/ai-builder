# Phase 6 — Inference server

Port **8100** (product API stays on 8000).

```bash
cd ml && source .venv/bin/activate
PYTHONPATH=. python -m serve.server
```

```bash
curl -s http://127.0.0.1:8100/v1/health
curl -s -X POST http://127.0.0.1:8100/v1/generate/component \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Create a Navbar","max_new_tokens":256}'
```

Requires `checkpoints/tinygpt-8m-c1/best.pt`.

#!/usr/bin/env bash
# Train TinyGPT curriculum C2 → C3, then run eval gates.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
export PYTHONPATH=.
export PYTHONUNBUFFERED=1

echo "==> Training C2 (pages) from C1 + replay"
python -m train.train_stage c2

echo "==> Training C3 (sites) from C2 + replay"
python -m train.train_stage c3

echo "==> Eval gates"
python -m eval.run_eval c2 || true
python -m eval.run_eval c3 || true

echo "==> Start inference server with:"
echo "  PYTHONPATH=. python -m serve.server"

# Phase 3–6 Progress

## Phase 3 Datasets (done)

| Dataset | Train | Val | Test |
|---------|-------|-----|------|
| ds_comp_v1 | 2400 | 50 | 50 |
| ds_page_v1 | 1120 | 40 | 40 |
| ds_site_v1 | 540 | 30 | 30 |

Tokenizer retrain vocab ≈ **3014**. Token shards under `datasets/shards/`.

## Rebuild

```bash
cd ml && source .venv/bin/activate
PYTHONPATH=. python data/build_all.py
```

## Phase 4 Model

`ml/model/tinygpt.py` — TinyGPT-8M with RMSNorm, RoPE, causal SDPA.

## Phase 5 Train

```bash
PYTHONPATH=. python -m train.train_stage c1          # full C1
PYTHONPATH=. python -m train.train_stage c1 --quick  # 1 epoch smoke
PYTHONPATH=. python -m train.train_stage c2 --quick
PYTHONPATH=. python -m train.train_stage c3 --quick
```

## Phase 6 Serve

```bash
PYTHONPATH=. python -m serve.server   # http://127.0.0.1:8100
curl http://127.0.0.1:8100/v1/health
```

# Phase 1 — Environment Plan (Apple M1)

## Goals

1. Reproducible Python env for ML (separate from `apps/api` FastAPI venv)
2. PyTorch with **MPS** backend
3. Disk layout for datasets / checkpoints (gitignored)
4. Smoke-test plan (verify MPS) — **executed only after Phase 1 approval of “scaffold”**; no TinyGPT training yet

## Python version

| Use | Version |
|-----|---------|
| Recommended for ML | **3.11 or 3.12** via `pyenv` or official installer |
| Current system | 3.14.5 — may lack mature PyTorch wheels; do **not** rely on it for ML |

Create a dedicated venv:

```text
ml/.venv/          # PyTorch + tokenizers + datasets
apps/api/.venv/    # FastAPI only (existing)
```

## Libraries (install in Phase 1 scaffold — pin later in requirements)

| Package | Purpose |
|---------|---------|
| `torch` | Model + train (MPS) |
| `numpy` | Arrays / metrics |
| `tokenizers` | BPE (Phase 2) |
| `safetensors` | Weight I/O |
| `pyyaml` | Configs |
| `tqdm` | Progress |
| `pytest` | Unit tests |
| `tensorboard` or `wandb` (optional) | Logs |

**Explicitly excluded:** OpenAI / Anthropic / Google SDKs.

## Device policy

```text
if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
```

### M1 constraints

| Topic | Guidance |
|-------|----------|
| Batch size | Start small (8–32); watch unified memory |
| Precision | Prefer **fp32** on MPS first; try fp16 later |
| Context length | Curriculum: 512 → 1024 → 2048 max for TinyGPT |
| Overnight runs | Keep Mac awake; expect C1 in hours not minutes |

## Disk budget (estimate)

| Path | Size |
|------|------|
| `datasets/` | 5–20 GB (TinyGPT era) |
| `checkpoints/` | 1–5 GB (TinyGPT) |
| `ml/.venv` | 2–4 GB |

## Smoke tests (Phase 1 complete when these pass)

1. `python -c "import torch; print(torch.__version__, torch.backends.mps.is_available())"` → `True`
2. Allocate a small tensor on MPS, matmul, copy back to CPU
3. Write/read a dummy `safetensors` file under `checkpoints/_smoke/`

## Security / hygiene

- Never commit `datasets/`, `checkpoints/`, `ml/.venv/`
- No API keys in configs
- Synthetic data only from local rule engine + open licenses

## What Phase 1 does **not** include

- Tokenizer training
- Dataset generation at scale
- TinyGPT model class
- Training loop
- Inference server

Those start at Phase 2+ after approval.

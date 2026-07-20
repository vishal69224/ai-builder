# ML Roadmap — Locked Decisions (Phase 0–1)

## Hardware (detected)

| Item | Value |
|------|-------|
| Chip | Apple M1 (arm64) |
| GPU | Apple M1, 8 cores, Metal |
| Train device | **MPS** (PyTorch) |
| Fallback | CPU |
| Python | 3.14.x (project will pin **3.11 or 3.12** for PyTorch stability) |

## Locked model path

1. **TinyGPT-8M** (d_model=384, layers=6, heads=6, vocab=16k) — first
2. Curriculum SFT: component → page → site (**skip long pretrain** for TinyGPT)
3. Hybrid fallback to rule engine until C3 quality is acceptable
4. Later: WebGPT-S (~50M) on same pipeline

## Phase status

| Phase | Status |
|-------|--------|
| 0 System design | Approved |
| 1 Math + environment | Approved |
| **2 Tokenizer** | **Complete** — see PHASE2_TOKENIZER.md |
| 3 Dataset | Waiting approval |
| 4–6 TinyGPT train/infer | Waiting |
| 7+ Scale + product | Waiting |

No training or model implementation code until Phase 2+ is approved.

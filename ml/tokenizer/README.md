# Phase 2 — Tokenizer (Hugging Face tokenizers BPE)

See `docs/ml/PHASE2_TOKENIZER.md` for design.

## Quick use (after train)

```bash
cd ml
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m tokenizer.build_corpus
python -m tokenizer.train_tokenizer
python -m tokenizer.test_roundtrip
```

Artifacts land in `ml/tokenizer/artifacts/`.

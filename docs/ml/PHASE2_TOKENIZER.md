# Phase 2 — Tokenizer Design & Results

## Goal

Train a **byte-level BPE** tokenizer (vocab ≈ 16k) optimized for React / TSX / Tailwind / JSON, with TinyGPT special tokens.

## Special tokens

| Name | Token |
|------|-------|
| bos | `<\|bos\|>` |
| eos | `<\|eos\|>` |
| pad | `<\|pad\|>` |
| user / assistant | `<\|user\|>` `<\|assistant\|>` |
| file structure | `<\|file\|>` `<\|path\|>` `<\|content\|>` |
| curriculum modes | `<\|comp\|>` `<\|page\|>` `<\|site\|>` |

## Training string format

```text
<|bos|><|user|>{prompt}<|assistant|><|comp|>
<|file|><|path|>src/components/X.tsx<|content|>
{body}
<|eos|>
```

## How to train (M1)

```bash
cd ml
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python -m tokenizer.build_corpus
PYTHONPATH=. python -m tokenizer.train_tokenizer
PYTHONPATH=. python -m tokenizer.test_roundtrip
```

## Artifacts

| File | Purpose |
|------|---------|
| `ml/tokenizer/artifacts/tokenizer.json` | Trained tokenizer |
| `ml/tokenizer/artifacts/tokenizer_meta.json` | Vocab size + special IDs |
| `ml/tokenizer/corpus/train_corpus.txt` | Training corpus (gitignored) |
| `ml/tokenizer/artifacts/roundtrip_report.json` | Test report |

## Results (this run)

| Metric | Value |
|--------|-------|
| Vocab size | **2771** (target 16k deferred to Phase 3 larger corpus) |
| Special tokens | IDs 0–10 all registered |
| Round-trip tests | **All passed** |
| Compression | ~3.4 chars/token on TSX |

**Note:** Byte-level BPE only creates merges for unique byte pairs in the corpus. With ~700KB of repetitive React/Tailwind text, vocabulary saturates around 2.5–3k. Phase 3 dataset builders will retrain the tokenizer on a much larger diverse corpus aiming for 16k.

## Exit criteria (Phase 2)

- [x] Special tokens registered with IDs
- [x] Round-trip encode→decode→encode stable on TSX samples
- [x] Structured training strings preserve markers
- [x] Compression ≥ ~2 chars/token on repeated TSX
- [x] TinyGPT config uses **actual** vocab size from `tokenizer_meta.json`

## Next

**Phase 3 — Dataset builders** (prompt → React JSONL at scale + tokenizer retrain toward 16k). Approve to start.

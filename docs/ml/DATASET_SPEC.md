# Dataset Spec — Prompt → React Pairs

## JSONL schemas

See roadmap. Summary:

| Dataset | Stage | Min size |
|---------|-------|----------|
| `ds_comp_v1` | component | 2,000 |
| `ds_page_v1` | page | 1,000 |
| `ds_site_v1` | site | 500 |
| Golden eval | all | 70 prompts |

## Training serialization

```text
<|bos|><|user|>{prompt}<|assistant|><|comp|>
<|file|><|path|>src/components/X.tsx<|content|>
{body}
<|eos|>
```

## Sources

1. Local rule/template generator (`apps/api` generation engine) as teacher
2. Hand-written golden set
3. Open MIT templates only

## Builder modules (code in Phase 3)

`ml/data/builders/{component,page,site}_builder.py`

No builder code until Phase 3 is approved.

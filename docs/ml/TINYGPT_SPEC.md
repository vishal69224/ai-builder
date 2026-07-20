# TinyGPT-8M — Architecture Spec (Design Only)

## Config (locked)

| Hyperparameter | Value |
|----------------|-------|
| Name | `tinygpt-8m` |
| d_model | 384 |
| n_layers | 6 |
| n_heads | 6 |
| head_dim | 64 |
| ffn_dim | 1536 |
| vocab_size | **2771 now** (from Phase 2 tokenizer); target **16384** after Phase 3 retrain |
| max_seq_len | 2048 (train curriculum up to this) |
| dropout | 0.1 |
| norm | Pre-RMSNorm |
| pos | RoPE |
| activation | GELU |
| tied embeddings | Yes |
| approx params | 8–10M |

## Block

```text
x → RMSNorm → Causal MHA (RoPE) → +x
  → RMSNorm → Linear-GELU-Linear → +x
```

## Special tokens

`<|bos|> <|eos|> <|pad|> <|user|> <|assistant|> <|file|> <|path|> <|content|> <|comp|> <|page|> <|site|>`

## Stages

| Stage | Token | Max seq | Target |
|-------|-------|---------|--------|
| C1 | `<|comp|>` | 512 | One component file |
| C2 | `<|page|>` | 1024 | Page ± components |
| C3 | `<|site|>` | 2048 | Multi-file project |

Implementation: **Phase 4** (after tokenizer + dataset approvals).

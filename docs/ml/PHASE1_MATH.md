# Phase 1 — Mathematics Prerequisites Checklist

Complete this checklist before Phase 2 (tokenizer). You do not need proofs — you need working intuition to debug training.

## 1. Linear algebra

- [ ] Vectors and matrices; matrix × vector
- [ ] Dot product as similarity (attention scores)
- [ ] Why we reshape Q, K, V into heads

**Self-test:** Explain in one sentence why `Q @ K.T` produces attention logits.

## 2. Calculus / autodiff

- [ ] Chain rule (loss → layers → embeddings)
- [ ] Gradient = direction of steepest increase
- [ ] Why exploding/vanishing gradients hurt deep nets
- [ ] Role of residual connections and LayerNorm/RMSNorm

**Self-test:** If loss is NaN after 100 steps, name three things to check.

## 3. Probability & loss

- [ ] Softmax turns logits into a probability distribution
- [ ] Cross-entropy = −log P(correct next token)
- [ ] Perplexity = exp(average CE) — lower is better
- [ ] Teacher forcing (train with ground-truth previous tokens)

**Self-test:** If val perplexity is 50 on a 16k vocab, is that “good” for TinyGPT early training? (Roughly: better than random ~16000; early CE ~4–8 is common.)

## 4. Optimization

- [ ] SGD vs AdamW (adaptive LR + weight decay)
- [ ] Learning rate warmup then cosine decay
- [ ] Gradient clipping (prevents huge updates)
- [ ] Batch size vs learning rate (rough coupling)

**Self-test:** Why is SFT LR usually **lower** than pretrain LR?

## 5. Sequence models

- [ ] Autoregressive factorization: P(x₁…xₙ) = ∏ P(xᵢ | x₁…xᵢ₋₁)
- [ ] Causal mask: token i cannot see i+1…n
- [ ] Context length limit = max tokens the model can attend over
- [ ] Special tokens as control structure (`<|file|>`, `<|eos|>`)

**Self-test:** Why does TinyGPT need a causal mask and not bidirectional BERT attention?

## 6. Curriculum learning (project-specific)

- [ ] Short tasks first (component) → longer (page) → longest (site)
- [ ] Replay earlier data to avoid catastrophic forgetting
- [ ] Exit criteria are metrics (parse rate), not “feels good”

## Recommended study (M1-friendly, free)

1. 3Blue1Brown — Neural Networks (essence)
2. Karpathy — makemore / nanoGPT lectures (especially causal LM)
3. Skim: “Attention Is All You Need” (Figure 1 + multi-head attention)

## Phase 1 exit (math)

Mark all self-tests answered (even roughly). Then approve Phase 2.

**No code required for this checklist.**

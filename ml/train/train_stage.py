"""Train TinyGPT on a curriculum stage (default C1)."""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import torch
import yaml
from torch.utils.data import DataLoader

ML = Path(__file__).resolve().parents[1]
REPO = ML.parent
sys.path.insert(0, str(ML))

from model.tinygpt import TinyGPT, TinyGPTConfig
from train.dataset import MixedReplayDataset, ShardDataset, collate_pad, shard_dir_from_manifest
from tokenizer.wrapper import TinyGPTTokenizer


def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_vocab_size() -> int:
    meta = ML / "tokenizer" / "artifacts" / "tokenizer_meta.json"
    return json.loads(meta.read_text())["vocab_size"]


# Curriculum order — each stage, by default, initializes from the previous
# stage's best checkpoint instead of random weights. This is what makes it
# an actual curriculum (component -> page -> site) rather than three
# independently-trained models that happen to share an architecture.
STAGE_ORDER = {"c1": None, "c2": "c1", "c3": "c2"}


def _default_init_checkpoint(stage: str) -> Path | None:
    prev = STAGE_ORDER.get(stage)
    if prev is None:
        return None
    candidate = REPO / "checkpoints" / f"tinygpt-8m-{prev}" / "best.pt"
    return candidate if candidate.exists() else None


def load_pretrained_weights(model: TinyGPT, ckpt_path: Path, device: torch.device) -> None:
    """Initialize `model` from a prior stage's checkpoint. Loads with
    strict=False so it still works if vocab size or a shape changed between
    stages (e.g. tokenizer retrained) — mismatched tensors are skipped
    rather than crashing the run."""
    state = torch.load(ckpt_path, map_location=device)
    sd = state["model"] if isinstance(state, dict) and "model" in state else state
    missing, unexpected = model.load_state_dict(sd, strict=False)
    print(
        f"Initialized from {ckpt_path.relative_to(REPO)} "
        f"(missing={len(missing)}, unexpected={len(unexpected)}, "
        f"prior best_val={state.get('val_loss', 'n/a')})"
    )


def train_stage(config_path: Path, *, init_from: Path | None = None, from_scratch: bool = False) -> Path:
    cfg_yaml = yaml.safe_load(config_path.read_text())
    stage = cfg_yaml["stage"]
    max_seq = int(cfg_yaml["max_seq_len"])
    epochs = int(cfg_yaml.get("epochs", 3))
    batch_size = int(cfg_yaml.get("batch_size", 8))
    lr = float(cfg_yaml.get("lr", 1e-4))
    ckpt_dir = REPO / cfg_yaml["checkpoint_dir"]
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    # map stage to shard folder
    shard_name = {"c1": "ds_comp_v1", "c2": "ds_page_v1", "c3": "ds_site_v1"}[stage]
    shard_dir = REPO / "datasets" / "shards" / shard_name

    vocab_size = load_vocab_size()
    model_cfg = TinyGPTConfig(vocab_size=vocab_size, max_seq_len=max_seq)
    device = get_device()
    model = TinyGPT(model_cfg).to(device)

    if from_scratch:
        print(f"Device={device} params={model.param_count():,} vocab={vocab_size} stage={stage} (from scratch)")
    else:
        ckpt_to_load = init_from or _default_init_checkpoint(stage)
        if ckpt_to_load:
            load_pretrained_weights(model, ckpt_to_load, device)
        print(f"Device={device} params={model.param_count():,} vocab={vocab_size} stage={stage}")

    current_train = ShardDataset(shard_dir, "train", max_seq_len=max_seq)
    train_ds: ShardDataset | MixedReplayDataset = current_train
    val_ds = ShardDataset(shard_dir, "val", max_seq_len=max_seq)

    # Curriculum replay: mix prior-stage shards so C2/C3 don't forget C1 patterns
    replay_ratio = float(cfg_yaml.get("replay_prev_ratio") or 0.0)
    replay_manifests = list(cfg_yaml.get("replay_manifests") or [])
    if replay_ratio > 0 and replay_manifests:
        replay_sets: list[ShardDataset] = []
        for m in replay_manifests:
            rdir = shard_dir_from_manifest(REPO, m)
            if (rdir / "train_tokens.npy").exists():
                replay_sets.append(ShardDataset(rdir, "train", max_seq_len=max_seq))
            else:
                print(f"  warn: replay shard missing at {rdir}")
        if replay_sets:
            train_ds = MixedReplayDataset(current_train, replay_sets, replay_ratio=replay_ratio)
            print(
                f"  replay mixing enabled: ratio={replay_ratio} "
                f"pools={len(replay_sets)} current_n={len(current_train)}"
            )

    pad_id = TinyGPTTokenizer().token_to_id("<|pad|>") or 2

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=lambda b: collate_pad(b, pad_id=pad_id),
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=lambda b: collate_pad(b, pad_id=pad_id),
    )

    opt = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.95), weight_decay=0.1)
    best_val = float("inf")
    history = []
    global_step = 0
    max_steps = cfg_yaml.get("max_steps")

    for epoch in range(1, epochs + 1):
        model.train()
        running = 0.0
        n_batches = 0
        t0 = time.time()
        for batch in train_loader:
            global_step += 1
            x = batch["input_ids"].to(device)
            y = batch["labels"].to(device)
            _, loss = model(x, y)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            running += float(loss.item())
            n_batches += 1
            if global_step % 20 == 0 or global_step == 1:
                print(f"step {global_step} epoch {epoch} loss {loss.item():.4f}", flush=True)
            if max_steps and global_step >= int(max_steps):
                break
        if max_steps and global_step >= int(max_steps):
            # still run validation once
            train_loss = running / max(n_batches, 1)
            val_loss = evaluate(model, val_loader, device)
            row = {
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "val_ppl": math.exp(min(val_loss, 20)),
                "sec": round(time.time() - t0, 1),
                "stopped_early": True,
                "steps": global_step,
            }
            history.append(row)
            print(json.dumps(row), flush=True)
            save_checkpoint(ckpt_dir / "last.pt", model, opt, model_cfg, epoch, val_loss, history)
            save_checkpoint(ckpt_dir / "best.pt", model, opt, model_cfg, epoch, val_loss, history)
            best_val = val_loss
            break

        train_loss = running / max(n_batches, 1)
        val_loss = evaluate(model, val_loader, device)
        elapsed = time.time() - t0
        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_ppl": math.exp(min(val_loss, 20)),
            "sec": round(elapsed, 1),
        }
        history.append(row)
        print(json.dumps(row))

        # save last
        save_checkpoint(ckpt_dir / "last.pt", model, opt, model_cfg, epoch, val_loss, history)
        if val_loss < best_val:
            best_val = val_loss
            save_checkpoint(ckpt_dir / "best.pt", model, opt, model_cfg, epoch, val_loss, history)
            print(f"  new best val_loss={val_loss:.4f}")

    # also write config json
    (ckpt_dir / "config.json").write_text(json.dumps(model_cfg.to_dict(), indent=2), encoding="utf-8")
    (ckpt_dir / "train_meta.json").write_text(
        json.dumps({"stage": stage, "best_val": best_val, "history": history, "params": model.param_count()}, indent=2),
        encoding="utf-8",
    )
    return ckpt_dir / "best.pt"


@torch.no_grad()
def evaluate(model: TinyGPT, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    total = 0.0
    n = 0
    for batch in loader:
        x = batch["input_ids"].to(device)
        y = batch["labels"].to(device)
        _, loss = model(x, y)
        total += float(loss.item())
        n += 1
    return total / max(n, 1)


def save_checkpoint(path, model, opt, cfg, epoch, val_loss, history):
    torch.save(
        {
            "model": model.state_dict(),
            "optimizer": opt.state_dict(),
            "config": cfg.to_dict(),
            "epoch": epoch,
            "val_loss": val_loss,
            "history": history,
        },
        path,
    )


if __name__ == "__main__":
    stage = "c1"
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        stage = args[0]
    config = ML / "configs" / f"curriculum_{stage}.yaml"
    data = yaml.safe_load(config.read_text())
    if "--quick" in sys.argv:
        data["epochs"] = 1
        data["batch_size"] = min(int(data.get("batch_size", 8)), 4)
    # Optional: stop after N optimizer steps (fast smoke)
    max_steps = None
    for a in sys.argv:
        if a.startswith("--max-steps="):
            max_steps = int(a.split("=", 1)[1])
    if max_steps:
        data["max_steps"] = max_steps
        data["epochs"] = 1
        data["batch_size"] = min(int(data.get("batch_size", 8)), 4)
    if "--quick" in sys.argv or max_steps:
        quick = ML / "configs" / f"_quick_{stage}.yaml"
        quick.write_text(yaml.dump(data), encoding="utf-8")
        config = quick

    # Curriculum init: by default c2/c3 auto-load the previous stage's best
    # checkpoint (see STAGE_ORDER). --from-scratch disables that. --init-from=
    # overrides it with an explicit checkpoint path.
    from_scratch = "--from-scratch" in sys.argv
    init_from = None
    for a in sys.argv:
        if a.startswith("--init-from="):
            init_from = Path(a.split("=", 1)[1])

    train_stage(config, init_from=init_from, from_scratch=from_scratch)

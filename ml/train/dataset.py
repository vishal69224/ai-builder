"""Dataset loader for pre-tokenized shards + curriculum replay mixing."""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


class ShardDataset(Dataset):
    def __init__(self, shard_dir: Path, split: str = "train", max_seq_len: int = 512) -> None:
        self.max_seq_len = max_seq_len
        self.shard_dir = Path(shard_dir)
        tokens = np.load(self.shard_dir / f"{split}_tokens.npy")
        lengths = np.load(self.shard_dir / f"{split}_lengths.npy")
        self.sequences: list[np.ndarray] = []
        offset = 0
        for length in lengths.tolist():
            seq = tokens[offset : offset + length]
            offset += length
            self.sequences.append(seq)

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        seq = self.sequences[idx].astype(np.int64)
        if len(seq) > self.max_seq_len:
            seq = seq[: self.max_seq_len]
        # input / target shift
        x = seq[:-1]
        y = seq[1:].copy()
        return {
            "input_ids": torch.from_numpy(x),
            "labels": torch.from_numpy(y),
        }


class MixedReplayDataset(Dataset):
    """Blend current-stage shards with prior-stage replay examples.

    With probability `replay_ratio`, sample from the replay pool; otherwise
    sample from the current stage. Epoch length equals the current stage size
    so step counts stay comparable to a non-replay run.
    """

    def __init__(
        self,
        current: ShardDataset,
        replay: list[ShardDataset],
        *,
        replay_ratio: float = 0.3,
        seed: int = 42,
    ) -> None:
        self.current = current
        self.replay = [r for r in replay if len(r) > 0]
        self.replay_ratio = float(max(0.0, min(1.0, replay_ratio)))
        self._rng = random.Random(seed)
        if not self.replay:
            self.replay_ratio = 0.0

    def __len__(self) -> int:
        return len(self.current)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        if self.replay and self._rng.random() < self.replay_ratio:
            pool = self.replay[self._rng.randrange(len(self.replay))]
            j = self._rng.randrange(len(pool))
            return pool[j]
        return self.current[idx % len(self.current)]


def shard_dir_from_manifest(repo: Path, manifest_path: str | Path) -> Path:
    """Map `datasets/processed/ds_comp_v1/manifest.json` → `datasets/shards/ds_comp_v1`."""
    p = Path(manifest_path)
    name = p.parent.name if p.suffix == ".json" else p.name
    return repo / "datasets" / "shards" / name


def collate_pad(batch: list[dict], pad_id: int = 2) -> dict[str, torch.Tensor]:
    max_len = max(b["input_ids"].numel() for b in batch)
    bsz = len(batch)
    input_ids = torch.full((bsz, max_len), pad_id, dtype=torch.long)
    labels = torch.full((bsz, max_len), -100, dtype=torch.long)
    for i, b in enumerate(batch):
        n = b["input_ids"].numel()
        input_ids[i, :n] = b["input_ids"]
        labels[i, :n] = b["labels"]
    return {"input_ids": input_ids, "labels": labels}

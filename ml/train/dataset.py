"""Dataset loader for pre-tokenized shards."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


class ShardDataset(Dataset):
    def __init__(self, shard_dir: Path, split: str = "train", max_seq_len: int = 512) -> None:
        self.max_seq_len = max_seq_len
        tokens = np.load(shard_dir / f"{split}_tokens.npy")
        lengths = np.load(shard_dir / f"{split}_lengths.npy")
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

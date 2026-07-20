"""Serialize JSONL datasets into training text + token shards for TinyGPT."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from tokenizer.specials import format_training_example
from tokenizer.wrapper import TinyGPTTokenizer

REPO = Path(__file__).resolve().parents[3]


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def example_to_text(ex: dict) -> str:
    mode = {"component": "comp", "page": "page", "site": "site"}.get(ex.get("stage", "component"), "comp")
    return format_training_example(ex["prompt"], ex["files"], mode=mode)


def build_shards(dataset_dir: Path, out_dir: Path, max_seq_len: int = 512) -> dict:
    tok = TinyGPTTokenizer()
    out_dir.mkdir(parents=True, exist_ok=True)
    stats = {}
    for split in ("train", "val", "test"):
        src = dataset_dir / f"{split}.jsonl"
        if not src.exists():
            continue
        sequences: list[list[int]] = []
        for ex in iter_jsonl(src):
            text = example_to_text(ex)
            ids = tok.encode(text, add_special_tokens=False)
            # truncate long examples for stage
            if len(ids) > max_seq_len:
                ids = ids[:max_seq_len]
            if len(ids) < 8:
                continue
            sequences.append(ids)
        # pack into flat array with lengths
        flat = []
        lengths = []
        for seq in sequences:
            flat.extend(seq)
            lengths.append(len(seq))
        arr = np.array(flat, dtype=np.uint16 if tok.vocab_size < 65535 else np.uint32)
        len_arr = np.array(lengths, dtype=np.int32)
        np.save(out_dir / f"{split}_tokens.npy", arr)
        np.save(out_dir / f"{split}_lengths.npy", len_arr)
        stats[split] = {"sequences": len(sequences), "tokens": int(len_arr.sum())}
    meta = {
        "dataset": str(dataset_dir),
        "out": str(out_dir),
        "vocab_size": tok.vocab_size,
        "max_seq_len": max_seq_len,
        "splits": stats,
    }
    (out_dir / "shard_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return meta


def build_all_shards() -> None:
    mapping = [
        ("ds_comp_v1", 512),
        ("ds_page_v1", 1024),
        ("ds_site_v1", 2048),
    ]
    for name, seq in mapping:
        ds = REPO / "datasets" / "processed" / name
        out = REPO / "datasets" / "shards" / name
        if (ds / "train.jsonl").exists():
            build_shards(ds, out, max_seq_len=seq)


if __name__ == "__main__":
    build_all_shards()

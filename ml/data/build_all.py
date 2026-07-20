"""Build all Phase 3 datasets, retrain tokenizer, create shards."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure ml/ is on path
ML = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML))

from data.builders.component_builder import build as build_comp
from data.builders.page_builder import build as build_page
from data.builders.site_builder import build as build_site
from tokenizer.build_corpus import build_corpus
from tokenizer.train_tokenizer import train_tokenizer
from data.serialize.to_shards import build_all_shards


def main() -> None:
    print("=== Building datasets ===")
    m1 = build_comp(2500)
    m2 = build_page(1200)
    m3 = build_site(600)

    # Enrich tokenizer corpus with dataset train text
    print("=== Expanding tokenizer corpus from datasets ===")
    from tokenizer.specials import format_training_example

    corpus_extra = ML / "tokenizer" / "corpus" / "dataset_extra.txt"
    lines = []
    for ds in ("ds_comp_v1", "ds_page_v1", "ds_site_v1"):
        path = ML.parent / "datasets" / "processed" / ds / "train.jsonl"
        with path.open(encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i > 800:  # sample for tokenizer diversity
                    break
                ex = json.loads(line)
                mode = {"component": "comp", "page": "page", "site": "site"}[ex["stage"]]
                lines.append(format_training_example(ex["prompt"], ex["files"], mode=mode))
                for fi in ex["files"]:
                    lines.append(fi["content"])
    corpus_extra.write_text("\n\n".join(lines), encoding="utf-8")
    # Append into main corpus
    main_corpus = ML / "tokenizer" / "corpus" / "train_corpus.txt"
    build_corpus()
    with main_corpus.open("a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write(corpus_extra.read_text(encoding="utf-8"))

    print("=== Retraining tokenizer ===")
    train_tokenizer()

    print("=== Building token shards ===")
    build_all_shards()

    summary = {"comp": m1, "page": m2, "site": m3}
    out = ML.parent / "datasets" / "processed" / "phase3_summary.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Phase 3 complete:", out)


if __name__ == "__main__":
    main()

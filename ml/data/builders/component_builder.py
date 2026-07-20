"""Build ds_comp_v1 — prompt → single React component pairs."""

from __future__ import annotations

import json
from pathlib import Path

from data.templates import (
    BRANDS,
    COMPONENT_BUILDERS,
    COMPONENTS,
    COLORS,
    SITE_TYPES,
    STYLES,
    stable_id,
)

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "datasets" / "processed" / "ds_comp_v1"


def build(target: int = 2500) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "train.jsonl"
    examples = []
    i = 0
    while len(examples) < target:
        for brand in BRANDS:
            for style in STYLES:
                for dark in (False, True):
                    for glass in (False, True):
                        for comp in COMPONENTS:
                            site = SITE_TYPES[i % len(SITE_TYPES)]
                            pages = site[1]
                            color = COLORS[i % len(COLORS)]
                            builder = COMPONENT_BUILDERS[comp]
                            content = builder(
                                brand=brand,
                                pages=pages,
                                dark=dark or style == "dark",
                                glass=glass or "glass" in style,
                                subtitle=f"{site[0].title()} experience for {brand}.",
                                cta="Get started",
                            )
                            style_bits = []
                            if dark or style == "dark":
                                style_bits.append("dark mode")
                            if glass:
                                style_bits.append("glassmorphism")
                            style_bits.append(style)
                            prompt = f"Create a {comp} component for a {site[0]} called {brand} with {' and '.join(style_bits)}"
                            ex = {
                                "id": stable_id("comp", prompt, comp, i),
                                "stage": "component",
                                "prompt": prompt,
                                "files": [{"path": f"src/components/{comp}.tsx", "content": content}],
                                "tags": [comp.lower(), style, site[0].replace(" ", "_")],
                                "license": "synthetic-mit",
                            }
                            examples.append(ex)
                            i += 1
                            if len(examples) >= target:
                                break
                        if len(examples) >= target:
                            break
                    if len(examples) >= target:
                        break
                if len(examples) >= target:
                    break
            if len(examples) >= target:
                break

    # split
    n = len(examples)
    n_val = max(50, n // 50)
    n_test = max(50, n // 50)
    train, val, test = examples[: n - n_val - n_test], examples[n - n_val - n_test : n - n_test], examples[n - n_test :]

    def write(name: str, rows: list) -> None:
        p = OUT / name
        with p.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    write("train.jsonl", train)
    write("val.jsonl", val)
    write("test.jsonl", test)
    manifest = {
        "name": "ds_comp_v1",
        "stage": "component",
        "counts": {"train": len(train), "val": len(val), "test": len(test), "total": n},
        "path": str(OUT),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    build()

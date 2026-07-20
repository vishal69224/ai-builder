"""Build ds_page_v1 — prompt → page (+ optional components)."""

from __future__ import annotations

import json
from pathlib import Path

from data.templates import (
    BRANDS,
    SITE_TYPES,
    STYLES,
    card_tsx,
    cta_tsx,
    feature_grid_tsx,
    hero_tsx,
    page_tsx,
    stable_id,
)

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "datasets" / "processed" / "ds_page_v1"


def build(target: int = 1200) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    examples = []
    i = 0
    while len(examples) < target:
        for brand in BRANDS:
            for style in STYLES:
                for site_name, pages in SITE_TYPES:
                    dark = style in {"dark", "luxury"} or i % 2 == 0
                    for page in pages:
                        files = [
                            {
                                "path": f"src/pages/{('Home' if page.lower()=='home' else page.replace(' ', ''))}Page.tsx",
                                "content": page_tsx(page, brand, use_hero=page.lower() == "home"),
                            }
                        ]
                        if page.lower() == "home":
                            files.extend(
                                [
                                    {
                                        "path": "src/components/Hero.tsx",
                                        "content": hero_tsx(brand, f"A {style} {site_name}.", "Explore", dark),
                                    },
                                    {"path": "src/components/FeatureGrid.tsx", "content": feature_grid_tsx()},
                                    {"path": "src/components/CTA.tsx", "content": cta_tsx(brand)},
                                    {"path": "src/components/Card.tsx", "content": card_tsx()},
                                ]
                            )
                        prompt = f"Create a {page} page for a {style} {site_name} website called {brand}"
                        examples.append(
                            {
                                "id": stable_id("page", prompt, i),
                                "stage": "page",
                                "prompt": prompt,
                                "files": files,
                                "tags": [page.lower(), style, site_name.replace(" ", "_")],
                                "license": "synthetic-mit",
                            }
                        )
                        i += 1
                        if len(examples) >= target:
                            break
                    if len(examples) >= target:
                        break
                if len(examples) >= target:
                    break
            if len(examples) >= target:
                break

    n = len(examples)
    n_val = max(40, n // 50)
    n_test = max(40, n // 50)
    train = examples[: n - n_val - n_test]
    val = examples[n - n_val - n_test : n - n_test]
    test = examples[n - n_test :]

    def write(name: str, rows: list) -> None:
        with (OUT / name).open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    write("train.jsonl", train)
    write("val.jsonl", val)
    write("test.jsonl", test)
    manifest = {
        "name": "ds_page_v1",
        "stage": "page",
        "counts": {"train": len(train), "val": len(val), "test": len(test), "total": n},
        "path": str(OUT),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    build()

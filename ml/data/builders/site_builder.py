"""Build ds_site_v1 — prompt → full React project file sets."""

from __future__ import annotations

import json
from pathlib import Path

from data.templates import (
    BRANDS,
    COLORS,
    SITE_TYPES,
    STYLES,
    app_tsx,
    footer_tsx,
    index_css,
    index_html,
    main_tsx,
    navbar_tsx,
    package_json,
    page_tsx,
    slugify,
    stable_id,
)

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "datasets" / "processed" / "ds_site_v1"


def build(target: int = 600) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    examples = []
    i = 0
    while len(examples) < target:
        for brand in BRANDS:
            for style in STYLES:
                for site_name, pages in SITE_TYPES:
                    dark = style in {"dark", "luxury"} or "dark" in site_name
                    glass = style in {"modern", "luxury"}
                    color = COLORS[i % len(COLORS)]
                    files = [
                        {"path": "package.json", "content": package_json(slugify(brand))},
                        {"path": "index.html", "content": index_html(brand)},
                        {"path": "src/main.tsx", "content": main_tsx()},
                        {"path": "src/App.tsx", "content": app_tsx(pages)},
                        {"path": "src/index.css", "content": index_css(dark, color)},
                        {
                            "path": "src/components/Navbar.tsx",
                            "content": navbar_tsx(brand, pages, dark, glass),
                        },
                        {"path": "src/components/Footer.tsx", "content": footer_tsx(brand, dark)},
                    ]
                    for page in pages:
                        pname = "Home" if page.lower() == "home" else page.replace(" ", "")
                        files.append(
                            {
                                "path": f"src/pages/{pname}Page.tsx",
                                "content": page_tsx(page, brand, use_hero=page.lower() == "home"),
                            }
                        )
                    bits = [style]
                    if dark:
                        bits.append("dark mode")
                    if glass:
                        bits.append("smooth animations")
                    prompt = f"Build a {style} {site_name} website called {brand} with {' and '.join(bits)}"
                    examples.append(
                        {
                            "id": stable_id("site", prompt, i),
                            "stage": "site",
                            "prompt": prompt,
                            "files": files,
                            "meta": {
                                "website_type": site_name,
                                "pages": pages,
                                "framework": "React",
                                "styling": "Tailwind",
                                "brand": brand,
                            },
                            "tags": [site_name.replace(" ", "_"), style],
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

    n = len(examples)
    n_val = max(30, n // 40)
    n_test = max(30, n // 40)
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
        "name": "ds_site_v1",
        "stage": "site",
        "counts": {"train": len(train), "val": len(val), "test": len(test), "total": n},
        "path": str(OUT),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    build()

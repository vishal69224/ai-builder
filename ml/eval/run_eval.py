"""Evaluation harness for TinyGPT curriculum stages.

Usage:
  cd ml && source .venv/bin/activate
  PYTHONPATH=. python -m eval.run_eval c1
  PYTHONPATH=. python -m eval.run_eval c2 --ckpt ../checkpoints/tinygpt-8m-c2/best.pt
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ML = Path(__file__).resolve().parents[1]
REPO = ML.parent
sys.path.insert(0, str(ML))

from serve.server import generate_text, load_model, parse_files  # noqa: E402
from train.train_stage import get_device  # noqa: E402

GATES = {
    "c1": {"format_valid_pct": 90, "jsx_parse_pct": 80, "mode": "comp"},
    "c2": {"format_valid_pct": 85, "jsx_parse_pct": 70, "mode": "page"},
    "c3": {"format_valid_pct": 80, "jsx_parse_pct": 50, "mode": "site"},
}


def _looks_jsx(content: str) -> bool:
    c = content or ""
    if "export " not in c and "export default" not in c:
        return False
    return bool(re.search(r"<\/?[A-Za-z][\w.-]*[\s/>]", c) or "React" in c or "jsx" in c.lower())


def _format_valid(files: list[dict[str, str]], mode: str) -> bool:
    if not files:
        return False
    for f in files:
        path = f.get("path") or ""
        content = f.get("content") or ""
        if not path or not content.strip():
            return False
        if mode == "comp" and ("export" not in content):
            return False
    if mode == "site":
        paths = {f["path"] for f in files}
        if not any(p.endswith("App.tsx") or p == "src/App.tsx" for p in paths) and "package.json" not in paths:
            # Still ok if several source files
            if sum(1 for p in paths if p.endswith((".tsx", ".ts"))) < 2:
                return False
    return True


def load_prompts(stage: str) -> list[str]:
    path = ML / "eval" / "prompts_golden.jsonl"
    prompts: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("stage") in {stage, "all", None} or "stage" not in row:
                prompts.append(str(row["prompt"]))
    if not prompts:
        prompts = [
            "A minimal React button component with Tailwind classes",
            "Hero section for a luxury clothing brand called Vishu Creation",
            "Product card with image, price, and add to cart",
            "Contact form page with email and phone fields",
            "Portfolio page for a Flutter developer named Alex",
        ]
    return prompts[:20]


def run_eval(stage: str, ckpt: Path | None = None) -> dict:
    gate = GATES[stage]
    mode = gate["mode"]
    ckpt = ckpt or (REPO / "checkpoints" / f"tinygpt-8m-{stage}" / "best.pt")
    if not ckpt.exists():
        return {"ok": False, "error": f"checkpoint missing: {ckpt}", "stage": stage}

    model, tok, meta = load_model(ckpt)
    prompts = load_prompts(stage)
    format_ok = 0
    jsx_ok = 0
    details = []

    for prompt in prompts:
        raw = generate_text(model, tok, prompt, mode=mode, max_new_tokens=256 if mode == "comp" else 512)
        files = parse_files(raw)
        fv = _format_valid(files, mode)
        jx = any(_looks_jsx(f.get("content", "")) for f in files) if files else False
        format_ok += int(fv)
        jsx_ok += int(jx)
        details.append(
            {
                "prompt": prompt[:80],
                "files": len(files),
                "format_valid": fv,
                "jsx_parse": jx,
            }
        )

    n = max(len(prompts), 1)
    format_pct = 100.0 * format_ok / n
    jsx_pct = 100.0 * jsx_ok / n
    passed = format_pct >= gate["format_valid_pct"] and jsx_pct >= gate["jsx_parse_pct"]
    report = {
        "ok": passed,
        "stage": stage,
        "checkpoint": str(ckpt),
        "device": str(get_device()),
        "meta": meta,
        "n": n,
        "format_valid_pct": round(format_pct, 1),
        "jsx_parse_pct": round(jsx_pct, 1),
        "gates": gate,
        "details": details,
    }
    out = ML / "eval" / f"report_{stage}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "details"}, indent=2))
    print(f"wrote {out}")
    return report


if __name__ == "__main__":
    stage = "c1"
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        stage = args[0]
    ckpt = None
    for a in sys.argv:
        if a.startswith("--ckpt="):
            ckpt = Path(a.split("=", 1)[1])
    run_eval(stage, ckpt)

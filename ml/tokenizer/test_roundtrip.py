"""Round-trip and special-token tests for Phase 2 tokenizer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tokenizer.specials import format_training_example, load_special_token_map
from tokenizer.wrapper import TinyGPTTokenizer

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "artifacts" / "roundtrip_report.json"

SAMPLES = [
    'export function Navbar() {\n  return <header className="bg-white/10 backdrop-blur-xl">Bean</header>\n}\n',
    'import { Route, Routes } from \'react-router-dom\'\n',
    '{"name":"bean-house","dependencies":{"react":"^19.0.0"}}\n',
    '@import "tailwindcss";\n:root { --brand: #0d9488; }\n',
]


def run_tests() -> dict:
    tok = TinyGPTTokenizer()
    st = load_special_token_map()
    results = []
    failures = []

    # 1) Special tokens must have IDs
    for name, token in st.items():
        tid = tok.token_to_id(token)
        ok = tid is not None
        results.append({"check": f"special_id:{name}", "ok": ok, "id": tid})
        if not ok:
            failures.append(f"missing special token id: {token}")

    # 2) Round-trip code samples (ByteLevel may normalize spaces — compare via re-encode)
    for i, sample in enumerate(SAMPLES):
        ids = tok.encode(sample, add_special_tokens=False)
        decoded = tok.decode(ids, skip_special_tokens=False)
        # Re-encode decoded text; IDs should match for lossless byte-level BPE
        ids2 = tok.encode(decoded, add_special_tokens=False)
        ok = ids == ids2
        results.append(
            {
                "check": f"roundtrip_sample_{i}",
                "ok": ok,
                "n_tokens": len(ids),
                "preview": decoded[:80].replace("\n", "\\n"),
            }
        )
        if not ok:
            failures.append(f"roundtrip failed sample {i}")

    # 3) Structured training string
    structured = format_training_example(
        "Create a Card component",
        [{"path": "src/components/Card.tsx", "content": "export function Card() { return <div /> }\n"}],
        mode="comp",
    )
    ids = tok.encode(structured, add_special_tokens=False)
    decoded = tok.decode(ids, skip_special_tokens=False)
    # All special markers should survive
    for key in ("bos", "user", "assistant", "comp", "file", "path", "content", "eos"):
        marker = st[key]
        present = marker in decoded or marker in structured
        # After encode/decode, specials as single tokens should decode back to the string
        ok = marker in decoded
        results.append({"check": f"structured_contains:{key}", "ok": ok})
        if not ok:
            failures.append(f"structured decode missing {marker}")

    # 4) Compression sanity: TSX should not explode to 1 token per char forever
    long_tsx = SAMPLES[0] * 5
    n = len(tok.encode(long_tsx, add_special_tokens=False))
    chars = len(long_tsx)
    ratio = chars / max(n, 1)
    ok_ratio = ratio >= 2.0  # at least ~2 chars/token average
    results.append({"check": "compression_ratio", "ok": ok_ratio, "chars_per_token": round(ratio, 2)})
    if not ok_ratio:
        failures.append(f"poor compression ratio: {ratio}")

    report = {
        "vocab_size": tok.vocab_size,
        "passed": len(failures) == 0,
        "failures": failures,
        "results": results,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    report = run_tests()
    sys.exit(0 if report["passed"] else 1)

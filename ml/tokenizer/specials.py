"""Special token constants and helpers for TinyGPT tokenizer."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPECIAL_TOKENS_PATH = ROOT / "special_tokens.json"


def load_special_token_map() -> dict[str, str]:
    return json.loads(SPECIAL_TOKENS_PATH.read_text(encoding="utf-8"))


def special_token_list() -> list[str]:
    return list(load_special_token_map().values())


def format_training_example(
    prompt: str,
    files: list[dict[str, str]],
    mode: str = "comp",
) -> str:
    """Serialize prompt + files into the TinyGPT training string format."""
    st = load_special_token_map()
    mode_token = st.get(mode, st["comp"])
    parts = [
        st["bos"],
        st["user"],
        prompt.strip(),
        st["assistant"],
        mode_token,
    ]
    for f in files:
        parts.append(st["file"])
        parts.append(st["path"])
        parts.append(f["path"].strip())
        parts.append(st["content"])
        parts.append(f["content"])
        if not f["content"].endswith("\n"):
            parts.append("\n")
        parts.append(st["eos"])
    return "".join(parts)

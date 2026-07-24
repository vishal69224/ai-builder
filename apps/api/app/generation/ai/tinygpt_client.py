"""TinyGPT HTTP client — taglines + hybrid component/page/site generation.

Talks to ml/serve/server.py on localhost:8100. Soft-fails to None so the
rule-based generators always remain a working fallback.
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger("tinygpt_client")

DEFAULT_BASE = "http://127.0.0.1:8100"
TAGLINE_TIMEOUT = 2.0
GENERATE_TIMEOUT = 45.0


def health(*, base_url: str = DEFAULT_BASE, timeout: float = 1.5) -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/v1/health", timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        logger.debug("TinyGPT health failed: %s", exc)
        return None


def fetch_tagline(prompt: str, *, base_url: str = DEFAULT_BASE) -> str | None:
    """Ask TinyGPT for a short site tagline (uses component endpoint)."""
    text = (prompt or "").strip()
    if not text:
        return None

    result = _post_generate(
        "component",
        (
            "Write one short website tagline (max 12 words) for this site. "
            "Reply with the tagline only, no quotes, no code.\n\n"
            f"{text[:800]}"
        ),
        base_url=base_url,
        max_new_tokens=48,
        temperature=0.5,
        timeout=TAGLINE_TIMEOUT,
    )
    if not result:
        return None

    raw = str(result.get("raw_text") or "")
    # Prefer plain text before file markers
    cleaned = _extract_plain_tagline(raw)
    if not cleaned:
        return None
    if len(cleaned) < 4 or len(cleaned) > 120:
        return None
    return cleaned


def generate_files(
    prompt: str,
    *,
    mode: str = "site",
    base_url: str = DEFAULT_BASE,
    max_new_tokens: int = 768,
    temperature: float = 0.35,
    timeout: float = GENERATE_TIMEOUT,
) -> list[dict[str, str]] | None:
    """Generate file payloads from TinyGPT. mode: component | page | site."""
    text = (prompt or "").strip()
    if not text:
        return None
    endpoint = {"component": "component", "comp": "component", "page": "page", "site": "site"}.get(
        mode, "site"
    )
    result = _post_generate(
        endpoint,
        text,
        base_url=base_url,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        timeout=timeout,
    )
    if not result:
        return None
    files = result.get("files")
    if not isinstance(files, list) or not files:
        # Try parse raw_text locally if server returned empty files
        raw = str(result.get("raw_text") or "")
        files = _parse_files_fallback(raw)
    cleaned: list[dict[str, str]] = []
    for f in files or []:
        if not isinstance(f, dict):
            continue
        path = str(f.get("path") or "").strip().lstrip("/")
        content = str(f.get("content") or "")
        if path and content.strip():
            cleaned.append({"path": path, "content": content})
    return cleaned or None


def files_pass_quality_gate(files: list[dict[str, str]], *, mode: str = "site") -> bool:
    """Cheap hybrid gate before replacing rule-engine output."""
    if not files:
        return False
    by_path = {f["path"]: f["content"] for f in files}
    joined = "\n".join(by_path.values())

    # Format / JSX-ish signals
    has_export = "export " in joined or "export default" in joined
    has_jsx = ("<" in joined and ">" in joined) or "react" in joined.lower()
    if not has_export:
        return False

    # Reject obvious incomplete shells that break vite (missing FeatureGrid etc.)
    import_re = re.compile(r"""from\s+['"](\.\.?/[^'"]+)['"]""")
    for path, content in by_path.items():
        if not path.endswith((".tsx", ".ts", ".jsx", ".js")):
            continue
        parent = "/".join(path.split("/")[:-1])
        for rel in import_re.findall(content or ""):
            parts = (parent + "/" + rel).split("/")
            stack: list[str] = []
            for part in parts:
                if part in ("", "."):
                    continue
                if part == "..":
                    if stack:
                        stack.pop()
                    continue
                stack.append(part)
            resolved = "/".join(stack)
            candidates = {
                resolved,
                resolved + ".tsx",
                resolved + ".ts",
                resolved + ".jsx",
                resolved + ".js",
                resolved + "/index.tsx",
                resolved + "/index.ts",
            }
            if not candidates.intersection(by_path):
                # Allow external packages (no relative path) — already filtered by \./
                # Missing local import → fail the gate
                return False

    if mode == "component":
        return len(files) >= 1 and has_jsx

    if mode == "page":
        return any("pages/" in p or p.endswith("Page.tsx") for p in by_path) or has_jsx

    # site
    has_app = any(p.endswith("App.tsx") or p == "src/App.tsx" for p in by_path)
    has_pkg = "package.json" in by_path
    # Accept partial site generations that still look like real React sources
    tsx_count = sum(1 for p in by_path if p.endswith((".tsx", ".ts", ".jsx", ".js")))
    if has_app or has_pkg:
        return tsx_count >= 2 or has_jsx
    return tsx_count >= 3 and has_jsx


def _post_generate(
    endpoint: str,
    prompt: str,
    *,
    base_url: str,
    max_new_tokens: int,
    temperature: float,
    timeout: float,
) -> dict[str, Any] | None:
    url = f"{base_url.rstrip('/')}/v1/generate/{endpoint}"
    payload = json.dumps(
        {
            "prompt": prompt,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": 0.9,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        logger.debug("TinyGPT generate/%s failed: %s", endpoint, exc)
        return None


def _extract_plain_tagline(raw: str) -> str | None:
    text = raw or ""
    # Drop special tokens and file blocks
    text = re.sub(r"<\|[^|>]+\|>", " ", text)
    text = re.sub(r"(?is)<\|file\|>.*", " ", text)
    line = " ".join(text.split()).strip(" \"'")
    if not line:
        return None
    # First sentence / line only
    line = re.split(r"[\n.!?]", line)[0].strip()
    words = line.split()
    if len(words) > 14:
        line = " ".join(words[:12])
    return line or None


def _parse_files_fallback(text: str) -> list[dict[str, str]]:
    files: list[dict[str, str]] = []
    if "<|file|>" not in text and "<|path|>" not in text:
        return files
    parts = text.split("<|file|>")
    for part in parts[1:]:
        if "<|path|>" not in part or "<|content|>" not in part:
            continue
        after = part.split("<|path|>", 1)[1]
        path_part, content_part = after.split("<|content|>", 1)
        path = path_part.strip()
        content = content_part.split("<|eos|>")[0]
        if path:
            files.append({"path": path, "content": content})
    return files

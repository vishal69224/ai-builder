"""Optional TinyGPT HTTP client — short taglines from localhost:8100."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

logger = logging.getLogger("tinygpt_client")

DEFAULT_URL = "http://127.0.0.1:8100/generate"
TIMEOUT_SECONDS = 2.0


def fetch_tagline(prompt: str, *, base_url: str = DEFAULT_URL) -> str | None:
    """Ask a local TinyGPT-style service for a short site tagline.

    Returns None on any failure (offline, timeout, bad payload) so generation
    can continue without TinyGPT.
    """
    text = (prompt or "").strip()
    if not text:
        return None

    payload = json.dumps(
        {
            "prompt": (
                "Write one short website tagline (max 12 words) for this site. "
                "Reply with the tagline only, no quotes.\n\n"
                f"{text[:800]}"
            ),
            "max_tokens": 40,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        base_url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.debug("TinyGPT unavailable: %s", exc)
        return None

    tagline = _parse_tagline(raw)
    if not tagline:
        return None
    # Keep it short and safe for HTML attributes
    cleaned = " ".join(tagline.split()).strip(" \"'")
    if len(cleaned) < 4 or len(cleaned) > 120:
        return None
    return cleaned


def _parse_tagline(raw: str) -> str | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw.splitlines()[0].strip() or None

    if isinstance(data, str):
        return data.strip() or None
    if isinstance(data, dict):
        for key in ("tagline", "text", "output", "response", "content", "result"):
            val = data.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
            if isinstance(val, dict):
                inner = val.get("text") or val.get("content")
                if isinstance(inner, str) and inner.strip():
                    return inner.strip()
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                msg = first.get("message") or first
                if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                    return msg["content"].strip()
                if isinstance(first.get("text"), str):
                    return first["text"].strip()
    return None

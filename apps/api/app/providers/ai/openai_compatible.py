import json
import re

import httpx

from app.domain.paths import sanitize_relative_path
from app.providers.ai.schemas import FileSpec, GenerationRequest, GenerationResult

SYSTEM_PROMPT = """You are an expert React engineer. Generate a complete Vite + React + TypeScript + Tailwind v4 website.
Return ONLY valid JSON with this shape:
{"summary":"short string","files":[{"path":"relative/path","content":"file contents"}]}
Rules:
- Include package.json, index.html, vite.config.ts, tsconfig.json, src/main.tsx, src/App.tsx, src/index.css
- Use @tailwindcss/vite plugin and @import "tailwindcss" in CSS
- Do not include markdown fences
- Paths must be relative, no .. segments
"""

EDIT_SYSTEM_PROMPT = """You are an expert React + Tailwind engineer editing an existing Vite website.
Return ONLY valid JSON:
{"summary":"short string","files":[{"path":"relative/path","content":"full updated file contents"}]}
Rules:
- Only return files you changed (full file content for each)
- Keep TypeScript/TSX valid
- Preserve brand names and routes unless the user asks to change them
- Prefer visual polish: spacing, typography, hero, CTAs, colors
- Do not wrap in markdown fences
"""


class OpenAICompatibleProvider:
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def generate_site(self, request: GenerationRequest) -> GenerationResult:
        user_content = {
            "project_name": request.project_name,
            "prompt": request.prompt,
            "prior_files": (
                [{"path": f.path, "content": f.content[:4000]} for f in (request.prior_files or [])[:20]
                ]
                if request.prior_files
                else None
            ),
        }
        payload = {
            "model": self.model,
            "temperature": 0.4,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_content)},
            ],
        }
        return self._complete(payload)

    def edit_site(self, request: GenerationRequest) -> GenerationResult:
        prior = request.prior_files or []
        user_content = {
            "project_name": request.project_name,
            "edit_instruction": request.prompt,
            "files": [{"path": f.path, "content": f.content[:12000]} for f in prior[:24]],
        }
        payload = {
            "model": self.model,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": EDIT_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_content)},
            ],
        }
        return self._complete(payload)

    def _complete(self, payload: dict) -> GenerationResult:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # OpenRouter recommends these headers
        if "openrouter.ai" in self.base_url:
            headers["HTTP-Referer"] = "http://localhost:5173"
            headers["X-Title"] = "AI Website Builder"
        with httpx.Client(timeout=120.0) as client:
            response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        parsed = _parse_json_content(content)
        files: list[FileSpec] = []
        for item in parsed.get("files", []):
            path = sanitize_relative_path(item["path"])
            files.append(FileSpec(path=path, content=str(item.get("content", ""))))
        if not files:
            raise ValueError("AI returned no files")
        return GenerationResult(files=files, summary=parsed.get("summary"))


def _parse_json_content(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("AI response was not valid JSON")
        return json.loads(match.group(0))

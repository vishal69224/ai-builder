"""SDD §17 Edit Mode — update only targeted files from follow-up prompts."""

from __future__ import annotations

import re

from app.generation.pipeline import GeneratedFile


EDIT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(navbar|nav bar|navigation)\b", re.I), "src/components/Navbar.tsx"),
    (re.compile(r"\b(footer)\b", re.I), "src/components/Footer.tsx"),
    (re.compile(r"\b(hero|header section)\b", re.I), "src/components/Hero.tsx"),
    (re.compile(r"\b(button|cta)\b", re.I), "src/components/Button.tsx"),
    (re.compile(r"\b(card|cards)\b", re.I), "src/components/Card.tsx"),
    (re.compile(r"\b(theme|dark mode|color palette|styling|css)\b", re.I), "src/index.css"),
]


class EditModeService:
    def is_edit_prompt(self, prompt: str, has_existing_project: bool) -> bool:
        if not has_existing_project:
            return False
        lowered = prompt.lower()
        edit_verbs = ("change", "update", "modify", "make the", "switch", "refine", "edit", "fix")
        return any(v in lowered for v in edit_verbs)

    def detect_targets(self, prompt: str) -> list[str]:
        targets: list[str] = []
        for pattern, path in EDIT_PATTERNS:
            if pattern.search(prompt):
                targets.append(path)
        return list(dict.fromkeys(targets))  # preserve order, unique

    def apply_edits(
        self,
        prompt: str,
        existing_files: list[GeneratedFile],
    ) -> list[GeneratedFile]:
        """Patch existing files; untouched files are returned as-is."""
        targets = self.detect_targets(prompt)
        if not targets:
            return existing_files

        by_path = {f.path: f for f in existing_files}
        lowered = prompt.lower()

        for path in targets:
            current = by_path.get(path)
            if current is None:
                continue

            if path.endswith("Navbar.tsx"):
                by_path[path] = GeneratedFile(path=path, content=self._patch_navbar(current.content, lowered))
            elif path.endswith("index.css"):
                by_path[path] = GeneratedFile(path=path, content=self._patch_css(current.content, lowered))
            elif path.endswith("Hero.tsx"):
                by_path[path] = GeneratedFile(path=path, content=self._patch_hero(current.content, lowered))
            else:
                by_path[path] = GeneratedFile(
                    path=path,
                    content=current.content + f"\n// Edit applied: {prompt[:80]}\n",
                )

        return list(by_path.values())

    def _patch_navbar(self, content: str, lowered: str) -> str:
        if "glassmorphism" in lowered or "glass" in lowered:
            content = re.sub(
                r'className="sticky top-0 z-50 border-b [^"]+"',
                'className="sticky top-0 z-50 border-b bg-white/10 backdrop-blur-xl border-white/20 shadow-lg"',
                content,
            )
            if "bg-white/10" not in content:
                content = content.replace(
                    'className="sticky top-0 z-50 border-b',
                    'className="sticky top-0 z-50 border-b bg-white/10 backdrop-blur-xl border-white/20',
                    1,
                )
        if "dark" in lowered:
            content = content.replace(
                "bg-white/90",
                "bg-slate-950/90 text-white",
            )
        return content

    def _patch_css(self, content: str, lowered: str) -> str:
        if "dark" in lowered:
            content = re.sub(r"--bg: [^;]+;", "--bg: #0a0f1a;", content)
            content = re.sub(r"--text: [^;]+;", "--text: #e2e8f0;", content)
        if "warm" in lowered:
            content = re.sub(r"--brand: [^;]+;", "--brand: #8B5E3C;", content)
        return content

    def _patch_hero(self, content: str, lowered: str) -> str:
        if "bold" in lowered or "large" in lowered:
            content = content.replace("text-4xl", "text-5xl").replace("sm:text-5xl", "sm:text-6xl")
        return content

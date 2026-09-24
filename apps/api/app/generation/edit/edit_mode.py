"""SDD §17 Edit Mode — classify follow-ups, patch files, or hand off to AI."""

from __future__ import annotations

import re
from enum import Enum

from app.generation.pipeline import GeneratedFile


class FollowUpKind(str, Enum):
    revert = "revert"
    polish = "polish"
    targeted_edit = "targeted_edit"
    soft_edit = "soft_edit"
    generate = "generate"


EDIT_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b(navbar|nav bar|navigation)\b", re.I), "src/components/Navbar.tsx"),
    (re.compile(r"\b(footer)\b", re.I), "src/components/Footer.tsx"),
    (re.compile(r"\b(hero|header section|headline)\b", re.I), "src/components/Hero.tsx"),
    (re.compile(r"\b(button|cta)\b", re.I), "src/components/Button.tsx"),
    (re.compile(r"\b(card|cards)\b", re.I), "src/components/Card.tsx"),
    (re.compile(r"\b(theme|dark mode|color palette|styling|css)\b", re.I), "src/index.css"),
    (re.compile(r"\b(product|shop|catalog)\b", re.I), "src/data/catalog.ts"),
    (re.compile(r"\b(fashion hero|store navbar)\b", re.I), "src/components/FashionHero.tsx"),
]

# Also map specialty component paths when present
SPECIALTY_ALIASES = {
    "src/components/Navbar.tsx": (
        "src/components/StoreNavbar.tsx",
        "src/components/PortfolioNav.tsx",
        "src/components/ProductNavbar.tsx",
    ),
    "src/components/Hero.tsx": (
        "src/components/FashionHero.tsx",
        "src/components/PortfolioHero.tsx",
        "src/components/ProductHero.tsx",
    ),
    "src/components/Footer.tsx": (
        "src/components/StoreFooter.tsx",
        "src/components/PortfolioFooter.tsx",
        "src/components/ProductFooter.tsx",
    ),
    "src/components/Button.tsx": (
        "src/components/StoreButton.tsx",
        "src/components/PortfolioButton.tsx",
    ),
}

_REVERT_RE = re.compile(
    r"\b(revert|undo|roll\s*back|go\s*back|previous\s*version|restore\s*(the\s*)?(last|previous)|cancel\s*(the\s*)?changes)\b",
    re.I,
)
_POLISH_RE = re.compile(
    r"\b("
    r"make\s+it\s+(perfect|better|beautiful|premium|luxury|polished|nice)|"
    r"improve(\s+it|\s+the\s+site|\s+the\s+design)?|"
    r"polish(\s+it|\s+the\s+site)?|"
    r"looks?\s+(bad|ugly|worse|broken)|"
    r"fix\s+(the\s+)?(design|ui|layout|site)|"
    r"beautify|"
    r"upgrade\s+(the\s+)?(design|ui|look)"
    r")\b",
    re.I,
)
_EDIT_VERBS = (
    "change",
    "update",
    "modify",
    "make the",
    "switch",
    "refine",
    "edit",
    "fix",
    "replace",
    "rename",
    "add a",
    "remove the",
)


class EditModeService:
    def classify(self, prompt: str, has_existing_project: bool) -> FollowUpKind:
        if not has_existing_project:
            return FollowUpKind.generate
        text = prompt.strip()
        if not text:
            return FollowUpKind.generate
        if _REVERT_RE.search(text):
            return FollowUpKind.revert
        if _POLISH_RE.search(text):
            return FollowUpKind.polish
        lowered = text.lower()
        if any(v in lowered for v in _EDIT_VERBS) or self.detect_targets(text):
            if self.detect_targets(text):
                return FollowUpKind.targeted_edit
            return FollowUpKind.soft_edit
        return FollowUpKind.generate

    def is_edit_prompt(self, prompt: str, has_existing_project: bool) -> bool:
        kind = self.classify(prompt, has_existing_project)
        return kind in {FollowUpKind.targeted_edit, FollowUpKind.soft_edit}

    def is_revert_prompt(self, prompt: str, has_existing_project: bool) -> bool:
        return self.classify(prompt, has_existing_project) == FollowUpKind.revert

    def is_polish_prompt(self, prompt: str, has_existing_project: bool) -> bool:
        return self.classify(prompt, has_existing_project) == FollowUpKind.polish

    def detect_targets(self, prompt: str) -> list[str]:
        targets: list[str] = []
        for pattern, path in EDIT_PATTERNS:
            if pattern.search(prompt):
                targets.append(path)
        return list(dict.fromkeys(targets))

    def resolve_existing_targets(
        self, prompt: str, existing_files: list[GeneratedFile]
    ) -> list[str]:
        """Map logical targets to files that actually exist in the project."""
        by_path = {f.path for f in existing_files}
        resolved: list[str] = []
        for logical in self.detect_targets(prompt):
            if logical in by_path:
                resolved.append(logical)
                continue
            for alias in SPECIALTY_ALIASES.get(logical, ()):
                if alias in by_path:
                    resolved.append(alias)
            # Fashion-specific extras
            if "hero" in prompt.lower() and "src/components/FashionHero.tsx" in by_path:
                resolved.append("src/components/FashionHero.tsx")
            if "catalog" in prompt.lower() or "product" in prompt.lower():
                if "src/data/catalog.ts" in by_path:
                    resolved.append("src/data/catalog.ts")
        return list(dict.fromkeys(resolved))

    def polish_seed_prompt(self, *, project_name: str, last_prompt: str | None, niche_hint: str) -> str:
        brand = (project_name or "Brand").strip()
        base = (last_prompt or "").strip()
        # Prefer the last real build prompt, not a previous polish/revert line
        if base and not (_POLISH_RE.search(base) or _REVERT_RE.search(base)):
            seed = base
        else:
            seed = f"{brand} {niche_hint} website"
        return (
            f"{seed}. Polish this into a premium, client-ready {niche_hint} site for {brand}: "
            "strong hero, clear navigation, refined typography, polished sections, "
            "and a cohesive luxury look. Keep the same brand name."
        )

    def apply_edits(
        self,
        prompt: str,
        existing_files: list[GeneratedFile],
    ) -> list[GeneratedFile]:
        """Patch existing files; untouched files are returned as-is."""
        targets = self.resolve_existing_targets(prompt, existing_files)
        if not targets:
            # Soft edits without targets — nudge hero + css lightly
            targets = [
                p
                for p in (
                    "src/components/FashionHero.tsx",
                    "src/components/Hero.tsx",
                    "src/components/ProductHero.tsx",
                    "src/index.css",
                )
                if any(f.path == p for f in existing_files)
            ][:2]
        if not targets:
            return existing_files

        by_path = {f.path: f for f in existing_files}
        lowered = prompt.lower()

        for path in targets:
            current = by_path.get(path)
            if current is None:
                continue
            name = path.rsplit("/", 1)[-1]
            if "Navbar" in name or path.endswith("Navbar.tsx"):
                by_path[path] = GeneratedFile(path=path, content=self._patch_navbar(current.content, lowered))
            elif path.endswith("index.css"):
                by_path[path] = GeneratedFile(path=path, content=self._patch_css(current.content, lowered))
            elif "Hero" in name:
                by_path[path] = GeneratedFile(path=path, content=self._patch_hero(current.content, lowered))
            elif path.endswith("catalog.ts"):
                by_path[path] = GeneratedFile(path=path, content=self._patch_catalog(current.content, lowered))
            else:
                # Avoid appending junk comments that break TSX
                by_path[path] = GeneratedFile(path=path, content=current.content)

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
            content = content.replace("bg-white/90", "bg-slate-950/90 text-white")
            content = content.replace("bg-[#FAFAF8]/95", "bg-stone-950/95")
        return content

    def _patch_css(self, content: str, lowered: str) -> str:
        if "dark" in lowered or "darker" in lowered:
            content = re.sub(r"--bg: [^;]+;", "--bg: #05080f;", content)
            content = re.sub(r"--text: [^;]+;", "--text: #e2e8f0;", content)
        if "warm" in lowered:
            content = re.sub(r"--brand: [^;]+;", "--brand: #8B5E3C;", content)
        if any(k in lowered for k in ("perfect", "polish", "premium", "luxury")):
            if "letter-spacing" not in content:
                content += (
                    "\nbody { letter-spacing: -0.011em; }\n"
                    "h1, h2, h3 { letter-spacing: -0.03em; }\n"
                )
        return content

    def _patch_hero(self, content: str, lowered: str) -> str:
        if "bold" in lowered or "large" in lowered:
            content = content.replace("text-4xl", "text-5xl").replace("sm:text-5xl", "sm:text-6xl")
        if any(k in lowered for k in ("darker", "dark", "premium", "perfect", "polish", "luxury", "better")):
            content = content.replace("opacity-40", "opacity-20")
            content = content.replace("opacity-50", "opacity-25")
            content = content.replace("bg-[#0B1220]", "bg-[#05080f]")
            content = content.replace("via-[#0B1220]/90", "via-[#05080f]/96")
            content = content.replace("to-[#0B1220]/40", "to-[#05080f]/75")
            content = content.replace("min-h-[68vh]", "min-h-[82vh]")
            content = content.replace("min-h-[70vh]", "min-h-[82vh]")
            content = content.replace("min-h-[76vh]", "min-h-[86vh]")
            content = content.replace("via-stone-950/75", "via-stone-950/92")
            content = content.replace("via-stone-950/55", "via-stone-950/88")
            content = content.replace("to-transparent", "to-stone-950/45")
            content = content.replace("to-stone-950/25", "to-stone-950/55")
            content = content.replace("pb-16", "pb-20")
            content = content.replace("text-stone-300", "text-stone-200")
            if "premium" in lowered or "luxury" in lowered:
                content = content.replace("text-teal-300", "text-amber-200")
                content = content.replace("tracking-[0.28em]", "tracking-[0.34em]")
                content = content.replace("font-serif text-4xl", "font-serif text-5xl")
        return content

    def _patch_catalog(self, content: str, lowered: str) -> str:
        if "cheaper" in lowered or "lower price" in lowered:
            content = re.sub(r'"price":\s*(\d+)', lambda m: f'"price": {max(20, int(m.group(1)) - 10)}', content)
        if "expensive" in lowered or "premium price" in lowered:
            content = re.sub(r'"price":\s*(\d+)', lambda m: f'"price": {int(m.group(1)) + 20}', content)
        return content

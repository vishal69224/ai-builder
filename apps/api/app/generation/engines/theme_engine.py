"""Theme Engine (Phase 2) — WebsitePlan → design tokens → CSS variables.

Additive: only used when GEN_V2_THEME=true. Does not change component structure.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.generation.pipeline import WebsitePlan


# Preset library — keyed by WebsitePlan.theme.token_preset
THEME_PRESETS: dict[str, dict[str, Any]] = {
    "luxury_minimal": {
        "id": "luxury_minimal",
        "mode": "light",
        "colors": {
            "primary": "#111827",
            "secondary": "#F9FAFB",
            "accent": "#B45309",
            "bg": "#FAFAF9",
            "text": "#111827",
            "muted": "#78716C",
            "line": "#E7E5E4",
        },
        "radius": "16px",
        "font": '"Fraunces", "Iowan Old Style", Georgia, serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Luxury Minimal",
    },
    "bold_modern": {
        "id": "bold_modern",
        "mode": "light",
        "colors": {
            "primary": "#0F172A",
            "secondary": "#F8FAFC",
            "accent": "#2563EB",
            "bg": "#F8FAFC",
            "text": "#0F172A",
            "muted": "#64748B",
            "line": "#E2E8F0",
        },
        "radius": "12px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Bold Modern",
    },
    "tech_dark": {
        "id": "tech_dark",
        "mode": "dark",
        "colors": {
            "primary": "#38BDF8",
            "secondary": "#0B1220",
            "accent": "#22D3EE",
            "bg": "#0A0F1A",
            "text": "#E2E8F0",
            "muted": "#94A3B8",
            "line": "#1E293B",
        },
        "radius": "12px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Modern Dark",
    },
    "warm_hospitality": {
        "id": "warm_hospitality",
        "mode": "light",
        "colors": {
            "primary": "#7C2D12",
            "secondary": "#FFF7ED",
            "accent": "#EA580C",
            "bg": "#FFFBEB",
            "text": "#1C1917",
            "muted": "#78716C",
            "line": "#FED7AA",
        },
        "radius": "14px",
        "font": '"Libre Baskerville", Georgia, serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Warm Editorial",
    },
    "warm_cafe": {
        "id": "warm_cafe",
        "mode": "light",
        "colors": {
            "primary": "#78350F",
            "secondary": "#FEF3C7",
            "accent": "#D97706",
            "bg": "#FFFBEB",
            "text": "#292524",
            "muted": "#92400E",
            "line": "#FDE68A",
        },
        "radius": "18px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Warm Minimal",
    },
    "minimal_ink": {
        "id": "minimal_ink",
        "mode": "light",
        "colors": {
            "primary": "#18181B",
            "secondary": "#FAFAFA",
            "accent": "#3F3F46",
            "bg": "#FFFFFF",
            "text": "#18181B",
            "muted": "#71717A",
            "line": "#E4E4E7",
        },
        "radius": "8px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Minimal",
    },
    "agency_sharp": {
        "id": "agency_sharp",
        "mode": "light",
        "colors": {
            "primary": "#020617",
            "secondary": "#F1F5F9",
            "accent": "#0D9488",
            "bg": "#F8FAFC",
            "text": "#020617",
            "muted": "#475569",
            "line": "#CBD5E1",
        },
        "radius": "4px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Sharp Modern",
    },
    "calm_home": {
        "id": "calm_home",
        "mode": "light",
        "colors": {
            "primary": "#334155",
            "secondary": "#F8FAFC",
            "accent": "#0F766E",
            "bg": "#F8FAFC",
            "text": "#0F172A",
            "muted": "#64748B",
            "line": "#E2E8F0",
        },
        "radius": "12px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Calm Modern",
    },
    "clinical": {
        "id": "clinical",
        "mode": "light",
        "colors": {
            "primary": "#0E7490",
            "secondary": "#F0FDFA",
            "accent": "#0891B2",
            "bg": "#F8FAFC",
            "text": "#0F172A",
            "muted": "#64748B",
            "line": "#CFE8F3",
        },
        "radius": "10px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Clean Clinical",
    },
    "travel_bright": {
        "id": "travel_bright",
        "mode": "light",
        "colors": {
            "primary": "#0369A1",
            "secondary": "#E0F2FE",
            "accent": "#F59E0B",
            "bg": "#F0F9FF",
            "text": "#0C4A6E",
            "muted": "#0284C7",
            "line": "#BAE6FD",
        },
        "radius": "16px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Bright Editorial",
    },
    "bold_athletic": {
        "id": "bold_athletic",
        "mode": "dark",
        "colors": {
            "primary": "#EF4444",
            "secondary": "#111827",
            "accent": "#F97316",
            "bg": "#0B0F19",
            "text": "#F9FAFB",
            "muted": "#9CA3AF",
            "line": "#1F2937",
        },
        "radius": "10px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Bold Athletic",
    },
    "academic": {
        "id": "academic",
        "mode": "light",
        "colors": {
            "primary": "#1E3A8A",
            "secondary": "#EFF6FF",
            "accent": "#B91C1C",
            "bg": "#F8FAFC",
            "text": "#0F172A",
            "muted": "#475569",
            "line": "#DBEAFE",
        },
        "radius": "8px",
        "font": '"Libre Baskerville", Georgia, serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Clear Academic",
    },
    "formal_law": {
        "id": "formal_law",
        "mode": "light",
        "colors": {
            "primary": "#1C1917",
            "secondary": "#FAFAF9",
            "accent": "#92400E",
            "bg": "#FAFAF9",
            "text": "#1C1917",
            "muted": "#78716C",
            "line": "#E7E5E4",
        },
        "radius": "6px",
        "font": '"Libre Baskerville", Georgia, serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Formal Minimal",
    },
    "finance_clean": {
        "id": "finance_clean",
        "mode": "light",
        "colors": {
            "primary": "#0F766E",
            "secondary": "#F0FDFA",
            "accent": "#115E59",
            "bg": "#F8FAFC",
            "text": "#0F172A",
            "muted": "#64748B",
            "line": "#CCFBF1",
        },
        "radius": "10px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Clean Corporate",
    },
    "editorial_teal": {
        "id": "editorial_teal",
        "mode": "light",
        "colors": {
            "primary": "#0F766E",
            "secondary": "#F0FDFA",
            "accent": "#0D9488",
            "bg": "#FAFAF9",
            "text": "#1C1917",
            "muted": "#57534E",
            "line": "#D6D3D1",
        },
        "radius": "14px",
        "font": '"Libre Baskerville", Georgia, serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Readable Editorial",
    },
    "realty_clean": {
        "id": "realty_clean",
        "mode": "light",
        "colors": {
            "primary": "#1E40AF",
            "secondary": "#EFF6FF",
            "accent": "#2563EB",
            "bg": "#F8FAFC",
            "text": "#0F172A",
            "muted": "#64748B",
            "line": "#BFDBFE",
        },
        "radius": "12px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Clean Listing",
    },
    "hospitality_luxury": {
        "id": "hospitality_luxury",
        "mode": "light",
        "colors": {
            "primary": "#44403C",
            "secondary": "#FAFAF9",
            "accent": "#A16207",
            "bg": "#FAFAF9",
            "text": "#1C1917",
            "muted": "#78716C",
            "line": "#E7E5E4",
        },
        "radius": "16px",
        "font": '"Fraunces", Georgia, serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Calm Luxury",
    },
    "auto_steel": {
        "id": "auto_steel",
        "mode": "dark",
        "colors": {
            "primary": "#94A3B8",
            "secondary": "#0F172A",
            "accent": "#F97316",
            "bg": "#020617",
            "text": "#E2E8F0",
            "muted": "#94A3B8",
            "line": "#1E293B",
        },
        "radius": "8px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Bold Showroom",
    },
    "romantic_soft": {
        "id": "romantic_soft",
        "mode": "light",
        "colors": {
            "primary": "#9F1239",
            "secondary": "#FFF1F2",
            "accent": "#E11D48",
            "bg": "#FFF7F8",
            "text": "#4C0519",
            "muted": "#9F1239",
            "line": "#FECDD3",
        },
        "radius": "20px",
        "font": '"Fraunces", Georgia, serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Soft Romantic",
    },
    "beauty_soft": {
        "id": "beauty_soft",
        "mode": "light",
        "colors": {
            "primary": "#9D174D",
            "secondary": "#FDF2F8",
            "accent": "#DB2777",
            "bg": "#FFF7FB",
            "text": "#500724",
            "muted": "#9D174D",
            "line": "#FBCFE8",
        },
        "radius": "18px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Soft Beauty",
    },
    "modern_default": {
        "id": "modern_default",
        "mode": "light",
        "colors": {
            "primary": "#0F172A",
            "secondary": "#F8FAFC",
            "accent": "#0D7A5F",
            "bg": "#F8FAFC",
            "text": "#0F172A",
            "muted": "#64748B",
            "line": "#E2E8F0",
        },
        "radius": "12px",
        "font": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "font_body": '"IBM Plex Sans", "Segoe UI", sans-serif',
        "spacing": "8px",
        "style_label": "Modern",
    },
}


class ThemeEngine:
    """Resolve design tokens from a WebsitePlan (or preset id)."""

    def resolve_from_plan(self, website_plan: WebsitePlan | dict[str, Any]) -> dict[str, Any]:
        plan = website_plan.to_dict() if isinstance(website_plan, WebsitePlan) else website_plan
        theme = plan.get("theme") or {}
        preset_id = str(theme.get("token_preset") or "modern_default")
        tokens = self.resolve_preset(preset_id)

        # Optional override: analyzer primary_color when present and non-empty
        primary_override = str(theme.get("primary_color") or "").strip()
        if primary_override and primary_override.startswith("#"):
            tokens["colors"]["primary"] = primary_override
            tokens["colors"]["brand"] = primary_override
        else:
            tokens["colors"]["brand"] = tokens["colors"]["primary"]

        tokens["niche"] = plan.get("niche") or ""
        tokens["brand_name"] = plan.get("brand_name") or ""
        return tokens

    def resolve_preset(self, preset_id: str) -> dict[str, Any]:
        base = THEME_PRESETS.get(preset_id) or THEME_PRESETS["modern_default"]
        tokens = deepcopy(base)
        tokens["colors"] = dict(tokens["colors"])
        tokens["colors"]["brand"] = tokens["colors"]["primary"]
        return tokens

    def to_css_variables(self, tokens: dict[str, Any]) -> str:
        """Emit :root block body (without wrapping braces)."""
        colors = tokens.get("colors") or {}
        lines = [
            f"  --brand: {colors.get('brand') or colors.get('primary')};",
            f"  --color-primary: {colors.get('primary')};",
            f"  --color-secondary: {colors.get('secondary')};",
            f"  --color-accent: {colors.get('accent')};",
            f"  --bg: {colors.get('bg')};",
            f"  --text: {colors.get('text')};",
            f"  --muted: {colors.get('muted')};",
            f"  --line: {colors.get('line')};",
            f"  --radius: {tokens.get('radius', '12px')};",
            f"  --spacing: {tokens.get('spacing', '8px')};",
            f"  --font-display: {tokens.get('font', 'system-ui, sans-serif')};",
            f"  --font-body: {tokens.get('font_body') or tokens.get('font') or 'system-ui, sans-serif'};",
            f"  --style: {tokens.get('style_label') or tokens.get('id') or 'modern'};",
            f"  --theme-mode: {tokens.get('mode', 'light')};",
            '  font-family: var(--font-body);',
        ]
        return "\n".join(lines)

    def list_presets(self) -> list[str]:
        return sorted(THEME_PRESETS.keys())

"""Content Engine (Phase 4) — niche-specific copy + product catalogs."""

from __future__ import annotations

from typing import Any

from app.generation.pipeline import GeneratedFile, WebsitePlan
from app.generation.planner.niches import NICHES

BANNED_PHRASES = (
    "welcome to our website",
    "lorem ipsum",
    "coming soon",
    "your company name",
)

NICHE_COPY: dict[str, dict[str, Any]] = {
    "clothing": {
        "hero_headline": "Apparel that feels intentional",
        "tagline": "Elevated essentials for everyday confidence.",
        "cta_primary": "Shop the collection",
        "about": "We design wardrobe staples with clean lines, honest materials, and a quiet luxury finish.",
        "products": [
            {"name": "Structured Tee", "category": "T-Shirts", "price": "$48"},
            {"name": "City Hoodie", "category": "Hoodies", "price": "$118"},
            {"name": "Indigo Straight Jean", "category": "Jeans", "price": "$148"},
            {"name": "Wool-Blend Jacket", "category": "Jackets", "price": "$220"},
        ],
    },
    "footwear": {
        "hero_headline": "Steps built for momentum",
        "tagline": "Performance sneakers and everyday footwear with durable comfort.",
        "cta_primary": "Shop shoes",
        "about": "From training days to city nights, every pair is engineered for fit and feel.",
        "products": [
            {"name": "Aero Runner", "category": "Sneakers", "price": "$129"},
            {"name": "Trail Peak", "category": "Running Shoes", "price": "$149"},
            {"name": "Metro Loafer", "category": "Loafers", "price": "$159"},
        ],
    },
    "electronics": {
        "hero_headline": "Tech that keeps pace",
        "tagline": "Phones, audio, and accessories from trusted brands.",
        "cta_primary": "Browse devices",
        "about": "Honest pricing, verified stock, and support that answers when you need it.",
        "products": [
            {"name": "Flagship Phone", "category": "Smartphones", "price": "$799"},
            {"name": "Noise-Cancel Buds", "category": "Audio", "price": "$179"},
            {"name": "Fast Charge Hub", "category": "Accessories", "price": "$49"},
        ],
    },
    "coffee_shop": {
        "hero_headline": "Roast, pour, linger",
        "tagline": "Single-origin espresso and slow mornings in one cup.",
        "cta_primary": "See the menu",
        "about": "We roast in small batches and serve drinks the way the bean intended.",
        "products": [
            {"name": "House Espresso", "category": "Espresso", "price": "$4"},
            {"name": "Pour Over", "category": "Pour Over", "price": "$5"},
            {"name": "Butter Croissant", "category": "Pastries", "price": "$3.5"},
        ],
    },
    "restaurant": {
        "hero_headline": "A table worth lingering at",
        "tagline": "Seasonal plates, thoughtful wine, and warm hospitality.",
        "cta_primary": "View the menu",
        "about": "Our kitchen cooks with local produce and a respect for classic technique.",
        "products": [
            {"name": "Heirloom Tomato Salad", "category": "Starters", "price": "$14"},
            {"name": "Wood-Fired Catch", "category": "Mains", "price": "$32"},
            {"name": "Olive Oil Cake", "category": "Desserts", "price": "$12"},
        ],
    },
    "blog": {
        "hero_headline": "SEO playbooks that compound",
        "tagline": "Practical guides for publishers who care about organic growth.",
        "cta_primary": "Read articles",
        "about": "We publish field-tested strategy for teams shipping content every week.",
        "products": [],
    },
    "medical": {
        "hero_headline": "Care that listens first",
        "tagline": "Modern clinic care with clear guidance and calm spaces.",
        "cta_primary": "Book a visit",
        "about": "Our clinicians combine evidence-based practice with time to explain your options.",
        "products": [
            {"name": "General Consultation", "category": "Consultations", "price": ""},
            {"name": "Diagnostics Panel", "category": "Diagnostics", "price": ""},
        ],
    },
    "portfolio": {
        "hero_headline": "Work with clarity and craft",
        "tagline": "Selected projects, process notes, and collaborations.",
        "cta_primary": "View work",
        "about": "I help teams ship thoughtful digital products and visual systems.",
        "products": [],
    },
}


class ContentEngine:
    def build(self, website_plan: WebsitePlan | dict[str, Any]) -> dict[str, Any]:
        plan = website_plan.to_dict() if isinstance(website_plan, WebsitePlan) else website_plan
        niche_id = plan.get("niche") or "generic"
        niche = NICHES.get(niche_id) or NICHES["generic"]
        pack = dict(NICHE_COPY.get(niche_id) or {})
        brand = plan.get("brand_name") or niche.label
        tagline = pack.get("tagline") or plan.get("tagline") or f"{brand} — {niche.default_subcategory}"
        headline = pack.get("hero_headline") or f"{brand} for {niche.target_audience}"
        headline = self._scrub(headline, brand)
        tagline = self._scrub(tagline, brand)

        products = pack.get("products")
        if products is None:
            products = [{"name": p, "category": p, "price": ""} for p in (plan.get("product_types") or [])[:6]]

        # Enforce forbidden list
        forbidden = {f.lower() for f in (plan.get("forbidden_products") or [])}
        cleaned = []
        for item in products:
            blob = f"{item.get('name','')} {item.get('category','')}".lower()
            if any(f in blob for f in forbidden if f):
                continue
            cleaned.append(item)

        bag = {
            "brand_name": brand,
            "tagline": tagline,
            "hero_headline": headline,
            "cta_primary": pack.get("cta_primary") or "Get started",
            "about": pack.get("about") or f"{brand} serves {niche.target_audience.lower()} with a focus on {niche.brand_style.lower()}.",
            "products": cleaned,
            "product_types": plan.get("product_types") or list(niche.product_types),
            "forbidden_products": plan.get("forbidden_products") or list(niche.forbidden_products),
            "niche": niche_id,
        }
        return bag

    def emit_data_module(self, content: dict[str, Any]) -> GeneratedFile:
        import json

        payload = json.dumps(content, indent=2)
        return GeneratedFile(
            path="src/data/siteContent.ts",
            content=f"export const siteContent = {payload} as const\nexport type SiteContent = typeof siteContent\n",
        )

    def _scrub(self, text: str, brand: str) -> str:
        lower = text.lower()
        for phrase in BANNED_PHRASES:
            if phrase in lower:
                return f"{brand} — built with care for the details that matter"
        return text

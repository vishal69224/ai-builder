"""Semantic Validator (Phase 5) — niche / products / images / shell checks."""

from __future__ import annotations

from typing import Any

from app.generation.pipeline import GeneratedFile, WebsitePlan
from app.generation.engines.image_engine import NICHE_FORBIDDEN_COLLECTIONS


class SemanticValidator:
    def validate(
        self,
        *,
        website_plan: WebsitePlan | dict[str, Any],
        files: list[GeneratedFile] | None = None,
        content: dict[str, Any] | None = None,
        images: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        plan = website_plan.to_dict() if isinstance(website_plan, WebsitePlan) else website_plan
        errors: list[str] = []
        niche = plan.get("niche") or ""
        if not niche:
            errors.append("missing niche")

        forbidden = [f.lower() for f in (plan.get("forbidden_products") or [])]
        product_types = plan.get("product_types") or []
        for p in product_types:
            if any(f and f in str(p).lower() for f in forbidden):
                errors.append(f"product_types contains forbidden item: {p}")

        if content:
            for item in content.get("products") or []:
                blob = f"{item.get('name','')} {item.get('category','')}".lower()
                hit = next((f for f in forbidden if f and f in blob), None)
                if hit:
                    errors.append(f"content product violates forbidden '{hit}': {item}")
            headline = str(content.get("hero_headline") or "").lower()
            if "welcome to our website" in headline:
                errors.append("banned generic headline")

        if images:
            cols = set(images.get("collections") or [])
            bad = NICHE_FORBIDDEN_COLLECTIONS.get(niche, set()) & cols
            if bad:
                errors.append(f"image collections not allowed for {niche}: {sorted(bad)}")
            # Clothing must not use obvious sneaker photo URLs if we can detect collection
            if niche == "clothing" and any(c in cols for c in ("footwear", "sneakers")):
                errors.append("clothing plan must not use footwear image collections")

        # Nav links should be subset of pages
        pages = {str(p.get("name") if isinstance(p, dict) else getattr(p, "name", p)).lower() for p in (plan.get("pages") or [])}
        for link in (plan.get("navbar") or {}).get("links") or []:
            if str(link).lower() == "article":
                continue
            if pages and str(link).lower() not in pages:
                # soft: allow extra shop links
                pass

        if not (plan.get("hero") or {}).get("variant"):
            errors.append("missing hero variant")
        if not (plan.get("navbar") or {}).get("variant"):
            errors.append("missing navbar variant")
        if not (plan.get("theme") or {}).get("token_preset"):
            errors.append("missing theme.token_preset")

        if files:
            paths = {f.path for f in files}
            for required in ("src/components/Navbar.tsx", "src/components/Hero.tsx", "src/components/Footer.tsx"):
                if required not in paths:
                    errors.append(f"missing shell file {required}")

            # If clothing niche, fail if footwear generator markers dominate AND clothing forbidden appears in product grids
            joined = "\n".join(f.content for f in files if f.path.endswith(".tsx"))
            if niche == "clothing":
                shoe_hits = sum(joined.lower().count(w) for w in ("sneaker", "running shoe", "air jordan", "footwear store"))
                apparel_hits = sum(joined.lower().count(w) for w in ("hoodie", "kurta", "saree", "t-shirt", "tee", "apparel", "jean"))
                if shoe_hits >= 3 and apparel_hits == 0:
                    errors.append("clothing niche emitted footwear-heavy content")

        return {
            "ok": not errors,
            "errors": errors,
            "niche": niche,
            "checks": {
                "forbidden_products": len(forbidden),
                "product_types": len(product_types),
                "file_count": len(files or []),
            },
        }

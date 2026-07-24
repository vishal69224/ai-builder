"""Image Engine (Phase 6) — named collections, no generator-owned hardcodes."""

from __future__ import annotations

from typing import Any

from app.generation.pipeline import GeneratedFile, WebsitePlan

# Curated Unsplash collections — selected by Planner image_collections IDs
IMAGE_COLLECTIONS: dict[str, dict[str, list[str]]] = {
    "fashion": {
        "hero": [
            "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [
            "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=800&q=80",
        ],
    },
    "luxury": {
        "hero": [
            "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=800&q=80",
        ],
    },
    "streetwear": {
        "hero": [
            "https://images.unsplash.com/photo-1523398002811-999ca8dec234?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [
            "https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?auto=format&fit=crop&w=800&q=80",
        ],
    },
    "formal": {
        "hero": [
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "formal_wear": {
        "hero": [
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "footwear": {
        "hero": [
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [
            "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80",
        ],
    },
    "sneakers": {
        "hero": [
            "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [
            "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=800&q=80",
        ],
    },
    "electronics": {
        "hero": [
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [
            "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80",
        ],
    },
    "gadgets": {"hero": [], "products": []},
    "phones": {"hero": [], "products": []},
    "coffee": {
        "hero": [
            "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [
            "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=800&q=80",
        ],
    },
    "cafe": {"hero": [], "products": []},
    "interior": {
        "hero": [
            "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "restaurant": {
        "hero": [
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=800&q=80",
        ],
    },
    "dining": {"hero": [], "products": []},
    "pizza": {"hero": [], "products": []},
    "medical": {
        "hero": [
            "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "doctors": {"hero": [], "products": []},
    "hospital": {"hero": [], "products": []},
    "healthcare": {"hero": [], "products": []},
    "editorial": {
        "hero": [
            "https://images.unsplash.com/photo-1432888498266-38ffec6682cd?auto=format&fit=crop&w=1600&q=80",
        ],
        "covers": [
            "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80",
        ],
        "products": [],
    },
    "workspace": {"hero": [], "products": []},
    "modern": {
        "hero": [
            "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "photography": {
        "hero": [
            "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "creative": {"hero": [], "products": []},
    "office": {"hero": [], "products": []},
    "furniture": {
        "hero": [
            "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "bedroom": {"hero": [], "products": []},
    "bakery": {
        "hero": [
            "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "pastry": {"hero": [], "products": []},
    "travel": {
        "hero": [
            "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "landscape": {"hero": [], "products": []},
    "fitness": {
        "hero": [
            "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "campus": {"hero": [], "products": []},
    "learning": {"hero": [], "products": []},
    "finance": {"hero": [], "products": []},
    "books": {
        "hero": [
            "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "architecture": {"hero": [], "products": []},
    "hospitality": {
        "hero": [
            "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "auto": {
        "hero": [
            "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "showroom": {"hero": [], "products": []},
    "wedding": {
        "hero": [
            "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "floral": {"hero": [], "products": []},
    "beauty": {
        "hero": [
            "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
    "salon": {"hero": [], "products": []},
    "jewelry": {
        "hero": [
            "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=1600&q=80",
        ],
        "products": [],
    },
}


# Niche → collections that are forbidden (semantic validator / image engine)
NICHE_FORBIDDEN_COLLECTIONS: dict[str, set[str]] = {
    "clothing": {"footwear", "sneakers"},
    "footwear": set(),
    "restaurant": {"medical", "hospital", "footwear"},
    "medical": {"fashion", "footwear", "sneakers", "restaurant"},
}


class ImageEngine:
    def build(self, website_plan: WebsitePlan | dict[str, Any]) -> dict[str, Any]:
        plan = website_plan.to_dict() if isinstance(website_plan, WebsitePlan) else website_plan
        niche = plan.get("niche") or "generic"
        wanted = list(plan.get("image_collections") or ["modern"])
        forbidden = NICHE_FORBIDDEN_COLLECTIONS.get(niche, set())
        collection_ids = [c for c in wanted if c not in forbidden]
        if not collection_ids:
            collection_ids = ["modern"]

        hero: list[str] = []
        products: list[str] = []
        covers: list[str] = []
        for cid in collection_ids:
            block = IMAGE_COLLECTIONS.get(cid) or {}
            hero.extend(block.get("hero") or [])
            products.extend(block.get("products") or [])
            covers.extend(block.get("covers") or [])

        # Deduplicate preserving order
        def uniq(seq: list[str]) -> list[str]:
            seen: set[str] = set()
            out: list[str] = []
            for x in seq:
                if x and x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        return {
            "niche": niche,
            "collections": collection_ids,
            "hero": uniq(hero)[:1] or [
                "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1600&q=80"
            ],
            "products": uniq(products)[:8],
            "covers": uniq(covers)[:6],
        }

    def emit_data_module(self, images: dict[str, Any]) -> GeneratedFile:
        import json

        payload = json.dumps(images, indent=2)
        return GeneratedFile(
            path="src/data/images.ts",
            content=f"export const siteImages = {payload} as const\nexport type SiteImages = typeof siteImages\n",
        )

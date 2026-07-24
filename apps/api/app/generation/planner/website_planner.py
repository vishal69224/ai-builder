"""Website Planner (Phase 1) — PromptAnalysis → WebsitePlan JSON source of truth.

Does not emit React files. Legacy ComponentGenerator remains authoritative for codegen
until later phases opt in via feature flags.
"""

from __future__ import annotations

from app.generation.pipeline import (
    IntentSnapshot,
    PromptAnalysis,
    StructuredRequirements,
    WebsitePlan,
    WebsitePlanPage,
    WebsitePlanSection,
)
from app.generation.planner.niches import invent_brand_name, resolve_niche

PLAN_VERSION = "1.0.0"


class WebsitePlanner:
    def plan_from_analysis(
        self,
        analysis: PromptAnalysis,
        *,
        requirements: StructuredRequirements | None = None,
        project_name: str | None = None,
    ) -> WebsitePlan:
        niche = resolve_niche(analysis.website_type_id, analysis.raw_prompt)
        brand = invent_brand_name(analysis.brand_name or project_name or "", niche)
        tone = (requirements.tone if requirements else "") or niche.brand_style

        tagline = ""
        if isinstance(analysis.seo, dict):
            tagline = str(analysis.seo.get("tagline") or "").strip()
        if not tagline:
            tagline = f"{niche.label} crafted for {niche.target_audience.lower()}."

        pages = list(analysis.pages) if analysis.pages else list(niche.default_pages)
        if analysis.layout == "single_page" and not getattr(analysis, "pages_explicit", False):
            # Bookstore / shop niches should never collapse to a marketing single-pager
            if niche.id in {"bookstore", "footwear", "clothing", "electronics", "saas"}:
                pages = list(niche.default_pages)
            else:
                pages = ["Home"]
        elif (
            not getattr(analysis, "pages_explicit", False)
            and pages == ["Home"]
            and len(niche.default_pages) > 1
        ):
            pages = list(niche.default_pages)

        # Bookstore always needs browse / library / cart when commerce verbs are present
        if niche.id == "bookstore" and not getattr(analysis, "pages_explicit", False):
            for extra in niche.default_pages:
                if extra not in pages:
                    pages.append(extra)

        prompt_l = (analysis.raw_prompt or "").lower()
        # Clothing stores: only expand IA when the user did not name exact pages
        if niche.id == "clothing" and not getattr(analysis, "pages_explicit", False):
            for extra in ("Shop", "Lookbook", "About", "Contact"):
                if extra not in pages:
                    pages.append(extra)
            if any(k in prompt_l for k in ("sign in", "sign up", "login", "register", "signup", "signin")):
                for extra in ("Login", "Register"):
                    if extra not in pages:
                        pages.append(extra)

        sections = list(analysis.sections) if analysis.sections else list(niche.default_sections)
        if not sections:
            sections = list(niche.default_sections)

        intent = IntentSnapshot(
            website_type=niche.label,
            website_type_id=analysis.website_type_id,
            industry=niche.industry,
            subcategory=niche.default_subcategory,
            business_type=niche.label,
            target_audience=niche.target_audience,
            brand_style=niche.brand_style,
            design_style=niche.design_style,
            color_theme=str((analysis.theme or {}).get("primary_color") or analysis.color or ""),
            typography_style=niche.typography_style,
            pages=pages,
            sections=sections,
            components=list(analysis.components or []),
            animations=list(analysis.animations or []),
            tone=tone,
            product_types=list(niche.product_types),
            forbidden_products=list(niche.forbidden_products),
            image_style=niche.image_style,
            seo_keywords=list((analysis.seo or {}).get("keywords") or analysis.tags or []),
            business_name=brand,
            confidence=float(analysis.confidence or 0),
            raw_prompt=analysis.raw_prompt,
            understanding_source="rules_classifier",
        )

        return WebsitePlan(
            version=PLAN_VERSION,
            niche=niche.id,
            brand_name=brand,
            tagline=tagline,
            intent=intent.to_dict(),
            theme={
                "token_preset": niche.token_preset,
                "style": niche.design_style,
                "primary_color": str((analysis.theme or {}).get("primary_color") or ""),
                "color_label": analysis.color,
            },
            typography={"style": niche.typography_style},
            navbar={"variant": niche.navbar_variant, "links": pages},
            footer={"variant": niche.footer_variant},
            hero={"variant": niche.hero_variant},
            pages=[_build_page(name, sections, niche.hero_variant) for name in pages],
            product_types=list(niche.product_types),
            forbidden_products=list(niche.forbidden_products),
            image_collections=list(niche.image_collections),
            animations=list(analysis.animations or ["fade-in"]),
            seo={
                "meta_description": (analysis.seo or {}).get("meta_description")
                or f"{brand} — {niche.label} for {niche.target_audience}.",
                "keywords": intent.seo_keywords,
                "tagline": tagline,
            },
            components=sorted(
                {
                    niche.navbar_variant,
                    niche.hero_variant,
                    niche.footer_variant,
                    *list(analysis.components or []),
                }
            ),
        )


def _build_page(page_name: str, sections: list[str], hero_variant: str) -> WebsitePlanPage:
    path = "/" if page_name.lower() == "home" else "/" + page_name.lower().replace(" ", "-")
    if page_name.lower() != "home":
        return WebsitePlanPage(
            name=page_name,
            path=path,
            sections=[
                WebsitePlanSection(
                    id=page_name.lower().replace(" ", "_"),
                    component=page_name.replace(" ", "") + "View",
                    variant="PageStandard",
                )
            ],
        )

    has_hero = any(s.lower() == "hero" for s in sections)
    page_sections: list[WebsitePlanSection] = []
    if not has_hero:
        page_sections.append(WebsitePlanSection(id="hero", component="Hero", variant=hero_variant))

    for section in sections:
        key = section.lower()
        if key == "hero":
            page_sections.append(WebsitePlanSection(id="hero", component="Hero", variant=hero_variant))
            continue
        page_sections.append(
            WebsitePlanSection(
                id=key.replace(" ", "_"),
                component=section.replace(" ", ""),
                variant=_default_variant(section),
            )
        )
    return WebsitePlanPage(name=page_name, path=path, sections=page_sections)


def _default_variant(section: str) -> str:
    key = section.lower()
    mapping = {
        "collections": "ProductGrid",
        "trending": "ProductGrid",
        "featured": "ProductGrid",
        "newsletter": "Newsletter",
        "categories": "CategoryStrip",
        "reviews": "Testimonials",
        "testimonials": "Testimonials",
        "about": "AboutSection",
        "contact": "ContactForm",
        "cta": "CTABanner",
        "gallery": "GalleryGrid",
        "services": "ServiceGrid",
        "pricing": "PricingCards",
    }
    return mapping.get(key, section.replace(" ", "") + "Block")

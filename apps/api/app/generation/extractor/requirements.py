from app.generation.pipeline import PromptAnalysis, StructuredRequirements


class RequirementExtractor:
    def extract(self, analysis: PromptAnalysis) -> StructuredRequirements:
        features = [f"{page} page" for page in analysis.pages]
        features.extend(
            [
                "Responsive layout",
                f"Theme: {analysis.theme.get('style', 'modern')}",
                f"Icon set: {analysis.icons.get('library', 'lucide-react')}",
            ]
        )
        if analysis.seo.get("enabled"):
            features.append("SEO meta + semantic HTML")
        if analysis.animations:
            features.append("Motion / animation accents")
        if getattr(analysis, "layout", "") == "single_page":
            features.append("Single-page scroll layout")

        content_sections = list(getattr(analysis, "sections", []) or [])
        if not content_sections:
            content_sections = [c for c in analysis.components if c not in {"Navbar", "Footer", "Button", "Card"}]

        tone = str(analysis.theme.get("mood", "modern"))
        cta = "Get started"
        prompt = analysis.raw_prompt.lower()
        type_id = (analysis.website_type_id or "").lower()
        if any(k in prompt for k in ("cloth", "fashion", "apparel", "boutique", "clothing")) or "fashion" in type_id:
            cta = "Shop now"
        elif any(k in prompt for k in ("shop", "buy", "order", "menu")):
            cta = "Order now"
        elif any(k in prompt for k in ("book", "reserve", "appointment")):
            cta = "Book now"
        elif any(k in prompt for k in ("donate", "nonprofit", "charity")):
            cta = "Donate"
        elif any(k in prompt for k in ("waitlist", "signup", "sign up")):
            cta = "Join waitlist"
        elif any(k in prompt for k in ("personal", "portfolio", "hire")):
            cta = "Let's work together"

        return StructuredRequirements(
            analysis=analysis,
            features=features,
            content_sections=content_sections,
            cta_primary=cta,
            tone=tone,
        )

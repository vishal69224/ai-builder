"""Prompt Analyzer — extracts structured website intent from natural language."""

from __future__ import annotations

import re
from collections import Counter

from app.generation.analyzer.website_types import WEBSITE_TYPES, WebsiteType, catalog_stats
from app.generation.pipeline import PromptAnalysis

ICON_LIBS = ("lucide-react", "heroicons", "phosphor", "react-icons")
DEFAULT_LIBRARIES = ("react", "react-router-dom", "tailwindcss", "vite", "typescript")


class PromptAnalyzer:
    """Rule + catalog analyzer supporting hundreds of website types."""

    def __init__(self, catalog: list[WebsiteType] | None = None) -> None:
        self.catalog = catalog or WEBSITE_TYPES

    def analyze(self, prompt: str) -> PromptAnalysis:
        text = prompt.strip()
        lowered = text.lower()
        matched, confidence = self._match_type(lowered)

        sections = self._extract_sections(text, lowered)
        pages = self._extract_pages(lowered, matched, sections, text)
        components = self._extract_components(lowered, matched, sections)
        theme = self._extract_theme(lowered, matched)
        animations = self._extract_animations(lowered, matched)
        libraries = self._extract_libraries(lowered)
        icons = self._extract_icons(lowered)
        responsive = self._extract_responsive(lowered)
        seo = self._extract_seo(lowered, matched, text)
        tags = self._extract_tags(lowered, matched)
        layout = self._choose_layout(matched, sections, pages)
        if layout == "single_page":
            pages = ["Home"]
        brand_name = self._extract_brand_name(text, matched)
        framework = "React"
        styling = "Tailwind"
        color = self._extract_color_label(lowered, theme)

        return PromptAnalysis(
            website_type=matched.label,
            website_type_id=matched.id,
            confidence=round(confidence, 3),
            pages=pages,
            components=components,
            theme=theme,
            animations=animations,
            libraries=libraries,
            icons=icons,
            responsive=responsive,
            seo=seo,
            framework=framework,
            styling=styling,
            color=color,
            tags=tags,
            raw_prompt=text,
            sections=sections,
            layout=layout,
            brand_name=brand_name,
        )

    def _extract_color_label(self, lowered: str, theme: dict) -> str:
        style = theme.get("style", "modern")
        if "dark" in lowered or style in {"dark", "luxury", "neon"}:
            return "Dark"
        if "light" in lowered or style in {"minimal", "clean"}:
            return "Light"
        if style in {"warm", "earth"}:
            return "Warm"
        return "Light"

    def _match_type(self, lowered: str) -> tuple[WebsiteType, float]:
        # 1) Local trained ML classifier (no API key)
        try:
            from app.ai_model.classifier import LocalWebsiteClassifier

            clf = LocalWebsiteClassifier()
            if clf.is_ready:
                ml_result = clf.predict(lowered)
                if ml_result and ml_result[1] >= 0.15:
                    return ml_result
        except Exception:
            pass

        # 2) Rule + keyword catalog fallback
        scores: list[tuple[float, WebsiteType]] = []
        for wt in self.catalog:
            score = 0.0
            for kw in wt.keywords:
                if kw in lowered:
                    # Longer phrases weigh more
                    score += 1.0 + min(len(kw.split()), 4) * 0.35
            if score > 0:
                # Prefer curated (no __style suffix depth) slightly
                depth_penalty = wt.id.count("__") * 0.05
                scores.append((score - depth_penalty, wt))

        if not scores:
            fallback = next(t for t in self.catalog if t.id == "landing_page")
            return fallback, 0.35

        scores.sort(key=lambda x: x[0], reverse=True)
        best_score, best = scores[0]
        # Normalize confidence into 0.4–0.98
        confidence = min(0.98, 0.4 + best_score / 8.0)
        return best, confidence

    def _extract_brand_name(self, original: str, matched: WebsiteType) -> str:
        """Pull a shop/brand name from casual prompts like 'name was Shree Hari…'."""
        # Prefer quoted brand first: called "MobileHub"
        q = re.search(
            r"(?:called|named|brand|store|shop)\s+[\"']([A-Za-z][^\"']{1,50})[\"']",
            original,
            flags=re.I,
        )
        if q:
            return q.group(1).strip()
        q2 = re.search(r"[\"']([A-Za-z][A-Za-z0-9 &''.-]{1,40})[\"']", original)
        if q2:
            candidate = q2.group(1).strip()
            if candidate.lower() not in {"home", "about", "contact", "shop"}:
                return candidate

        # ALLCAPS / Camel brand tokens: STEPX, Nike, …
        for token in re.findall(r"\b([A-Z]{2,}[A-Za-z0-9]*)\b", original):
            if token.lower() not in {
                "faq",
                "seo",
                "ui",
                "ux",
                "api",
                "emi",
                "cod",
                "home",
                "shop",
                "page",
                "pages",
                "theme",
                "create",
                "build",
            }:
                return token

        # "for STEPX sneakers" / "for Acme shoes"
        m_for = re.search(
            r"\bfor\s+([A-Z][A-Za-z0-9&''.-]{1,40})(?:\s+(?:sneakers?|shoes?|footwear|store|shop))?",
            original,
        )
        if m_for:
            return m_for.group(1).strip()

        patterns = [
            r"(?:shop\s+name|store\s+name|brand\s+name|name(?:d)?|called)\s+(?:is|was|of)?\s*[:\-]?\s*[\"']?([A-Za-z][A-Za-z0-9 &''.-]{2,60})",
            r"(?:my|our)\s+(?:shop|store|brand|boutique)\s+(?:is|was|called|named)?\s*[\"']?([A-Za-z][A-Za-z0-9 &''.-]{2,60})",
            r"(?:it'?s\s+called|known\s+as)\s+[\"']?([A-Za-z][A-Za-z0-9 &''.-]{2,60})",
        ]
        for pat in patterns:
            m = re.search(pat, original, flags=re.I)
            if not m:
                continue
            name = re.sub(r"\s+", " ", m.group(1)).strip(" .,!?'\"")
            name = re.sub(
                r"\b(website|site|online|please|thanks|for\s+me)\b.*$",
                "",
                name,
                flags=re.I,
            ).strip(" .,")
            name = re.sub(r"^(it|the|a|an)\s+", "", name, flags=re.I).strip()
            if len(name) >= 3:
                return name.title() if not any(c.isupper() for c in name[1:]) else name

        # Prefer a publishable brand over catalog type labels for blogs
        if matched.id.startswith("blog") or "magazine" in matched.id:
            return "Insight Blog"
        return matched.label

    def _extract_pages_block(self, original: str) -> list[str]:
        pages: list[str] = []
        m = re.search(r"pages?\s*:", original, flags=re.I)
        if not m:
            return pages
        skip = {
            "modern",
            "minimal",
            "responsive",
            "seo",
            "dark",
            "theme",
            "white",
            "black",
            "blue",
        }
        rest = original[m.end() :]
        for line in rest.splitlines():
            raw = line.strip()
            if not raw:
                if pages:
                    break
                continue
            if set(raw) <= {"=", "-", "_", "*"} or raw.startswith("==="):
                break
            if re.match(r"^[A-Z][A-Z0-9 ]{8,}$", raw) and " " in raw:
                # e.g. HOME PAGE / POPULAR BRANDS
                break
            if "section" in raw.lower() and not raw.lower().startswith("-"):
                break
            name = re.sub(r"^[-*•\d.)\s]+", "", raw).strip()
            if not name or len(name) > 40 or name.lower() in skip:
                continue
            if ":" in name and len(name.split()) <= 2:
                break
            titled = "FAQ" if name.lower() == "faq" else name.title()
            if titled in {"About Us", "Aboutus"}:
                titled = "About"
            if titled not in pages:
                pages.append(titled)
            if len(pages) >= 12:
                break
        return pages

    def _choose_layout(self, matched: WebsiteType, sections: list[str], pages: list[str]) -> str:
        # Stores / shops are always multi-page sites
        if matched.category == "retail" or any(
            k in matched.id for k in ("store", "shop", "ecommerce", "fashion", "mobile")
        ):
            return "multi_page"
        if matched.category == "portfolio" or matched.id in {"personal_brand", "landing_page"}:
            return "single_page"
        if len(pages) <= 1 and len(sections) >= 5:
            return "single_page"
        if len(pages) <= 1:
            return "single_page"
        return "multi_page"

    def _extract_pages(
        self, lowered: str, matched: WebsiteType, sections: list[str], original: str = ""
    ) -> list[str]:
        explicit = self._extract_pages_block(original) if original else []
        if explicit:
            # Ensure Home first
            if "Home" not in explicit:
                explicit.insert(0, "Home")
            elif explicit[0] != "Home":
                explicit = ["Home"] + [p for p in explicit if p != "Home"]
            return explicit

        # Prefer explicit content sections as IA when listed
        page_like = [
            s
            for s in sections
            if s.lower() not in {"hero", "footer", "navbar", "nav"}
        ]
        if len(page_like) >= 3 and (
            matched.category == "portfolio" or matched.id == "personal_brand" or "personal brand" in lowered
        ):
            return ["Home"]

        pages = list(matched.default_pages)
        extras = {
            "blog": "Blog",
            "pricing": "Pricing",
            "faq": "FAQ",
            "gallery": "Gallery",
            "shop": "Shop",
            "menu": "Menu",
            "careers": "Careers",
            "team": "Team",
            "testimonials": "Testimonials",
            "docs": "Docs",
            "login": "Login",
            "signup": "Sign Up",
            "dashboard": "Dashboard",
            "booking": "Booking",
            "reservation": "Reservations",
            "experience": "Experience",
            "skills": "Skills",
            "projects": "Projects",
            "smartphone": "Smartphones",
            "accessories": "Accessories",
            "offers": "Offers",
        }
        for key, page in extras.items():
            if key in lowered and page not in pages:
                # Avoid Blog+Articles duplicate for SEO/blog sites
                if page == "Blog" and (
                    "Articles" in pages
                    or matched.id.startswith("blog")
                    or "magazine" in matched.id
                ):
                    continue
                pages.append(page)

        for s in page_like:
            if s not in pages and s.lower() != "home":
                pages.append(s)

        listed = re.findall(
            r"(?:pages?(?: include| are|:)?|include(?:s)?(?: the)? pages?)\s+([a-z0-9 ,&/-]+)",
            lowered,
        )
        for chunk in listed:
            for part in re.split(r"[,&/]| and ", chunk):
                name = part.strip().title()
                if name and name not in pages and len(name) < 40:
                    pages.append(name)
        return pages

    def _extract_sections(self, original: str, lowered: str) -> list[str]:
        """Parse explicit Sections: lists and common section keywords."""
        sections: list[str] = []
        block = re.search(
            r"sections?\s*:?\s*\n((?:\s*[-*]?\s*[A-Za-z][A-Za-z0-9 /&-]{1,40}\s*\n?)+)",
            original,
            flags=re.I,
        )
        if block:
            for line in block.group(1).splitlines():
                name = re.sub(r"^[-*•\d.)\s]+", "", line).strip()
                if not name or len(name) > 40:
                    continue
                if name.lower() in {
                    "modern",
                    "minimal",
                    "dark theme",
                    "scroll animations",
                    "responsive",
                    "seo optimized",
                    "seo",
                    "dark",
                }:
                    continue
                titled = name.title() if name.lower() != "faq" else "FAQ"
                if titled not in sections:
                    sections.append(titled)

        keyword_map = {
            "hero": "Hero",
            "about": "About",
            "experience": "Experience",
            "skills": "Skills",
            "projects": "Projects",
            "portfolio": "Projects",
            "work": "Projects",
            "blog": "Blog",
            "writing": "Blog",
            "testimonials": "Testimonials",
            "reviews": "Testimonials",
            "contact": "Contact",
            "footer": "Footer",
            "services": "Services",
            "pricing": "Pricing",
            "faq": "FAQ",
            "team": "Team",
            "gallery": "Gallery",
            "newsletter": "Newsletter",
            "deals": "Deals",
            "brands": "Brands",
            "accessories": "Accessories",
        }
        for key, label in keyword_map.items():
            if key in lowered and label not in sections:
                if sections or "section" in lowered or key in {"about", "contact", "hero"}:
                    sections.append(label)

        seen: set[str] = set()
        out: list[str] = []
        for s in sections:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    def _extract_components(
        self, lowered: str, matched: WebsiteType, sections: list[str]
    ) -> list[str]:
        components = list(matched.default_components)
        section_to_comp = {
            "Hero": "Hero",
            "About": "AboutSection",
            "Experience": "ExperienceSection",
            "Skills": "SkillsSection",
            "Projects": "ProjectGallery",
            "Blog": "BlogSection",
            "Testimonials": "Testimonials",
            "Contact": "ContactForm",
            "Footer": "Footer",
            "Services": "ServiceCards",
            "Pricing": "PricingTable",
            "FAQ": "FAQ",
            "Team": "TeamGrid",
            "Gallery": "Gallery",
        }
        for s in sections:
            comp = section_to_comp.get(s)
            if comp and comp not in components:
                components.append(comp)
        extras = {
            "testimonial": "Testimonials",
            "newsletter": "Newsletter",
            "map": "MapEmbed",
            "chat": "ChatWidget",
            "pricing table": "PricingTable",
            "faq": "FAQ",
            "carousel": "Carousel",
            "slider": "HeroSlider",
            "video": "VideoEmbed",
            "stats": "StatsStrip",
            "logo cloud": "LogoCloud",
            "dark mode": "ThemeToggle",
            "experience": "ExperienceSection",
            "skills": "SkillsSection",
            "projects": "ProjectGallery",
            "about": "AboutSection",
        }
        for key, comp in extras.items():
            if key in lowered and comp not in components:
                components.append(comp)
        # Ensure shell components
        for required in ("Navbar", "Hero", "Footer"):
            if required not in components:
                components.insert(0, required)
        return components

    def _extract_theme(self, lowered: str, matched: WebsiteType) -> dict:
        style, primary, mood = matched.default_theme
        palette_hints = {
            "warm": ("warm", "#8B5E3C"),
            "dark": ("dark", "#0F172A"),
            "minimal": ("minimal", "#111827"),
            "luxury": ("luxury", "#C6A75E"),
            "pastel": ("pastel", "#F9A8D4"),
            "neon": ("neon", "#22D3EE"),
            "earth": ("earth", "#78716C"),
            "ocean": ("ocean", "#0284C7"),
            "forest": ("forest", "#166534"),
            "coffee": ("warm", "#6F4E37"),
            "modern": ("modern", "#2563EB"),
            "blue": ("modern", "#2563EB"),
            "premium": ("premium", "#1D4ED8"),
        }
        for key, (style_name, color) in palette_hints.items():
            if key in lowered:
                style = style_name
                primary = color
                # Don't break on first — prefer more specific later keys
        # Explicit white/black/blue electronics palette
        if "blue" in lowered and ("white" in lowered or "black" in lowered):
            style = "premium"
            primary = "#2563EB"
            mood = "professional"

        if "serif" in lowered:
            typography = "serif-display"
        elif "mono" in lowered or "technical" in lowered:
            typography = "mono-accent"
        else:
            typography = "sans"

        return {
            "style": style,
            "mood": mood,
            "primary_color": primary,
            "typography": typography,
            "density": "comfortable" if "spacious" in lowered or "airy" in lowered else "balanced",
        }

    def _extract_animations(self, lowered: str, matched: WebsiteType) -> list[str]:
        animations = list(matched.default_animations)
        if "no animation" in lowered or "without animation" in lowered:
            return []
        extras = {
            "parallax": "parallax",
            "marquee": "marquee",
            "hover": "hover-lift",
            "micro-interaction": "micro-interactions",
            "scroll": "scroll-reveal",
            "lottie": "lottie",
        }
        for key, anim in extras.items():
            if key in lowered and anim not in animations:
                animations.append(anim)
        return animations

    def _extract_libraries(self, lowered: str) -> list[str]:
        libs = list(DEFAULT_LIBRARIES)
        optional = {
            "framer motion": "framer-motion",
            "motion": "framer-motion",
            "three": "three",
            "gsap": "gsap",
            "swiper": "swiper",
            "chart": "recharts",
            "form": "react-hook-form",
            "zod": "zod",
            "i18n": "i18next",
            "cms": "@tanstack/react-query",
        }
        for key, pkg in optional.items():
            if key in lowered and pkg not in libs:
                libs.append(pkg)
        if "animation" in lowered and "framer-motion" not in libs:
            libs.append("framer-motion")
        return libs

    def _extract_icons(self, lowered: str) -> dict:
        library = "lucide-react"
        for lib in ICON_LIBS:
            if lib.replace("-", " ") in lowered or lib in lowered:
                library = lib
                break
        if "font awesome" in lowered or "fontawesome" in lowered:
            library = "react-icons"
        return {
            "library": library,
            "style": "outline" if "outline" in lowered else "default",
            "usage": ["nav", "features", "social"],
        }

    def _extract_responsive(self, lowered: str) -> dict:
        mobile_first = "desktop-first" not in lowered
        breakpoints = ["sm", "md", "lg", "xl"]
        notes = []
        if "mobile" in lowered or "responsive" in lowered:
            notes.append("Explicit responsive requirement detected")
        if "tablet" in lowered:
            notes.append("Tablet layouts emphasized")
        return {
            "required": True,
            "mobile_first": mobile_first,
            "breakpoints": breakpoints,
            "notes": notes or ["Standard responsive breakpoints"],
        }

    def _extract_seo(self, lowered: str, matched: WebsiteType, original: str) -> dict:
        title_seed = matched.label
        wants_blog = "blog" in lowered
        return {
            "enabled": "no seo" not in lowered,
            "title_template": f"{title_seed} | {{page}}",
            "meta_description": self._meta_description(original, matched),
            "og_image": True,
            "sitemap": True,
            "semantic_html": True,
            "json_ld": matched.category in {"food_beverage", "retail", "healthcare", "events", "travel"},
            "blog_seo": wants_blog,
        }

    def _meta_description(self, original: str, matched: WebsiteType) -> str:
        cleaned = re.sub(r"\s+", " ", original).strip()
        if len(cleaned) > 140:
            cleaned = cleaned[:137] + "..."
        return cleaned or f"A modern {matched.label.lower()} website."

    def _extract_tags(self, lowered: str, matched: WebsiteType) -> list[str]:
        words = re.findall(r"[a-z]{4,}", lowered)
        common = {w for w, _ in Counter(words).most_common(12)}
        tags = [matched.category, matched.id.split("__")[0]]
        for w in ("modern", "minimal", "luxury", "responsive", "seo", "dark", "animated"):
            if w in common or w in lowered:
                tags.append(w)
        # unique preserve order
        seen: set[str] = set()
        out: list[str] = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out


def analyze_prompt(prompt: str) -> dict:
    analysis = PromptAnalyzer().analyze(prompt)
    payload = analysis.to_dict()
    payload["catalog"] = catalog_stats()
    return payload

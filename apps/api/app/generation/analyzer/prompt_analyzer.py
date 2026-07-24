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
        spoken = self._extract_spoken_pages(lowered)
        pages_block = self._extract_pages_block(text)
        pages_explicit = bool(spoken or pages_block)
        if spoken:
            pages = spoken
        elif pages_block:
            pages = pages_block
            if "Home" not in pages:
                pages.insert(0, "Home")
            elif pages[0] != "Home":
                pages = ["Home"] + [p for p in pages if p != "Home"]
        else:
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
        if layout == "single_page" and not pages_explicit:
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
            pages_explicit=pages_explicit,
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
        from app.generation.understanding.intent_guards import (
            explicitly_forbids_footwear,
            has_strong_clothing_intent,
            sanitize_prompt_for_matching,
        )

        # Match against sanitized text so "Avoid: Shoes" does not become shoe_store
        match_text = sanitize_prompt_for_matching(lowered) or lowered

        # 1) Local trained ML classifier (no API key)
        try:
            from app.ai_model.classifier import LocalWebsiteClassifier

            clf = LocalWebsiteClassifier()
            if clf.is_ready:
                ml_result = clf.predict(match_text)
                if ml_result and ml_result[1] >= 0.15:
                    matched, conf = ml_result
                    matched, conf = self._override_footwear_misroute(matched, conf, lowered)
                    matched, conf = self._override_bookstore_misroute(matched, conf, lowered)
                    return matched, conf
        except Exception:
            pass

        # 2) Rule + keyword catalog fallback
        scores: list[tuple[float, WebsiteType]] = []
        for wt in self.catalog:
            score = 0.0
            for kw in wt.keywords:
                if kw in match_text:
                    # Longer phrases weigh more
                    score += 1.0 + min(len(kw.split()), 4) * 0.35
            if score > 0:
                # Prefer curated (no __style suffix depth) slightly
                depth_penalty = wt.id.count("__") * 0.05
                scores.append((score - depth_penalty, wt))

        # Boost fashion when clothing intent is explicit
        if has_strong_clothing_intent(lowered) or explicitly_forbids_footwear(lowered):
            for i, (score, wt) in enumerate(scores):
                if "fashion" in wt.id or "clothing" in wt.id or "apparel" in wt.id:
                    scores[i] = (score + 5.0, wt)
                if "shoe" in wt.id or "sneaker" in wt.id or "footwear" in wt.id:
                    scores[i] = (score - 8.0, wt)

        # Boost bookstore when book-store commerce intent is explicit
        if any(
            p in match_text
            for p in ("book store", "bookstore", "book shop", "buy books", "read books", "download")
        ) and ("book" in match_text):
            for i, (score, wt) in enumerate(scores):
                if "book" in wt.id:
                    scores[i] = (score + 6.0, wt)
                if wt.id.startswith("landing"):
                    scores[i] = (score - 5.0, wt)

        if not scores:
            fallback = next(t for t in self.catalog if t.id == "landing_page")
            return fallback, 0.35

        scores.sort(key=lambda x: x[0], reverse=True)
        best_score, best = scores[0]
        # Normalize confidence into 0.4–0.98
        confidence = min(0.98, 0.4 + best_score / 8.0)
        best, confidence = self._override_footwear_misroute(best, confidence, lowered)
        best, confidence = self._override_bookstore_misroute(best, confidence, lowered)
        return best, confidence

    def _override_bookstore_misroute(
        self, matched: WebsiteType, confidence: float, original_lowered: str
    ) -> tuple[WebsiteType, float]:
        text = (original_lowered or "").lower()
        bookstoreish = any(
            p in text
            for p in (
                "book store",
                "bookstore",
                "book shop",
                "bookshop",
                "online book",
                "buy books",
                "read books",
                "download the books",
                "books pdf",
            )
        ) or (
            "book" in text
            and any(w in text for w in ("buy", "read", "search", "download", "pdf"))
            and any(w in text for w in ("store", "shop", "online"))
        )
        if not bookstoreish:
            return matched, confidence
        tid = (matched.id or "").lower()
        if "book" in tid:
            return matched, max(confidence, 0.92)
        book = next((t for t in self.catalog if t.id == "bookstore" or t.id.startswith("bookstore")), None)
        if book is None:
            book = next((t for t in self.catalog if "book" in t.id and "bookkeep" not in t.id), matched)
        return book, max(confidence, 0.92)

    def _override_footwear_misroute(
        self, matched: WebsiteType, confidence: float, original_lowered: str
    ) -> tuple[WebsiteType, float]:
        from app.generation.understanding.intent_guards import (
            explicitly_forbids_footwear,
            has_strong_clothing_intent,
            positive_footwear_intent,
        )

        tid = (matched.id or "").lower()
        is_shoe_type = any(k in tid for k in ("shoe", "sneaker", "footwear"))
        if is_shoe_type and (
            explicitly_forbids_footwear(original_lowered)
            or (has_strong_clothing_intent(original_lowered) and not positive_footwear_intent(original_lowered))
        ):
            fashion = next((t for t in self.catalog if t.id == "fashion_brand"), None)
            if fashion is None:
                fashion = next((t for t in self.catalog if "fashion" in t.id), matched)
            return fashion, max(confidence, 0.9)
        return matched, confidence

    def _extract_brand_name(self, original: str, matched: WebsiteType) -> str:
        """Pull a shop/brand name from casual prompts like 'name was Shree Hari…'."""
        # Prefer: "shop name is Vishu Creation" / "my cloth shop name is …"
        named = re.search(
            r"(?:(?:cloth|clothing|fashion)\s+)?(?:shop|store|brand|boutique)\s+name\s+is\s+"
            r"([A-Za-z][A-Za-z0-9&''.-]*(?:\s+[A-Za-z][A-Za-z0-9&''.-]*){0,3})",
            original,
            flags=re.I,
        )
        if named:
            return self._clean_brand_candidate(named.group(1))

        # Prefer quoted brand first: called "MobileHub"
        q = re.search(
            r"(?:called|named|brand|store|shop)\s+[\"']([A-Za-z][^\"']{1,50})[\"']",
            original,
            flags=re.I,
        )
        if q:
            return self._clean_brand_candidate(q.group(1))
        q2 = re.search(r"[\"']([A-Za-z][A-Za-z0-9 &''.-]{1,40})[\"']", original)
        if q2:
            candidate = self._clean_brand_candidate(q2.group(1))
            if candidate.lower() not in {"home", "about", "contact", "shop"}:
                return candidate

        # ALLCAPS / Camel brand tokens: STEPX, Nike, … (skip instruction words)
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
                "dark",
                "new",
            }:
                return token

        # "for STEPX sneakers" / "for Acme shoes"
        m_for = re.search(
            r"\bfor\s+([A-Z][A-Za-z0-9&''.-]{1,40})(?:\s+(?:sneakers?|shoes?|footwear|store|shop))?",
            original,
        )
        if m_for:
            return self._clean_brand_candidate(m_for.group(1))

        patterns = [
            r"(?:shop\s+name|store\s+name|brand\s+name|name(?:d)?|called)\s+(?:is|was|of)?\s*[:\-]?\s*[\"']?([A-Za-z][A-Za-z0-9 &''.-]{2,60})",
            r"(?:my|our)\s+(?:shop|store|brand|boutique)\s+(?:is|was|called|named)?\s*[\"']?([A-Za-z][A-Za-z0-9 &''.-]{2,60})",
            r"(?:it'?s\s+called|known\s+as)\s+[\"']?([A-Za-z][A-Za-z0-9 &''.-]{2,60})",
        ]
        for pat in patterns:
            m = re.search(pat, original, flags=re.I)
            if not m:
                continue
            name = self._clean_brand_candidate(m.group(1))
            if len(name) >= 3:
                return name.title() if not any(c.isupper() for c in name[1:]) else name

        # Prefer a publishable brand over catalog type labels for blogs
        if matched.id.startswith("blog") or "magazine" in matched.id:
            return "Insight Blog"
        # Never use catalog type labels as the public brand — niche invent fills in
        return ""

    def _normalize_page_name(self, raw: str) -> str | None:
        token = re.sub(r"\s+", " ", (raw or "").strip().lower())
        token = re.sub(r"^(?:and|or|plus|also|then|with)\s+", "", token)
        token = re.sub(r"\s+pages?$", "", token).strip()
        token = token.replace("-", " ")
        if not token or len(token) > 32:
            return None
        skip = {
            "three",
            "two",
            "one",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "web",
            "landing",
            "multi",
            "single",
            "this",
            "that",
            "the",
            "a",
            "an",
            "each",
            "every",
            "first",
            "second",
            "third",
            "main",
            "new",
            "my",
            "our",
            "some",
            "more",
            "extra",
            "other",
            "those",
            "these",
            "website",
            "site",
            "proper",
            "luxury",
        }
        if token in skip or token.isdigit():
            return None
        aliases = {
            "home": "Home",
            "homepage": "Home",
            "landing": "Home",
            "about": "About",
            "about us": "About",
            "aboutus": "About",
            "contact": "Contact",
            "contact us": "Contact",
            "contactus": "Contact",
            "shop": "Shop",
            "store": "Shop",
            "products": "Shop",
            "product": "Shop",
            "lookbook": "Lookbook",
            "gallery": "Gallery",
            "collections": "Collections",
            "collection": "Collections",
            "men": "Men",
            "women": "Women",
            "login": "Login",
            "sign in": "Login",
            "signin": "Login",
            "register": "Register",
            "sign up": "Register",
            "signup": "Register",
            "blog": "Blog",
            "pricing": "Pricing",
            "faq": "FAQ",
            "services": "Services",
            "work": "Work",
            "portfolio": "Portfolio",
            "menu": "Menu",
            "reservations": "Reservations",
            "booking": "Booking",
        }
        compact = token.replace(" ", "")
        if token in aliases:
            return aliases[token]
        if compact in {k.replace(" ", ""): v for k, v in aliases.items()}:
            return {k.replace(" ", ""): v for k, v in aliases.items()}[compact]
        # Reject junk phrases that aren't real pages
        if any(w in token.split() for w in ("reference", "luxury", "proper", "create", "want", "need")):
            return None
        titled = token.title()
        if titled in {"About Us", "Aboutus"}:
            return "About"
        return titled if 2 <= len(titled) <= 24 else None

    def _extract_spoken_pages(self, lowered: str) -> list[str] | None:
        """Parse natural-language page lists like 'three page. home, contact and about'."""
        found: list[str] = []

        def _add(name: str | None) -> None:
            if name and name not in found:
                found.append(name)

        # Left-to-right discovery preserves the user's listed order
        for m in re.finditer(
            r"\b(home(?:\s*page)?|about(?:\s+us)?(?:\s*page)?|contact(?:\s+us)?(?:\s*page)?|"
            r"shop(?:\s*page)?|store(?:\s*page)?|lookbook(?:\s*page)?|gallery(?:\s*page)?|"
            r"collections?(?:\s*page)?|men(?:\s*page)?|women(?:\s*page)?|"
            r"login(?:\s*page)?|register(?:\s*page)?|blog(?:\s*page)?|pricing(?:\s*page)?|"
            r"faq(?:\s*page)?|services?(?:\s*page)?|portfolio(?:\s*page)?|menu(?:\s*page)?)\b",
            lowered,
        ):
            _add(self._normalize_page_name(m.group(1)))

        # Explicit count: "3 pages" / "three pages"
        count_m = re.search(
            r"\b(\d+|one|two|three|four|five|six|seven|eight)\s+pages?\b",
            lowered,
        )
        word_counts = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
        }
        expected = None
        if count_m:
            raw = count_m.group(1)
            expected = int(raw) if raw.isdigit() else word_counts.get(raw)

        # "pages: home, about, contact"
        listed = re.findall(
            r"(?:pages?(?:\s+include|\s+are|:)\s+)([a-z0-9 ,&/-]+)",
            lowered,
        )
        for chunk in listed:
            for part in re.split(r"[,/]| and ", chunk):
                _add(self._normalize_page_name(part))

        # Require a clear page-intent signal
        has_page_word = bool(re.search(r"\bpages?\b", lowered))
        if not found or not has_page_word:
            return None
        if not expected and len(found) < 2:
            return None

        # If a count was given, keep Home + the next (n-1) pages in mention order
        if expected and len(found) > expected:
            rest = [p for p in found if p != "Home"]
            found = (["Home"] if "Home" in found else []) + rest
            found = found[:expected]

        if "Home" not in found:
            found.insert(0, "Home")
        elif found[0] != "Home":
            found = ["Home"] + [p for p in found if p != "Home"]

        out: list[str] = []
        for p in found:
            if p not in out:
                out.append(p)
        if expected:
            out = out[:expected]
        return out[:12]

    def _extract_pages(
        self, lowered: str, matched: WebsiteType, sections: list[str], original: str = ""
    ) -> list[str]:
        # Spoken / block extraction is handled in analyze(); this is the default path
        explicit = self._extract_pages_block(original) if original else []
        if explicit:
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
                if page == "Blog" and (
                    "Articles" in pages
                    or matched.id.startswith("blog")
                    or "magazine" in matched.id
                ):
                    continue
                pages.append(page)

        if any(k in lowered for k in ("sign in", "sign-in", "log in", "log-in")) and "Login" not in pages:
            pages.append("Login")
        if any(k in lowered for k in ("sign up", "sign-up", "register", "create account")) and "Register" not in pages:
            pages.append("Register")

        for s in page_like:
            if s not in pages and s.lower() != "home":
                pages.append(s)

        return pages

    def _clean_brand_candidate(self, raw: str) -> str:
        """Strip instructional tails so 'Vishu Creation so create…' → 'Vishu Creation'."""
        name = re.sub(r"\s+", " ", (raw or "")).strip(" .,!?'\"")
        # Cut at common instruction / filler boundaries
        name = re.split(
            r"\b(?:so|please|and|with|that|also|give|create|make|build|for|to|which|where|"
            r"website|site|responsive|logo|attractive|customer|customers|sign\s*in|sign\s*up|"
            r"easy|collection|branding|3d|view)\b",
            name,
            maxsplit=1,
            flags=re.I,
        )[0].strip(" .,!?'\"-")
        # Keep at most 4 words for a brand mark
        parts = [p for p in name.split() if p]
        if len(parts) > 4:
            parts = parts[:4]
        name = " ".join(parts).strip()
        if len(name) < 2:
            return ""
        # Title-case if mostly lowercase
        if name.islower() or (name[:1].islower()):
            return name.title()
        return name

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
            named = self._normalize_page_name(titled) or titled
            if named not in pages:
                pages.append(named)
            if len(pages) >= 12:
                break
        return pages

    def _choose_layout(self, matched: WebsiteType, sections: list[str], pages: list[str]) -> str:
        # Explicit multi-page lists always win
        if len(pages) >= 2:
            return "multi_page"
        # Retail / store types are always multi-page sites
        if matched.category == "retail" or any(
            k in matched.id
            for k in ("store", "shop", "ecommerce", "fashion", "mobile", "book", "shoe", "sneaker")
        ):
            return "multi_page"
        if matched.category == "portfolio" or matched.id in {"personal_brand", "landing_page"}:
            return "single_page"
        if len(pages) <= 1 and len(sections) >= 5:
            return "single_page"
        if len(pages) <= 1:
            return "single_page"
        return "multi_page"

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
        lower = cleaned.lower()
        # Never publish raw build instructions as SEO description
        if any(
            m in lower
            for m in (
                "i want",
                "give me",
                "create ",
                "build ",
                "make ",
                "website design",
                "full website",
            )
        ):
            if any(k in lower for k in ("video", "generator")):
                return "AI video generator — turn prompts into polished videos in seconds."
            return f"Discover {matched.label.lower()} — modern, fast, and ready to ship."
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

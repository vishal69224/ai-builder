from __future__ import annotations

import re

from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements


class ComponentGenerator:
    """Generate real React + Tailwind sites — style picked from prompt intent."""

    def generate(self, requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
        analysis = requirements.analysis
        type_id = (analysis.website_type_id or "").lower()
        prompt = analysis.raw_prompt.lower()

        def has_word(*words: str) -> bool:
            return any(re.search(rf"\b{re.escape(w)}\b", prompt) for w in words)

        is_footwear = (
            any(k in type_id for k in ("shoe", "sneaker", "footwear"))
            or has_word(
                "shoe",
                "shoes",
                "sneaker",
                "sneakers",
                "footwear",
                "loafer",
                "loafers",
            )
            or "shoe store" in prompt
            or "shoe shop" in prompt
            or "footwear store" in prompt
        )

        # Footwear MUST win (was incorrectly generating phone stores)
        if is_footwear:
            from app.generation.generators.footwear import generate_shoe_store

            return generate_shoe_store(requirements, plan)

        is_blog = (
            any(k in type_id for k in ("blog", "magazine"))
            or has_word("blog", "magazine", "editorial")
            or "seo blog" in prompt
            or "seo website" in prompt
            or "seo site" in prompt
            or "newsletter site" in prompt
        )
        if is_blog:
            from app.generation.generators.blog import generate_seo_blog

            return generate_seo_blog(requirements, plan)

        # Strict electronics signals only — never bare "mobile" (matches mobile-first)
        is_electronics = (
            "mobile_store" in type_id
            or "electronics" in type_id
            or "mobilehub" in prompt
            or "smartphone" in prompt
            or "smartphones" in prompt
            or "electronics store" in prompt
            or "phone store" in prompt
            or "mobile store" in prompt
            or "mobile shop" in prompt
            or "mobile phone" in prompt
            or has_word("iphone", "oneplus", "xiaomi")
            or ("samsung" in prompt and has_word("galaxy", "phone", "mobile"))
        )

        if is_electronics:
            from app.generation.generators.electronics import generate_electronics_store

            return generate_electronics_store(requirements, plan)

        if any(
            k in type_id for k in ("fashion", "clothing", "boutique", "apparel")
        ) or has_word("clothing", "apparel", "boutique", "garment", "menswear", "womenswear") or any(
            s in prompt for s in ("cloth shop", "clothing store", "cloth store", "clothes shop")
        ):
            return _generate_fashion_shop(requirements, plan)

        return _generate_generic(requirements, plan)


def _generate_generic(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    analysis = requirements.analysis
    title = plan.project_name
    theme = analysis.theme
    primary = theme.get("primary_color", "#0f172a")
    is_dark = (
        analysis.color == "Dark"
        or theme.get("style") in {"dark", "luxury", "neon", "nightlife"}
        or "dark" in analysis.raw_prompt.lower()
    )
    glass = "glassmorphism" in analysis.raw_prompt.lower() or "glass" in analysis.raw_prompt.lower()
    scroll = any("scroll" in a for a in analysis.animations) or "scroll" in analysis.raw_prompt.lower()
    brand = getattr(analysis, "brand_name", "") or title
    tagline = _tagline(analysis.raw_prompt, analysis.website_type, brand)
    cta = requirements.cta_primary
    if any(k in analysis.raw_prompt.lower() for k in ("personal", "brand", "portfolio", "hire")):
        cta = "Let's work together"

    sections = _resolve_sections(requirements)
    single_page = analysis.layout == "single_page" or len(plan.routes) == 1

    nav_bg = (
        "bg-white/10 backdrop-blur-xl border-white/20 text-white"
        if glass
        else ("bg-slate-950/95 text-white border-slate-800" if is_dark else "bg-white/90 backdrop-blur border-slate-200")
    )
    page_bg = "bg-slate-950 text-slate-100" if is_dark else "bg-slate-50 text-slate-900"
    muted = "text-slate-400" if is_dark else "text-slate-600"
    card = (
        "rounded-2xl border border-slate-800 bg-slate-900/80 p-6"
        if is_dark
        else "rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
    )

    files: list[GeneratedFile] = []
    files.append(_button(primary))
    files.append(_card(card, muted))
    files.append(_hero(is_dark, muted))
    files.append(_navbar(title, plan, sections, single_page, nav_bg))
    files.append(_footer(title, is_dark))

    section_files = {
        "About": _about_section(title, card, muted, scroll),
        "Experience": _experience_section(card, muted, scroll),
        "Skills": _skills_section(card, muted, scroll),
        "Projects": _projects_section(card, muted, scroll),
        "Blog": _blog_section(card, muted, scroll),
        "Testimonials": _testimonials_section(card, muted, scroll),
        "Contact": _contact_section(card, muted, primary, scroll),
        "Services": _services_section(card, muted, scroll),
    }

    needed = set(sections)
    for name, gen in section_files.items():
        if name in needed or (name == "Contact" and "ContactForm" in analysis.components):
            files.append(gen)

    if "ProjectGallery" in analysis.components and "Projects" not in needed:
        files.append(section_files["Projects"])
        needed.add("Projects")
    if "AboutSection" in analysis.components and "About" not in needed:
        files.append(section_files["About"])
        needed.add("About")
    if "ExperienceSection" in analysis.components and "Experience" not in needed:
        files.append(section_files["Experience"])
        needed.add("Experience")
    if "SkillsSection" in analysis.components and "Skills" not in needed:
        files.append(section_files["Skills"])
        needed.add("Skills")
    if "BlogSection" in analysis.components and "Blog" not in needed:
        files.append(section_files["Blog"])
        needed.add("Blog")
    if "Testimonials" in analysis.components and "Testimonials" not in needed:
        files.append(section_files["Testimonials"])
        needed.add("Testimonials")
    if "ContactForm" in analysis.components and "Contact" not in needed:
        files.append(section_files["Contact"])
        needed.add("Contact")

    for route in plan.routes:
        if route["path"] == "/":
            body = _home_page(title, tagline, cta, analysis.website_type, sorted_sections(needed), page_bg)
        else:
            body = _content_page(route["page"], route["component"], title, card, muted, page_bg)
        files.append(GeneratedFile(path=f"src/pages/{route['component']}.tsx", content=body))

    files.append(_use_theme(is_dark))
    by_path = {f.path: f for f in files}
    return list(by_path.values())


def _generate_fashion_shop(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    analysis = requirements.analysis
    title = (getattr(analysis, "brand_name", "") or plan.project_name).strip() or "Fashion Store"
    primary = analysis.theme.get("primary_color", "#111827")
    is_dark = analysis.color == "Dark" or "dark" in analysis.raw_prompt.lower()
    tagline = _tagline(analysis.raw_prompt, analysis.website_type, title)
    if "i have" in tagline.lower() or "cloth shop" in tagline.lower():
        tagline = f"Contemporary clothing for everyday style — curated by {title}."
    cta = "Shop now"
    page_bg = "bg-neutral-950 text-neutral-50" if is_dark else "bg-stone-50 text-stone-900"
    muted = "text-neutral-400" if is_dark else "text-stone-600"
    card = (
        "rounded-2xl border border-neutral-800 bg-neutral-900 p-5"
        if is_dark
        else "rounded-2xl border border-stone-200 bg-white p-5 shadow-sm"
    )
    nav_bg = (
        "bg-neutral-950/95 text-white border-neutral-800"
        if is_dark
        else "bg-white/95 backdrop-blur border-stone-200 text-stone-900"
    )

    files = [
        _button(primary),
        _card(card, muted),
        _fashion_hero(is_dark, muted),
        _navbar(title, plan, [], False, nav_bg),
        _footer(title, is_dark),
        _product_grid(title, card, muted, is_dark),
        _lookbook_grid(card, muted, is_dark),
        _category_strip(is_dark),
        _testimonials_section(card, muted, True),
        _contact_section(card, muted, primary, True),
        _fashion_about(title, card, muted),
        _use_theme(is_dark),
    ]

    for route in plan.routes:
        page = route["page"].lower()
        if route["path"] == "/":
            body = _fashion_home(title, tagline, cta, analysis.website_type, page_bg)
        elif "shop" in page:
            body = _shop_page(route["component"], title, page_bg)
        elif "lookbook" in page or "gallery" in page:
            body = _lookbook_page(route["component"], page_bg)
        elif "about" in page:
            body = (
                f"import {{ AboutBrand }} from '../components/AboutBrand'\n\n"
                f"export default function {route['component']}() {{\n"
                f"  return (\n    <div className=\"{page_bg}\">\n      <AboutBrand />\n    </div>\n  )\n}}\n"
            )
        elif "contact" in page:
            body = (
                f"import {{ ContactForm }} from '../components/ContactForm'\n\n"
                f"export default function {route['component']}() {{\n"
                f"  return (\n    <div className=\"{page_bg}\">\n      <ContactForm />\n    </div>\n  )\n}}\n"
            )
        else:
            body = _content_page(route["page"], route["component"], title, card, muted, page_bg)
        files.append(GeneratedFile(path=f"src/pages/{route['component']}.tsx", content=body))

    by_path = {f.path: f for f in files}
    return list(by_path.values())


def _use_theme(is_dark: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/hooks/useTheme.ts",
        content=(
            "import { useEffect, useState } from 'react'\n\n"
            "export function useTheme() {\n"
            f"  const [dark] = useState({str(is_dark).lower()})\n"
            "  useEffect(() => {\n"
            "    document.documentElement.classList.toggle('dark', dark)\n"
            "  }, [dark])\n"
            "  return { dark }\n"
            "}\n"
        ),
    )


def _fashion_hero(is_dark: bool, muted: str) -> GeneratedFile:
    accent = "text-amber-300" if is_dark else "text-amber-800"
    return GeneratedFile(
        path="src/components/Hero.tsx",
        content=(
            "import { Button } from './Button'\n\n"
            "type HeroProps = { title: string; subtitle: string; eyebrow: string; cta: string }\n\n"
            "export function Hero({ title, subtitle, eyebrow, cta }: HeroProps) {\n"
            "  return (\n"
            "    <section className=\"relative overflow-hidden\">\n"
            "      <div className=\"absolute inset-0 bg-gradient-to-br from-stone-900 via-stone-800 to-amber-900/40\" />\n"
            "      <div className=\"relative mx-auto flex min-h-[78vh] max-w-6xl flex-col justify-center px-4 py-20 text-white\">\n"
            f"        <p className=\"text-sm font-semibold uppercase tracking-[0.25em] {accent}\">{{eyebrow}}</p>\n"
            "        <h1 className=\"mt-4 max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl\">{title}</h1>\n"
            "        <p className=\"mt-5 max-w-2xl text-lg leading-relaxed text-stone-200\">{subtitle}</p>\n"
            "        <div className=\"mt-10 flex flex-wrap gap-3\">\n"
            "          <Button href=\"#/shop\">{cta}</Button>\n"
            "          <Button href=\"#/lookbook\" variant=\"ghost\">View lookbook</Button>\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _product_grid(brand: str, card: str, muted: str, is_dark: bool) -> GeneratedFile:
    safe = brand.replace("'", "")
    return GeneratedFile(
        path="src/components/ProductGrid.tsx",
        content=(
            "const products = [\n"
            f"  {{ name: 'Everyday Cotton Kurta', price: '₹1,299', tag: 'Men', tone: 'from-amber-200 to-stone-400' }},\n"
            f"  {{ name: 'Festive Silk Saree', price: '₹4,999', tag: 'Women', tone: 'from-rose-200 to-amber-300' }},\n"
            f"  {{ name: 'Kids Printed Set', price: '₹899', tag: 'Kids', tone: 'from-sky-200 to-emerald-200' }},\n"
            f"  {{ name: 'Linen Shirt', price: '₹1,599', tag: 'Men', tone: 'from-stone-200 to-stone-500' }},\n"
            f"  {{ name: 'Embroidered Dupatta', price: '₹799', tag: 'Women', tone: 'from-violet-200 to-rose-200' }},\n"
            f"  {{ name: 'Casual Denim Jacket', price: '₹2,499', tag: 'Unisex', tone: 'from-blue-300 to-slate-500' }},\n"
            "]\n\n"
            "export function ProductGrid({ limit }: { limit?: number }) {\n"
            "  const items = typeof limit === 'number' ? products.slice(0, limit) : products\n"
            "  return (\n"
            "    <section id=\"shop\" className=\"mx-auto max-w-6xl px-4 py-16\">\n"
            "      <div className=\"flex flex-wrap items-end justify-between gap-3\">\n"
            "        <div>\n"
            "          <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-amber-700\">Shop</p>\n"
            f"          <h2 className=\"mt-2 text-3xl font-bold tracking-tight\">{safe} collection</h2>\n"
            "        </div>\n"
            "        <a href=\"#/shop\" className=\"text-sm font-medium underline-offset-4 hover:underline\">View all</a>\n"
            "      </div>\n"
            "      <div className=\"mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3\">\n"
            "        {items.map((p) => (\n"
            f"          <article key={{p.name}} className=\"{card} overflow-hidden p-0\">\n"
            "            <div className={`h-44 bg-gradient-to-br ${p.tone}`} />\n"
            "            <div className=\"p-5\">\n"
            f"              <p className=\"text-xs uppercase tracking-wide {muted}\">{{p.tag}}</p>\n"
            "              <h3 className=\"mt-1 text-lg font-semibold\">{p.name}</h3>\n"
            "              <p className=\"mt-2 text-sm font-medium\">{p.price}</p>\n"
            "              <button type=\"button\" className=\"mt-4 text-sm font-semibold underline-offset-4 hover:underline\">Add to bag</button>\n"
            "            </div>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _lookbook_grid(card: str, muted: str, is_dark: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/LookbookGrid.tsx",
        content=(
            "const shots = [\n"
            "  { title: 'Festive Edit', note: 'Rich weaves for celebrations' },\n"
            "  { title: 'Daily Essentials', note: 'Soft cottons for work and home' },\n"
            "  { title: 'Monsoon Layers', note: 'Light jackets and breathable fits' },\n"
            "  { title: 'Family Styles', note: 'Matching looks for everyone' },\n"
            "]\n\n"
            "export function LookbookGrid() {\n"
            "  return (\n"
            "    <section id=\"lookbook\" className=\"mx-auto max-w-6xl px-4 py-16\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-amber-700\">Lookbook</p>\n"
            "      <h2 className=\"mt-2 text-3xl font-bold tracking-tight\">Seasonal styles</h2>\n"
            "      <div className=\"mt-8 grid gap-4 md:grid-cols-2\">\n"
            "        {shots.map((shot, i) => (\n"
            f"          <article key={{shot.title}} className=\"{card} min-h-52\">\n"
            "            <div className={`mb-4 h-36 rounded-xl bg-gradient-to-br ${i % 2 ? 'from-stone-300 to-amber-200' : 'from-amber-100 to-stone-400'}`} />\n"
            "            <h3 className=\"text-xl font-semibold\">{shot.title}</h3>\n"
            f"            <p className=\"mt-2 text-sm {muted}\">{{shot.note}}</p>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _category_strip(is_dark: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/CategoryStrip.tsx",
        content=(
            "const cats = ['Men', 'Women', 'Kids', 'Festive', 'Accessories']\n\n"
            "export function CategoryStrip() {\n"
            "  return (\n"
            "    <section className=\"border-y border-stone-200/60 bg-white/50\">\n"
            "      <div className=\"mx-auto flex max-w-6xl flex-wrap gap-3 px-4 py-5 text-sm font-medium\">\n"
            "        {cats.map((c) => (\n"
            "          <a key={c} href=\"#/shop\" className=\"rounded-full border border-stone-300 px-4 py-1.5 hover:border-stone-900\">\n"
            "            {c}\n"
            "          </a>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _fashion_about(title: str, card: str, muted: str) -> GeneratedFile:
    safe = title.replace("'", "")
    return GeneratedFile(
        path="src/components/AboutBrand.tsx",
        content=(
            "export function AboutBrand() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-16\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-amber-700\">About</p>\n"
            f"      <h2 className=\"mt-2 text-3xl font-bold tracking-tight\">About {safe}</h2>\n"
            f"      <div className=\"mt-8 grid gap-6 md:grid-cols-2\">\n"
            f"        <div className=\"{card}\">\n"
            f"          <p className=\"leading-relaxed {muted}\">\n"
            f"            {safe} is a clothing destination for quality everyday fashion — from festive wear to comfortable daily outfits for the whole family.\n"
            "          </p>\n"
            "        </div>\n"
            f"        <div className=\"{card}\">\n"
            "          <ul className=\"space-y-3 text-sm\">\n"
            "            <li>• Men, women, and kids collections</li>\n"
            "            <li>• New arrivals every season</li>\n"
            "            <li>• Friendly in-store styling help</li>\n"
            "          </ul>\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _fashion_home(title: str, tagline: str, cta: str, website_type: str, page_bg: str) -> str:
    safe_tag = tagline.replace("`", "'").replace('"', "'")
    return (
        "import { Hero } from '../components/Hero'\n"
        "import { CategoryStrip } from '../components/CategoryStrip'\n"
        "import { ProductGrid } from '../components/ProductGrid'\n"
        "import { LookbookGrid } from '../components/LookbookGrid'\n"
        "import { Testimonials } from '../components/Testimonials'\n"
        "import { Button } from '../components/Button'\n\n"
        "export default function HomePage() {\n"
        "  return (\n"
        f'    <div className="{page_bg}">\n'
        f'      <Hero title="{title}" subtitle="{safe_tag}" eyebrow="{website_type}" cta="{cta}" />\n'
        "      <CategoryStrip />\n"
        "      <ProductGrid limit={3} />\n"
        "      <LookbookGrid />\n"
        "      <Testimonials />\n"
        "      <section className=\"mx-auto max-w-6xl px-4 py-16 text-center\">\n"
        f'        <h2 className="text-3xl font-bold tracking-tight">Visit {title}</h2>\n'
        '        <p className="mx-auto mt-3 max-w-xl text-stone-600">Discover new arrivals, festive edits, and everyday essentials.</p>\n'
        '        <div className="mt-8 flex justify-center gap-3">\n'
        '          <Button href="#/shop">Shop collection</Button>\n'
        '          <Button href="#/contact" variant="ghost">Contact us</Button>\n'
        "        </div>\n"
        "      </section>\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _shop_page(component: str, title: str, page_bg: str) -> str:
    return (
        "import { ProductGrid } from '../components/ProductGrid'\n\n"
        f"export default function {component}() {{\n"
        "  return (\n"
        f'    <div className="{page_bg}">\n'
        "      <ProductGrid />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _lookbook_page(component: str, page_bg: str) -> str:
    return (
        "import { LookbookGrid } from '../components/LookbookGrid'\n\n"
        f"export default function {component}() {{\n"
        "  return (\n"
        f'    <div className="{page_bg}">\n'
        "      <LookbookGrid />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _resolve_sections(requirements: StructuredRequirements) -> list[str]:
    analysis = requirements.analysis
    raw = list(analysis.sections or [])
    # Fall back to content_sections / pages
    if not raw:
        for item in requirements.content_sections:
            label = item.replace("Section", "").replace("Gallery", "Projects").replace("Form", "")
            if label and label not in raw:
                raw.append(label)
        for page in analysis.pages:
            if page != "Home" and page not in raw:
                raw.append(page)
    # Normalize
    out: list[str] = []
    for s in raw:
        if s.lower() in {"hero", "footer", "navbar", "nav"}:
            continue
        if s not in out:
            out.append(s)
    if not out:
        out = ["About", "Projects", "Contact"]
    if "Contact" not in out:
        out.append("Contact")
    return out


def sorted_sections(needed: set[str]) -> list[str]:
    order = ["About", "Experience", "Skills", "Projects", "Services", "Blog", "Testimonials", "Contact"]
    return [s for s in order if s in needed] + [s for s in needed if s not in order]


def _tagline(prompt: str, website_type: str, brand: str = "") -> str:
    cleaned = re.sub(r"\s+", " ", prompt).strip()
    lower = cleaned.lower()
    # Casual shop prompts → polished tagline
    if any(k in lower for k in ("cloth", "clothing", "fashion", "apparel", "boutique")):
        name = brand or "our store"
        return f"Quality clothing and fashion for the whole family — welcome to {name}."
    first = re.split(r"[.\n]", cleaned)[0].strip()
    first = re.sub(r"^(create|build|make|design|i have|i own)\s+(a|an|the|one)?\s*", "", first, flags=re.I)
    if len(first) > 120:
        first = first[:117] + "..."
    if len(first) < 12 or first.lower().startswith("name was"):
        return f"A modern {website_type.lower()} experience."
    return first[0].upper() + first[1:]


def _button(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Button.tsx",
        content=(
            "type ButtonProps = {\n"
            "  children: React.ReactNode\n"
            "  variant?: 'primary' | 'ghost'\n"
            "  href?: string\n"
            "}\n\n"
            "export function Button({ children, variant = 'primary', href = '#' }: ButtonProps) {\n"
            "  const base = 'inline-flex items-center rounded-lg px-5 py-2.5 text-sm font-semibold transition'\n"
            "  if (variant === 'primary') {\n"
            "    return (\n"
            f"      <a href={{href}} className={{`${{base}} text-white`}} style={{{{ backgroundColor: '{primary}' }}}}>\n"
            "        {children}\n"
            "      </a>\n"
            "    )\n"
            "  }\n"
            "  return (\n"
            "    <a href={href} className={`${base} border border-slate-400/40 bg-transparent opacity-90 hover:opacity-100`}>\n"
            "      {children}\n"
            "    </a>\n"
            "  )\n"
            "}\n"
        ),
    )


def _card(card: str, muted: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Card.tsx",
        content=(
            "type CardProps = { title: string; description: string }\n\n"
            "export function Card({ title, description }: CardProps) {\n"
            "  return (\n"
            f"    <article className=\"{card} transition hover:-translate-y-0.5\">\n"
            "      <h3 className=\"text-lg font-semibold\">{title}</h3>\n"
            f"      <p className=\"mt-2 text-sm leading-relaxed {muted}\">{{description}}</p>\n"
            "    </article>\n"
            "  )\n"
            "}\n"
        ),
    )


def _hero(is_dark: bool, muted: str) -> GeneratedFile:
    accent = "text-teal-300" if is_dark else "text-teal-700"
    return GeneratedFile(
        path="src/components/Hero.tsx",
        content=(
            "import { Button } from './Button'\n\n"
            "type HeroProps = {\n"
            "  title: string\n"
            "  subtitle: string\n"
            "  eyebrow: string\n"
            "  cta: string\n"
            "}\n\n"
            "export function Hero({ title, subtitle, eyebrow, cta }: HeroProps) {\n"
            "  return (\n"
            "    <section id=\"hero\" className=\"mx-auto flex min-h-[78vh] max-w-6xl flex-col justify-center px-4 py-20\">\n"
            f"      <p className=\"text-sm font-semibold uppercase tracking-[0.22em] {accent}\">{{eyebrow}}</p>\n"
            "      <h1 className=\"mt-4 max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl\">{title}</h1>\n"
            f"      <p className=\"mt-5 max-w-2xl text-lg leading-relaxed {muted}\">{{subtitle}}</p>\n"
            "      <div className=\"mt-10 flex flex-wrap gap-3\">\n"
            "        <Button href=\"#contact\">{cta}</Button>\n"
            "        <Button href=\"#projects\" variant=\"ghost\">View work</Button>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _navbar(title: str, plan: ProjectPlan, sections: list[str], single_page: bool, nav_bg: str) -> GeneratedFile:
    if single_page:
        links = []
        for s in sorted_sections(set(sections)):
            slug = s.lower().replace(" ", "-")
            links.append(f'  {{ to: "#{slug}", label: "{s}" }}')
        link_lines = ",\n".join(links) or '  { to: "#contact", label: "Contact" }'
        return GeneratedFile(
            path="src/components/Navbar.tsx",
            content=(
                "const links = [\n"
                f"{link_lines}\n"
                "]\n\n"
                "export function Navbar() {\n"
                "  return (\n"
                f"    <header className=\"sticky top-0 z-50 border-b {nav_bg}\">\n"
                "      <div className=\"mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4\">\n"
                f"        <a href=\"#hero\" className=\"text-lg font-semibold tracking-tight\">{title}</a>\n"
                "        <nav className=\"flex flex-wrap justify-end gap-x-4 gap-y-2 text-sm\">\n"
                "          {links.map((link) => (\n"
                "            <a key={link.to} href={link.to} className=\"opacity-75 hover:opacity-100\">\n"
                "              {link.label}\n"
                "            </a>\n"
                "          ))}\n"
                "        </nav>\n"
                "      </div>\n"
                "    </header>\n"
                "  )\n"
                "}\n"
            ),
        )

    link_lines = ",\n".join(f'  {{ to: "{r["path"]}", label: "{r["page"]}" }}' for r in plan.routes)
    return GeneratedFile(
        path="src/components/Navbar.tsx",
        content=(
            "import { Link, NavLink } from 'react-router-dom'\n\n"
            f"const links = [\n{link_lines}\n]\n\n"
            "export function Navbar() {\n"
            "  return (\n"
            f"    <header className=\"sticky top-0 z-50 border-b {nav_bg}\">\n"
            "      <div className=\"mx-auto flex max-w-6xl items-center justify-between px-4 py-4\">\n"
            f"        <Link to=\"/\" className=\"text-lg font-semibold tracking-tight\">{title}</Link>\n"
            "        <nav className=\"flex flex-wrap gap-3 text-sm\">\n"
            "          {links.map((link) => (\n"
            "            <NavLink\n"
            "              key={link.to}\n"
            "              to={link.to}\n"
            "              className={({ isActive }) =>\n"
            "                isActive ? 'font-semibold opacity-100' : 'opacity-70 hover:opacity-100'\n"
            "              }\n"
            "            >\n"
            "              {link.label}\n"
            "            </NavLink>\n"
            "          ))}\n"
            "        </nav>\n"
            "      </div>\n"
            "    </header>\n"
            "  )\n"
            "}\n"
        ),
    )


def _footer(title: str, is_dark: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Footer.tsx",
        content=(
            "export function Footer() {\n"
            "  return (\n"
            f"    <footer className=\"border-t {'border-slate-800 bg-slate-950 text-slate-400' if is_dark else 'border-slate-200 bg-slate-50 text-slate-600'}\">\n"
            "      <div className=\"mx-auto flex max-w-6xl flex-col gap-2 px-4 py-10 text-sm sm:flex-row sm:items-center sm:justify-between\">\n"
            f"        <p>© {{new Date().getFullYear()}} {title}</p>\n"
            "        <div className=\"flex gap-4\">\n"
            "          <a href=\"#about\" className=\"hover:opacity-100 opacity-80\">About</a>\n"
            "          <a href=\"#projects\" className=\"hover:opacity-100 opacity-80\">Projects</a>\n"
            "          <a href=\"#contact\" className=\"hover:opacity-100 opacity-80\">Contact</a>\n"
            "        </div>\n"
            "      </div>\n"
            "    </footer>\n"
            "  )\n"
            "}\n"
        ),
    )


def _reveal(scroll: bool) -> str:
    return "motion-safe:animate-[fadeUp_0.7s_ease-out_both]" if scroll else ""


def _about_section(title: str, card: str, muted: str, scroll: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/AboutSection.tsx",
        content=(
            "export function AboutSection() {\n"
            "  return (\n"
            f"    <section id=\"about\" className=\"mx-auto max-w-6xl px-4 py-20 {_reveal(scroll)}\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-teal-500\">About</p>\n"
            f"      <h2 className=\"mt-3 text-3xl font-bold tracking-tight\">About {title}</h2>\n"
            f"      <div className=\"mt-8 grid gap-6 md:grid-cols-2\">\n"
            f"        <div className=\"{card}\">\n"
            f"          <p className=\"leading-relaxed {muted}\">\n"
            "            I help brands and teams communicate clearly through thoughtful design, writing, and digital products.\n"
            "            This site is a living showcase of selected work, experience, and ideas.\n"
            "          </p>\n"
            "        </div>\n"
            f"        <div className=\"{card}\">\n"
            "          <ul className=\"space-y-3 text-sm\">\n"
            "            <li>• Strategy-minded storytelling</li>\n"
            "            <li>• Product and brand design</li>\n"
            "            <li>• Clear writing for the web</li>\n"
            "          </ul>\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _experience_section(card: str, muted: str, scroll: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ExperienceSection.tsx",
        content=(
            "const roles = [\n"
            "  { role: 'Lead Product Designer', org: 'Northstar Labs', years: '2022 — Present', detail: 'Owned end-to-end product UX for B2B tools.' },\n"
            "  { role: 'Brand Strategist', org: 'Studio Ember', years: '2019 — 2022', detail: 'Built brand systems and launch sites for startups.' },\n"
            "  { role: 'Frontend Engineer', org: 'Pulse Media', years: '2016 — 2019', detail: 'Shipped accessible marketing experiences.' },\n"
            "]\n\n"
            "export function ExperienceSection() {\n"
            "  return (\n"
            f"    <section id=\"experience\" className=\"mx-auto max-w-6xl px-4 py-20 {_reveal(scroll)}\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-teal-500\">Experience</p>\n"
            "      <h2 className=\"mt-3 text-3xl font-bold tracking-tight\">Selected experience</h2>\n"
            "      <div className=\"mt-8 space-y-4\">\n"
            "        {roles.map((item) => (\n"
            f"          <article key={{item.role}} className=\"{card}\">\n"
            "            <div className=\"flex flex-wrap items-baseline justify-between gap-2\">\n"
            "              <h3 className=\"text-lg font-semibold\">{item.role}</h3>\n"
            f"              <span className=\"text-xs {muted}\">{{item.years}}</span>\n"
            "            </div>\n"
            f"            <p className=\"mt-1 text-sm font-medium\">{{item.org}}</p>\n"
            f"            <p className=\"mt-2 text-sm {muted}\">{{item.detail}}</p>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _skills_section(card: str, muted: str, scroll: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/SkillsSection.tsx",
        content=(
            "const skills = [\n"
            "  { name: 'Product Design', level: 'Expert' },\n"
            "  { name: 'Brand Systems', level: 'Advanced' },\n"
            "  { name: 'React / TypeScript', level: 'Advanced' },\n"
            "  { name: 'Content Strategy', level: 'Advanced' },\n"
            "  { name: 'SEO & Analytics', level: 'Intermediate' },\n"
            "  { name: 'Motion Design', level: 'Intermediate' },\n"
            "]\n\n"
            "export function SkillsSection() {\n"
            "  return (\n"
            f"    <section id=\"skills\" className=\"mx-auto max-w-6xl px-4 py-20 {_reveal(scroll)}\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-teal-500\">Skills</p>\n"
            "      <h2 className=\"mt-3 text-3xl font-bold tracking-tight\">Capabilities</h2>\n"
            "      <div className=\"mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3\">\n"
            "        {skills.map((skill) => (\n"
            f"          <div key={{skill.name}} className=\"{card}\">\n"
            "            <h3 className=\"font-semibold\">{skill.name}</h3>\n"
            f"            <p className=\"mt-1 text-sm {muted}\">{{skill.level}}</p>\n"
            "          </div>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _projects_section(card: str, muted: str, scroll: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ProjectGallery.tsx",
        content=(
            "const projects = [\n"
            "  { title: 'Atlas Brand Refresh', desc: 'Identity, site, and launch campaign for a climate startup.' },\n"
            "  { title: 'Harbor Dashboard', desc: 'Product design system for a logistics analytics suite.' },\n"
            "  { title: 'Editorial Series', desc: 'Long-form essays and visual essays on craft and culture.' },\n"
            "]\n\n"
            "export function ProjectGallery() {\n"
            "  return (\n"
            f"    <section id=\"projects\" className=\"mx-auto max-w-6xl px-4 py-20 {_reveal(scroll)}\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-teal-500\">Projects</p>\n"
            "      <h2 className=\"mt-3 text-3xl font-bold tracking-tight\">Featured work</h2>\n"
            "      <div className=\"mt-8 grid gap-4 md:grid-cols-3\">\n"
            "        {projects.map((project) => (\n"
            f"          <article key={{project.title}} className=\"{card}\">\n"
            "            <div className=\"mb-4 h-28 rounded-xl bg-gradient-to-br from-teal-500/30 to-slate-500/20\" />\n"
            "            <h3 className=\"text-lg font-semibold\">{project.title}</h3>\n"
            f"            <p className=\"mt-2 text-sm {muted}\">{{project.desc}}</p>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _blog_section(card: str, muted: str, scroll: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/BlogSection.tsx",
        content=(
            "const posts = [\n"
            "  { title: 'Designing for quiet confidence', date: 'Mar 2026' },\n"
            "  { title: 'Notes on personal brand systems', date: 'Feb 2026' },\n"
            "  { title: 'Shipping a site in a weekend', date: 'Jan 2026' },\n"
            "]\n\n"
            "export function BlogSection() {\n"
            "  return (\n"
            f"    <section id=\"blog\" className=\"mx-auto max-w-6xl px-4 py-20 {_reveal(scroll)}\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-teal-500\">Blog</p>\n"
            "      <h2 className=\"mt-3 text-3xl font-bold tracking-tight\">Writing</h2>\n"
            "      <div className=\"mt-8 space-y-3\">\n"
            "        {posts.map((post) => (\n"
            f"          <article key={{post.title}} className=\"{card} flex flex-wrap items-center justify-between gap-3\">\n"
            "            <h3 className=\"font-semibold\">{post.title}</h3>\n"
            f"            <span className=\"text-xs {muted}\">{{post.date}}</span>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _testimonials_section(card: str, muted: str, scroll: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Testimonials.tsx",
        content=(
            "const quotes = [\n"
            "  { quote: 'Clear thinking, beautiful execution, and a calm process.', name: 'Amina R.', role: 'Founder' },\n"
            "  { quote: 'Elevated our brand without losing who we are.', name: 'Jordan K.', role: 'CMO' },\n"
            "]\n\n"
            "export function Testimonials() {\n"
            "  return (\n"
            f"    <section id=\"testimonials\" className=\"mx-auto max-w-6xl px-4 py-20 {_reveal(scroll)}\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-teal-500\">Testimonials</p>\n"
            "      <h2 className=\"mt-3 text-3xl font-bold tracking-tight\">Kind words</h2>\n"
            "      <div className=\"mt-8 grid gap-4 md:grid-cols-2\">\n"
            "        {quotes.map((item) => (\n"
            f"          <blockquote key={{item.name}} className=\"{card}\">\n"
            f"            <p className=\"text-base leading-relaxed {muted}\">“{{item.quote}}”</p>\n"
            "            <footer className=\"mt-4 text-sm font-semibold\">{item.name} · {item.role}</footer>\n"
            "          </blockquote>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _contact_section(card: str, muted: str, primary: str, scroll: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ContactForm.tsx",
        content=(
            "export function ContactForm() {\n"
            "  return (\n"
            f"    <section id=\"contact\" className=\"mx-auto max-w-6xl px-4 py-20 {_reveal(scroll)}\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-teal-500\">Contact</p>\n"
            "      <h2 className=\"mt-3 text-3xl font-bold tracking-tight\">Start a conversation</h2>\n"
            f"      <form className=\"mt-8 grid max-w-xl gap-4 {card}\" onSubmit={{(e) => e.preventDefault()}}>\n"
            "        <label className=\"grid gap-1 text-sm\">\n"
            "          Name\n"
            "          <input className=\"rounded-lg border border-slate-500/30 bg-transparent px-3 py-2\" placeholder=\"Your name\" />\n"
            "        </label>\n"
            "        <label className=\"grid gap-1 text-sm\">\n"
            "          Email\n"
            "          <input type=\"email\" className=\"rounded-lg border border-slate-500/30 bg-transparent px-3 py-2\" placeholder=\"you@email.com\" />\n"
            "        </label>\n"
            "        <label className=\"grid gap-1 text-sm\">\n"
            "          Message\n"
            f"          <textarea className=\"min-h-28 rounded-lg border border-slate-500/30 bg-transparent px-3 py-2\" placeholder=\"Tell me about your project\" />\n"
            "        </label>\n"
            f"        <button type=\"submit\" className=\"rounded-lg px-5 py-2.5 text-sm font-semibold text-white\" style={{{{ backgroundColor: '{primary}' }}}}>\n"
            "          Send message\n"
            "        </button>\n"
            f"        <p className=\"text-xs {muted}\">This demo form does not submit to a server.</p>\n"
            "      </form>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _services_section(card: str, muted: str, scroll: bool) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ServiceCards.tsx",
        content=(
            "const services = [\n"
            "  { title: 'Brand Strategy', desc: 'Positioning, messaging, and visual direction.' },\n"
            "  { title: 'Website Design', desc: 'Modern, responsive sites built to convert.' },\n"
            "  { title: 'Content Systems', desc: 'Reusable frameworks for ongoing publishing.' },\n"
            "]\n\n"
            "export function ServiceCards() {\n"
            "  return (\n"
            f"    <section id=\"services\" className=\"mx-auto max-w-6xl px-4 py-20 {_reveal(scroll)}\">\n"
            "      <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-teal-500\">Services</p>\n"
            "      <h2 className=\"mt-3 text-3xl font-bold tracking-tight\">How I can help</h2>\n"
            "      <div className=\"mt-8 grid gap-4 md:grid-cols-3\">\n"
            "        {services.map((s) => (\n"
            f"          <article key={{s.title}} className=\"{card}\">\n"
            "            <h3 className=\"text-lg font-semibold\">{s.title}</h3>\n"
            f"            <p className=\"mt-2 text-sm {muted}\">{{s.desc}}</p>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


SECTION_IMPORTS = {
    "About": ("AboutSection", "AboutSection"),
    "Experience": ("ExperienceSection", "ExperienceSection"),
    "Skills": ("SkillsSection", "SkillsSection"),
    "Projects": ("ProjectGallery", "ProjectGallery"),
    "Blog": ("BlogSection", "BlogSection"),
    "Testimonials": ("Testimonials", "Testimonials"),
    "Contact": ("ContactForm", "ContactForm"),
    "Services": ("ServiceCards", "ServiceCards"),
}


def _home_page(
    title: str,
    tagline: str,
    cta: str,
    website_type: str,
    sections: list[str],
    page_bg: str,
) -> str:
    safe_tagline = tagline.replace("`", "'").replace('"', "'")
    imports = [
        "import { Hero } from '../components/Hero'",
    ]
    jsx_parts = [
        f'      <Hero title="{title}" subtitle="{safe_tagline}" eyebrow="{website_type}" cta="{cta}" />',
    ]
    for section in sections:
        if section not in SECTION_IMPORTS:
            continue
        mod, export = SECTION_IMPORTS[section]
        imports.append(f"import {{ {export} }} from '../components/{mod}'")
        jsx_parts.append(f"      <{export} />")

    return (
        "\n".join(imports)
        + "\n\n"
        + "export default function HomePage() {\n"
        + "  return (\n"
        + f'    <div className="{page_bg}">\n'
        + "\n".join(jsx_parts)
        + "\n"
        + "    </div>\n"
        + "  )\n"
        + "}\n"
    )


def _content_page(page: str, component: str, title: str, card: str, muted: str, page_bg: str) -> str:
    return (
        f"export default function {component}() {{\n"
        "  return (\n"
        f'    <section className="mx-auto max-w-6xl px-4 py-16 {page_bg}">\n'
        f'      <h1 className="text-3xl font-bold tracking-tight">{page}</h1>\n'
        f'      <p className="mt-3 max-w-2xl {muted}">Explore {page.lower()} for {title}.</p>\n'
        f'      <div className="mt-8 grid gap-4 md:grid-cols-2">\n'
        f'        <article className="{card}"><h2 className="font-semibold">Overview</h2><p className="mt-2 text-sm {muted}">Curated content for this section of the site.</p></article>\n'
        f'        <article className="{card}"><h2 className="font-semibold">Highlights</h2><p className="mt-2 text-sm {muted}">Key details visitors should notice first.</p></article>\n'
        "      </div>\n"
        "    </section>\n"
        "  )\n"
        "}\n"
    )

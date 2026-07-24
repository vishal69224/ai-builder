"""Footwear / shoe brand generator — respects requested pages; no forced shop catalog."""

from __future__ import annotations

import re

from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements
from app.generation.planner.niches import invent_brand_name, resolve_niche

SHOE_IMGS = [
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=1200&q=80",
]


def generate_shoe_store(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    analysis = requirements.analysis
    prompt = analysis.raw_prompt or ""
    niche = resolve_niche(analysis.website_type_id, prompt)
    brand = invent_brand_name(
        getattr(analysis, "brand_name", "") or plan.project_name or "",
        niche,
    )
    primary = analysis.theme.get("primary_color", "#111827")
    if "blue" not in prompt.lower():
        primary = "#C6A75E" if "luxury" in prompt.lower() else "#111827"

    route_names = {r["page"].lower() for r in plan.routes}
    has_shop = any(k in n for n in route_names for k in ("shop", "product", "collection", "sneaker"))
    has_lookbook = any(k in n for n in route_names for k in ("lookbook", "gallery"))
    has_about = any("about" in n for n in route_names)
    has_contact = any("contact" in n for n in route_names)
    luxury = "luxury" in prompt.lower() or "premium" in prompt.lower()
    copy = _brand_copy(brand, prompt, luxury=luxury)

    files: list[GeneratedFile] = [
        _button(primary),
        _header(brand, plan, primary, has_shop=has_shop),
        _hero(brand, primary, copy, has_shop=has_shop, has_about=has_about, has_contact=has_contact),
        _story(brand, copy, primary),
        _pillars(brand, luxury=luxury),
        _footer(brand, plan),
        _use_theme(),
        GeneratedFile(path="src/components/Navbar.tsx", content="export { ShoeHeader as Navbar } from './ShoeHeader'\n"),
        GeneratedFile(path="src/components/Hero.tsx", content="export { ShoeHero as Hero } from './ShoeHero'\n"),
        GeneratedFile(path="src/components/Footer.tsx", content="export { ShoeFooter as Footer } from './ShoeFooter'\n"),
        GeneratedFile(
            path="src/components/Card.tsx",
            content=(
                "type CardProps = { title: string; description: string }\n"
                "export function Card({ title, description }: CardProps) {\n"
                "  return (\n"
                "    <article className=\"rounded-2xl border border-stone-200 bg-white p-5 shadow-sm\">\n"
                "      <h3 className=\"font-semibold\">{title}</h3>\n"
                "      <p className=\"mt-2 text-sm text-stone-600\">{description}</p>\n"
                "    </article>\n"
                "  )\n"
                "}\n"
            ),
        ),
    ]

    # Shop / lookbook modules only when those routes exist
    if has_shop:
        files.extend([_categories(), _product_grid(brand, primary, copy), _newsletter(primary, brand)])
    if has_lookbook:
        files.append(_lookbook())
    if has_contact:
        files.append(_contact_block(brand, primary, copy))

    for route in plan.routes:
        page = route["page"].lower()
        comp = route["component"]
        if route["path"] == "/":
            body = _home(
                brand,
                primary,
                copy,
                has_shop=has_shop,
                has_lookbook=has_lookbook,
                has_about=has_about,
                has_contact=has_contact,
            )
        elif any(k in page for k in ("shop", "sneaker", "product", "collection")):
            body = _shop_page(comp, brand)
        elif any(k in page for k in ("lookbook", "gallery")):
            body = _lookbook_page(comp)
        elif "about" in page:
            body = _about_page(comp, brand, copy, primary)
        elif "contact" in page:
            body = _contact_page(comp, brand, primary, copy)
        else:
            body = (
                f"export default function {comp}() {{\n"
                f"  return (\n"
                f"    <section className=\"mx-auto max-w-6xl overflow-x-hidden px-4 py-16\">\n"
                f"      <h1 className=\"text-3xl font-bold tracking-tight\">{route['page']}</h1>\n"
                f"      <p className=\"mt-3 max-w-xl text-stone-600\">{copy['short']}</p>\n"
                f"    </section>\n"
                f"  )\n"
                f"}}\n"
            )
        files.append(GeneratedFile(path=f"src/pages/{comp}.tsx", content=body))

    return list({f.path: f for f in files}.values())


def _brand_copy(brand: str, prompt: str, *, luxury: bool) -> dict[str, str]:
    if luxury:
        return {
            "eyebrow": "Luxury footwear house",
            "headline": "Crafted for presence.",
            "short": f"{brand} designs refined footwear with quiet luxury — form, material, and finish.",
            "about": (
                f"{brand} is a luxury shoe brand built around craftsmanship and calm confidence. "
                "Every silhouette is refined for people who want elevated everyday footwear — "
                "not loud logos, not disposable trends."
            ),
            "cta_primary": "Discover the house",
            "cta_secondary": "Get in touch",
        }
    # Pull a short user phrase if they described the brand beyond page lists
    cleaned = re.sub(
        r"(?i)\b(i want to create|website|page|pages|home|about|contact|ui|ux|reference|proper)\b",
        " ",
        prompt,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,")
    short = (
        f"{brand} — a modern shoe brand focused on comfort, style, and clear design."
        if len(cleaned) < 20
        else f"{brand} — {cleaned[:140].rstrip(' .,')}."
    )
    return {
        "eyebrow": "Shoe brand",
        "headline": "Step with intention.",
        "short": short,
        "about": (
            f"{brand} builds footwear for everyday movement — considered design, "
            "honest materials, and a brand experience that feels clear on every screen."
        ),
        "cta_primary": "About the brand",
        "cta_secondary": "Contact",
    }


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("`", "\\`")


def _use_theme() -> GeneratedFile:
    return GeneratedFile(
        path="src/hooks/useTheme.ts",
        content=(
            "import { useEffect, useState } from 'react'\n"
            "export function useTheme() {\n"
            "  const [dark] = useState(false)\n"
            "  useEffect(() => { document.documentElement.classList.toggle('dark', dark) }, [dark])\n"
            "  return { dark }\n"
            "}\n"
        ),
    )


def _button(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Button.tsx",
        content=(
            "type ButtonProps = { children: React.ReactNode; variant?: 'primary' | 'ghost'; href?: string; className?: string }\n"
            "export function Button({ children, variant = 'primary', href = '#', className = '' }: ButtonProps) {\n"
            "  const base = 'inline-flex items-center justify-center rounded-full px-5 py-2.5 text-sm font-semibold transition '\n"
            "  const styles = variant === 'primary' ? 'text-stone-950' : 'border border-white/35 bg-white/10 text-white'\n"
            f"  const style = variant === 'primary' ? {{ backgroundColor: '{primary}' }} : undefined\n"
            "  return <a href={href} className={base + styles + ' ' + className} style={style}>{children}</a>\n"
            "}\n"
        ),
    )


def _header(brand: str, plan: ProjectPlan, primary: str, *, has_shop: bool) -> GeneratedFile:
    links = ",\n".join(f'  {{ to: "{r["path"]}", label: "{r["page"]}" }}' for r in plan.routes)
    bag = (
        "          <button type=\"button\" className=\"rounded-full p-2 hover:bg-stone-100\" aria-label=\"Bag\"><ShoppingBag className=\"h-5 w-5\" /></button>\n"
        if has_shop
        else ""
    )
    search = (
        "          <button type=\"button\" className=\"rounded-full p-2 hover:bg-stone-100\" aria-label=\"Search\"><Search className=\"h-5 w-5\" /></button>\n"
        if has_shop
        else ""
    )
    icons_import = "Menu, X" + (", Search, ShoppingBag" if has_shop else "")
    return GeneratedFile(
        path="src/components/ShoeHeader.tsx",
        content=(
            "import { useState } from 'react'\n"
            "import { Link, NavLink } from 'react-router-dom'\n"
            f"import {{ {icons_import} }} from 'lucide-react'\n\n"
            f"const links = [\n{links}\n]\n\n"
            "export function ShoeHeader() {\n"
            "  const [open, setOpen] = useState(false)\n"
            "  return (\n"
            "    <header className=\"sticky top-0 z-50 border-b border-stone-200/80 bg-[#FAFAF8]/95 backdrop-blur\">\n"
            "      <div className=\"mx-auto flex h-16 max-w-6xl items-center gap-4 px-4 sm:px-6\">\n"
            f"        <Link to=\"/\" className=\"text-lg font-semibold tracking-[0.14em] uppercase\" style={{{{ color: '{primary}' }}}}>{brand}</Link>\n"
            "        <nav className=\"ml-auto hidden gap-7 text-[11px] font-medium uppercase tracking-[0.18em] md:flex\">\n"
            "          {links.map((l) => (\n"
            "            <NavLink key={l.to} to={l.to} className={({ isActive }) => isActive ? 'text-stone-950' : 'text-stone-500 hover:text-stone-950'}>{l.label}</NavLink>\n"
            "          ))}\n"
            "        </nav>\n"
            "        <div className=\"flex items-center gap-1 md:ml-2\">\n"
            f"{search}{bag}"
            "          <button type=\"button\" className=\"rounded-full p-2 hover:bg-stone-100 md:hidden\" onClick={() => setOpen(v => !v)} aria-label=\"Menu\">{open ? <X className=\"h-5 w-5\" /> : <Menu className=\"h-5 w-5\" />}</button>\n"
            "        </div>\n"
            "      </div>\n"
            "      {open && (\n"
            "        <div className=\"grid gap-1 border-t border-stone-200 px-4 py-3 md:hidden\">\n"
            "          {links.map((l) => <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)} className=\"py-2 text-sm font-medium uppercase tracking-wider\">{l.label}</NavLink>)}\n"
            "        </div>\n"
            "      )}\n"
            "    </header>\n"
            "  )\n"
            "}\n"
        ),
    )


def _hero(
    brand: str,
    primary: str,
    copy: dict[str, str],
    *,
    has_shop: bool,
    has_about: bool,
    has_contact: bool,
) -> GeneratedFile:
    img = SHOE_IMGS[0]
    primary_href = "#/shop" if has_shop else ("#/about" if has_about else "#/contact")
    secondary_href = "#/lookbook" if has_shop else ("#/contact" if has_contact else "#/about")
    primary_label = "Shop collection" if has_shop else _esc(copy["cta_primary"])
    secondary_label = "View lookbook" if has_shop else _esc(copy["cta_secondary"])
    return GeneratedFile(
        path="src/components/ShoeHero.tsx",
        content=(
            "import { Button } from './Button'\n\n"
            "export function ShoeHero() {\n"
            "  return (\n"
            "    <section className=\"relative isolate overflow-hidden bg-stone-950 text-white\">\n"
            f"      <div className=\"absolute inset-0\" style={{{{ backgroundImage: `url('{img}')`, backgroundSize: 'cover', backgroundPosition: 'center' }}}} />\n"
            "      <div className=\"absolute inset-0 bg-gradient-to-r from-stone-950 via-stone-950/80 to-stone-950/30\" />\n"
            "      <div className=\"relative mx-auto flex min-h-[72vh] max-w-6xl flex-col justify-end px-4 pb-16 pt-28 sm:px-6 md:pb-20\">\n"
            f"        <p className=\"text-[11px] font-semibold uppercase tracking-[0.35em]\" style={{{{ color: '{primary}' }}}}>{_esc(copy['eyebrow'])}</p>\n"
            f"        <h1 className=\"mt-4 max-w-2xl font-serif text-4xl leading-[1.08] tracking-tight sm:text-5xl md:text-6xl\">{_esc(copy['headline'])}</h1>\n"
            f"        <p className=\"mt-5 max-w-lg text-sm leading-relaxed text-stone-300 sm:text-base\">{_esc(copy['short'])}</p>\n"
            "        <div className=\"mt-9 flex flex-wrap gap-3\">\n"
            f"          <Button href=\"{primary_href}\">{primary_label}</Button>\n"
            f"          <Button href=\"{secondary_href}\" variant=\"ghost\">{secondary_label}</Button>\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _story(brand: str, copy: dict[str, str], primary: str) -> GeneratedFile:
    img = SHOE_IMGS[1]
    return GeneratedFile(
        path="src/components/ShoeStory.tsx",
        content=(
            "export function ShoeStory() {\n"
            "  return (\n"
            "    <section className=\"mx-auto grid max-w-6xl gap-10 px-4 py-16 sm:px-6 md:grid-cols-2 md:items-center\">\n"
            "      <div>\n"
            f"        <p className=\"text-[11px] font-semibold uppercase tracking-[0.28em]\" style={{{{ color: '{primary}' }}}}>The brand</p>\n"
            f"        <h2 className=\"mt-3 font-serif text-3xl tracking-tight text-stone-950 sm:text-4xl\">{brand}</h2>\n"
            f"        <p className=\"mt-5 text-base leading-relaxed text-stone-600\">{_esc(copy['about'])}</p>\n"
            "      </div>\n"
            f"      <img src=\"{img}\" alt=\"\" className=\"h-80 w-full rounded-3xl object-cover shadow-lg\" loading=\"lazy\" />\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _pillars(brand: str, *, luxury: bool) -> GeneratedFile:
    items = (
        [
            ("Material", "Premium leathers and quiet hardware."),
            ("Silhouette", "Clean lines made for lasting wear."),
            ("Finish", "Hand-finished details, not mass noise."),
            ("Experience", "A calm brand site — clear pages, clear story."),
        ]
        if luxury
        else [
            ("Comfort", "Built for long days and real movement."),
            ("Design", "Modern shapes with a clean UI language."),
            ("Quality", "Honest materials and careful construction."),
            ("Clarity", "A brand website that stays easy to use."),
        ]
    )
    rows = ",\n".join(f'  {{ title: "{t}", body: "{b}" }}' for t, b in items)
    return GeneratedFile(
        path="src/components/ShoePillars.tsx",
        content=(
            f"const items = [\n{rows}\n]\n"
            "export function ShoePillars() {\n"
            "  return (\n"
            "    <section className=\"border-y border-stone-200 bg-white\">\n"
            "      <div className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
            f"        <h2 className=\"font-serif text-3xl tracking-tight\">Why {brand}</h2>\n"
            "        <div className=\"mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4\">\n"
            "          {items.map((item) => (\n"
            "            <div key={item.title} className=\"rounded-2xl border border-stone-200 bg-[#FAFAF8] p-5\">\n"
            "              <h3 className=\"text-sm font-semibold uppercase tracking-wider\">{item.title}</h3>\n"
            "              <p className=\"mt-2 text-sm leading-relaxed text-stone-600\">{item.body}</p>\n"
            "            </div>\n"
            "          ))}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _categories() -> GeneratedFile:
    cats = [
        ("Sneakers", SHOE_IMGS[1]),
        ("Running", SHOE_IMGS[3]),
        ("Formals", SHOE_IMGS[2]),
        ("Boots", SHOE_IMGS[4]),
    ]
    rows = ",\n".join(f'  {{ name: "{n}", img: "{i}" }}' for n, i in cats)
    return GeneratedFile(
        path="src/components/ShoeCategories.tsx",
        content=(
            f"const cats = [\n{rows}\n]\n"
            "export function ShoeCategories() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
            "      <h2 className=\"font-serif text-3xl tracking-tight\">Shop by category</h2>\n"
            "      <div className=\"mt-8 grid grid-cols-2 gap-4 md:grid-cols-4\">\n"
            "        {cats.map((c) => (\n"
            "          <a key={c.name} href=\"#/shop\" className=\"group overflow-hidden rounded-2xl border border-stone-200 bg-white\">\n"
            "            <img src={c.img} alt={c.name} className=\"h-40 w-full object-cover transition group-hover:scale-105\" loading=\"lazy\" />\n"
            "            <div className=\"p-4 text-sm font-semibold uppercase tracking-wider\">{c.name}</div>\n"
            "          </a>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _product_grid(brand: str, primary: str, copy: dict[str, str]) -> GeneratedFile:
    # Brand-owned names only when a Shop page was requested — not a fake Nike catalog
    products = [
        (f"{brand} Runner", "Running"),
        (f"{brand} City", "Casual"),
        (f"{brand} Oxford", "Formal"),
        (f"{brand} Trail", "Boots"),
        (f"{brand} Court", "Sneakers"),
        (f"{brand} Soft", "Everyday"),
    ]
    rows = []
    for i, (name, cat) in enumerate(products):
        rows.append(
            f'  {{ name: "{name}", cat: "{cat}", img: "{SHOE_IMGS[i % len(SHOE_IMGS)]}" }}'
        )
    return GeneratedFile(
        path="src/components/ShoeGrid.tsx",
        content=(
            f"const products = [\n" + ",\n".join(rows) + "\n]\n\n"
            "export function ShoeGrid({ title = 'Collection', limit }: { title?: string; limit?: number }) {\n"
            "  const items = typeof limit === 'number' ? products.slice(0, limit) : products\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
            "      <h2 className=\"font-serif text-3xl tracking-tight\">{title}</h2>\n"
            f"      <p className=\"mt-2 max-w-xl text-sm text-stone-600\">{_esc(copy['short'])}</p>\n"
            "      <div className=\"mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3\">\n"
            "        {items.map((p) => (\n"
            "          <article key={p.name} className=\"overflow-hidden rounded-2xl border border-stone-200 bg-white transition hover:-translate-y-1 hover:shadow-lg\">\n"
            "            <img src={p.img} alt={p.name} className=\"aspect-[4/3] w-full object-cover\" loading=\"lazy\" />\n"
            "            <div className=\"p-4\">\n"
            "              <p className=\"text-[10px] uppercase tracking-wider text-stone-500\">{p.cat}</p>\n"
            "              <h3 className=\"mt-1 font-medium\">{p.name}</h3>\n"
            f"              <button type=\"button\" className=\"mt-4 w-full rounded-full py-2.5 text-[11px] font-semibold uppercase tracking-wider text-stone-950\" style={{{{ backgroundColor: '{primary}' }}}}>Enquire</button>\n"
            "            </div>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _lookbook() -> GeneratedFile:
    rows = ",\n".join(f'  "{u}"' for u in SHOE_IMGS[:4])
    return GeneratedFile(
        path="src/components/ShoeLookbook.tsx",
        content=(
            f"const shots = [\n{rows}\n]\n"
            "export function ShoeLookbook() {\n"
            "  return (\n"
            "    <section className=\"bg-stone-100\">\n"
            "      <div className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
            "        <h2 className=\"font-serif text-3xl tracking-tight\">Lookbook</h2>\n"
            "        <div className=\"mt-8 grid gap-4 sm:grid-cols-2\">\n"
            "          {shots.map((src, i) => (\n"
            "            <img key={src} src={src} alt={`Look ${i + 1}`} className=\"h-72 w-full rounded-2xl object-cover\" loading=\"lazy\" />\n"
            "          ))}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _newsletter(primary: str, brand: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ShoeNewsletter.tsx",
        content=(
            "export function ShoeNewsletter() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-10 sm:px-6\">\n"
            "      <div className=\"rounded-3xl bg-stone-950 px-8 py-10 text-white\">\n"
            f"        <h2 className=\"font-serif text-3xl\">{brand} notes</h2>\n"
            "        <p className=\"mt-2 text-stone-300\">Season drops and private fittings — email only.</p>\n"
            "        <form className=\"mt-6 flex max-w-lg flex-col gap-3 sm:flex-row\" onSubmit={(e) => e.preventDefault()}>\n"
            "          <input type=\"email\" placeholder=\"Email address\" className=\"flex-1 rounded-full px-4 py-3 text-sm text-stone-900\" />\n"
            f"          <button type=\"submit\" className=\"rounded-full px-5 py-3 text-sm font-semibold text-stone-950\" style={{{{ backgroundColor: '{primary}' }}}}>Subscribe</button>\n"
            "        </form>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _contact_block(brand: str, primary: str, copy: dict[str, str]) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ShoeContact.tsx",
        content=(
            "export function ShoeContact() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
            "      <h2 className=\"font-serif text-3xl tracking-tight\">Contact</h2>\n"
            f"      <p className=\"mt-3 max-w-xl text-stone-600\">{_esc(copy['short'])}</p>\n"
            f"      <p className=\"mt-4 text-sm text-stone-500\">Concierge for {brand} — reply within one business day.</p>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _footer(brand: str, plan: ProjectPlan) -> GeneratedFile:
    link_js = ",\n".join(f'  {{ to: "{r["path"]}", label: "{r["page"]}" }}' for r in plan.routes)
    return GeneratedFile(
        path="src/components/ShoeFooter.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n\n"
            f"const links = [\n{link_js}\n]\n\n"
            "export function ShoeFooter() {\n"
            "  return (\n"
            "    <footer className=\"border-t border-stone-800 bg-stone-950 text-stone-400\">\n"
            "      <div className=\"mx-auto flex max-w-6xl flex-col gap-4 px-4 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-6\">\n"
            f"        <p className=\"text-sm text-white tracking-[0.2em] uppercase\">{brand}</p>\n"
            "        <div className=\"flex flex-wrap gap-4 text-xs uppercase tracking-wider\">\n"
            "          {links.map((l) => <Link key={l.to} to={l.to} className=\"hover:text-white\">{l.label}</Link>)}\n"
            "        </div>\n"
            "      </div>\n"
            f"      <div className=\"border-t border-stone-800 px-4 py-4 text-center text-xs\">© {{new Date().getFullYear()}} {brand}</div>\n"
            "    </footer>\n"
            "  )\n"
            "}\n"
        ),
    )


def _home(
    brand: str,
    primary: str,
    copy: dict[str, str],
    *,
    has_shop: bool,
    has_lookbook: bool,
    has_about: bool,
    has_contact: bool,
) -> str:
    imports = [
        "import { ShoeHero } from '../components/ShoeHero'",
        "import { ShoeStory } from '../components/ShoeStory'",
        "import { ShoePillars } from '../components/ShoePillars'",
    ]
    body = ["      <ShoeHero />", "      <ShoeStory />", "      <ShoePillars />"]
    if has_shop:
        imports.extend(
            [
                "import { ShoeCategories } from '../components/ShoeCategories'",
                "import { ShoeGrid } from '../components/ShoeGrid'",
                "import { ShoeNewsletter } from '../components/ShoeNewsletter'",
            ]
        )
        body.extend(
            [
                "      <ShoeCategories />",
                "      <ShoeGrid limit={6} />",
                "      <ShoeNewsletter />",
            ]
        )
    if has_lookbook:
        imports.append("import { ShoeLookbook } from '../components/ShoeLookbook'")
        body.append("      <ShoeLookbook />")
    if has_contact and not has_shop:
        imports.append("import { Link } from 'react-router-dom'")
        body.append(
            "      <section className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">"
            "<div className=\"rounded-3xl bg-stone-950 px-8 py-10 text-white\">"
            f"<h2 className=\"font-serif text-3xl\">Talk to {brand}</h2>"
            f"<p className=\"mt-2 max-w-md text-stone-300\">{_esc(copy['short'])}</p>"
            "<Link to=\"/contact\" className=\"mt-6 inline-flex rounded-full bg-white px-5 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-stone-950\">Contact</Link>"
            "</div></section>"
        )
    return (
        "\n".join(imports)
        + "\n\nexport default function HomePage() {\n"
        "  return (\n"
        "    <div className=\"overflow-x-hidden bg-[#FAFAF8] text-stone-900\">\n"
        + "\n".join(body)
        + "\n    </div>\n  )\n}\n"
    )


def _shop_page(comp: str, brand: str) -> str:
    return (
        "import { ShoeGrid } from '../components/ShoeGrid'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"overflow-x-hidden bg-[#FAFAF8]\">\n"
        f"      <ShoeGrid title=\"{brand} collection\" />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _lookbook_page(comp: str) -> str:
    return (
        "import { ShoeLookbook } from '../components/ShoeLookbook'\n\n"
        f"export default function {comp}() {{\n"
        "  return <div className=\"overflow-x-hidden bg-[#FAFAF8]\"><ShoeLookbook /></div>\n"
        "}\n"
    )


def _about_page(comp: str, brand: str, copy: dict[str, str], primary: str) -> str:
    return (
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <section className=\"mx-auto max-w-3xl overflow-x-hidden px-4 py-16 sm:px-6\">\n"
        f"      <p className=\"text-[11px] font-semibold uppercase tracking-[0.28em]\" style={{{{ color: '{primary}' }}}}>{brand}</p>\n"
        f"      <h1 className=\"mt-3 font-serif text-4xl tracking-tight\">About</h1>\n"
        f"      <p className=\"mt-6 text-lg leading-relaxed text-stone-600\">{_esc(copy['about'])}</p>\n"
        "    </section>\n"
        "  )\n"
        "}\n"
    )


def _contact_page(comp: str, brand: str, primary: str, copy: dict[str, str]) -> str:
    return (
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"overflow-x-hidden bg-[#FAFAF8]\">\n"
        "      <section className=\"mx-auto max-w-xl px-4 py-14 sm:px-6\">\n"
        "        <h1 className=\"font-serif text-4xl tracking-tight\">Contact</h1>\n"
        f"        <p className=\"mt-3 text-stone-600\">{_esc(copy['short'])}</p>\n"
        "        <form className=\"mt-8 grid gap-3 rounded-2xl border border-stone-200 bg-white p-6\" onSubmit={(e) => e.preventDefault()}>\n"
        "          <input className=\"rounded-xl border border-stone-300 px-3 py-2.5 text-sm\" placeholder=\"Name\" required />\n"
        "          <input type=\"email\" className=\"rounded-xl border border-stone-300 px-3 py-2.5 text-sm\" placeholder=\"Email\" required />\n"
        "          <textarea className=\"min-h-28 rounded-xl border border-stone-300 px-3 py-2.5 text-sm\" placeholder=\"Message\" required />\n"
        f"          <button type=\"submit\" className=\"rounded-full px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-stone-950\" style={{{{ backgroundColor: '{primary}' }}}}>Send message</button>\n"
        "        </form>\n"
        f"        <p className=\"mt-6 text-xs text-stone-500\">Messages reach the {brand} team directly.</p>\n"
        "      </section>\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )

"""Luxury fashion clothing brand generator — apparel only, never footwear."""

from __future__ import annotations

import json
import re

from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements

# Editorial fashion photography (clothing / models — no footwear product shots)
FASHION_IMGS = [
    "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1600&q=80",
    "https://images.unsplash.com/photo-1469334031218-e382a71b716b?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?auto=format&fit=crop&w=800&q=80",
]

DEFAULT_PRODUCTS = [
    ("Oversized Essential Tee", "Oversized T-Shirts", 48, "Unisex"),
    ("Studio Graphic Tee", "Graphic T-Shirts", 52, "Unisex"),
    ("Piqué Polo", "Polo Shirts", 68, "Men"),
    ("Soft Casual Shirt", "Casual Shirts", 78, "Men"),
    ("Poplin Formal Shirt", "Formal Shirts", 88, "Men"),
    ("Heavyweight Hoodie", "Hoodies", 118, "Unisex"),
    ("Brushed Sweatshirt", "Sweatshirts", 98, "Unisex"),
    ("Tailored Wool Jacket", "Jackets", 240, "Unisex"),
    ("Single-Breasted Blazer", "Blazers", 260, "Unisex"),
    ("Relaxed Cargo Pant", "Cargo Pants", 110, "Unisex"),
    ("Straight Indigo Jean", "Jeans", 128, "Unisex"),
    ("Pleated Trouser", "Trousers", 120, "Unisex"),
    ("Tailored Short", "Shorts", 72, "Unisex"),
    ("Column Midi Dress", "Dresses", 148, "Women"),
    ("A-Line Skirt", "Skirts", 96, "Women"),
    ("Linen Co-ord Set", "Co-ord Sets", 168, "Women"),
    ("Merino Knit", "Knitwear", 132, "Unisex"),
    ("Leather Belt", "Belts", 58, "Unisex"),
    ("Structured Cap", "Caps", 42, "Unisex"),
    ("Soft Leather Tote", "Bags", 190, "Women"),
]

SHOE_BLOCK = re.compile(
    r"\b(shoe|shoes|sneaker|sneakers|boot|boots|sandal|sandals|footwear|loafer|running shoe|football shoe)\b",
    re.I,
)

# Curated accent palettes so different brands actually look different — the
# logo, navbar, hero and footer all derive their accent color from here
# instead of a single hardcoded gold, which previously made every generated
# clothing-brand site look visually identical regardless of brand name.
PALETTES = [
    {"name": "gold",      "from": "#C6A75E", "via": "#E8D5A3", "to": "#8B7355", "accent": "#C6A75E"},
    {"name": "rose",      "from": "#C98A9C", "via": "#E8C4CE", "to": "#8C5A6B", "accent": "#C98A9C"},
    {"name": "emerald",   "from": "#3E8E77", "via": "#8FCBB6", "to": "#1E4A3D", "accent": "#3E8E77"},
    {"name": "midnight",  "from": "#4C6E9C", "via": "#8EA8CE", "to": "#1F324D", "accent": "#4C6E9C"},
    {"name": "terracotta","from": "#C77D2E", "via": "#E5A85E", "to": "#7A4419", "accent": "#C77D2E"},
    {"name": "plum",      "from": "#8C5A87", "via": "#C08BB8", "to": "#4A2A49", "accent": "#8C5A87"},
    {"name": "charcoal",  "from": "#5A5A5A", "via": "#8A8A8A", "to": "#2A2A2A", "accent": "#5A5A5A"},
    {"name": "ocean",     "from": "#2C8C8F", "via": "#6FC1C3", "to": "#123F42", "accent": "#2C8C8F"},
]

_COLOR_WORD_MAP = {
    "gold": "gold", "luxury": "gold", "champagne": "gold",
    "rose": "rose", "pink": "rose", "blush": "rose",
    "green": "emerald", "emerald": "emerald", "olive": "emerald",
    "blue": "midnight", "navy": "midnight", "midnight": "midnight",
    "earth": "terracotta", "terracotta": "terracotta", "brown": "terracotta",
    "orange": "terracotta", "rust": "terracotta", "amber": "terracotta",
    "purple": "plum", "plum": "plum", "berry": "plum", "wine": "plum", "violet": "plum",
    "black and white": "charcoal", "monochrome": "charcoal", "grayscale": "charcoal",
    "greyscale": "charcoal", "minimal": "charcoal", "gray": "charcoal", "grey": "charcoal",
    "teal": "ocean", "ocean": "ocean", "turquoise": "ocean", "cyan": "ocean",
}


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _pick_palette(brand: str, prompt: str) -> dict:
    """Pick an accent palette for this brand — honors an explicit color
    mention in the prompt first, otherwise derives a deterministic (but
    varied) choice from the brand name so the same brand always regenerates
    the same look, while different brands get visibly different results."""
    lowered = (prompt or "").lower()
    for word, palette_name in _COLOR_WORD_MAP.items():
        if word in lowered:
            return next(p for p in PALETTES if p["name"] == palette_name)
    seed = sum(ord(c) for c in (brand or "brand")) or 1
    return PALETTES[seed % len(PALETTES)]


def generate_luxury_fashion(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    analysis = requirements.analysis
    brand = _clean_brand(
        getattr(analysis, "brand_name", "") or plan.project_name or "",
        analysis.raw_prompt or "",
    )
    if not brand or brand.lower() in {"fashion brand", "clothing store", "blog / magazine"}:
        # Prefer explicit shop name from prompt ("my shop name is X" phrasing)
        m = re.search(
            r"(?:(?:cloth|clothing|fashion)\s+)?(?:shop|store|brand)\s+name\s+is\s+"
            r"([A-Za-z][A-Za-z0-9&''.-]*(?:\s+[A-Za-z][A-Za-z0-9&''.-]*){0,3})",
            analysis.raw_prompt or "",
            flags=re.I,
        )
        local_extract = _clean_brand(m.group(1) if m else "", analysis.raw_prompt or "")
        # Fall back to the shared analyzer's brand_name (handles other
        # phrasings like called "X") before resorting to a generic default —
        # never distrust a real extraction just because it needs a fallback.
        brand = local_extract or (getattr(analysis, "brand_name", "") or "").strip() or "Studio Label"

    products = _products_from_prompt(analysis.raw_prompt) or [
        {
            "id": f"p{i+1}",
            "name": name,
            "category": cat,
            "price": price,
            "gender": gender,
            "sizes": ["XS", "S", "M", "L", "XL"],
            "colors": ["Black", "Ivory", "Sand", "Navy"],
            "rating": round(4.4 + (i % 5) * 0.1, 1),
            "image": FASHION_IMGS[(i + 4) % len(FASHION_IMGS)],
            "badge": ["New", "Best Seller", "Limited", ""][i % 4],
        }
        for i, (name, cat, price, gender) in enumerate(DEFAULT_PRODUCTS)
    ]

    # Absolute ban on footwear products
    products = [p for p in products if not SHOE_BLOCK.search(f"{p['name']} {p['category']}")]

    tagline = f"{brand} — branded clothing with editorial polish and everyday ease."
    if "young" in (analysis.raw_prompt or "").lower():
        tagline = f"Modern branded fashion from {brand} — built for style that moves."

    headline = _hero_headline(brand, analysis.raw_prompt or "")
    monogram = "".join(w[0] for w in brand.split()[:2]).upper() or "VC"
    palette = _pick_palette(brand, analysis.raw_prompt or "")
    hero_img = FASHION_IMGS[(sum(ord(c) for c in brand) + 1) % min(4, len(FASHION_IMGS))]

    catalog_json = json.dumps(products, indent=2)
    files: list[GeneratedFile] = [
        GeneratedFile(
            path="src/data/catalog.ts",
            content=(
                "export type Product = {\n"
                "  id: string\n  name: string\n  category: string\n  price: number\n  gender: string\n"
                "  sizes: string[]\n  colors: string[]\n  rating: number\n  image: string\n  badge?: string\n"
                "}\n\n"
                f"export const brandName = {json.dumps(brand)}\n"
                f"export const brandMonogram = {json.dumps(monogram)}\n"
                f"export const brandTagline = {json.dumps(tagline)}\n"
                f"export const brandHeadline = {json.dumps(headline)}\n"
                f"export const heroImage = {json.dumps(hero_img)}\n"
                f"export const products: Product[] = {catalog_json}\n\n"
                "export function filterProducts(opts: { gender?: string; category?: string; q?: string }) {\n"
                "  return products.filter((p) => {\n"
                "    if (opts.gender && opts.gender !== 'all' && p.gender !== 'Unisex' && p.gender !== opts.gender) return false\n"
                "    if (opts.category && opts.category !== 'all' && p.category !== opts.category) return false\n"
                "    if (opts.q && !`${p.name} ${p.category}`.toLowerCase().includes(opts.q.toLowerCase())) return false\n"
                "    return true\n"
                "  })\n"
                "}\n"
            ),
        ),
        _theme_hook(),
        _button(),
        _logo(palette),
        _navbar(brand, plan, palette),
        _hero(brand, tagline, palette, hero_img, headline),
        _product_card(),
        _product_grid(),
        _section_blocks(brand),
        _footer(brand, palette),
        _auth_pages(brand, palette),
        GeneratedFile(path="src/components/Navbar.tsx", content="export { StoreNavbar as Navbar } from './StoreNavbar'\n"),
        GeneratedFile(path="src/components/Hero.tsx", content="export { FashionHero as Hero } from './FashionHero'\n"),
        GeneratedFile(path="src/components/Footer.tsx", content="export { StoreFooter as Footer } from './StoreFooter'\n"),
        GeneratedFile(path="src/components/Button.tsx", content="export { StoreButton as Button } from './StoreButton'\n"),
        GeneratedFile(
            path="src/components/Card.tsx",
            content=(
                "import type { ReactNode } from 'react'\n"
                "export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {\n"
                "  return <div className={`rounded-2xl border border-stone-200 bg-white ${className}`}>{children}</div>\n"
                "}\n"
            ),
        ),
    ]

    want_auth = any(
        k in (analysis.raw_prompt or "").lower()
        for k in ("sign in", "sign up", "login", "register", "email", "phone")
    )

    for route in plan.routes:
        page = route["page"].lower()
        comp = route["component"]
        if route["path"] == "/":
            body = _home_page(comp, brand)
        elif page in {"login", "sign in", "signin"}:
            body = _login_page(comp, brand)
        elif page in {"register", "sign up", "signup"}:
            body = _register_page(comp, brand)
        elif "shop" in page or "arrival" in page or page in {"men", "women", "collections", "new arrivals"}:
            gender = "Men" if page == "men" else "Women" if page == "women" else "all"
            body = _shop_page(comp, brand, gender=gender, title=route["page"], palette=palette)
        elif "lookbook" in page:
            body = _lookbook_page(comp, brand, palette)
        elif "about" in page:
            body = _about_page(comp, brand, palette)
        elif "contact" in page:
            body = _contact_page(comp, brand)
        else:
            body = _shop_page(comp, brand, gender="all", title=route["page"], palette=palette)
        files.append(GeneratedFile(path=f"src/pages/{comp}.tsx", content=body))

    # Ensure auth pages exist even if planner missed them
    if want_auth:
        by = {f.path: f for f in files}
        if "src/pages/LoginPage.tsx" not in by:
            files.append(GeneratedFile(path="src/pages/LoginPage.tsx", content=_login_page("LoginPage", brand)))
        if "src/pages/RegisterPage.tsx" not in by:
            files.append(GeneratedFile(path="src/pages/RegisterPage.tsx", content=_register_page("RegisterPage", brand)))

    return list({f.path: f for f in files}.values())


def _clean_brand(raw: str, prompt: str = "") -> str:
    name = re.sub(r"\s+", " ", (raw or "")).strip(" .,!?'\"")
    name = re.split(
        r"\b(?:so|please|and|with|that|also|give|create|make|build|for|to|"
        r"website|site|responsive|logo|attractive|customer|sign|easy|collection|"
        r"branding|3d|view)\b",
        name,
        maxsplit=1,
        flags=re.I,
    )[0].strip(" .,!?'\"-")
    parts = name.split()
    if len(parts) > 4:
        name = " ".join(parts[:4])
    if len(name) < 2 or len(name) > 40:
        return ""
    if re.search(r"\b(create|responsive|website|give me)\b", name, flags=re.I):
        return ""
    # Fallback from prompt if needed
    if not name and prompt:
        m = re.search(
            r"(?:shop|store|brand)\s+name\s+is\s+([A-Za-z][A-Za-z0-9&''.-]*(?:\s+[A-Za-z][A-Za-z0-9&''.-]*){0,3})",
            prompt,
            flags=re.I,
        )
        if m:
            return _clean_brand(m.group(1), "")
    return name.title() if name.islower() else name


def _products_from_prompt(prompt: str) -> list[dict] | None:
    if not prompt:
        return None
    # Capture bullet list under Products should include
    m = re.search(r"(?is)products should include only\s*:?\s*(.+?)(?:\n\s*\n|every product|features\s*:|design inspiration|avoid\s*:)", prompt)
    if not m:
        return None
    block = m.group(1)
    names = re.findall(r"[-*•]\s*([A-Za-z][A-Za-z0-9 &\-']{2,60})", block)
    if len(names) < 4:
        names = [n.strip() for n in re.split(r"[\n,]", block) if 2 < len(n.strip()) < 60]
    out = []
    for i, name in enumerate(names[:24]):
        if SHOE_BLOCK.search(name):
            continue
        clean = name.strip()
        price = 49 + (i * 7) % 160
        low = clean.lower()
        gender = "Women" if any(w in low for w in ("dress", "skirt", "women")) else (
            "Men" if any(w in low for w in ("polo", "formal shirt", "men")) else "Unisex"
        )
        category = _category_for_product(clean)
        out.append(
            {
                "id": f"p{i+1}",
                "name": clean,
                "category": category,
                "price": price,
                "gender": gender,
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colors": ["Black", "White", "Beige", "Cream", "Gold"],
                "rating": round(4.5 + (i % 4) * 0.1, 1),
                "image": FASHION_IMGS[(i + 4) % len(FASHION_IMGS)],
                "badge": ["New", "Best Seller", "Limited", ""][i % 4],
            }
        )
    return out or None


def _category_for_product(name: str) -> str:
    low = name.lower()
    mapping = (
        ("t-shirt", "T-Shirts"),
        ("tee", "T-Shirts"),
        ("hoodie", "Hoodies"),
        ("sweatshirt", "Sweatshirts"),
        ("jean", "Jeans"),
        ("dress", "Dresses"),
        ("blazer", "Blazers"),
        ("jacket", "Jackets"),
        ("skirt", "Skirts"),
        ("trouser", "Trousers"),
        ("pant", "Pants"),
        ("short", "Shorts"),
        ("knit", "Knitwear"),
        ("shirt", "Shirts"),
        ("polo", "Polo Shirts"),
        ("co-ord", "Co-ord Sets"),
        ("coord", "Co-ord Sets"),
        ("belt", "Belts"),
        ("cap", "Caps"),
        ("bag", "Bags"),
        ("tote", "Bags"),
    )
    for needle, label in mapping:
        if needle in low:
            return label
    return "Ready-to-wear"


def _theme_hook() -> GeneratedFile:
    return GeneratedFile(
        path="src/hooks/useTheme.ts",
        content=(
            "import { useEffect, useState } from 'react'\n\n"
            "export function useTheme() {\n"
            "  const [dark, setDark] = useState(false)\n"
            "  useEffect(() => {\n"
            "    const saved = localStorage.getItem('atelier-theme')\n"
            "    const next = saved ? saved === 'dark' : false\n"
            "    setDark(next)\n"
            "    document.documentElement.classList.toggle('dark', next)\n"
            "  }, [])\n"
            "  const toggle = () => {\n"
            "    setDark((d) => {\n"
            "      const next = !d\n"
            "      document.documentElement.classList.toggle('dark', next)\n"
            "      localStorage.setItem('atelier-theme', next ? 'dark' : 'light')\n"
            "      return next\n"
            "    })\n"
            "  }\n"
            "  return { dark, toggle }\n"
            "}\n"
        ),
    )


def _button() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/StoreButton.tsx",
        content=(
            "type Props = { children: React.ReactNode; className?: string; onClick?: () => void; type?: 'button' | 'submit' }\n"
            "export function StoreButton({ children, className = '', onClick, type = 'button' }: Props) {\n"
            "  return (\n"
            "    <button type={type} onClick={onClick} className={`inline-flex items-center justify-center rounded-full bg-stone-950 px-5 py-2.5 text-xs font-semibold uppercase tracking-[0.18em] text-white transition hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-950 dark:hover:bg-white ${className}`}>\n"
            "      {children}\n"
            "    </button>\n"
            "  )\n"
            "}\n"
        ),
    )


def _logo(palette: dict) -> GeneratedFile:
    shadow = _hex_to_rgba(palette["accent"], 0.35)
    return GeneratedFile(
        path="src/components/BrandLogo.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n"
            "import { brandMonogram, brandName } from '../data/catalog'\n\n"
            "export function BrandLogo({ compact = false }: { compact?: boolean }) {\n"
            "  return (\n"
            "    <Link to=\"/\" className=\"group flex items-center gap-3 no-underline\">\n"
            f"      <span className=\"flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[{palette['from']}] via-[{palette['via']}] to-[{palette['to']}] text-sm font-bold tracking-wide text-stone-950 shadow-[0_8px_24px_{shadow}] transition group-hover:scale-105\">\n"
            "        {brandMonogram}\n"
            "      </span>\n"
            "      {!compact && (\n"
            "        <span className=\"flex flex-col leading-tight\">\n"
            "          <span className=\"text-sm font-semibold tracking-[0.18em] text-stone-950 uppercase dark:text-stone-50\">{brandName}</span>\n"
            f"          <span className=\"text-[10px] uppercase tracking-[0.28em] text-[{palette['accent']}]\">Est. atelier</span>\n"
            "        </span>\n"
            "      )}\n"
            "    </Link>\n"
            "  )\n"
            "}\n"
        ),
    )


def _auth_pages(brand: str, palette: dict) -> GeneratedFile:
    accent = palette["accent"]
    # Shared form primitives used by Login / Register pages
    return GeneratedFile(
        path="src/components/AuthForm.tsx",
        content=(
            "import { useState, type FormEvent } from 'react'\n"
            "import { Link } from 'react-router-dom'\n"
            "import { BrandLogo } from './BrandLogo'\n\n"
            "type Mode = 'login' | 'register'\n\n"
            f"export function AuthForm({{ mode }}: {{ mode: Mode }}) {{\n"
            "  const [method, setMethod] = useState<'email' | 'phone'>('email')\n"
            "  const [done, setDone] = useState(false)\n"
            "  const isLogin = mode === 'login'\n"
            "  function onSubmit(e: FormEvent) {\n"
            "    e.preventDefault()\n"
            "    setDone(true)\n"
            "  }\n"
            "  return (\n"
            "    <section className=\"mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-16\">\n"
            "      <div className=\"mb-8 flex justify-center\"><BrandLogo /></div>\n"
            "      <div className=\"rounded-3xl border border-stone-200 bg-white p-8 shadow-[0_24px_80px_rgba(0,0,0,0.08)] dark:border-stone-800 dark:bg-stone-900\">\n"
            f"        <p className=\"text-center text-[10px] uppercase tracking-[0.3em] text-[{accent}]\">{brand}</p>\n"
            "        <h1 className=\"mt-2 text-center font-serif text-3xl\">{isLogin ? 'Welcome back' : 'Join the house'}</h1>\n"
            "        <p className=\"mt-2 text-center text-sm text-stone-500\">{isLogin ? 'Sign in with email or phone' : 'Create an account with email or phone'}</p>\n"
            "        <div className=\"mt-6 grid grid-cols-2 gap-2 rounded-full bg-stone-100 p-1 dark:bg-stone-800\">\n"
            "          <button type=\"button\" onClick={() => setMethod('email')} className={`rounded-full py-2 text-xs uppercase tracking-wider ${method === 'email' ? 'bg-white shadow dark:bg-stone-950' : ''}`}>Email</button>\n"
            "          <button type=\"button\" onClick={() => setMethod('phone')} className={`rounded-full py-2 text-xs uppercase tracking-wider ${method === 'phone' ? 'bg-white shadow dark:bg-stone-950' : ''}`}>Phone</button>\n"
            "        </div>\n"
            "        {done ? (\n"
            "          <p className=\"mt-8 text-center text-sm text-emerald-700\">You're in — explore the collection.</p>\n"
            "        ) : (\n"
            "          <form className=\"mt-6 grid gap-3\" onSubmit={onSubmit}>\n"
            "            {!isLogin && <input required className=\"rounded-xl border border-stone-200 px-3 py-3 text-sm dark:border-stone-700 dark:bg-stone-950\" placeholder=\"Full name\" />}\n"
            "            {method === 'email' ? (\n"
            "              <input type=\"email\" required className=\"rounded-xl border border-stone-200 px-3 py-3 text-sm dark:border-stone-700 dark:bg-stone-950\" placeholder=\"Email address\" />\n"
            "            ) : (\n"
            "              <input type=\"tel\" required className=\"rounded-xl border border-stone-200 px-3 py-3 text-sm dark:border-stone-700 dark:bg-stone-950\" placeholder=\"Phone number\" />\n"
            "            )}\n"
            "            <input type=\"password\" required minLength={6} className=\"rounded-xl border border-stone-200 px-3 py-3 text-sm dark:border-stone-700 dark:bg-stone-950\" placeholder=\"Password\" />\n"
            f"            <button type=\"submit\" className=\"mt-2 rounded-full bg-stone-950 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-white dark:bg-[{accent}] dark:text-stone-950\">{{isLogin ? 'Sign in' : 'Create account'}}</button>\n"
            "          </form>\n"
            "        )}\n"
            "        <p className=\"mt-6 text-center text-sm text-stone-500\">\n"
            "          {isLogin ? (\n"
            f"            <>New here? <Link className=\"text-[{accent}] underline\" to=\"/register\">Sign up</Link></>\n"
            "          ) : (\n"
            f"            <>Already a member? <Link className=\"text-[{accent}] underline\" to=\"/login\">Sign in</Link></>\n"
            "          )}\n"
            "        </p>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _navbar(brand: str, plan: ProjectPlan, palette: dict) -> GeneratedFile:
    accent = palette["accent"]
    auth_labels = {"login", "register", "sign in", "sign up", "signin", "signup"}
    links = []
    has_login = False
    has_register = False
    for r in plan.routes:
        label = r["page"]
        low = label.lower()
        if low == "article":
            continue
        if low in auth_labels:
            if "login" in low or low == "sign in":
                has_login = True
            if "register" in low or "sign up" in low or low == "signup":
                has_register = True
            continue
        links.append({"to": r["path"], "label": label})
    for r in plan.routes:
        low = r["page"].lower()
        if low in {"login", "sign in", "signin"}:
            has_login = True
        if low in {"register", "sign up", "signup"}:
            has_register = True
    links_js = json.dumps(links)
    return GeneratedFile(
        path="src/components/StoreNavbar.tsx",
        content=(
            "import { useState } from 'react'\n"
            "import { Link, NavLink } from 'react-router-dom'\n"
            "import { BrandLogo } from './BrandLogo'\n"
            "import { useTheme } from '../hooks/useTheme'\n"
            f"const links = {links_js} as {{ to: string; label: string }}[]\n"
            f"const showLogin = {str(has_login).lower()}\n"
            f"const showRegister = {str(has_register).lower()}\n\n"
            "export function StoreNavbar() {\n"
            "  const [open, setOpen] = useState(false)\n"
            "  const { dark, toggle } = useTheme()\n"
            "  return (\n"
            "    <header className=\"sticky top-0 z-50 border-b border-stone-200/70 bg-[#FAFAF8]/95 backdrop-blur-md dark:border-stone-800 dark:bg-stone-950/95\">\n"
            "      <div className=\"mx-auto flex h-16 max-w-6xl items-center justify-between gap-6 px-4 sm:px-6\">\n"
            "        <BrandLogo />\n"
            "        <nav className=\"hidden items-center gap-8 text-[12px] font-medium uppercase tracking-[0.16em] md:flex\">\n"
            "          {links.map((l) => (\n"
            "            <NavLink key={l.to} to={l.to} className={({ isActive }) =>\n"
            "              `transition ${isActive ? 'text-stone-950 dark:text-white' : 'text-stone-500 hover:text-stone-950 dark:hover:text-white'}`\n"
            "            }>{l.label}</NavLink>\n"
            "          ))}\n"
            "        </nav>\n"
            "        <div className=\"flex items-center gap-2\">\n"
            "          <button type=\"button\" onClick={toggle} className=\"hidden rounded-full border border-stone-200 px-3.5 py-2 text-[11px] uppercase tracking-wider text-stone-600 sm:inline-flex dark:border-stone-700 dark:text-stone-300\">{dark ? 'Light' : 'Dark'}</button>\n"
            "          {showLogin && <Link to=\"/login\" className=\"hidden rounded-full px-3.5 py-2 text-[11px] uppercase tracking-wider text-stone-600 sm:inline-flex dark:text-stone-300\">Sign in</Link>}\n"
            f"          {{showRegister && <Link to=\"/register\" className=\"hidden rounded-full px-4 py-2 text-[11px] uppercase tracking-wider text-stone-950 sm:inline-flex\" style={{{{ backgroundColor: '{accent}' }}}}>Sign up</Link>}}\n"
            "          <Link to=\"/shop\" className=\"rounded-full bg-stone-950 px-5 py-2 text-[11px] font-semibold uppercase tracking-wider text-white transition hover:bg-stone-800 dark:bg-stone-100 dark:text-stone-950 dark:hover:bg-white\">Bag</Link>\n"
            "          <button type=\"button\" className=\"rounded-full border border-stone-200 px-3 py-1.5 text-[10px] uppercase md:hidden dark:border-stone-700\" onClick={() => setOpen(v => !v)}>Menu</button>\n"
            "        </div>\n"
            "      </div>\n"
            "      {open && (\n"
            "        <div className=\"border-t border-stone-200 px-4 py-3 md:hidden dark:border-stone-800\">\n"
            "          <div className=\"flex flex-col gap-1\">\n"
            "            {links.map((l) => <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)} className=\"rounded-lg px-2 py-2.5 text-sm uppercase tracking-wider\">{l.label}</NavLink>)}\n"
            "          </div>\n"
            "        </div>\n"
            "      )}\n"
            "    </header>\n"
            "  )\n"
            "}\n"
        ),
    )


def _hero_headline(brand: str, prompt: str) -> str:
    lowered = prompt.lower()
    if any(k in lowered for k in ("street", "urban", "young", "gen z", "hype")):
        return "Worn loud.\nMade clean."
    if any(k in lowered for k in ("minimal", "quiet", "atelier", "editorial", "luxury")):
        return "New season.\nQuiet luxury."
    if any(k in lowered for k in ("summer", "linen", "resort")):
        return "Light layers.\nLong days."
    seed = sum(ord(c) for c in brand) % 3
    options = [
        "New season.\nQuiet luxury.",
        "Cut sharp.\nFeel easy.",
        f"{brand}.\nEveryday elevated.",
    ]
    return options[seed]


def _hero(brand: str, tagline: str, palette: dict, hero_img: str, headline: str) -> GeneratedFile:
    accent = palette["accent"]
    safe_tag = tagline.replace("'", "\\'")
    _ = headline  # stored in catalog as brandHeadline
    return GeneratedFile(
        path="src/components/FashionHero.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n"
            "import { brandName, brandTagline, brandHeadline, heroImage } from '../data/catalog'\n\n"
            "export function FashionHero() {\n"
            "  const lines = String(brandHeadline || 'New season.\\nQuiet luxury.').split('\\n')\n"
            "  return (\n"
            "    <section className=\"relative isolate overflow-hidden bg-stone-950 text-white\">\n"
            f"      <div className=\"absolute inset-0 scale-105\" style={{{{ backgroundImage: `url(${{heroImage || '{hero_img}'}})`, backgroundSize: 'cover', backgroundPosition: 'center 18%' }}}} />\n"
            "      <div className=\"absolute inset-0 bg-gradient-to-r from-stone-950/95 via-stone-950/55 to-transparent\" />\n"
            "      <div className=\"absolute inset-0 bg-gradient-to-t from-stone-950/70 via-transparent to-stone-950/20\" />\n"
            "      <div className=\"relative mx-auto flex min-h-[76vh] max-w-6xl flex-col justify-end px-4 pb-20 pt-32 sm:px-6 md:min-h-[86vh] md:pb-24\">\n"
            f"        <p className=\"text-[12px] font-semibold uppercase tracking-[0.32em]\" style={{{{ color: '{accent}' }}}}>{{brandName}}</p>\n"
            "        <h1 className=\"mt-5 max-w-3xl font-serif text-4xl leading-[1.05] tracking-tight sm:text-5xl md:text-7xl\">\n"
            "          {lines[0]}\n"
            "          {lines[1] ? <><br />{lines[1]}</> : null}\n"
            "        </h1>\n"
            f"        <p className=\"mt-6 max-w-lg text-[15px] leading-relaxed text-stone-200/90 sm:text-base\">{{brandTagline || '{safe_tag}'}}</p>\n"
            "        <div className=\"mt-10 flex flex-wrap gap-3\">\n"
            "          <Link to=\"/shop\" className=\"rounded-full bg-white px-7 py-3.5 text-[12px] font-semibold uppercase tracking-[0.18em] text-stone-950 transition hover:bg-stone-100\">Shop collection</Link>\n"
            "          <Link to=\"/lookbook\" className=\"rounded-full border border-white/40 px-7 py-3.5 text-[12px] font-semibold uppercase tracking-[0.18em] transition hover:border-white hover:bg-white/10\">View lookbook</Link>\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _product_card() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ProductCard.tsx",
        content=(
            "import { useState } from 'react'\n"
            "import type { Product } from '../data/catalog'\n\n"
            "export function ProductCard({ product }: { product: Product }) {\n"
            "  const [wish, setWish] = useState(false)\n"
            "  const [quick, setQuick] = useState(false)\n"
            "  return (\n"
            "    <article className=\"group flex flex-col\">\n"
            "      <div className=\"relative overflow-hidden rounded-2xl border border-stone-200/80 bg-white shadow-[0_8px_30px_rgba(0,0,0,0.04)] transition duration-300 group-hover:-translate-y-1 group-hover:shadow-[0_18px_40px_rgba(0,0,0,0.1)] dark:border-stone-800 dark:bg-stone-900\">\n"
            "        <div className=\"relative aspect-[3/4] overflow-hidden bg-stone-100 dark:bg-stone-800\">\n"
            "          <img src={product.image} alt={product.name} className=\"h-full w-full object-cover transition duration-700 group-hover:scale-[1.04]\" loading=\"lazy\" />\n"
            "          {product.badge ? <span className=\"absolute left-3 top-3 rounded-full bg-stone-950/90 px-2.5 py-1 text-[10px] uppercase tracking-wider text-white\">{product.badge}</span> : null}\n"
            "          <button type=\"button\" onClick={() => setWish(v => !v)} className=\"absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-white/95 text-sm shadow-sm\" aria-label=\"Wishlist\">{wish ? '♥' : '♡'}</button>\n"
            "          <div className=\"absolute inset-x-3 bottom-3 flex gap-2 opacity-0 transition duration-300 group-hover:opacity-100\">\n"
            "            <button type=\"button\" className=\"flex-1 rounded-full bg-white py-2 text-[10px] font-semibold uppercase tracking-wider text-stone-950\" onClick={() => setQuick(true)}>Quick view</button>\n"
            "            <button type=\"button\" className=\"flex-1 rounded-full bg-stone-950 py-2 text-[10px] font-semibold uppercase tracking-wider text-white\">Add</button>\n"
            "          </div>\n"
            "        </div>\n"
            "        <div className=\"flex flex-col gap-1 p-4\">\n"
            "          <p className=\"text-[10px] uppercase tracking-[0.16em] text-stone-500\">{product.category}</p>\n"
            "          <h3 className=\"text-[15px] font-medium text-stone-950 dark:text-stone-50\">{product.name}</h3>\n"
            "          <div className=\"mt-1 flex items-center justify-between\">\n"
            "            <p className=\"text-sm text-stone-700 dark:text-stone-300\">${product.price}</p>\n"
            "            <p className=\"text-xs text-amber-700\">★ {product.rating}</p>\n"
            "          </div>\n"
            "        </div>\n"
            "      </div>\n"
            "      {quick && (\n"
            "        <div className=\"fixed inset-0 z-[60] flex items-center justify-center bg-stone-950/55 p-4\" onClick={() => setQuick(false)}>\n"
            "          <div className=\"w-full max-w-md overflow-hidden rounded-3xl bg-white dark:bg-stone-900\" onClick={(e) => e.stopPropagation()}>\n"
            "            <img src={product.image} alt=\"\" className=\"h-64 w-full object-cover\" />\n"
            "            <div className=\"p-6\">\n"
            "              <h4 className=\"font-serif text-2xl\">{product.name}</h4>\n"
            "              <p className=\"mt-2 text-sm text-stone-600\">{product.category} · ${product.price}</p>\n"
            "              <p className=\"mt-3 text-sm text-stone-500\">Sizes {product.sizes.join(' · ')}</p>\n"
            "              <button type=\"button\" className=\"mt-6 w-full rounded-full bg-stone-950 py-3 text-[11px] uppercase tracking-wider text-white\" onClick={() => setQuick(false)}>Close</button>\n"
            "            </div>\n"
            "          </div>\n"
            "        </div>\n"
            "      )}\n"
            "    </article>\n"
            "  )\n"
            "}\n"
        ),
    )


def _product_grid() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ProductGrid.tsx",
        content=(
            "import { useMemo, useState } from 'react'\n"
            "import { filterProducts, products } from '../data/catalog'\n"
            "import { ProductCard } from './ProductCard'\n\n"
            "type Props = {\n"
            "  title?: string\n"
            "  gender?: string\n"
            "  limit?: number\n"
            "  showFilters?: boolean\n"
            "  hideTitle?: boolean\n"
            "}\n\n"
            "export function ProductGrid({ title = 'Featured', gender = 'all', limit, showFilters = false, hideTitle = false }: Props) {\n"
            "  const [category, setCategory] = useState('all')\n"
            "  const [sort, setSort] = useState('featured')\n"
            "  const [q, setQ] = useState('')\n"
            "  const [page, setPage] = useState(1)\n"
            "  const categories = ['all', ...Array.from(new Set(products.map((p) => p.category).filter(Boolean)))]\n"
            "  const filtered = useMemo(() => filterProducts({ gender, category, q }), [gender, category, q])\n"
            "  const items = useMemo(() => {\n"
            "    let list = filtered\n"
            "    if (sort === 'price-asc') list = [...list].sort((a, b) => a.price - b.price)\n"
            "    if (sort === 'price-desc') list = [...list].sort((a, b) => b.price - a.price)\n"
            "    if (sort === 'rating') list = [...list].sort((a, b) => b.rating - a.rating)\n"
            "    return list\n"
            "  }, [filtered, sort])\n"
            "  const pageSize = 8\n"
            "  const sliced = limit ? items.slice(0, limit) : items\n"
            "  const totalPages = Math.max(1, Math.ceil(sliced.length / pageSize))\n"
            "  const view = showFilters ? sliced.slice((page - 1) * pageSize, page * pageSize) : sliced\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-12 sm:px-6 sm:py-14\">\n"
            "      {(!hideTitle || showFilters) && (\n"
            "        <div className=\"mb-8 flex flex-col gap-5\">\n"
            "          {!hideTitle && <h2 className=\"font-serif text-3xl tracking-tight text-stone-950 dark:text-stone-50\">{title}</h2>}\n"
            "          {showFilters && (\n"
            "            <div className=\"flex flex-col gap-4\">\n"
            "              <div className=\"flex flex-wrap gap-2\">\n"
            "                {categories.map((c) => (\n"
            "                  <button\n"
            "                    key={c}\n"
            "                    type=\"button\"\n"
            "                    onClick={() => { setCategory(c); setPage(1) }}\n"
            "                    className={`rounded-full px-4 py-2 text-[11px] font-medium uppercase tracking-wider transition ${\n"
            "                      category === c\n"
            "                        ? 'bg-stone-950 text-white dark:bg-stone-100 dark:text-stone-950'\n"
            "                        : 'border border-stone-300 bg-white text-stone-700 hover:border-stone-500 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-200'\n"
            "                    }`}\n"
            "                  >\n"
            "                    {c === 'all' ? 'All' : c}\n"
            "                  </button>\n"
            "                ))}\n"
            "              </div>\n"
            "              <div className=\"flex flex-wrap gap-2\">\n"
            "                <input value={q} onChange={(e) => { setQ(e.target.value); setPage(1) }} placeholder=\"Search products\" className=\"min-w-[180px] flex-1 rounded-full border border-stone-300 bg-white px-4 py-2.5 text-sm text-stone-900 outline-none focus:border-stone-500 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100\" />\n"
            "                <select value={sort} onChange={(e) => setSort(e.target.value)} className=\"rounded-full border border-stone-300 bg-white px-4 py-2.5 text-sm text-stone-900 dark:border-stone-700 dark:bg-stone-900 dark:text-stone-100\">\n"
            "                  <option value=\"featured\">Featured</option>\n"
            "                  <option value=\"price-asc\">Price: Low to high</option>\n"
            "                  <option value=\"price-desc\">Price: High to low</option>\n"
            "                  <option value=\"rating\">Top rated</option>\n"
            "                </select>\n"
            "              </div>\n"
            "            </div>\n"
            "          )}\n"
            "        </div>\n"
            "      )}\n"
            "      <div className=\"grid grid-cols-2 gap-4 sm:gap-5 lg:grid-cols-4\">\n"
            "        {view.map((p) => <ProductCard key={p.id} product={p} />)}\n"
            "      </div>\n"
            "      {view.length === 0 && <p className=\"py-16 text-center text-sm text-stone-500\">No pieces match these filters.</p>}\n"
            "      {showFilters && totalPages > 1 && (\n"
            "        <div className=\"mt-10 flex justify-center gap-2\">\n"
            "          {Array.from({ length: totalPages }, (_, i) => (\n"
            "            <button key={i} type=\"button\" onClick={() => setPage(i + 1)} className={`flex h-9 w-9 items-center justify-center rounded-full text-xs ${page === i + 1 ? 'bg-stone-950 text-white dark:bg-stone-100 dark:text-stone-950' : 'border border-stone-300 text-stone-700 dark:border-stone-700'}`}>{i + 1}</button>\n"
            "          ))}\n"
            "        </div>\n"
            "      )}\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _section_blocks(brand: str) -> GeneratedFile:
    look1, look2, look3 = FASHION_IMGS[1], FASHION_IMGS[2], FASHION_IMGS[3]
    lookbook = json.dumps([look1, look2, look3])
    gram = json.dumps(FASHION_IMGS[4:10])
    return GeneratedFile(
        path="src/components/BrandSections.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n"
            "import { ProductGrid } from './ProductGrid'\n\n"
            "export function CategorySplit() {\n"
            "  return (\n"
            "    <section className=\"mx-auto grid max-w-6xl gap-4 px-4 py-12 sm:px-6 md:grid-cols-2\">\n"
            f"      <Link to=\"/men\" className=\"group relative min-h-80 overflow-hidden rounded-3xl\">\n"
            f"        <img src=\"{look2}\" alt=\"Men\" className=\"absolute inset-0 h-full w-full object-cover transition duration-700 group-hover:scale-105\" />\n"
            "        <div className=\"absolute inset-0 bg-stone-950/35\" /><div className=\"absolute bottom-6 left-6 text-white\"><p className=\"text-xs uppercase tracking-[0.25em]\">Men</p><h3 className=\"mt-2 font-serif text-3xl\">Men's collection</h3></div>\n"
            "      </Link>\n"
            f"      <Link to=\"/women\" className=\"group relative min-h-80 overflow-hidden rounded-3xl\">\n"
            f"        <img src=\"{look3}\" alt=\"Women\" className=\"absolute inset-0 h-full w-full object-cover transition duration-700 group-hover:scale-105\" />\n"
            "        <div className=\"absolute inset-0 bg-stone-950/35\" /><div className=\"absolute bottom-6 left-6 text-white\"><p className=\"text-xs uppercase tracking-[0.25em]\">Women</p><h3 className=\"mt-2 font-serif text-3xl\">Women's collection</h3></div>\n"
            "      </Link>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            "export function Lookbook() {\n"
            f"  const shots = {lookbook}\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
            "      <h2 className=\"font-serif text-3xl\">Lookbook</h2>\n"
            "      <p className=\"mt-2 max-w-xl text-stone-600 dark:text-stone-400\">Editorial frames. Clothing only — no footwear collections.</p>\n"
            "      <div className=\"mt-8 grid gap-4 md:grid-cols-3\">\n"
            "        {shots.map((src) => (\n"
            "          <img key={src} src={src} alt=\"Lookbook\" className=\"h-80 w-full rounded-3xl object-cover\" loading=\"lazy\" />\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            f"export function WhyUs() {{\n"
            "  const items = ['Quiet luxury fabrics', 'Editorial fits', 'Timeless neutrals', 'Responsible production']\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
            f"      <h2 className=\"font-serif text-3xl\">Why choose {brand}</h2>\n"
            "      <div className=\"mt-8 grid gap-4 md:grid-cols-4\">\n"
            "        {items.map((t) => <div key={t} className=\"rounded-2xl border border-stone-200 bg-white p-5 dark:border-stone-800 dark:bg-stone-900\"><p className=\"text-sm font-medium\">{t}</p></div>)}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            "export function Testimonials() {\n"
            "  const rows = [\n"
            "    ['Amelia', 'The oversized tee drape is immaculate — finally a brand that edits properly.'],\n"
            "    ['Noah', 'Minimal, modern, and actually wearable. Feels like COS meeting quiet luxury.'],\n"
            "    ['Ivy', 'Packaging, fit notes, fabric — everything feels considered.'],\n"
            "  ]\n"
            "  return (\n"
            "    <section className=\"bg-stone-100 py-16 dark:bg-stone-900/50\">\n"
            "      <div className=\"mx-auto max-w-6xl px-4 sm:px-6\">\n"
            "        <h2 className=\"font-serif text-3xl\">Customer stories</h2>\n"
            "        <div className=\"mt-8 grid gap-4 md:grid-cols-3\">\n"
            "          {rows.map(([n, q]) => <blockquote key={n} className=\"rounded-2xl border border-stone-200 bg-white p-5 dark:border-stone-800 dark:bg-stone-950\"><p className=\"text-sm leading-relaxed text-stone-600 dark:text-stone-300\">“{q}”</p><footer className=\"mt-4 text-xs uppercase tracking-wider\">{n}</footer></blockquote>)}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            "export function Newsletter() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
            "      <div className=\"rounded-[2rem] bg-stone-950 px-8 py-12 text-white\">\n"
            "        <h2 className=\"font-serif text-3xl\">New season notes</h2>\n"
            "        <p className=\"mt-2 max-w-md text-stone-300\">Early access to drops, lookbooks, and private fittings.</p>\n"
            "        <form className=\"mt-6 flex flex-col gap-3 sm:flex-row\" onSubmit={(e) => e.preventDefault()}>\n"
            "          <input required type=\"email\" placeholder=\"Email\" className=\"w-full rounded-full border border-white/20 bg-transparent px-4 py-3 text-sm\" />\n"
            "          <button className=\"rounded-full bg-white px-6 py-3 text-xs font-semibold uppercase tracking-wider text-stone-950\">Subscribe</button>\n"
            "        </form>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            "export function InstagramGallery() {\n"
            f"  const imgs = {gram}\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
            "      <h2 className=\"font-serif text-3xl\">Instagram</h2>\n"
            "      <div className=\"mt-8 grid grid-cols-2 gap-3 md:grid-cols-6\">\n"
            "        {imgs.map((src) => <img key={src} src={src} alt=\"\" className=\"aspect-square rounded-2xl object-cover\" loading=\"lazy\" />)}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            "export function HomeMerchandising() {\n"
            "  return (\n"
            "    <>\n"
            "      <ProductGrid title=\"New arrivals\" limit={4} />\n"
            "      <CategorySplit />\n"
            "      <ProductGrid title=\"Featured pieces\" limit={8} />\n"
            "      <Lookbook />\n"
            "      <WhyUs />\n"
            "      <Testimonials />\n"
            "      <Newsletter />\n"
            "      <InstagramGallery />\n"
            "    </>\n"
            "  )\n"
            "}\n"
        ),
    )


def _footer(brand: str, palette: dict | None = None) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/StoreFooter.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n\n"
            "export function StoreFooter() {\n"
            "  return (\n"
            "    <footer className=\"border-t border-stone-200 bg-[#FAFAF8] dark:border-stone-800 dark:bg-stone-950\">\n"
            "      <div className=\"mx-auto grid max-w-6xl gap-8 px-4 py-14 sm:px-6 md:grid-cols-4\">\n"
            f"        <div><p className=\"text-lg tracking-[0.25em]\">{brand}</p><p className=\"mt-3 text-sm text-stone-500\">Premium branded clothing with responsive shopping and member access.</p></div>\n"
            "        <div className=\"text-sm\"><p className=\"font-medium\">Shop</p><div className=\"mt-3 grid gap-2 text-stone-500\"><Link to=\"/shop\">All</Link><Link to=\"/lookbook\">Lookbook</Link><Link to=\"/about\">About</Link></div></div>\n"
            "        <div className=\"text-sm\"><p className=\"font-medium\">Account</p><div className=\"mt-3 grid gap-2 text-stone-500\"><Link to=\"/login\">Sign in</Link><Link to=\"/register\">Sign up</Link><Link to=\"/contact\">Contact</Link></div></div>\n"
            "        <div className=\"text-sm\"><p className=\"font-medium\">Client care</p><p className=\"mt-3 text-stone-500\">Easy browsing on every screen. Email or phone membership. Complimentary returns within 14 days.</p></div>\n"
            "      </div>\n"
            f"      <div className=\"border-t border-stone-200 px-4 py-4 text-center text-xs text-stone-500 dark:border-stone-800\">© {brand}. All rights reserved.</div>\n"
            "    </footer>\n"
            "  )\n"
            "}\n"
        ),
    )


def _home_page(comp: str, brand: str) -> str:
    return (
        "import { FashionHero } from '../components/FashionHero'\n"
        "import { HomeMerchandising } from '../components/BrandSections'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"overflow-x-hidden bg-[#FAFAF8] text-stone-950 dark:bg-stone-950 dark:text-stone-50\">\n"
        "      <FashionHero />\n"
        "      <HomeMerchandising />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _login_page(comp: str, brand: str) -> str:
    return (
        "import { AuthForm } from '../components/AuthForm'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-[#FAFAF8] dark:bg-stone-950\">\n"
        "      <AuthForm mode=\"login\" />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _register_page(comp: str, brand: str) -> str:
    return (
        "import { AuthForm } from '../components/AuthForm'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-[#FAFAF8] dark:bg-stone-950\">\n"
        "      <AuthForm mode=\"register\" />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _lookbook_page(comp: str, brand: str, palette: dict | None = None) -> str:
    accent = (palette or PALETTES[0])["accent"]
    imgs = json.dumps(FASHION_IMGS[:8])
    return (
        f"const shots = {imgs} as string[]\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <section className=\"mx-auto max-w-6xl overflow-x-hidden px-4 py-14 sm:px-6\">\n"
        f"      <p className=\"text-xs uppercase tracking-[0.25em] text-[{accent}]\">{brand}</p>\n"
        "      <h1 className=\"mt-2 font-serif text-4xl md:text-5xl\">Lookbook</h1>\n"
        "      <p className=\"mt-3 max-w-xl text-stone-600 dark:text-stone-300\">Editorial frames from the season — crafted to feel dimensional on every screen.</p>\n"
        "      <div className=\"mt-10 columns-1 gap-4 sm:columns-2 lg:columns-3\">\n"
        "        {shots.map((src, i) => (\n"
        "          <img key={src} src={src} alt=\"\" className={`mb-4 w-full break-inside-avoid rounded-2xl object-cover shadow-lg ${i % 3 === 0 ? 'aspect-[3/4]' : 'aspect-[4/5]'}`} loading=\"lazy\" />\n"
        "        ))}\n"
        "      </div>\n"
        "    </section>\n"
        "  )\n"
        "}\n"
    )


def _shop_page(comp: str, brand: str, *, gender: str, title: str, palette: dict | None = None) -> str:
    accent = (palette or PALETTES[0])["accent"]
    return (
        "import { ProductGrid } from '../components/ProductGrid'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"overflow-x-hidden bg-[#FAFAF8] dark:bg-stone-950\">\n"
        "      <div className=\"border-b border-stone-200/80 dark:border-stone-800\">\n"
        f"        <div className=\"mx-auto max-w-6xl px-4 py-10 sm:px-6 sm:py-12\">\n"
        f"          <p className=\"text-[11px] font-semibold uppercase tracking-[0.28em] text-[{accent}]\">{brand}</p>\n"
        f"          <h1 className=\"mt-3 font-serif text-4xl tracking-tight text-stone-950 dark:text-stone-50 sm:text-5xl\">{title}</h1>\n"
        "          <p className=\"mt-3 max-w-lg text-sm leading-relaxed text-stone-600 dark:text-stone-400\">Curated apparel with clear filters, search, and a calm shopping layout.</p>\n"
        "        </div>\n"
        "      </div>\n"
        f"      <ProductGrid title=\"{title}\" gender=\"{gender}\" showFilters hideTitle />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _about_page(comp: str, brand: str, palette: dict | None = None) -> str:
    accent = (palette or PALETTES[0])["accent"]
    return (
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <section className=\"mx-auto max-w-3xl px-4 py-16\">\n"
        f"      <p className=\"text-xs uppercase tracking-[0.25em] text-[{accent}]\">{brand}</p>\n"
        "      <h1 className=\"mt-3 font-serif text-4xl\">About the house</h1>\n"
        f"      <p className=\"mt-6 text-lg leading-relaxed text-stone-600 dark:text-stone-300\">{brand} is a premium clothing brand for men, women, and young fashion enthusiasts. We design apparel and accessories with a luxury-minimal language — black, white, beige, cream, and gold — never footwear or athletic gear.</p>\n"
        "    </section>\n"
        "  )\n"
        "}\n"
    )


def _contact_page(comp: str, brand: str) -> str:
    return (
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <section className=\"mx-auto max-w-xl px-4 py-16\">\n"
        "      <h1 className=\"font-serif text-4xl\">Contact</h1>\n"
        f"      <p className=\"mt-3 text-stone-600\">Concierge for {brand} clients.</p>\n"
        "      <form className=\"mt-8 grid gap-3\" onSubmit={(e) => e.preventDefault()}>\n"
        "        <input className=\"rounded-xl border border-stone-200 px-3 py-3 text-sm dark:border-stone-700 dark:bg-stone-900\" placeholder=\"Name\" required />\n"
        "        <input type=\"email\" className=\"rounded-xl border border-stone-200 px-3 py-3 text-sm dark:border-stone-700 dark:bg-stone-900\" placeholder=\"Email\" required />\n"
        "        <textarea className=\"min-h-32 rounded-xl border border-stone-200 px-3 py-3 text-sm dark:border-stone-700 dark:bg-stone-900\" placeholder=\"Message\" required />\n"
        "        <button className=\"rounded-full bg-stone-950 py-3 text-xs font-semibold uppercase tracking-wider text-white\">Send</button>\n"
        "      </form>\n"
        "    </section>\n"
        "  )\n"
        "}\n"
    )

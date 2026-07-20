"""Footwear / shoe store generator — distinct from phones & clothing."""

from __future__ import annotations

from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements

SHOE_IMGS = [
    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1460353581641-37baddab0fa2?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=800&q=80",
]


def generate_shoe_store(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    analysis = requirements.analysis
    brand = (getattr(analysis, "brand_name", "") or plan.project_name or "Shoe Store").strip()
    if brand.lower() in {"marketing landing page", "e-commerce store", "fashion brand", "sneaker store"}:
        brand = plan.project_name if plan.project_name.lower() not in {"new", "untitled"} else "STEPX"
    primary = analysis.theme.get("primary_color", "#111827")
    if primary in {"#2563EB", "blue"} or "blue" not in analysis.raw_prompt.lower():
        # Prefer footwear palette: black / charcoal accent unless user asked blue
        if "blue" not in analysis.raw_prompt.lower():
            primary = "#111827"

    files: list[GeneratedFile] = [
        _button(primary),
        _header(brand, plan, primary),
        _hero(brand, primary),
        _categories(),
        _product_grid(brand, primary),
        _lookbook(),
        _why_us(),
        _reviews(),
        _newsletter(primary),
        _contact(brand, primary),
        _footer(brand),
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

    for route in plan.routes:
        page = route["page"].lower()
        comp = route["component"]
        if route["path"] == "/":
            body = _home(brand, primary)
        elif "shop" in page or "sneaker" in page or "shoe" in page or "product" in page or "collection" in page:
            body = _shop_page(comp, brand)
        elif "lookbook" in page or "gallery" in page:
            body = _lookbook_page(comp)
        elif "about" in page:
            body = _about_page(comp, brand)
        elif "contact" in page:
            body = _contact_page(comp, brand, primary)
        else:
            body = (
                f"export default function {comp}() {{\n"
                f"  return (\n"
                f"    <section className=\"mx-auto max-w-6xl px-4 py-16\">\n"
                f"      <h1 className=\"text-3xl font-bold\">{route['page']}</h1>\n"
                f"      <p className=\"mt-3 text-stone-600\">Explore {route['page']} at {brand}.</p>\n"
                f"    </section>\n"
                f"  )\n"
                f"}}\n"
            )
        files.append(GeneratedFile(path=f"src/pages/{comp}.tsx", content=body))

    return list({f.path: f for f in files}.values())


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
            f"  const styles = variant === 'primary' ? 'text-white' : 'border border-stone-300 bg-white text-stone-900'\n"
            f"  const style = variant === 'primary' ? {{ backgroundColor: '{primary}' }} : undefined\n"
            "  return <a href={href} className={base + styles + ' ' + className} style={style}>{children}</a>\n"
            "}\n"
        ),
    )


def _header(brand: str, plan: ProjectPlan, primary: str) -> GeneratedFile:
    links = ",\n".join(f'  {{ to: "{r["path"]}", label: "{r["page"]}" }}' for r in plan.routes)
    return GeneratedFile(
        path="src/components/ShoeHeader.tsx",
        content=(
            "import { useState } from 'react'\n"
            "import { Link, NavLink } from 'react-router-dom'\n"
            "import { Menu, Search, ShoppingBag, X } from 'lucide-react'\n\n"
            f"const links = [\n{links}\n]\n\n"
            "export function ShoeHeader() {\n"
            "  const [open, setOpen] = useState(false)\n"
            "  return (\n"
            "    <header className=\"sticky top-0 z-50 border-b border-stone-200 bg-white/95 backdrop-blur\">\n"
            "      <div className=\"mx-auto flex max-w-6xl items-center gap-4 px-4 py-4\">\n"
            f"        <Link to=\"/\" className=\"text-xl font-black tracking-tight\" style={{{{ color: '{primary}' }}}}>{brand}</Link>\n"
            "        <nav className=\"ml-auto hidden gap-5 text-sm font-medium md:flex\">\n"
            "          {links.map((l) => (\n"
            "            <NavLink key={l.to} to={l.to} className={({ isActive }) => isActive ? 'text-stone-950' : 'text-stone-500 hover:text-stone-950'}>{l.label}</NavLink>\n"
            "          ))}\n"
            "        </nav>\n"
            "        <div className=\"ml-auto flex items-center gap-2 md:ml-4\">\n"
            "          <button type=\"button\" className=\"rounded-full p-2 hover:bg-stone-100\" aria-label=\"Search\"><Search className=\"h-5 w-5\" /></button>\n"
            "          <button type=\"button\" className=\"rounded-full p-2 hover:bg-stone-100\" aria-label=\"Bag\"><ShoppingBag className=\"h-5 w-5\" /></button>\n"
            "          <button type=\"button\" className=\"rounded-full p-2 hover:bg-stone-100 md:hidden\" onClick={() => setOpen(v => !v)} aria-label=\"Menu\">{open ? <X className=\"h-5 w-5\" /> : <Menu className=\"h-5 w-5\" />}</button>\n"
            "        </div>\n"
            "      </div>\n"
            "      {open && (\n"
            "        <div className=\"grid gap-2 border-t border-stone-200 px-4 py-3 md:hidden\">\n"
            "          {links.map((l) => <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)} className=\"py-2 text-sm font-medium\">{l.label}</NavLink>)}\n"
            "        </div>\n"
            "      )}\n"
            "    </header>\n"
            "  )\n"
            "}\n"
        ),
    )


def _hero(brand: str, primary: str) -> GeneratedFile:
    img = SHOE_IMGS[0]
    return GeneratedFile(
        path="src/components/ShoeHero.tsx",
        content=(
            "import { Button } from './Button'\n\n"
            "export function ShoeHero() {\n"
            "  return (\n"
            "    <section className=\"relative overflow-hidden bg-stone-950 text-white\">\n"
            f"      <div className=\"absolute inset-0 opacity-50\" style={{{{ backgroundImage: `url('{img}')`, backgroundSize: 'cover', backgroundPosition: 'center' }}}} />\n"
            "      <div className=\"absolute inset-0 bg-gradient-to-r from-stone-950 via-stone-950/85 to-transparent\" />\n"
            "      <div className=\"relative mx-auto grid max-w-6xl gap-8 px-4 py-20 md:grid-cols-2 md:items-center\">\n"
            "        <div>\n"
            f"          <p className=\"text-sm font-semibold uppercase tracking-[0.25em] text-amber-300\">{brand}</p>\n"
            "          <h1 className=\"mt-4 text-4xl font-black tracking-tight sm:text-6xl\">Step Into Style</h1>\n"
            "          <p className=\"mt-4 max-w-xl text-lg text-stone-300\">Sneakers, formals, and everyday footwear crafted for comfort and confidence.</p>\n"
            "          <div className=\"mt-8 flex flex-wrap gap-3\">\n"
            "            <Button href=\"#/shop\">Shop Shoes</Button>\n"
            "            <Button href=\"#/lookbook\" variant=\"ghost\" className=\"border-white/30 bg-white/10 text-white\">View Lookbook</Button>\n"
            "          </div>\n"
            "        </div>\n"
            f"        <img src=\"{img}\" alt=\"Featured shoes\" className=\"h-72 w-full rounded-3xl object-cover shadow-2xl md:h-96\" />\n"
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
        ("Sandals", SHOE_IMGS[5]),
        ("Kids", SHOE_IMGS[0]),
    ]
    rows = ",\n".join(f'  {{ name: "{n}", img: "{i}" }}' for n, i in cats)
    return GeneratedFile(
        path="src/components/ShoeCategories.tsx",
        content=(
            f"const cats = [\n{rows}\n]\n"
            "export function ShoeCategories() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14\">\n"
            "      <h2 className=\"text-3xl font-bold tracking-tight\">Shop by Category</h2>\n"
            "      <div className=\"mt-8 grid grid-cols-2 gap-4 md:grid-cols-3\">\n"
            "        {cats.map((c) => (\n"
            "          <a key={c.name} href=\"#/shop\" className=\"group overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm\">\n"
            "            <img src={c.img} alt={c.name} className=\"h-40 w-full object-cover transition group-hover:scale-105\" loading=\"lazy\" />\n"
            "            <div className=\"p-4 font-semibold\">{c.name}</div>\n"
            "          </a>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _product_grid(brand: str, primary: str) -> GeneratedFile:
    products = [
        ("Aero Run Pro", "Running", 4999, 3999),
        ("City Walk Slip-On", "Casual", 2499, 1999),
        ("Oxford Classic", "Formal", 5999, 4999),
        ("Trail Blaze Boot", "Boots", 6999, 5499),
        ("Street Kick Low", "Sneakers", 3499, 2999),
        ("Cloud Soft Sandal", "Sandals", 1799, 1499),
        ("Kids Bounce", "Kids", 1999, 1599),
        ("Court Ace", "Sneakers", 4299, 3599),
    ]
    rows = []
    for i, (name, cat, orig, price) in enumerate(products):
        rows.append(
            f'  {{ name: "{name}", cat: "{cat}", original: {orig}, price: {price}, img: "{SHOE_IMGS[i % len(SHOE_IMGS)]}" }}'
        )
    return GeneratedFile(
        path="src/components/ShoeGrid.tsx",
        content=(
            "import { Button } from './Button'\n\n"
            f"const products = [\n" + ",\n".join(rows) + "\n]\n\n"
            "function inr(n: number) {\n"
            "  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)\n"
            "}\n\n"
            "export function ShoeGrid({ title = 'Best Sellers', limit }: { title?: string; limit?: number }) {\n"
            "  const items = typeof limit === 'number' ? products.slice(0, limit) : products\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14\">\n"
            "      <h2 className=\"text-3xl font-bold tracking-tight\">{title}</h2>\n"
            "      <div className=\"mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4\">\n"
            "        {items.map((p) => (\n"
            "          <article key={p.name} className=\"overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg\">\n"
            "            <img src={p.img} alt={p.name} className=\"h-48 w-full object-cover\" loading=\"lazy\" />\n"
            "            <div className=\"p-4\">\n"
            "              <p className=\"text-xs uppercase tracking-wide text-stone-500\">{p.cat}</p>\n"
            "              <h3 className=\"mt-1 font-semibold\">{p.name}</h3>\n"
            "              <div className=\"mt-2 flex items-baseline gap-2\">\n"
            "                <span className=\"text-lg font-bold\">{inr(p.price)}</span>\n"
            "                <span className=\"text-sm text-stone-400 line-through\">{inr(p.original)}</span>\n"
            "              </div>\n"
            "              <Button className=\"mt-4 w-full\">Add to Bag</Button>\n"
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
            "      <div className=\"mx-auto max-w-6xl px-4 py-14\">\n"
            "        <h2 className=\"text-3xl font-bold tracking-tight\">Lookbook</h2>\n"
            "        <div className=\"mt-8 grid gap-4 sm:grid-cols-2\">\n"
            "          {shots.map((src, i) => (\n"
            "            <img key={src} src={src} alt={`Look ${i + 1}`} className=\"h-64 w-full rounded-2xl object-cover shadow-sm\" loading=\"lazy\" />\n"
            "          ))}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _why_us() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ShoeWhyUs.tsx",
        content=(
            "const items = ['Free Size Exchange', 'Genuine Materials', 'Pan-India Delivery', 'Easy 7-Day Returns']\n"
            "export function ShoeWhyUs() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14\">\n"
            "      <h2 className=\"text-3xl font-bold\">Why Shop With Us</h2>\n"
            "      <div className=\"mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4\">\n"
            "        {items.map((item) => (\n"
            "          <div key={item} className=\"rounded-2xl border border-stone-200 bg-white p-5 shadow-sm\">\n"
            "            <p className=\"font-semibold\">{item}</p>\n"
            "          </div>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _reviews() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ShoeReviews.tsx",
        content=(
            "const reviews = [\n"
            "  { name: 'Meera', text: 'Perfect fit and stylish sneakers. Delivery was fast!' },\n"
            "  { name: 'Arjun', text: 'Great formal shoes for office — comfort all day.' },\n"
            "  { name: 'Sana', text: 'Loved the collection. Size exchange was hassle-free.' },\n"
            "]\n"
            "export function ShoeReviews() {\n"
            "  return (\n"
            "    <section className=\"bg-white\">\n"
            "      <div className=\"mx-auto max-w-6xl px-4 py-14\">\n"
            "        <h2 className=\"text-3xl font-bold\">Customer Love</h2>\n"
            "        <div className=\"mt-8 grid gap-4 md:grid-cols-3\">\n"
            "          {reviews.map((r) => (\n"
            "            <blockquote key={r.name} className=\"rounded-2xl border border-stone-200 bg-stone-50 p-5\">\n"
            "              <p className=\"text-amber-500\">★★★★★</p>\n"
            "              <p className=\"mt-3 text-sm text-stone-700\">“{r.text}”</p>\n"
            "              <footer className=\"mt-3 text-sm font-semibold\">{r.name}</footer>\n"
            "            </blockquote>\n"
            "          ))}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _newsletter(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ShoeNewsletter.tsx",
        content=(
            "export function ShoeNewsletter() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-10\">\n"
            "      <div className=\"rounded-3xl bg-stone-950 px-8 py-10 text-white\">\n"
            "        <h2 className=\"text-3xl font-bold\">New Drops Every Week</h2>\n"
            "        <p className=\"mt-2 text-stone-300\">Get early access to sneakers and festive footwear offers.</p>\n"
            "        <form className=\"mt-6 flex max-w-lg flex-col gap-3 sm:flex-row\" onSubmit={(e) => e.preventDefault()}>\n"
            "          <input type=\"email\" placeholder=\"Email address\" className=\"flex-1 rounded-full px-4 py-3 text-sm text-stone-900\" />\n"
            f"          <button type=\"submit\" className=\"rounded-full px-5 py-3 text-sm font-semibold text-white\" style={{{{ backgroundColor: '{primary}' }}}}>Subscribe</button>\n"
            "        </form>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _contact(brand: str, primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ShoeContact.tsx",
        content=(
            "export function ShoeContact() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14\">\n"
            "      <h2 className=\"text-3xl font-bold\">Visit Our Store</h2>\n"
            f"      <p className=\"mt-3 text-stone-600\">{brand} · Footwear & Sneakers</p>\n"
            "      <p className=\"mt-2 text-sm text-stone-600\">42 Fashion Street, Mumbai · +91 98765 43210</p>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _footer(brand: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ShoeFooter.tsx",
        content=(
            "export function ShoeFooter() {\n"
            "  return (\n"
            "    <footer className=\"border-t border-stone-800 bg-stone-950 text-stone-400\">\n"
            "      <div className=\"mx-auto flex max-w-6xl flex-col gap-2 px-4 py-8 text-sm sm:flex-row sm:justify-between\">\n"
            f"        <p>© {{new Date().getFullYear()}} {brand}</p>\n"
            "        <p>Shoes · Sneakers · Formals · Delivery across India</p>\n"
            "      </div>\n"
            "    </footer>\n"
            "  )\n"
            "}\n"
        ),
    )


def _home(brand: str, primary: str) -> str:
    return (
        "import { ShoeHero } from '../components/ShoeHero'\n"
        "import { ShoeCategories } from '../components/ShoeCategories'\n"
        "import { ShoeGrid } from '../components/ShoeGrid'\n"
        "import { ShoeLookbook } from '../components/ShoeLookbook'\n"
        "import { ShoeWhyUs } from '../components/ShoeWhyUs'\n"
        "import { ShoeReviews } from '../components/ShoeReviews'\n"
        "import { ShoeNewsletter } from '../components/ShoeNewsletter'\n"
        "import { ShoeContact } from '../components/ShoeContact'\n\n"
        "export default function HomePage() {\n"
        "  return (\n"
        "    <div className=\"bg-stone-50 text-stone-900\">\n"
        "      <ShoeHero />\n"
        "      <ShoeCategories />\n"
        "      <ShoeGrid limit={8} />\n"
        "      <ShoeLookbook />\n"
        "      <ShoeWhyUs />\n"
        "      <ShoeReviews />\n"
        "      <ShoeNewsletter />\n"
        "      <ShoeContact />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _shop_page(comp: str, brand: str) -> str:
    return (
        "import { ShoeGrid } from '../components/ShoeGrid'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-stone-50\">\n"
        f"      <ShoeGrid title=\"{brand} Collection\" />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _lookbook_page(comp: str) -> str:
    return (
        "import { ShoeLookbook } from '../components/ShoeLookbook'\n\n"
        f"export default function {comp}() {{\n"
        "  return <div className=\"bg-stone-50\"><ShoeLookbook /></div>\n"
        "}\n"
    )


def _about_page(comp: str, brand: str) -> str:
    return (
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <section className=\"mx-auto max-w-6xl px-4 py-16\">\n"
        f"      <h1 className=\"text-4xl font-bold\">About {brand}</h1>\n"
        f"      <p className=\"mt-4 max-w-2xl text-lg text-stone-600\">{brand} is a footwear destination for sneakers, formals, and everyday comfort — quality shoes for every step.</p>\n"
        "    </section>\n"
        "  )\n"
        "}\n"
    )


def _contact_page(comp: str, brand: str, primary: str) -> str:
    return (
        "import { ShoeContact } from '../components/ShoeContact'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-stone-50\">\n"
        "      <section className=\"mx-auto max-w-xl px-4 py-14\">\n"
        "        <h1 className=\"text-3xl font-bold\">Contact</h1>\n"
        "        <form className=\"mt-6 grid gap-3 rounded-2xl border border-stone-200 bg-white p-6\" onSubmit={(e) => e.preventDefault()}>\n"
        "          <input className=\"rounded-xl border border-stone-300 px-3 py-2 text-sm\" placeholder=\"Name\" />\n"
        "          <input className=\"rounded-xl border border-stone-300 px-3 py-2 text-sm\" placeholder=\"Phone\" />\n"
        "          <textarea className=\"min-h-24 rounded-xl border border-stone-300 px-3 py-2 text-sm\" placeholder=\"Message\" />\n"
        f"          <button type=\"submit\" className=\"rounded-full px-4 py-2.5 text-sm font-semibold text-white\" style={{{{ backgroundColor: '{primary}' }}}}>Send</button>\n"
        "        </form>\n"
        "      </section>\n"
        "      <ShoeContact />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )

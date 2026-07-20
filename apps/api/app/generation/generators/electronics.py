"""Premium electronics / mobile store generator (MobileHub-style)."""

from __future__ import annotations

from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements

# Free Unsplash images (no API key)
PHONE_IMGS = [
    "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?auto=format&fit=crop&w=800&q=80",
]
ACC_IMGS = [
    "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?auto=format&fit=crop&w=600&q=80",
]
STORE_IMGS = [
    "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=900&q=80",
    "https://images.unsplash.com/photo-1556740738-b6a63e27c4df?auto=format&fit=crop&w=900&q=80",
]


def generate_electronics_store(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    analysis = requirements.analysis
    brand = (getattr(analysis, "brand_name", "") or plan.project_name or "MobileHub").strip()
    primary = analysis.theme.get("primary_color", "#2563EB")
    whatsapp = "+919876543210"
    if "+91" in analysis.raw_prompt:
        import re

        m = re.search(r"\+91[\s\-]?(\d[\d\s\-]{8,14}\d)", analysis.raw_prompt)
        if m:
            whatsapp = "+91" + re.sub(r"\D", "", m.group(1))

    files: list[GeneratedFile] = [
        _button(primary),
        _announcement(),
        _header(brand, plan, primary),
        _hero(brand, primary),
        _brands(),
        _categories(),
        _product_grid(primary),
        _deals(primary),
        _why_us(),
        _accessories(),
        _reviews(),
        _gallery(),
        _newsletter(primary),
        _contact_block(brand, primary),
        _footer(brand, plan),
        _whatsapp(brand, whatsapp),
        _faq(),
        _filters_panel(primary),
        _use_theme(),
    ]

    for route in plan.routes:
        page = route["page"].lower().replace(" ", "")
        comp = route["component"]
        if route["path"] == "/":
            body = _home_page(brand, primary)
        elif "smartphone" in page or page == "shop":
            body = _shop_page(comp, "Smartphones", primary)
        elif "accessor" in page:
            body = _accessories_page(comp)
        elif "offer" in page or "deal" in page:
            body = _offers_page(comp, primary)
        elif "about" in page:
            body = _about_page(comp, brand)
        elif "contact" in page:
            body = _contact_page(comp, brand, primary)
        elif "faq" in page:
            body = _faq_page(comp)
        elif "product" in page:
            body = _product_detail_page(comp, primary)
        else:
            body = (
                f"export default function {comp}() {{\n"
                f"  return (\n"
                f"    <section className=\"mx-auto max-w-6xl px-4 py-16\">\n"
                f"      <h1 className=\"text-3xl font-bold\">{route['page']}</h1>\n"
                f"      <p className=\"mt-3 text-slate-600\">Explore {route['page']} at {brand}.</p>\n"
                f"    </section>\n"
                f"  )\n"
                f"}}\n"
            )
        files.append(GeneratedFile(path=f"src/pages/{comp}.tsx", content=body))

    # Compatibility aliases expected by older validators / router shell
    files.append(
        GeneratedFile(
            path="src/components/Navbar.tsx",
            content="export { StoreHeader as Navbar } from './StoreHeader'\n",
        )
    )
    files.append(
        GeneratedFile(
            path="src/components/Hero.tsx",
            content="export { StoreHero as Hero } from './StoreHero'\n",
        )
    )
    files.append(
        GeneratedFile(
            path="src/components/Footer.tsx",
            content="export { StoreFooter as Footer } from './StoreFooter'\n",
        )
    )
    files.append(
        GeneratedFile(
            path="src/components/Card.tsx",
            content=(
                "type CardProps = { title: string; description: string }\n"
                "export function Card({ title, description }: CardProps) {\n"
                "  return (\n"
                "    <article className=\"rounded-2xl border border-slate-200 bg-white p-5 shadow-sm\">\n"
                "      <h3 className=\"font-semibold\">{title}</h3>\n"
                "      <p className=\"mt-2 text-sm text-slate-600\">{description}</p>\n"
                "    </article>\n"
                "  )\n"
                "}\n"
            ),
        )
    )

    by_path = {f.path: f for f in files}
    return list(by_path.values())


def _use_theme() -> GeneratedFile:
    return GeneratedFile(
        path="src/hooks/useTheme.ts",
        content=(
            "import { useEffect, useState } from 'react'\n\n"
            "export function useTheme() {\n"
            "  const [dark] = useState(false)\n"
            "  useEffect(() => {\n"
            "    document.documentElement.classList.toggle('dark', dark)\n"
            "  }, [dark])\n"
            "  return { dark }\n"
            "}\n"
        ),
    )


def _button(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Button.tsx",
        content=(
            "type ButtonProps = { children: React.ReactNode; variant?: 'primary' | 'ghost' | 'dark'; href?: string; onClick?: () => void; className?: string }\n"
            "export function Button({ children, variant = 'primary', href, onClick, className = '' }: ButtonProps) {\n"
            "  const base = 'inline-flex items-center justify-center rounded-xl px-5 py-2.5 text-sm font-semibold transition hover:-translate-y-0.5 '\n"
            "  const styles =\n"
            f"    variant === 'primary' ? 'text-white shadow-lg shadow-blue-500/20' :\n"
            "    variant === 'dark' ? 'bg-slate-950 text-white' :\n"
            "    'border border-slate-300 bg-white text-slate-800 hover:border-slate-400'\n"
            f"  const style = variant === 'primary' ? {{ backgroundColor: '{primary}' }} : undefined\n"
            "  if (href) return <a href={href} className={base + styles + ' ' + className} style={style}>{children}</a>\n"
            "  return <button type=\"button\" onClick={onClick} className={base + styles + ' ' + className} style={style}>{children}</button>\n"
            "}\n"
        ),
    )


def _announcement() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/AnnouncementBar.tsx",
        content=(
            "const items = [\n"
            "  'Free Delivery on Orders Above ₹999',\n"
            "  'EMI Available',\n"
            "  'Official Brand Warranty',\n"
            "  '24/7 Customer Support',\n"
            "]\n"
            "export function AnnouncementBar() {\n"
            "  return (\n"
            "    <div className=\"bg-slate-950 text-white\">\n"
            "      <div className=\"mx-auto flex max-w-7xl gap-6 overflow-x-auto px-4 py-2 text-xs font-medium tracking-wide sm:justify-center sm:gap-10\">\n"
            "        {items.map((item) => (\n"
            "          <span key={item} className=\"whitespace-nowrap opacity-90\">{item}</span>\n"
            "        ))}\n"
            "      </div>\n"
            "    </div>\n"
            "  )\n"
            "}\n"
        ),
    )


def _header(brand: str, plan: ProjectPlan, primary: str) -> GeneratedFile:
    links = ",\n".join(f'  {{ to: "{r["path"]}", label: "{r["page"]}" }}' for r in plan.routes)
    return GeneratedFile(
        path="src/components/StoreHeader.tsx",
        content=(
            "import { useState } from 'react'\n"
            "import { Link, NavLink } from 'react-router-dom'\n"
            "import { Heart, Menu, Search, ShoppingCart, User, X, GitCompare } from 'lucide-react'\n\n"
            f"const links = [\n{links}\n]\n\n"
            "export function StoreHeader() {\n"
            "  const [open, setOpen] = useState(false)\n"
            "  return (\n"
            "    <header className=\"sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur-xl\">\n"
            "      <div className=\"mx-auto flex max-w-7xl items-center gap-3 px-4 py-3\">\n"
            f"        <Link to=\"/\" className=\"text-xl font-bold tracking-tight\" style={{{{ color: '{primary}' }}}}>{brand}</Link>\n"
            "        <nav className=\"ml-4 hidden items-center gap-4 text-sm font-medium lg:flex\">\n"
            "          {links.map((l) => (\n"
            "            <NavLink key={l.to} to={l.to} className={({ isActive }) => isActive ? 'text-slate-950' : 'text-slate-500 hover:text-slate-950'}>{l.label}</NavLink>\n"
            "          ))}\n"
            "        </nav>\n"
            "        <div className=\"ml-auto hidden min-w-0 flex-1 items-center md:flex md:max-w-sm lg:max-w-md\">\n"
            "          <div className=\"flex w-full items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm\">\n"
            "            <Search className=\"h-4 w-4 text-slate-400\" />\n"
            "            <input className=\"w-full bg-transparent outline-none\" placeholder=\"Search smartphones, brands…\" />\n"
            "          </div>\n"
            "        </div>\n"
            "        <div className=\"ml-auto flex items-center gap-2 text-slate-700 md:ml-2\">\n"
            "          <button type=\"button\" className=\"rounded-lg p-2 hover:bg-slate-100\" aria-label=\"Compare\"><GitCompare className=\"h-5 w-5\" /></button>\n"
            "          <button type=\"button\" className=\"rounded-lg p-2 hover:bg-slate-100\" aria-label=\"Wishlist\"><Heart className=\"h-5 w-5\" /></button>\n"
            "          <button type=\"button\" className=\"rounded-lg p-2 hover:bg-slate-100\" aria-label=\"Cart\"><ShoppingCart className=\"h-5 w-5\" /></button>\n"
            "          <button type=\"button\" className=\"hidden rounded-lg p-2 hover:bg-slate-100 sm:inline-flex\" aria-label=\"Account\"><User className=\"h-5 w-5\" /></button>\n"
            "          <button type=\"button\" className=\"rounded-lg p-2 hover:bg-slate-100 lg:hidden\" onClick={() => setOpen((v) => !v)} aria-label=\"Menu\">{open ? <X className=\"h-5 w-5\" /> : <Menu className=\"h-5 w-5\" />}</button>\n"
            "        </div>\n"
            "      </div>\n"
            "      {open && (\n"
            "        <div className=\"border-t border-slate-200 bg-white px-4 py-3 lg:hidden\">\n"
            "          <div className=\"mb-3 flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm md:hidden\">\n"
            "            <Search className=\"h-4 w-4 text-slate-400\" /><input className=\"w-full bg-transparent outline-none\" placeholder=\"Search…\" />\n"
            "          </div>\n"
            "          <div className=\"grid gap-2 text-sm font-medium\">\n"
            "            {links.map((l) => (\n"
            "              <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)} className=\"rounded-lg px-2 py-2 hover:bg-slate-50\">{l.label}</NavLink>\n"
            "            ))}\n"
            "          </div>\n"
            "        </div>\n"
            "      )}\n"
            "    </header>\n"
            "  )\n"
            "}\n"
        ),
    )


def _hero(brand: str, primary: str) -> GeneratedFile:
    img = PHONE_IMGS[0]
    return GeneratedFile(
        path="src/components/StoreHero.tsx",
        content=(
            "import { Button } from './Button'\n\n"
            "export function StoreHero() {\n"
            "  return (\n"
            "    <section className=\"relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-white\">\n"
            "      <div className=\"absolute inset-0 opacity-40\" style={{ backgroundImage: `url('{img}')`, backgroundSize: 'cover', backgroundPosition: 'center' }} />\n"
            "      <div className=\"absolute inset-0 bg-gradient-to-r from-slate-950/95 via-slate-950/80 to-transparent\" />\n"
            "      <div className=\"relative mx-auto grid max-w-7xl gap-8 px-4 py-16 md:grid-cols-2 md:items-center md:py-24\">\n"
            "        <div>\n"
            f"          <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-blue-300\">{brand}</p>\n"
            "          <h1 className=\"mt-4 text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl\">The Latest Smartphones at the Best Prices</h1>\n"
            "          <p className=\"mt-4 max-w-xl text-base leading-relaxed text-slate-300\">Explore iPhone, Samsung, OnePlus, Xiaomi, Google Pixel, Vivo, Oppo, Motorola and more.</p>\n"
            "          <div className=\"mt-8 flex flex-wrap gap-3\">\n"
            "            <Button href=\"#/smartphones\">Shop Now</Button>\n"
            "            <Button href=\"#/offers\" variant=\"ghost\" className=\"border-white/30 bg-white/10 text-white hover:bg-white/20\">View Offers</Button>\n"
            "          </div>\n"
            "        </div>\n"
            f"        <div className=\"justify-self-center overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-3 shadow-2xl backdrop-blur\">\n"
            f"          <img src=\"{img}\" alt=\"Latest smartphones\" className=\"h-64 w-full rounded-2xl object-cover sm:h-80\" loading=\"eager\" />\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _brands() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/BrandStrip.tsx",
        content=(
            "const brands = ['Apple','Samsung','OnePlus','Xiaomi','Google Pixel','Vivo','Oppo','Motorola','Nothing','Realme']\n"
            "export function BrandStrip() {\n"
            "  return (\n"
            "    <section className=\"border-b border-slate-200 bg-white\">\n"
            "      <div className=\"mx-auto max-w-7xl px-4 py-10\">\n"
            "        <h2 className=\"text-center text-sm font-semibold uppercase tracking-[0.2em] text-slate-500\">Popular Brands</h2>\n"
            "        <div className=\"mt-6 flex flex-wrap items-center justify-center gap-3\">\n"
            "          {brands.map((b) => (\n"
            "            <div key={b} className=\"rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm\">{b}</div>\n"
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
        ("Smartphones", PHONE_IMGS[1], "#/smartphones"),
        ("Tablets", PHONE_IMGS[2], "#/smartphones"),
        ("Smart Watches", ACC_IMGS[1], "#/accessories"),
        ("Wireless Earbuds", ACC_IMGS[0], "#/accessories"),
        ("Chargers", ACC_IMGS[3], "#/accessories"),
        ("Power Banks", ACC_IMGS[2], "#/accessories"),
        ("Mobile Covers", ACC_IMGS[0], "#/accessories"),
        ("Screen Protectors", PHONE_IMGS[3], "#/accessories"),
        ("Bluetooth Speakers", ACC_IMGS[1], "#/accessories"),
    ]
    items = ",\n".join(
        f'  {{ name: "{n}", img: "{i}", to: "{t}" }}' for n, i, t in cats
    )
    return GeneratedFile(
        path="src/components/CategoryGrid.tsx",
        content=(
            f"const cats = [\n{items}\n]\n"
            "export function CategoryGrid() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-7xl px-4 py-14\">\n"
            "      <h2 className=\"text-3xl font-bold tracking-tight\">Shop by Category</h2>\n"
            "      <div className=\"mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5\">\n"
            "        {cats.map((c) => (\n"
            "          <a key={c.name} href={c.to} className=\"group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md\">\n"
            "            <img src={c.img} alt={c.name} className=\"h-28 w-full object-cover transition group-hover:scale-105\" loading=\"lazy\" />\n"
            "            <div className=\"p-3 text-sm font-semibold\">{c.name}</div>\n"
            "          </a>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _product_grid(primary: str) -> GeneratedFile:
    phones = [
        ("Apple", "iPhone 16 Pro", "256GB", "8GB", "Natural Titanium", 149900, 139900, 4.8),
        ("Samsung", "Galaxy S25 Ultra", "512GB", "12GB", "Titanium Gray", 141999, 129999, 4.7),
        ("OnePlus", "13", "256GB", "12GB", "Arctic Dawn", 69999, 64999, 4.6),
        ("Google", "Pixel 9 Pro", "256GB", "16GB", "Obsidian", 109999, 99999, 4.7),
        ("Xiaomi", "15 Pro", "256GB", "12GB", "Black", 69999, 62999, 4.5),
        ("Vivo", "X200 Pro", "256GB", "12GB", "Titanium", 89999, 84999, 4.5),
        ("Oppo", "Find X8", "256GB", "12GB", "Space Black", 69999, 64999, 4.4),
        ("Motorola", "Edge 50 Ultra", "256GB", "12GB", "Forest Grey", 59999, 52999, 4.3),
        ("Nothing", "Phone (2a)", "256GB", "12GB", "White", 27999, 24999, 4.4),
        ("Realme", "GT 7 Pro", "256GB", "12GB", "Meadow Green", 59999, 54999, 4.4),
        ("Samsung", "Galaxy A56", "128GB", "8GB", "Awesome Navy", 39999, 34999, 4.3),
        ("Apple", "iPhone 15", "128GB", "6GB", "Blue", 69900, 64900, 4.8),
    ]
    rows = []
    for i, (brand, model, storage, ram, color, orig, disc, rating) in enumerate(phones):
        img = PHONE_IMGS[i % len(PHONE_IMGS)]
        rows.append(
            f'  {{ brand: "{brand}", model: "{model}", storage: "{storage}", ram: "{ram}", color: "{color}", '
            f'original: {orig}, price: {disc}, rating: {rating}, img: "{img}" }}'
        )
    return GeneratedFile(
        path="src/components/ProductGrid.tsx",
        content=(
            "import { Heart, GitCompare, Star } from 'lucide-react'\n"
            "import { Button } from './Button'\n\n"
            f"const products = [\n" + ",\n".join(rows) + "\n]\n\n"
            "function inr(n: number) {\n"
            "  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)\n"
            "}\n\n"
            "export function ProductGrid({ title = 'Featured Smartphones', limit }: { title?: string; limit?: number }) {\n"
            "  const items = typeof limit === 'number' ? products.slice(0, limit) : products\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-7xl px-4 py-14\">\n"
            "      <div className=\"flex items-end justify-between gap-3\">\n"
            "        <h2 className=\"text-3xl font-bold tracking-tight\">{title}</h2>\n"
            "        <a href=\"#/smartphones\" className=\"text-sm font-semibold text-blue-600 hover:underline\">View all</a>\n"
            "      </div>\n"
            "      <div className=\"mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4\">\n"
            "        {items.map((p) => (\n"
            "          <article key={p.brand + p.model} className=\"group flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg\">\n"
            "            <div className=\"relative overflow-hidden bg-slate-50\">\n"
            "              <img src={p.img} alt={`${p.brand} ${p.model}`} className=\"h-48 w-full object-cover transition duration-500 group-hover:scale-110\" loading=\"lazy\" />\n"
            "              <span className=\"absolute left-3 top-3 rounded-full bg-blue-600 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-white\">EMI Available</span>\n"
            "              <div className=\"absolute right-3 top-3 flex gap-1\">\n"
            "                <button type=\"button\" className=\"rounded-full bg-white/90 p-2 shadow\" aria-label=\"Wishlist\"><Heart className=\"h-4 w-4\" /></button>\n"
            "                <button type=\"button\" className=\"rounded-full bg-white/90 p-2 shadow\" aria-label=\"Compare\"><GitCompare className=\"h-4 w-4\" /></button>\n"
            "              </div>\n"
            "            </div>\n"
            "            <div className=\"flex flex-1 flex-col p-4\">\n"
            "              <p className=\"text-xs font-semibold uppercase tracking-wide text-slate-500\">{p.brand}</p>\n"
            "              <h3 className=\"mt-1 text-base font-semibold\">{p.model}</h3>\n"
            "              <p className=\"mt-1 text-xs text-slate-500\">{p.storage} · {p.ram} · {p.color}</p>\n"
            "              <div className=\"mt-2 flex items-center gap-1 text-amber-500\"><Star className=\"h-4 w-4 fill-current\" /><span className=\"text-sm font-medium text-slate-700\">{p.rating}</span></div>\n"
            "              <div className=\"mt-3 flex items-baseline gap-2\">\n"
            "                <span className=\"text-lg font-bold\">{inr(p.price)}</span>\n"
            "                <span className=\"text-sm text-slate-400 line-through\">{inr(p.original)}</span>\n"
            "              </div>\n"
            "              <div className=\"mt-auto grid grid-cols-2 gap-2 pt-4\">\n"
            f"                <Button className=\"w-full px-2 py-2 text-xs\">Add to Cart</Button>\n"
            "                <Button variant=\"dark\" className=\"w-full px-2 py-2 text-xs\">Buy Now</Button>\n"
            "              </div>\n"
            "            </div>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _deals(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/DealsBanner.tsx",
        content=(
            "import { useEffect, useState } from 'react'\n"
            "import { Button } from './Button'\n\n"
            "export function DealsBanner() {\n"
            "  const [left, setLeft] = useState(12 * 3600 + 34 * 60 + 56)\n"
            "  useEffect(() => {\n"
            "    const id = setInterval(() => setLeft((s) => (s > 0 ? s - 1 : 0)), 1000)\n"
            "    return () => clearInterval(id)\n"
            "  }, [])\n"
            "  const h = String(Math.floor(left / 3600)).padStart(2, '0')\n"
            "  const m = String(Math.floor((left % 3600) / 60)).padStart(2, '0')\n"
            "  const s = String(left % 60).padStart(2, '0')\n"
            "  return (\n"
            f"    <section className=\"mx-auto max-w-7xl px-4 py-8\">\n"
            f"      <div className=\"overflow-hidden rounded-3xl bg-gradient-to-r from-blue-700 via-blue-600 to-slate-900 p-8 text-white shadow-xl sm:p-12\">\n"
            "        <p className=\"text-sm font-semibold uppercase tracking-[0.2em] text-blue-100\">Today's Deals</p>\n"
            "        <h2 className=\"mt-3 text-4xl font-bold sm:text-5xl\">Up To 40% OFF</h2>\n"
            "        <p className=\"mt-3 text-blue-100\">Limited-time offers on flagship smartphones and accessories.</p>\n"
            "        <div className=\"mt-6 flex flex-wrap items-center gap-3\">\n"
            "          {[h, m, s].map((v, i) => (\n"
            "            <div key={i} className=\"rounded-xl bg-white/15 px-4 py-3 text-center backdrop-blur\">\n"
            "              <div className=\"text-2xl font-bold tabular-nums\">{v}</div>\n"
            "              <div className=\"text-[10px] uppercase tracking-wide text-blue-100\">{['Hrs','Min','Sec'][i]}</div>\n"
            "            </div>\n"
            "          ))}\n"
            "          <Button href=\"#/offers\" variant=\"ghost\" className=\"ml-2 border-white/30 bg-white text-slate-900 hover:bg-blue-50\">Shop Deals</Button>\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _why_us() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/WhyChooseUs.tsx",
        content=(
            "const items = [\n"
            "  '100% Genuine Products',\n"
            "  'Brand Warranty',\n"
            "  'Secure Payments',\n"
            "  'Fast Delivery',\n"
            "  'Easy Returns',\n"
            "  'Expert Customer Support',\n"
            "]\n"
            "export function WhyChooseUs() {\n"
            "  return (\n"
            "    <section className=\"bg-slate-50\">\n"
            "      <div className=\"mx-auto max-w-7xl px-4 py-14\">\n"
            "        <h2 className=\"text-3xl font-bold tracking-tight\">Why Choose Us</h2>\n"
            "        <div className=\"mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3\">\n"
            "          {items.map((item) => (\n"
            "            <div key={item} className=\"rounded-2xl border border-slate-200 bg-white p-5 shadow-sm\">\n"
            "              <div className=\"flex h-10 w-10 items-center justify-center rounded-full bg-blue-50 text-lg font-bold text-blue-700\">✓</div>\n"
            "              <h3 className=\"mt-3 font-semibold\">{item}</h3>\n"
            "            </div>\n"
            "          ))}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _accessories() -> GeneratedFile:
    items = [
        ("Wireless Earbuds", ACC_IMGS[0], 2999),
        ("Power Banks", ACC_IMGS[2], 1999),
        ("Smart Watches", ACC_IMGS[1], 8999),
        ("Phone Cases", ACC_IMGS[0], 699),
        ("Chargers", ACC_IMGS[3], 1499),
        ("Cables", ACC_IMGS[3], 499),
        ("Bluetooth Speakers", ACC_IMGS[1], 3499),
        ("Car Chargers", ACC_IMGS[2], 999),
    ]
    rows = ",\n".join(f'  {{ name: "{n}", img: "{i}", price: {p} }}' for n, i, p in items)
    return GeneratedFile(
        path="src/components/AccessoriesGrid.tsx",
        content=(
            f"const items = [\n{rows}\n]\n"
            "export function AccessoriesGrid() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-7xl px-4 py-14\">\n"
            "      <h2 className=\"text-3xl font-bold tracking-tight\">Latest Accessories</h2>\n"
            "      <div className=\"mt-8 grid grid-cols-2 gap-4 md:grid-cols-4\">\n"
            "        {items.map((item) => (\n"
            "          <article key={item.name} className=\"overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md\">\n"
            "            <img src={item.img} alt={item.name} className=\"h-36 w-full object-cover\" loading=\"lazy\" />\n"
            "            <div className=\"p-4\">\n"
            "              <h3 className=\"font-semibold\">{item.name}</h3>\n"
            "              <p className=\"mt-1 text-sm text-slate-600\">From ₹{item.price}</p>\n"
            "            </div>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _reviews() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Reviews.tsx",
        content=(
            "const reviews = [\n"
            "  { name: 'Rahul S.', text: 'Bought my S25 Ultra here — genuine product, quick delivery, and helpful staff.', rating: 5 },\n"
            "  { name: 'Ananya P.', text: 'Best EMI options in town. MobileHub made upgrading my iPhone easy.', rating: 5 },\n"
            "  { name: 'Vikram D.', text: 'Transparent pricing and proper warranty. Highly recommended.', rating: 5 },\n"
            "]\n"
            "export function Reviews() {\n"
            "  return (\n"
            "    <section className=\"bg-white\">\n"
            "      <div className=\"mx-auto max-w-7xl px-4 py-14\">\n"
            "        <h2 className=\"text-3xl font-bold tracking-tight\">Customer Reviews</h2>\n"
            "        <div className=\"mt-8 grid gap-4 md:grid-cols-3\">\n"
            "          {reviews.map((r) => (\n"
            "            <blockquote key={r.name} className=\"rounded-2xl border border-slate-200 bg-slate-50 p-6 shadow-sm\">\n"
            "              <div className=\"text-amber-500\">{'★'.repeat(r.rating)}</div>\n"
            "              <p className=\"mt-3 text-sm leading-relaxed text-slate-700\">“{r.text}”</p>\n"
            "              <footer className=\"mt-4 text-sm font-semibold\">{r.name}</footer>\n"
            "            </blockquote>\n"
            "          ))}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _gallery() -> GeneratedFile:
    rows = ",\n".join(f'  "{u}"' for u in STORE_IMGS)
    return GeneratedFile(
        path="src/components/StoreGallery.tsx",
        content=(
            f"const shots = [\n{rows}\n]\n"
            "export function StoreGallery() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-7xl px-4 py-14\">\n"
            "      <h2 className=\"text-3xl font-bold tracking-tight\">Store Gallery</h2>\n"
            "      <div className=\"mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4\">\n"
            "        {shots.map((src, i) => (\n"
            "          <img key={src} src={src} alt={`Store photo ${i + 1}`} className=\"h-48 w-full rounded-2xl object-cover shadow-sm\" loading=\"lazy\" />\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _newsletter(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Newsletter.tsx",
        content=(
            "export function Newsletter() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-7xl px-4 py-8\">\n"
            f"      <div className=\"rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-50 to-blue-50 p-8 sm:p-10\">\n"
            "        <h2 className=\"text-3xl font-bold tracking-tight\">Get Exclusive Mobile Deals</h2>\n"
            "        <p className=\"mt-2 text-slate-600\">Subscribe for launches, festival offers, and EMI updates.</p>\n"
            "        <form className=\"mt-6 flex max-w-xl flex-col gap-3 sm:flex-row\" onSubmit={(e) => e.preventDefault()}>\n"
            "          <input type=\"email\" required placeholder=\"Enter your email\" className=\"flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500\" />\n"
            f"          <button type=\"submit\" className=\"rounded-xl px-5 py-3 text-sm font-semibold text-white\" style={{{{ backgroundColor: '{primary}' }}}}>Subscribe</button>\n"
            "        </form>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _contact_block(brand: str, primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ContactBlock.tsx",
        content=(
            f"export function ContactBlock() {{\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-7xl px-4 py-14\">\n"
            "      <h2 className=\"text-3xl font-bold tracking-tight\">Visit Our Store</h2>\n"
            "      <div className=\"mt-8 grid gap-6 lg:grid-cols-2\">\n"
            "        <div className=\"rounded-2xl border border-slate-200 bg-white p-6 shadow-sm\">\n"
            f"          <p className=\"font-semibold\">{brand}</p>\n"
            "          <p className=\"mt-3 text-sm text-slate-600\">12 MG Road, Commercial Street, Bengaluru, Karnataka 560001</p>\n"
            "          <p className=\"mt-2 text-sm\">Phone: <a className=\"text-blue-600\" href=\"tel:+919876543210\">+91 98765 43210</a></p>\n"
            f"          <p className=\"mt-1 text-sm\">Email: <a className=\"text-blue-600\" href=\"mailto:hello@{brand.lower().replace(' ', '')}.com\">hello@{brand.lower().replace(' ', '')}.com</a></p>\n"
            "          <p className=\"mt-4 text-sm text-slate-600\">Business Hours: Mon–Sun · 10:00 AM – 9:00 PM</p>\n"
            "        </div>\n"
            "        <div className=\"overflow-hidden rounded-2xl border border-slate-200 shadow-sm\">\n"
            "          <iframe title=\"Store map\" className=\"h-72 w-full\" loading=\"lazy\" referrerPolicy=\"no-referrer-when-downgrade\" src=\"https://maps.google.com/maps?q=Commercial%20Street%20Bengaluru&t=&z=14&ie=UTF8&iwloc=&output=embed\" />\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _footer(brand: str, plan: ProjectPlan) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/StoreFooter.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n\n"
            "export function StoreFooter() {\n"
            "  return (\n"
            "    <footer className=\"border-t border-slate-800 bg-slate-950 text-slate-300\">\n"
            "      <div className=\"mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:grid-cols-2 lg:grid-cols-4\">\n"
            "        <div>\n"
            f"          <p className=\"text-lg font-bold text-white\">{brand}</p>\n"
            "          <p className=\"mt-3 text-sm leading-relaxed\">Premium smartphones & accessories with genuine warranty and expert support.</p>\n"
            "        </div>\n"
            "        <div>\n"
            "          <p className=\"font-semibold text-white\">Quick Links</p>\n"
            "          <div className=\"mt-3 grid gap-2 text-sm\">\n"
            "            <Link to=\"/\">Home</Link><Link to=\"/smartphones\">Smartphones</Link><Link to=\"/offers\">Offers</Link><Link to=\"/about\">About</Link>\n"
            "          </div>\n"
            "        </div>\n"
            "        <div>\n"
            "          <p className=\"font-semibold text-white\">Support</p>\n"
            "          <div className=\"mt-3 grid gap-2 text-sm\">\n"
            "            <Link to=\"/faq\">FAQ</Link><a href=\"#\">Warranty Policy</a><a href=\"#\">Shipping Policy</a><a href=\"#\">Returns</a>\n"
            "          </div>\n"
            "        </div>\n"
            "        <div>\n"
            "          <p className=\"font-semibold text-white\">Legal</p>\n"
            "          <div className=\"mt-3 grid gap-2 text-sm\">\n"
            "            <a href=\"#\">Privacy Policy</a><a href=\"#\">Terms & Conditions</a><Link to=\"/contact\">Contact</Link>\n"
            "          </div>\n"
            "        </div>\n"
            "      </div>\n"
            f"      <div className=\"border-t border-slate-800 py-4 text-center text-xs text-slate-500\">© {{new Date().getFullYear()}} {brand}. All rights reserved.</div>\n"
            "    </footer>\n"
            "  )\n"
            "}\n"
        ),
    )


def _whatsapp(brand: str, phone: str) -> GeneratedFile:
    msg = f"Hello {brand}, I'm interested in purchasing a smartphone. Please help me choose the best model and share today's offers."
    from urllib.parse import quote

    url = f"https://wa.me/{phone.lstrip('+')}?text={quote(msg)}"
    return GeneratedFile(
        path="src/components/WhatsAppFloat.tsx",
        content=(
            f"export function WhatsAppFloat() {{\n"
            "  return (\n"
            f"    <a href=\"{url}\" target=\"_blank\" rel=\"noreferrer\" className=\"fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500 text-2xl text-white shadow-xl shadow-emerald-500/30 transition hover:scale-105\" aria-label=\"WhatsApp\">\n"
            "      ☎\n"
            "    </a>\n"
            "  )\n"
            "}\n"
        ),
    )


def _faq() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/FAQList.tsx",
        content=(
            "const faqs = [\n"
            "  { q: 'Do you offer shipping?', a: 'Yes — free delivery on orders above ₹999 across major cities.' },\n"
            "  { q: 'What is your return policy?', a: 'Easy returns within 7 days for sealed / unused products as per brand policy.' },\n"
            "  { q: 'Is warranty included?', a: 'All smartphones include official brand warranty.' },\n"
            "  { q: 'Can I buy on EMI?', a: 'Yes, EMI is available on major credit cards and select finance partners.' },\n"
            "  { q: 'Which payment methods are accepted?', a: 'UPI, cards, net banking, wallets, and cash on delivery where available.' },\n"
            "  { q: 'Do you accept exchanges?', a: 'Yes, exchange offers are available on select smartphone models.' },\n"
            "]\n"
            "export function FAQList() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-3xl px-4 py-14\">\n"
            "      <h1 className=\"text-3xl font-bold tracking-tight\">FAQ</h1>\n"
            "      <div className=\"mt-8 space-y-3\">\n"
            "        {faqs.map((f) => (\n"
            "          <details key={f.q} className=\"rounded-2xl border border-slate-200 bg-white p-4 shadow-sm open:shadow-md\">\n"
            "            <summary className=\"cursor-pointer font-semibold\">{f.q}</summary>\n"
            "            <p className=\"mt-2 text-sm leading-relaxed text-slate-600\">{f.a}</p>\n"
            "          </details>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _filters_panel(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ShopFilters.tsx",
        content=(
            "const groups = [\n"
            "  { label: 'Brand', options: ['Apple', 'Samsung', 'OnePlus', 'Xiaomi', 'Google'] },\n"
            "  { label: 'RAM', options: ['6GB', '8GB', '12GB', '16GB'] },\n"
            "  { label: 'Storage', options: ['128GB', '256GB', '512GB'] },\n"
            "  { label: 'Network', options: ['5G', '4G'] },\n"
            "]\n"
            "export function ShopFilters() {\n"
            "  return (\n"
            "    <aside className=\"rounded-2xl border border-slate-200 bg-white p-4 shadow-sm\">\n"
            "      <h2 className=\"font-semibold\">Filters</h2>\n"
            "      <div className=\"mt-4 space-y-5\">\n"
            "        {groups.map((g) => (\n"
            "          <div key={g.label}>\n"
            "            <p className=\"text-xs font-semibold uppercase tracking-wide text-slate-500\">{g.label}</p>\n"
            "            <div className=\"mt-2 space-y-2\">\n"
            "              {g.options.map((o) => (\n"
            "                <label key={o} className=\"flex items-center gap-2 text-sm\">\n"
            "                  <input type=\"checkbox\" className=\"rounded border-slate-300\" /> {o}\n"
            "                </label>\n"
            "              ))}\n"
            "            </div>\n"
            "          </div>\n"
            "        ))}\n"
            "        <div>\n"
            "          <p className=\"text-xs font-semibold uppercase tracking-wide text-slate-500\">Price</p>\n"
            "          <input type=\"range\" min={10000} max={160000} className=\"mt-2 w-full\" />\n"
            "        </div>\n"
            "      </div>\n"
            "    </aside>\n"
            "  )\n"
            "}\n"
        ),
    )


def _home_page(brand: str, primary: str) -> str:
    return (
        "import { AnnouncementBar } from '../components/AnnouncementBar'\n"
        "import { StoreHero } from '../components/StoreHero'\n"
        "import { BrandStrip } from '../components/BrandStrip'\n"
        "import { CategoryGrid } from '../components/CategoryGrid'\n"
        "import { ProductGrid } from '../components/ProductGrid'\n"
        "import { DealsBanner } from '../components/DealsBanner'\n"
        "import { WhyChooseUs } from '../components/WhyChooseUs'\n"
        "import { AccessoriesGrid } from '../components/AccessoriesGrid'\n"
        "import { Reviews } from '../components/Reviews'\n"
        "import { StoreGallery } from '../components/StoreGallery'\n"
        "import { Newsletter } from '../components/Newsletter'\n"
        "import { ContactBlock } from '../components/ContactBlock'\n"
        "import { WhatsAppFloat } from '../components/WhatsAppFloat'\n\n"
        "export default function HomePage() {\n"
        "  return (\n"
        "    <div className=\"bg-white text-slate-900\">\n"
        "      <AnnouncementBar />\n"
        "      <StoreHero />\n"
        "      <BrandStrip />\n"
        "      <CategoryGrid />\n"
        "      <ProductGrid limit={12} />\n"
        "      <DealsBanner />\n"
        "      <WhyChooseUs />\n"
        "      <AccessoriesGrid />\n"
        "      <Reviews />\n"
        "      <StoreGallery />\n"
        "      <Newsletter />\n"
        "      <ContactBlock />\n"
        "      <WhatsAppFloat />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _shop_page(comp: str, title: str, primary: str) -> str:
    return (
        "import { ProductGrid } from '../components/ProductGrid'\n"
        "import { ShopFilters } from '../components/ShopFilters'\n"
        "import { WhatsAppFloat } from '../components/WhatsAppFloat'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-slate-50\">\n"
        "      <div className=\"mx-auto grid max-w-7xl gap-6 px-4 py-10 lg:grid-cols-[240px_1fr]\">\n"
        "        <ShopFilters />\n"
        "        <div>\n"
        "          <div className=\"mb-4 flex flex-wrap items-center justify-between gap-3\">\n"
        f"            <h1 className=\"text-3xl font-bold\">{title}</h1>\n"
        "            <select className=\"rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm\">\n"
        "              <option>Sort by: Popular</option>\n"
        "              <option>Price: Low to High</option>\n"
        "              <option>Price: High to Low</option>\n"
        "              <option>Rating</option>\n"
        "            </select>\n"
        "          </div>\n"
        f"          <ProductGrid title=\"{title}\" />\n"
        "          <div className=\"flex justify-center gap-2 pb-10\">\n"
        "            {[1,2,3].map((n) => <button key={n} type=\"button\" className=\"h-10 w-10 rounded-xl border border-slate-300 bg-white text-sm font-semibold\">{n}</button>)}\n"
        "          </div>\n"
        "        </div>\n"
        "      </div>\n"
        "      <WhatsAppFloat />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _accessories_page(comp: str) -> str:
    return (
        "import { AccessoriesGrid } from '../components/AccessoriesGrid'\n"
        "import { WhatsAppFloat } from '../components/WhatsAppFloat'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-white\"><AccessoriesGrid /><WhatsAppFloat /></div>\n"
        "  )\n"
        "}\n"
    )


def _offers_page(comp: str, primary: str) -> str:
    return (
        "import { DealsBanner } from '../components/DealsBanner'\n"
        "import { ProductGrid } from '../components/ProductGrid'\n"
        "import { WhatsAppFloat } from '../components/WhatsAppFloat'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-white\">\n"
        "      <DealsBanner />\n"
        "      <ProductGrid title=\"Offer Zone\" limit={8} />\n"
        "      <WhatsAppFloat />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _about_page(comp: str, brand: str) -> str:
    return (
        "import { StoreGallery } from '../components/StoreGallery'\n"
        "import { WhyChooseUs } from '../components/WhyChooseUs'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-white\">\n"
        "      <section className=\"mx-auto max-w-7xl px-4 py-14\">\n"
        f"        <h1 className=\"text-4xl font-bold tracking-tight\">About {brand}</h1>\n"
        f"        <p className=\"mt-4 max-w-3xl text-lg leading-relaxed text-slate-600\">{brand} is a premium electronics destination for smartphones and accessories — built on trust, genuine products, and expert guidance.</p>\n"
        "        <div className=\"mt-8 grid gap-4 md:grid-cols-3\">\n"
        "          <article className=\"rounded-2xl border border-slate-200 p-5 shadow-sm\"><h2 className=\"font-semibold\">Mission</h2><p className=\"mt-2 text-sm text-slate-600\">Bring premium mobiles to everyone with transparent pricing.</p></article>\n"
        "          <article className=\"rounded-2xl border border-slate-200 p-5 shadow-sm\"><h2 className=\"font-semibold\">Vision</h2><p className=\"mt-2 text-sm text-slate-600\">Become the most trusted mobile destination in India.</p></article>\n"
        "          <article className=\"rounded-2xl border border-slate-200 p-5 shadow-sm\"><h2 className=\"font-semibold\">Trust</h2><p className=\"mt-2 text-sm text-slate-600\">Official warranty, secure payments, and happy customers.</p></article>\n"
        "        </div>\n"
        "      </section>\n"
        "      <WhyChooseUs />\n"
        "      <StoreGallery />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _contact_page(comp: str, brand: str, primary: str) -> str:
    return (
        "import { ContactBlock } from '../components/ContactBlock'\n"
        "import { WhatsAppFloat } from '../components/WhatsAppFloat'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-slate-50\">\n"
        "      <section className=\"mx-auto max-w-7xl px-4 py-14\">\n"
        "        <h1 className=\"text-4xl font-bold\">Contact Us</h1>\n"
        "        <form className=\"mt-8 grid max-w-xl gap-3 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm\" onSubmit={(e) => e.preventDefault()}>\n"
        "          <input className=\"rounded-xl border border-slate-300 px-3 py-2 text-sm\" placeholder=\"Your name\" />\n"
        "          <input className=\"rounded-xl border border-slate-300 px-3 py-2 text-sm\" placeholder=\"Phone / WhatsApp\" />\n"
        "          <input className=\"rounded-xl border border-slate-300 px-3 py-2 text-sm\" placeholder=\"Email\" />\n"
        "          <textarea className=\"min-h-28 rounded-xl border border-slate-300 px-3 py-2 text-sm\" placeholder=\"How can we help?\" />\n"
        f"          <button type=\"submit\" className=\"rounded-xl px-4 py-2.5 text-sm font-semibold text-white\" style={{{{ backgroundColor: '{primary}' }}}}>Send message</button>\n"
        "        </form>\n"
        "      </section>\n"
        "      <ContactBlock />\n"
        "      <WhatsAppFloat />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _faq_page(comp: str) -> str:
    return (
        "import { FAQList } from '../components/FAQList'\n"
        "import { WhatsAppFloat } from '../components/WhatsAppFloat'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-slate-50\"><FAQList /><WhatsAppFloat /></div>\n"
        "  )\n"
        "}\n"
    )


def _product_detail_page(comp: str, primary: str) -> str:
    img = PHONE_IMGS[0]
    return (
        "import { Button } from '../components/Button'\n"
        "import { ProductGrid } from '../components/ProductGrid'\n"
        "import { WhatsAppFloat } from '../components/WhatsAppFloat'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-white\">\n"
        "      <section className=\"mx-auto grid max-w-7xl gap-8 px-4 py-12 lg:grid-cols-2\">\n"
        f"        <img src=\"{img}\" alt=\"Product\" className=\"h-96 w-full rounded-3xl object-cover shadow-lg\" />\n"
        "        <div>\n"
        "          <p className=\"text-sm font-semibold uppercase tracking-wide text-slate-500\">Apple</p>\n"
        "          <h1 className=\"mt-2 text-4xl font-bold\">iPhone 16 Pro</h1>\n"
        "          <p className=\"mt-3 text-2xl font-bold\">₹1,39,900 <span className=\"text-base font-normal text-slate-400 line-through\">₹1,49,900</span></p>\n"
        "          <p className=\"mt-2 text-sm text-slate-600\">EMI from ₹11,658/month · Official brand warranty</p>\n"
        "          <div className=\"mt-6 flex flex-wrap gap-2\">\n"
        "            {['128GB','256GB','512GB'].map((v) => <button key={v} type=\"button\" className=\"rounded-xl border border-slate-300 px-3 py-2 text-sm\">{v}</button>)}\n"
        "          </div>\n"
        "          <div className=\"mt-6 flex flex-wrap gap-3\">\n"
        "            <Button>Add to Cart</Button>\n"
        "            <Button variant=\"dark\">Buy Now</Button>\n"
        "          </div>\n"
        "          <ul className=\"mt-8 space-y-2 text-sm text-slate-600\">\n"
        "            <li>• A18 Pro chip · ProMotion display</li>\n"
        "            <li>• Advanced camera system</li>\n"
        "            <li>• 5G connectivity · Face ID</li>\n"
        "          </ul>\n"
        "        </div>\n"
        "      </section>\n"
        "      <ProductGrid title=\"Related Products\" limit={4} />\n"
        "      <WhatsAppFloat />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )

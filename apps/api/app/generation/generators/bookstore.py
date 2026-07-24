"""Online bookstore specialty — search, buy, read, and download PDFs."""

from __future__ import annotations

import json

from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements
from app.generation.planner.niches import invent_brand_name, resolve_niche

BOOK_COVERS = [
    "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1476275466078-4007374efbbe?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=600&q=80",
    "https://images.unsplash.com/photo-1519682337058-a94d519337bc?auto=format&fit=crop&w=600&q=80",
]

# Public-domain sample PDF for download demos
SAMPLE_PDF = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"

DEFAULT_BOOKS = [
    ("The Quiet Atlas", "Mira Ellison", "Fiction", 18.0, "A cartographer maps cities that only exist in memory."),
    ("Code & Clay", "Devon Park", "Technology", 24.0, "Builders, craft, and the soft edges of hard systems."),
    ("Kitchen Midnight", "Asha Reddy", "Food", 16.0, "Recipes and stories from kitchens that never sleep."),
    ("Orbit Letters", "Jules Hart", "Sci-Fi", 21.0, "Postcards from the far side of a quiet colony."),
    ("Ink & Tide", "Noor Alami", "Poetry", 14.0, "Shoreline verses for restless evenings."),
    ("The Long Table", "Eli Cho", "Non-Fiction", 22.0, "How shared meals rebuild neighborhoods."),
    ("Paper Lanterns", "Sofia Mendes", "Children", 12.0, "A festival of light for curious readers."),
    ("Signal Bloom", "Ravi Shah", "Business", 26.0, "Growing a brand without burning the soil."),
    ("Glass Hour", "Lena Vogt", "Mystery", 19.0, "A librarian finds a clock that runs backward."),
    ("Wild Margin", "Tomás Rivera", "Nature", 17.0, "Field notes from forests that keep secrets."),
    ("Northbound", "Hannah Cole", "Travel", 20.0, "Trains, journals, and the courage to leave."),
    ("Soft Circuits", "Priya Nair", "Technology", 23.0, "Human-centered product craft for builders."),
]


def generate_bookstore(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    analysis = requirements.analysis
    prompt = analysis.raw_prompt or ""
    niche = resolve_niche(analysis.website_type_id, prompt)
    brand = invent_brand_name(getattr(analysis, "brand_name", "") or plan.project_name or "", niche)
    accent = "#0F766E"  # editorial teal — fits reading, not marketing purple

    books = [
        {
            "id": f"b{i+1}",
            "title": title,
            "author": author,
            "category": cat,
            "price": price,
            "cover": BOOK_COVERS[i % len(BOOK_COVERS)],
            "synopsis": synopsis,
            "pdfUrl": SAMPLE_PDF,
            "pages": 180 + (i * 17) % 220,
        }
        for i, (title, author, cat, price, synopsis) in enumerate(DEFAULT_BOOKS)
    ]

    files: list[GeneratedFile] = [
        _catalog(brand, books),
        _store_hook(),
        _theme_hook(),
        _navbar(brand, plan, accent),
        _footer(brand, plan),
        _book_card(accent),
        _search_bar(),
        _reader(),
        GeneratedFile(path="src/components/Navbar.tsx", content="export { BookNavbar as Navbar } from './BookNavbar'\n"),
        GeneratedFile(path="src/components/Footer.tsx", content="export { BookFooter as Footer } from './BookFooter'\n"),
        GeneratedFile(
            path="src/components/Hero.tsx",
            content=(
                "import { Link } from 'react-router-dom'\n"
                "import { brandName, brandTagline } from '../data/catalog'\n\n"
                "export function Hero() {\n"
                "  return (\n"
                "    <section className=\"relative overflow-hidden bg-[#0B1220] text-white\">\n"
                f"      <div className=\"absolute inset-0 opacity-40\" style={{{{ backgroundImage: `url('{BOOK_COVERS[2]}')`, backgroundSize: 'cover', backgroundPosition: 'center' }}}} />\n"
                "      <div className=\"absolute inset-0 bg-gradient-to-r from-[#0B1220] via-[#0B1220]/90 to-[#0B1220]/40\" />\n"
                "      <div className=\"relative mx-auto flex min-h-[68vh] max-w-6xl flex-col justify-end px-4 pb-16 pt-28 sm:px-6\">\n"
                "        <p className=\"text-[11px] font-semibold uppercase tracking-[0.28em] text-teal-300\">Online bookstore</p>\n"
                "        <h1 className=\"mt-3 max-w-2xl font-serif text-4xl leading-tight sm:text-5xl md:text-6xl\">{brandName}</h1>\n"
                "        <p className=\"mt-4 max-w-xl text-base text-stone-300\">{brandTagline}</p>\n"
                "        <div className=\"mt-8 flex flex-wrap gap-3\">\n"
                "          <Link to=\"/browse\" className=\"rounded-full bg-teal-600 px-6 py-3 text-[11px] font-semibold uppercase tracking-wider text-white hover:bg-teal-500\">Browse books</Link>\n"
                "          <Link to=\"/library\" className=\"rounded-full border border-white/30 px-6 py-3 text-[11px] font-semibold uppercase tracking-wider text-white hover:border-white/60\">My library</Link>\n"
                "        </div>\n"
                "      </div>\n"
                "    </section>\n"
                "  )\n"
                "}\n"
            ),
        ),
        GeneratedFile(
            path="src/components/Button.tsx",
            content=(
                "type Props = { children: React.ReactNode; className?: string; onClick?: () => void; type?: 'button' | 'submit' }\n"
                "export function Button({ children, className = '', onClick, type = 'button' }: Props) {\n"
                f"  return <button type={{type}} onClick={{onClick}} className={{`inline-flex items-center justify-center rounded-full bg-teal-700 px-5 py-2.5 text-xs font-semibold uppercase tracking-wider text-white hover:bg-teal-600 ${{className}}`}}>{{children}}</button>\n"
                "}\n"
            ),
        ),
        GeneratedFile(
            path="src/components/Card.tsx",
            content=(
                "import type { ReactNode } from 'react'\n"
                "export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {\n"
                "  return <div className={`rounded-2xl border border-stone-200 bg-white p-5 ${className}`}>{children}</div>\n"
                "}\n"
            ),
        ),
    ]

    for route in plan.routes:
        page = route["page"].lower()
        comp = route["component"]
        if route["path"] == "/":
            body = _home_page(comp)
        elif any(k in page for k in ("browse", "shop", "catalog", "search")):
            body = _browse_page(comp)
        elif "library" in page or "read" in page:
            body = _library_page(comp)
        elif "cart" in page or "checkout" in page:
            body = _cart_page(comp)
        elif "about" in page:
            body = _about_page(comp, brand)
        elif "contact" in page:
            body = _contact_page(comp, brand, accent)
        else:
            body = _browse_page(comp)
        files.append(GeneratedFile(path=f"src/pages/{comp}.tsx", content=body))

    # Ensure core commerce pages exist even if planner was thin
    by = {f.path: f for f in files}
    for path, content in (
        ("src/pages/BrowsePage.tsx", _browse_page("BrowsePage")),
        ("src/pages/LibraryPage.tsx", _library_page("LibraryPage")),
        ("src/pages/CartPage.tsx", _cart_page("CartPage")),
    ):
        if path not in by and any(p in path.lower() for p in ("browse", "library", "cart")):
            # Only add if route exists
            pass
    wanted = {r["component"] for r in plan.routes}
    for name, factory in (
        ("BrowsePage", _browse_page),
        ("LibraryPage", _library_page),
        ("CartPage", _cart_page),
    ):
        if name in wanted and f"src/pages/{name}.tsx" not in by:
            files.append(GeneratedFile(path=f"src/pages/{name}.tsx", content=factory(name)))

    return list({f.path: f for f in files}.values())


def _catalog(brand: str, books: list[dict]) -> GeneratedFile:
    tagline = f"Buy, read, search, and download — your online bookshelf at {brand}."
    return GeneratedFile(
        path="src/data/catalog.ts",
        content=(
            "export type Book = {\n"
            "  id: string\n  title: string\n  author: string\n  category: string\n  price: number\n"
            "  cover: string\n  synopsis: string\n  pdfUrl: string\n  pages: number\n"
            "}\n\n"
            f"export const brandName = {json.dumps(brand)}\n"
            f"export const brandTagline = {json.dumps(tagline)}\n"
            f"export const books: Book[] = {json.dumps(books, indent=2)}\n\n"
            "export function searchBooks(q: string, category = 'all') {\n"
            "  const needle = q.trim().toLowerCase()\n"
            "  return books.filter((b) => {\n"
            "    if (category !== 'all' && b.category !== category) return false\n"
            "    if (!needle) return true\n"
            "    return `${b.title} ${b.author} ${b.category} ${b.synopsis}`.toLowerCase().includes(needle)\n"
            "  })\n"
            "}\n"
        ),
    )


def _theme_hook() -> GeneratedFile:
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


def _store_hook() -> GeneratedFile:
    return GeneratedFile(
        path="src/hooks/useBookStore.ts",
        content=(
            "import { useEffect, useState } from 'react'\n"
            "import type { Book } from '../data/catalog'\n"
            "import { books } from '../data/catalog'\n\n"
            "type State = { cart: string[]; owned: string[] }\n\n"
            "const KEY = 'ember-bookstore-v1'\n\n"
            "function load(): State {\n"
            "  try {\n"
            "    const raw = localStorage.getItem(KEY)\n"
            "    if (raw) return JSON.parse(raw) as State\n"
            "  } catch {}\n"
            "  return { cart: [], owned: [] }\n"
            "}\n\n"
            "function save(s: State) {\n"
            "  localStorage.setItem(KEY, JSON.stringify(s))\n"
            "}\n\n"
            "export function useBookStore() {\n"
            "  const [state, setState] = useState<State>({ cart: [], owned: [] })\n"
            "  useEffect(() => { setState(load()) }, [])\n"
            "  const persist = (next: State) => { setState(next); save(next) }\n"
            "  const cartBooks = state.cart.map((id) => books.find((b) => b.id === id)).filter(Boolean) as Book[]\n"
            "  const ownedBooks = state.owned.map((id) => books.find((b) => b.id === id)).filter(Boolean) as Book[]\n"
            "  const addToCart = (id: string) => {\n"
            "    if (state.owned.includes(id) || state.cart.includes(id)) return\n"
            "    persist({ ...state, cart: [...state.cart, id] })\n"
            "  }\n"
            "  const removeFromCart = (id: string) => persist({ ...state, cart: state.cart.filter((x) => x !== id) })\n"
            "  const checkout = () => {\n"
            "    const owned = Array.from(new Set([...state.owned, ...state.cart]))\n"
            "    persist({ cart: [], owned })\n"
            "  }\n"
            "  const owns = (id: string) => state.owned.includes(id)\n"
            "  const inCart = (id: string) => state.cart.includes(id)\n"
            "  const total = cartBooks.reduce((sum, b) => sum + b.price, 0)\n"
            "  return { cartBooks, ownedBooks, addToCart, removeFromCart, checkout, owns, inCart, total, cartCount: state.cart.length }\n"
            "}\n"
        ),
    )


def _navbar(brand: str, plan: ProjectPlan, accent: str) -> GeneratedFile:
    links = ",\n".join(f'  {{ to: "{r["path"]}", label: "{r["page"]}" }}' for r in plan.routes)
    return GeneratedFile(
        path="src/components/BookNavbar.tsx",
        content=(
            "import { useState } from 'react'\n"
            "import { Link, NavLink, useNavigate } from 'react-router-dom'\n"
            "import { useBookStore } from '../hooks/useBookStore'\n\n"
            f"const links = [\n{links}\n]\n\n"
            "export function BookNavbar() {\n"
            "  const [open, setOpen] = useState(false)\n"
            "  const [q, setQ] = useState('')\n"
            "  const { cartCount } = useBookStore()\n"
            "  const nav = useNavigate()\n"
            "  return (\n"
            "    <header className=\"sticky top-0 z-50 border-b border-stone-200/80 bg-[#F7F4EF]/95 backdrop-blur\">\n"
            "      <div className=\"mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:px-6\">\n"
            "        <div className=\"flex items-center gap-4\">\n"
            f"          <Link to=\"/\" className=\"text-lg font-semibold tracking-tight\" style={{{{ color: '{accent}' }}}}>{brand}</Link>\n"
            "          <nav className=\"ml-auto hidden items-center gap-6 text-[11px] font-medium uppercase tracking-[0.16em] md:flex\">\n"
            "            {links.map((l) => (\n"
            "              <NavLink key={l.to} to={l.to} className={({ isActive }) => isActive ? 'text-stone-950' : 'text-stone-500 hover:text-stone-950'}>{l.label}</NavLink>\n"
            "            ))}\n"
            "          </nav>\n"
            "          <Link to=\"/cart\" className=\"rounded-full bg-stone-950 px-3 py-1.5 text-[10px] uppercase tracking-wider text-white\">Cart {cartCount}</Link>\n"
            "          <button type=\"button\" className=\"rounded-full border border-stone-300 px-3 py-1.5 text-[10px] uppercase md:hidden\" onClick={() => setOpen(v => !v)}>Menu</button>\n"
            "        </div>\n"
            "        <form className=\"flex gap-2\" onSubmit={(e) => { e.preventDefault(); nav(`/browse?q=${encodeURIComponent(q)}`) }}>\n"
            "          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder=\"Search all books…\" className=\"w-full rounded-full border border-stone-300 bg-white px-4 py-2.5 text-sm outline-none focus:border-teal-600\" />\n"
            "          <button type=\"submit\" className=\"rounded-full bg-teal-700 px-5 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-white\">Search</button>\n"
            "        </form>\n"
            "      </div>\n"
            "      {open && (\n"
            "        <div className=\"border-t border-stone-200 px-4 py-3 md:hidden\">\n"
            "          {links.map((l) => <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)} className=\"block py-2 text-sm uppercase tracking-wider\">{l.label}</NavLink>)}\n"
            "        </div>\n"
            "      )}\n"
            "    </header>\n"
            "  )\n"
            "}\n"
        ),
    )


def _footer(brand: str, plan: ProjectPlan) -> GeneratedFile:
    link_js = ",\n".join(f'  {{ to: "{r["path"]}", label: "{r["page"]}" }}' for r in plan.routes)
    return GeneratedFile(
        path="src/components/BookFooter.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n\n"
            f"const links = [\n{link_js}\n]\n\n"
            "export function BookFooter() {\n"
            "  return (\n"
            "    <footer className=\"border-t border-stone-200 bg-[#F7F4EF]\">\n"
            "      <div className=\"mx-auto flex max-w-6xl flex-col gap-4 px-4 py-10 sm:flex-row sm:items-center sm:justify-between sm:px-6\">\n"
            f"        <p className=\"font-serif text-xl text-stone-900\">{brand}</p>\n"
            "        <div className=\"flex flex-wrap gap-4 text-xs uppercase tracking-wider text-stone-500\">\n"
            "          {links.map((l) => <Link key={l.to} to={l.to} className=\"hover:text-stone-900\">{l.label}</Link>)}\n"
            "        </div>\n"
            "      </div>\n"
            f"      <div className=\"border-t border-stone-200 px-4 py-4 text-center text-xs text-stone-500\">© {{new Date().getFullYear()}} {brand}. Buy · Read · Search · Download PDF.</div>\n"
            "    </footer>\n"
            "  )\n"
            "}\n"
        ),
    )


def _search_bar() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/BookSearch.tsx",
        content=(
            "type Props = { value: string; onChange: (v: string) => void; placeholder?: string }\n"
            "export function BookSearch({ value, onChange, placeholder = 'Search title, author, or topic' }: Props) {\n"
            "  return (\n"
            "    <input\n"
            "      value={value}\n"
            "      onChange={(e) => onChange(e.target.value)}\n"
            "      placeholder={placeholder}\n"
            "      className=\"w-full rounded-full border border-stone-300 bg-white px-4 py-2.5 text-sm outline-none focus:border-teal-600\"\n"
            "    />\n"
            "  )\n"
            "}\n"
        ),
    )


def _book_card(accent: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/BookCard.tsx",
        content=(
            "import type { Book } from '../data/catalog'\n"
            "import { useBookStore } from '../hooks/useBookStore'\n\n"
            "export function BookCard({ book, onRead }: { book: Book; onRead?: (b: Book) => void }) {\n"
            "  const { addToCart, owns, inCart } = useBookStore()\n"
            "  const owned = owns(book.id)\n"
            "  return (\n"
            "    <article className=\"flex flex-col overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md\">\n"
            "      <img src={book.cover} alt={book.title} className=\"aspect-[3/4] w-full object-cover\" loading=\"lazy\" />\n"
            "      <div className=\"flex flex-1 flex-col gap-1 p-4\">\n"
            "        <p className=\"text-[10px] uppercase tracking-wider text-stone-500\">{book.category}</p>\n"
            "        <h3 className=\"font-serif text-lg leading-snug text-stone-950\">{book.title}</h3>\n"
            "        <p className=\"text-sm text-stone-500\">{book.author}</p>\n"
            "        <p className=\"mt-1 line-clamp-2 text-xs leading-relaxed text-stone-600\">{book.synopsis}</p>\n"
            "        <div className=\"mt-auto flex items-center justify-between pt-3\">\n"
            "          <p className=\"text-sm font-semibold\">${book.price.toFixed(2)}</p>\n"
            "          {owned ? (\n"
            "            <button type=\"button\" onClick={() => onRead?.(book)} className=\"rounded-full bg-stone-950 px-3 py-1.5 text-[10px] uppercase tracking-wider text-white\">Read</button>\n"
            "          ) : (\n"
            "            <button type=\"button\" disabled={inCart(book.id)} onClick={() => addToCart(book.id)} className=\"rounded-full px-3 py-1.5 text-[10px] uppercase tracking-wider text-white disabled:opacity-50\" style={{ backgroundColor: '#0F766E' }}>{inCart(book.id) ? 'In cart' : 'Buy'}</button>\n"
            "          )}\n"
            "        </div>\n"
            "      </div>\n"
            "    </article>\n"
            "  )\n"
            "}\n"
        ),
    )


def _reader() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/BookReader.tsx",
        content=(
            "import type { Book } from '../data/catalog'\n\n"
            "export function BookReader({ book, onClose }: { book: Book; onClose: () => void }) {\n"
            "  return (\n"
            "    <div className=\"fixed inset-0 z-[70] flex items-center justify-center bg-stone-950/60 p-4\" onClick={onClose}>\n"
            "      <div className=\"flex max-h-[90vh] w-full max-w-3xl flex-col overflow-hidden rounded-3xl bg-[#F7F4EF] shadow-2xl\" onClick={(e) => e.stopPropagation()}>\n"
            "        <div className=\"flex items-center justify-between border-b border-stone-200 px-5 py-4\">\n"
            "          <div>\n"
            "            <h3 className=\"font-serif text-xl\">{book.title}</h3>\n"
            "            <p className=\"text-sm text-stone-500\">{book.author} · {book.pages} pages</p>\n"
            "          </div>\n"
            "          <div className=\"flex gap-2\">\n"
            "            <a href={book.pdfUrl} download={`${book.title}.pdf`} target=\"_blank\" rel=\"noreferrer\" className=\"rounded-full bg-teal-700 px-4 py-2 text-[10px] font-semibold uppercase tracking-wider text-white\">Download PDF</a>\n"
            "            <button type=\"button\" onClick={onClose} className=\"rounded-full border border-stone-300 px-4 py-2 text-[10px] uppercase tracking-wider\">Close</button>\n"
            "          </div>\n"
            "        </div>\n"
            "        <div className=\"overflow-y-auto px-6 py-8\">\n"
            "          <p className=\"font-serif text-2xl leading-relaxed text-stone-800\">{book.synopsis}</p>\n"
            "          <p className=\"mt-6 text-sm leading-7 text-stone-600\">\n"
            "            This in-app reader opens your purchased title. Use Download PDF for the full file offline.\n"
            "            Chapter one begins with the same quiet attention the store was built for — search, buy, read, and keep.\n"
            "          </p>\n"
            "          {Array.from({ length: 4 }).map((_, i) => (\n"
            "            <p key={i} className=\"mt-4 text-sm leading-7 text-stone-600\">\n"
            "              {book.title} continues across the next pages with the voice of {book.author}.\n"
            "              The layout stays calm on phone and desktop so reading never feels cramped.\n"
            "            </p>\n"
            "          ))}\n"
            "        </div>\n"
            "      </div>\n"
            "    </div>\n"
            "  )\n"
            "}\n"
        ),
    )


def _home_page(comp: str) -> str:
    return (
        "import { useState } from 'react'\n"
        "import { Link } from 'react-router-dom'\n"
        "import { Hero } from '../components/Hero'\n"
        "import { BookCard } from '../components/BookCard'\n"
        "import { BookReader } from '../components/BookReader'\n"
        "import { books, type Book } from '../data/catalog'\n\n"
        f"export default function {comp}() {{\n"
        "  const [reading, setReading] = useState<Book | null>(null)\n"
        "  const featured = books.slice(0, 4)\n"
        "  return (\n"
        "    <div className=\"overflow-x-hidden bg-[#F7F4EF] text-stone-900\">\n"
        "      <Hero />\n"
        "      <section className=\"mx-auto max-w-6xl px-4 py-14 sm:px-6\">\n"
        "        <div className=\"flex items-end justify-between gap-4\">\n"
        "          <div>\n"
        "            <h2 className=\"font-serif text-3xl tracking-tight\">Featured titles</h2>\n"
        "            <p className=\"mt-2 text-sm text-stone-600\">Search the full shelf, buy instantly, then read or download PDF.</p>\n"
        "          </div>\n"
        "          <Link to=\"/browse\" className=\"text-xs font-semibold uppercase tracking-wider text-teal-700\">View all</Link>\n"
        "        </div>\n"
        "        <div className=\"mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-4\">\n"
        "          {featured.map((b) => <BookCard key={b.id} book={b} onRead={setReading} />)}\n"
        "        </div>\n"
        "      </section>\n"
        "      <section className=\"border-y border-stone-200 bg-white\">\n"
        "        <div className=\"mx-auto grid max-w-6xl gap-6 px-4 py-14 sm:grid-cols-3 sm:px-6\">\n"
        "          {[('Search', 'Find any title or author instantly.'), ('Buy & own', 'Checkout adds books to your library.'), ('Read & PDF', 'Open in-reader or download the file.')].map(([t, d]) => (\n"
        "            <div key={t}><h3 className=\"font-serif text-xl\">{t}</h3><p className=\"mt-2 text-sm text-stone-600\">{d}</p></div>\n"
        "          ))}\n"
        "        </div>\n"
        "      </section>\n"
        "      {reading && <BookReader book={reading} onClose={() => setReading(null)} />}\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _browse_page(comp: str) -> str:
    return (
        "import { useMemo, useState } from 'react'\n"
        "import { useSearchParams } from 'react-router-dom'\n"
        "import { BookCard } from '../components/BookCard'\n"
        "import { BookReader } from '../components/BookReader'\n"
        "import { BookSearch } from '../components/BookSearch'\n"
        "import { books, searchBooks, type Book } from '../data/catalog'\n\n"
        f"export default function {comp}() {{\n"
        "  const [params] = useSearchParams()\n"
        "  const [q, setQ] = useState(params.get('q') || '')\n"
        "  const [category, setCategory] = useState('all')\n"
        "  const [reading, setReading] = useState<Book | null>(null)\n"
        "  const categories = ['all', ...Array.from(new Set(books.map((b) => b.category)))]\n"
        "  const results = useMemo(() => searchBooks(q, category), [q, category])\n"
        "  return (\n"
        "    <div className=\"overflow-x-hidden bg-[#F7F4EF]\">\n"
        "      <section className=\"mx-auto max-w-6xl px-4 py-10 sm:px-6\">\n"
        "        <h1 className=\"font-serif text-4xl tracking-tight\">Browse books</h1>\n"
        "        <p className=\"mt-2 text-sm text-stone-600\">Search the full catalog — then buy, read, or download PDF from your library.</p>\n"
        "        <div className=\"mt-6 flex flex-col gap-3\">\n"
        "          <BookSearch value={q} onChange={setQ} />\n"
        "          <div className=\"flex flex-wrap gap-2\">\n"
        "            {categories.map((c) => (\n"
        "              <button key={c} type=\"button\" onClick={() => setCategory(c)} className={`rounded-full px-4 py-2 text-[11px] uppercase tracking-wider ${category === c ? 'bg-stone-950 text-white' : 'border border-stone-300 bg-white text-stone-700'}`}>{c === 'all' ? 'All' : c}</button>\n"
        "            ))}\n"
        "          </div>\n"
        "        </div>\n"
        "        <p className=\"mt-6 text-xs uppercase tracking-wider text-stone-500\">{results.length} titles</p>\n"
        "        <div className=\"mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-4\">\n"
        "          {results.map((b) => <BookCard key={b.id} book={b} onRead={setReading} />)}\n"
        "        </div>\n"
        "        {results.length === 0 && <p className=\"py-16 text-center text-sm text-stone-500\">No books match that search.</p>}\n"
        "      </section>\n"
        "      {reading && <BookReader book={reading} onClose={() => setReading(null)} />}\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _library_page(comp: str) -> str:
    return (
        "import { useState } from 'react'\n"
        "import { Link } from 'react-router-dom'\n"
        "import { BookReader } from '../components/BookReader'\n"
        "import { useBookStore } from '../hooks/useBookStore'\n"
        "import type { Book } from '../data/catalog'\n\n"
        f"export default function {comp}() {{\n"
        "  const { ownedBooks } = useBookStore()\n"
        "  const [reading, setReading] = useState<Book | null>(null)\n"
        "  return (\n"
        "    <div className=\"overflow-x-hidden bg-[#F7F4EF]\">\n"
        "      <section className=\"mx-auto max-w-6xl px-4 py-10 sm:px-6\">\n"
        "        <h1 className=\"font-serif text-4xl tracking-tight\">My library</h1>\n"
        "        <p className=\"mt-2 text-sm text-stone-600\">Books you bought — open the reader or download the PDF.</p>\n"
        "        {ownedBooks.length === 0 ? (\n"
        "          <div className=\"mt-12 rounded-3xl border border-dashed border-stone-300 bg-white px-6 py-16 text-center\">\n"
        "            <p className=\"text-stone-600\">Your shelf is empty. Browse titles and checkout to start reading.</p>\n"
        "            <Link to=\"/browse\" className=\"mt-6 inline-flex rounded-full bg-teal-700 px-5 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-white\">Browse books</Link>\n"
        "          </div>\n"
        "        ) : (\n"
        "          <div className=\"mt-8 grid gap-4\">\n"
        "            {ownedBooks.map((b) => (\n"
        "              <article key={b.id} className=\"flex flex-col gap-4 rounded-2xl border border-stone-200 bg-white p-4 sm:flex-row sm:items-center\">\n"
        "                <img src={b.cover} alt=\"\" className=\"h-28 w-20 rounded-lg object-cover\" />\n"
        "                <div className=\"flex-1\">\n"
        "                  <h3 className=\"font-serif text-xl\">{b.title}</h3>\n"
        "                  <p className=\"text-sm text-stone-500\">{b.author}</p>\n"
        "                </div>\n"
        "                <div className=\"flex flex-wrap gap-2\">\n"
        "                  <button type=\"button\" onClick={() => setReading(b)} className=\"rounded-full bg-stone-950 px-4 py-2 text-[10px] uppercase tracking-wider text-white\">Read</button>\n"
        "                  <a href={b.pdfUrl} download={`${b.title}.pdf`} target=\"_blank\" rel=\"noreferrer\" className=\"rounded-full border border-stone-300 px-4 py-2 text-[10px] uppercase tracking-wider\">Download PDF</a>\n"
        "                </div>\n"
        "              </article>\n"
        "            ))}\n"
        "          </div>\n"
        "        )}\n"
        "      </section>\n"
        "      {reading && <BookReader book={reading} onClose={() => setReading(null)} />}\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _cart_page(comp: str) -> str:
    return (
        "import { Link } from 'react-router-dom'\n"
        "import { useBookStore } from '../hooks/useBookStore'\n\n"
        f"export default function {comp}() {{\n"
        "  const { cartBooks, removeFromCart, checkout, total } = useBookStore()\n"
        "  return (\n"
        "    <div className=\"overflow-x-hidden bg-[#F7F4EF]\">\n"
        "      <section className=\"mx-auto max-w-3xl px-4 py-10 sm:px-6\">\n"
        "        <h1 className=\"font-serif text-4xl tracking-tight\">Cart</h1>\n"
        "        <p className=\"mt-2 text-sm text-stone-600\">Checkout unlocks Read + PDF download in your library.</p>\n"
        "        {cartBooks.length === 0 ? (\n"
        "          <div className=\"mt-12 rounded-3xl border border-dashed border-stone-300 bg-white px-6 py-16 text-center\">\n"
        "            <p className=\"text-stone-600\">Cart is empty.</p>\n"
        "            <Link to=\"/browse\" className=\"mt-6 inline-flex rounded-full bg-teal-700 px-5 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-white\">Browse books</Link>\n"
        "          </div>\n"
        "        ) : (\n"
        "          <div className=\"mt-8 space-y-3\">\n"
        "            {cartBooks.map((b) => (\n"
        "              <div key={b.id} className=\"flex items-center gap-4 rounded-2xl border border-stone-200 bg-white p-4\">\n"
        "                <img src={b.cover} alt=\"\" className=\"h-16 w-12 rounded object-cover\" />\n"
        "                <div className=\"flex-1\">\n"
        "                  <p className=\"font-medium\">{b.title}</p>\n"
        "                  <p className=\"text-sm text-stone-500\">${b.price.toFixed(2)}</p>\n"
        "                </div>\n"
        "                <button type=\"button\" onClick={() => removeFromCart(b.id)} className=\"text-xs uppercase tracking-wider text-stone-500\">Remove</button>\n"
        "              </div>\n"
        "            ))}\n"
        "            <div className=\"flex items-center justify-between rounded-2xl bg-stone-950 px-5 py-4 text-white\">\n"
        "              <p className=\"text-sm\">Total <span className=\"font-semibold\">${total.toFixed(2)}</span></p>\n"
        "              <button type=\"button\" onClick={checkout} className=\"rounded-full bg-teal-500 px-5 py-2 text-[11px] font-semibold uppercase tracking-wider text-stone-950\">Buy now</button>\n"
        "            </div>\n"
        "            <p className=\"text-xs text-stone-500\">Demo checkout — purchases are saved in this browser for Library access.</p>\n"
        "          </div>\n"
        "        )}\n"
        "      </section>\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _about_page(comp: str, brand: str) -> str:
    return (
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <section className=\"mx-auto max-w-3xl overflow-x-hidden px-4 py-16 sm:px-6\">\n"
        f"      <h1 className=\"font-serif text-4xl tracking-tight\">About {brand}</h1>\n"
        f"      <p className=\"mt-6 text-lg leading-relaxed text-stone-600\">{brand} is an online bookstore where readers can search the full catalog, buy titles, read in-browser, and download PDFs — with a calm layout that stays clear on every screen.</p>\n"
        "    </section>\n"
        "  )\n"
        "}\n"
    )


def _contact_page(comp: str, brand: str, accent: str) -> str:
    return (
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <section className=\"mx-auto max-w-xl overflow-x-hidden px-4 py-16 sm:px-6\">\n"
        "      <h1 className=\"font-serif text-4xl tracking-tight\">Contact</h1>\n"
        f"      <p className=\"mt-3 text-stone-600\">Questions about orders or PDF access at {brand}.</p>\n"
        "      <form className=\"mt-8 grid gap-3\" onSubmit={(e) => e.preventDefault()}>\n"
        "        <input className=\"rounded-xl border border-stone-300 px-3 py-2.5 text-sm\" placeholder=\"Name\" required />\n"
        "        <input type=\"email\" className=\"rounded-xl border border-stone-300 px-3 py-2.5 text-sm\" placeholder=\"Email\" required />\n"
        "        <textarea className=\"min-h-28 rounded-xl border border-stone-300 px-3 py-2.5 text-sm\" placeholder=\"Message\" required />\n"
        f"        <button type=\"submit\" className=\"rounded-full px-4 py-2.5 text-[11px] font-semibold uppercase tracking-wider text-white\" style={{{{ backgroundColor: '{accent}' }}}}>Send</button>\n"
        "      </form>\n"
        "    </section>\n"
        "  )\n"
        "}\n"
    )

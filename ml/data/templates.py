"""Shared templates and variation helpers for synthetic React datasets."""

from __future__ import annotations

import hashlib
import itertools
import json
from typing import Any

BRANDS = [
    "Bean House", "Wanderlust", "Nova Studio", "Pulse Fitness", "Harbor Legal",
    "Lumen SaaS", "Cedar Spa", "Orbit Games", "Maple Realty", "Forge Agency",
    "Aqua Dental", "Summit Trails", "Velvet Boutique", "CloudLedger", "Bright Kids",
]

COMPONENTS = ["Navbar", "Hero", "Footer", "Button", "Card", "CTA", "FeatureGrid", "Pricing"]
STYLES = ["modern", "minimal", "dark", "luxury", "playful", "corporate"]
COLORS = ["#0f172a", "#0d9488", "#7c3aed", "#b45309", "#be123c", "#0369a1"]

SITE_TYPES = [
    ("coffee shop", ["Home", "Menu", "About", "Contact"]),
    ("travel agency", ["Home", "Destinations", "Packages", "Contact"]),
    ("portfolio", ["Home", "Work", "About", "Contact"]),
    ("saas startup", ["Home", "Features", "Pricing", "Contact"]),
    ("restaurant", ["Home", "Menu", "Reservations", "Contact"]),
    ("fitness gym", ["Home", "Classes", "Trainers", "Contact"]),
    ("law firm", ["Home", "Practice Areas", "Attorneys", "Contact"]),
    ("real estate", ["Home", "Listings", "Agents", "Contact"]),
]


def stable_id(prefix: str, *parts: Any) -> str:
    h = hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:10]
    return f"{prefix}_{h}"


def navbar_tsx(brand: str, pages: list[str], dark: bool, glass: bool) -> str:
    links = ",\n".join(
        f'  {{ to: "{"/" if p.lower()=="home" else "/" + p.lower().replace(" ", "-")}", label: "{p}" }}'
        for p in pages
    )
    if glass:
        hdr = "sticky top-0 z-50 border-b border-white/20 bg-white/10 backdrop-blur-xl"
    elif dark:
        hdr = "sticky top-0 z-50 border-b border-slate-800 bg-slate-950/90 text-white"
    else:
        hdr = "sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur"
    return f'''import {{ Link, NavLink }} from 'react-router-dom'

const links = [
{links}
]

export function Navbar() {{
  return (
    <header className="{hdr}">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link to="/" className="text-lg font-semibold tracking-tight">{brand}</Link>
        <nav className="flex flex-wrap gap-3 text-sm">
          {{links.map((link) => (
            <NavLink key={{link.to}} to={{link.to}} className="opacity-80 hover:opacity-100">
              {{link.label}}
            </NavLink>
          ))}}
        </nav>
      </div>
    </header>
  )
}}
'''


def hero_tsx(brand: str, subtitle: str, cta: str, dark: bool) -> str:
    bg = "bg-slate-950 text-white" if dark else "bg-slate-50 text-slate-900"
    muted = "text-slate-300" if dark else "text-slate-600"
    return f'''type HeroProps = {{ title?: string; subtitle?: string; cta?: string }}

export function Hero({{ title = "{brand}", subtitle = "{subtitle}", cta = "{cta}" }}: HeroProps) {{
  return (
    <section className="mx-auto flex min-h-[70vh] max-w-6xl flex-col justify-center px-4 py-16 {bg}">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-teal-500">Welcome</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">{{title}}</h1>
      <p className="mt-4 max-w-2xl text-lg {muted}">{{subtitle}}</p>
      <a href="#contact" className="mt-8 inline-flex w-fit rounded-lg bg-teal-600 px-5 py-2.5 text-sm font-semibold text-white">
        {{cta}}
      </a>
    </section>
  )
}}
'''


def footer_tsx(brand: str, dark: bool) -> str:
    bg = "border-slate-800 bg-slate-950 text-slate-400" if dark else "border-slate-200 bg-slate-50 text-slate-600"
    return f'''export function Footer() {{
  return (
    <footer className="border-t {bg}">
      <div className="mx-auto flex max-w-6xl justify-between px-4 py-8 text-sm">
        <p>© {{new Date().getFullYear()}} {brand}</p>
        <p>Built with React + Tailwind</p>
      </div>
    </footer>
  )
}}
'''


def button_tsx() -> str:
    return '''type ButtonProps = {
  children: React.ReactNode
  variant?: 'primary' | 'ghost'
  href?: string
}

export function Button({ children, variant = 'primary', href = '#' }: ButtonProps) {
  const base = 'inline-flex items-center rounded-lg px-5 py-2.5 text-sm font-semibold transition'
  const styles =
    variant === 'primary'
      ? `${base} bg-slate-900 text-white hover:bg-slate-700`
      : `${base} border border-slate-300 bg-white text-slate-800`
  return (
    <a href={href} className={styles}>
      {children}
    </a>
  )
}
'''


def card_tsx() -> str:
    return '''type CardProps = { title: string; description: string }

export function Card({ title, description }: CardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">{description}</p>
    </article>
  )
}
'''


def cta_tsx(brand: str) -> str:
    return f'''export function CTA() {{
  return (
    <section className="mx-auto max-w-6xl px-4 py-16">
      <div className="rounded-2xl bg-teal-600 px-8 py-12 text-center text-white">
        <h2 className="text-3xl font-bold">Ready to try {brand}?</h2>
        <p className="mt-3 text-teal-50">Join thousands of happy customers today.</p>
        <a href="#contact" className="mt-6 inline-flex rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-teal-800">
          Get started
        </a>
      </div>
    </section>
  )
}}
'''


def feature_grid_tsx() -> str:
    return '''import { Card } from './Card'

const features = [
  { title: 'Fast', description: 'Optimized React performance.' },
  { title: 'Responsive', description: 'Looks great on every screen.' },
  { title: 'Modern', description: 'Tailwind utility-first styling.' },
]

export function FeatureGrid() {
  return (
    <section className="mx-auto grid max-w-6xl gap-4 px-4 py-16 sm:grid-cols-3">
      {features.map((f) => (
        <Card key={f.title} title={f.title} description={f.description} />
      ))}
    </section>
  )
}
'''


def pricing_tsx() -> str:
    return '''export function Pricing() {
  const plans = [
    { name: 'Starter', price: '$0' },
    { name: 'Pro', price: '$29' },
    { name: 'Team', price: '$99' },
  ]
  return (
    <section className="mx-auto grid max-w-6xl gap-4 px-4 py-16 sm:grid-cols-3">
      {plans.map((p) => (
        <div key={p.name} className="rounded-2xl border border-slate-200 bg-white p-6">
          <h3 className="text-lg font-semibold">{p.name}</h3>
          <p className="mt-2 text-3xl font-bold">{p.price}</p>
        </div>
      ))}
    </section>
  )
}
'''


COMPONENT_BUILDERS = {
    "Navbar": lambda brand, pages, dark, glass, **_: navbar_tsx(brand, pages, dark, glass),
    "Hero": lambda brand, pages, dark, glass, subtitle="A modern experience.", cta="Get started", **_: hero_tsx(brand, subtitle, cta, dark),
    "Footer": lambda brand, pages, dark, glass, **_: footer_tsx(brand, dark),
    "Button": lambda **_: button_tsx(),
    "Card": lambda **_: card_tsx(),
    "CTA": lambda brand, **_: cta_tsx(brand),
    "FeatureGrid": lambda **_: feature_grid_tsx(),
    "Pricing": lambda **_: pricing_tsx(),
}


def page_tsx(page_name: str, brand: str, use_hero: bool) -> str:
    comp = page_name.replace(" ", "") + "Page"
    if page_name.lower() == "home" and use_hero:
        return f'''import {{ Hero }} from '../components/Hero'
import {{ FeatureGrid }} from '../components/FeatureGrid'
import {{ CTA }} from '../components/CTA'

export default function {comp}() {{
  return (
    <>
      <Hero title="{brand}" subtitle="Built for modern teams and customers." cta="Explore" />
      <FeatureGrid />
      <CTA />
    </>
  )
}}
'''
    return f'''export default function {comp}() {{
  return (
    <section className="mx-auto max-w-6xl px-4 py-16">
      <h1 className="text-3xl font-bold tracking-tight">{page_name}</h1>
      <p className="mt-3 max-w-2xl text-slate-600">
        Learn more about {brand} — {page_name.lower()} details and next steps.
      </p>
    </section>
  )
}}
'''


def package_json(slug: str) -> str:
    return json.dumps(
        {
            "name": slug,
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {"dev": "vite", "build": "tsc -b && vite build", "preview": "vite preview"},
            "dependencies": {
                "react": "^19.0.0",
                "react-dom": "^19.0.0",
                "react-router-dom": "^7.0.0",
            },
            "devDependencies": {
                "@tailwindcss/vite": "^4.0.0",
                "@types/react": "^19.0.0",
                "@types/react-dom": "^19.0.0",
                "@vitejs/plugin-react": "^4.3.4",
                "tailwindcss": "^4.0.0",
                "typescript": "~5.7.2",
                "vite": "^6.0.0",
            },
        },
        indent=2,
    ) + "\n"


def app_tsx(pages: list[str]) -> str:
    imports = []
    routes = []
    for p in pages:
        comp = ("Home" if p.lower() == "home" else p.replace(" ", "")) + "Page"
        path = "/" if p.lower() == "home" else "/" + p.lower().replace(" ", "-")
        imports.append(f"import {comp} from './pages/{comp}'")
        routes.append(f'          <Route path="{path}" element={{<{comp} />}} />')
    return (
        "import { Route, Routes } from 'react-router-dom'\n"
        "import { Navbar } from './components/Navbar'\n"
        "import { Footer } from './components/Footer'\n"
        + "\n".join(imports)
        + "\n\nexport default function App() {\n"
        "  return (\n"
        '    <div className="flex min-h-screen flex-col">\n'
        "      <Navbar />\n"
        '      <main className="flex-1">\n'
        "        <Routes>\n"
        + "\n".join(routes)
        + "\n        </Routes>\n"
        "      </main>\n"
        "      <Footer />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def main_tsx() -> str:
    return '''import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
'''


def index_css(dark: bool, color: str) -> str:
    bg = "#0a0f1a" if dark else "#f8fafc"
    text = "#e2e8f0" if dark else "#0f172a"
    return f'''@import "tailwindcss";

:root {{
  --brand: {color};
  --bg: {bg};
  --text: {text};
}}

body {{
  margin: 0;
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: "Segoe UI", system-ui, sans-serif;
}}
'''


def index_html(brand: str) -> str:
    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{brand}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''


def slugify(name: str) -> str:
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-") or "site"


def iter_combos(limit: int | None = None):
    combos = list(itertools.product(BRANDS, STYLES, [True, False], [True, False]))
    if limit:
        combos = combos[:limit]
    return combos

"""Build a text corpus for BPE training from artifacts + synthetic React/TSX."""

from __future__ import annotations

import json
from pathlib import Path

from tokenizer.specials import format_training_example, special_token_list

REPO_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO_ROOT / "apps" / "api" / "artifacts"
OUT_DIR = Path(__file__).resolve().parent / "corpus"
CORPUS_FILE = OUT_DIR / "train_corpus.txt"


SYNTHETIC_COMPONENTS = [
    {
        "prompt": "Create a glassmorphism Navbar for Bean House",
        "files": [
            {
                "path": "src/components/Navbar.tsx",
                "content": '''import { Link, NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Home' },
  { to: '/menu', label: 'Menu' },
  { to: '/about', label: 'About' },
  { to: '/contact', label: 'Contact' },
]

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/20 bg-white/10 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link to="/" className="text-lg font-semibold tracking-tight text-slate-900">
          Bean House
        </Link>
        <nav className="flex flex-wrap gap-3 text-sm text-slate-700">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} className="hover:text-slate-900">
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}
''',
            }
        ],
    },
    {
        "prompt": "Create a Hero with dark mode and CTA",
        "files": [
            {
                "path": "src/components/Hero.tsx",
                "content": '''type HeroProps = {
  title: string
  subtitle: string
  cta: string
}

export function Hero({ title, subtitle, cta }: HeroProps) {
  return (
    <section className="mx-auto flex min-h-[70vh] max-w-6xl flex-col justify-center bg-slate-950 px-4 py-16 text-white">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-teal-300">Welcome</p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">{title}</h1>
      <p className="mt-4 max-w-2xl text-lg text-slate-300">{subtitle}</p>
      <a
        href="#contact"
        className="mt-8 inline-flex w-fit rounded-lg bg-teal-500 px-5 py-2.5 text-sm font-semibold text-slate-950"
      >
        {cta}
      </a>
    </section>
  )
}
''',
            }
        ],
    },
    {
        "prompt": "Create a Card component with Tailwind",
        "files": [
            {
                "path": "src/components/Card.tsx",
                "content": '''type CardProps = { title: string; description: string }

export function Card({ title, description }: CardProps) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">{description}</p>
    </article>
  )
}
''',
            }
        ],
    },
    {
        "prompt": "Create a Footer for a travel agency",
        "files": [
            {
                "path": "src/components/Footer.tsx",
                "content": '''export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50">
      <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-8 text-sm text-slate-600 sm:flex-row sm:justify-between">
        <p>© {new Date().getFullYear()} Wanderlust Travel</p>
        <p>Destinations · Packages · Contact</p>
      </div>
    </footer>
  )
}
''',
            }
        ],
    },
    {
        "prompt": "Create a Button with primary and ghost variants",
        "files": [
            {
                "path": "src/components/Button.tsx",
                "content": '''type ButtonProps = {
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
''',
            }
        ],
    },
]

SYNTHETIC_PAGES = [
    {
        "prompt": "Create a Home page with Hero and three Cards",
        "mode": "page",
        "files": [
            {
                "path": "src/pages/HomePage.tsx",
                "content": '''import { Hero } from '../components/Hero'
import { Card } from '../components/Card'

export default function HomePage() {
  return (
    <>
      <Hero title="Bean House" subtitle="Specialty coffee roasted weekly." cta="Order now" />
      <section className="mx-auto grid max-w-6xl gap-4 px-4 pb-16 sm:grid-cols-3">
        <Card title="Fresh Roast" description="Single-origin beans every week." />
        <Card title="Cozy Space" description="Wi-Fi and calm mornings." />
        <Card title="Pastries" description="Baked fresh each dawn." />
      </section>
    </>
  )
}
''',
            }
        ],
    },
]

SYNTHETIC_SITES = [
    {
        "prompt": "Build a modern coffee shop website with dark mode",
        "mode": "site",
        "files": [
            {
                "path": "package.json",
                "content": json.dumps(
                    {
                        "name": "bean-house",
                        "private": True,
                        "type": "module",
                        "scripts": {"dev": "vite", "build": "tsc -b && vite build"},
                        "dependencies": {
                            "react": "^19.0.0",
                            "react-dom": "^19.0.0",
                            "react-router-dom": "^7.0.0",
                        },
                        "devDependencies": {
                            "@tailwindcss/vite": "^4.0.0",
                            "tailwindcss": "^4.0.0",
                            "typescript": "~5.7.2",
                            "vite": "^6.0.0",
                            "@vitejs/plugin-react": "^4.3.4",
                        },
                    },
                    indent=2,
                )
                + "\n",
            },
            {
                "path": "src/App.tsx",
                "content": '''import { Route, Routes } from 'react-router-dom'
import { Navbar } from './components/Navbar'
import { Footer } from './components/Footer'
import HomePage from './pages/HomePage'

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
''',
            },
            {
                "path": "src/index.css",
                "content": '''@import "tailwindcss";

:root {
  --brand: #0d9488;
  --bg: #0a0f1a;
  --text: #e2e8f0;
}

body {
  margin: 0;
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}
''',
            },
        ],
    },
]


def _collect_artifact_texts() -> list[str]:
    texts: list[str] = []
    if not ARTIFACTS.exists():
        return texts
    for path in ARTIFACTS.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".tsx", ".ts", ".jsx", ".js", ".css", ".json", ".html", ".md"}:
            continue
        if "node_modules" in path.parts or "dist" in path.parts:
            continue
        try:
            texts.append(path.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return texts


def _synthetic_strings() -> list[str]:
    out: list[str] = []
    for item in SYNTHETIC_COMPONENTS:
        out.append(format_training_example(item["prompt"], item["files"], mode="comp"))
        for f in item["files"]:
            out.append(f["content"])
    for item in SYNTHETIC_PAGES:
        out.append(format_training_example(item["prompt"], item["files"], mode=item["mode"]))
    for item in SYNTHETIC_SITES:
        out.append(format_training_example(item["prompt"], item["files"], mode=item["mode"]))
        for f in item["files"]:
            out.append(f["content"])
    # Extra Tailwind / JSX vocabulary boosters
    boosters = [
        "className=\"mx-auto flex max-w-6xl items-center justify-between px-4 py-4\"",
        "bg-gradient-to-br from-slate-950 via-slate-900 to-teal-950",
        "rounded-2xl border border-white/10 backdrop-blur-xl shadow-lg",
        "export default function AboutPage() { return <section className=\"py-16\">About</section> }",
        "import { defineConfig } from 'vite'\nimport react from '@vitejs/plugin-react'\nimport tailwindcss from '@tailwindcss/vite'",
        "react-router-dom BrowserRouter Routes Route NavLink",
        "framer-motion axios lucide-react typescript vite",
    ]
    # Repeat structured examples to overweight special format + grow merges
    for _ in range(80):
        out.extend(boosters)
        for item in SYNTHETIC_COMPONENTS:
            out.append(format_training_example(item["prompt"], item["files"], mode="comp"))
        for item in SYNTHETIC_PAGES:
            out.append(format_training_example(item["prompt"], item["files"], mode=item["mode"]))
        for item in SYNTHETIC_SITES:
            out.append(format_training_example(item["prompt"], item["files"], mode=item["mode"]))

    # Lexicon dump — common Tailwind utilities & React keywords to enlarge vocab
    tw = [
        "flex", "grid", "hidden", "block", "inline-flex", "items-center", "justify-between",
        "justify-center", "gap-1", "gap-2", "gap-3", "gap-4", "gap-6", "gap-8",
        "p-2", "p-4", "p-6", "p-8", "px-3", "px-4", "px-5", "py-2", "py-2.5", "py-4", "py-8", "py-16",
        "m-0", "mx-auto", "mt-2", "mt-3", "mt-4", "mt-8", "mb-2", "min-h-screen", "min-h-[70vh]",
        "max-w-2xl", "max-w-3xl", "max-w-6xl", "w-full", "w-fit", "h-9", "h-full",
        "text-sm", "text-base", "text-lg", "text-xl", "text-2xl", "text-3xl", "text-4xl", "text-5xl",
        "font-medium", "font-semibold", "font-bold", "tracking-tight", "tracking-[0.2em]",
        "uppercase", "leading-relaxed", "truncate", "line-clamp-2",
        "rounded-lg", "rounded-xl", "rounded-2xl", "rounded-full",
        "border", "border-b", "border-t", "border-slate-200", "border-slate-300", "border-white/10", "border-white/20",
        "bg-white", "bg-slate-50", "bg-slate-900", "bg-slate-950", "bg-teal-500", "bg-white/10",
        "text-white", "text-slate-600", "text-slate-700", "text-slate-900", "text-teal-300", "text-teal-700",
        "shadow-sm", "shadow-md", "shadow-lg", "backdrop-blur", "backdrop-blur-xl",
        "sticky", "top-0", "z-50", "transition", "hover:shadow-md", "hover:-translate-y-0.5",
        "sm:flex-row", "sm:grid-cols-3", "sm:text-5xl", "md:px-6", "lg:px-8",
        "from-slate-950", "via-slate-900", "to-teal-950", "bg-gradient-to-br",
    ]
    react_kw = [
        "export", "default", "function", "return", "import", "from", "const", "type",
        "React", "ReactNode", "useState", "useEffect", "useMemo", "useCallback",
        "BrowserRouter", "Routes", "Route", "Link", "NavLink", "Outlet",
        "createRoot", "StrictMode", "className", "props", "children",
    ]
    for _ in range(30):
        out.append(" ".join(tw))
        out.append(" ".join(react_kw))
        out.append("\n".join(f'className="{c}"' for c in tw[:40]))

    return out

def build_corpus() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    chunks = _collect_artifact_texts() + _synthetic_strings()
    # Ensure special tokens appear in corpus so they aren't "unknown" patterns
    chunks.extend(special_token_list() * 50)

    CORPUS_FILE.write_text("\n\n".join(chunks), encoding="utf-8")
    meta = {
        "path": str(CORPUS_FILE),
        "num_chunks": len(chunks),
        "bytes": CORPUS_FILE.stat().st_size,
        "artifact_files": len(_collect_artifact_texts()),
    }
    (OUT_DIR / "corpus_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return CORPUS_FILE


if __name__ == "__main__":
    build_corpus()

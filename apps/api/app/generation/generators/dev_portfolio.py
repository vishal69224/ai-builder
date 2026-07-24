"""Developer portfolio generator — multiple distinct visual systems."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements


SKILL_CATALOG = {
    "flutter": ["Flutter", "Dart", "Provider / Riverpod", "Firebase", "REST APIs"],
    "python": ["Python", "FastAPI", "Django", "Pandas", "Automation"],
    "react": ["React", "TypeScript", "Next.js", "Tailwind CSS"],
    "default": ["Flutter", "Dart", "Python", "FastAPI", "Git", "REST APIs", "Firebase", "PostgreSQL"],
}


@dataclass(frozen=True)
class StylePack:
    id: str
    label: str
    page_bg: str
    ink: str
    muted: str
    accent: str
    accent_soft: str
    panel: str
    border: str
    hero_layout: str  # split | stack | banner
    radius: str
    display_weight: str


STYLES: dict[str, StylePack] = {
    "aurora": StylePack(
        id="aurora",
        label="Aurora Dark",
        page_bg="bg-[#070B14] text-slate-100",
        ink="text-white",
        muted="text-slate-400",
        accent="text-cyan-300",
        accent_soft="bg-cyan-400 text-slate-950",
        panel="rounded-3xl border border-white/10 bg-white/[0.04]",
        border="border-white/10",
        hero_layout="split",
        radius="rounded-full",
        display_weight="font-semibold",
    ),
    "paper": StylePack(
        id="paper",
        label="Editorial Paper",
        page_bg="bg-[#F7F4EF] text-stone-900",
        ink="text-stone-900",
        muted="text-stone-500",
        accent="text-teal-800",
        accent_soft="bg-stone-900 text-white",
        panel="rounded-none border border-stone-300 bg-white",
        border="border-stone-300",
        hero_layout="stack",
        radius="rounded-none",
        display_weight="font-bold",
    ),
    "signal": StylePack(
        id="signal",
        label="Signal Bold",
        page_bg="bg-[#F4F7FB] text-slate-950",
        ink="text-slate-950",
        muted="text-slate-500",
        accent="text-orange-600",
        accent_soft="bg-orange-500 text-white",
        panel="rounded-[2rem] border border-slate-200 bg-white shadow-sm",
        border="border-slate-200",
        hero_layout="banner",
        radius="rounded-2xl",
        display_weight="font-extrabold",
    ),
    "terminal": StylePack(
        id="terminal",
        label="Terminal Forge",
        page_bg="bg-[#050806] text-emerald-50",
        ink="text-emerald-50",
        muted="text-emerald-200/60",
        accent="text-lime-300",
        accent_soft="bg-lime-300 text-emerald-950",
        panel="rounded-xl border border-lime-300/20 bg-emerald-950/40",
        border="border-lime-300/20",
        hero_layout="split",
        radius="rounded-md",
        display_weight="font-semibold tracking-tight",
    ),
}


def pick_style(prompt: str) -> StylePack:
    lowered = prompt.lower()
    if any(k in lowered for k in ("light", "clean", "minimal", "editorial", "simple")):
        return STYLES["paper"]
    if any(k in lowered for k in ("bold", "loud", "colorful", "modern", "startup")):
        return STYLES["signal"]
    if any(k in lowered for k in ("terminal", "hacker", "cyber", "cli", "matrix")):
        return STYLES["terminal"]
    if any(k in lowered for k in ("dark", "neon", "glow", "night")):
        return STYLES["aurora"]
    # Stable variety from prompt content so regenerations of different briefs differ
    digest = sum(ord(c) for c in lowered) % 4
    return list(STYLES.values())[digest]


def generate_dev_portfolio(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    analysis = requirements.analysis
    prompt = analysis.raw_prompt or ""
    lowered = prompt.lower()
    style = pick_style(prompt)

    name = _display_name(analysis.brand_name, plan.project_name, prompt)
    role = _role_line(lowered)
    skills = _skills(lowered)
    projects = _projects(lowered)
    tagline = f"{role} building polished apps, APIs, and products you can ship."

    data = {
        "name": name,
        "role": role,
        "tagline": tagline,
        "email": "hello@example.com",
        "location": "Remote · Worldwide",
        "style": style.id,
        "styleLabel": style.label,
        "skills": skills,
        "stack": _stack(lowered),
        "experience": [
            {
                "role": "Flutter Developer",
                "org": "Product Studio",
                "period": "2023 — Present",
                "points": [
                    "Shipped cross-platform mobile apps with Flutter and clean architecture",
                    "Integrated REST/GraphQL APIs, auth, and offline-first local storage",
                    "Partnered with design to deliver motion-rich, accessible UI",
                ],
            },
            {
                "role": "Python Engineer",
                "org": "Platform Team",
                "period": "2021 — 2023",
                "points": [
                    "Built FastAPI services, workers, and data pipelines",
                    "Automated reporting and CI helpers used across the squad",
                    "Improved API latency and observability for production workloads",
                ],
            },
        ],
        "projects": projects,
        "about": (
            f"I'm {name}, a {role.lower()} who cares about craft: clear architecture, "
            "fast feedback loops, and interfaces people enjoy using. This template is ready to "
            "edit — swap projects, skills, and copy to make it yours."
        ),
    }

    files = [
        GeneratedFile(
            path="src/data/portfolio.ts",
            content=f"export const portfolio = {json.dumps(data, indent=2)} as const\n",
        ),
        _use_theme(style),
        _button(style),
        _navbar(name, style),
        _hero(style),
        _sections(style),
        _footer(name, style),
        GeneratedFile(path="src/components/Navbar.tsx", content="export { PortfolioNav as Navbar } from './PortfolioNav'\n"),
        GeneratedFile(path="src/components/Hero.tsx", content="export { PortfolioHero as Hero } from './PortfolioHero'\n"),
        GeneratedFile(path="src/components/Footer.tsx", content="export { PortfolioFooter as Footer } from './PortfolioFooter'\n"),
        GeneratedFile(
            path="src/components/Button.tsx",
            content="export { PortfolioButton as Button } from './PortfolioButton'\n",
        ),
        GeneratedFile(
            path="src/components/Card.tsx",
            content=(
                "import type { ReactNode } from 'react'\n"
                f"export function Card({{ children, className = '' }}: {{ children: ReactNode; className?: string }}) {{\n"
                f"  return <div className={{`{style.panel} p-5 ${{className}}`}}>{{children}}</div>\n"
                "}\n"
            ),
        ),
        GeneratedFile(
            path="src/pages/HomePage.tsx",
            content=(
                "import { PortfolioHero } from '../components/PortfolioHero'\n"
                "import { AboutSection, SkillsSection, ExperienceSection, ProjectsSection, ContactSection } from '../components/PortfolioSections'\n\n"
                "export default function HomePage() {\n"
                f"  return (\n"
                f"    <div className=\"{style.page_bg}\">\n"
                "      <PortfolioHero />\n"
                "      <AboutSection />\n"
                "      <SkillsSection />\n"
                "      <ExperienceSection />\n"
                "      <ProjectsSection />\n"
                "      <ContactSection />\n"
                "    </div>\n"
                "  )\n"
                "}\n"
            ),
        ),
    ]

    for route in plan.routes:
        if route["path"] == "/":
            continue
        page = route["page"].lower()
        comp = route["component"]
        if "project" in page or "work" in page:
            body = (
                "import { ProjectsSection } from '../components/PortfolioSections'\n"
                f"export default function {comp}() {{\n"
                f"  return <div className=\"{style.page_bg} pt-10\"><ProjectsSection /></div>\n"
                "}\n"
            )
        elif "about" in page:
            body = (
                "import { AboutSection, SkillsSection } from '../components/PortfolioSections'\n"
                f"export default function {comp}() {{\n"
                f"  return <div className=\"{style.page_bg} pt-10\"><AboutSection /><SkillsSection /></div>\n"
                "}\n"
            )
        elif "contact" in page:
            body = (
                "import { ContactSection } from '../components/PortfolioSections'\n"
                f"export default function {comp}() {{\n"
                f"  return <div className=\"{style.page_bg} pt-10\"><ContactSection /></div>\n"
                "}\n"
            )
        else:
            body = (
                f"export default function {comp}() {{\n"
                f"  return <section className=\"mx-auto max-w-5xl px-4 py-20\"><h1 className=\"text-3xl {style.display_weight}\">{route['page']}</h1><p className=\"mt-3 {style.muted}\">Edit this page in the code tab.</p></section>\n"
                "}\n"
            )
        files.append(GeneratedFile(path=f"src/pages/{comp}.tsx", content=body))

    return list({f.path: f for f in files}.values())


def _display_name(brand: str, project_name: str, prompt: str) -> str:
    q = re.search(r"(?:i(?:'m| am)|my name is|called)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", prompt)
    if q:
        return q.group(1).strip()
    name = (brand or project_name or "").strip()
    if name.lower() in {
        "",
        "creative portfolio",
        "portfolio",
        "personal brand",
        "marketing landing page",
        "generated site",
        "studio north",
    }:
        return "Alex Rivera"
    return name


def _role_line(lowered: str) -> str:
    parts = []
    if "flutter" in lowered:
        parts.append("Flutter")
    if "python" in lowered:
        parts.append("Python")
    if "react" in lowered or "frontend" in lowered:
        parts.append("Frontend")
    if not parts:
        parts = ["Software"]
    if len(parts) == 1:
        return f"{parts[0]} Developer"
    return f"{' & '.join(parts)} Developer"


def _skills(lowered: str) -> list[str]:
    skills: list[str] = []
    if "flutter" in lowered:
        skills.extend(SKILL_CATALOG["flutter"])
    if "python" in lowered:
        skills.extend(SKILL_CATALOG["python"])
    if "react" in lowered:
        skills.extend(SKILL_CATALOG["react"])
    if not skills:
        skills = list(SKILL_CATALOG["default"])
    seen: set[str] = set()
    out: list[str] = []
    for s in skills:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out[:12]


def _stack(lowered: str) -> list[str]:
    stack = []
    for token in ("Flutter", "Dart", "Python", "FastAPI", "Firebase", "PostgreSQL", "Docker", "Git"):
        if token.lower() in lowered or token == "Git":
            stack.append(token)
    if "flutter" in lowered and "Dart" not in stack:
        stack.insert(1, "Dart")
    if "python" in lowered and "FastAPI" not in stack:
        stack.append("FastAPI")
    return stack or ["Flutter", "Python", "Git"]


def _projects(lowered: str) -> list[dict]:
    base = [
        {
            "title": "Shoply — Flutter Commerce App",
            "blurb": "Cross-platform storefront with carts, payments hooks, and offline cache.",
            "tags": ["Flutter", "Firebase", "Stripe"],
            "href": "#contact",
        },
        {
            "title": "Pulse API — FastAPI Platform",
            "blurb": "Typed Python services with JWT auth, background jobs, and OpenAPI docs.",
            "tags": ["Python", "FastAPI", "PostgreSQL"],
            "href": "#contact",
        },
        {
            "title": "Devfolio — This Template",
            "blurb": "Editable portfolio starter — swap copy, projects, and skills to make it yours.",
            "tags": ["React", "Tailwind", "Vite"],
            "href": "#projects",
        },
    ]
    if "flutter" not in lowered:
        base[0] = {
            "title": "Mobile Companion App",
            "blurb": "Product UI with smooth navigation and API-backed screens.",
            "tags": ["Mobile", "UI", "API"],
            "href": "#contact",
        }
    if "python" not in lowered:
        base[1] = {
            "title": "Automation Toolkit",
            "blurb": "Scripts and services that remove repetitive ops work.",
            "tags": ["Automation", "CLI"],
            "href": "#contact",
        }
    return base


def _use_theme(style: StylePack) -> GeneratedFile:
    dark = style.id in {"aurora", "terminal"}
    return GeneratedFile(
        path="src/hooks/useTheme.ts",
        content=(
            "import { useEffect } from 'react'\n"
            "export function useTheme() {\n"
            f"  useEffect(() => {{ document.documentElement.classList.{'add' if dark else 'remove'}('dark') }}, [])\n"
            "}\n"
        ),
    )


def _button(style: StylePack) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/PortfolioButton.tsx",
        content=(
            "import type { ReactNode } from 'react'\n"
            "type Props = { children: ReactNode; href?: string; variant?: 'primary' | 'ghost' }\n"
            "export function PortfolioButton({ children, href = '#contact', variant = 'primary' }: Props) {\n"
            f"  const cls = variant === 'ghost'\n"
            f"    ? '{style.border} border bg-transparent {style.ink} hover:opacity-80'\n"
            f"    : '{style.accent_soft} hover:opacity-90'\n"
            f"  return <a href={{href}} className={{`inline-flex items-center justify-center {style.radius} px-5 py-2.5 text-sm font-semibold transition ${{cls}}`}}>{{children}}</a>\n"
            "}\n"
        ),
    )


def _navbar(name: str, style: StylePack) -> GeneratedFile:
    header_bg = {
        "aurora": "border-b border-white/10 bg-[#070B14]/80 backdrop-blur",
        "paper": "border-b border-stone-300 bg-[#F7F4EF]/90 backdrop-blur",
        "signal": "border-b border-slate-200 bg-white/90 backdrop-blur",
        "terminal": "border-b border-lime-300/20 bg-[#050806]/90 backdrop-blur",
    }[style.id]
    return GeneratedFile(
        path="src/components/PortfolioNav.tsx",
        content=(
            "import { useState } from 'react'\n\n"
            "const links = [\n"
            "  { href: '#about', label: 'About' },\n"
            "  { href: '#skills', label: 'Skills' },\n"
            "  { href: '#experience', label: 'Experience' },\n"
            "  { href: '#projects', label: 'Work' },\n"
            "  { href: '#contact', label: 'Contact' },\n"
            "]\n\n"
            "export function PortfolioNav() {\n"
            "  const [open, setOpen] = useState(false)\n"
            "  return (\n"
            f"    <header className=\"sticky top-0 z-50 {header_bg}\">\n"
            "      <div className=\"mx-auto flex max-w-5xl items-center gap-4 px-4 py-4\">\n"
            f"        <a href=\"#\" className=\"text-sm {style.display_weight} uppercase tracking-[0.18em] {style.ink}\">{name}</a>\n"
            f"        <nav className=\"ml-auto hidden gap-5 text-sm {style.muted} md:flex\">\n"
            f"          {{links.map((l) => <a key={{l.href}} href={{l.href}} className=\"hover:opacity-100 opacity-80\">{{l.label}}</a>)}}\n"
            "        </nav>\n"
            f"        <a href=\"#contact\" className=\"ml-auto hidden {style.radius} {style.accent_soft} px-4 py-2 text-xs font-semibold md:inline-flex\">Hire me</a>\n"
            f"        <button type=\"button\" className=\"md:hidden {style.radius} border {style.border} px-3 py-1.5 text-xs\" onClick={{() => setOpen(v => !v)}}>Menu</button>\n"
            "      </div>\n"
            "      {open && (\n"
            f"        <div className=\"grid gap-2 border-t {style.border} px-4 py-3 md:hidden\">\n"
            "          {links.map((l) => <a key={l.href} href={l.href} onClick={() => setOpen(false)} className=\"py-2 text-sm\">{l.label}</a>)}\n"
            "        </div>\n"
            "      )}\n"
            "    </header>\n"
            "  )\n"
            "}\n"
        ),
    )


def _hero(style: StylePack) -> GeneratedFile:
    if style.hero_layout == "stack":
        body = (
            "      <div className=\"relative mx-auto max-w-4xl px-4 py-20 md:py-28\">\n"
            f"        <p className=\"text-xs font-semibold uppercase tracking-[0.28em] {style.accent}\">{{portfolio.styleLabel}}</p>\n"
            f"        <h1 className=\"mt-5 text-5xl {style.display_weight} tracking-tight {style.ink} md:text-6xl\">{{portfolio.name}}</h1>\n"
            f"        <p className=\"mt-4 text-xl {style.accent}\">{{portfolio.role}}</p>\n"
            f"        <p className=\"mt-6 max-w-2xl text-lg leading-relaxed {style.muted}\">{{portfolio.tagline}}</p>\n"
            "        <div className=\"mt-10 flex flex-wrap gap-3\">\n"
            "          <PortfolioButton href=\"#projects\">View projects</PortfolioButton>\n"
            "          <PortfolioButton href=\"#contact\" variant=\"ghost\">Contact</PortfolioButton>\n"
            "        </div>\n"
            "      </div>\n"
        )
    elif style.hero_layout == "banner":
        body = (
            "      <div className=\"relative mx-auto max-w-6xl px-4 py-16 md:py-24\">\n"
            f"        <div className=\"{style.panel} overflow-hidden p-8 md:p-12\">\n"
            "          <div className=\"grid gap-8 md:grid-cols-[1.4fr_0.6fr] md:items-end\">\n"
            "            <div>\n"
            f"              <p className=\"text-xs font-bold uppercase tracking-[0.24em] {style.accent}\">{{portfolio.styleLabel}}</p>\n"
            f"              <h1 className=\"mt-4 text-4xl {style.display_weight} tracking-tight sm:text-6xl\">{{portfolio.name}}</h1>\n"
            f"              <p className=\"mt-4 text-lg {style.muted}\">{{portfolio.tagline}}</p>\n"
            "              <div className=\"mt-8 flex flex-wrap gap-3\">\n"
            "                <PortfolioButton href=\"#projects\">See work</PortfolioButton>\n"
            "                <PortfolioButton href=\"#contact\" variant=\"ghost\">Hire</PortfolioButton>\n"
            "              </div>\n"
            "            </div>\n"
            f"            <div className=\"{style.accent_soft} {style.radius} p-6 text-sm\">\n"
            "              <p className=\"font-bold\">{portfolio.role}</p>\n"
            "              <p className=\"mt-2 opacity-90\">{portfolio.location}</p>\n"
            "              <p className=\"mt-4 text-xs opacity-80\">Edit src/data/portfolio.ts</p>\n"
            "            </div>\n"
            "          </div>\n"
            "        </div>\n"
            "      </div>\n"
        )
    else:
        glow = (
            "      <div className=\"pointer-events-none absolute -left-24 top-0 h-72 w-72 rounded-full bg-cyan-500/20 blur-3xl\" />\n"
            "      <div className=\"pointer-events-none absolute -right-16 top-24 h-72 w-72 rounded-full bg-indigo-500/20 blur-3xl\" />\n"
            if style.id == "aurora"
            else (
                "      <div className=\"pointer-events-none absolute -left-16 top-10 h-64 w-64 rounded-full bg-lime-300/10 blur-3xl\" />\n"
                if style.id == "terminal"
                else ""
            )
        )
        body = (
            f"{glow}"
            "      <div className=\"relative mx-auto grid max-w-5xl gap-10 px-4 py-20 md:grid-cols-[1.2fr_0.8fr] md:py-28\">\n"
            "        <div>\n"
            f"          <p className=\"text-xs font-semibold uppercase tracking-[0.28em] {style.accent}\">{{portfolio.styleLabel}}</p>\n"
            f"          <h1 className=\"mt-4 text-4xl {style.display_weight} tracking-tight {style.ink} sm:text-5xl md:text-6xl\">{{portfolio.name}}</h1>\n"
            f"          <p className=\"mt-3 text-lg {style.accent}\">{{portfolio.role}}</p>\n"
            f"          <p className=\"mt-5 max-w-xl text-base leading-relaxed {style.muted}\">{{portfolio.tagline}}</p>\n"
            "          <div className=\"mt-8 flex flex-wrap gap-3\">\n"
            "            <PortfolioButton href=\"#projects\">View projects</PortfolioButton>\n"
            "            <PortfolioButton href=\"#contact\" variant=\"ghost\">Contact</PortfolioButton>\n"
            "          </div>\n"
            "          <div className=\"mt-8 flex flex-wrap gap-2\">\n"
            f"            {{portfolio.stack.map((s) => <span key={{s}} className=\"{style.radius} border {style.border} px-3 py-1 text-xs\">{{s}}</span>)}}\n"
            "          </div>\n"
            "        </div>\n"
            f"        <div className=\"{style.panel} p-6\">\n"
            f"          <p className=\"text-xs uppercase tracking-[0.2em] {style.muted}\">Quick facts</p>\n"
            "          <ul className=\"mt-4 space-y-3 text-sm\">\n"
            f"            <li className=\"flex justify-between gap-4 border-b {style.border} pb-3\"><span className=\"{style.muted}\">Focus</span><span>{{portfolio.role}}</span></li>\n"
            f"            <li className=\"flex justify-between gap-4 border-b {style.border} pb-3\"><span className=\"{style.muted}\">Location</span><span>{{portfolio.location}}</span></li>\n"
            "            <li className=\"flex justify-between gap-4\"><span className={style.muted}>Open to</span><span>Freelance · Full-time</span></li>\n"
            "          </ul>\n"
            f"          <p className=\"mt-6 text-xs leading-relaxed {style.muted}\">Edit <code>src/data/portfolio.ts</code> to personalize.</p>\n"
            "        </div>\n"
            "      </div>\n"
        )

    # Fix the Open to line - I mixed style.muted incorrectly
    body = body.replace(
        "<li className=\"flex justify-between gap-4\"><span className={style.muted}>Open to</span><span>Freelance · Full-time</span></li>",
        f'<li className="flex justify-between gap-4"><span className="{style.muted}">Open to</span><span>Freelance · Full-time</span></li>',
    )

    return GeneratedFile(
        path="src/components/PortfolioHero.tsx",
        content=(
            "import { portfolio } from '../data/portfolio'\n"
            "import { PortfolioButton } from './PortfolioButton'\n\n"
            "export function PortfolioHero() {\n"
            "  return (\n"
            "    <section className=\"relative overflow-hidden\">\n"
            f"{body}"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _sections(style: StylePack) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/PortfolioSections.tsx",
        content=(
            "import { portfolio } from '../data/portfolio'\n"
            "import { PortfolioButton } from './PortfolioButton'\n\n"
            "export function AboutSection() {\n"
            "  return (\n"
            "    <section id=\"about\" className=\"mx-auto max-w-5xl px-4 py-16\">\n"
            f"      <p className=\"text-xs font-semibold uppercase tracking-[0.22em] {style.accent}\">About</p>\n"
            f"      <h2 className=\"mt-3 text-3xl {style.display_weight} tracking-tight\">Built to be edited</h2>\n"
            f"      <p className=\"mt-5 max-w-3xl text-base leading-relaxed {style.muted}\">{{portfolio.about}}</p>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            "export function SkillsSection() {\n"
            "  return (\n"
            "    <section id=\"skills\" className=\"mx-auto max-w-5xl px-4 py-16\">\n"
            f"      <p className=\"text-xs font-semibold uppercase tracking-[0.22em] {style.accent}\">Skills</p>\n"
            f"      <h2 className=\"mt-3 text-3xl {style.display_weight} tracking-tight\">What I work with</h2>\n"
            "      <div className=\"mt-8 grid gap-3 sm:grid-cols-2 md:grid-cols-3\">\n"
            f"        {{portfolio.skills.map((s) => (\n"
            f"          <div key={{s}} className=\"{style.panel} px-4 py-4 text-sm\">{{s}}</div>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            "export function ExperienceSection() {\n"
            "  return (\n"
            "    <section id=\"experience\" className=\"mx-auto max-w-5xl px-4 py-16\">\n"
            f"      <p className=\"text-xs font-semibold uppercase tracking-[0.22em] {style.accent}\">Experience</p>\n"
            f"      <h2 className=\"mt-3 text-3xl {style.display_weight} tracking-tight\">Recent work</h2>\n"
            "      <div className=\"mt-8 space-y-4\">\n"
            "        {portfolio.experience.map((job) => (\n"
            f"          <article key={{job.role + job.org}} className=\"{style.panel} p-6\">\n"
            "            <div className=\"flex flex-wrap items-baseline justify-between gap-2\">\n"
            f"              <h3 className=\"text-lg {style.display_weight}\">{{job.role}} · {{job.org}}</h3>\n"
            f"              <span className=\"text-xs {style.muted}\">{{job.period}}</span>\n"
            "            </div>\n"
            f"            <ul className=\"mt-4 space-y-2 text-sm {style.muted}\">\n"
            f"              {{job.points.map((p) => <li key={{p}} className=\"flex gap-2\"><span className=\"{style.accent}\">▹</span><span>{{p}}</span></li>)}}\n"
            "            </ul>\n"
            "          </article>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            "export function ProjectsSection() {\n"
            "  return (\n"
            "    <section id=\"projects\" className=\"mx-auto max-w-5xl px-4 py-16\">\n"
            f"      <p className=\"text-xs font-semibold uppercase tracking-[0.22em] {style.accent}\">Projects</p>\n"
            f"      <h2 className=\"mt-3 text-3xl {style.display_weight} tracking-tight\">Selected work</h2>\n"
            "      <div className=\"mt-8 grid gap-4 md:grid-cols-3\">\n"
            "        {portfolio.projects.map((p) => (\n"
            f"          <a key={{p.title}} href={{p.href}} className=\"group {style.panel} p-5 transition hover:opacity-95\">\n"
            f"            <h3 className=\"text-lg {style.display_weight}\">{{p.title}}</h3>\n"
            f"            <p className=\"mt-3 text-sm leading-relaxed {style.muted}\">{{p.blurb}}</p>\n"
            "            <div className=\"mt-4 flex flex-wrap gap-2\">{p.tags.map((t) => (\n"
            f"              <span key={{t}} className=\"border {style.border} px-2.5 py-1 text-[11px]\">{{t}}</span>\n"
            "            ))}</div>\n"
            "          </a>\n"
            "        ))}\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n\n"
            "export function ContactSection() {\n"
            "  return (\n"
            "    <section id=\"contact\" className=\"mx-auto max-w-5xl px-4 py-16 pb-24\">\n"
            f"      <div className=\"{style.panel} p-8 md:p-10\">\n"
            f"        <p className=\"text-xs font-semibold uppercase tracking-[0.22em] {style.accent}\">Contact</p>\n"
            f"        <h2 className=\"mt-3 text-3xl {style.display_weight} tracking-tight\">Let's build something</h2>\n"
            f"        <p className=\"mt-3 max-w-xl {style.muted}\">Tell me about your app, API, or product idea.</p>\n"
            "        <form className=\"mt-8 grid max-w-lg gap-3\" onSubmit={(e) => e.preventDefault()}>\n"
            f"          <input className=\"border {style.border} bg-transparent px-3 py-3 text-sm outline-none {style.radius}\" placeholder=\"Name\" required />\n"
            f"          <input type=\"email\" className=\"border {style.border} bg-transparent px-3 py-3 text-sm outline-none {style.radius}\" placeholder=\"Email\" required />\n"
            f"          <textarea className=\"min-h-28 border {style.border} bg-transparent px-3 py-3 text-sm outline-none {style.radius}\" placeholder=\"Project details\" required />\n"
            "          <PortfolioButton href=\"#\">Send message</PortfolioButton>\n"
            "        </form>\n"
            f"        <p className=\"mt-6 text-sm {style.muted}\">{{portfolio.email}}</p>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _footer(name: str, style: StylePack) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/PortfolioFooter.tsx",
        content=(
            "export function PortfolioFooter() {\n"
            "  return (\n"
            f"    <footer className=\"border-t {style.border}\">\n"
            f"      <div className=\"mx-auto flex max-w-5xl flex-col gap-2 px-4 py-8 text-sm {style.muted} sm:flex-row sm:items-center sm:justify-between\">\n"
            f"        <p>© {{new Date().getFullYear()}} {name}. {style.label} template — edit freely.</p>\n"
            "        <p>Flutter · Python · Product-minded engineering</p>\n"
            "      </div>\n"
            "    </footer>\n"
            "  )\n"
            "}\n"
        ),
    )

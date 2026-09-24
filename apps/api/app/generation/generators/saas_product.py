"""SaaS / AI product specialty — video generators, AI tools, product landings."""

from __future__ import annotations

import re

from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements


def generate_saas_product(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    analysis = requirements.analysis
    # Prefer planned brand (invented) over analyzer catalog labels like "SaaS Startup"
    brand = (plan.project_name or getattr(analysis, "brand_name", "") or "LumaClip").strip()
    brand = _clean_brand(brand) or "LumaClip"
    prompt = (analysis.raw_prompt or "").lower()
    primary = analysis.theme.get("primary_color", "#7C3AED")
    product = _product_kind(prompt)
    tagline = _product_tagline(product, brand)
    cta = "Start free" if "video" in product or "ai" in product else "Get started"

    files: list[GeneratedFile] = [
        _tokens(primary),
        _button(primary),
        _navbar(brand, plan, primary, cta),
        _hero(brand, tagline, cta, product, primary),
        _social_proof(),
        _features(product),
        _how_it_works(product),
        _demo(product, primary),
        _pricing(brand, primary),
        _faq(product),
        _cta_banner(brand, cta, primary),
        _footer(brand, plan),
        _use_theme(),
    ]

    for route in plan.routes:
        page = route["page"].lower().replace(" ", "")
        comp = route["component"]
        if route["path"] == "/":
            body = _home_page(brand)
        elif "feature" in page:
            body = _features_page(comp, product)
        elif "pric" in page:
            body = _pricing_page(comp, brand, primary)
        elif "about" in page:
            body = _about_page(comp, brand, product)
        elif "contact" in page:
            body = _contact_page(comp, brand, primary)
        elif "doc" in page:
            body = _docs_page(comp, brand, product)
        else:
            body = _simple_page(comp, route["page"], brand)
        files.append(GeneratedFile(path=f"src/pages/{comp}.tsx", content=body))

    files.append(
        GeneratedFile(
            path="src/data/product.ts",
            content=(
                f'export const brandName = "{_esc(brand)}"\n'
                f'export const productKind = "{_esc(product)}"\n'
                f'export const tagline = "{_esc(tagline)}"\n'
            ),
        )
    )
    return files


def _clean_brand(name: str) -> str:
    name = re.split(
        r"\b(?:so|please|and give|create|make|build|website|design|give me|attractive|full)\b",
        name,
        maxsplit=1,
        flags=re.I,
    )[0].strip(" .,!?'\"-")
    banned = {
        "",
        "saas startup",
        "ai product",
        "marketing landing page",
        "landing page",
        "software",
        "startup",
        "generated site",
        "new",
        "untitled",
    }
    if name.lower() in banned:
        return ""
    if len(name) > 28 or re.search(r"\b(want|generator|website|design|saas|startup)\b", name, re.I):
        return ""
    return name


def _product_kind(prompt: str) -> str:
    p = prompt.replace("ganerator", "generator").replace("generater", "generator")
    if any(k in p for k in ("video", "reel", "clip", "text to video", "ai video")):
        return "video"
    if any(k in p for k in ("image generator", "image ai", "text to image")):
        return "image"
    if any(k in p for k in ("ai tool", "ai app", "ai product", "llm", "chatgpt")):
        return "ai"
    return "saas"


def _product_tagline(kind: str, brand: str) -> str:
    if kind == "video":
        return f"Turn ideas into stunning videos in seconds — with {brand}."
    if kind == "image":
        return f"Generate beautiful images from a simple prompt — powered by {brand}."
    if kind == "ai":
        return f"Ship faster with AI that understands your workflow — meet {brand}."
    return f"The modern platform teams use to build, launch, and grow — {brand}."


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _tokens(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/styles/product.css",
        content=(
            f":root {{\n"
            f"  --brand: {primary};\n"
            f"  --brand-soft: color-mix(in oklab, {primary} 18%, white);\n"
            f"}}\n"
        ),
    )


def _button(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Button.tsx",
        content=(
            "type ButtonProps = {\n"
            "  children: React.ReactNode\n"
            "  variant?: 'primary' | 'ghost' | 'soft'\n"
            "  href?: string\n"
            "  className?: string\n"
            "}\n\n"
            "export function Button({ children, variant = 'primary', href = '#', className = '' }: ButtonProps) {\n"
            "  const base = 'inline-flex items-center justify-center rounded-xl px-5 py-2.5 text-sm font-semibold transition '\n"
            "  const styles =\n"
            "    variant === 'primary'\n"
            "      ? 'text-white shadow-lg hover:brightness-110'\n"
            "      : variant === 'soft'\n"
            f"        ? 'hover:opacity-90'\n"
            "        : 'border border-slate-200 bg-white text-slate-800 hover:bg-slate-50'\n"
            "  const softStyle = variant === 'soft' ? { backgroundColor: 'color-mix(in oklab, var(--brand) 14%, white)', color: 'var(--brand)' } : undefined\n"
            "  const shadow = variant === 'primary' ? { backgroundColor: 'var(--brand)', boxShadow: '0 12px 28px -14px color-mix(in oklab, var(--brand) 55%, transparent)' } : softStyle\n"
            "  return (\n"
            "    <a href={href} className={`${base}${styles} ${className}`} style={shadow}>\n"
            "      {children}\n"
            "    </a>\n"
            "  )\n"
            "}\n"
        ),
    )


def _navbar(brand: str, plan: ProjectPlan, primary: str, cta: str = "Start free") -> GeneratedFile:
    links = []
    for r in plan.routes:
        if r["path"] == "/":
            continue
        label = r["page"]
        if label.lower() in {"docs", "blog"}:
            continue
        links.append(f'    {{ to: "{r["path"]}", label: "{label}" }},')
    links_js = "\n".join(links) or '    { to: "/features", label: "Features" },\n    { to: "/pricing", label: "Pricing" },'
    return GeneratedFile(
        path="src/components/ProductNavbar.tsx",
        content=(
            "import { Link, NavLink } from 'react-router-dom'\n"
            "import { Button } from './Button'\n\n"
            f"const links = [\n{links_js}\n]\n\n"
            "export function ProductNavbar() {\n"
            "  return (\n"
            "    <header className=\"sticky top-0 z-40 border-b border-slate-200/80 bg-white/80 backdrop-blur-xl\">\n"
            "      <div className=\"mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6\">\n"
            f"        <Link to=\"/\" className=\"text-[15px] font-bold tracking-tight text-slate-900 no-underline\">\n"
            f"          <span className=\"mr-1.5 inline-block h-2 w-2 rounded-full\" style={{{{ backgroundColor: '{primary}' }}}} />\n"
            f"          {_esc(brand)}\n"
            "        </Link>\n"
            "        <nav className=\"hidden items-center gap-1 md:flex\">\n"
            "          {links.map((l) => (\n"
            "            <NavLink\n"
            "              key={l.to}\n"
            "              to={l.to}\n"
            "              className={({ isActive }) =>\n"
            "                `rounded-lg px-3 py-1.5 text-sm font-medium no-underline ${isActive ? 'bg-slate-100 text-slate-900' : 'text-slate-600 hover:text-slate-900'}`\n"
            "              }\n"
            "            >\n"
            "              {l.label}\n"
            "            </NavLink>\n"
            "          ))}\n"
            "        </nav>\n"
            "        <div className=\"flex items-center gap-2\">\n"
            "          <Button href=\"#demo\" variant=\"ghost\" className=\"hidden sm:inline-flex\">Sign in</Button>\n"
            f"          <Button href=\"#pricing\">{_esc(cta)}</Button>\n"
            "        </div>\n"
            "      </div>\n"
            "    </header>\n"
            "  )\n"
            "}\n"
        ),
    )


def _hero(brand: str, tagline: str, cta: str, product: str, primary: str) -> GeneratedFile:
    eyebrow = {
        "video": "AI Video Generator",
        "image": "AI Image Generator",
        "ai": "AI Platform",
        "saas": "Product Platform",
    }.get(product, "AI Product")
    headlines = {
        "video": f"Turn prompts into polished videos with {_esc(brand)}",
        "image": f"Generate stunning visuals with {_esc(brand)}",
        "ai": f"Ship faster with {_esc(brand)}",
        "saas": f"Launch and grow with {_esc(brand)}",
    }
    headline = headlines.get(product, f"Build with {_esc(brand)}")
    preview_label = "Script → cinematic clip" if product == "video" else "Prompt → polished output"
    return GeneratedFile(
        path="src/components/ProductHero.tsx",
        content=(
            "import { Button } from './Button'\n"
            "import '../styles/product.css'\n\n"
            "export function ProductHero() {\n"
            "  return (\n"
            "    <section className=\"relative overflow-hidden border-b border-slate-200 bg-gradient-to-b from-[color-mix(in_oklab,var(--brand)_10%,white)] via-white to-white\">\n"
            "      <div className=\"pointer-events-none absolute -left-24 top-10 h-64 w-64 rounded-full blur-3xl\" style={{ backgroundColor: 'color-mix(in oklab, var(--brand) 28%, transparent)' }} />\n"
            "      <div className=\"pointer-events-none absolute -right-20 bottom-0 h-72 w-72 rounded-full blur-3xl\" style={{ backgroundColor: 'color-mix(in oklab, var(--brand) 18%, transparent)' }} />\n"
            "      <div className=\"relative mx-auto grid max-w-6xl gap-12 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:items-center lg:py-28\">\n"
            "        <div>\n"
            f"          <p className=\"mb-4 inline-flex rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-wider\" style={{{{ color: '{primary}' }}}}>{eyebrow}</p>\n"
            f"          <h1 className=\"text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl lg:text-[3.25rem] lg:leading-[1.1]\">{headline}</h1>\n"
            f"          <p className=\"mt-5 max-w-lg text-lg leading-relaxed text-slate-600\">{_esc(tagline)}</p>\n"
            "          <div className=\"mt-8 flex flex-wrap gap-3\">\n"
            f"            <Button href=\"#demo\">{_esc(cta)}</Button>\n"
            "            <Button href=\"#how\" variant=\"ghost\">See how it works</Button>\n"
            "          </div>\n"
            "          <p className=\"mt-6 text-sm text-slate-500\">No credit card · Export in HD · Ready in minutes</p>\n"
            "        </div>\n"
            "        <div className=\"relative\">\n"
            "          <div className=\"rounded-2xl border border-slate-200 bg-slate-950 p-3 shadow-2xl\" style={{ boxShadow: '0 28px 60px -28px color-mix(in oklab, var(--brand) 45%, transparent)' }}>\n"
            "            <div className=\"flex items-center gap-1.5 px-2 pb-3\">\n"
            "              <span className=\"h-2.5 w-2.5 rounded-full bg-rose-400\" />\n"
            "              <span className=\"h-2.5 w-2.5 rounded-full bg-amber-400\" />\n"
            "              <span className=\"h-2.5 w-2.5 rounded-full bg-emerald-400\" />\n"
            f"              <span className=\"ml-2 text-xs text-slate-400\">{preview_label}</span>\n"
            "            </div>\n"
            f"            <div className=\"min-h-[240px] overflow-hidden rounded-xl p-6\" style={{{{ background: `linear-gradient(145deg, {primary}, #0f172a 72%)` }}}}>\n"
            "              <div className=\"rounded-lg border border-white/15 bg-white/10 p-4 backdrop-blur\">\n"
            "                <p className=\"text-xs font-medium uppercase tracking-wide text-white/70\">Prompt</p>\n"
            "                <p className=\"mt-2 text-sm leading-relaxed text-white\">A neon city street at night, slow camera push-in, cinematic lighting…</p>\n"
            "              </div>\n"
            "              <div className=\"mt-4 flex items-center justify-between rounded-lg bg-black/30 px-4 py-3\">\n"
            "                <div className=\"h-1.5 flex-1 overflow-hidden rounded-full bg-white/20\">\n"
            "                  <div className=\"h-full w-2/3 rounded-full bg-white\" />\n"
            "                </div>\n"
            "                <span className=\"ml-3 text-xs font-semibold text-white\">Rendering 67%</span>\n"
            "              </div>\n"
            "            </div>\n"
            "          </div>\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _social_proof() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/SocialProof.tsx",
        content=(
            "const brands = ['Studio North', 'Pulse Media', 'Orbit Labs', 'Frame Co', 'Nova Ads']\n\n"
            "export function SocialProof() {\n"
            "  return (\n"
            "    <section className=\"border-b border-slate-100 bg-white py-12\">\n"
            "      <div className=\"mx-auto max-w-6xl px-4 sm:px-6\">\n"
            "        <p className=\"text-center text-xs font-semibold uppercase tracking-wider text-slate-400\">Trusted by creators at</p>\n"
            "        <ul className=\"mt-6 flex flex-wrap items-center justify-center gap-x-10 gap-y-4\">\n"
            "          {brands.map((b) => (\n"
            "            <li key={b} className=\"text-sm font-semibold tracking-tight text-slate-500\">{b}</li>\n"
            "          ))}\n"
            "        </ul>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _features(product: str) -> GeneratedFile:
    if product == "video":
        items = [
            ("Text to video", "Describe a scene — get a polished clip with motion, music, and captions."),
            ("Brand kits", "Lock fonts, colors, and logos so every export looks on-brand."),
            ("Smart edits", "Auto-cut silence, add transitions, and sync beats without a timeline."),
            ("HD exports", "Download 1080p / 4K for social, ads, and product demos."),
            ("Templates", "Start from proven formats for reels, ads, explainers, and launches."),
            ("Team workspace", "Share drafts, comment, and approve before you publish."),
        ]
    elif product == "image":
        items = [
            ("Prompt studio", "Iterate fast with style presets and reference images."),
            ("Upscale & edit", "Fix details, expand canvases, and remove backgrounds."),
            ("Brand styles", "Save your look once — reuse it across campaigns."),
            ("Batch generate", "Create dozens of variants for ads and social in one run."),
            ("Commercial license", "Clear rights for client work and product pages."),
            ("API access", "Plug generation into your product or pipeline."),
        ]
    else:
        items = [
            ("Fast setup", "Go from idea to live product surface in minutes."),
            ("Beautiful UI", "Conversion-ready layouts with modern motion and clarity."),
            ("Integrations", "Connect the tools your team already uses."),
            ("Analytics", "See what converts — improve with real usage signals."),
            ("Security", "Roles, SSO-ready patterns, and sensible defaults."),
            ("Support", "Docs, examples, and a team that ships with you."),
        ]
    items_js = ",\n".join(
        f'  {{ title: "{t}", body: "{b}" }}' for t, b in items
    )
    return GeneratedFile(
        path="src/components/FeatureGrid.tsx",
        content=(
            f"const features = [\n{items_js}\n]\n\n"
            "export function FeatureGrid() {\n"
            "  return (\n"
            "    <section id=\"features\" className=\"bg-slate-50 py-20\">\n"
            "      <div className=\"mx-auto max-w-6xl px-4 sm:px-6\">\n"
            "        <p className=\"text-sm font-semibold uppercase tracking-wider\" style={{ color: 'var(--brand)' }}>Features</p>\n"
            "        <h2 className=\"mt-2 text-3xl font-bold tracking-tight text-slate-900\">Everything you need to ship</h2>\n"
            "        <p className=\"mt-3 max-w-2xl text-slate-600\">Built for creators who want premium output without a production team.</p>\n"
            "        <ul className=\"mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3\">\n"
            "          {features.map((f) => (\n"
            "            <li key={f.title} className=\"rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md\">\n"
            "              <div className=\"mb-4 h-9 w-9 rounded-xl\" style={{ backgroundColor: 'color-mix(in oklab, var(--brand) 16%, white)' }} />\n"
            "              <h3 className=\"text-lg font-semibold text-slate-900\">{f.title}</h3>\n"
            "              <p className=\"mt-2 text-sm leading-relaxed text-slate-600\">{f.body}</p>\n"
            "            </li>\n"
            "          ))}\n"
            "        </ul>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _how_it_works(product: str) -> GeneratedFile:
    if product == "video":
        steps = [
            ("1", "Describe", "Write a short prompt or paste a script."),
            ("2", "Generate", "AI builds scenes, motion, and audio."),
            ("3", "Polish", "Tweak captions, brand, and length."),
            ("4", "Export", "Download or share to social in one click."),
        ]
    else:
        steps = [
            ("1", "Describe", "Tell us what you want to create."),
            ("2", "Generate", "Get a polished first draft instantly."),
            ("3", "Refine", "Adjust style, tone, and details."),
            ("4", "Ship", "Export, embed, or publish."),
        ]
    steps_js = ",\n".join(f'  {{ n: "{n}", title: "{t}", body: "{b}" }}' for n, t, b in steps)
    return GeneratedFile(
        path="src/components/HowItWorks.tsx",
        content=(
            f"const steps = [\n{steps_js}\n]\n\n"
            "export function HowItWorks() {\n"
            "  return (\n"
            "    <section id=\"how\" className=\"bg-white py-20\">\n"
            "      <div className=\"mx-auto max-w-6xl px-4 sm:px-6\">\n"
            "        <p className=\"text-sm font-semibold uppercase tracking-wider\" style={{ color: 'var(--brand)' }}>How it works</p>\n"
            "        <h2 className=\"mt-2 text-3xl font-bold tracking-tight text-slate-900\">From prompt to finished piece</h2>\n"
            "        <ol className=\"mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4\">\n"
            "          {steps.map((s) => (\n"
            "            <li key={s.n} className=\"rounded-2xl border border-slate-200 p-5\">\n"
            "              <span className=\"text-2xl font-bold\" style={{ color: 'var(--brand)' }}>{s.n}</span>\n"
            "              <h3 className=\"mt-3 font-semibold text-slate-900\">{s.title}</h3>\n"
            "              <p className=\"mt-2 text-sm text-slate-600\">{s.body}</p>\n"
            "            </li>\n"
            "          ))}\n"
            "        </ol>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _demo(product: str, primary: str) -> GeneratedFile:
    placeholder = (
        "A product launch reel with bold captions and upbeat music…"
        if product == "video"
        else "Describe what you want to create…"
    )
    return GeneratedFile(
        path="src/components/DemoWidget.tsx",
        content=(
            "import { useState } from 'react'\n\n"
            "export function DemoWidget() {\n"
            "  const [value, setValue] = useState('')\n"
            "  const [done, setDone] = useState(false)\n"
            "  return (\n"
            "    <section id=\"demo\" className=\"border-y border-slate-200 bg-slate-950 py-20 text-white\">\n"
            "      <div className=\"mx-auto max-w-3xl px-4 sm:px-6\">\n"
            "        <h2 className=\"text-center text-3xl font-bold tracking-tight\">Try it in your browser</h2>\n"
            "        <p className=\"mt-3 text-center text-slate-400\">Type a prompt — see how the studio responds.</p>\n"
            "        <div className=\"mt-8 rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur\">\n"
            "          <textarea\n"
            f"            placeholder=\"{_esc(placeholder)}\"\n"
            "            value={value}\n"
            "            onChange={(e) => { setValue(e.target.value); setDone(false) }}\n"
            "            className=\"min-h-28 w-full resize-none rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-[var(--brand)]\"\n"
            "          />\n"
            "          <div className=\"mt-3 flex justify-end\">\n"
            "            <button\n"
            "              type=\"button\"\n"
            "              onClick={() => setDone(true)}\n"
            f"              className=\"rounded-xl px-5 py-2.5 text-sm font-semibold text-white\"\n"
            f"              style={{{{ backgroundColor: '{primary}' }}}}\n"
            "            >\n"
            "              Generate preview\n"
            "            </button>\n"
            "          </div>\n"
            "          {done && (\n"
            "            <p className=\"mt-4 rounded-xl bg-emerald-500/15 px-4 py-3 text-sm text-emerald-300\">\n"
            "              Preview queued — in the full product this becomes your rendered output.\n"
            "            </p>\n"
            "          )}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _pricing(brand: str, primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/PricingTable.tsx",
        content=(
            "import { Button } from './Button'\n\n"
            "const plans = [\n"
            "  { name: 'Starter', price: '$0', note: 'For trying ideas', perks: ['20 generations / mo', '720p export', 'Watermark-free previews'], cta: 'Start free', featured: false },\n"
            "  { name: 'Pro', price: '$29', note: 'For creators who ship', perks: ['Unlimited drafts', '1080p / 4K', 'Brand kits', 'Priority render'], cta: 'Go Pro', featured: true },\n"
            "  { name: 'Team', price: '$79', note: 'For studios', perks: ['Seats & roles', 'Shared library', 'API access', 'SSO-ready'], cta: 'Contact sales', featured: false },\n"
            "]\n\n"
            "export function PricingTable() {\n"
            "  return (\n"
            "    <section id=\"pricing\" className=\"bg-white py-20\">\n"
            "      <div className=\"mx-auto max-w-6xl px-4 sm:px-6\">\n"
            "        <p className=\"text-sm font-semibold uppercase tracking-wider\" style={{ color: 'var(--brand)' }}>Pricing</p>\n"
            f"        <h2 className=\"mt-2 text-3xl font-bold tracking-tight text-slate-900\">Simple plans for {_esc(brand)}</h2>\n"
            "        <div className=\"mt-12 grid gap-5 lg:grid-cols-3\">\n"
            "          {plans.map((p) => (\n"
            "            <div\n"
            "              key={p.name}\n"
            "              className={`flex flex-col rounded-2xl border p-6 ${p.featured ? 'shadow-lg' : 'border-slate-200 bg-white'}`}\n"
            "              style={p.featured ? { borderColor: 'color-mix(in oklab, var(--brand) 45%, white)', backgroundColor: 'color-mix(in oklab, var(--brand) 8%, white)', boxShadow: '0 18px 40px -24px color-mix(in oklab, var(--brand) 40%, transparent)' } : undefined}\n"
            "            >\n"
            "              <div className=\"flex items-center justify-between\">\n"
            "                <h3 className=\"text-lg font-semibold text-slate-900\">{p.name}</h3>\n"
            "                {p.featured && <span className=\"rounded-full px-2.5 py-0.5 text-[11px] font-semibold text-white\" style={{ backgroundColor: 'var(--brand)' }}>Popular</span>}\n"
            "              </div>\n"
            "              <p className=\"mt-4 text-3xl font-bold text-slate-900\">{p.price}<span className=\"text-sm font-medium text-slate-500\">/mo</span></p>\n"
            "              <p className=\"mt-1 text-sm text-slate-600\">{p.note}</p>\n"
            "              <ul className=\"mt-6 flex-1 space-y-2\">\n"
            "                {p.perks.map((x) => (\n"
            "                  <li key={x} className=\"text-sm text-slate-700\">✓ {x}</li>\n"
            "                ))}\n"
            "              </ul>\n"
            "              <Button href=\"#demo\" variant={p.featured ? 'primary' : 'ghost'} className=\"mt-8 w-full\">{p.cta}</Button>\n"
            "            </div>\n"
            "          ))}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _faq(product: str) -> GeneratedFile:
    q1 = "Can I use videos commercially?" if product == "video" else "Can I use outputs commercially?"
    a1 = "Yes on Pro and Team — exports include a commercial license for ads and client work."
    return GeneratedFile(
        path="src/components/FAQ.tsx",
        content=(
            "const faqs = [\n"
            f'  {{ q: "{q1}", a: "{a1}" }},\n'
            '  { q: "Do I need editing experience?", a: "No. Start from a prompt or template — polish only what you care about." },\n'
            '  { q: "How fast is generation?", a: "Most drafts render in under a minute depending on length and quality." },\n'
            '  { q: "Can my team collaborate?", a: "Team plans include shared libraries, comments, and approval flows." },\n'
            "]\n\n"
            "export function FAQ() {\n"
            "  return (\n"
            "    <section className=\"bg-slate-50 py-20\">\n"
            "      <div className=\"mx-auto max-w-3xl px-4 sm:px-6\">\n"
            "        <h2 className=\"text-center text-3xl font-bold tracking-tight text-slate-900\">FAQ</h2>\n"
            "        <ul className=\"mt-10 space-y-4\">\n"
            "          {faqs.map((f) => (\n"
            "            <li key={f.q} className=\"rounded-2xl border border-slate-200 bg-white p-5\">\n"
            "              <h3 className=\"font-semibold text-slate-900\">{f.q}</h3>\n"
            "              <p className=\"mt-2 text-sm leading-relaxed text-slate-600\">{f.a}</p>\n"
            "            </li>\n"
            "          ))}\n"
            "        </ul>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _cta_banner(brand: str, cta: str, primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/CTABanner.tsx",
        content=(
            "export function CTABanner() {\n"
            "  return (\n"
            f"    <section className=\"py-20\" style={{{{ background: `linear-gradient(135deg, {primary}, #0f172a)` }}}}>\n"
            "      <div className=\"mx-auto max-w-3xl px-4 text-center sm:px-6\">\n"
            f"        <h2 className=\"text-3xl font-bold text-white\">Ready to create with {_esc(brand)}?</h2>\n"
            "        <p className=\"mt-3 text-white/80\">Start free — upgrade when you outgrow the starter plan.</p>\n"
            f"        <div className=\"mt-8 flex justify-center\"><a href=\"#demo\" className=\"inline-flex rounded-xl bg-white px-6 py-3 text-sm font-semibold no-underline\" style={{{{ color: '{primary}' }}}}>{_esc(cta)}</a></div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _footer(brand: str, plan: ProjectPlan) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/ProductFooter.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n\n"
            "export function ProductFooter() {\n"
            "  return (\n"
            "    <footer className=\"border-t border-slate-200 bg-white py-12\">\n"
            "      <div className=\"mx-auto flex max-w-6xl flex-col gap-6 px-4 sm:flex-row sm:items-center sm:justify-between sm:px-6\">\n"
            f"        <p className=\"font-semibold text-slate-900\">{_esc(brand)}</p>\n"
            "        <div className=\"flex flex-wrap gap-4 text-sm text-slate-600\">\n"
            "          <Link to=\"/features\" className=\"no-underline hover:text-slate-900\">Features</Link>\n"
            "          <Link to=\"/pricing\" className=\"no-underline hover:text-slate-900\">Pricing</Link>\n"
            "          <Link to=\"/contact\" className=\"no-underline hover:text-slate-900\">Contact</Link>\n"
            "        </div>\n"
            f"        <p className=\"text-sm text-slate-400\">© {2026} {_esc(brand)}</p>\n"
            "      </div>\n"
            "    </footer>\n"
            "  )\n"
            "}\n"
        ),
    )


def _use_theme() -> GeneratedFile:
    return GeneratedFile(
        path="src/hooks/useTheme.ts",
        content="export function useTheme() {\n  return { isDark: false }\n}\n",
    )


def _home_page(brand: str) -> str:
    return (
        "import { ProductNavbar } from '../components/ProductNavbar'\n"
        "import { ProductHero } from '../components/ProductHero'\n"
        "import { SocialProof } from '../components/SocialProof'\n"
        "import { FeatureGrid } from '../components/FeatureGrid'\n"
        "import { HowItWorks } from '../components/HowItWorks'\n"
        "import { DemoWidget } from '../components/DemoWidget'\n"
        "import { PricingTable } from '../components/PricingTable'\n"
        "import { FAQ } from '../components/FAQ'\n"
        "import { CTABanner } from '../components/CTABanner'\n"
        "import { ProductFooter } from '../components/ProductFooter'\n\n"
        f"export default function HomePage() {{\n"
        "  return (\n"
        "    <div className=\"min-h-screen bg-white text-slate-900\">\n"
        "      <ProductNavbar />\n"
        "      <ProductHero />\n"
        "      <SocialProof />\n"
        "      <FeatureGrid />\n"
        "      <HowItWorks />\n"
        "      <DemoWidget />\n"
        "      <PricingTable />\n"
        "      <FAQ />\n"
        "      <CTABanner />\n"
        "      <ProductFooter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _features_page(comp: str, product: str) -> str:
    return (
        "import { ProductNavbar } from '../components/ProductNavbar'\n"
        "import { FeatureGrid } from '../components/FeatureGrid'\n"
        "import { ProductFooter } from '../components/ProductFooter'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"min-h-screen bg-white\">\n"
        "      <ProductNavbar />\n"
        "      <div className=\"mx-auto max-w-6xl px-4 py-16 sm:px-6\">\n"
        f"        <h1 className=\"text-4xl font-bold tracking-tight\">Features</h1>\n"
        f"        <p className=\"mt-3 text-slate-600\">Built for {_esc(product)} products that need to feel premium.</p>\n"
        "      </div>\n"
        "      <FeatureGrid />\n"
        "      <ProductFooter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _pricing_page(comp: str, brand: str, primary: str) -> str:
    return (
        "import { ProductNavbar } from '../components/ProductNavbar'\n"
        "import { PricingTable } from '../components/PricingTable'\n"
        "import { ProductFooter } from '../components/ProductFooter'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"min-h-screen bg-white\">\n"
        "      <ProductNavbar />\n"
        "      <PricingTable />\n"
        "      <ProductFooter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _about_page(comp: str, brand: str, product: str) -> str:
    return (
        "import { ProductNavbar } from '../components/ProductNavbar'\n"
        "import { ProductFooter } from '../components/ProductFooter'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"min-h-screen bg-white\">\n"
        "      <ProductNavbar />\n"
        "      <main className=\"mx-auto max-w-3xl px-4 py-20 sm:px-6\">\n"
        f"        <h1 className=\"text-4xl font-bold tracking-tight\">About {_esc(brand)}</h1>\n"
        f"        <p className=\"mt-6 text-lg leading-relaxed text-slate-600\">We build {_esc(product)} tools that turn rough ideas into finished, shippable creative — without a production crew.</p>\n"
        "      </main>\n"
        "      <ProductFooter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _contact_page(comp: str, brand: str, primary: str) -> str:
    return (
        "import { ProductNavbar } from '../components/ProductNavbar'\n"
        "import { ProductFooter } from '../components/ProductFooter'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"min-h-screen bg-white\">\n"
        "      <ProductNavbar />\n"
        "      <main className=\"mx-auto max-w-lg px-4 py-20 sm:px-6\">\n"
        f"        <h1 className=\"text-4xl font-bold tracking-tight\">Contact {_esc(brand)}</h1>\n"
        "        <form className=\"mt-8 space-y-4\" onSubmit={(e) => e.preventDefault()}>\n"
        "          <input className=\"w-full rounded-xl border border-slate-200 px-4 py-3 text-sm\" placeholder=\"Your name\" />\n"
        "          <input className=\"w-full rounded-xl border border-slate-200 px-4 py-3 text-sm\" placeholder=\"Email\" type=\"email\" />\n"
        "          <textarea className=\"min-h-28 w-full rounded-xl border border-slate-200 px-4 py-3 text-sm\" placeholder=\"How can we help?\" />\n"
        f"          <button type=\"submit\" className=\"w-full rounded-xl px-5 py-3 text-sm font-semibold text-white\" style={{{{ backgroundColor: '{primary}' }}}}>Send message</button>\n"
        "        </form>\n"
        "      </main>\n"
        "      <ProductFooter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _docs_page(comp: str, brand: str, product: str) -> str:
    return (
        "import { ProductNavbar } from '../components/ProductNavbar'\n"
        "import { ProductFooter } from '../components/ProductFooter'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"min-h-screen bg-white\">\n"
        "      <ProductNavbar />\n"
        "      <main className=\"mx-auto max-w-3xl px-4 py-20 sm:px-6\">\n"
        "        <h1 className=\"text-4xl font-bold tracking-tight\">Docs</h1>\n"
        f"        <p className=\"mt-4 text-slate-600\">Quickstart for {_esc(brand)} — describe, generate, refine, export.</p>\n"
        "        <ol className=\"mt-8 list-decimal space-y-3 pl-5 text-slate-700\">\n"
        "          <li>Open the studio and write a prompt.</li>\n"
        "          <li>Pick a template that matches your format.</li>\n"
        "          <li>Generate, polish, and export.</li>\n"
        "        </ol>\n"
        "      </main>\n"
        "      <ProductFooter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _simple_page(comp: str, title: str, brand: str) -> str:
    return (
        "import { ProductNavbar } from '../components/ProductNavbar'\n"
        "import { ProductFooter } from '../components/ProductFooter'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"min-h-screen bg-white\">\n"
        "      <ProductNavbar />\n"
        f"      <main className=\"mx-auto max-w-3xl px-4 py-20 sm:px-6\"><h1 className=\"text-4xl font-bold\">{_esc(title)}</h1><p className=\"mt-4 text-slate-600\">Part of {_esc(brand)}.</p></main>\n"
        "      <ProductFooter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )

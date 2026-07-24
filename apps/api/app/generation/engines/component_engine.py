"""Component Engine (Phase 3) — variant registry → Navbar/Hero/Footer TSX."""

from __future__ import annotations

from typing import Any

from app.generation.pipeline import GeneratedFile, WebsitePlan


class ComponentEngine:
    """Emit shell components from WebsitePlan variant IDs."""

    def emit_shells(
        self,
        website_plan: WebsitePlan | dict[str, Any],
        *,
        content: dict[str, Any] | None = None,
        images: dict[str, Any] | None = None,
    ) -> list[GeneratedFile]:
        plan = website_plan.to_dict() if isinstance(website_plan, WebsitePlan) else website_plan
        brand = plan.get("brand_name") or "Studio"
        tagline = plan.get("tagline") or content.get("tagline") if content else plan.get("tagline") or ""
        if content:
            tagline = content.get("tagline") or tagline
            brand = content.get("brand_name") or brand
        links = (plan.get("navbar") or {}).get("links") or ["Home", "About", "Contact"]
        hero_variant = (plan.get("hero") or {}).get("variant") or "HeroCenter"
        nav_variant = (plan.get("navbar") or {}).get("variant") or "NavbarClassic"
        foot_variant = (plan.get("footer") or {}).get("variant") or "FooterMinimal"
        hero_image = ""
        if images:
            hero_image = (images.get("hero") or images.get("covers") or [""])[0] if isinstance(
                images.get("hero") or images.get("covers"), list
            ) else (images.get("hero") or "")
            if isinstance(images.get("hero"), str):
                hero_image = images["hero"]

        files = [
            self._navbar(brand, links, nav_variant),
            self._hero(brand, tagline, hero_variant, hero_image, content),
            self._footer(brand, links, foot_variant),
            GeneratedFile(
                path="src/components/Button.tsx",
                content=(
                    "type Props = { children: React.ReactNode; href?: string; className?: string; variant?: 'primary' | 'ghost' }\n"
                    "export function Button({ children, href = '#', className = '', variant = 'primary' }: Props) {\n"
                    "  const base = 'inline-flex items-center justify-center rounded-[var(--radius,12px)] px-5 py-2.5 text-sm font-semibold transition'\n"
                    "  const styles = variant === 'ghost'\n"
                    "    ? 'border border-[var(--line,#e2e8f0)] bg-transparent text-[var(--text)]'\n"
                    "    : 'bg-[var(--color-primary,var(--brand,#0f172a))] text-white'\n"
                    "  return <a href={href} className={`${base} ${styles} ${className}`}>{children}</a>\n"
                    "}\n"
                ),
            ),
        ]
        return files

    def _navbar(self, brand: str, links: list[str], variant: str) -> GeneratedFile:
        nav_links = ",\n".join(
            f'  {{ to: "{"/" if str(l).lower()=="home" else "/" + str(l).lower().replace(" ", "-")}", label: "{l}" }}'
            for l in links
            if str(l).lower() != "article"
        )
        transparent = "NavbarTransparent" in variant
        header_cls = (
            "sticky top-0 z-50 border-b border-transparent bg-transparent"
            if transparent
            else "sticky top-0 z-50 border-b border-[var(--line,#e2e8f0)] bg-[color-mix(in_oklab,var(--bg,#fff)_92%,transparent)] backdrop-blur"
        )
        return GeneratedFile(
            path="src/components/Navbar.tsx",
            content=(
                "import { useState } from 'react'\n"
                "import { Link, NavLink } from 'react-router-dom'\n\n"
                f"const links = [\n{nav_links}\n]\n\n"
                f"/** variant: {variant} */\n"
                "export function Navbar() {\n"
                "  const [open, setOpen] = useState(false)\n"
                "  return (\n"
                f"    <header className=\"{header_cls}\">\n"
                "      <div className=\"mx-auto flex max-w-6xl items-center gap-4 px-4 py-4\">\n"
                f"        <Link to=\"/\" className=\"text-lg font-bold tracking-tight text-[var(--color-primary,var(--brand))]\">{brand}</Link>\n"
                "        <nav className=\"ml-auto hidden gap-5 text-sm font-medium md:flex\">\n"
                "          {links.map((l) => (\n"
                "            <NavLink key={l.to} to={l.to} className={({ isActive }) => isActive ? 'text-[var(--text)]' : 'text-[var(--muted,#64748b)] hover:text-[var(--text)]'}>{l.label}</NavLink>\n"
                "          ))}\n"
                "        </nav>\n"
                "        <button type=\"button\" className=\"ml-auto rounded-lg px-2 py-1 text-sm md:hidden\" onClick={() => setOpen(v => !v)}>Menu</button>\n"
                "      </div>\n"
                "      {open && (\n"
                "        <div className=\"grid gap-2 border-t border-[var(--line)] px-4 py-3 md:hidden\">\n"
                "          {links.map((l) => <NavLink key={l.to} to={l.to} onClick={() => setOpen(false)} className=\"py-2 text-sm\">{l.label}</NavLink>)}\n"
                "        </div>\n"
                "      )}\n"
                "    </header>\n"
                "  )\n"
                "}\n"
            ),
        )

    def _hero(
        self,
        brand: str,
        tagline: str,
        variant: str,
        hero_image: str,
        content: dict[str, Any] | None,
    ) -> GeneratedFile:
        safe_tag = (tagline or "").replace("`", "'").replace('"', "'")
        headline = (content or {}).get("hero_headline") or f"Welcome to {brand}"
        if "Welcome to Our Website" in headline:
            headline = f"{brand} — crafted for what you need next"
        safe_headline = str(headline).replace("`", "'").replace('"', "'")
        cta = (content or {}).get("cta_primary") or "Explore"
        safe_cta = str(cta).replace('"', "'")
        img_block = ""
        use_bg = bool(hero_image) and any(k in variant for k in ("Split", "Fashion", "Image", "Restaurant"))
        if use_bg:
            img_block = (
                f"      <div className=\"absolute inset-0 opacity-35\" style={{{{ backgroundImage: `url('{hero_image}')`, backgroundSize: 'cover', backgroundPosition: 'center' }}}} />\n"
                "      <div className=\"absolute inset-0 bg-gradient-to-r from-[var(--bg)] via-[color-mix(in_oklab,var(--bg)_80%,transparent)] to-transparent\" />\n"
            )

        align = "text-center items-center mx-auto" if "Center" in variant or "SaaS" in variant else "text-left items-start"
        return GeneratedFile(
            path="src/components/Hero.tsx",
            content=(
                "import { Button } from './Button'\n\n"
                "type HeroProps = {\n"
                "  title?: string\n"
                "  subtitle?: string\n"
                "  eyebrow?: string\n"
                "  cta?: string\n"
                "}\n\n"
                f"/** variant: {variant} */\n"
                "export function Hero({\n"
                f"  title = '{safe_headline}',\n"
                f"  subtitle = '{safe_tag}',\n"
                f"  eyebrow = '{brand}',\n"
                f"  cta = '{safe_cta}',\n"
                "}: HeroProps) {\n"
                "  return (\n"
                "    <section className=\"relative overflow-hidden\">\n"
                f"{img_block}"
                f"      <div className=\"relative mx-auto flex max-w-6xl flex-col {align} px-4 py-20 md:py-28\">\n"
                "        <p className=\"text-xs font-semibold uppercase tracking-[0.22em] text-[var(--color-accent,var(--brand))]\">{eyebrow}</p>\n"
                "        <h1 className=\"mt-4 max-w-3xl text-4xl font-bold tracking-tight text-[var(--text)] sm:text-5xl\">{title}</h1>\n"
                "        <p className=\"mt-4 max-w-2xl text-lg text-[var(--muted,#64748b)]\">{subtitle}</p>\n"
                "        <div className=\"mt-8 flex flex-wrap gap-3\">\n"
                "          <Button href=\"#/shop\">{cta}</Button>\n"
                "          <Button href=\"#/about\" variant=\"ghost\">Learn more</Button>\n"
                "        </div>\n"
                "      </div>\n"
                "    </section>\n"
                "  )\n"
                "}\n"
            ),
        )

    def _footer(self, brand: str, links: list[str], variant: str) -> GeneratedFile:
        dark = "Dark" in variant or "Premium" in variant
        bg = (
            "bg-[var(--color-primary,#0f172a)] text-white"
            if dark
            else "border-t border-[var(--line)] bg-[var(--bg)] text-[var(--text)]"
        )
        muted = "text-white/70" if dark else "text-[var(--muted)]"
        parts: list[str] = []
        for label in links[:6]:
            if str(label).lower() == "article":
                continue
            href = "/" if str(label).lower() == "home" else "/" + str(label).lower().replace(" ", "-")
            parts.append(f'<a className="hover:underline" href="#{href}">{label}</a>')
        link_items = "".join(parts)
        return GeneratedFile(
            path="src/components/Footer.tsx",
            content=(
                f"/** variant: {variant} */\n"
                "export function Footer() {\n"
                "  return (\n"
                f'    <footer className="{bg}">\n'
                '      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-12 md:flex-row md:items-center md:justify-between">\n'
                f'        <div><p className="text-lg font-semibold">{brand}</p>'
                f'<p className="mt-1 text-sm {muted}">Built with AI Website Builder</p></div>\n'
                f'        <div className="flex flex-wrap gap-4 text-sm {muted}">{link_items}</div>\n'
                "      </div>\n"
                "    </footer>\n"
                "  )\n"
                "}\n"
            ),
        )

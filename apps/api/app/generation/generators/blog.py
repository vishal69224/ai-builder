"""SEO blog / magazine generator — full articles, teal editorial theme."""

from __future__ import annotations

from app.generation.pipeline import GeneratedFile, ProjectPlan, StructuredRequirements

COVER_IMGS = [
    "https://images.unsplash.com/photo-1432888498266-38ffec6682cd?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80",
]

_GENERIC_BRANDS = {
    "blog / magazine",
    "blog",
    "magazine",
    "blog magazine",
    "marketing landing page",
    "new",
    "untitled",
    "generated site",
}


def generate_seo_blog(requirements: StructuredRequirements, plan: ProjectPlan) -> list[GeneratedFile]:
    """Build a complete SEO blog site with real article bodies and HashRouter links."""
    analysis = requirements.analysis
    brand = (getattr(analysis, "brand_name", "") or plan.project_name or "Insight Blog").strip()
    if brand.lower() in _GENERIC_BRANDS or brand.lower() == (analysis.website_type or "").lower():
        brand = "Insight Blog"
    primary = "#0F766E"
    theme_primary = (analysis.theme or {}).get("primary_color", "")
    if theme_primary and theme_primary not in {"#2563EB", "blue", "indigo"}:
        # Keep teal as the editorial default unless a strong custom color is set
        if "teal" in analysis.raw_prompt.lower() or not theme_primary:
            primary = "#0F766E"
        else:
            primary = theme_primary or "#0F766E"
    else:
        primary = "#0F766E"

    tagline = (analysis.seo or {}).get("tagline") or (
        f"Practical SEO playbooks and content strategy from {brand}."
    )

    files: list[GeneratedFile] = [
        _posts_data(),
        _button(primary),
        _seo(),
        _header(brand, plan, primary),
        _hero(brand, tagline, primary),
        _featured_posts(primary),
        _post_card(primary),
        _post_list(primary),
        _category_pills(primary),
        _newsletter(primary),
        _about(brand, primary),
        _footer(brand),
        _use_theme(),
        _card(),
        GeneratedFile(path="src/components/Navbar.tsx", content="export { BlogHeader as Navbar } from './BlogHeader'\n"),
        GeneratedFile(path="src/components/Hero.tsx", content="export { BlogHero as Hero } from './BlogHero'\n"),
        GeneratedFile(path="src/components/Footer.tsx", content="export { BlogFooter as Footer } from './BlogFooter'\n"),
    ]

    for route in plan.routes:
        page = route["page"].lower()
        comp = route["component"]
        if route["path"] == "/":
            body = _home(brand, primary)
        elif "article" in page and "articles" not in page:
            body = _article_page(comp, brand, primary)
        elif "articles" in page or "blog" in page or "post" in page:
            body = _articles_page(comp, brand, primary)
        elif "categor" in page:
            body = _categories_page(comp, brand, primary)
        elif "about" in page:
            body = _about_page(comp, brand, primary)
        elif "contact" in page:
            body = _contact_page(comp, brand, primary)
        else:
            body = (
                f"export default function {comp}() {{\n"
                f"  return (\n"
                f"    <section className=\"mx-auto max-w-6xl px-4 py-16\">\n"
                f"      <h1 className=\"text-3xl font-bold tracking-tight\">{route['page']}</h1>\n"
                f"      <p className=\"mt-3 text-stone-600\">Explore {route['page']} on {brand}.</p>\n"
                f"    </section>\n"
                f"  )\n"
                f"}}\n"
            )
        files.append(GeneratedFile(path=f"src/pages/{comp}.tsx", content=body))

    # Ensure ArticlePage exists even if planner omitted the route
    if not any(f.path == "src/pages/ArticlePage.tsx" for f in files):
        files.append(
            GeneratedFile(
                path="src/pages/ArticlePage.tsx",
                content=_article_page("ArticlePage", brand, primary),
            )
        )

    return list({f.path: f for f in files}.values())


def _posts_data() -> GeneratedFile:
    """Six full SEO articles with multi-paragraph bodies — not placeholders."""
    content = r'''export type Post = {
  slug: string
  title: string
  excerpt: string
  category: string
  author: string
  date: string
  readMinutes: number
  cover: string
  body: string[]
}

export const categories = [
  'On-Page SEO',
  'Keyword Research',
  'Technical SEO',
  'Content Strategy',
  'Link Building',
  'Performance',
] as const

export const posts: Post[] = [
  {
    slug: 'on-page-seo-checklist-2026',
    title: 'The Practical On-Page SEO Checklist That Still Moves Rankings in 2026',
    excerpt:
      'Title tags, intent-matched headings, internal links, and helpful media — a field-tested checklist you can apply to every publishing workflow.',
    category: 'On-Page SEO',
    author: 'Aisha Rahman',
    date: '2026-03-12',
    readMinutes: 9,
    cover: 'COVER_0',
    body: [
      'On-page SEO is no longer a game of stuffing keywords into meta tags. Search engines reward pages that answer a clear search intent with scannable structure, trustworthy sourcing, and a reading experience that keeps people engaged. Start every draft by writing a one-sentence promise: who this page helps and what outcome they should leave with. That sentence becomes your H1, your meta description backbone, and the filter for every paragraph you keep.',
      'Craft a unique title tag under roughly 60 characters that leads with the primary phrase users actually type, then add a benefit or year only when it improves clarity. Pair it with a meta description that earns the click without bait — mention the problem, the method, and a concrete takeaway. Inside the article, use H2s that mirror related queries and H3s for steps, tools, or examples. Search engines parse that outline; humans skim it.',
      'Place your primary keyword naturally in the first 100 words, then support it with semantically related language instead of repetition. Every major section should earn at least one contextual internal link to a deeper guide or a category hub. External citations to primary research or official documentation raise trust signals and help readers verify claims.',
      'Images deserve the same discipline as copy. Compress covers, write descriptive alt text that explains the visual in context, and caption charts so the insight stands alone. Close each page with a short FAQ that mirrors People Also Ask phrasing, then a soft CTA toward a related article or newsletter. Revisit top pages quarterly: refresh stats, tighten intros, and prune outdated advice before you publish net-new content.',
    ],
  },
  {
    slug: 'keyword-research-without-vanity-metrics',
    title: 'Keyword Research Without Vanity Metrics: Map Intent Before You Chase Volume',
    excerpt:
      'Stop ranking for phrases nobody converts on. Learn a research workflow that clusters topics by intent, difficulty, and business value.',
    category: 'Keyword Research',
    author: 'Marcus Chen',
    date: '2026-02-28',
    readMinutes: 11,
    cover: 'COVER_1',
    body: [
      'Keyword volume is a popularity contest, not a strategy. The research process that wins starts with customer language — support tickets, sales calls, Reddit threads, and search suggestions — then validates those phrases with tools. Capture seed terms that describe jobs-to-be-done, not brand slogans. Expand each seed into questions, comparisons, and problem statements so you understand the journey around the keyword, not just the head term.',
      'Classify every candidate by intent: informational, commercial investigation, transactional, or navigational. A how-to query deserves a guide; a “best X for Y” query deserves a comparison with clear criteria; a “buy” or “pricing” query deserves a product or service page. Mixing intents on one URL usually dilutes relevance and confuses both users and algorithms.',
      'Score opportunities with a simple matrix: relevance to revenue, realistic difficulty for your domain authority, and content gap versus competitors. Prefer mid-volume phrases where you can publish something 2x clearer than the current top results. Build clusters — a pillar page plus supporting articles that interlink — so authority concentrates around topics instead of scattering across orphan posts.',
      'Document the primary keyword, secondary phrases, and the searcher’s expected format before drafting. After publish, track impressions and queries in Search Console, then expand sections that already attract related searches. Keyword research is not a one-time spreadsheet; it is a feedback loop between what people ask and how you answer.',
    ],
  },
  {
    slug: 'technical-seo-foundations-for-publishers',
    title: 'Technical SEO Foundations for Publishers: Crawl, Index, and Render Without Drama',
    excerpt:
      'Sitemaps, canonicals, robots rules, and JavaScript rendering — the infrastructure that lets great content actually get discovered.',
    category: 'Technical SEO',
    author: 'Priya Nair',
    date: '2026-01-18',
    readMinutes: 10,
    cover: 'COVER_2',
    body: [
      'Technical SEO is the plumbing of discoverability. If crawlers cannot reach, understand, or efficiently render your pages, editorial excellence never compounds. Begin with a clean information architecture: predictable URLs, shallow depth to important content, and XML sitemaps that list only indexable URLs with sensible lastmod timestamps. Submit the sitemap in Search Console and monitor coverage for soft 404s, redirect chains, and excluded pages.',
      'Canonical tags should point to the preferred version of each article when parameters, trailing slashes, or syndication create duplicates. Use robots.txt to block staging environments and infinite filter combinations — never to hide thin content you should delete or consolidate instead. Status codes matter: 301 permanent moves preserve equity; temporary 302s should be rare for editorial URLs.',
      'For JavaScript-heavy sites, confirm critical content appears in the initial HTML or is reliably rendered for bots. Lazy-load below-the-fold media, but keep headings and primary copy available without waiting on third-party scripts. Structured data (Article, BreadcrumbList, FAQPage when accurate) helps rich results; invalid markup can be ignored or worse — keep schemas truthful to visible content.',
      'Schedule monthly crawls with a site auditor. Fix broken internal links, orphan pages, and conflicting noindex signals before they accumulate. Technical SEO is not glamorous, but it is the reason your best articles compound traffic instead of sitting invisible in a CMS.',
    ],
  },
  {
    slug: 'topical-authority-content-clusters',
    title: 'Build Topical Authority with Content Clusters That Actually Interlink',
    excerpt:
      'Pillars, clusters, and hub pages — how to cover a subject so thoroughly that search engines associate your brand with the topic.',
    category: 'Content Strategy',
    author: 'Elena Volkov',
    date: '2025-12-05',
    readMinutes: 12,
    cover: 'COVER_3',
    body: [
      'Topical authority is earned when your site becomes the most useful destination for a subject, not when you publish the longest single article. Map the topic into a pillar that defines the big idea, then surround it with cluster pieces that answer specific sub-questions. Each cluster article should link up to the pillar and across to sibling posts where the reader’s next question naturally leads.',
      'Write briefs that force differentiation: what angle will make this page better than the current SERP leaders? Include original examples, screenshots from your own workflows, checklists readers can copy, and clear definitions for jargon. Thin rewrites of competitor headlines rarely move rankings; depth plus clarity does.',
      'Update the pillar whenever clusters ship so the hub stays current and surfaces the newest deep dives. Use consistent taxonomy — categories and tags that reflect how users think, not how your CMS was configured years ago. A category archive with a short editorial intro and curated featured posts can rank for head terms while individual articles capture long-tail demand.',
      'Measure authority through share of impressions across the topic cluster, not vanity traffic on a single post. When a cluster underperforms, improve the weakest page first: better intro, stronger visuals, fresher data. Authority compounds through maintenance as much as through net-new publishing.',
    ],
  },
  {
    slug: 'ethical-link-building-for-content-sites',
    title: 'Ethical Link Building for Content Sites: Earn Mentions Without Shortcuts',
    excerpt:
      'Digital PR, original research, and resource linkability — sustainable ways to grow referring domains while protecting brand trust.',
    category: 'Link Building',
    author: 'Jordan Blake',
    date: '2025-11-20',
    readMinutes: 8,
    cover: 'COVER_4',
    body: [
      'Links remain a ranking factor because they are hard-earned votes of confidence. The durable approach for publishers is to create assets people want to cite: original surveys, unique data visualizations, definitive templates, and expert roundups with real insight. Promote those assets to journalists, newsletter authors, and community curators who already cover your niche.',
      'Digital PR works when your pitch leads with a newsworthy finding, not a request for a backlink. Package methodology, quotable stats, and ready-to-use charts. Unlinked brand mentions are opportunities — politely suggest adding a citation when your research was used. Guest contributions should teach something specific; thin “listicles for links” damage reputation faster than they help rankings.',
      'Avoid schemes that sell links, automate outreach spam, or cloak paid placements. Search systems are increasingly skilled at detecting patterns that do not look like editorial endorsements. Invest instead in relationships: podcast appearances, conference talks, and collaborative research with complementary brands.',
      'Track referring domains, anchor diversity, and the relevance of linking pages. A handful of contextual links from respected sites in your field outperforms hundreds of irrelevant directory listings. Link building done ethically is simply great content distribution with patience.',
    ],
  },
  {
    slug: 'core-web-vitals-for-content-teams',
    title: 'Core Web Vitals for Content Teams: Speed Without Sacrificing Design',
    excerpt:
      'LCP, INP, and CLS explained for editors and marketers — practical fixes that keep pages fast while preserving brand polish.',
    category: 'Performance',
    author: 'Sofia Martins',
    date: '2025-10-08',
    readMinutes: 9,
    cover: 'COVER_5',
    body: [
      'Page experience is part of how users (and search systems) judge quality. Largest Contentful Paint (LCP) asks whether the main hero or headline area appears quickly. Interaction to Next Paint (INP) checks how snappy the page feels when someone taps a menu or filter. Cumulative Layout Shift (CLS) penalizes janky layouts that jump as fonts and images load. Content teams influence all three through media choices and template discipline.',
      'Prefer modern image formats, explicit width and height (or aspect-ratio CSS), and responsive srcsets so mobile devices do not download desktop-sized covers. Defer non-critical scripts — chat widgets, heavy analytics, and social embeds — until after the primary content paints. Self-host critical fonts with font-display: swap and limit family weights to what the design actually uses.',
      'Hero carousels and autoplay videos often hurt LCP and INP; a single strong static cover with a clear headline usually converts better and measures cleaner. Reserve space for ads and embeds so late-loading creatives do not shove copy downward. Test templates on mid-tier mobile hardware, not only on a developer laptop.',
      'Make performance a publishing gate: if a new template regresses LCP on a staging URL, fix it before rollout. Pair lab tools (Lighthouse) with field data (CrUX / Search Console) so you optimize what real users feel. Fast pages keep readers long enough to finish — and finishing is the goal of every SEO article you ship.',
    ],
  },
]

export function getPostBySlug(slug: string | null | undefined): Post | undefined {
  if (!slug) return undefined
  return posts.find((p) => p.slug === slug)
}

export function getPostsByCategory(category: string): Post[] {
  return posts.filter((p) => p.category === category)
}

export function getFeaturedPosts(limit = 3): Post[] {
  return posts.slice(0, limit)
}
'''
    for i, url in enumerate(COVER_IMGS):
        content = content.replace(f"COVER_{i}", url)
    return GeneratedFile(path="src/data/posts.ts", content=content)


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


def _card() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Card.tsx",
        content=(
            "type CardProps = { title: string; description: string }\n"
            "export function Card({ title, description }: CardProps) {\n"
            "  return (\n"
            "    <article className=\"rounded-2xl border border-stone-200 bg-white p-5 shadow-sm\">\n"
            "      <h3 className=\"font-semibold text-stone-900\">{title}</h3>\n"
            "      <p className=\"mt-2 text-sm text-stone-600\">{description}</p>\n"
            "    </article>\n"
            "  )\n"
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
            "  const styles = variant === 'primary' ? 'text-white' : 'border border-stone-300 bg-white text-stone-900'\n"
            f"  const style = variant === 'primary' ? {{ backgroundColor: '{primary}' }} : undefined\n"
            "  return <a href={href} className={base + styles + ' ' + className} style={style}>{children}</a>\n"
            "}\n"
        ),
    )


def _seo() -> GeneratedFile:
    return GeneratedFile(
        path="src/components/Seo.tsx",
        content=(
            "import { useEffect } from 'react'\n\n"
            "type SeoProps = { title: string; description?: string }\n\n"
            "export function Seo({ title, description }: SeoProps) {\n"
            "  useEffect(() => {\n"
            "    document.title = title\n"
            "    if (description) {\n"
            "      let meta = document.querySelector('meta[name=\"description\"]') as HTMLMetaElement | null\n"
            "      if (!meta) {\n"
            "        meta = document.createElement('meta')\n"
            "        meta.name = 'description'\n"
            "        document.head.appendChild(meta)\n"
            "      }\n"
            "      meta.content = description\n"
            "    }\n"
            "  }, [title, description])\n"
            "  return null\n"
            "}\n"
        ),
    )


def _header(brand: str, plan: ProjectPlan, primary: str) -> GeneratedFile:
    nav_routes = [r for r in plan.routes if r["page"].lower() != "article"]
    links = ",\n".join(f'  {{ to: "{r["path"]}", label: "{r["page"]}" }}' for r in nav_routes)
    return GeneratedFile(
        path="src/components/BlogHeader.tsx",
        content=(
            "import { useState } from 'react'\n"
            "import { Link, NavLink } from 'react-router-dom'\n"
            "import { Menu, Search, X } from 'lucide-react'\n\n"
            f"const links = [\n{links}\n]\n\n"
            "export function BlogHeader() {\n"
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
            "          <a href=\"#/articles\" className=\"rounded-full p-2 hover:bg-stone-100\" aria-label=\"Search articles\"><Search className=\"h-5 w-5\" /></a>\n"
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


def _hero(brand: str, tagline: str, primary: str) -> GeneratedFile:
    safe_tag = tagline.replace("`", "'").replace('"', "'").replace("\\", "")
    img = COVER_IMGS[0]
    return GeneratedFile(
        path="src/components/BlogHero.tsx",
        content=(
            "import { Button } from './Button'\n\n"
            "export function BlogHero() {\n"
            "  return (\n"
            "    <section className=\"relative overflow-hidden bg-stone-950 text-white\">\n"
            f"      <div className=\"absolute inset-0 opacity-40\" style={{{{ backgroundImage: `url('{img}')`, backgroundSize: 'cover', backgroundPosition: 'center' }}}} />\n"
            "      <div className=\"absolute inset-0 bg-gradient-to-r from-stone-950 via-stone-950/90 to-stone-950/40\" />\n"
            "      <div className=\"relative mx-auto max-w-6xl px-4 py-20 md:py-28\">\n"
            f"        <p className=\"text-sm font-semibold uppercase tracking-[0.25em]\" style={{{{ color: '{primary}' }}}}>{brand}</p>\n"
            "        <h1 className=\"mt-4 max-w-3xl text-4xl font-black tracking-tight sm:text-5xl md:text-6xl\">SEO playbooks that compound organic growth</h1>\n"
            f"        <p className=\"mt-5 max-w-2xl text-lg text-stone-300\">{safe_tag}</p>\n"
            "        <div className=\"mt-8 flex flex-wrap gap-3\">\n"
            "          <Button href=\"#/articles\">Read articles</Button>\n"
            "          <Button href=\"#/categories\" variant=\"ghost\" className=\"border-white/30 bg-white/10 text-white\">Browse topics</Button>\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _featured_posts(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/FeaturedPosts.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n"
            "import { getFeaturedPosts } from '../data/posts'\n"
            "import { PostCard } from './PostCard'\n\n"
            "export function FeaturedPosts() {\n"
            "  const featured = getFeaturedPosts(3)\n"
            "  const [lead, ...rest] = featured\n"
            "  if (!lead) return null\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14\">\n"
            "      <div className=\"flex items-end justify-between gap-4\">\n"
            "        <div>\n"
            "          <h2 className=\"text-3xl font-bold tracking-tight\">Featured insights</h2>\n"
            "          <p className=\"mt-2 text-stone-600\">Editor-picked guides for marketers and publishers.</p>\n"
            "        </div>\n"
            "        <Link to=\"/articles\" className=\"hidden text-sm font-semibold sm:inline\" "
            f"style={{{{ color: '{primary}' }}}}>View all</Link>\n"
            "      </div>\n"
            "      <div className=\"mt-8 grid gap-6 lg:grid-cols-5\">\n"
            "        <Link to={`/article?slug=${lead.slug}`} className=\"group overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-sm lg:col-span-3\">\n"
            "          <img src={lead.cover} alt={lead.title} className=\"h-64 w-full object-cover transition group-hover:scale-[1.02] md:h-80\" loading=\"lazy\" />\n"
            "          <div className=\"p-6\">\n"
            f"            <p className=\"text-xs font-semibold uppercase tracking-wide\" style={{{{ color: '{primary}' }}}}>{{lead.category}}</p>\n"
            "            <h3 className=\"mt-2 text-2xl font-bold tracking-tight group-hover:underline\">{lead.title}</h3>\n"
            "            <p className=\"mt-3 text-stone-600\">{lead.excerpt}</p>\n"
            "            <p className=\"mt-4 text-sm text-stone-500\">{lead.author} · {lead.readMinutes} min read</p>\n"
            "          </div>\n"
            "        </Link>\n"
            "        <div className=\"grid gap-4 lg:col-span-2\">\n"
            "          {rest.map((p) => <PostCard key={p.slug} post={p} compact />)}\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _post_card(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/PostCard.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n"
            "import type { Post } from '../data/posts'\n\n"
            "type Props = { post: Post; compact?: boolean }\n\n"
            "export function PostCard({ post, compact = false }: Props) {\n"
            "  return (\n"
            "    <Link to={`/article?slug=${post.slug}`} className={`group flex overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md ${compact ? 'flex-col' : 'flex-col sm:flex-row'}`}>\n"
            f"      <img src={{post.cover}} alt={{post.title}} className={{compact ? 'h-40 w-full object-cover' : 'h-44 w-full object-cover sm:h-auto sm:w-48'}} loading=\"lazy\" />\n"
            "      <div className=\"flex flex-1 flex-col p-4\">\n"
            f"        <p className=\"text-xs font-semibold uppercase tracking-wide\" style={{{{ color: '{primary}' }}}}>{{post.category}}</p>\n"
            "        <h3 className={`mt-1 font-bold tracking-tight group-hover:underline ${compact ? 'text-base' : 'text-lg'}`}>{post.title}</h3>\n"
            "        {!compact && <p className=\"mt-2 line-clamp-2 text-sm text-stone-600\">{post.excerpt}</p>}\n"
            "        <p className=\"mt-auto pt-3 text-xs text-stone-500\">{post.date} · {post.readMinutes} min</p>\n"
            "      </div>\n"
            "    </Link>\n"
            "  )\n"
            "}\n"
        ),
    )


def _post_list(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/PostList.tsx",
        content=(
            "import { posts } from '../data/posts'\n"
            "import { PostCard } from './PostCard'\n\n"
            "type Props = { category?: string; limit?: number; title?: string }\n\n"
            "export function PostList({ category, limit, title = 'Latest articles' }: Props) {\n"
            "  let items = category ? posts.filter((p) => p.category === category) : posts\n"
            "  if (typeof limit === 'number') items = items.slice(0, limit)\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14\">\n"
            "      <h2 className=\"text-3xl font-bold tracking-tight\">{title}</h2>\n"
            "      <div className=\"mt-8 grid gap-5\">\n"
            "        {items.map((p) => <PostCard key={p.slug} post={p} />)}\n"
            "      </div>\n"
            f"      {{items.length === 0 && <p className=\"mt-6 text-stone-600\">No articles in this category yet.</p>}}\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _category_pills(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/CategoryPills.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n"
            "import { categories } from '../data/posts'\n\n"
            "export function CategoryPills({ active }: { active?: string }) {\n"
            "  return (\n"
            "    <div className=\"flex flex-wrap gap-2\">\n"
            "      <Link to=\"/categories\" className={`rounded-full px-4 py-1.5 text-sm font-medium ${!active ? 'text-white' : 'bg-stone-100 text-stone-700 hover:bg-stone-200'}`}"
            f" style={{!active ? {{ backgroundColor: '{primary}' }} : undefined}}>All topics</Link>\n"
            "      {categories.map((c) => (\n"
            "        <Link key={c} to={`/categories`} className={`rounded-full px-4 py-1.5 text-sm font-medium ${active === c ? 'text-white' : 'bg-stone-100 text-stone-700 hover:bg-stone-200'}`}"
            f" style={{active === c ? {{ backgroundColor: '{primary}' }} : undefined}}>{{c}}</Link>\n"
            "      ))}\n"
            "    </div>\n"
            "  )\n"
            "}\n"
        ),
    )


def _newsletter(primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/BlogNewsletter.tsx",
        content=(
            "export function BlogNewsletter() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-10\">\n"
            f"      <div className=\"rounded-3xl px-8 py-10 text-white\" style={{{{ backgroundColor: '{primary}' }}}}>\n"
            "        <h2 className=\"text-3xl font-bold\">Get the weekly SEO brief</h2>\n"
            "        <p className=\"mt-2 max-w-xl text-teal-50\">One actionable playbook every week — on-page, technical, and content strategy. No fluff.</p>\n"
            "        <form className=\"mt-6 flex max-w-lg flex-col gap-3 sm:flex-row\" onSubmit={(e) => e.preventDefault()}>\n"
            "          <input type=\"email\" required placeholder=\"you@company.com\" className=\"flex-1 rounded-full px-4 py-3 text-sm text-stone-900\" />\n"
            "          <button type=\"submit\" className=\"rounded-full bg-stone-950 px-5 py-3 text-sm font-semibold text-white hover:bg-stone-800\">Subscribe</button>\n"
            "        </form>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _about(brand: str, primary: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/BlogAbout.tsx",
        content=(
            "export function BlogAbout() {\n"
            "  return (\n"
            "    <section className=\"mx-auto max-w-6xl px-4 py-14\">\n"
            "      <div className=\"grid gap-8 md:grid-cols-2 md:items-center\">\n"
            "        <div>\n"
            f"          <p className=\"text-sm font-semibold uppercase tracking-wide\" style={{{{ color: '{primary}' }}}}>About {brand}</p>\n"
            "          <h2 className=\"mt-2 text-3xl font-bold tracking-tight\">Editorial SEO for teams who ship</h2>\n"
            f"          <p className=\"mt-4 text-stone-600\">{brand} publishes practical guides on search, content systems, and site performance. Our writers combine agency experience with in-house publishing workflows so every article is something you can apply the same week you read it.</p>\n"
            "          <p className=\"mt-3 text-stone-600\">We cover on-page craft, keyword strategy, technical foundations, topical authority, ethical links, and Core Web Vitals — always with examples, never empty frameworks.</p>\n"
            "        </div>\n"
            "        <div className=\"rounded-3xl border border-stone-200 bg-stone-50 p-8\">\n"
            "          <ul className=\"space-y-3 text-sm text-stone-700\">\n"
            "            <li>· Field-tested checklists editors actually use</li>\n"
            "            <li>· Intent-first keyword and cluster planning</li>\n"
            "            <li>· Performance guidance that respects design</li>\n"
            "            <li>· Ethical growth — no link schemes</li>\n"
            "          </ul>\n"
            "        </div>\n"
            "      </div>\n"
            "    </section>\n"
            "  )\n"
            "}\n"
        ),
    )


def _footer(brand: str) -> GeneratedFile:
    return GeneratedFile(
        path="src/components/BlogFooter.tsx",
        content=(
            "import { Link } from 'react-router-dom'\n\n"
            "export function BlogFooter() {\n"
            "  return (\n"
            "    <footer className=\"border-t border-stone-800 bg-stone-950 text-stone-400\">\n"
            "      <div className=\"mx-auto grid max-w-6xl gap-8 px-4 py-12 md:grid-cols-3\">\n"
            "        <div>\n"
            f"          <p className=\"text-lg font-bold text-white\">{brand}</p>\n"
            "          <p className=\"mt-2 text-sm\">SEO strategy, content systems, and performance — written for marketers and publishers.</p>\n"
            "        </div>\n"
            "        <div className=\"text-sm\">\n"
            "          <p className=\"font-semibold text-white\">Explore</p>\n"
            "          <div className=\"mt-3 grid gap-2\">\n"
            "            <Link to=\"/articles\" className=\"hover:text-white\">Articles</Link>\n"
            "            <Link to=\"/categories\" className=\"hover:text-white\">Categories</Link>\n"
            "            <Link to=\"/about\" className=\"hover:text-white\">About</Link>\n"
            "            <Link to=\"/contact\" className=\"hover:text-white\">Contact</Link>\n"
            "          </div>\n"
            "        </div>\n"
            "        <div className=\"text-sm\">\n"
            "          <p className=\"font-semibold text-white\">Hash routes</p>\n"
            "          <p className=\"mt-3\">Articles live at <code className=\"text-teal-300\">#/articles</code>. Open a post with <code className=\"text-teal-300\">#/article?slug=...</code>.</p>\n"
            "        </div>\n"
            "      </div>\n"
            "      <div className=\"border-t border-stone-800\">\n"
            "        <div className=\"mx-auto flex max-w-6xl flex-col gap-2 px-4 py-6 text-sm sm:flex-row sm:justify-between\">\n"
            f"          <p>© {{new Date().getFullYear()}} {brand}</p>\n"
            "          <p>Built for organic growth teams</p>\n"
            "        </div>\n"
            "      </div>\n"
            "    </footer>\n"
            "  )\n"
            "}\n"
        ),
    )


def _home(brand: str, primary: str) -> str:
    return (
        "import { Seo } from '../components/Seo'\n"
        "import { BlogHero } from '../components/BlogHero'\n"
        "import { FeaturedPosts } from '../components/FeaturedPosts'\n"
        "import { CategoryPills } from '../components/CategoryPills'\n"
        "import { PostList } from '../components/PostList'\n"
        "import { BlogAbout } from '../components/BlogAbout'\n"
        "import { BlogNewsletter } from '../components/BlogNewsletter'\n\n"
        "export default function HomePage() {\n"
        "  return (\n"
        "    <div className=\"bg-stone-50 text-stone-900\">\n"
        f"      <Seo title=\"{brand} — SEO Blog\" description=\"Practical SEO playbooks on on-page, keywords, technical SEO, content clusters, links, and performance.\" />\n"
        "      <BlogHero />\n"
        "      <div className=\"mx-auto max-w-6xl px-4 pt-10\">\n"
        "        <CategoryPills />\n"
        "      </div>\n"
        "      <FeaturedPosts />\n"
        "      <PostList limit={4} title=\"Fresh from the desk\" />\n"
        "      <BlogAbout />\n"
        "      <BlogNewsletter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _articles_page(comp: str, brand: str, primary: str) -> str:
    _ = primary
    return (
        "import { Seo } from '../components/Seo'\n"
        "import { CategoryPills } from '../components/CategoryPills'\n"
        "import { PostList } from '../components/PostList'\n"
        "import { BlogNewsletter } from '../components/BlogNewsletter'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-stone-50 text-stone-900\">\n"
        f"      <Seo title=\"Articles — {brand}\" description=\"Browse all SEO guides and content strategy articles.\" />\n"
        "      <section className=\"mx-auto max-w-6xl px-4 py-12\">\n"
        "        <h1 className=\"text-4xl font-bold tracking-tight\">All articles</h1>\n"
        "        <p className=\"mt-3 max-w-2xl text-stone-600\">Deep-dive SEO guidance with full article bodies — open any card to read via <code className=\"text-sm\">#/article?slug=...</code>.</p>\n"
        "        <div className=\"mt-6\"><CategoryPills /></div>\n"
        "      </section>\n"
        "      <PostList title=\"Library\" />\n"
        "      <BlogNewsletter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _categories_page(comp: str, brand: str, primary: str) -> str:
    return (
        "import { useMemo, useState } from 'react'\n"
        "import { Seo } from '../components/Seo'\n"
        "import { categories, posts } from '../data/posts'\n"
        "import { PostCard } from '../components/PostCard'\n\n"
        f"export default function {comp}() {{\n"
        "  const [active, setActive] = useState<string | undefined>(undefined)\n"
        "  const items = useMemo(() => active ? posts.filter((p) => p.category === active) : posts, [active])\n"
        "  return (\n"
        "    <div className=\"bg-stone-50 text-stone-900\">\n"
        f"      <Seo title=\"Categories — {brand}\" description=\"Explore SEO topics by category.\" />\n"
        "      <section className=\"mx-auto max-w-6xl px-4 py-12\">\n"
        "        <h1 className=\"text-4xl font-bold tracking-tight\">Categories</h1>\n"
        "        <p className=\"mt-3 text-stone-600\">Filter the library by topic focus.</p>\n"
        "        <div className=\"mt-6 flex flex-wrap gap-2\">\n"
        "          <button type=\"button\" onClick={() => setActive(undefined)} className={`rounded-full px-4 py-1.5 text-sm font-medium ${!active ? 'text-white' : 'bg-stone-100'}`}"
        f" style={{!active ? {{ backgroundColor: '{primary}' }} : undefined}}>All</button>\n"
        "          {categories.map((c) => (\n"
        "            <button key={c} type=\"button\" onClick={() => setActive(c)} className={`rounded-full px-4 py-1.5 text-sm font-medium ${active === c ? 'text-white' : 'bg-stone-100'}`}"
        f" style={{active === c ? {{ backgroundColor: '{primary}' }} : undefined}}>{{c}}</button>\n"
        "          ))}\n"
        "        </div>\n"
        "        <div className=\"mt-8 grid gap-5\">\n"
        "          {items.map((p) => <PostCard key={p.slug} post={p} />)}\n"
        "        </div>\n"
        "      </section>\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _about_page(comp: str, brand: str, primary: str) -> str:
    return (
        "import { Seo } from '../components/Seo'\n"
        "import { BlogAbout } from '../components/BlogAbout'\n"
        "import { BlogNewsletter } from '../components/BlogNewsletter'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-stone-50\">\n"
        f"      <Seo title=\"About — {brand}\" description=\"Learn about our editorial SEO mission.\" />\n"
        "      <BlogAbout />\n"
        "      <BlogNewsletter />\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _contact_page(comp: str, brand: str, primary: str) -> str:
    return (
        "import { Seo } from '../components/Seo'\n\n"
        f"export default function {comp}() {{\n"
        "  return (\n"
        "    <div className=\"bg-stone-50 text-stone-900\">\n"
        f"      <Seo title=\"Contact — {brand}\" description=\"Get in touch with the editorial team.\" />\n"
        "      <section className=\"mx-auto max-w-xl px-4 py-14\">\n"
        "        <h1 className=\"text-3xl font-bold tracking-tight\">Contact</h1>\n"
        f"        <p className=\"mt-3 text-stone-600\">Pitch a guest brief, ask about partnerships, or tell us what SEO topic you want covered next at {brand}.</p>\n"
        "        <form className=\"mt-6 grid gap-3 rounded-2xl border border-stone-200 bg-white p-6\" onSubmit={(e) => e.preventDefault()}>\n"
        "          <input className=\"rounded-xl border border-stone-300 px-3 py-2 text-sm\" placeholder=\"Name\" required />\n"
        "          <input type=\"email\" className=\"rounded-xl border border-stone-300 px-3 py-2 text-sm\" placeholder=\"Email\" required />\n"
        "          <textarea className=\"min-h-28 rounded-xl border border-stone-300 px-3 py-2 text-sm\" placeholder=\"Message\" required />\n"
        f"          <button type=\"submit\" className=\"rounded-full px-4 py-2.5 text-sm font-semibold text-white\" style={{{{ backgroundColor: '{primary}' }}}}>Send message</button>\n"
        "        </form>\n"
        f"        <p className=\"mt-6 text-sm text-stone-500\">hello@{brand.lower().replace(' ', '')}.com · Editorial desk</p>\n"
        "      </section>\n"
        "    </div>\n"
        "  )\n"
        "}\n"
    )


def _article_page(comp: str, brand: str, primary: str) -> str:
    """Reads slug from hash query: #/article?slug=... via useSearchParams."""
    return (
        "import { Link, useSearchParams } from 'react-router-dom'\n"
        "import { Seo } from '../components/Seo'\n"
        "import { getPostBySlug, posts } from '../data/posts'\n"
        "import { PostCard } from '../components/PostCard'\n"
        "import { BlogNewsletter } from '../components/BlogNewsletter'\n\n"
        f"export default function {comp}() {{\n"
        "  const [params] = useSearchParams()\n"
        "  const slug = params.get('slug')\n"
        "  const post = getPostBySlug(slug)\n"
        "  if (!post) {\n"
        "    return (\n"
        "      <section className=\"mx-auto max-w-3xl px-4 py-16\">\n"
        f"        <Seo title=\"Article not found — {brand}\" />\n"
        "        <h1 className=\"text-3xl font-bold\">Article not found</h1>\n"
        "        <p className=\"mt-3 text-stone-600\">Missing or invalid slug. Try the library at <Link to=\"/articles\" className=\"underline\">#/articles</Link>.</p>\n"
        "        <div className=\"mt-8 grid gap-4\">\n"
        "          {posts.slice(0, 3).map((p) => <PostCard key={p.slug} post={p} />)}\n"
        "        </div>\n"
        "      </section>\n"
        "    )\n"
        "  }\n"
        "  return (\n"
        "    <article className=\"bg-stone-50 text-stone-900\">\n"
        f"      <Seo title={{`${{post.title}} — {brand}`}} description={{post.excerpt}} />\n"
        "      <div className=\"mx-auto max-w-3xl px-4 py-12\">\n"
        "        <p className=\"text-sm font-semibold uppercase tracking-wide\" "
        f"style={{{{ color: '{primary}' }}}}>{{post.category}}</p>\n"
        "        <h1 className=\"mt-3 text-4xl font-black tracking-tight\">{post.title}</h1>\n"
        "        <p className=\"mt-4 text-lg text-stone-600\">{post.excerpt}</p>\n"
        "        <p className=\"mt-4 text-sm text-stone-500\">{post.author} · {post.date} · {post.readMinutes} min read</p>\n"
        "        <img src={post.cover} alt={post.title} className=\"mt-8 h-64 w-full rounded-3xl object-cover md:h-80\" />\n"
        "        <div className=\"prose prose-stone mt-10 max-w-none\">\n"
        "          {post.body.map((para, i) => (\n"
        "            <p key={i} className=\"mb-5 text-base leading-relaxed text-stone-700\">{para}</p>\n"
        "          ))}\n"
        "        </div>\n"
        "        <div className=\"mt-10 flex flex-wrap gap-3\">\n"
        "          <Link to=\"/articles\" className=\"text-sm font-semibold underline\">← All articles</Link>\n"
        f"          <Link to=\"/categories\" className=\"text-sm font-semibold\" style={{{{ color: '{primary}' }}}}>More in {{post.category}}</Link>\n"
        "        </div>\n"
        "      </div>\n"
        "      <BlogNewsletter />\n"
        "    </article>\n"
        "  )\n"
        "}\n"
    )

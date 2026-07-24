import { useEffect, useState } from 'react'

const slides = [
  {
    label: 'E‑commerce',
    title: 'LUNETTE',
    blurb: 'Hero · Product grid · Checkout-ready layout',
    gradient: 'linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%)',
    ink: '#0f172a',
    muted: '#64748b',
    accent: '#0d9488',
  },
  {
    label: 'Portfolio',
    title: 'Alex Rivera',
    blurb: 'Flutter · Python · Case studies',
    gradient: 'linear-gradient(145deg, #0b1220 0%, #134e4a 100%)',
    ink: '#f8fafc',
    muted: '#94a3b8',
    accent: '#2dd4bf',
  },
  {
    label: 'Real estate',
    title: 'Dream Homes',
    blurb: 'Listings · Search · Contact',
    gradient: 'linear-gradient(145deg, #1c1917 0%, #44403c 100%)',
    ink: '#fafaf9',
    muted: '#a8a29e',
    accent: '#fb923c',
  },
  {
    label: 'Café',
    title: 'Harbor Roast',
    blurb: 'Menu · Story · Hours',
    gradient: 'linear-gradient(145deg, #fff7ed 0%, #ffedd5 100%)',
    ink: '#431407',
    muted: '#9a3412',
    accent: '#ea580c',
  },
]

export function SiteShowcase() {
  const [i, setI] = useState(0)

  useEffect(() => {
    const t = window.setInterval(() => setI((v) => (v + 1) % slides.length), 3400)
    return () => window.clearInterval(t)
  }, [])

  const slide = slides[i]

  return (
    <div className="scene-3d relative mx-auto w-full max-w-lg">
      <div
        className="float-y absolute -left-6 top-10 hidden h-28 w-40 rounded-2xl border border-[var(--line)] bg-[var(--bg-elevated)] p-3 shadow-[var(--shadow-card)] sm:block"
        style={{ transform: 'rotate(-8deg)' }}
      >
        <div className="h-2 w-16 rounded bg-[var(--bg-muted)]" />
        <div className="mt-3 space-y-2">
          <div className="h-2 w-full rounded bg-[var(--bg-muted)]" />
          <div className="h-2 w-3/4 rounded bg-[var(--bg-muted)]" />
        </div>
      </div>
      <div
        className="float-y-delay absolute -right-4 bottom-8 hidden h-24 w-36 rounded-2xl border border-[var(--line)] bg-[var(--bg-elevated)] p-3 shadow-[var(--shadow-card)] sm:block"
        style={{ transform: 'rotate(7deg)' }}
      >
        <div className="flex gap-1">
          <span className="h-2 w-2 rounded-full bg-[#ff5f57]" />
          <span className="h-2 w-2 rounded-full bg-[#febc2e]" />
          <span className="h-2 w-2 rounded-full bg-[#28c840]" />
        </div>
        <div className="mt-3 h-10 rounded-lg bg-[var(--bg-muted)]" />
      </div>

      <div
        className="relative overflow-hidden rounded-[1.75rem] border border-[var(--line)] shadow-[var(--shadow-float)]"
        style={{ transform: 'rotateY(-6deg) rotateX(4deg)' }}
      >
        <div className="flex items-center gap-2 border-b border-black/5 bg-[#eceff3] px-4 py-2.5 dark:border-white/5 dark:bg-[#1a2433]">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          <span className="ml-2 truncate text-[11px] font-medium text-[var(--muted)]">
            prism.app / live-preview
          </span>
        </div>
        <div
          key={slide.title}
          className="animate-rise relative min-h-[300px] p-8 md:min-h-[340px]"
          style={{ background: slide.gradient, color: slide.ink }}
        >
          <p className="text-[11px] font-bold uppercase tracking-[0.22em]" style={{ color: slide.accent }}>
            {slide.label}
          </p>
          <h3 className="font-display mt-4 text-3xl font-bold tracking-tight md:text-4xl">{slide.title}</h3>
          <p className="mt-3 text-sm" style={{ color: slide.muted }}>
            {slide.blurb}
          </p>
          <div className="mt-8 grid grid-cols-3 gap-2">
            {[0, 1, 2].map((n) => (
              <div
                key={n}
                className="h-16 rounded-xl"
                style={{ background: `${slide.ink}14` }}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="mt-5 flex justify-center gap-2">
        {slides.map((s, idx) => (
          <button
            key={s.title}
            type="button"
            aria-label={s.label}
            onClick={() => setI(idx)}
            className={`h-1.5 rounded-full transition-all ${
              idx === i ? 'w-8 bg-[var(--ink)]' : 'w-2 bg-[var(--line)]'
            }`}
          />
        ))}
      </div>
    </div>
  )
}

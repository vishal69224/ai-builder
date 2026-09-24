import { Link } from 'react-router-dom'

const included = [
  'Unlimited local generations',
  'Live React preview',
  'Code editor + ZIP download',
  'Built-in local AI (no API key required)',
]

export function BillingPage() {
  return (
    <div className="mx-auto max-w-2xl">
      <h2 className="k-title">Plan</h2>
      <p className="k-caption mt-2 max-w-lg" style={{ fontSize: 'var(--text-body)' }}>
        This portfolio demo runs on a free workspace. Paid upgrades are not available yet.
      </p>

      <div className="k-card mt-10 p-7">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="k-section">Studio Free</p>
            <p className="k-caption mt-1">Your current plan</p>
          </div>
          <span className="k-badge k-badge-accent">Active</span>
        </div>

        <p className="mt-6 text-[2rem] font-semibold tracking-tight">
          $0
          <span className="k-caption ml-2 text-[var(--text-body)] font-normal">forever</span>
        </p>

        <ul className="mt-6 space-y-2.5">
          {included.map((item) => (
            <li key={item} className="flex items-start gap-2.5 text-[var(--text-body)] text-[var(--ink)]">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[var(--accent)]" aria-hidden />
              {item}
            </li>
          ))}
        </ul>

        <Link to="/" className="k-btn k-btn-primary mt-8 w-full sm:w-auto">
          Back to studio
        </Link>
      </div>

      <p className="k-caption mt-6 max-w-lg leading-relaxed">
        Pro and Team billing will ship later. For this demo, everything you need to generate, preview,
        edit, and download sites is already included.
      </p>
    </div>
  )
}

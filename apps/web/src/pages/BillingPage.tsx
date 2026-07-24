import { Link } from 'react-router-dom'

const plans = [
  {
    name: 'Free',
    price: '$0',
    note: 'Build sites with AI, preview live, download ZIP.',
    cta: 'Start building',
    to: '/',
    featured: true,
  },
  {
    name: 'Pro',
    price: '$29',
    note: 'More generations when you need them. Coming soon.',
    cta: null,
    to: null,
    featured: false,
  },
  {
    name: 'Team',
    price: '$99',
    note: 'Shared workspaces for your studio. Coming soon.',
    cta: null,
    to: null,
    featured: false,
  },
]

export function BillingPage() {
  return (
    <div className="mx-auto max-w-3xl">
      <h2 className="k-title">Billing</h2>
      <p className="k-caption mt-2 max-w-md" style={{ fontSize: 'var(--text-body)' }}>
        Start free. Upgrade when you outgrow it.
      </p>

      <div className="mt-12 grid gap-5 md:grid-cols-3">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={`k-card flex flex-col p-6 ${
              plan.featured ? 'ring-2 ring-[var(--accent)] ring-offset-2 ring-offset-[var(--bg)]' : ''
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <p className="k-section">{plan.name}</p>
              {plan.featured && <span className="k-badge k-badge-accent">Current</span>}
            </div>
            <p className="mt-5 text-[1.75rem] font-semibold tracking-tight">{plan.price}</p>
            <p className="k-caption mt-2 flex-1" style={{ fontSize: 'var(--text-body)' }}>
              {plan.note}
            </p>
            {plan.to && plan.cta ? (
              <Link to={plan.to} className="k-btn k-btn-primary mt-8 w-full">
                {plan.cta}
              </Link>
            ) : (
              <button type="button" disabled className="k-btn mt-8 w-full">
                Coming soon
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export function BillingPage() {
  return (
    <div className="mx-auto max-w-3xl">
      <div className="rounded-2xl border border-[var(--line)] bg-[var(--bg-elevated)] p-6 md:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--accent-2)]">
          Coming soon
        </p>
        <h3 className="mt-2 text-2xl font-semibold tracking-tight">Billing</h3>
        <p className="mt-3 max-w-xl text-sm leading-relaxed text-[var(--muted)]">
          Plans, usage meters, and invoices will live here. For now this is a placeholder so the
          dashboard navigation and layout are complete.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          {[
            { name: 'Starter', price: '$0', note: 'Mock generations' },
            { name: 'Pro', price: '$29', note: 'Real AI + more runs' },
            { name: 'Team', price: '$99', note: 'Shared workspaces' },
          ].map((plan) => (
            <div
              key={plan.name}
              className="rounded-xl border border-[var(--line)] bg-[var(--bg)] p-4 opacity-80"
            >
              <p className="text-sm font-semibold">{plan.name}</p>
              <p className="mt-2 text-2xl font-semibold">{plan.price}</p>
              <p className="mt-1 text-xs text-[var(--muted)]">{plan.note}</p>
              <button
                type="button"
                disabled
                className="mt-4 w-full rounded-lg border border-[var(--line)] px-3 py-2 text-sm font-medium opacity-60"
              >
                Unavailable
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

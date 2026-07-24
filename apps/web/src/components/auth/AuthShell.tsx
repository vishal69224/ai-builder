import type { ReactNode } from 'react'
import { EmberLogo } from '../brand/KilnLogo'

type AuthShellProps = {
  title: string
  subtitle: string
  children: ReactNode
  footer: ReactNode
}

export function AuthShell({ title, subtitle, children, footer }: AuthShellProps) {
  return (
    <div className="k-surface relative min-h-screen overflow-hidden">
      <div className="k-ambient" aria-hidden />
      <div className="relative mx-auto grid min-h-screen max-w-5xl lg:grid-cols-2">
        <aside className="hidden flex-col justify-between px-10 py-12 lg:flex">
          <EmberLogo to="/" />
          <div className="max-w-sm pb-8">
            <h2 className="k-title mt-3" style={{ fontSize: '1.85rem' }}>
              Build a website with AI
            </h2>
            <p className="k-caption mt-4" style={{ fontSize: 'var(--text-body)' }}>
              Describe a site, preview it live, edit the code, download the project.
            </p>
          </div>
          <p className="k-caption">Ember</p>
        </aside>

        <main className="flex items-center justify-center px-5 py-12 sm:px-8">
          <div className="w-full max-w-[400px]">
            <div className="mb-8 lg:hidden">
              <EmberLogo to="/" />
            </div>
            <div className="k-card p-6 sm:p-7">
              <h1 className="k-title" style={{ fontSize: '1.5rem' }}>
                {title}
              </h1>
              <p className="k-caption mt-2" style={{ fontSize: 'var(--text-body)' }}>
                {subtitle}
              </p>
              <div className="mt-6">{children}</div>
            </div>
            <div className="mt-6 text-center text-[var(--text-body)] text-[var(--muted)]">{footer}</div>
          </div>
        </main>
      </div>
    </div>
  )
}

export function AuthField({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="k-caption mb-1.5 block font-medium">{label}</span>
      {children}
    </label>
  )
}

export const authInputClass = 'k-input'
export const authPrimaryBtnClass = 'k-btn k-btn-primary w-full'

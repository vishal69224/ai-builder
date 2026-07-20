import { useAuth } from '../../auth/AuthContext'
import { useTheme } from '../../theme/ThemeContext'

type TopNavProps = {
  title: string
  subtitle?: string
  onMenuClick: () => void
}

export function TopNav({ title, subtitle, onMenuClick }: TopNavProps) {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b border-[var(--line)] bg-[var(--topnav)] px-4 py-3 backdrop-blur md:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-[var(--line)] bg-[var(--bg-elevated)] text-lg lg:hidden"
          aria-label="Open sidebar"
        >
          ☰
        </button>
        <div className="min-w-0">
          <h2 className="truncate text-base font-semibold tracking-tight md:text-lg">{title}</h2>
          {subtitle && <p className="truncate text-xs text-[var(--muted)] md:text-sm">{subtitle}</p>}
        </div>
      </div>

      <div className="flex items-center gap-2 md:gap-3">
        <button
          type="button"
          onClick={toggleTheme}
          className="rounded-lg border border-[var(--line)] bg-[var(--bg-elevated)] px-3 py-2 text-xs font-medium md:text-sm"
          aria-label="Toggle dark mode"
        >
          {theme === 'dark' ? 'Light' : 'Dark'}
        </button>
        <div className="hidden text-right sm:block">
          <p className="text-sm font-medium leading-tight">{user?.name}</p>
          <p className="text-xs text-[var(--muted)]">{user?.email}</p>
        </div>
        <button
          type="button"
          onClick={logout}
          className="rounded-lg bg-[var(--ink)] px-3 py-2 text-xs font-semibold text-[var(--bg)] md:text-sm"
        >
          Log out
        </button>
      </div>
    </header>
  )
}

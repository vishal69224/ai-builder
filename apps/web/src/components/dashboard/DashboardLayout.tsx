import { useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { EmberLogo } from '../brand/KilnLogo'
import { useTheme } from '../../theme/ThemeContext'

const links = [
  { to: '/projects', label: 'Projects', end: true },
  { to: '/history', label: 'History', end: false },
  { to: '/settings', label: 'Settings', end: false },
  { to: '/billing', label: 'Billing', end: false },
]

export function DashboardLayout() {
  const [menuOpen, setMenuOpen] = useState(false)
  const { pathname } = useLocation()
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="k-surface relative min-h-screen">
      <header className="sticky top-0 z-40 border-b border-[var(--line)] bg-[var(--topnav)] backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4 md:px-6">
          <div className="flex items-center gap-6">
            <EmberLogo size="sm" />
            <nav className="hidden items-center gap-1 md:flex">
              {links.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.end}
                  className={({ isActive }) =>
                    `rounded-[var(--radius-sm)] px-3 py-1.5 text-[13px] font-medium no-underline transition ${
                      isActive
                        ? 'bg-[var(--accent-soft)] text-[var(--accent)]'
                        : 'text-[var(--muted)] hover:bg-[var(--bg-muted)] hover:text-[var(--ink)]'
                    }`
                  }
                >
                  {link.label}
                </NavLink>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-2">
            <NavLink
              to="/"
              className="k-btn k-btn-ghost hidden text-[13px] sm:inline-flex"
            >
              New build
            </NavLink>
            <button type="button" onClick={toggleTheme} className="k-btn k-btn-ghost text-[13px]">
              {theme === 'dark' ? 'Light' : 'Dark'}
            </button>
            <span className="hidden text-[13px] font-medium text-[var(--muted)] lg:inline">
              {user?.name?.split(' ')[0]}
            </span>
            <button type="button" onClick={logout} className="k-btn text-[13px]">
              Log out
            </button>
            <button
              type="button"
              className="k-btn md:hidden"
              aria-expanded={menuOpen}
              aria-label="Open menu"
              onClick={() => setMenuOpen((v) => !v)}
            >
              Menu
            </button>
          </div>
        </div>

        {menuOpen && (
          <nav className="border-t border-[var(--line)] px-4 py-3 md:hidden">
            <div className="flex flex-col gap-1">
              {links.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.end}
                  onClick={() => setMenuOpen(false)}
                  className={({ isActive }) =>
                    `rounded-[var(--radius-sm)] px-3 py-2.5 text-[var(--text-body)] font-medium no-underline ${
                      isActive
                        ? 'bg-[var(--accent-soft)] text-[var(--accent)]'
                        : 'text-[var(--muted)]'
                    }`
                  }
                >
                  {link.label}
                </NavLink>
              ))}
              <NavLink
                to="/"
                onClick={() => setMenuOpen(false)}
                className="rounded-[var(--radius-sm)] px-3 py-2.5 font-medium text-[var(--accent)] no-underline"
              >
                New build
              </NavLink>
            </div>
          </nav>
        )}
      </header>

      <main key={pathname} className="k-fade mx-auto max-w-6xl px-4 py-10 md:px-6">
        <Outlet />
      </main>
    </div>
  )
}

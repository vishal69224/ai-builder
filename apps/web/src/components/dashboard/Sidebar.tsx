import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Projects', end: true, icon: '▦' },
  { to: '/projects/new', label: 'New project', end: false, icon: '+' },
  { to: '/history', label: 'Prompt history', end: false, icon: '☰' },
  { to: '/settings', label: 'Settings', end: false, icon: '⚙' },
  { to: '/billing', label: 'Billing', end: false, icon: '💳' },
]

type SidebarProps = {
  open: boolean
  onClose: () => void
}

export function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      <div
        className={`fixed inset-0 z-40 bg-black/40 transition lg:hidden ${open ? 'opacity-100' : 'pointer-events-none opacity-0'}`}
        onClick={onClose}
        aria-hidden={!open}
      />
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-[var(--sidebar)] text-[var(--sidebar-ink)] transition-transform duration-200 lg:static lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="border-b border-white/10 px-5 py-5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-[var(--sidebar-muted)]">
            AI Website Builder
          </p>
          <h1 className="mt-1 text-lg font-semibold tracking-tight">Studio</h1>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                  isActive
                    ? 'bg-white/12 text-white'
                    : 'text-[var(--sidebar-muted)] hover:bg-white/6 hover:text-white'
                }`
              }
            >
              <span className="w-5 text-center text-base leading-none opacity-80">{link.icon}</span>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 px-5 py-4 text-xs text-[var(--sidebar-muted)]">
          Generate · Preview · Iterate
        </div>
      </aside>
    </>
  )
}

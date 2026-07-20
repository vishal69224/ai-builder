import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopNav } from './TopNav'

const titles: Record<string, { title: string; subtitle: string }> = {
  '/': { title: 'Projects', subtitle: 'Manage and open your generated websites' },
  '/projects/new': { title: 'Create project', subtitle: 'Name it and describe what to generate' },
  '/history': { title: 'Prompt history', subtitle: 'Past generation prompts across projects' },
  '/settings': { title: 'User settings', subtitle: 'Profile and preferences' },
  '/billing': { title: 'Billing', subtitle: 'Plans and usage — placeholder' },
}

export function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { pathname } = useLocation()
  const meta = titles[pathname] ?? { title: 'Dashboard', subtitle: '' }

  return (
    <div className="flex min-h-screen bg-[var(--bg)] text-[var(--ink)]">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopNav
          title={meta.title}
          subtitle={meta.subtitle}
          onMenuClick={() => setSidebarOpen(true)}
        />
        <main className="flex-1 px-4 py-6 md:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

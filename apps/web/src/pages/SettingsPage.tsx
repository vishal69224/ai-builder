import { useState, type FormEvent } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useTheme } from '../theme/ThemeContext'

export function SettingsPage() {
  const { user } = useAuth()
  const { theme, setTheme } = useTheme()
  const [name, setName] = useState(user?.name ?? '')
  const [saved, setSaved] = useState(false)

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    // Profile update API lands in a later auth phase; persist locally for now.
    localStorage.setItem('ai_builder_display_name', name.trim())
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="mx-auto grid max-w-3xl gap-6">
      <form
        onSubmit={onSubmit}
        className="space-y-4 rounded-2xl border border-[var(--line)] bg-[var(--bg-elevated)] p-6"
      >
        <h3 className="text-base font-semibold">Profile</h3>
        <label className="block text-sm">
          <span className="mb-1.5 block font-medium">Display name</span>
          <input
            className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3 py-2.5 outline-none ring-[var(--accent-2)] focus:ring-2"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1.5 block font-medium">Email</span>
          <input
            className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg-muted)] px-3 py-2.5 text-[var(--muted)]"
            value={user?.email ?? ''}
            disabled
          />
        </label>
        <button
          type="submit"
          className="rounded-xl bg-[var(--ink)] px-4 py-2.5 text-sm font-semibold text-[var(--bg)]"
        >
          Save changes
        </button>
        {saved && <p className="text-sm text-[var(--accent)]">Preferences saved locally.</p>}
      </form>

      <div className="space-y-4 rounded-2xl border border-[var(--line)] bg-[var(--bg-elevated)] p-6">
        <h3 className="text-base font-semibold">Appearance</h3>
        <p className="text-sm text-[var(--muted)]">Choose light or dark mode for the dashboard.</p>
        <div className="flex gap-2">
          {(['light', 'dark'] as const).map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setTheme(mode)}
              className={`rounded-xl px-4 py-2 text-sm font-medium capitalize ${
                theme === mode
                  ? 'bg-[var(--ink)] text-[var(--bg)]'
                  : 'border border-[var(--line)] bg-[var(--bg)]'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

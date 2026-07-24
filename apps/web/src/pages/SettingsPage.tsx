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
    localStorage.setItem('ai_builder_display_name', name.trim())
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="mx-auto grid max-w-lg gap-8">
      <div>
        <h2 className="k-title">Settings</h2>
        <p className="k-caption mt-2">Account and appearance.</p>
      </div>

      <form onSubmit={onSubmit} className="k-card space-y-5 p-6">
        <h3 className="k-section">Profile</h3>
        <label className="block">
          <span className="k-caption mb-1.5 block font-medium">Display name</span>
          <input className="k-input" value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label className="block">
          <span className="k-caption mb-1.5 block font-medium">Email</span>
          <input className="k-input" value={user?.email ?? ''} disabled />
        </label>
        <button type="submit" className="k-btn k-btn-primary">
          Save
        </button>
        {saved && <p className="k-caption font-medium text-[var(--success)]">Saved.</p>}
      </form>

      <div className="k-card space-y-5 p-6">
        <h3 className="k-section">Appearance</h3>
        <p className="k-caption">Light or dark — same warm Ember system.</p>
        <div className="flex gap-2">
          {(['light', 'dark'] as const).map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setTheme(mode)}
              className={`k-btn capitalize ${theme === mode ? 'k-btn-primary' : ''}`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

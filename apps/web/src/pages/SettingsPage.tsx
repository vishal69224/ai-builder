import { useEffect, useState, type FormEvent } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useTheme } from '../theme/ThemeContext'

export function SettingsPage() {
  const { user, updateProfile } = useAuth()
  const { theme, setTheme } = useTheme()
  const [name, setName] = useState(user?.name ?? '')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setName(user?.name ?? '')
  }, [user?.name])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    const next = name.trim()
    if (!next) {
      setError('Display name is required.')
      return
    }
    if (next === user?.name) {
      setSaved(true)
      window.setTimeout(() => setSaved(false), 2000)
      return
    }
    setSaving(true)
    setError(null)
    setSaved(false)
    try {
      await updateProfile(next)
      setSaved(true)
      window.setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="mx-auto grid max-w-lg gap-8">
      <div>
        <h2 className="k-title">Settings</h2>
        <p className="k-caption mt-2">Account and appearance.</p>
      </div>

      <form onSubmit={(e) => void onSubmit(e)} className="k-card space-y-5 p-6">
        <h3 className="k-section">Profile</h3>
        <label className="block">
          <span className="k-caption mb-1.5 block font-medium">Display name</span>
          <input
            className="k-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            maxLength={120}
            required
            autoComplete="name"
          />
        </label>
        <label className="block">
          <span className="k-caption mb-1.5 block font-medium">Email</span>
          <input className="k-input" value={user?.email ?? ''} disabled />
        </label>
        <div className="flex flex-wrap items-center gap-3">
          <button type="submit" className="k-btn k-btn-primary" disabled={saving || !name.trim()}>
            {saving ? 'Saving…' : 'Save changes'}
          </button>
          {saved && <p className="k-caption font-medium text-[var(--success)]">Saved to your account.</p>}
        </div>
        {error && <p className="text-[var(--text-body)] text-[var(--danger)]">{error}</p>}
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

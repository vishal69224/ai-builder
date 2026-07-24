import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import {
  AuthField,
  AuthShell,
  authInputClass,
  authPrimaryBtnClass,
} from '../components/auth/AuthShell'

export function RegisterPage() {
  const { register, token } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  if (token) return <Navigate to="/" replace />

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await register(email, password, name)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create your account. Try again.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AuthShell
      title="Create your account"
      subtitle="Join Studio and turn a short brief into a React + Vite site you can preview and download."
      footer={
        <>
          Already have an account?{' '}
          <Link
            className="font-semibold text-[var(--accent)] underline-offset-4 hover:underline"
            to="/login"
          >
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <AuthField label="Full name">
          <input
            className={authInputClass}
            autoComplete="name"
            placeholder="Alex Rivera"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </AuthField>

        <AuthField label="Email">
          <input
            className={authInputClass}
            type="email"
            autoComplete="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </AuthField>

        <AuthField label="Password">
          <div className="relative">
            <input
              className={`${authInputClass} pr-16`}
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-[var(--muted)] transition hover:bg-[var(--bg-muted)] hover:text-[var(--ink)]"
            >
              {showPassword ? 'Hide' : 'Show'}
            </button>
          </div>
          <span className="mt-1.5 block text-xs text-[var(--muted)]">
            Use 8+ characters for a stronger password.
          </span>
        </AuthField>

        {error && (
          <p
            role="alert"
            className="rounded-xl border border-[color-mix(in_oklab,var(--danger)_30%,transparent)] bg-[color-mix(in_oklab,var(--danger)_8%,transparent)] px-3.5 py-2.5 text-sm text-[var(--danger)]"
          >
            {error}
          </p>
        )}

        <button type="submit" disabled={busy} className={authPrimaryBtnClass}>
          {busy ? 'Creating…' : 'Create account'}
        </button>
      </form>
    </AuthShell>
  )
}

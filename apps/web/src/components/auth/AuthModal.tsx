import { useEffect, useId, useState, type FormEvent } from 'react'
import { createPortal } from 'react-dom'
import { useAuth } from '../../auth/AuthContext'
import { AuthField, authInputClass, authPrimaryBtnClass } from './AuthShell'

type Mode = 'signin' | 'signup'

type AuthModalProps = {
  open: boolean
  initialMode?: Mode
  onClose: () => void
  onSuccess: () => void
  reason?: string
}

export function AuthModal({
  open,
  initialMode = 'signup',
  onClose,
  onSuccess,
  reason = 'Sign in to generate your website and save it.',
}: AuthModalProps) {
  const { login, register } = useAuth()
  const titleId = useId()
  const [mode, setMode] = useState<Mode>(initialMode)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (open) {
      setMode(initialMode)
      setError(null)
    }
  }, [open, initialMode])

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [open, onClose])

  if (!open) return null

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      if (mode === 'signin') {
        await login(email, password)
      } else {
        await register(email, password, name.trim() || email.split('@')[0] || 'Maker')
      }
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Try again.')
    } finally {
      setBusy(false)
    }
  }

  return createPortal(
    <div className="fixed inset-0 z-[100] flex items-end justify-center p-4 sm:items-center sm:p-6">
      <button
        type="button"
        aria-label="Close"
        className="absolute inset-0 bg-black/55 backdrop-blur-[2px]"
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="k-card relative z-10 w-full max-w-[400px] p-7 sm:p-8"
      >
        <div className="text-center">
          <h2 id={titleId} className="k-title" style={{ fontSize: '1.4rem' }}>
            {mode === 'signin' ? 'Welcome back' : 'Create your account'}
          </h2>
          <p className="k-caption mx-auto mt-2 max-w-sm leading-relaxed" style={{ fontSize: 'var(--text-body)' }}>
            {reason}
          </p>
        </div>

        <div className="mt-7 grid grid-cols-2 gap-1 rounded-[var(--radius)] border border-[var(--line)] bg-[var(--bg-muted)] p-1">
          <button
            type="button"
            onClick={() => {
              setMode('signup')
              setError(null)
            }}
            className={`rounded-[var(--radius-sm)] px-3 py-2.5 text-[var(--text-body)] font-medium transition ${
              mode === 'signup' ? 'bg-[var(--bg-elevated)] text-[var(--ink)] shadow-[var(--shadow-soft)]' : 'text-[var(--muted)]'
            }`}
          >
            Sign up
          </button>
          <button
            type="button"
            onClick={() => {
              setMode('signin')
              setError(null)
            }}
            className={`rounded-[var(--radius-sm)] px-3 py-2.5 text-[var(--text-body)] font-medium transition ${
              mode === 'signin' ? 'bg-[var(--bg-elevated)] text-[var(--ink)] shadow-[var(--shadow-soft)]' : 'text-[var(--muted)]'
            }`}
          >
            Sign in
          </button>
        </div>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          {mode === 'signup' && (
            <AuthField label="Name">
              <input
                className={authInputClass}
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alex Rivera"
                autoComplete="name"
              />
            </AuthField>
          )}
          <AuthField label="Email">
            <input
              className={authInputClass}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              autoComplete="email"
              required
            />
          </AuthField>
          <AuthField label="Password">
            <div className="relative">
              <input
                className={`${authInputClass} pr-16`}
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
                autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
                required
                minLength={8}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md px-2 py-1 text-[var(--text-caption)] font-medium text-[var(--muted)] hover:text-[var(--ink)]"
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </AuthField>

          {error && (
            <p
              role="alert"
              className="rounded-[var(--radius)] border border-[var(--line)] px-3 py-2.5 text-center text-[var(--text-body)] text-[var(--danger)]"
            >
              {error}
            </p>
          )}

          <button type="submit" disabled={busy} className={`${authPrimaryBtnClass} mt-1`}>
            {busy
              ? mode === 'signin'
                ? 'Signing in…'
                : 'Creating…'
              : mode === 'signin'
                ? 'Sign in'
                : 'Create account'}
          </button>
        </form>
      </div>
    </div>,
    document.body,
  )
}

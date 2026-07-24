import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { AuthModal } from '../components/auth/AuthModal'
import { EmberLogo } from '../components/brand/KilnLogo'
import { GenerationStages } from '../components/GenerationStages'
import { api, type Project } from '../lib/api'
import { clearPendingPrompt, readPendingPrompt, savePendingPrompt } from '../lib/pendingPrompt'
import { useTheme } from '../theme/ThemeContext'

const suggestions = [
  {
    label: 'Fashion store',
    prompt:
      'Premium luxury fashion clothing brand website called VELORA for men and women — shop, lookbook, and sign in',
  },
  {
    label: 'Developer portfolio',
    prompt: 'Flutter and Python developer portfolio with projects, skills, and contact',
  },
  {
    label: 'Café website',
    prompt: 'Warm café website with menu, story, hours, and reservation for Harbor Roast',
  },
  {
    label: 'SaaS landing',
    prompt: 'SaaS analytics landing with hero, features, pricing, and signup called Pulse',
  },
  {
    label: 'Booking studio',
    prompt: 'Booking site for a photography studio with portfolio, packages, and calendar',
  },
  {
    label: 'Restaurant menu',
    prompt: 'Modern restaurant website with tasting menu, chef story, and reservations',
  },
]

export function StudioHomePage() {
  const { token, user, loading, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const [prompt, setPrompt] = useState('')
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [authOpen, setAuthOpen] = useState(false)
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signup')
  const [recent, setRecent] = useState<Project[]>([])
  const [tinygptOnline, setTinygptOnline] = useState<boolean | null>(null)
  const pendingStarted = useRef(false)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const s = await api.aiStatus()
        if (!cancelled) setTinygptOnline(Boolean(s.tinygpt?.ok))
      } catch {
        if (!cancelled) setTinygptOnline(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    const t = window.setTimeout(() => inputRef.current?.focus(), 160)
    return () => window.clearTimeout(t)
  }, [])

  useEffect(() => {
    if (!token) {
      setRecent([])
      return
    }
    let cancelled = false
    ;(async () => {
      try {
        const list = await api.listProjects(token)
        if (!cancelled) setRecent(list.slice(0, 3))
      } catch {
        /* ignore */
      }
    })()
    return () => {
      cancelled = true
    }
  }, [token])

  const runGenerate = useCallback(
    async (text: string, accessToken: string) => {
      setBusy(true)
      setError(null)
      setStatus('Building your site…')
      try {
        const result = await api.generate(accessToken, { prompt: text })
        clearPendingPrompt()
        pendingStarted.current = false
        navigate(`/projects/${result.project.id}`)
      } catch (err) {
        pendingStarted.current = false
        setError(err instanceof Error ? err.message : 'Generation failed')
        setStatus(null)
      } finally {
        setBusy(false)
      }
    },
    [navigate],
  )

  useEffect(() => {
    if (loading || !token || pendingStarted.current) return
    const pending = readPendingPrompt()
    if (!pending) return
    pendingStarted.current = true
    setPrompt(pending)
    void runGenerate(pending, token)
  }, [loading, token, runGenerate])

  function requestGenerate(raw: string) {
    const text = raw.trim()
    if (!text || busy) return
    if (!token) {
      savePendingPrompt(text)
      setAuthMode('signup')
      setAuthOpen(true)
      setStatus('Sign in to save your site.')
      return
    }
    void runGenerate(text, token)
  }

  return (
    <div className="k-surface relative min-h-screen overflow-hidden">
      <div className="k-ambient" aria-hidden />

      <header className="relative z-20 mx-auto flex w-full max-w-5xl items-center justify-between px-5 py-4 md:px-6">
        <EmberLogo />
        <div className="flex items-center gap-1">
          <button type="button" className="k-btn k-btn-ghost" onClick={toggleTheme}>
            {theme === 'dark' ? 'Light' : 'Dark'}
          </button>
          {token ? (
            <>
              <Link to="/projects" className="k-btn k-btn-ghost">
                Projects
              </Link>
              <span className="hidden px-2 text-[var(--text-caption)] text-[var(--muted)] sm:inline">
                {user?.name?.split(' ')[0]}
              </span>
              <button type="button" className="k-btn k-btn-ghost" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                className="k-btn k-btn-ghost"
                onClick={() => {
                  setAuthMode('signin')
                  setAuthOpen(true)
                }}
              >
                Sign in
              </button>
              <button
                type="button"
                className="k-btn k-btn-primary"
                onClick={() => {
                  setAuthMode('signup')
                  setAuthOpen(true)
                }}
              >
                Get started
              </button>
            </>
          )}
        </div>
      </header>

      <main className="relative z-10 mx-auto flex min-h-[calc(100vh-4.5rem)] w-full max-w-xl flex-col px-5 pb-16 md:px-6">
        <div className="flex flex-1 flex-col justify-center py-8">
          <div className="k-fade text-center">
            <h1
              className="k-title"
              style={{ fontSize: 'clamp(1.75rem, 4.5vw, 2.35rem)', letterSpacing: '-0.03em' }}
            >
              What are we building today?
            </h1>
            <p
              className="k-caption mx-auto mt-2.5 max-w-lg leading-relaxed"
              style={{ fontSize: 'var(--text-body)' }}
            >
              Describe a website — Ember builds a live React site you can preview, edit, and download.
            </p>
          </div>

          <form
            className="ember-prompt k-fade mt-7"
            style={{ animationDelay: '0.05s' }}
            onSubmit={(e: FormEvent) => {
              e.preventDefault()
              requestGenerate(prompt)
            }}
          >
            <textarea
              ref={inputRef}
              className="ember-prompt__input"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  requestGenerate(prompt)
                }
              }}
              rows={2}
              disabled={busy}
              placeholder="What website do you need?"
              aria-label="Describe the website to build"
            />
            <div className="ember-prompt__bar">
              <span className="k-caption hidden sm:inline">Enter to build</span>
              <button
                type="submit"
                className={`ember-prompt__send ${busy ? 'k-pulse-warm' : ''}`}
                disabled={busy || !prompt.trim()}
                aria-label="Build site"
              >
                {busy ? (
                  <span className="k-spin inline-block h-4 w-4 rounded-full border-2 border-[#fffcf8] border-t-transparent" />
                ) : (
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
                    <path
                      d="M8 12V4M8 4L4.5 7.5M8 4l3.5 3.5"
                      stroke="currentColor"
                      strokeWidth="1.75"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                )}
              </button>
            </div>
          </form>

          {!busy && (
            <div
              className="k-fade mt-6 flex flex-wrap justify-center gap-2.5"
              style={{ animationDelay: '0.1s' }}
            >
              {suggestions.map((s) => (
                <button
                  key={s.label}
                  type="button"
                  className="ember-pill"
                  disabled={busy}
                  onClick={() => {
                    setPrompt(s.prompt)
                    inputRef.current?.focus()
                  }}
                >
                  {s.label}
                </button>
              ))}
            </div>
          )}

          <GenerationStages active={busy} tinygptOnline={tinygptOnline} />

          {(status || error) && !busy && (
            <p
              className={`mt-6 text-center text-[var(--text-body)] ${error ? 'text-[var(--danger)]' : 'text-[var(--muted)]'}`}
            >
              {error || status}
            </p>
          )}
        </div>

        {token && recent.length > 0 && !busy && (
          <section className="mt-4 pb-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="k-section">Recent</h2>
              <Link
                to="/projects"
                className="k-caption font-medium text-[var(--accent)] no-underline hover:underline"
              >
                View all
              </Link>
            </div>
            <ul className="grid gap-2">
              {recent.map((p) => (
                <li key={p.id}>
                  <Link
                    to={`/projects/${p.id}`}
                    className="k-card flex items-center justify-between gap-3 px-4 py-3.5 no-underline"
                  >
                    <span className="min-w-0">
                      <span className="block truncate font-semibold text-[var(--ink)]">{p.name}</span>
                      <span className="k-caption block truncate">{p.description || 'Open workspace'}</span>
                    </span>
                    <span className="k-badge k-badge-accent shrink-0">Open</span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        )}
      </main>

      <AuthModal
        open={authOpen}
        initialMode={authMode}
        onClose={() => setAuthOpen(false)}
        onSuccess={() => setAuthOpen(false)}
        reason="Sign in to save your Ember site and keep building."
      />
    </div>
  )
}

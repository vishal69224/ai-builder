import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { api } from '../lib/api'

export function NewProjectPage() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [prompt, setPrompt] = useState('')
  const [analysisPreview, setAnalysisPreview] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)

  async function onAnalyze() {
    if (!prompt.trim()) return
    setAnalyzing(true)
    setError(null)
    try {
      const result = await api.analyze(prompt.trim())
      setAnalysisPreview(result)
      if (!name.trim() && typeof result.website_type === 'string') {
        setName(String(result.website_type))
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analyze failed')
    } finally {
      setAnalyzing(false)
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!token) return
    setBusy(true)
    setError(null)
    try {
      if (prompt.trim()) {
        // Full pipeline: analyze → plan → generate → save
        const result = await api.generate(token, {
          prompt: prompt.trim(),
          project_name: name.trim() || undefined,
        })
        navigate(`/projects/${result.project.id}`)
        return
      }
      const project = await api.createProject(token, {
        name,
        description: description || undefined,
      })
      navigate(`/projects/${project.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <form
        onSubmit={onSubmit}
        className="space-y-5 rounded-2xl border border-[var(--line)] bg-[var(--bg-elevated)] p-6 md:p-8"
      >
        <label className="block text-sm">
          <span className="mb-1.5 block font-medium">Project name</span>
          <input
            className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3 py-2.5 outline-none ring-[var(--accent-2)] focus:ring-2"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Auto-filled from analyzer if empty"
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1.5 block font-medium">Description</span>
          <input
            className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3 py-2.5 outline-none ring-[var(--accent-2)] focus:ring-2"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional short summary"
          />
        </label>
        <label className="block text-sm">
          <span className="mb-1.5 block font-medium">Prompt</span>
          <textarea
            className="min-h-36 w-full rounded-xl border border-[var(--line)] bg-[var(--bg)] px-3 py-2.5 outline-none ring-[var(--accent-2)] focus:ring-2"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Build a modern coffee shop website with a warm palette…"
            required
          />
        </label>

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => void onAnalyze()}
            disabled={analyzing || !prompt.trim()}
            className="rounded-xl border border-[var(--line)] px-4 py-2.5 text-sm font-medium disabled:opacity-60"
          >
            {analyzing ? 'Analyzing…' : 'Analyze prompt'}
          </button>
          <button
            type="submit"
            disabled={busy || !prompt.trim()}
            className="rounded-xl bg-[var(--ink)] px-5 py-2.5 text-sm font-semibold text-[var(--bg)] disabled:opacity-60"
          >
            {busy ? 'Generating…' : 'Generate website'}
          </button>
          <Link
            to="/"
            className="rounded-xl border border-[var(--line)] px-5 py-2.5 text-sm font-medium"
          >
            Cancel
          </Link>
        </div>

        {error && <p className="text-sm text-[var(--danger)]">{error}</p>}

        {analysisPreview && (
          <div className="rounded-xl border border-[var(--line)] bg-[var(--bg)] p-4 text-sm">
            <p className="font-semibold">
              Type: {String(analysisPreview.website_type)}{' '}
              <span className="text-[var(--muted)]">
                ({Math.round(Number(analysisPreview.confidence ?? 0) * 100)}% confidence)
              </span>
            </p>
            <p className="mt-2 text-[var(--muted)]">
              Pages: {Array.isArray(analysisPreview.pages) ? analysisPreview.pages.join(', ') : '—'}
            </p>
            <p className="mt-1 text-[var(--muted)]">
              Components:{' '}
              {Array.isArray(analysisPreview.components)
                ? analysisPreview.components.join(', ')
                : '—'}
            </p>
          </div>
        )}
      </form>
    </div>
  )
}

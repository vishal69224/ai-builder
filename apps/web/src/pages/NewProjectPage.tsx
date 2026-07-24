import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { api } from '../lib/api'

const starters = [
  {
    label: 'Portfolio',
    prompt:
      'I am a Flutter developer and Python also so I want to make one portfolio — give me the perfect portfolio template I can edit and make mine',
  },
  {
    label: 'Clothing brand',
    prompt:
      'Create a premium luxury fashion clothing brand website called VELORA for men and women — clothing only, no shoes',
  },
  {
    label: 'Café',
    prompt:
      'Warm modern coffee shop website with menu, story, and visit hours for a local café called Harbor Roast',
  },
]

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
        const result = await api.generate(token, {
          prompt: prompt.trim(),
          project_name: name.trim() || undefined,
        })
        navigate(`/projects/${result.project.id}`, { replace: false })
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
    <div className="mx-auto grid max-w-4xl gap-8 lg:grid-cols-[1.1fr_0.9fr]">
      <form onSubmit={onSubmit} className="k-card space-y-4 p-6">
        <div>
          <p className="k-label">Brief</p>
          <h3 className="k-section mt-1">Tell Ember what to build</h3>
        </div>

        <label className="block">
          <span className="k-caption mb-1.5 block">Project name</span>
          <input
            className="k-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Optional"
          />
        </label>
        <label className="block">
          <span className="k-caption mb-1.5 block">Note</span>
          <input
            className="k-input"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional"
          />
        </label>
        <label className="block">
          <span className="k-caption mb-1.5 block">Prompt</span>
          <textarea
            className="k-input min-h-36"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the website…"
            required
          />
        </label>

        {error && <p className="text-[var(--text-body)] text-[var(--danger)]">{error}</p>}

        <div className="flex flex-wrap gap-2">
          <button type="button" className="k-btn" disabled={analyzing || !prompt.trim()} onClick={() => void onAnalyze()}>
            {analyzing ? 'Analyzing…' : 'Analyze'}
          </button>
          <button type="submit" className="k-btn k-btn-primary" disabled={busy || !prompt.trim()}>
            {busy ? 'Building…' : 'Build'}
          </button>
        </div>
      </form>

      <div className="space-y-4">
        <div className="k-card p-5">
          <p className="k-label">Examples</p>
          <ul className="mt-3 space-y-2">
            {starters.map((s) => (
              <li key={s.label}>
                <button
                  type="button"
                  className="w-full rounded-[var(--radius)] border border-[var(--line)] px-3 py-2.5 text-left transition hover:bg-[var(--bg-muted)]"
                  onClick={() => setPrompt(s.prompt)}
                >
                  <span className="block text-[var(--text-body)] font-medium">{s.label}</span>
                  <span className="k-caption mt-0.5 line-clamp-2 block">{s.prompt}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
        {analysisPreview && (
          <div className="k-card p-5">
            <p className="k-label">Analysis</p>
            <pre className="k-mono mt-3 max-h-64 overflow-auto text-[var(--muted)]">
              {JSON.stringify(analysisPreview, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

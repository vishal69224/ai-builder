import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { ProjectThumb } from '../components/brand/ProjectThumb'
import { api, type Project } from '../lib/api'

export function ProjectsPage() {
  const { token } = useAuth()
  const [projects, setProjects] = useState<Project[]>([])
  const [query, setQuery] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) return
    let cancelled = false
    ;(async () => {
      try {
        const data = await api.listProjects(token)
        if (!cancelled) setProjects(data)
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Couldn’t load projects')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [token])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return projects
    return projects.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        (p.description ?? '').toLowerCase().includes(q),
    )
  }, [projects, query])

  async function removeProject(id: string) {
    if (!token || !confirm('Archive this project?')) return
    await api.deleteProject(token, id)
    setProjects((prev) => prev.filter((p) => p.id !== id))
  }

  return (
    <div className="k-page">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="k-title">Projects</h2>
          <p className="k-caption mt-2">
            {projects.length} site{projects.length === 1 ? '' : 's'}
          </p>
        </div>
        <Link to="/" className="k-btn k-btn-primary">
          New site
        </Link>
      </div>

      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search projects…"
        className="k-input mt-10 max-w-sm"
      />

      {loading && <p className="k-caption mt-12">Loading…</p>}
      {error && <p className="mt-12 text-[var(--danger)]">{error}</p>}

      {!loading && !error && filtered.length === 0 && (
        <div className="k-card mt-14 px-6 py-16 text-center">
          <h3 className="k-section">No projects yet</h3>
          <p className="k-caption mx-auto mt-2 max-w-sm" style={{ fontSize: 'var(--text-body)' }}>
            Describe a website on the home page — Ember builds it in one step.
          </p>
          <Link to="/" className="k-btn k-btn-primary mt-8">
            Build a site
          </Link>
        </div>
      )}

      <ul className="mt-10 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((project) => (
          <li key={project.id} className="k-card overflow-hidden">
            <ProjectPreviewBanner id={project.id} name={project.name} />
            <div className="p-5">
              <div className="flex items-start justify-between gap-2">
                <Link
                  to={`/projects/${project.id}`}
                  className="truncate text-[var(--text-section)] font-semibold text-[var(--ink)] no-underline hover:text-[var(--accent)]"
                >
                  {project.name}
                </Link>
                <span
                  className={`k-badge shrink-0 ${
                    project.current_run_id ? 'k-badge-accent' : 'k-badge-neutral'
                  }`}
                >
                  {project.current_run_id ? 'Ready' : 'Draft'}
                </span>
              </div>
              <p className="k-caption mt-2 line-clamp-2">
                {project.description || 'Open workspace'}
              </p>
              <div className="mt-5 flex gap-2">
                <Link to={`/projects/${project.id}`} className="k-btn k-btn-primary">
                  Open
                </Link>
                <button
                  type="button"
                  onClick={() => void removeProject(project.id)}
                  className="k-btn k-btn-ghost text-[var(--danger)]"
                >
                  Archive
                </button>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}

function ProjectPreviewBanner({ id, name }: { id: string; name: string }) {
  let h = 0
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0
  const tints = [
    'linear-gradient(160deg, color-mix(in oklab, var(--accent) 22%, var(--bg-muted)), var(--bg-muted))',
    'linear-gradient(145deg, #ebe4da, color-mix(in oklab, var(--accent) 18%, #f6f1ea))',
    'linear-gradient(160deg, #2a241e, color-mix(in oklab, var(--accent) 45%, #3d2e24))',
  ]
  return (
    <div
      className="relative h-32 border-b border-[var(--line)]"
      style={{ background: tints[h % tints.length] }}
    >
      <div className="absolute inset-x-4 bottom-3 flex items-center gap-3 rounded-[var(--radius)] border border-[var(--line)] bg-[var(--bg-elevated)]/95 p-2.5 shadow-[var(--shadow-soft)]">
        <ProjectThumb id={id} name={name} size={40} />
        <div className="min-w-0 flex-1">
          <div className="h-2 w-3/5 rounded-full bg-[var(--bg-muted)]" />
          <div className="mt-2 flex gap-1.5">
            <div className="h-5 flex-1 rounded-[8px] bg-[var(--accent-soft)]" />
            <div className="h-5 flex-1 rounded-[8px] bg-[var(--bg-muted)]" />
          </div>
        </div>
      </div>
    </div>
  )
}

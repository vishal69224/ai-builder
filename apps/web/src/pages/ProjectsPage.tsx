import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
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
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load projects')
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
    <div className="mx-auto max-w-6xl">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:max-w-sm">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search projects…"
            className="w-full rounded-xl border border-[var(--line)] bg-[var(--bg-elevated)] px-4 py-2.5 text-sm outline-none ring-[var(--accent-2)] focus:ring-2"
          />
        </div>
        <Link
          to="/projects/new"
          className="inline-flex items-center justify-center rounded-xl bg-[var(--ink)] px-4 py-2.5 text-sm font-semibold text-[var(--bg)]"
        >
          Create new project
        </Link>
      </div>

      {loading && <p className="mt-10 text-[var(--muted)]">Loading projects…</p>}
      {error && <p className="mt-10 text-[var(--danger)]">{error}</p>}

      {!loading && !error && filtered.length === 0 && (
        <div className="mt-12 rounded-2xl border border-dashed border-[var(--line)] bg-[var(--bg-elevated)] px-6 py-12 text-center">
          <h3 className="text-lg font-semibold">No projects yet</h3>
          <p className="mx-auto mt-2 max-w-md text-sm text-[var(--muted)]">
            Create a project, describe the website you want, and generate a React app.
          </p>
          <Link
            to="/projects/new"
            className="mt-6 inline-flex rounded-xl bg-[var(--accent)] px-4 py-2.5 text-sm font-semibold text-white"
          >
            Create your first project
          </Link>
        </div>
      )}

      <ul className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {filtered.map((project) => (
          <li
            key={project.id}
            className="flex flex-col rounded-2xl border border-[var(--line)] bg-[var(--bg-elevated)] p-5 shadow-[0_1px_0_rgba(15,28,46,0.04)]"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <Link
                  to={`/projects/${project.id}`}
                  className="block truncate text-base font-semibold hover:underline"
                >
                  {project.name}
                </Link>
                <p className="mt-1 line-clamp-2 text-sm text-[var(--muted)]">
                  {project.description || 'No description'}
                </p>
              </div>
              <span
                className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${
                  project.current_run_id
                    ? 'bg-[var(--accent-soft)] text-[var(--accent)]'
                    : 'bg-[var(--bg-muted)] text-[var(--muted)]'
                }`}
              >
                {project.current_run_id ? 'Ready' : 'Draft'}
              </span>
            </div>
            <p className="mt-4 text-xs text-[var(--muted)]">
              Updated {new Date(project.updated_at).toLocaleString()}
            </p>
            <div className="mt-4 flex gap-2">
              <Link
                to={`/projects/${project.id}`}
                className="rounded-lg border border-[var(--line)] px-3 py-1.5 text-sm font-medium"
              >
                Open
              </Link>
              <button
                type="button"
                onClick={() => void removeProject(project.id)}
                className="rounded-lg px-3 py-1.5 text-sm font-medium text-[var(--danger)]"
              >
                Archive
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}

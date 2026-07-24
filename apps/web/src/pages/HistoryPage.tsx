import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { api, type Generation, type Project } from '../lib/api'

type HistoryRow = Generation & { projectName: string }

function statusBadge(status: string) {
  const s = status.toLowerCase()
  if (s === 'succeeded' || s === 'completed' || s === 'success') return 'k-badge-success'
  if (s === 'failed' || s === 'error') return 'k-badge-danger'
  if (s === 'queued' || s === 'running' || s === 'pending') return 'k-badge-accent'
  return 'k-badge-neutral'
}

function friendlyStatus(status: string) {
  const s = status.toLowerCase()
  if (s === 'succeeded' || s === 'completed') return 'Ready'
  if (s === 'failed') return 'Failed'
  if (s === 'running') return 'Building'
  if (s === 'queued') return 'Queued'
  return status
}

export function HistoryPage() {
  const { token } = useAuth()
  const [rows, setRows] = useState<HistoryRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    let cancelled = false
    ;(async () => {
      try {
        const projects = await api.listProjects(token)
        const batches = await Promise.all(
          projects.map(async (project: Project) => {
            const gens = await api.listGenerations(token, project.id)
            return gens.map((g) => ({ ...g, projectName: project.name }))
          }),
        )
        const flat = batches.flat().sort((a, b) => +new Date(b.created_at) - +new Date(a.created_at))
        if (!cancelled) setRows(flat)
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Couldn’t load history')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [token])

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-10">
        <h2 className="k-title">History</h2>
        <p className="k-caption mt-2">Every build you run, in one place.</p>
      </div>

      {loading && <p className="k-caption">Loading…</p>}
      {error && <p className="text-[var(--danger)]">{error}</p>}
      {!loading && !error && rows.length === 0 && (
        <div className="k-card px-6 py-16 text-center">
          <h3 className="k-section">No builds yet</h3>
          <p className="k-caption mt-2">Generate a site — it will show up here.</p>
          <Link to="/" className="k-btn k-btn-primary mt-8">
            Build a site
          </Link>
        </div>
      )}
      <ul className="space-y-3">
        {rows.map((row) => (
          <li key={row.id} className="k-card p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <Link
                to={`/projects/${row.project_id}`}
                className="font-semibold text-[var(--ink)] no-underline hover:text-[var(--accent)]"
              >
                {row.projectName}
              </Link>
              <div className="flex items-center gap-2">
                <span className={`k-badge ${statusBadge(row.status)}`}>{friendlyStatus(row.status)}</span>
                <span className="k-caption">{new Date(row.created_at).toLocaleString()}</span>
              </div>
            </div>
            <p className="mt-3 text-[var(--text-body)] leading-relaxed text-[var(--muted)]">{row.prompt}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}

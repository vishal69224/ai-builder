import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { api, type Generation, type Project } from '../lib/api'

type HistoryRow = Generation & { projectName: string }

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
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load history')
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [token])

  return (
    <div className="mx-auto max-w-4xl">
      {loading && <p className="text-[var(--muted)]">Loading prompt history…</p>}
      {error && <p className="text-[var(--danger)]">{error}</p>}
      {!loading && !error && rows.length === 0 && (
        <div className="rounded-2xl border border-dashed border-[var(--line)] bg-[var(--bg-elevated)] px-6 py-12 text-center">
          <h3 className="text-lg font-semibold">No prompts yet</h3>
          <p className="mt-2 text-sm text-[var(--muted)]">
            Generations you run will appear here for quick reference.
          </p>
        </div>
      )}
      <ul className="space-y-3">
        {rows.map((row) => (
          <li
            key={row.id}
            className="rounded-2xl border border-[var(--line)] bg-[var(--bg-elevated)] p-5"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <Link
                to={`/projects/${row.project_id}`}
                className="text-sm font-semibold text-[var(--accent-2)] hover:underline"
              >
                {row.projectName}
              </Link>
              <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
                <span className="rounded-full bg-[var(--bg-muted)] px-2 py-0.5 font-semibold uppercase tracking-wide">
                  {row.status}
                </span>
                <span>{new Date(row.created_at).toLocaleString()}</span>
              </div>
            </div>
            <p className="mt-3 text-sm leading-relaxed">{row.prompt}</p>
            {row.error_message && (
              <p className="mt-2 text-sm text-[var(--danger)]">{row.error_message}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

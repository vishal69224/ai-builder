import Editor from '@monaco-editor/react'
import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { api, type FileEntry, type Generation, type Project } from '../lib/api'

type Tab = 'preview' | 'code' | 'history'

export function WorkspacePage() {
  const { id = '' } = useParams()
  const { token } = useAuth()
  const [project, setProject] = useState<Project | null>(null)
  const [runs, setRuns] = useState<Generation[]>([])
  const [files, setFiles] = useState<FileEntry[]>([])
  const [selectedPath, setSelectedPath] = useState<string | null>(null)
  const [content, setContent] = useState('')
  const [prompt, setPrompt] = useState('')
  const [tab, setTab] = useState<Tab>('preview')
  const [previewHtml, setPreviewHtml] = useState<string>('')
  const [livePreview, setLivePreview] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [statusMsg, setStatusMsg] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [saving, setSaving] = useState(false)

  const latestActive = useMemo(
    () => runs.find((r) => r.status === 'queued' || r.status === 'running'),
    [runs],
  )

  const refresh = useCallback(async () => {
    if (!token || !id) return
    const [p, gens] = await Promise.all([api.getProject(token, id), api.listGenerations(token, id)])
    setProject(p)
    setRuns(gens)
    if (p.current_run_id) {
      const fileList = await api.listFiles(token, id)
      setFiles(fileList)
      if (!selectedPath && fileList.length) {
        const preferred =
          fileList.find((f) => f.path === 'src/pages/HomePage.tsx') ??
          fileList.find((f) => f.path === 'src/App.tsx') ??
          fileList.find((f) => f.path === 'README.md') ??
          fileList[0]
        setSelectedPath(preferred.path)
      }
      const liveOk = await probeLivePreview(token, id)
      setLivePreview(liveOk)
      if (!liveOk) {
        const html = await fetchPreview(token, id)
        setPreviewHtml(html)
      }
    }
  }, [token, id, selectedPath])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        await refresh()
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load project')
      }
    })()
    return () => {
      cancelled = true
    }
  }, [refresh])

  useEffect(() => {
    if (!token || !id || !selectedPath) return
    let cancelled = false
    ;(async () => {
      try {
        const file = await api.readFile(token, id, selectedPath)
        if (!cancelled) setContent(file.content)
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to read file')
      }
    })()
    return () => {
      cancelled = true
    }
  }, [token, id, selectedPath])

  useEffect(() => {
    if (!token || !latestActive) return
    const timer = setInterval(() => {
      void (async () => {
        const run = await api.getGeneration(token, latestActive.id)
        if (run.status === 'succeeded' || run.status === 'failed') {
          setStatusMsg(run.status === 'succeeded' ? 'Generation complete' : run.error_message)
          await refresh()
        } else {
          setRuns((prev) => prev.map((r) => (r.id === run.id ? run : r)))
        }
      })()
    }, 1500)
    return () => clearInterval(timer)
  }, [token, latestActive, refresh])

  async function onGenerate(e: FormEvent) {
    e.preventDefault()
    if (!token || !id || !prompt.trim()) return
    setBusy(true)
    setError(null)
    setStatusMsg('Running generation pipeline…')
    try {
      const result = await api.generate(token, {
        prompt: prompt.trim(),
        project_id: id,
      })
      setStatusMsg(
        result.mode === 'edit'
          ? `Edit applied — ${result.files.length} files`
          : result.preview?.ok
            ? `Built ${result.files.length} files — live preview ready`
            : `Generated ${result.files.length} files (static preview)`,
      )
      setLivePreview(Boolean(result.preview?.ok))
      setPrompt('')
      setSelectedPath(null)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed')
      setStatusMsg(null)
    } finally {
      setBusy(false)
    }
  }

  async function onSave() {
    if (!token || !id || !selectedPath) return
    setSaving(true)
    try {
      await api.writeFile(token, id, selectedPath, content)
      setStatusMsg(`Saved ${selectedPath}`)
      const html = await fetchPreview(token, id)
      setPreviewHtml(html)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  async function onDownload() {
    if (!token || !id) return
    const res = await fetch(api.downloadUrl(id), {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      setError('Download failed')
      return
    }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${project?.name ?? 'project'}.zip`
    a.click()
    URL.revokeObjectURL(url)
  }

  const language = useMemo(() => languageFor(selectedPath), [selectedPath])

  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--line)] bg-white/80 px-5 py-3 backdrop-blur">
        <div className="min-w-0">
          <Link to="/" className="text-xs font-medium text-[var(--muted)] hover:text-[var(--ink)]">
            ← Projects
          </Link>
          <h1 className="truncate text-lg font-semibold">{project?.name ?? 'Workspace'}</h1>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => void onDownload()}
            className="rounded-lg border border-[var(--line)] bg-white px-3 py-1.5 text-sm font-medium"
            disabled={!project?.current_run_id}
          >
            Download ZIP
          </button>
          <span className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-medium text-[var(--muted)]">
            Deploy: later
          </span>
        </div>
      </header>

      <div className="grid flex-1 lg:grid-cols-[320px_1fr]">
        <aside className="border-b border-[var(--line)] bg-white/70 p-4 lg:border-b-0 lg:border-r">
          <form onSubmit={onGenerate} className="space-y-3">
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium">Prompt</span>
              <textarea
                className="min-h-28 w-full rounded-lg border border-[var(--line)] bg-white px-3 py-2 text-sm outline-none ring-[var(--accent-2)] focus:ring-2"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Refine the site or edit: Change the navbar to glassmorphism…"
              />
            </label>
            <button
              type="submit"
              disabled={busy || !prompt.trim()}
              className="w-full rounded-lg bg-[var(--ink)] px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
            >
              {busy ? 'Submitting…' : latestActive ? 'Queue another run' : 'Generate / regenerate'}
            </button>
          </form>

          {statusMsg && <p className="mt-3 text-sm text-[var(--accent)]">{statusMsg}</p>}
          {error && <p className="mt-3 text-sm text-[var(--danger)]">{error}</p>}
          {latestActive && (
            <p className="mt-3 text-sm text-[var(--muted)]">
              Status: <strong>{latestActive.status}</strong>
            </p>
          )}

          <div className="mt-6">
            <p className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">Files</p>
            <ul className="mt-2 max-h-64 space-y-1 overflow-auto text-sm">
              {files.map((f) => (
                <li key={f.path}>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedPath(f.path)
                      setTab('code')
                    }}
                    className={`w-full rounded px-2 py-1 text-left hover:bg-slate-100 ${
                      selectedPath === f.path ? 'bg-slate-100 font-medium' : ''
                    }`}
                  >
                    {f.path}
                  </button>
                </li>
              ))}
              {!files.length && <li className="text-[var(--muted)]">No files yet</li>}
            </ul>
          </div>
        </aside>

        <section className="flex min-h-[70vh] flex-col">
          <div className="flex gap-1 border-b border-[var(--line)] bg-white/60 px-3 py-2">
            {(['preview', 'code', 'history'] as Tab[]).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium capitalize ${
                  tab === t ? 'bg-[var(--ink)] text-white' : 'text-[var(--muted)] hover:bg-slate-100'
                }`}
              >
                {t}
              </button>
            ))}
            {tab === 'code' && (
              <button
                type="button"
                onClick={() => void onSave()}
                disabled={saving || !selectedPath}
                className="ml-auto rounded-md border border-[var(--line)] bg-white px-3 py-1.5 text-sm font-medium disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Save file'}
              </button>
            )}
          </div>

          {tab === 'preview' && (
            livePreview && token ? (
              <iframe
                title="Live Preview"
                className="min-h-[70vh] w-full flex-1 bg-white"
                src={`${api.livePreviewUrl(id)}?access_token=${encodeURIComponent(token)}`}
                sandbox="allow-scripts allow-same-origin"
              />
            ) : (
              <iframe
                title="Preview"
                className="min-h-[70vh] w-full flex-1 bg-white"
                srcDoc={previewHtml || emptyPreview}
                sandbox="allow-scripts allow-same-origin"
              />
            )
          )}

          {tab === 'code' && (
            <div className="min-h-[70vh] flex-1">
              <Editor
                height="70vh"
                theme="vs-light"
                language={language}
                value={content}
                onChange={(v) => setContent(v ?? '')}
                options={{ fontSize: 14, minimap: { enabled: false }, wordWrap: 'on' }}
              />
            </div>
          )}

          {tab === 'history' && (
            <ul className="space-y-3 p-5">
              {runs.map((run) => (
                <li key={run.id} className="rounded-xl border border-[var(--line)] bg-white/80 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">
                      {run.status}
                    </span>
                    <span className="text-xs text-[var(--muted)]">
                      {new Date(run.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-relaxed">{run.prompt}</p>
                  {run.error_message && (
                    <p className="mt-2 text-sm text-[var(--danger)]">{run.error_message}</p>
                  )}
                </li>
              ))}
              {!runs.length && <p className="text-[var(--muted)]">No generations yet.</p>}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}

const emptyPreview = `<!doctype html><html><body style="font-family:sans-serif;padding:2rem;color:#627d98">
Generate a site to see the live preview here.</body></html>`

async function probeLivePreview(token: string, projectId: string): Promise<boolean> {
  try {
    const res = await fetch(`${api.livePreviewUrl(projectId)}?access_token=${encodeURIComponent(token)}`, {
      method: 'GET',
      headers: { Accept: 'text/html' },
    })
    return res.ok
  } catch {
    return false
  }
}

async function fetchPreview(token: string, projectId: string): Promise<string> {
  const res = await fetch(`/api/v1/preview/${projectId}/preview.html`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) return emptyPreview
  return res.text()
}

function languageFor(path: string | null): string {
  if (!path) return 'plaintext'
  if (path.endsWith('.tsx') || path.endsWith('.ts')) return 'typescript'
  if (path.endsWith('.jsx') || path.endsWith('.js')) return 'javascript'
  if (path.endsWith('.css')) return 'css'
  if (path.endsWith('.html')) return 'html'
  if (path.endsWith('.json')) return 'json'
  if (path.endsWith('.md')) return 'markdown'
  return 'plaintext'
}

import Editor from '@monaco-editor/react'
import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { GenerationStages } from '../components/GenerationStages'
import { api, type FileEntry, type Generation, type Project } from '../lib/api'

type Tab = 'preview' | 'code' | 'history'

export function WorkspacePage() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
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
  const [previewKey, setPreviewKey] = useState(0)
  const [previewError, setPreviewError] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [statusMsg, setStatusMsg] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [saving, setSaving] = useState(false)

  const latestActive = useMemo(
    () => runs.find((r) => r.status === 'queued' || r.status === 'running'),
    [runs],
  )

  const goToProjects = useCallback(() => {
    navigate('/projects', { replace: false })
  }, [navigate])

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
          fileList.find((f) => f.path === 'src/data/portfolio.ts') ??
          fileList.find((f) => f.path === 'src/App.tsx') ??
          fileList.find((f) => f.path === 'README.md') ??
          fileList[0]
        setSelectedPath(preferred.path)
      }
      const liveOk = await probeLivePreview(token, id)
      setLivePreview(liveOk)
      const html = await fetchPreview(token, id)
      setPreviewHtml(html)
      if (liveOk) setPreviewError(null)
    } else {
      setLivePreview(false)
      setPreviewHtml('')
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
    setTab('preview')
    try {
      const result = await api.generate(token, {
        prompt: prompt.trim(),
        project_id: id,
      })
      setStatusMsg(
        result.mode === 'edit'
          ? `Edit applied — ${result.files.length} files`
          : result.mode === 'revert'
            ? `Reverted to previous version — ${result.files.length} files restored`
          : result.preview?.ok
            ? `Built ${result.files.length} files — live preview ready`
            : `Generated ${result.files.length} files`,
      )
      if (result.preview?.ok) {
        setLivePreview(true)
        setPreviewError(null)
      } else {
        setLivePreview(false)
        setPreviewError(
          typeof result.preview?.error === 'string'
            ? result.preview.error
            : 'Live build failed — showing static snapshot. Regenerate to retry.',
        )
      }
      setPreviewKey((k) => k + 1)
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
      setLivePreview(false)
      const ok = await probeLivePreview(token, id)
      setLivePreview(ok)
      if (!ok) setPreviewHtml(await fetchPreview(token, id))
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

  const canOpenPreview = Boolean(project?.current_run_id && (livePreview || previewHtml))

  const previewSrc = useMemo(() => {
    if (!token || !id) return null
    if (livePreview) {
      return `${api.livePreviewUrl(id)}?access_token=${encodeURIComponent(token)}&v=${previewKey}`
    }
    return null
  }, [token, id, livePreview, previewKey])

  function onOpenInNewTab() {
    if (!token || !id || !canOpenPreview) return
    if (livePreview) {
      const url = `${api.livePreviewUrl(id)}?access_token=${encodeURIComponent(token)}&v=${Date.now()}`
      window.open(url, '_blank', 'noopener,noreferrer')
      return
    }
    const html = previewHtml || emptyPreview
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank', 'noopener,noreferrer')
    window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
  }

  function onRefreshPreview() {
    setPreviewKey((k) => k + 1)
    void refresh()
  }

  const language = useMemo(() => languageFor(selectedPath), [selectedPath])
  const visibleFiles = useMemo(
    () => files.filter((f) => !f.path.startsWith('.builder/') && f.path !== 'preview.html'),
    [files],
  )

  return (
    <div className="k-surface relative flex min-h-screen flex-col">
      <div className="k-warm-bg opacity-30" aria-hidden />
      <header className="relative z-40 sticky top-0 border-b border-[var(--line)] bg-[var(--topnav)]">
        <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 md:px-5">
          <div className="flex min-w-0 items-center gap-3">
            <button type="button" onClick={goToProjects} className="k-btn">
              ← Projects
            </button>
            <div className="min-w-0">
              <p className="k-label">Workspace</p>
              <h1 className="k-section truncate">{project?.name ?? 'Workspace'}</h1>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className={`k-badge ${livePreview ? 'k-badge-accent' : 'k-badge-neutral'}`}>
              {livePreview ? 'Live' : project?.current_run_id ? 'Static' : 'Empty'}
            </span>
            <button
              type="button"
              onClick={onOpenInNewTab}
              className="k-btn"
              disabled={!canOpenPreview}
              title="Open preview in a new browser tab"
            >
              <ExternalLinkIcon />
              Open in new tab
            </button>
            <button
              type="button"
              onClick={() => void onDownload()}
              className="k-btn k-btn-primary"
              disabled={!project?.current_run_id}
            >
              Download ZIP
            </button>
          </div>
        </div>
      </header>

      <div className="grid flex-1 lg:grid-cols-[minmax(280px,320px)_minmax(0,1fr)]">
        <aside className="order-2 flex flex-col border-t border-[var(--line)] bg-[var(--bg)] p-5 lg:order-1 lg:border-r lg:border-t-0">
          <form onSubmit={onGenerate} className="k-composer space-y-3 p-4">
            <div>
              <p className="k-label">Control</p>
              <p className="k-caption mt-1">Describe a new site or refine this one.</p>
            </div>
            <textarea
              className="k-input min-h-28 border-0 bg-transparent shadow-none focus:shadow-none"
              style={{ boxShadow: 'none' }}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. make it perfect · revert · change the hero to dark luxury"
            />
            <button
              type="submit"
              disabled={busy || !prompt.trim()}
              className={`k-btn k-btn-primary w-full ${busy ? 'k-pulse-warm' : ''}`}
            >
              {busy ? 'Generating…' : latestActive ? 'Queue another' : 'Generate'}
            </button>
          </form>

          {busy && <GenerationStages active tone="app" tinygptOnline={null} />}

          {statusMsg && !busy && (
            <p className="mt-3 rounded-[var(--radius)] border border-[var(--line)] bg-[var(--accent-soft)] px-3 py-2 text-[var(--text-body)] text-[var(--accent)]">
              {statusMsg}
            </p>
          )}
          {previewError && !livePreview && (
            <p className="k-caption mt-3 rounded-[var(--radius)] border border-[var(--line)] px-3 py-2">
              Preview note: {previewError.slice(0, 220)}
            </p>
          )}
          {error && (
            <p className="mt-3 rounded-[var(--radius)] border border-[var(--line)] px-3 py-2 text-[var(--text-body)] text-[var(--danger)]">
              {error}
            </p>
          )}

          <div className="mt-6 flex-1">
            <div className="flex items-center justify-between">
              <p className="k-label">Files</p>
              <span className="k-caption">{visibleFiles.length}</span>
            </div>
            <ul className="mt-2 max-h-[40vh] space-y-0.5 overflow-auto rounded-[var(--radius)] border border-[var(--line)] bg-[var(--bg)] p-1">
              {visibleFiles.map((f) => (
                <li key={f.path}>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedPath(f.path)
                      setTab('code')
                    }}
                    className={`k-mono w-full rounded-[var(--radius)] px-2 py-1.5 text-left transition ${
                      selectedPath === f.path
                        ? 'bg-[var(--accent-soft)] text-[var(--accent)]'
                        : 'text-[var(--muted)] hover:bg-[var(--bg-muted)] hover:text-[var(--ink)]'
                    }`}
                  >
                    {f.path}
                  </button>
                </li>
              ))}
              {!visibleFiles.length && (
                <li className="k-caption px-2 py-3">Generate a site to see files</li>
              )}
            </ul>
          </div>
        </aside>

        <section className="order-1 flex min-h-0 flex-1 flex-col lg:order-2 lg:min-h-[calc(100vh-4.25rem)]">
          <div className="flex flex-wrap items-center gap-1 border-b border-[var(--line)] bg-[var(--bg-elevated)] px-3 py-2">
            {(['preview', 'code', 'history'] as Tab[]).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setTab(t)}
                className={`rounded-[var(--radius)] px-3 py-1.5 text-[var(--text-body)] font-medium capitalize ${
                  tab === t
                    ? 'bg-[var(--accent-soft)] text-[var(--accent)]'
                    : 'text-[var(--muted)] hover:bg-[var(--bg-muted)] hover:text-[var(--ink)]'
                }`}
              >
                {t}
              </button>
            ))}
            {tab === 'preview' && (
              <div className="ml-auto flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={onRefreshPreview}
                  className="k-btn k-btn-ghost"
                  disabled={!project?.current_run_id || busy}
                  title="Refresh preview"
                >
                  <RefreshIcon />
                  Refresh
                </button>
                <button
                  type="button"
                  onClick={onOpenInNewTab}
                  className="k-btn"
                  disabled={!canOpenPreview}
                  title="Open preview in a new browser tab"
                >
                  <ExternalLinkIcon />
                  Open in new tab
                </button>
              </div>
            )}
            {tab === 'code' && (
              <button
                type="button"
                onClick={() => void onSave()}
                disabled={saving || !selectedPath}
                className="k-btn ml-auto"
              >
                {saving ? 'Saving…' : 'Save file'}
              </button>
            )}
          </div>

          {tab === 'preview' && (
            <div className="relative flex min-h-[70vh] flex-1 flex-col bg-[var(--bg-muted)] p-3 md:p-4">
              <div className="mb-3 flex items-center gap-2 rounded-[var(--radius)] border border-[var(--line)] bg-[var(--bg-elevated)] px-3 py-2 shadow-[var(--shadow-soft)]">
                <span className="flex gap-1.5" aria-hidden>
                  <span className="h-2.5 w-2.5 rounded-full bg-[#e8a0a0]" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[#e8d4a0]" />
                  <span className="h-2.5 w-2.5 rounded-full bg-[#a8d4b8]" />
                </span>
                <div className="k-mono min-w-0 flex-1 truncate rounded-full bg-[var(--bg-muted)] px-3 py-1 text-[var(--muted)]">
                  {livePreview ? 'live preview · full site' : project?.current_run_id ? 'static snapshot' : 'no preview yet'}
                </div>
                <button
                  type="button"
                  onClick={onOpenInNewTab}
                  className="k-btn k-btn-ghost shrink-0 !min-h-8 !px-2.5"
                  disabled={!canOpenPreview}
                  aria-label="Open preview in new tab"
                  title="Open in new tab"
                >
                  <ExternalLinkIcon />
                </button>
              </div>

              <div className="relative min-h-0 flex-1 overflow-hidden rounded-[var(--radius)] border border-[var(--line)] bg-white shadow-[var(--shadow-soft)]">
                {busy && (
                  <div
                    className="absolute inset-0 z-10 flex items-center justify-center"
                    style={{ background: 'color-mix(in oklab, var(--bg) 82%, transparent)' }}
                  >
                    <div className="k-card k-fade px-8 py-6 text-center">
                      <div className="k-pulse-warm mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-[var(--accent-soft)] text-[var(--accent)]">
                        <span className="k-spin inline-block h-6 w-6 rounded-full border-2 border-[var(--accent)] border-t-transparent" />
                      </div>
                      <p className="mt-4 font-semibold text-[var(--ink)]">Building preview…</p>
                      <p className="k-caption mt-1">Almost ready.</p>
                    </div>
                  </div>
                )}
                {previewSrc ? (
                  <iframe
                    key={`live-${previewKey}-${id}`}
                    title="Live Preview"
                    className="h-full min-h-[calc(70vh-3.5rem)] w-full bg-white"
                    src={previewSrc}
                    sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                  />
                ) : (
                  <iframe
                    key={`static-${previewKey}`}
                    title="Preview"
                    className="h-full min-h-[calc(70vh-3.5rem)] w-full bg-white"
                    srcDoc={previewHtml || (visibleFiles.length ? buildingPreview : emptyPreview)}
                    sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                  />
                )}
              </div>
            </div>
          )}

          {tab === 'code' && (
            <div className="min-h-[70vh] flex-1 overflow-hidden">
              <div className="k-mono border-b border-[var(--line)] bg-[var(--bg-muted)] px-4 py-2 text-[var(--muted)]">
                {selectedPath ?? 'Select a file'}
              </div>
              <Editor
                height="calc(70vh - 36px)"
                theme="vs-dark"
                language={language}
                value={content}
                onChange={(v) => setContent(v ?? '')}
                options={{ fontSize: 13, fontFamily: 'JetBrains Mono, monospace', minimap: { enabled: false }, wordWrap: 'on', padding: { top: 12 } }}
              />
            </div>
          )}

          {tab === 'history' && (
            <ul className="space-y-2 p-4">
              {runs.map((run) => (
                <li key={run.id} className="k-card p-4">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span
                      className={`k-badge ${
                        run.status === 'succeeded' || run.status === 'completed'
                          ? 'k-badge-success'
                          : run.status === 'failed'
                            ? 'k-badge-danger'
                            : run.status === 'running' || run.status === 'queued'
                              ? 'k-badge-accent'
                              : 'k-badge-neutral'
                      }`}
                    >
                      {run.status}
                    </span>
                    <span className="k-caption">{new Date(run.created_at).toLocaleString()}</span>
                  </div>
                  <p className="mt-2 text-[var(--text-body)] leading-relaxed">{run.prompt}</p>
                  {run.error_message && (
                    <p className="mt-2 text-[var(--text-body)] text-[var(--danger)]">{run.error_message}</p>
                  )}
                </li>
              ))}
              {!runs.length && <p className="k-caption">No generations yet.</p>}
            </ul>
          )}
        </section>
      </div>
    </div>
  )
}

const emptyPreview = `<!doctype html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600&display=swap');
body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:#f6f1ea;color:#2a241e}
.card{max-width:22rem;padding:2.25rem;text-align:center;border-radius:16px;border:1px solid #e2d8cc;background:#fffcf8;box-shadow:0 14px 36px -18px rgba(42,36,30,.2)}
h1{margin:0;font-size:1.25rem;font-weight:600;letter-spacing:-.03em}p{margin:.75rem 0 0;color:#7a7066;font-size:.9rem;line-height:1.55}
</style></head><body><div class="card"><h1>Ready when you are</h1>
<p>Describe your idea on the left — Ember will build a site you can preview and ship.</p>
</div></body></html>`

const buildingPreview = `<!doctype html><html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600&display=swap');
body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:#f6f1ea;color:#2a241e}
.card{max-width:22rem;padding:2.25rem;text-align:center;border-radius:16px;border:1px solid #e2d8cc;background:#fffcf8}
h1{margin:0;font-size:1.15rem;font-weight:600}p{margin:.75rem 0 0;color:#7a7066;font-size:.9rem;line-height:1.55}
</style></head><body><div class="card"><h1>Files ready</h1>
<p>Lighting the preview… If this stays blank, generate once more.</p>
</div></body></html>`

async function probeLivePreview(token: string, projectId: string): Promise<boolean> {
  try {
    const res = await fetch(`${api.livePreviewUrl(projectId)}?access_token=${encodeURIComponent(token)}`, {
      method: 'GET',
      headers: { Accept: 'text/html' },
    })
    if (!res.ok) return false
    const text = await res.text()
    if (text.includes('If you see this fallback')) return false
    if (text.includes('Live React preview builds after generate') && !text.includes('id="root"')) {
      return false
    }
    return text.includes('id="root"') || text.includes('/assets/') || text.length > 400
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

function ExternalLinkIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M14 4h6v6M10 14 20 4M20 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h5"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function RefreshIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M21 12a9 9 0 1 1-2.64-6.36M21 3v6h-6"
        stroke="currentColor"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

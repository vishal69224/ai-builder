const API_BASE = import.meta.env.VITE_API_BASE ?? ''

export type User = {
  id: string
  email: string
  name: string
  created_at: string
}

export type Project = {
  id: string
  name: string
  description: string | null
  status: string
  current_run_id: string | null
  created_at: string
  updated_at: string
}

export type Generation = {
  id: string
  project_id: string
  prompt: string
  status: string
  error_message: string | null
  provider: string
  model: string
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export type FileEntry = {
  path: string
  size_bytes: number | null
}

function authHeaders(token: string | null): HeadersInit {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  return headers
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token: string | null = null,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...authHeaders(token), ...(options.headers ?? {}) },
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ?? JSON.stringify(body)
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === 'string' ? detail : 'Request failed')
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const api = {
  register: (email: string, password: string, name: string) =>
    request<{ access_token: string }>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    }),
  login: (email: string, password: string) =>
    request<{ access_token: string }>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  me: (token: string) => request<User>('/api/v1/auth/me', {}, token),
  listProjects: (token: string) => request<Project[]>('/api/v1/projects', {}, token),
  createProject: (token: string, data: { name: string; description?: string; prompt?: string }) =>
    request<Project>('/api/v1/projects', { method: 'POST', body: JSON.stringify(data) }, token),
  getProject: (token: string, id: string) => request<Project>(`/api/v1/projects/${id}`, {}, token),
  deleteProject: (token: string, id: string) =>
    request<void>(`/api/v1/projects/${id}`, { method: 'DELETE' }, token),
  listGenerations: (token: string, projectId: string) =>
    request<Generation[]>(`/api/v1/projects/${projectId}/generations`, {}, token),
  createGeneration: (token: string, projectId: string, prompt: string) =>
    request<Generation>(
      `/api/v1/projects/${projectId}/generations`,
      { method: 'POST', body: JSON.stringify({ prompt }) },
      token,
    ),
  getGeneration: (token: string, runId: string) =>
    request<Generation>(`/api/v1/generations/${runId}`, {}, token),
  listFiles: (token: string, projectId: string) =>
    request<FileEntry[]>(`/api/v1/projects/${projectId}/files`, {}, token),
  readFile: (token: string, projectId: string, path: string) =>
    request<{ path: string; content: string }>(
      `/api/v1/projects/${projectId}/file?path=${encodeURIComponent(path)}`,
      {},
      token,
    ),
  writeFile: (token: string, projectId: string, path: string, content: string) =>
    request<{ path: string; content: string }>(
      `/api/v1/projects/${projectId}/file`,
      { method: 'PUT', body: JSON.stringify({ path, content }) },
      token,
    ),
  downloadUrl: (projectId: string) => `${API_BASE}/api/v1/projects/${projectId}/download`,
  previewUrl: (projectId: string, token: string) =>
    `${API_BASE}/api/v1/preview/${projectId}/preview.html?token=${encodeURIComponent(token)}`,
  analyze: (prompt: string) =>
    request<Record<string, unknown>>('/api/v1/analyze', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    }),
  generate: (
    token: string,
    data: { prompt: string; project_name?: string; project_id?: string },
  ) =>
    request<{
      mode: string
      project: { id: string; name: string; description: string | null; current_run_id: string | null }
      run: { id: string; status: string; prompt: string }
      analysis: Record<string, unknown>
      files: FileEntry[]
      validation: { ok: boolean }
      preview: { ok: boolean; preview_url: string | null; error?: string }
    }>('/api/v1/generate', { method: 'POST', body: JSON.stringify(data) }, token),
  livePreviewUrl: (projectId: string) => `${API_BASE}/api/v1/preview-live/${projectId}/`,
  aiStatus: () =>
    request<{
      active_provider: string
      description: string
      tinygpt?: {
        ok: boolean
        hybrid?: boolean
        checkpoint?: string
        params?: number
        error?: string
      }
      pipeline?: string[]
    }>('/api/v1/ai/status'),
}

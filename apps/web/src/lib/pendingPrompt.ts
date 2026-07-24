const PENDING_KEY = 'ember_pending_prompt'
const LEGACY_KEYS = ['prism_pending_prompt', 'kiln_pending_prompt', 'forge_pending_prompt']

export function savePendingPrompt(prompt: string) {
  sessionStorage.setItem(PENDING_KEY, prompt.trim())
  for (const k of LEGACY_KEYS) sessionStorage.removeItem(k)
}

export function readPendingPrompt(): string | null {
  const v =
    sessionStorage.getItem(PENDING_KEY) ??
    LEGACY_KEYS.map((k) => sessionStorage.getItem(k)).find(Boolean) ??
    null
  return v?.trim() ? v.trim() : null
}

export function clearPendingPrompt() {
  sessionStorage.removeItem(PENDING_KEY)
  for (const k of LEGACY_KEYS) sessionStorage.removeItem(k)
}

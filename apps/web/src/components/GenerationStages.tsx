import { useEffect, useState } from 'react'
import { WarmSpark } from './brand/WarmIllustrations'

const STAGES = [
  { id: 'listen', label: 'Reading your prompt' },
  { id: 'sketch', label: 'Drafting the layout' },
  { id: 'shape', label: 'Generating components' },
  { id: 'glow', label: 'Lighting the preview' },
] as const

type Props = {
  active: boolean
  tinygptOnline?: boolean | null
  tone?: 'studio' | 'app'
}

export function GenerationStages({ active, tinygptOnline }: Props) {
  const [step, setStep] = useState(0)

  useEffect(() => {
    if (!active) {
      setStep(0)
      return
    }
    setStep(0)
    const timers = [
      window.setTimeout(() => setStep(1), 900),
      window.setTimeout(() => setStep(2), 2200),
      window.setTimeout(() => setStep(3), 3800),
    ]
    return () => timers.forEach((t) => window.clearTimeout(t))
  }, [active])

  if (!active) return null

  return (
    <div className="k-card mt-6 w-full p-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="k-label inline-flex items-center gap-1.5">
          <WarmSpark className="text-[var(--accent)]" />
          Building
        </p>
        <span className="k-caption">
          {tinygptOnline ? 'TinyGPT online' : tinygptOnline === false ? 'Engine ready' : '…'}
        </span>
      </div>
      <ol className="grid gap-2.5">
        {STAGES.map((s, i) => {
          const done = i < step
          const current = i === step
          return (
            <li key={s.id} className="flex items-center gap-3">
              <span
                className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold ${
                  done
                    ? 'bg-[var(--accent)] text-[#fffcf8]'
                    : current
                      ? 'k-pulse-warm border-2 border-[var(--accent)] text-[var(--accent)]'
                      : 'border border-[var(--line)] text-[var(--muted)]'
                }`}
              >
                {done ? '✓' : i + 1}
              </span>
              <span
                className={`text-[var(--text-body)] font-medium ${
                  current || done ? 'text-[var(--ink)]' : 'text-[var(--muted)]'
                }`}
              >
                {s.label}
              </span>
            </li>
          )
        })}
      </ol>
    </div>
  )
}

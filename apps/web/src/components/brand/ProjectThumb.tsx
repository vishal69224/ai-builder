/** Warm thumbnail — soft copper/cream gradients, no 3D tilt */
export function ProjectThumb({ id, name, size = 44 }: { id: string; name: string; size?: number }) {
  let h = 0
  for (let i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0
  const hues = [
    'linear-gradient(145deg, color-mix(in oklab, var(--accent) 42%, var(--bg-muted)), var(--bg-elevated))',
    'linear-gradient(145deg, #d4a574, color-mix(in oklab, var(--bg-muted) 70%, #c45a2c))',
    'linear-gradient(160deg, #3d2e24, color-mix(in oklab, var(--accent) 55%, #2a241e))',
  ]
  return (
    <span
      className="relative flex shrink-0 overflow-hidden rounded-[var(--radius)]"
      style={{
        width: size,
        height: size,
        background: hues[h % hues.length],
        boxShadow: 'var(--shadow-soft)',
      }}
      aria-hidden
    >
      <span
        className="absolute inset-0 opacity-30"
        style={{
          background: `radial-gradient(circle at ${30 + (h % 40)}% 25%, rgba(255,252,248,0.55), transparent 55%)`,
        }}
      />
      <span className="relative z-10 m-auto text-[13px] font-semibold text-[#fffcf8]">
        {name.slice(0, 1).toUpperCase()}
      </span>
    </span>
  )
}

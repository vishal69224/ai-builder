/** Emergent-style floating 3D app preview cards */
const apps = [
  {
    title: 'Shoply',
    tag: 'Store',
    gradient: 'linear-gradient(160deg, #1e1b4b, #0f766e)',
    delay: '0s',
    rot: '-8deg',
    x: '8%',
    y: '12%',
  },
  {
    title: 'NovaCRM',
    tag: 'SaaS',
    gradient: 'linear-gradient(160deg, #172554, #4c1d95)',
    delay: '0.6s',
    rot: '6deg',
    x: '72%',
    y: '8%',
  },
  {
    title: 'Pulse Fit',
    tag: 'Mobile',
    gradient: 'linear-gradient(160deg, #422006, #9a3412)',
    delay: '1.1s',
    rot: '4deg',
    x: '78%',
    y: '58%',
  },
  {
    title: 'Studio Folio',
    tag: 'Portfolio',
    gradient: 'linear-gradient(160deg, #052e16, #155e75)',
    delay: '0.3s',
    rot: '-5deg',
    x: '4%',
    y: '55%',
  },
]

export function OrbitCards() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      {apps.map((app) => (
        <div
          key={app.title}
          className="absolute hidden w-[150px] sm:block md:w-[170px]"
          style={{
            left: app.x,
            top: app.y,
            transform: `rotate(${app.rot})`,
            animation: `float-y 6s ease-in-out ${app.delay} infinite`,
          }}
        >
          <div
            className="overflow-hidden rounded-2xl border border-white/10 shadow-[0_30px_60px_-30px_rgba(0,0,0,0.9)]"
            style={{ background: app.gradient }}
          >
            <div className="flex items-center gap-1.5 border-b border-white/10 px-2.5 py-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-white/40" />
              <span className="h-1.5 w-1.5 rounded-full bg-white/25" />
              <span className="h-1.5 w-1.5 rounded-full bg-white/15" />
            </div>
            <div className="p-3">
              <p className="text-[9px] font-bold uppercase tracking-[0.18em] text-white/50">
                {app.tag}
              </p>
              <p className="mt-1 font-display text-sm font-bold text-white">{app.title}</p>
              <div className="mt-3 space-y-1.5">
                <div className="h-1.5 w-full rounded bg-white/15" />
                <div className="h-1.5 w-4/5 rounded bg-white/10" />
                <div className="mt-2 grid grid-cols-2 gap-1">
                  <div className="h-8 rounded-lg bg-white/10" />
                  <div className="h-8 rounded-lg bg-white/10" />
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

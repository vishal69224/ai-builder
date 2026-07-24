import { Link } from 'react-router-dom'

type EmberLogoProps = {
  size?: 'sm' | 'md' | 'lg'
  withWordmark?: boolean
  to?: string | null
  className?: string
  /** Monochrome for dark-on-light / light-on-dark contexts */
  mono?: boolean
}

const box = { sm: 22, md: 28, lg: 34 } as const

/** Refined ember / spark mark — holds at 16px and in monochrome */
export function EmberMark({
  size = 28,
  className = '',
  mono = false,
}: {
  size?: number
  className?: string
  mono?: boolean
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <path
        fill={mono ? 'currentColor' : 'var(--accent, #C45A2C)'}
        d="M16 4c.4 5.2 3.2 8.8 5.6 11.2C19.2 17.6 17.2 20 16 24c-1.2-4-3.2-6.4-5.6-8.8C12.8 12.8 15.6 9.2 16 4z"
      />
      <path
        fill={mono ? 'currentColor' : 'var(--accent, #C45A2C)'}
        opacity="0.35"
        d="M16 10c.25 3 1.8 5 3.2 6.4C18 17.8 16.8 19.2 16 22c-.8-2.8-2-4.2-3.2-5.6C14.2 15 15.75 13 16 10z"
      />
    </svg>
  )
}

export function EmberLogo({
  size = 'md',
  withWordmark = true,
  to = '/',
  className = '',
  mono = false,
}: EmberLogoProps) {
  const px = box[size]
  const inner = (
    <span className={`k-logo ${className}`}>
      <span className="k-logo__mark">
        <EmberMark size={px} mono={mono} />
      </span>
      {withWordmark && <span className="k-logo__word">Ember</span>}
    </span>
  )
  if (to === null) return inner
  return (
    <Link to={to} className="k-logo-link">
      {inner}
    </Link>
  )
}

/** Back-compat aliases */
export const PrismLogo = EmberLogo
export const KilnLogo = EmberLogo
export const PrismMark = EmberMark
export const KilnMark = EmberMark

/** Minimal empty-state mark — soft ember arch, not a mascot */
export function EmptyCraftIllustration({ className = '' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 200 140"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden
    >
      <ellipse cx="100" cy="118" rx="42" ry="7" fill="currentColor" opacity="0.1" />
      <path
        fill="currentColor"
        opacity="0.28"
        d="M100 36c.7 9 5.5 15.2 9.6 19.4C104.8 60 101.4 64.2 99.2 71c-2.2-6.8-5.6-11-9.6-15.6C94.5 51.2 99.3 45 100 36z"
      />
      <path
        fill="currentColor"
        opacity="0.55"
        d="M100 48c.45 5.4 3.5 9.2 6.1 11.8C103.5 62.8 101.4 65.4 100 70c-1.4-4.6-3.5-7.2-6.1-10.2C96.5 57.2 99.55 53.4 100 48z"
      />
    </svg>
  )
}

export function WarmSpark({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" className={className} aria-hidden>
      <path
        fill="currentColor"
        d="M12 3c.3 3.9 2.4 6.6 4.2 8.4C14.4 13.2 12.9 15 12 18c-.9-3-2.4-4.8-4.2-6.6C9.6 9.6 11.7 6.9 12 3z"
      />
    </svg>
  )
}

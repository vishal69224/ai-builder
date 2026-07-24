const faqs = [
  {
    q: 'What is Ember?',
    a: 'Ember turns a prompt into a React + Vite + Tailwind site with live preview, code editing, and ZIP download.',
  },
  {
    q: 'Do I need an API key?',
    a: 'No. Generation runs locally with specialty engines and optional TinyGPT on your machine.',
  },
  {
    q: 'Can I edit the code?',
    a: 'Yes. Open any project workspace to preview, edit files, and download the full source.',
  },
]

export function MarketingFaq() {
  return (
    <section className="mx-auto max-w-2xl px-6 py-16">
      <h2 className="k-title">FAQ</h2>
      <ul className="mt-8 space-y-4">
        {faqs.map((f) => (
          <li key={f.q} className="k-card p-5">
            <p className="k-section">{f.q}</p>
            <p className="k-caption mt-2" style={{ fontSize: 'var(--text-body)' }}>
              {f.a}
            </p>
          </li>
        ))}
      </ul>
    </section>
  )
}

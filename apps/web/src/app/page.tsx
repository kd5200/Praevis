const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "Praevis";
const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-16">
      <p className="text-sm font-medium uppercase tracking-[0.2em] text-accent">{appName}</p>
      <h1 className="mt-4 text-4xl font-semibold tracking-tight text-ink md:text-5xl">
        Security gateway for AI agents
      </h1>
      <p className="mt-4 max-w-xl text-lg text-ink-muted">
        Submit URLs for inspection, review findings, and consume sanitized content with
        provenance. Dashboard scan flows arrive in Phase 3.
      </p>
      <div className="mt-10 flex flex-wrap gap-3">
        <a
          className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white transition hover:opacity-90"
          href={`${apiBase}/health`}
          rel="noreferrer"
          target="_blank"
        >
          API health
        </a>
        <a
          className="rounded-md border border-ink/15 bg-surface-card px-4 py-2 text-sm font-medium text-ink transition hover:bg-white"
          href={`${apiBase}/docs`}
          rel="noreferrer"
          target="_blank"
        >
          OpenAPI docs
        </a>
      </div>
      <p className="mt-12 font-mono text-xs text-ink-muted">
        Phase 1 placeholder · API {apiBase}
      </p>
    </main>
  );
}

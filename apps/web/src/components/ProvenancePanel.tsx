import type { Provenance } from "@/lib/types";

export function ProvenancePanel({
  provenance,
  finalUrl,
  normalizedUrl,
}: {
  provenance?: Provenance | null;
  finalUrl?: string | null;
  normalizedUrl?: string | null;
}) {
  const redirects = provenance?.redirect_chain ?? [];

  return (
    <dl className="grid gap-3 text-sm sm:grid-cols-2">
      <div>
        <dt className="text-xs uppercase tracking-wide text-ink-muted">Normalized URL</dt>
        <dd className="mt-1 break-all font-mono text-xs text-ink">{normalizedUrl ?? "—"}</dd>
      </div>
      <div>
        <dt className="text-xs uppercase tracking-wide text-ink-muted">Final URL</dt>
        <dd className="mt-1 break-all font-mono text-xs text-ink">{finalUrl ?? "—"}</dd>
      </div>
      <div>
        <dt className="text-xs uppercase tracking-wide text-ink-muted">Retrieved at</dt>
        <dd className="mt-1 text-ink">
          {provenance?.retrieved_at ? new Date(provenance.retrieved_at).toLocaleString() : "—"}
        </dd>
      </div>
      <div>
        <dt className="text-xs uppercase tracking-wide text-ink-muted">Content hash</dt>
        <dd className="mt-1 break-all font-mono text-xs text-ink">
          {provenance?.content_hash ?? "—"}
        </dd>
      </div>
      <div className="sm:col-span-2">
        <dt className="text-xs uppercase tracking-wide text-ink-muted">Redirect chain</dt>
        <dd className="mt-1">
          {redirects.length === 0 ? (
            <span className="text-ink-muted">None</span>
          ) : (
            <ol className="list-decimal space-y-1 pl-5 font-mono text-xs text-ink">
              {redirects.map((hop) => (
                <li key={hop} className="break-all">
                  {hop}
                </li>
              ))}
            </ol>
          )}
        </dd>
      </div>
    </dl>
  );
}

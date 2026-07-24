import type { Finding } from "@/lib/types";

const SEVERITY_CLASS: Record<string, string> = {
  critical: "text-red-800",
  high: "text-red-700",
  medium: "text-amber-800",
  low: "text-ink-muted",
  info: "text-ink-muted",
};

export function FindingsPanel({ findings }: { findings: Finding[] }) {
  if (findings.length === 0) {
    return <p className="text-sm text-ink-muted">No findings recorded for this scan.</p>;
  }

  return (
    <ul className="space-y-4">
      {findings.map((finding, index) => (
        <li key={finding.id ?? `${finding.detector}-${index}`} className="border-t border-ink/10 pt-4">
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <h3 className="font-medium text-ink">{finding.title}</h3>
            <span className={`text-xs font-semibold uppercase ${SEVERITY_CLASS[finding.severity] ?? ""}`}>
              {finding.severity}
            </span>
            <span className="font-mono text-xs text-ink-muted">{finding.detector}</span>
          </div>
          <p className="mt-1 text-sm text-ink-muted">{finding.description}</p>
          {finding.evidence ? (
            <pre className="mt-2 overflow-x-auto rounded-md bg-ink/[0.04] p-3 font-mono text-xs text-ink">
              {finding.evidence}
            </pre>
          ) : null}
          {finding.remediation ? (
            <p className="mt-2 text-sm text-ink">
              <span className="font-medium">Remediation:</span> {finding.remediation}
            </p>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

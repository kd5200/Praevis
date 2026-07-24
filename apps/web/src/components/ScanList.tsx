import Link from "next/link";

import { DecisionBadge } from "@/components/DecisionBadge";
import type { Scan } from "@/lib/types";

function formatWhen(value?: string | null): string {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export function ScanList({ scans }: { scans: Scan[] }) {
  if (scans.length === 0) {
    return (
      <p className="text-sm text-ink-muted">No scans yet. Submit a URL above to create the first one.</p>
    );
  }

  return (
    <ul className="divide-y divide-ink/10 border-t border-ink/10">
      {scans.map((scan) => (
        <li key={scan.scan_id}>
          <Link
            href={`/scans/${scan.scan_id}`}
            className="flex flex-col gap-2 py-4 transition hover:bg-white/50 sm:flex-row sm:items-center sm:justify-between"
          >
            <div className="min-w-0">
              <p className="truncate font-medium text-ink">{scan.submitted_url}</p>
              <p className="mt-1 font-mono text-xs text-ink-muted">
                {scan.status} · {formatWhen(scan.created_at ?? scan.completed_at)}
              </p>
            </div>
            <div className="flex items-center gap-3 text-sm">
              <span className="text-ink-muted">
                risk {scan.risk_score ?? "—"} / trust {scan.trust_score ?? "—"}
              </span>
              <DecisionBadge decision={scan.decision} />
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}

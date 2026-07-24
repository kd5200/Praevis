export function ScorePanel({
  riskScore,
  trustScore,
}: {
  riskScore?: number | null;
  trustScore?: number | null;
}) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <p className="text-xs uppercase tracking-wide text-ink-muted">Risk</p>
        <p className="mt-1 text-3xl font-semibold tabular-nums text-ink">{riskScore ?? "—"}</p>
        <p className="mt-1 text-xs text-ink-muted">Detected danger (0–100)</p>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wide text-ink-muted">Trust</p>
        <p className="mt-1 text-3xl font-semibold tabular-nums text-ink">{trustScore ?? "—"}</p>
        <p className="mt-1 text-xs text-ink-muted">Confidence to consume safely</p>
      </div>
    </div>
  );
}

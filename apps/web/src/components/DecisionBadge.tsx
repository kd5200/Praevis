import type { Decision } from "@/lib/types";

const STYLES: Record<string, string> = {
  allow: "bg-accent/15 text-accent ring-accent/30",
  warn: "bg-amber-100 text-amber-900 ring-amber-300/60",
  block: "bg-red-100 text-red-900 ring-red-300/60",
  pending: "bg-ink/5 text-ink-muted ring-ink/10",
  failed: "bg-red-50 text-red-800 ring-red-200",
};

const TERMINAL = new Set(["completed", "blocked", "failed"]);

export function DecisionBadge({
  decision,
  status,
}: {
  decision?: Decision | null;
  status?: string | null;
}) {
  let value: string;
  if (decision) {
    value = decision.toLowerCase();
  } else if (status && !TERMINAL.has(status)) {
    value = "pending";
  } else if (status === "failed") {
    value = "failed";
  } else {
    value = "pending";
  }

  const style = STYLES[value] ?? "bg-ink/5 text-ink-muted ring-ink/10";
  return (
    <span
      className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ring-1 ring-inset ${style}`}
    >
      {value}
    </span>
  );
}
